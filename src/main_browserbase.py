#!/usr/bin/env python3
"""
Restaurant Review Scraper - Main Module (Browserbase Version)

This is the main module for the Restaurant Review Scraper project.
It coordinates the scraping of reviews from multiple platforms
and exports them to an Excel file.

This version uses the Browserbase API instead of Puppeteer.
"""

import os
import sys
import logging
import argparse
import yaml
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add the 'src' directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import scrapers and utilities
from scrapers.yelp_browserbase_scraper import YelpBrowserbaseScraper
from scrapers.tripadvisor_browserbase_scraper import TripAdvisorBrowserbaseScraper
from scrapers.google_browserbase_scraper import GoogleBrowserbaseScraper
from review_categorizer import ReviewCategorizer
from excel_exporter import ExcelExporter

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scraper.log')
    ]
)

logger = logging.getLogger(__name__)


def load_config(config_path: str = 'config.yaml') -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path (str, optional): Path to config file. Defaults to 'config.yaml'.
        
    Returns:
        Dict[str, Any]: Configuration dictionary.
        
    Raises:
        FileNotFoundError: If config file doesn't exist.
        yaml.YAMLError: If config file has invalid YAML.
    """
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        logger.info(f"Loaded configuration from {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"Config file not found: {config_path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Error parsing config file: {e}")
        raise


def scrape_tripadvisor(config: Dict[str, Any], max_reviews: int = 100) -> List[Dict[str, Any]]:
    """
    Scrape reviews from TripAdvisor.
    
    Args:
        config (Dict[str, Any]): Configuration dictionary.
        max_reviews (int, optional): Maximum number of reviews to scrape. Defaults to 100.
        
    Returns:
        List[Dict[str, Any]]: List of review dictionaries.
    """
    try:
        # Get API key from config
        api_key = config.get('browserbase_api_key')
        
        # Get TripAdvisor URL from config
        url = config.get('tripadvisor_url')
        if not url:
            logger.warning("TripAdvisor URL not found in config, skipping TripAdvisor scraping")
            return []
        
        logger.info(f"Scraping TripAdvisor reviews from {url}")
        
        # Create TripAdvisor scraper
        tripadvisor_scraper = TripAdvisorBrowserbaseScraper(api_key=api_key)
        
        # Scrape reviews
        reviews = tripadvisor_scraper.scrape_reviews(url=url, max_reviews=max_reviews)
        
        logger.info(f"Scraped {len(reviews)} TripAdvisor reviews")
        return reviews
    
    except Exception as e:
        logger.error(f"Error scraping TripAdvisor reviews: {e}", exc_info=True)
        return []


def scrape_yelp(config: Dict[str, Any], max_reviews: int = 100) -> List[Dict[str, Any]]:
    """
    Scrape reviews from Yelp.
    
    Args:
        config (Dict[str, Any]): Configuration dictionary.
        max_reviews (int, optional): Maximum number of reviews to scrape. Defaults to 100.
        
    Returns:
        List[Dict[str, Any]]: List of review dictionaries.
    """
    try:
        # Get API key from config
        api_key = config.get('browserbase_api_key')
        
        # Get Yelp URL from config
        url = config.get('yelp_url')
        if not url:
            logger.warning("Yelp URL not found in config, skipping Yelp scraping")
            return []
        
        logger.info(f"Scraping Yelp reviews from {url}")
        
        # Create Yelp scraper
        yelp_scraper = YelpBrowserbaseScraper(api_key=api_key)
        
        # Scrape reviews
        reviews = yelp_scraper.scrape_reviews(url=url, max_reviews=max_reviews)
        
        logger.info(f"Scraped {len(reviews)} Yelp reviews")
        return reviews
    
    except Exception as e:
        logger.error(f"Error scraping Yelp reviews: {e}", exc_info=True)
        return []


def scrape_google(config: Dict[str, Any], max_reviews: int = 100) -> List[Dict[str, Any]]:
    """
    Scrape reviews from Google.
    
    Args:
        config (Dict[str, Any]): Configuration dictionary.
        max_reviews (int, optional): Maximum number of reviews to scrape. Defaults to 100.
        
    Returns:
        List[Dict[str, Any]]: List of review dictionaries.
    """
    try:
        # Get API key from config
        api_key = config.get('browserbase_api_key')
        
        # Get Google Place ID from config
        place_id = config.get('google_place_id')
        if not place_id:
            logger.warning("Google Place ID not found in config, skipping Google scraping")
            return []
        
        logger.info(f"Scraping Google reviews for Place ID: {place_id}")
        
        # Create Google scraper
        google_scraper = GoogleBrowserbaseScraper(api_key=api_key)
        
        # Scrape reviews
        reviews = google_scraper.scrape_reviews(place_id=place_id, max_reviews=max_reviews)
        
        logger.info(f"Scraped {len(reviews)} Google reviews")
        return reviews
    
    except Exception as e:
        logger.error(f"Error scraping Google reviews: {e}", exc_info=True)
        return []


def categorize_reviews(reviews: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Categorize reviews and add sentiment analysis.
    
    Args:
        reviews (List[Dict[str, Any]]): List of review dictionaries.
        config (Dict[str, Any]): Configuration dictionary.
        
    Returns:
        List[Dict[str, Any]]: List of review dictionaries with categories and sentiment.
    """
    try:
        # Create categorizer
        categorizer = ReviewCategorizer(config)
        
        # Process each review
        categorized_reviews = []
        for review in reviews:
            # Add category and sentiment
            categorized_review = categorizer.categorize_review(review)
            categorized_reviews.append(categorized_review)
        
        logger.info(f"Categorized {len(categorized_reviews)} reviews")
        return categorized_reviews
    
    except Exception as e:
        logger.error(f"Error categorizing reviews: {e}", exc_info=True)
        return reviews  # Return uncategorized reviews if there's an error


