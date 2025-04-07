#!/usr/bin/env python3
"""
Browserbase Scraper Script

This script automates the review scraping process using Browserbase and Puppeteer.
It extracts reviews from Yelp, TripAdvisor, and Google Reviews, and saves them to CSV.
"""

import os
import sys
import json
import time
import logging
import argparse
import csv
import re
import yaml
import asyncio
from datetime import datetime
from urllib.parse import quote

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Constants
DEFAULT_OUTPUT_FILE = "data/scraped_reviews.csv"
DEFAULT_CONFIG_FILE = "config.yaml"
PLATFORMS = ["yelp", "tripadvisor", "google"]
DEFAULT_MAX_REVIEWS = 100
DEFAULT_MAX_PAGES = 10
DEFAULT_SCROLL_PAUSE = 1.5
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

class BrowserbaseScraper:
    """Main scraper class using Browserbase."""
    
    def __init__(self, config):
        """Initialize the scraper with the given configuration."""
        self.config = config
        self.api_key = config.get('browserbase_api_key')
        self.project_id = config.get('browserbase_project_id')
        self.max_reviews = config.get('max_reviews_per_platform', DEFAULT_MAX_REVIEWS)
        self.max_pages = config.get('max_pages_per_platform', DEFAULT_MAX_PAGES)
        self.scroll_pause = config.get('scroll_pause_time', DEFAULT_SCROLL_PAUSE)
        self.timeout = config.get('timeout_seconds', 60)
        self.platform_urls = {
            'yelp': config.get('yelp_url', ''),
            'tripadvisor': config.get('tripadvisor_url', ''),
            'google': config.get('google_place_id', '')
        }
        self.restaurant_name = config.get('restaurant_name', 'Restaurant')
        self.start_date = datetime.strptime(config.get('date_range', {}).get('start', '2020-01-01'), '%Y-%m-%d')
        self.end_date = datetime.strptime(config.get('date_range', {}).get('end', '2030-12-31'), '%Y-%m-%d')
        self.all_reviews = []
        self.browser = None
        self.page = None
    
    async def create_browser_session(self):
        """Create a new browser session using Browserbase."""
        logger.info("Creating Browserbase session")
        
        try:
            # Import Browserbase SDK and puppeteer
            from browserbase import Browserbase
            from puppeteer import launch
            
            # Initialize Browserbase if API key is provided
            if self.api_key:
                bb = Browserbase({
                    'apiKey': self.api_key,
                    'projectId': self.project_id
                })
                session = await bb.sessions.create()
                browser = await launch({
                    'browserWSEndpoint': session.connectUrl,
                    'headless': True
                })
            else:
                # Fall back to local Puppeteer if no API key
                browser = await launch({
                    'headless': True,
                    'args': [
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-web-security',
                        '--disable-features=IsolateOrigins,site-per-process'
                    ]
                })
            
            page = await browser.newPage()
            
            # Set user agent to avoid detection
            await page.setUserAgent(USER_AGENT)
            
            # Set viewport
            await page.setViewport({'width': 1280, 'height': 800})
            
            # Set timeout
            await page.setDefaultTimeout(self.timeout * 1000)
            
            self.browser = browser
            self.page = page
            
            return browser, page
            
        except ImportError:
            logger.error("Failed to import Browserbase SDK or puppeteer. Please install them with:")
            logger.error("  pip install browserbase-sdk puppeteer-python")
            raise
        except Exception as e:
            logger.error(f"Error creating browser session: {e}", exc_info=True)
            raise
    
    async def close_browser_session(self):
        """Close the browser session."""
        if self.browser:
            await self.browser.close()
            logger.info("Browser session closed")
    
    async def scrape_all_platforms(self):
        """Scrape reviews from all platforms."""
        reviews = []
        
        try:
            # Create browser session
            await self.create_browser_session()
            
            # Scrape each platform
            for platform in PLATFORMS:
                if self.platform_urls.get(platform):
                    logger.info(f"Scraping reviews from {platform}")
                    
                    # Call the appropriate scraper function
                    if platform == "yelp":
                        platform_reviews = await self.scrape_yelp()
                    elif platform == "tripadvisor":
                        platform_reviews = await self.scrape_tripadvisor()
                    elif platform == "google":
                        platform_reviews = await self.scrape_google()
                    
                    reviews.extend(platform_reviews)
                    logger.info(f"Found {len(platform_reviews)} reviews from {platform}")
        
        except Exception as e:
            logger.error(f"Error during scraping: {e}", exc_info=True)
        
        finally:
            # Close browser session
            await self.close_browser_session()
        
        return reviews
    
    async def take_screenshot(self, filename="screenshot.png"):
        """Take a screenshot for debugging."""
        if self.page:
            screenshot_dir = "screenshots"
            os.makedirs(screenshot_dir, exist_ok=True)
            path = os.path.join(screenshot_dir, filename)
            await self.page.screenshot({'path': path})
            logger.info(f"Screenshot saved to {path}")
    
    async def handle_cookies_popup(self):
        """Handle various cookie consent popups."""
        try:
            cookie_selectors = [
                '#onetrust-accept-btn-handler',
                '.evidon-banner-acceptbutton',
                'button[id*="cookie-accept"]',
                'button[id*="accept-cookies"]',
                'button[title*="Accept"]',
                '.accept-cookies-button',
                'button[aria-label*="Accept"]'
            ]
            
            for selector in cookie_selectors:
                try:
                    button = await self.page.querySelector(selector)
                    if button:
                        await button.click()
                        logger.info(f"Clicked cookie consent button: {selector}")
                        await self.page.waitForTimeout(1000)
                        break
                except Exception:
                    continue
        except Exception as e:
            logger.warning(f"Error handling cookie popup: {e}")
    
    def save_reviews_to_csv(self, reviews, output_file=DEFAULT_OUTPUT_FILE):
        """Save reviews to CSV file."""
        if not reviews:
            logger.warning("No reviews to save")
            return
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Determine CSV fields
            fieldnames = ['reviewer_name', 'date', 'rating', 'title', 'review_text', 
                          'platform', 'raw_date', 'category', 'sentiment']
            
            # Check if file exists to append or create new
            file_exists = os.path.exists(output_file)
            
            mode = 'a' if file_exists else 'w'
            with open(output_file, mode, newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header only if creating new file
                if not file_exists:
                    writer.writeheader()
                
                # Write reviews
                for review in reviews:
                    # Ensure all fields exist (with empty values if missing)
                    row = {field: review.get(field, '') for field in fieldnames}
                    writer.writerow(row)
            
            logger.info(f"Saved {len(reviews)} reviews to {output_file}")
        
        except Exception as e:
            logger.error(f"Error saving reviews to CSV: {e}", exc_info=True)
    
    def _parse_relative_date(self, date_text):
        """Parse relative date expressions (e.g., "2 weeks ago")."""
        if not date_text:
            return datetime.now()
        
        # Try parsing as standard date
        try:
            from dateutil import parser
            return parser.parse(date_text)
        except:
            pass
        
        # Handle relative dates
        current_date = datetime.now()
        
        if 'yesterday' in date_text.lower():
            return current_date.replace(day=current_date.day-1)
        
        if 'week' in date_text.lower():
            # Extract number of weeks
            weeks_match = re.search(r'(\d+)\s+weeks?', date_text.lower())
            weeks = int(weeks_match.group(1)) if weeks_match else 1
            return current_date.replace(day=current_date.day-(weeks*7))
        
        if 'month' in date_text.lower():
            # Extract number of months
            months_match = re.search(r'(\d+)\s+months?', date_text.lower())
            months = int(months_match.group(1)) if months_match else 1
            
            new_month = current_date.month - months
            new_year = current_date.year
            
            if new_month <= 0:
                new_month += 12
                new_year -= 1
            
            return current_date.replace(year=new_year, month=new_month)
        
        if 'day' in date_text.lower():
            # Extract number of days
            days_match = re.search(r'(\d+)\s+days?', date_text.lower())
            days = int(days_match.group(1)) if days_match else 1
            return current_date.replace(day=current_date.day-days)
        
        if 'year' in date_text.lower():
            # Extract number of years
            years_match = re.search(r'(\d+)\s+years?', date_text.lower())
            years = int(years_match.group(1)) if years_match else 1
            return current_date.replace(year=current_date.year-years)
        
        # Default to current date if parsing fails
        return current_date

# Main function to run the scraper
async def main_async(args):
    """Async main function to run the scraper."""
    try:
        # Load configuration
        with open(args.config, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Override config with command line arguments
        if args.output:
            config['excel_file_path'] = args.output
        if args.max_reviews:
            config['max_reviews_per_platform'] = args.max_reviews
        if args.start_date:
            config['date_range']['start'] = args.start_date
        if args.end_date:
            config['date_range']['end'] = args.end_date
        
        # Create scraper
        scraper = BrowserbaseScraper(config)
        
        # Scrape reviews
        if args.platform == 'all':
            reviews = await scraper.scrape_all_platforms()
        elif args.platform == 'yelp':
            await scraper.create_browser_session()
            reviews = await scraper.scrape_yelp()
            await scraper.close_browser_session()
        elif args.platform == 'tripadvisor':
            await scraper.create_browser_session()
            reviews = await scraper.scrape_tripadvisor()
            await scraper.close_browser_session()
        elif args.platform == 'google':
            await scraper.create_browser_session()
            reviews = await scraper.scrape_google()
            await scraper.close_browser_session()
        
        # Save reviews to CSV
        scraper.save_reviews_to_csv(reviews, args.output)
        
        return reviews
    
    except Exception as e:
        logger.error(f"Error in main function: {e}", exc_info=True)
        return []

def main():
    """Main function to parse arguments and run the scraper."""
    parser = argparse.ArgumentParser(description="Scrape restaurant reviews using Browserbase")
    parser.add_argument("--config", "-c", default=DEFAULT_CONFIG_FILE, help="Path to config file")
    parser.add_argument("--output", "-o", default=DEFAULT_OUTPUT_FILE, help="Path to output CSV file")
    parser.add_argument("--platform", "-p", choices=PLATFORMS + ["all"], default="all", help="Platform to scrape")
    parser.add_argument("--max-reviews", "-m", type=int, help="Maximum reviews to scrape per platform")
    parser.add_argument("--start-date", help="Start date in YYYY-MM-DD format")
    parser.add_argument("--end-date", help="End date in YYYY-MM-DD format")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    loop = asyncio.get_event_loop()
    reviews = loop.run_until_complete(main_async(args))
    
    logger.info(f"Scraped a total of {len(reviews)} reviews")

if __name__ == "__main__":
    main()
