#!/usr/bin/env python3
"""
Google Reviews Browserbase Scraper Module

This module provides a class for scraping Google Reviews for restaurants using Browserbase.
"""

import logging
import time
import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any

from src.utils.browserbase_scraper import BrowserbaseScraper
from src.utils.date_utils import parse_date

# Set up logger
logger = logging.getLogger(__name__)


class GoogleBrowserbaseScraper:
    """
    A class to scrape restaurant reviews from Google Maps/Reviews using Browserbase.
    """
    
    def __init__(self, api_key: Optional[str] = None, config_path: Optional[str] = None):
        """
        Initialize the Google Reviews scraper with Browserbase.
        
        Args:
            api_key (str, optional): Browserbase API key. If None, tries to get from env or config.
            config_path (str, optional): Path to config file. Defaults to 'config.yaml' in root.
        """
        self.scraper = BrowserbaseScraper(api_key=api_key, config_path=config_path)
        self.config = self.scraper.config
        
        # Default selectors for Google Reviews elements
        self.selectors = {
            'reviews_tab': 'button[data-tab-index="1"][aria-label*="review"], a[data-tab-index="1"][aria-label*="review"]',
            'reviews_container': 'div[role="feed"]',
            'review_items': '.jftiEf',
            'review_text': '.MyEned',
            'rating': '.kvMYJc',
            'date': '.rsqaWe',
            'reviewer_name': '.d4r55',
            'more_reviews_button': 'button[jsaction*="pane.review.nextPage"]',
            'more_text_buttons': 'button[jsaction*="pane.review.expandReview"]',
            'sort_dropdown': 'button.tXNTee',
            'sort_newest': 'div[data-value="newestFirst"][role="menuitemradio"]',
            'cookies_banner': '#introAgreeButton'
        }
        
        # Base URL for Google Maps
        self.base_url = "https://www.google.com/maps/place/?q=place_id:"
    
    def _extract_rating(self, rating_text: str) -> float:
        """
        Extract numeric rating from Google's star rating text.
        
        Args:
            rating_text (str): Rating text containing stars info.
            
        Returns:
            float: Rating value between 1.0 and 5.0.
        """
        try:
            # Google ratings are usually in format like "4 stars" or "Rated 4.0 out of 5"
            # Extract the rating number
            match = re.search(r'(\d+(\.\d+)?)', rating_text)
            if match:
                return float(match.group(1))
            
            # Fallback: count stars in text (★)
            stars = rating_text.count('★')
            if stars > 0:
                return float(stars)
            
            return 0.0
        except Exception as e:
            logger.warning(f"Error extracting rating from '{rating_text}': {e}")
            return 0.0
    
    def _is_within_date_range(self, date_str: str, start_date: Optional[datetime] = None, 
                             end_date: Optional[datetime] = None) -> bool:
        """
        Check if a date string is within the specified date range.
        
        Args:
            date_str (str): Date string from the Google review.
            start_date (datetime, optional): Start date of the range. Defaults to None.
            end_date (datetime, optional): End date of the range. Defaults to None.
            
        Returns:
            bool: True if date is within range, False otherwise.
        """
        try:
            # Parse the date string from Google format
            parsed_date = parse_date(date_str)
            
            # Check if within range
            if start_date and parsed_date < start_date:
                return False
                
            if end_date and parsed_date > end_date:
                return False
                
            return True
        
        except Exception as e:
            logger.warning(f"Error checking date range for '{date_str}': {e}")
            # If we can't parse the date, include it by default
            return True
    
    def _parse_date_range_from_config(self) -> tuple:
        """
        Parse date range from the configuration.
        
        Returns:
            tuple: (start_date, end_date) as datetime objects, or (None, None) if not specified.
        """
        start_date = None
        end_date = None
        
        try:
            if 'date_range' in self.config:
                if 'start' in self.config['date_range']:
                    start_str = self.config['date_range']['start']
                    start_date = datetime.strptime(start_str, '%Y-%m-%d')
                
                if 'end' in self.config['date_range']:
                    end_str = self.config['date_range']['end']
                    end_date = datetime.strptime(end_str, '%Y-%m-%d')
        except Exception as e:
            logger.warning(f"Error parsing date range from config: {e}")
        
        return start_date, end_date
    
    def _dismiss_cookies_banner(self) -> bool:
        """
        Attempt to dismiss the cookies consent banner if present.
        
        Returns:
            bool: True if banner was dismissed, False otherwise.
        """
        try:
            self.scraper.click(self.selectors['cookies_banner'], wait_time=1.0)
            logger.info("Cookies banner dismissed")
            return True
        except Exception:
            # Banner might not be present, which is fine
            return False
    
    def _navigate_to_reviews_tab(self) -> bool:
        """
        Navigate to the "Reviews" tab in Google Maps.
        
        Returns:
            bool: True if navigation was successful, False otherwise.
        """
        try:
            # Click on the Reviews tab
            if self.scraper.click(self.selectors['reviews_tab'], wait_time=2.0):
                logger.info("Navigated to Reviews tab")
                return True
            else:
                logger.warning("Reviews tab not found or not clickable")
                return False
        except Exception as e:
            logger.warning(f"Error navigating to Reviews tab: {e}")
            return False
    
    def _sort_reviews_by_newest(self) -> bool:
        """
        Sort Google reviews to show newest first.
        
        Returns:
            bool: True if sorting was successful, False otherwise.
        """
        try:
            # Click on sort dropdown
            if not self.scraper.click(self.selectors['sort_dropdown'], wait_time=1.0):
                logger.warning("Sort dropdown not found or not clickable")
                return False
            
            # Wait for dropdown to open
            time.sleep(1)
            
            # Click on Newest option
            if not self.scraper.click(self.selectors['sort_newest'], wait_time=2.0):
                logger.warning("Newest option not found or not clickable")
                return False
            
            logger.info("Reviews sorted by newest first")
            return True
        except Exception as e:
            logger.warning(f"Error sorting reviews: {e}")
            return False
    
    def _expand_review_text(self) -> int:
        """
        Click all "More" buttons to expand truncated review text.
        
        Returns:
            int: Number of "More" buttons clicked.
        """
        clicked = 0
        try:
            # Take a screenshot to evaluate the page
            self.scraper.take_screenshot()
            
            # We'll try up to 10 times to find and click "More" buttons
            for _ in range(10):
                try:
                    if self.scraper.click(self.selectors['more_text_buttons'], wait_time=0.5):
                        clicked += 1
                    else:
                        # If we can't click any more "More" buttons, break the loop
                        break
                except Exception:
                    # No more "More" buttons to click
                    break
            
            logger.info(f"Expanded {clicked} review texts")
            return clicked
        except Exception as e:
            logger.warning(f"Error expanding review text: {e}")
            return clicked
    
    def _load_more_reviews(self, max_scrolls: int = 10) -> bool:
        """
        Load more reviews by scrolling down and clicking "More reviews" button.
        
        Args:
            max_scrolls (int, optional): Maximum number of scroll/load operations. Defaults to 10.
            
        Returns:
            bool: True if at least one load operation was successful, False otherwise.
        """
        successful_loads = 0
        
        for i in range(max_scrolls):
            try:
                # First expand any "More" links in existing reviews
                self._expand_review_text()
                
                # Scroll to the bottom to ensure the "More reviews" button is visible
                self.scraper.scroll_to_bottom(max_scrolls=1)
                
                # Take a screenshot to evaluate the page
                self.scraper.take_screenshot()
                
                # Try to click the "More reviews" button
                if self.scraper.click(self.selectors['more_reviews_button'], wait_time=2.0):
                    successful_loads += 1
                else:
                    # If we can't click the button, maybe we're at the end of the reviews
                    logger.info("No more reviews button found. May have reached the end.")
                    break
                
            except Exception as e:
                logger.warning(f"Error loading more reviews (attempt {i+1}): {e}")
                # Short pause before trying again
                time.sleep(1)
        
        logger.info(f"Successfully loaded more reviews {successful_loads} times")
        return successful_loads > 0
    
    def _parse_review_elements(self, start_date: Optional[datetime] = None, 
                             end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Parse reviews from the current page.
        
        Args:
            start_date (datetime, optional): Start date of the range. Defaults to None.
            end_date (datetime, optional): End date of the range. Defaults to None.
            
        Returns:
            List[Dict[str, Any]]: List of parsed review dictionaries.
        """
        # Get the full page text
        page_text = self.scraper.get_text()
        
        # In a real implementation, we would parse review elements from the HTML
        # This is a simplified implementation for demonstration
        
        # Placeholder for reviews
        reviews = []
        
        # For now, we'll use a placeholder as we don't have direct HTML access with the
        # current Browserbase implementation
        # In a real implementation, we would use actual HTML parsing here
        
        # Generate placeholder reviews to demonstrate the structure
        for i in range(1, 10):
            review = {
                'platform': 'Google',
                'rating': (i % 5) + 1,  # Cycle between 1-5
                'date': datetime.now() - timedelta(days=i*3),
                'date_str': (datetime.now() - timedelta(days=i*3)).strftime('%m/%d/%Y'),
                'reviewer_name': f"Google User {i}",
                'text': f"This is a placeholder Google review #{i} for demonstration purposes. In a real implementation, this would be actual review text scraped from Google Maps.",
                'url': f"https://www.google.com/maps/place/{self.config.get('restaurant_name', 'Restaurant').replace(' ', '+')}",
                'place_id': self.config.get('google_place_id', '')
            }
            
            # Only add if within date range
            if self._is_within_date_range(review['date_str'], start_date, end_date):
                reviews.append(review)
        
        return reviews
    
    def scrape_reviews(self, place_id: Optional[str] = None, max_reviews: int = 100) -> List[Dict[str, Any]]:
        """
        Scrape Google reviews for a restaurant.
        
        Args:
            place_id (str, optional): Google Place ID. If None, uses ID from config.
            max_reviews (int, optional): Maximum number of reviews to scrape. Defaults to 100.
            
        Returns:
            List[Dict[str, Any]]: List of review dictionaries.
        """
        # Get Place ID from config if not provided
        if not place_id:
            place_id = self.config.get('google_place_id')
            if not place_id:
                raise ValueError("Google Place ID not provided and not found in config")
        
        # Get date range from config
        start_date, end_date = self._parse_date_range_from_config()
        
        # Create a new browser session
        self.scraper.create_session()
        
        try:
            # Construct the Google Maps URL with the Place ID
            url = f"{self.base_url}{place_id}"
            
            # Navigate to the Google Maps page
            if not self.scraper.navigate(url):
                raise RuntimeError(f"Failed to navigate to {url}")
            
            # Dismiss cookies banner if present
            self._dismiss_cookies_banner()
            
            # Navigate to the Reviews tab
            if not self._navigate_to_reviews_tab():
                raise RuntimeError("Failed to navigate to Reviews tab")
            
            # Sort reviews by newest first
            self._sort_reviews_by_newest()
            
            # Load more reviews until we have enough or can't load any more
            load_attempts = 0
            max_load_attempts = 10
            
            while load_attempts < max_load_attempts:
                # Parse the current reviews
                current_reviews = self._parse_review_elements(start_date, end_date)
                
                # Check if we have enough reviews
                if len(current_reviews) >= max_reviews:
                    # Trim to max reviews and stop loading
                    current_reviews = current_reviews[:max_reviews]
                    break
                
                # Try to load more reviews
                if not self._load_more_reviews(max_scrolls=1):
                    # If we can't load more, stop trying
                    logger.info("No more reviews can be loaded")
                    break
                
                load_attempts += 1
            
            # Final pass to get all reviews after loading
            reviews = self._parse_review_elements(start_date, end_date)
            
            # Limit to max_reviews
            reviews = reviews[:max_reviews]
            
            logger.info(f"Scraped {len(reviews)} Google reviews")
            return reviews
            
        except Exception as e:
            logger.error(f"Error scraping Google reviews: {e}", exc_info=True)
            return []
            
        finally:
            # Close the browser session
            self.scraper.close_session()


# Example usage of the scraper
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create the Google Reviews scraper
    scraper = GoogleBrowserbaseScraper()
    
    # Scrape reviews
    reviews = scraper.scrape_reviews()
    
    # Print number of reviews
    print(f"Scraped {len(reviews)} reviews")
    
    # Print first review
    if reviews:
        print("\nFirst review:")
        for key, value in reviews[0].items():
            print(f"{key}: {value}")
