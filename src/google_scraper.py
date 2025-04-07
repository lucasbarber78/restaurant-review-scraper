#!/usr/bin/env python3
"""
Google Reviews Scraper Module

This module handles the scraping of reviews from Google Maps/Reviews using Browserbase.
"""

import logging
import time
import re
import json
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from dateutil import parser
import urllib.parse

from src.utils.browser_utils import create_browser_session, close_browser_session

logger = logging.getLogger(__name__)


class GoogleScraper:
    """Scraper for Google Reviews."""
    
    def __init__(self, config):
        """Initialize the Google Reviews scraper.
        
        Args:
            config (dict): Configuration dictionary.
        """
        self.config = config
        self.place_id = config['google_place_id']
        self.restaurant_name = config['restaurant_name']
        self.start_date = datetime.strptime(config['date_range']['start'], '%Y-%m-%d')
        self.end_date = datetime.strptime(config['date_range']['end'], '%Y-%m-%d')
        self.max_reviews = config.get('max_reviews_per_platform', 0)
        self.timeout = config.get('timeout_seconds', 60)
        self.retry_attempts = config.get('retry_attempts', 3)
        self.scroll_pause_time = config.get('scroll_pause_time', 1.5)
        self.browser = None
        self.page = None
        
        # Construct Google Maps URL using place ID
        self.url = f"https://www.google.com/maps/place/?q=place_id:{self.place_id}"
        
        # Alternative URL using restaurant name if place ID fails
        self.search_url = f"https://www.google.com/maps/search/{urllib.parse.quote(self.restaurant_name)}"
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(Exception)
    )
    async def _navigate_to_reviews_page(self):
        """Navigate to the reviews section."""
        logger.info(f"Navigating to Google Maps URL: {self.url}")
        
        try:
            # Try with place ID first
            await self.page.goto(self.url, timeout=self.timeout * 1000)
            
            # Wait for the page to load
            await self.page.waitForSelector('h1', timeout=self.timeout * 1000)
            
            # Check if we landed on the right page
            title = await self.page.evaluate('() => document.querySelector("h1") ? document.querySelector("h1").textContent : ""')
            if self.restaurant_name.lower() not in title.lower():
                logger.warning(f"Page title '{title}' doesn't match restaurant name '{self.restaurant_name}'")
                
                # Try with search URL instead
                logger.info(f"Trying alternate search URL: {self.search_url}")
                await self.page.goto(self.search_url, timeout=self.timeout * 1000)
                
                # Wait for search results
                await self.page.waitForSelector('a[aria-label*="Results"]', timeout=self.timeout * 1000)
                
                # Click on the first result that matches our restaurant
                result_links = await self.page.querySelectorAll('a[aria-label*="Results"]')
                for link in result_links:
                    link_text = await self.page.evaluate('el => el.getAttribute("aria-label")', link)
                    if self.restaurant_name.lower() in link_text.lower():
                        await link.click()
                        await self.page.waitForNavigation()
                        break
            
            # Now look for the reviews section
            reviews_buttons = [
                'a[href*="reviews"]',
                'button[jsaction*="pane.rating.moreReviews"]',
                'button[aria-label*="reviews"]',
                'a[aria-label*="reviews"]',
                'div[role="button"][aria-label*="reviews"]'
            ]
            
            for selector in reviews_buttons:
                try:
                    review_button = await self.page.querySelector(selector)
                    if review_button:
                        await review_button.click()
                        logger.info("Clicked on reviews button")
                        await self.page.waitForTimeout(2000)
                        break
                except Exception as e:
                    logger.debug(f"Error clicking review button {selector}: {e}")
                    continue
            
            # Wait for reviews to load
            await self.page.waitForSelector('div[data-review-id]', timeout=self.timeout * 1000)
            
        except Exception as e:
            logger.error(f"Error navigating to Google reviews: {e}")
            raise
    
    async def _handle_cookies_popup(self):
        """Handle cookie consent popups if they appear."""
        try:
            # Look for various cookie consent buttons
            cookie_buttons = [
                'button[aria-label*="Accept"]',
                'button[aria-label*="agree"]',
                'button.VfPpkd-LgbsSe',
                'button[jsname="higCR"]'
            ]
            
            for selector in cookie_buttons:
                try:
                    buttons = await self.page.querySelectorAll(selector)
                    for button in buttons:
                        button_text = await self.page.evaluate('el => el.textContent', button)
                        if 'accept' in button_text.lower() or 'agree' in button_text.lower() or 'consent' in button_text.lower():
                            await button.click()
                            logger.info("Clicked cookie consent button")
                            await self.page.waitForTimeout(1000)
                            break
                except Exception:
                    continue
        except Exception as e:
            logger.warning(f"Error handling cookie popup: {e}")
    
    async def _sort_reviews_by_newest(self):
        """Sort reviews by newest first."""
        try:
            # Try to find and click on the sort button
            sort_buttons = [
                'button[aria-label*="Sort reviews"]',
                'button[data-value*="sort"]',
                'button[jsaction*="pane.review.sort"]'
            ]
            
            for selector in sort_buttons:
                sort_button = await self.page.querySelector(selector)
                if sort_button:
                    await sort_button.click()
                    logger.info("Clicked sort button")
                    await self.page.waitForTimeout(1000)
                    
                    # Look for the "newest" option
                    newest_options = [
                        'li[aria-label*="newest"]',
                        'span[aria-label*="newest"]',
                        'div[role="menuitemradio"]:has-text("newest")',
                        'div[role="menuitem"]:has-text("newest")'
                    ]
                    
                    for option_selector in newest_options:
                        try:
                            newest_option = await self.page.querySelector(option_selector)
                            if newest_option:
                                await newest_option.click()
                                logger.info("Selected newest first sort option")
                                await self.page.waitForTimeout(2000)  # Wait for reviews to reload
                                return
                        except Exception:
                            continue
        except Exception as e:
            logger.warning(f"Error sorting reviews by newest: {e}")
    
    async def _scroll_reviews(self):
        """Scroll through reviews to load more."""
        # Find the reviews container
        reviews_container = await self.page.querySelector('div[role="feed"]')
        if not reviews_container:
            logger.warning("Could not find reviews container")
            return
        
        previous_review_count = 0
        stall_count = 0
        reviews_loaded = 0
        
        while True:
            # Scroll the reviews container
            await self.page.evaluate('''
                document.querySelector('div[role="feed"]').scrollTop = 
                document.querySelector('div[role="feed"]').scrollHeight
            ''')
            
            # Wait for scrolling and loading
            await self.page.waitForTimeout(self.scroll_pause_time * 1000)
            
            # Expand all "More" buttons
            more_buttons = await self.page.querySelectorAll('button[jsaction*="pane.review.expandReview"]')
            for button in more_buttons:
                try:
                    await button.click()
                    await self.page.waitForTimeout(300)
                except Exception:
                    pass
            
            # Count reviews
            review_elements = await self.page.querySelectorAll('div[data-review-id]')
            reviews_loaded = len(review_elements)
            
            # Check if we've reached our review limit
            if self.max_reviews > 0 and reviews_loaded >= self.max_reviews:
                logger.info(f"Reached max reviews limit ({self.max_reviews})")
                break
                
            # Check if we've loaded new reviews
            if reviews_loaded == previous_review_count:
                stall_count += 1
                if stall_count >= 5:  # If we've stalled 5 times, assume we're done
                    logger.info("No new reviews loading, ending scroll")
                    break
            else:
                stall_count = 0
                
            previous_review_count = reviews_loaded
            logger.info(f"Loaded {reviews_loaded} Google reviews so far...")
    
    async def _extract_review_data(self):
        """Extract data from loaded reviews."""
        logger.info("Extracting review data from Google reviews...")
        
        reviews = []
        review_elements = await self.page.querySelectorAll('div[data-review-id]')
        
        for i, review_element in enumerate(review_elements):
            try:
                # Extract reviewer name
                name_element = await review_element.querySelector('.d4r55')
                reviewer_name = await self.page.evaluate('el => el.textContent', name_element) if name_element else "Anonymous"
                
                # Extract rating
                rating_element = await review_element.querySelector('span[role="img"]')
                rating_text = await self.page.evaluate('el => el.getAttribute("aria-label")', rating_element) if rating_element else ""
                rating_match = re.search(r'(\d+) stars?', rating_text)
                rating = int(rating_match.group(1)) if rating_match else 0
                
                # Extract review date
                date_element = await review_element.querySelector('.rsqaWe')
                date_text = await self.page.evaluate('el => el.textContent', date_element) if date_element else ""
                
                # Parse the date
                try:
                    # Google often uses relative dates like "2 weeks ago", "a month ago", etc.
                    review_date = parser.parse(date_text, fuzzy=True)
                except ValueError:
                    # Handle relative dates more explicitly
                    current_date = datetime.now()
                    
                    if 'week' in date_text.lower():
                        # Extract number of weeks
                        weeks_match = re.search(r'(\d+)\s+weeks?', date_text.lower())
                        weeks = int(weeks_match.group(1)) if weeks_match else 1
                        review_date = current_date.replace(day=current_date.day - (weeks * 7))
                    elif 'month' in date_text.lower():
                        # Extract number of months
                        months_match = re.search(r'(\d+)\s+months?', date_text.lower())
                        months = int(months_match.group(1)) if months_match else 1
                        new_month = current_date.month - months
                        new_year = current_date.year
                        if new_month <= 0:
                            new_month += 12
                            new_year -= 1
                        review_date = current_date.replace(year=new_year, month=new_month)
                    elif 'day' in date_text.lower() or 'yesterday' in date_text.lower():
                        # Extract number of days
                        if 'yesterday' in date_text.lower():
                            days = 1
                        else:
                            days_match = re.search(r'(\d+)\s+days?', date_text.lower())
                            days = int(days_match.group(1)) if days_match else 1
                        review_date = current_date.replace(day=current_date.day - days)
                    elif 'year' in date_text.lower():
                        # Extract number of years
                        years_match = re.search(r'(\d+)\s+years?', date_text.lower())
                        years = int(years_match.group(1)) if years_match else 1
                        review_date = current_date.replace(year=current_date.year - years)
                    else:
                        # Default to current date if parsing fails
                        review_date = current_date
                
                # Filter by date range
                if not (self.start_date <= review_date.replace(tzinfo=None) <= self.end_date):
                    continue
                
                # Extract review text
                text_element = await review_element.querySelector('.wiI7pd')
                review_text = await self.page.evaluate('el => el.textContent', text_element) if text_element else ""
                review_text = review_text.strip()
                
                # Create review object
                review = {
                    'platform': 'Google',
                    'reviewer_name': reviewer_name.strip(),
                    'date': review_date.strftime('%Y-%m-%d'),
                    'rating': rating,
                    'title': "",  # Google reviews don't have titles
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
                logger.warning(f"Failed to extract Google review {i}: {e}")
        
        logger.info(f"Extracted {len(reviews)} Google reviews in the specified date range")
        return reviews
    
    def scrape(self):
        """Scrape reviews from Google.
        
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
            logger.error(f"Error during Google reviews scraping: {e}", exc_info=True)
        finally:
            # Close browser session
            close_browser_session(self.browser)
        
        return reviews
    
    async def _scrape_async(self):
        """Async implementation of the scraping process."""
        try:
            # Navigate to Google reviews page
            await self._navigate_to_reviews_page()
            
            # Handle any cookie popups
            await self._handle_cookies_popup()
            
            # Sort reviews by newest first if possible
            await self._sort_reviews_by_newest()
            
            # Scroll to load more reviews
            await self._scroll_reviews()
            
            # Extract review data
            reviews = await self._extract_review_data()
            
            return reviews
            
        except Exception as e:
            logger.error(f"Error during async Google reviews scraping: {e}", exc_info=True)
            return []


if __name__ == "__main__":
    # Standalone usage example
    import yaml
    
    logging.basicConfig(level=logging.INFO)
    
    with open("config.yaml", 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    
    scraper = GoogleScraper(config)
    scraped_reviews = scraper.scrape()
    
    print(f"Scraped {len(scraped_reviews)} reviews")
    for review in scraped_reviews[:5]:
        print(json.dumps(review, indent=2))
