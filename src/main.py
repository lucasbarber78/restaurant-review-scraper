#!/usr/bin/env python3
"""
Main entry point for the restaurant review scraper.
This script orchestrates the scraping of reviews from TripAdvisor, Yelp, and Google Reviews.
"""

import os
import sys
import yaml
import logging
import time
import argparse
from datetime import datetime

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tripadvisor_scraper import TripAdvisorScraper
from src.yelp_scraper import YelpScraper
from src.google_scraper import GoogleScraper
from src.excel_exporter import ExcelExporter
from src.review_categorizer import ReviewCategorizer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def load_config(config_file="config.yaml"):
    """Load configuration from YAML file."""
    try:
        with open(config_file, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except Exception as e:
        logger.error(f"Error loading configuration file: {e}")
        sys.exit(1)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Scrape reviews from TripAdvisor, Yelp, and Google")
    parser.add_argument("--config", "-c", default="config.yaml", help="Path to configuration file")
    parser.add_argument("--platform", "-p", choices=["tripadvisor", "yelp", "google", "all"],
                        default="all", help="Platform to scrape (default: all)")
    parser.add_argument("--output", "-o", help="Path to output Excel file (overrides config)")
    parser.add_argument("--start-date", help="Start date in YYYY-MM-DD format (overrides config)")
    parser.add_argument("--end-date", help="End date in YYYY-MM-DD format (overrides config)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    return parser.parse_args()


def main():
    """Main function to orchestrate the scraping process."""
    args = parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("Starting restaurant review scraper")
    
    # Load configuration
    config = load_config(args.config)
    
    # Override config with command line arguments if provided
    if args.output:
        config["excel_file_path"] = args.output
    if args.start_date:
        config["date_range"]["start"] = args.start_date
    if args.end_date:
        config["date_range"]["end"] = args.end_date
    
    # Initialize categorizer
    categorizer = ReviewCategorizer(config)
    
    # Initialize scrapers
    scrapers = {}
    all_reviews = []
    
    if args.platform in ["tripadvisor", "all"]:
        scrapers["tripadvisor"] = TripAdvisorScraper(config)
    
    if args.platform in ["yelp", "all"]:
        scrapers["yelp"] = YelpScraper(config)
    
    if args.platform in ["google", "all"]:
        scrapers["google"] = GoogleScraper(config)
    
    # Run scrapers and collect reviews
    for platform, scraper in scrapers.items():
        try:
            logger.info(f"Scraping reviews from {platform.capitalize()}")
            reviews = scraper.scrape()
            logger.info(f"Found {len(reviews)} reviews from {platform.capitalize()}")
            
            # Categorize and determine sentiment
            for review in reviews:
                review["category"] = categorizer.categorize(review["text"])
                review["sentiment"] = categorizer.analyze_sentiment(review["text"])
                
            all_reviews.extend(reviews)
            
        except Exception as e:
            logger.error(f"Error scraping {platform}: {e}", exc_info=True)
    
    # Export to Excel
    if all_reviews:
        logger.info(f"Exporting {len(all_reviews)} reviews to Excel")
        exporter = ExcelExporter(config)
        exporter.export(all_reviews)
        logger.info(f"Successfully exported reviews to {config['excel_file_path']}")
    else:
        logger.warning("No reviews were scraped!")
    
    logger.info("Scraping process completed")


if __name__ == "__main__":
    main()
