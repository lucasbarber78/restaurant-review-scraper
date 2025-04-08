#!/usr/bin/env python3
"""
TripAdvisor Scraper Module using Puppeteer

This module handles the scraping of reviews from TripAdvisor using Puppeteer,
which has better capabilities for avoiding bot detection.
"""

import os
import sys
import csv
import yaml
import logging
import asyncio
import time
import re
import json
from datetime import datetime
from dateutil import parser
from pyppeteer import launch
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tripadvisor_scraper.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class TripAdvisorPuppeteerScraper:
    """Scraper for TripAdvisor reviews using Puppeteer."""
    
    def __init__(self, config):
        """Initialize the TripAdvisor scraper.
        
        Args:
            config (dict): Configuration dictionary.
        """
        self.config = config
        self.url = config['tripadvisor_url']
        self.restaurant_name = config.get('restaurant_name', 'Restaurant')
        self.start_date = datetime.strptime(config['date_range']['start'], '%Y-%m-%d')
        self.end_date = datetime.strptime(config['date_range']['end'], '%Y-%m-%d')
        self.max_reviews = config.get('max_reviews_per_platform', 0)
        self.timeout = config.get('timeout_seconds', 60)
        self.retry_attempts = config.get('retry_attempts', 3)
        self.scroll_pause_time = config.get('scroll_pause_time', 1.5)
        self.browser = None
        self.page = None
        
        # Category data for classification
        self.categories = config.get('categories', [])
        self.category_keywords = config.get('category_keywords', {})
        
        # Output file
        self.csv_file_path = config.get('csv_file_path', f"{self.restaurant_name.replace(' ', '_')}_TripAdvisor_Reviews.csv")
    
    async def initialize_browser(self):
        """Initialize the browser with anti-detection measures."""
        try:
            # Launch with anti-detection settings
            self.browser = await launch({
                'headless': False,  # Setting to False can help avoid detection
                'args': [
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-blink-features=AutomationControlled',  # Key for avoiding detection
                    '--disable-infobars',
                    '--window-size=1366,768',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                ]
            })
            
            # Create a new page
            self.page = await self.browser.newPage()
            
            # Set a realistic viewport
            await self.page.setViewport({
                'width': 1366,
                'height': 768
            })
            
            # Set a realistic user agent
            await self.page.setUserAgent(
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            # Disable webdriver mode
            await self.page.evaluateOnNewDocument("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false,
                });
            """)
            
            # Add extra properties to navigator
            await self.page.evaluateOnNewDocument("""
                // overwrite the `plugins` property to use a custom getter
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                // Overwrite the `languages` property
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
            """)
            
            # Set timeout
            await self.page.setDefaultNavigationTimeout(self.timeout * 1000)
            
            logger.info("Browser initialized with anti-detection measures")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            return False
    
    async def navigate_to_reviews_page(self):
        """Navigate to the reviews page."""
        try:
            logger.info(f"Navigating to TripAdvisor URL: {self.url}")
            
            # Navigate to the page with a randomized wait
            await self.page.goto(self.url)
            await asyncio.sleep(2 + (0.5 * (hash(str(time.time())) % 5)))  # Random wait between 2-4.5s
            
            # Check for and accept any cookies banners
            await self.handle_cookies_popup()
            
            # Try to find and click on reviews tab (if needed)
            try:
                # Take a screenshot to debug
                await self.page.screenshot({'path': 'debug_before_click.png'})
                
                # Look for reviews tab/link with various selectors
                selectors = [
                    'a[data-tab="#TABS_REVIEWS"]',
                    'a[href*="Reviews"]',
                    'a.tabs_header',
                    'div.tabs_label:nth-child(2)',
                ]
                
                for selector in selectors:
                    try:
                        # Check if element exists
                        element = await self.page.querySelector(selector)
                        if element:
                            logger.info(f"Found reviews tab with selector: {selector}")
                            await element.click()
                            await asyncio.sleep(3)  # Wait for page to load
                            break
                    except Exception as click_error:
                        logger.debug(f"Could not click on {selector}: {click_error}")
            
            except Exception as e:
                logger.warning(f"Could not find reviews tab: {e}")
                # We might already be on the reviews page, so continue
            
            # Take a screenshot after navigation
            await self.page.screenshot({'path': 'tripadvisor_reviews_page.png'})
            
            # Check if we can see reviews
            reviews = await self.page.querySelectorAll('.review-container')
            if not reviews:
                reviews = await self.page.querySelectorAll('.reviewSelector')
            
            if reviews:
                logger.info(f"Found {len(reviews)} review elements initially")
                return True
            else:
                logger.warning("No review elements found on the page")
                return False
                
        except Exception as e:
            logger.error(f"Failed to navigate to reviews page: {e}")
            return False
    
    async def handle_cookies_popup(self):
        """Handle cookie consent popups if they appear."""
        try:
            # List of possible cookie consent button selectors
            cookie_selectors = [
                '#onetrust-accept-btn-handler',
                'button#onetrust-accept-btn-handler',
                'button[id*="accept"]',
                'button[title*="Accept"]',
                '.accept-cookies-button',
                '#accept-cookie-consent',
                'button:has-text("Accept")',
                'button:has-text("Accept All")',
                'button:has-text("I Accept")',
                'button:has-text("OK")'
            ]
            
            for selector in cookie_selectors:
                try:
                    await self.page.waitForSelector(selector, {'timeout': 3000})
                    logger.info(f"Found cookie consent button: {selector}")
                    await self.page.click(selector)
                    logger.info("Clicked cookie consent button")
                    await asyncio.sleep(1)
                    break
                except Exception:
                    continue
                    
        except Exception as e:
            logger.debug(f"No cookie consent handling needed or error: {e}")
    
    async def scroll_for_reviews(self, max_scrolls=50):
        """Scroll down the page to load more reviews.
        
        Args:
            max_scrolls (int): Maximum number of scroll attempts
        """
        logger.info("Starting to scroll for reviews")
        
        previous_height = 0
        reviews_count = 0
        last_reviews_count = 0
        stall_count = 0
        
        for i in range(max_scrolls):
            # Get current page height
            current_height = await self.page.evaluate('() => document.body.scrollHeight')
            
            # Scroll down
            await self.page.evaluate('window.scrollBy(0, window.innerHeight)')
            
            # Add some randomness to scrolling
            await asyncio.sleep(self.scroll_pause_time + (hash(str(time.time())) % 10) / 10)
            
            # Click "More" buttons for expanded review text
            try:
                more_buttons = await self.page.querySelectorAll('.taLnk.ulBlueLinks')
                if more_buttons:
                    for button in more_buttons[:min(5, len(more_buttons))]:  # Limit to 5 at a time
                        try:
                            await button.click()
                            await asyncio.sleep(0.2)  # Small delay between clicks
                        except Exception:
                            pass
            except Exception as e:
                logger.debug(f"Error clicking 'More' buttons: {e}")
            
            # Try clicking "Show more" buttons for pagination
            try:
                load_more_button = await self.page.querySelector('button.load_more')
                if load_more_button:
                    await load_more_button.click()
                    logger.info("Clicked 'Show more' button")
                    await asyncio.sleep(3)  # Wait for new content to load
            except Exception:
                pass
                
            # Try clicking pagination buttons
            try:
                next_page = await self.page.querySelector('a.nav.next')
                if next_page:
                    await next_page.click()
                    logger.info("Clicked next page button")
                    await asyncio.sleep(3)  # Wait for new page to load
            except Exception:
                pass
            
            # Count reviews
            reviews = await self.page.querySelectorAll('.reviewSelector')
            if not reviews:
                reviews = await self.page.querySelectorAll('.review-container')
            
            reviews_count = len(reviews)
            logger.info(f"Scroll {i+1}/{max_scrolls}: Found {reviews_count} reviews")
            
            # Check if we've reached our limit
            if self.max_reviews > 0 and reviews_count >= self.max_reviews:
                logger.info(f"Reached maximum reviews limit: {self.max_reviews}")
                break
                
            # Check if we're not getting new reviews
            if reviews_count == last_reviews_count:
                stall_count += 1
                if stall_count >= 5:  # If no new reviews after 5 scrolls, stop
                    logger.info("No new reviews found after multiple scrolls, stopping")
                    break
            else:
                stall_count = 0
                
            # Check if we've reached the bottom of the page
            if current_height == previous_height and stall_count >= 3:
                logger.info("Reached the end of the page")
                break
                
            previous_height = current_height
            last_reviews_count = reviews_count
            
            # Take a screenshot occasionally to debug
            if i % 10 == 0:
                await self.page.screenshot({'path': f'scroll_progress_{i}.png'})
        
        logger.info(f"Finished scrolling, found {reviews_count} reviews")
        return reviews_count
    
    async def extract_reviews(self):
        """Extract and parse reviews from the page."""
        logger.info("Extracting reviews from page")
        
        # Find all review containers
        review_selectors = ['.reviewSelector', '.review-container', '.review_list_item']
        
        reviews = []
        for selector in review_selectors:
            try:
                elements = await self.page.querySelectorAll(selector)
                if elements and len(elements) > 0:
                    logger.info(f"Found {len(elements)} reviews with selector: {selector}")
                    
                    # Use this selector for extraction
                    for i, review_element in enumerate(elements):
                        try:
                            review_data = await self.extract_single_review(review_element, i)
                            if review_data:
                                reviews.append(review_data)
                                
                                # Check if we've reached the limit
                                if self.max_reviews > 0 and len(reviews) >= self.max_reviews:
                                    logger.info(f"Reached maximum review limit: {self.max_reviews}")
                                    break
                        except Exception as e:
                            logger.warning(f"Error extracting review {i}: {e}")
                    
                    # If we found reviews with this selector, stop trying others
                    if reviews:
                        break
            except Exception as e:
                logger.warning(f"Error with selector {selector}: {e}")
        
        logger.info(f"Extracted {len(reviews)} reviews total")
        return reviews
    
    async def extract_single_review(self, review_element, index):
        """Extract data from a single review element.
        
        Args:
            review_element: The DOM element containing the review
            index: The index number for logging
            
        Returns:
            dict: Review data or None if extraction failed
        """
        try:
            # Extract review date
            date_text = None
            date_selectors = ['.ratingDate', '.relativeDate', '.review_date']
            
            for selector in date_selectors:
                try:
                    date_element = await review_element.querySelector(selector)
                    if date_element:
                        date_text = await self.page.evaluate('(el) => el.textContent', date_element)
                        date_text = date_text.replace('Reviewed', '').strip()
                        break
                except Exception:
                    continue
            
            if not date_text:
                logger.warning(f"Could not extract date for review {index}")
                date_text = "Unknown date"
                
            # Parse the date
            review_date = None
            try:
                # Handle relative dates like "2 days ago"
                if 'ago' in date_text.lower():
                    # For demo purposes, we'll use the current date
                    # In a production environment, you would implement proper relative date parsing
                    review_date = datetime.now()
                else:
                    # Try to parse the actual date
                    review_date = parser.parse(date_text, fuzzy=True)
            except Exception:
                # Default to current date if parsing fails
                review_date = datetime.now()
                logger.warning(f"Could not parse date '{date_text}', using current date")
            
            # Filter by date range if we have a valid date
            if review_date and not (self.start_date <= review_date.replace(tzinfo=None) <= self.end_date):
                logger.debug(f"Review date {review_date} outside filter range, skipping")
                return None
            
            # Extract reviewer name
            reviewer_name = "Anonymous"
            name_selectors = ['.info_text', '.member_info .username', '.memberOverlayLink']
            
            for selector in name_selectors:
                try:
                    name_element = await review_element.querySelector(selector)
                    if name_element:
                        reviewer_name = await self.page.evaluate('(el) => el.textContent', name_element)
                        reviewer_name = reviewer_name.strip()
                        break
                except Exception:
                    continue
            
            # Extract rating
            rating = 0
            rating_selectors = ['.ui_bubble_rating', '.review-container span[class*="bubble"]']
            
            for selector in rating_selectors:
                try:
                    rating_element = await review_element.querySelector(selector)
                    if rating_element:
                        rating_class = await self.page.evaluate('(el) => el.className', rating_element)
                        rating_match = re.search(r'bubble_(\d+)', rating_class)
                        if rating_match:
                            rating = int(rating_match.group(1)) / 10
                            break
                except Exception:
                    continue
            
            # Extract review title
            review_title = ""
            title_selectors = ['.noQuotes', '.title', 'span.topTitle']
            
            for selector in title_selectors:
                try:
                    title_element = await review_element.querySelector(selector)
                    if title_element:
                        review_title = await self.page.evaluate('(el) => el.textContent', title_element)
                        review_title = review_title.strip()
                        break
                except Exception:
                    continue
            
            # Extract review text
            review_text = ""
            text_selectors = ['.partial_entry', '.prw_reviews_text_summary_hsx', '.review-content']
            
            for selector in text_selectors:
                try:
                    text_element = await review_element.querySelector(selector)
                    if text_element:
                        review_text = await self.page.evaluate('(el) => el.innerText', text_element)
                        review_text = review_text.strip()
                        # Remove "More" button text if present
                        review_text = re.sub(r'More$', '', review_text)
                        break
                except Exception:
                    continue
            
            # Extract review date in standardized format
            date_str = review_date.strftime('%Y-%m-%d') if review_date else "Unknown"
            
            # Categorize the review
            categories = self.categorize_review(review_text + " " + review_title)
            
            # Determine sentiment
            sentiment = self.analyze_sentiment(review_text, rating)
            
            # Create review object
            review = {
                'platform': 'TripAdvisor',
                'restaurant': self.restaurant_name,
                'reviewer_name': reviewer_name,
                'date': date_str,
                'raw_date': date_text,
                'rating': rating,
                'title': review_title,
                'text': review_text,
                'categories': ', '.join(categories),
                'sentiment': sentiment,
                'url': self.url
            }
            
            return review
            
        except Exception as e:
            logger.warning(f"Error extracting data from review {index}: {e}")
            return None
    
    def categorize_review(self, text):
        """Categorize a review based on its content.
        
        Args:
            text (str): The review text to categorize
            
        Returns:
            list: Categories that apply to this review
        """
        if not text:
            return ["Uncategorized"]
            
        text = text.lower()
        categories = []
        
        # Check each category
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    categories.append(category)
                    break
        
        # If no categories found, mark as Other
        if not categories:
            categories = ["Other"]
            
        return categories
    
    def analyze_sentiment(self, text, rating=0):
        """Simple sentiment analysis based on rating and key phrases.
        
        Args:
            text (str): Review text
            rating (float): Star rating if available
            
        Returns:
            str: "Positive", "Negative", or "Neutral"
        """
        if rating >= 4:
            return "Positive"
        elif rating <= 2:
            return "Negative"
        
        # If rating is 3 or not available, check text
        positive_words = ['good', 'great', 'excellent', 'amazing', 'awesome', 
                         'love', 'best', 'delicious', 'enjoyed', 'recommended']
        negative_words = ['bad', 'terrible', 'awful', 'poor', 'disappointing',
                         'worst', 'horrible', 'avoid', 'mediocre', 'overpriced']
        
        if not text:
            return "Neutral"
            
        text = text.lower()
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        # Check for negations
        negations = ['not', 'no', "n't", 'never', 'hardly']
        for neg in negations:
            if neg + ' ' in text.lower():
                # Flip the sentiment counts when negation is present
                positive_count, negative_count = negative_count, positive_count
                break
        
        if positive_count > negative_count:
            return "Positive"
        elif negative_count > positive_count:
            return "Negative"
        else:
            return "Neutral"
    
    async def save_to_csv(self, reviews, filepath=None):
        """Save reviews to a CSV file.
        
        Args:
            reviews (list): List of review dictionaries
            filepath (str, optional): Custom file path
        """
        if not reviews:
            logger.warning("No reviews to save")
            return
            
        # Use provided filepath or default
        output_path = filepath or self.csv_file_path
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Determine fieldnames from the first review
            fieldnames = list(reviews[0].keys())
            
            # Write to CSV
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(reviews)
                
            logger.info(f"Successfully saved {len(reviews)} reviews to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to save reviews to CSV: {e}")
            return None
    
    async def run(self):
        """Run the full scraping process."""
        reviews = []
        
        try:
            # Initialize browser with anti-detection measures
            success = await self.initialize_browser()
            if not success:
                logger.error("Failed to initialize browser")
                return []
            
            # Navigate to reviews page
            success = await self.navigate_to_reviews_page()
            if not success:
                logger.error("Failed to navigate to reviews page")
                return []
            
            # Scroll to load more reviews
            review_count = await self.scroll_for_reviews()
            if review_count == 0:
                logger.warning("No reviews found after scrolling")
            
            # Extract reviews
            reviews = await self.extract_reviews()
            logger.info(f"Extracted {len(reviews)} reviews")
            
            # Save to CSV
            if reviews:
                await self.save_to_csv(reviews)
            
        except Exception as e:
            logger.error(f"Error during scraping: {e}", exc_info=True)
        finally:
            # Close browser
            if self.browser:
                await self.browser.close()
                logger.info("Browser closed")
                
        return reviews
    
    @classmethod
    async def scrape_async(cls, config):
        """Class method to run the scraper asynchronously."""
        scraper = cls(config)
        return await scraper.run()
    
    @classmethod
    def scrape(cls, config):
        """Class method to run the scraper synchronously."""
        try:
            # Create and run event loop
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # If no event loop exists, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        try:
            reviews = loop.run_until_complete(cls.scrape_async(config))
            return reviews
        finally:
            # Clean up
            try:
                loop.run_until_complete(loop.shutdown_asyncgens())
                loop.close()
            except:
                pass


if __name__ == "__main__":
    # Set up command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Scrape TripAdvisor reviews using Puppeteer')
    parser.add_argument('--config', type=str, default='config.yaml', help='Path to config file')
    parser.add_argument('--url', type=str, help='TripAdvisor URL to scrape (overrides config)')
    parser.add_argument('--output', type=str, help='Output CSV file path')
    parser.add_argument('--max', type=int, help='Maximum number of reviews to scrape')
    args = parser.parse_args()
    
    # Load configuration
    try:
        with open(args.config, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Override with command line arguments if provided
        if args.url:
            config['tripadvisor_url'] = args.url
        if args.max:
            config['max_reviews_per_platform'] = args.max
        if args.output:
            config['csv_file_path'] = args.output
            
        # Set default CSV output path if not specified
        if 'csv_file_path' not in config:
            config['csv_file_path'] = os.path.join('data', f"{config.get('restaurant_name', 'restaurant').replace(' ', '_')}_tripadvisor_reviews.csv")
            
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(config['csv_file_path'])), exist_ok=True)
            
        # Run the scraper
        logger.info(f"Starting TripAdvisor scraper for {config.get('restaurant_name', 'Unknown Restaurant')}")
        scraper = TripAdvisorPuppeteerScraper(config)
        reviews = TripAdvisorPuppeteerScraper.scrape(config)
        
        logger.info(f"Scraped {len(reviews)} reviews")
        
    except Exception as e:
        logger.error(f"Error running scraper: {e}", exc_info=True)
        sys.exit(1)
