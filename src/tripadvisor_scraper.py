#!/usr/bin/env python3
"""
TripAdvisor Scraper Module

This module handles the scraping of reviews from TripAdvisor using Browserbase.
"""

import logging
import time
import re
import json
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from dateutil import parser

from src.utils.browser_utils import create_browser_session, close_browser_session

logger = logging.getLogger(__name__)


class TripAdvisorScraper:
    """Scraper for TripAdvisor reviews."""
    
    def __init__(self, config):
        """Initialize the TripAdvisor scraper.
        
        Args:
            config (dict): Configuration dictionary.
        """
        self.config = config
        self.url = config['tripadvisor_url']
        self.start_date = datetime.strptime(config['date_range']['start'], '%Y-%m-%d')
        self.end_date = datetime.strptime(config['date_range']['end'], '%Y-%m-%d')
        self.max_reviews = config.get('max_reviews_per_platform', 0)
        self.timeout = config.get('timeout_seconds', 60)
        self.retry_attempts = config.get('retry_attempts', 3)
        self.scroll_pause_time = config.get('scroll_pause_time', 1.5)
        self.browser = None
        self.page = None
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(Exception)
    )
    async def _navigate_to_reviews_page(self):
        """Navigate to the reviews page."""
        logger.info(f"Navigating to TripAdvisor URL: {self.url}")
        await self.page.goto(self.url, timeout=self.timeout * 1000)
        
        # Check if we need to click on a "Reviews" tab
        try:
            reviews_tab = await self.page.querySelector('a[data-tab="TABS_REVIEWS"]')
            if reviews_tab:
                await reviews_tab.click()
                await self.page.waitForSelector(".reviewSelector", timeout=self.timeout * 1000)
        except Exception as e:
            logger.warning(f"Could not find or click Reviews tab: {e}")
            
            # Try alternative methods to navigate to reviews
            try:
                reviews_link = await self.page.querySelector('a[href*="Reviews"]')
                if reviews_link:
                    await reviews_link.click()
                    await self.page.waitForSelector(".reviewSelector", timeout=self.timeout * 1000)
            except Exception as e2:
                logger.warning(f"Alternative navigation method failed: {e2}")
                # Continue anyway, we might already be on the reviews page
    
    async def _handle_cookies_popup(self):
        """Handle cookie consent popups if they appear."""
        try:
            # Look for various cookie consent buttons
            cookie_buttons = [
                '#onetrust-accept-btn-handler',
                '.evidon-banner-acceptbutton',
                'button[id*="cookie-accept"]',
                'button[id*="accept-cookies"]',
                'button[title*="Accept"]',
                '.accept-cookies-button'
            ]
            
            for selector in cookie_buttons:
                try:
                    button = await self.page.querySelector(selector)
                    if button:
                        await button.click()
                        logger.info("Clicked cookie consent button")
                        await self.page.waitForTimeout(1000)
                        break
                except Exception:
                    continue
        except Exception as e:
            logger.warning(f"Error handling cookie popup: {e}")
    
    async def _scroll_reviews(self):
        """Scroll through reviews to load more."""
        previous_height = await self.page.evaluate('document.body.scrollHeight')
        reviews_loaded = 0
        last_review_count = 0
        stall_count = 0
        
        while True:
            # Scroll down
            await self.page.evaluate('window.scrollBy(0, window.innerHeight)')
            await self.page.waitForTimeout(self.scroll_pause_time * 1000)
            
            # Check if we have new reviews
            current_reviews = await self.page.querySelectorAll('.reviewSelector')
            reviews_loaded = len(current_reviews)
            
            # Click "More" buttons if they exist
            more_buttons = await self.page.querySelectorAll('span.taLnk.ulBlueLinks')
            for button in more_buttons:
                try:
                    await button.click()
                    await self.page.waitForTimeout(500)
                except Exception:
                    pass
            
            # Check if we've reached our review limit
            if self.max_reviews > 0 and reviews_loaded >= self.max_reviews:
                logger.info(f"Reached max reviews limit ({self.max_reviews})")
                break
            
            # Check if we've loaded new reviews
            if reviews_loaded == last_review_count:
                stall_count += 1
                if stall_count >= 5:  # If we've stalled 5 times, assume we're done
                    logger.info("No new reviews loading, ending scroll")
                    break
            else:
                stall_count = 0
                
            last_review_count = reviews_loaded
            
            # Check if we've reached the bottom of the page
            current_height = await self.page.evaluate('document.body.scrollHeight')
            if current_height == previous_height:
                # Try to click "Load more" button if it exists
                try:
                    load_more = await self.page.querySelector('button.load_more')
                    if load_more:
                        await load_more.click()
                        await self.page.waitForTimeout(2000)
                    else:
                        # No more reviews to load
                        break
                except Exception:
                    # No more reviews to load
                    break
                    
            previous_height = current_height
            
            logger.info(f"Loaded {reviews_loaded} reviews so far...")
    
    async def _extract_review_data(self):
        """Extract data from loaded reviews."""
        logger.info("Extracting review data...")
        
        reviews = []
        review_elements = await self.page.querySelectorAll('.reviewSelector')
        
        for i, review_element in enumerate(review_elements):
            try:
                # Extract review date
                date_element = await review_element.querySelector('.ratingDate')
                if not date_element:
                    date_element = await review_element.querySelector('.relativeDate')
                
                date_text = await self.page.evaluate('el => el.textContent', date_element)
                date_text = date_text.replace('Reviewed', '').strip()
                
                # Parse the date
                try:
                    review_date = parser.parse(date_text, fuzzy=True)
                except ValueError:
                    # Handle relative dates like "yesterday", "a week ago", etc.
                    current_date = datetime.now()
                    if 'yesterday' in date_text.lower():
                        review_date = current_date.replace(day=current_date.day-1)
                    elif 'week ago' in date_text.lower():
                        review_date = current_date.replace(day=current_date.day-7)
                    elif 'month ago' in date_text.lower():
                        review_date = current_date.replace(month=current_date.month-1)
                    else:
                        # Default to current date if parsing fails
                        review_date = current_date
                
                # Filter by date range
                if not (self.start_date <= review_date.replace(tzinfo=None) <= self.end_date):
                    continue
                
                # Extract reviewer name
                name_element = await review_element.querySelector('.info_text')
                reviewer_name = await self.page.evaluate('el => el.textContent', name_element) if name_element else "Anonymous"
                
                # Extract rating
                rating_element = await review_element.querySelector('.ui_bubble_rating')
                rating_class = await self.page.evaluate('el => el.className', rating_element) if rating_element else ""
                rating_match = re.search(r'bubble_(\d+)', rating_class)
                rating = int(rating_match.group(1)) / 10 if rating_match else 0
                
                # Extract review title
                title_element = await review_element.querySelector('.noQuotes')
                review_title = await self.page.evaluate('el => el.textContent', title_element) if title_element else ""
                
                # Extract review text
                text_element = await review_element.querySelector('.partial_entry')
                review_text = await self.page.evaluate('el => el.textContent', text_element) if text_element else ""
                review_text = review_text.strip()
                
                # Create review object
                review = {
                    'platform': 'TripAdvisor',
                    'reviewer_name': reviewer_name.strip(),
                    'date': review_date.strftime('%Y-%m-%d'),
                    'rating': rating,
                    'title': review_title.strip(),
                    'text': review_text,
                    'url': self.url,
                    'raw_date': date_text
                }
                
                reviews.append(review)
                
                # Check if we've reached our review limit
                if self.max_reviews > 0 and len(reviews) >= self.max_reviews:
                    logger.info(f"Reached max reviews limit ({self.max_reviews})")
                    break
                
            except Exception as e:
                logger.warning(f"Failed to extract review {i}: {e}")
        
        logger.info(f"Extracted {len(reviews)} reviews in the specified date range")
        return reviews
    
    def scrape(self):
        """Scrape reviews from TripAdvisor.
        
        Returns:
            list: List of review dictionaries.
        """
        reviews = []
        
        try:
            # Create browser session
            self.browser, self.page = create_browser_session(self.config.get('browserbase_api_key'))
            
            # Run scraping in async mode
            import asyncio
            loop = asyncio.get_event_loop()
            reviews = loop.run_until_complete(self._scrape_async())
            
        except Exception as e:
            logger.error(f"Error during TripAdvisor scraping: {e}", exc_info=True)
        finally:
            # Close browser session
            close_browser_session(self.browser)
        
        return reviews
    
    async def _scrape_async(self):
        """Async implementation of the scraping process."""
        try:
            # Navigate to TripAdvisor reviews page
            await self._navigate_to_reviews_page()
            
            # Handle any cookie popups
            await self._handle_cookies_popup()
            
            # Scroll to load reviews
            await self._scroll_reviews()
            
            # Extract review data
            reviews = await self._extract_review_data()
            
            return reviews
            
        except Exception as e:
            logger.error(f"Error during async TripAdvisor scraping: {e}", exc_info=True)
            return []


if __name__ == "__main__":
    # Standalone usage example
    import yaml
    
    logging.basicConfig(level=logging.INFO)
    
    with open("config.yaml", 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    
    scraper = TripAdvisorScraper(config)
    scraped_reviews = scraper.scrape()
    
    print(f"Scraped {len(scraped_reviews)} reviews")
    for review in scraped_reviews[:5]:
        print(json.dumps(review, indent=2))