def export_to_excel(reviews: Dict[str, List[Dict[str, Any]]], config: Dict[str, Any]) -> None:
    """
    Export reviews to Excel file.
    
    Args:
        reviews (Dict[str, List[Dict[str, Any]]]): Dictionary mapping platform names to lists of reviews.
        config (Dict[str, Any]): Configuration dictionary.
    """
    try:
        # Get Excel file path from config
        file_path = config.get('excel_file_path', 'reviews.xlsx')
        
        # Create exporter
        exporter = ExcelExporter(file_path)
        
        # Export reviews
        exporter.export_reviews(reviews)
        
        logger.info(f"Exported reviews to {file_path}")
    
    except Exception as e:
        logger.error(f"Error exporting reviews to Excel: {e}", exc_info=True)


def main() -> None:
    """
    Main function to run the scraper.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Scrape restaurant reviews from multiple platforms.')
    parser.add_argument('--config', '-c', default='config.yaml', help='Path to config file')
    parser.add_argument('--max-reviews', '-m', type=int, default=100,
                        help='Maximum number of reviews to scrape per platform')
    parser.add_argument('--platforms', '-p', nargs='+', choices=['tripadvisor', 'yelp', 'google', 'all'],
                        default=['all'], help='Platforms to scrape')
    args = parser.parse_args()
    
    # Load configuration
    try:
        config = load_config(args.config)
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)
    
    # Determine which platforms to scrape
    platforms_to_scrape = args.platforms
    if 'all' in platforms_to_scrape:
        platforms_to_scrape = ['tripadvisor', 'yelp', 'google']
    
    # Dictionary to store reviews by platform
    all_reviews = {}
    
    # Scrape from each platform
    if 'tripadvisor' in platforms_to_scrape:
        tripadvisor_reviews = scrape_tripadvisor(config, args.max_reviews)
        all_reviews['tripadvisor'] = categorize_reviews(tripadvisor_reviews, config)
    
    if 'yelp' in platforms_to_scrape:
        yelp_reviews = scrape_yelp(config, args.max_reviews)
        all_reviews['yelp'] = categorize_reviews(yelp_reviews, config)
    
    if 'google' in platforms_to_scrape:
        google_reviews = scrape_google(config, args.max_reviews)
        all_reviews['google'] = categorize_reviews(google_reviews, config)
    
    # Export to Excel
    export_to_excel(all_reviews, config)
    
    # Log summary
    total_reviews = sum(len(reviews) for reviews in all_reviews.values())
    logger.info(f"Completed scraping {total_reviews} reviews from {len(all_reviews)} platforms")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
