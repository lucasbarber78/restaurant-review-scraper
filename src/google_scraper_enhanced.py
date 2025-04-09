#!/usr/bin/env python3
"""
Enhanced Google Reviews Scraper Module

This module handles the scraping of reviews from Google Maps using advanced anti-bot
detection measures including random delays, proxy rotation, and stealth plugins.
"""

import logging
import time
import re
import json
import random
import yaml
import os
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from dateutil import parser
import asyncio

# Import our utility modules
from src.utils.browser_utils import create_browser_session, close_browser_session
from src.utils.delay_utils import get_random_delay, delay_between_actions, simulate_human_typing
from src.utils.proxy_rotation import ProxyRotator, get_browserbase_api_key
from src.utils.stealth_plugins import StealthEnhancer, apply_stealth_measures

logger = logging.getLogger(__name__)

class EnhancedGoogleScraper:
    """Advanced scraper for Google Maps reviews with anti-bot detection measures."""
    
    def __init__(self, config):
        """Initialize the enhanced Google Maps reviews scraper.
        
        Args:
            config (dict): Configuration dictionary.
        """
        self.config = config
        self.url = config['google_url']
        self.start_date = datetime.strptime(config['date_range']['start'], '%Y-%m-%d')
        self.end_date = datetime.strptime(config['date_range']['end'], '%Y-%m-%d')
        self.max_reviews = config.get('max_reviews_per_platform', 0)
        self.timeout = config.get('timeout_seconds', 60)
        self.retry_attempts = config.get('retry_attempts', 3)
        
        # Anti-bot detection settings
        self.anti_bot_settings = config.get('anti_bot_settings', {})
        self.use_random_delays = self.anti_bot_settings.get('enable_random_delays', True)
        self.use_proxy_rotation = self.anti_bot_settings.get('enable_proxy_rotation', False)
        self.use_stealth_plugins = self.anti_bot_settings.get('enable_stealth_plugins', True)
        self.headless_mode = self.anti_bot_settings.get('headless_mode', False)
        self.simulate_human = self.anti_bot_settings.get('simulate_human_behavior', True)
        
        # Set scroll pause time with potential randomization
        base_scroll_time = config.get('scroll_pause_time', 1.5)
        if self.use_random_delays:
            self.scroll_pause_time = get_random_delay(base_scroll_time, 0.5)
        else:
            self.scroll_pause_time = base_scroll_time
            
        # Initialize proxy rotator if enabled
        self.proxy_rotator = None
        if self.use_proxy_rotation:
            self.proxy_rotator = ProxyRotator()
            
        # Initialize stealth enhancer for Google
        self.stealth_enhancer = None
        if self.use_stealth_plugins:
            self.stealth_enhancer = StealthEnhancer("google")
            
        # Browser and page objects
        self.browser = None
        self.page = None
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(Exception)
    )
    async def _navigate_to_reviews_page(self):
        """Navigate to the Google Maps page and find the reviews section."""
        logger.info(f"Navigating to Google Maps URL: {self.url}")
        
        # Use randomized delay for navigation
        if self.use_random_delays:
            delay = delay_between_actions("navigation")
            logger.debug(f"Adding navigation delay of {delay:.2f}s")
        
        # Navigate to URL
        await self.page.goto(self.url, timeout=self.timeout * 1000)
        
        # Simulate human behavior if enabled
        if self.simulate_human and self.stealth_enhancer:
            await self.stealth_enhancer.simulate_human_behavior(self.page)
        
        # Wait for the page to load fully
        if self.use_random_delays:
            timeout_with_jitter = self.timeout * (1 + random.uniform(-0.1, 0.2))
        else:
            timeout_with_jitter = self.timeout
        
        # Wait for the map to load
        await self.page.waitForSelector('div[role="main"]', timeout=timeout_with_jitter * 1000)
        
        # Try to find and click on the reviews section with human-like behavior
        try:
            # Different selectors for reviews button/tab
            review_button_selectors = [
                'button[jsaction*="pane.rating.morereviews"]',
                'button[aria-label*="reviews"]',
                'button.reviews-button',
                'div[role="button"][jsaction*="pane.reviewChart"]',
                'a[href*="reviews"]',
                'div[jsaction*="reviews"]'
            ]
            
            for selector in review_button_selectors:
                review_button = await self.page.querySelector(selector)
                if review_button:
                    # Add delay before clicking for human-like behavior
                    if self.use_random_delays:
                        delay_between_actions("click")
                        
                    # Click the reviews button
                    await review_button.click()
                    logger.info("Clicked on reviews section")
                    
                    # Wait for reviews to load
                    await self.page.waitForSelector('div.review-dialog-list', timeout=timeout_with_jitter * 1000)
                    break
            else:
                # If we didn't find a dedicated reviews button, the page might already be showing reviews
                logger.info("No reviews button found, checking if reviews are already visible")
                
                # Check if reviews are already visible
                reviews_visible = await self.page.evaluate("""
                    () => {
                        const reviewElements = document.querySelectorAll('div[data-review-id], div[jsdata*="review"]');
                        return reviewElements.length > 0;
                    }
                """)
                
                if not reviews_visible:
                    logger.warning("Reviews section not found")
                    # Take a screenshot for debugging
                    await self.page.screenshot({'path': 'debug_google_no_reviews.png'})
        
        except Exception as e:
            logger.warning(f"Error navigating to reviews: {e}")
            # Take screenshot for debugging
            await self.page.screenshot({'path': 'debug_google_navigation.png'})
            raise
    
    async def _handle_cookies_popup(self):
        """Handle cookie consent popups with human-like behavior."""
        try:
            # Look for various cookie consent buttons
            cookie_buttons = [
                'button[jsname="b3VHJd"]',  # Google's "Accept all" button
                'button[jsname="higCR"]',   # Google's "Customize" button
                'button[aria-label*="Accept"]',
                'button[data-tracking-consent="accept-all"]',
                'button.cookie-consent__button'
            ]
            
            for selector in cookie_buttons:
                try:
                    button = await self.page.querySelector(selector)
                    if button:
                        # Add delay before clicking for human-like behavior
                        if self.use_random_delays:
                            delay_between_actions("click")
                            
                        await button.click()
                        logger.info("Clicked cookie consent button")
                        
                        # Add post-click delay
                        await self.page.waitForTimeout(get_random_delay(1.0, 0.3) * 1000)
                        break
                except Exception:
                    continue
        except Exception as e:
            logger.warning(f"Error handling cookie popup: {e}")
    
    async def _handle_popups(self):
        """Handle various popups that might appear during scraping."""
        try:
            # Check for sign-in prompts
            signin_close_buttons = [
                'button[aria-label="Close"]',
                'button[jsname="Sx9Kwc"]',   # Google's "No thanks" button
                'button[jsname="tJiF1e"]',   # Google's "Close" button
                'div[jsname="c6xFrd"]'       # Close button on Google sign-in popup
            ]
            
            for selector in signin_close_buttons:
                try:
                    button = await self.page.querySelector(selector)
                    if button:
                        # Add pre-click delay for human-like behavior
                        if self.use_random_delays:
                            delay_between_actions("click")
                            
                        await button.click()
                        logger.info("Closed sign-in popup")
                        
                        # Add post-click delay
                        await self.page.waitForTimeout(get_random_delay(1.0, 0.3) * 1000)
                        break
                except Exception:
                    continue
                    
            # Check for other popups
            other_popup_buttons = [
                'button[jsname="gxjiv"]',  # Generic Google popup close button
                'button[jsname="OrQHOe"]'  # "Remind me later" button
            ]
            
            for selector in other_popup_buttons:
                try:
                    button = await self.page.querySelector(selector)
                    if button:
                        if self.use_random_delays:
                            delay_between_actions("click")
                            
                        await button.click()
                        logger.info("Closed popup")
                        
                        if self.use_random_delays:
                            await self.page.waitForTimeout(get_random_delay(1.0, 0.3) * 1000)
                        break
                except Exception:
                    continue
                    
        except Exception as e:
            logger.warning(f"Error handling popups: {e}")
    
    async def _filter_reviews(self):
        """Sort reviews with human-like interaction."""
        try:
            # Use randomized delay before filtering
            if self.use_random_delays:
                delay_between_actions("click")
            
            # Look for sort dropdown
            sort_dropdown_selectors = [
                'button[aria-label*="Sort reviews"]',
                'button[data-value="sort"]',
                'div[role="button"][jsaction*="sort"]'
            ]
            
            for selector in sort_dropdown_selectors:
                sort_dropdown = await self.page.querySelector(selector)
                if sort_dropdown:
                    # Add delay before clicking
                    if self.use_random_delays:
                        delay_between_actions("click")
                        
                    await sort_dropdown.click()
                    logger.info("Clicked sort dropdown")
                    
                    # Wait for dropdown to appear
                    await self.page.waitForTimeout(get_random_delay(1.0, 0.3) * 1000)
                    
                    # Find and click "Newest" option
                    newest_option_selectors = [
                        'li[aria-label*="Newest"]',
                        'span[jsname][data-value*="newest"]',
                        'span:has-text("Newest")'
                    ]
                    
                    for option_selector in newest_option_selectors:
                        newest_option = await self.page.querySelector(option_selector)
                        if newest_option:
                            if self.use_random_delays:
                                delay_between_actions("click")
                                
                            await newest_option.click()
                            logger.info("Selected newest first sorting")
                            
                            # Wait for reviews to reload
                            if self.use_random_delays:
                                await self.page.waitForTimeout(get_random_delay(2.0, 0.5) * 1000)
                            else:
                                await self.page.waitForTimeout(2000)
                            break
                    break
        except Exception as e:
            logger.warning(f"Error applying review filters: {e}")
    
    async def _scroll_reviews(self):
        """Scroll through reviews with human-like behavior."""
        # Find the reviews container
        reviews_container_selectors = [
            'div.review-dialog-list',
            'div[jsname="WMgU0"]',  # Google's reviews container
            'div[jsdata*="review"]'
        ]
        
        reviews_container = None
        for selector in reviews_container_selectors:
            container = await self.page.querySelector(selector)
            if container:
                reviews_container = container
                break
        
        if not reviews_container:
            logger.warning("Reviews container not found, trying to scroll the main page")
            # If we can't find a dedicated reviews container, use the main page
            reviews_container = await self.page.querySelector('div[role="main"]')
        
        if not reviews_container:
            logger.error("Couldn't find any scrollable container")
            return
            
        # Initial check of reviews
        reviews_loaded = 0
        last_review_count = 0
        stall_count = 0
        
        # Track scrolling behavior for realistic patterns
        scroll_count = 0
        
        # Get container handle for scrolling
        container_handle = reviews_container
        
        while True:
            # Increment scroll counter
            scroll_count += 1
            
            # Randomize scrolling behavior
            if self.use_random_delays and self.simulate_human:
                # Occasionally pause for a longer time (simulating user reading)
                if random.random() < 0.2:  # 20% chance
                    longer_pause = random.uniform(3.0, 8.0)
                    logger.debug(f"Simulating reading pause for {longer_pause:.2f}s")
                    await self.page.waitForTimeout(longer_pause * 1000)
                
                # Occasionally scroll up a bit before continuing down
                if scroll_count > 2 and random.random() < 0.15:  # 15% chance after 2nd scroll
                    scroll_up_amount = random.randint(100, 300)
                    logger.debug(f"Scrolling up {scroll_up_amount}px to simulate human behavior")
                    
                    # Scroll up in the reviews container
                    await self.page.evaluate(f"""
                        (container) => {{
                            container.scrollBy(0, -{scroll_up_amount});
                        }}
                    """, container_handle)
                    
                    await self.page.waitForTimeout(get_random_delay(0.8, 0.2) * 1000)
            
            # Scroll down with variable distance
            if self.use_random_delays and self.simulate_human:
                # Varied scroll distances instead of full viewport
                scroll_amount = random.randint(300, 800)
                
                # Scroll down in the reviews container
                await self.page.evaluate(f"""
                    (container) => {{
                        container.scrollBy(0, {scroll_amount});
                    }}
                """, container_handle)
            else:
                # Standard scroll by viewport height
                await self.page.evaluate("""
                    (container) => {
                        container.scrollBy(0, container.clientHeight);
                    }
                """, container_handle)
            
            # Randomized pause between scrolls
            if self.use_random_delays:
                await self.page.waitForTimeout(get_random_delay(self.scroll_pause_time, 0.5) * 1000)
            else:
                await self.page.waitForTimeout(self.scroll_pause_time * 1000)
            
            # Expand review text by clicking "More" buttons
            more_buttons = await self.page.querySelectorAll('button[jsaction*="pane.review.expandReview"]')
            
            # Only click a random subset of "More" buttons to appear human-like
            if self.simulate_human and len(more_buttons) > 0:
                # Randomly select only some buttons to click
                buttons_to_click = random.sample(
                    more_buttons, 
                    min(len(more_buttons), random.randint(1, min(3, len(more_buttons))))
                )
                
                for button in buttons_to_click:
                    try:
                        if self.use_random_delays:
                            delay_between_actions("click")
                        
                        await button.click()
                        
                        if self.use_random_delays:
                            await self.page.waitForTimeout(get_random_delay(0.5, 0.2) * 1000)
                        else:
                            await self.page.waitForTimeout(500)
                    except Exception:
                        pass
            else:
                # Default behavior: try to click all more buttons
                for button in more_buttons:
                    try:
                        await button.click()
                        await self.page.waitForTimeout(500)
                    except Exception:
                        pass
            
            # Check if we've reached our review limit
            current_reviews = await self.page.querySelectorAll('div[data-review-id], div[jsdata*="review"]')
            reviews_loaded = len(current_reviews)
            
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
            
            # Periodically check for CAPTCHA if stealth plugins are enabled
            if self.use_stealth_plugins and self.stealth_enhancer and scroll_count % 3 == 0:
                captcha_detected = await self.stealth_enhancer.detect_and_handle_captcha(self.page)
                if captcha_detected:
                    logger.warning("CAPTCHA detected during scrolling, attempting to handle")
            
            logger.info(f"Loaded {reviews_loaded} reviews so far...")
            
            # Check if we should rotate proxy
            if self.use_proxy_rotation and self.proxy_rotator:
                if self.proxy_rotator.should_rotate():
                    logger.info("Rotating proxy for next requests")
                    account, proxy = self.proxy_rotator.rotate()
                    # In a production environment, you would apply new proxy settings here

    async def _extract_review_data(self):
        """Extract data from loaded Google Maps reviews."""
        logger.info("Extracting review data from Google Maps...")
        
        reviews = []
        review_elements = await self.page.querySelectorAll('div[data-review-id], div[jsdata*="review"]')
        
        # Process reviews with human-like variable timing
        for i, review_element in enumerate(review_elements):
            try:
                # Add slight delay between processing reviews
                if self.use_random_delays and i > 0 and i % 3 == 0:
                    await self.page.waitForTimeout(get_random_delay(0.3, 0.1) * 1000)
                
                # Extract review date
                date_element = await review_element.querySelector('span[class*="review-date"]')
                if not date_element:
                    date_element = await review_element.querySelector('span.rsqaWe')  # Google's date class
                
                date_text = await self.page.evaluate('el => el.textContent', date_element) if date_element else ""
                
                # Parse the date
                try:
                    review_date = parser.parse(date_text, fuzzy=True)
                except ValueError:
                    # Handle relative dates like "a month ago", "a week ago", etc.
                    current_date = datetime.now()
                    if 'day ago' in date_text.lower() or 'days ago' in date_text.lower():
                        days_ago = re.search(r'(\d+)\s+day', date_text.lower())
                        days = 1 if not days_ago else int(days_ago.group(1))
                        review_date = current_date.replace(day=current_date.day-days)
                    elif 'week ago' in date_text.lower() or 'weeks ago' in date_text.lower():
                        weeks_ago = re.search(r'(\d+)\s+week', date_text.lower())
                        weeks = 1 if not weeks_ago else int(weeks_ago.group(1))
                        review_date = current_date.replace(day=current_date.day-(weeks*7))
                    elif 'month ago' in date_text.lower() or 'months ago' in date_text.lower():
                        months_ago = re.search(r'(\d+)\s+month', date_text.lower())
                        months = 1 if not months_ago else int(months_ago.group(1))
                        # Handle month rollover
                        new_month = current_date.month - months
                        if new_month <= 0:
                            new_month = 12 + new_month
                            review_date = current_date.replace(year=current_date.year-1, month=new_month)
                        else:
                            review_date = current_date.replace(month=new_month)
                    elif 'year ago' in date_text.lower() or 'years ago' in date_text.lower():
                        years_ago = re.search(r'(\d+)\s+year', date_text.lower())
                        years = 1 if not years_ago else int(years_ago.group(1))
                        review_date = current_date.replace(year=current_date.year-years)
                    else:
                        # Default to current date if parsing fails
                        review_date = current_date
                
                # Filter by date range
                if not (self.start_date <= review_date.replace(tzinfo=None) <= self.end_date):
                    continue
                
                # Extract reviewer name
                name_element = await review_element.querySelector('div.d4r55')
                if not name_element:
                    name_element = await review_element.querySelector('div.TSUbDb')  # Another Google name class
                reviewer_name = await self.page.evaluate('el => el.textContent', name_element) if name_element else "Anonymous"
                
                # Extract rating
                rating_element = await review_element.querySelector('span.kvMYJc')
                if not rating_element:
                    rating_element = await review_element.querySelector('span[aria-label*="stars"]')
                
                rating = 0  # Default value
                if rating_element:
                    aria_label = await self.page.evaluate('el => el.getAttribute("aria-label")', rating_element)
                    if aria_label:
                        rating_match = re.search(r'(\d+(\.\d+)?)\s*stars?', aria_label.lower())
                        if rating_match:
                            rating = float(rating_match.group(1))
                    else:
                        # Try to determine rating from class or style
                        style = await self.page.evaluate('el => el.getAttribute("style")', rating_element)
                        if style:
                            width_match = re.search(r'width:\s*(\d+(\.\d+)?)%', style)
                            if width_match:
                                # Convert percentage to rating (e.g., 100% = 5 stars)
                                width_percentage = float(width_match.group(1))
                                rating = round((width_percentage / 100) * 5, 1)
                
                # Extract review text
                text_element = await review_element.querySelector('span[jsaction*="pane.review.expandReview"]')
                if not text_element:
                    # Try alternative selectors
                    text_element = await review_element.querySelector('span.review-full-text')
                    if not text_element:
                        text_element = await review_element.querySelector('span[jsan*="review-full-text"]')
                
                review_text = await self.page.evaluate('el => el.textContent', text_element) if text_element else ""
                review_text = review_text.strip()
                
                # Create review object
                review = {
                    'platform': 'Google',
                    'reviewer_name': reviewer_name.strip(),
                    'date': review_date.strftime('%Y-%m-%d'),
                    'rating': rating,
                    'text': review_text,
                    'url': self.url,
                    'raw_date': date_text
                }
                
                # Categorize and add sentiment if configured
                if hasattr(self, 'categorize_review'):
                    categories = self.categorize_review(review_text)
                    review['categories'] = ', '.join(categories)
                
                if hasattr(self, 'analyze_sentiment'):
                    sentiment = self.analyze_sentiment(review_text, rating)
                    review['sentiment'] = sentiment
                
                reviews.append(review)
                
                # Check if we've reached our review limit
                if self.max_reviews > 0 and len(reviews) >= self.max_reviews:
                    logger.info(f"Reached max reviews limit ({self.max_reviews})")
                    break
                
            except Exception as e:
                logger.warning(f"Failed to extract Google review {i}: {e}")
        
        logger.info(f"Extracted {len(reviews)} Google reviews in the specified date range")
        return reviews
    
    def categorize_review(self, text):
        """Categorize a review based on its content."""
        if not text:
            return ["Uncategorized"]
            
        text = text.lower()
        categories = []
        
        # Check each category
        if 'category_keywords' in self.config:
            for category, keywords in self.config['category_keywords'].items():
                for keyword in keywords:
                    if keyword.lower() in text:
                        categories.append(category)
                        break
        
        # If no categories found, mark as Other
        if not categories:
            categories = ["Other"]
            
        return categories
    
    def analyze_sentiment(self, text, rating=0):
        """Simple sentiment analysis based on rating and key phrases."""
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
    
    # Add remaining methods in subsequent updates
    
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("google_scraper_enhanced.log"),
            logging.StreamHandler()
        ]
    )
    
    # Load configuration
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.yaml')
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        
        # Run the scraper
        scraper = EnhancedGoogleScraper(config)
        reviews = scraper.scrape()
        
        print(f"Scraped {len(reviews)} reviews")
            
    except Exception as e:
        logging.error(f"Error running scraper: {e}", exc_info=True)
