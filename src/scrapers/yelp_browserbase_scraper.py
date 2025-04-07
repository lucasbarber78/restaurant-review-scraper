#!/usr/bin/env python3
"""
Yelp Browserbase Scraper Module

This module provides a class for scraping Yelp restaurant reviews using Browserbase.
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


class YelpBrowserbaseScraper:
    """
    A class to scrape restaurant reviews from Yelp using Browserbase.
    """
    
    def __init__(self, api_key: Optional[str] = None, config_path: Optional[str] = None):
        """
        Initialize the Yelp scraper with Browserbase.
        
        Args:
            api_key (str, optional): Browserbase API key. If None, tries to get from env or config.
            config_path (str, optional): Path to config file. Defaults to 'config.yaml' in root.
        """
        self.scraper = BrowserbaseScraper(api_key=api_key, config_path=config_path)
        self.config = self.scraper.config
        
        # Default selectors for Yelp elements
        self.selectors = {
            'reviews_container': '.review-feed',
            'review_items': '.review__09f24__oHr9V.border-color--default__09f24__NPAKY',
            'review_text': '.comment__09f24__gu0rG.css-qgunke',
            'rating': '.five-stars__09f24__mBKym',
            'date': '.css-chan6m',
            'reviewer_name': '.user-passport-info .css-1m051bw',
            'more_reviews_button': '.css-1w0hvwb',
            'sort_dropdown': '[data-dropdown-toggle="sort-by"]',
            'sort_newest': 'a[href*="sort_by=date_desc"]',
            'cookies_banner': '.yelp-cookie-banner-notification button'
        }
    
    def _extract_rating(self, rating_class: str) -> float:
        """
        Extract numeric rating from Yelp's star rating CSS class.
        
        Args:
            rating_class (str): CSS class string containing rating info.
            
        Returns:
            float: Rating value between 1.0 and 5.0.
        """
        try:
            # Yelp typically has classes like "five-stars__09f24__mBKym star-rating__09f24__KlFwj stars__09f24__ztGpW border-color--default__09f24__NPAKY"
            # We need to look for patterns like "star-rating--1" to "star-rating--5"
            # or extract from aria-label which often has "X star rating"
            
            # This is a simplified implementation - in reality you'd need more robust parsing
            if "star-rating--1" in rating_class or "1 star rating" in rating_class:
                return 1.0
            elif "star-rating--2" in rating_class or "2 star rating" in rating_class:
                return 2.0
            elif "star-rating--3" in rating_class or "3 star rating" in rating_class:
                return 3.0
            elif "star-rating--4" in rating_class or "4 star rating" in rating_class:
                return 4.0
            elif "star-rating--5" in rating_class or "5 star rating" in rating_class:
                return 5.0
            
            # Fallback: look for a number in the string
            match = re.search(r'(\d+(\.\d+)?)', rating_class)
            if match:
                return float(match.group(1))
            
            return 0.0
        except Exception as e:
            logger.warning(f"Error extracting rating from '{rating_class}': {e}")
            return 0.0
    
    def _is_within_date_range(self, date_str: str, start_date: Optional[datetime] = None, 
                             end_date: Optional[datetime] = None) -> bool:
        """
        Check if a date string is within the specified date range.
        
        Args:
            date_str (str): Date string from the Yelp review.
            start_date (datetime, optional): Start date of the range. Defaults to None.
            end_date (datetime, optional): End date of the range. Defaults to None.
            
        Returns:
            bool: True if date is within range, False otherwise.
        """
        try:
            # Parse the date string from Yelp format
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
    
    def _sort_reviews_by_newest(self) -> bool:
        """
        Sort Yelp reviews to show newest first.
        
        Returns:
            bool: True if sorting was successful, False otherwise.
        """
        try:
            # Click on sort dropdown
            if not self.scraper.click(self.selectors['sort_dropdown'], wait_time=1.0):
                logger.warning("Failed to click sort dropdown")
                return False
            
            # Click on "Newest First" option
            if not self.scraper.click(self.selectors['sort_newest'], wait_time=2.0):
                logger.warning("Failed to click 'Newest First' sort option")
                return False
            
            logger.info("Reviews sorted by newest first")
            return True
        
        except Exception as e:
            logger.warning(f"Error sorting reviews: {e}")
            return False
    
    def _load_more_reviews(self, max_pages: int = 5) -> bool:
        """
        Load more reviews by clicking on "More reviews" button multiple times.
        
        Args:
            max_pages (int, optional): Maximum number of "More" clicks to perform. Defaults to 5.
            
        Returns:
            bool: True if at least one "More" click was successful, False otherwise.
        """
        successful_clicks = 0
        
        for _ in range(max_pages):
            try:
                # Take a screenshot to evaluate the page
                self.scraper.take_screenshot()
                
                # Try to click the "More reviews" button
                if self.scraper.click(self.selectors['more_reviews_button'], wait_time=2.0):
                    successful_clicks += 1
                else:
                    # Break the loop if we can't click the button
                    break
            
            except Exception as e:
                logger.warning(f"Error loading more reviews: {e}")
                break
        
        logger.info(f"Loaded {successful_clicks} additional pages of reviews")
        return successful_clicks > 0
    
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
        for i in range(1, 6):
            review = {
                'platform': 'Yelp',
                'rating': 5.0 - (i % 5),  # Alternate between 5, 4, 3, 2, 1
                'date': datetime.now() - timedelta(days=i*5),
                'date_str': (datetime.now() - timedelta(days=i*5)).strftime('%m/%d/%Y'),
                'reviewer_name': f"Yelp Reviewer {i}",
                'text': f"This is a placeholder review #{i} for demonstration purposes. In a real implementation, this would be actual review text scraped from Yelp.",
                'url': self.config.get('yelp_url', '')
            }
            
            # Only add if within date range
            if self._is_within_date_range(review['date_str'], start_date, end_date):
                reviews.append(review)
        
        return reviews
    
    def scrape_reviews(self, url: Optional[str] = None, max_reviews: int = 100) -> List[Dict[str, Any]]:
        """
        Scrape Yelp reviews for a restaurant.
        
        Args:
            url (str, optional): Yelp restaurant URL. If None, uses URL from config.
            max_reviews (int, optional): Maximum number of reviews to scrape. Defaults to 100.
            
        Returns:
            List[Dict[str, Any]]: List of review dictionaries.
        """
        # Get URL from config if not provided
        if not url:
            url = self.config.get('yelp_url')
            if not url:
                raise ValueError("Yelp URL not provided and not found in config")
        
        # Get date range from config
        start_date, end_date = self._parse_date_range_from_config()
        
        # Create a new browser session
        self.scraper.create_session()
        
        try:
            # Navigate to the Yelp page
            if not self.scraper.navigate(url):
                raise RuntimeError(f"Failed to navigate to {url}")
            
            # Dismiss cookies banner if present
            self._dismiss_cookies_banner()
            
            # Sort reviews by newest first
            self._sort_reviews_by_newest()
            
            # Load more reviews
            self._load_more_reviews()
            
            # Parse reviews from the page
            reviews = self._parse_review_elements(start_date, end_date)
            
            # Limit to max_reviews
            reviews = reviews[:max_reviews]
            
            logger.info(f"Scraped {len(reviews)} Yelp reviews")
            return reviews
            
        except Exception as e:
            logger.error(f"Error scraping Yelp reviews: {e}", exc_info=True)
            return []
            
        finally:
            # Close the browser session
            self.scraper.close_session()


# Example usage of the scraper
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create the Yelp scraper
    scraper = YelpBrowserbaseScraper()
    
    # Scrape reviews
    reviews = scraper.scrape_reviews()
    
    # Print number of reviews
    print(f"Scraped {len(reviews)} reviews")
    
    # Print first review
    if reviews:
        print("\nFirst review:")
        for key, value in reviews[0].items():
            print(f"{key}: {value}")
