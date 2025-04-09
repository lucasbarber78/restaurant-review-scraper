#!/usr/bin/env python3
"""
Main entry point for the restaurant review scraper.
This script orchestrates the scraping of reviews from TripAdvisor, Yelp, and Google Reviews
with enhanced anti-bot detection measures.
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

# Import traditional scrapers
from src.tripadvisor_scraper import TripAdvisorScraper
from src.yelp_scraper import YelpScraper
from src.google_scraper import GoogleScraper

# Import enhanced scrapers with anti-bot detection
from src.tripadvisor_puppeteer_scraper import TripAdvisorPuppeteerScraper
from src.yelp_scraper_enhanced import EnhancedYelpScraper

# Other imports
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
    parser.add_argument("--enhanced", action="store_true", 
                        help="Use enhanced scrapers with anti-bot detection measures")
    parser.add_argument("--headless", action="store_true",
                        help="Run browsers in headless mode (less visible but more detectable)")
    parser.add_argument("--no-stealth", action="store_true",
                        help="Disable stealth plugins (not recommended)")
    parser.add_argument("--no-random-delays", action="store_true",
                        help="Disable random delays (not recommended)")
    parser.add_argument("--enable-proxy-rotation", action="store_true",
                        help="Enable proxy rotation if configured in config.yaml")
    
    return parser.parse_args()


def main():
    """Main function to orchestrate the scraping process with anti-bot detection."""
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
    
    # Set anti-bot detection settings from command line arguments
    if "anti_bot_settings" not in config:
        config["anti_bot_settings"] = {}
        
    # Update anti-bot settings based on command line arguments
    if args.no_stealth:
        config["anti_bot_settings"]["enable_stealth_plugins"] = False
    if args.no_random_delays:
        config["anti_bot_settings"]["enable_random_delays"] = False
    if args.headless:
        config["anti_bot_settings"]["headless_mode"] = True
    if args.enable_proxy_rotation:
        config["anti_bot_settings"]["enable_proxy_rotation"] = True
    
    # Initialize categorizer
    categorizer = ReviewCategorizer(config)
    
    # Initialize scrapers
    scrapers = {}
    all_reviews = []
    
    if args.platform in ["tripadvisor", "all"]:
        if args.enhanced:
            logger.info("Using enhanced TripAdvisor scraper with anti-bot detection")
            scrapers["tripadvisor"] = TripAdvisorPuppeteerScraper(config)
        else:
            scrapers["tripadvisor"] = TripAdvisorScraper(config)
    
    if args.platform in ["yelp", "all"]:
        if args.enhanced:
            logger.info("Using enhanced Yelp scraper with anti-bot detection")
            scrapers["yelp"] = EnhancedYelpScraper(config)
        else:
            scrapers["yelp"] = YelpScraper(config)
    
    if args.platform in ["google", "all"]:
        scrapers["google"] = GoogleScraper(config)
    
    # Run scrapers and collect reviews
    for platform, scraper in scrapers.items():
        try:
            logger.info(f"Scraping reviews from {platform.capitalize()}")
            start_time = time.time()
            reviews = scraper.scrape()
            elapsed_time = time.time() - start_time
            logger.info(f"Found {len(reviews)} reviews from {platform.capitalize()} in {elapsed_time:.2f} seconds")
            
            # Categorize and determine sentiment
            for review in reviews:
                if "category" not in review:
                    review["category"] = categorizer.categorize(review["text"])
                if "sentiment" not in review:
                    review["sentiment"] = categorizer.analyze_sentiment(review["text"])
                
                # Add scraping metadata
                review["scraper_version"] = "enhanced" if args.enhanced else "standard"
                review["scrape_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
            all_reviews.extend(reviews)
            
        except Exception as e:
            logger.error(f"Error scraping {platform}: {e}", exc_info=True)
    
    # Export to Excel
    if all_reviews:
        logger.info(f"Exporting {len(all_reviews)} reviews to Excel")
        exporter = ExcelExporter(config)
        exporter.export(all_reviews)
        logger.info(f"Successfully exported reviews to {config['excel_file_path']}")
        
        # Save as CSV as well (for backup)
        csv_path = config.get('excel_file_path', 'reviews.xlsx').replace('.xlsx', '.csv')
        save_to_csv(all_reviews, csv_path)
        logger.info(f"Also saved reviews to CSV: {csv_path}")
    else:
        logger.warning("No reviews were scraped!")
    
    logger.info("Scraping process completed")


def save_to_csv(reviews, filepath):
    """Save reviews to a CSV file as backup."""
    import csv
    
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        
        # Write to CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            if reviews:
                fieldnames = list(reviews[0].keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(reviews)
                
        return True
        
    except Exception as e:
        logger.error(f"Failed to save reviews to CSV: {e}")
        return False


if __name__ == "__main__":
    main()
