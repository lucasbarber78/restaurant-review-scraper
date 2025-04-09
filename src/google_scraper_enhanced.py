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
    
    async def _initialize_browser(self):
        """Initialize browser with anti-bot protection measures."""
        try:
            from puppeteer import launch
            
            # Set launch options with anti-detection features
            launch_options = {
                'headless': self.headless_mode,
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
            }
            
            # If proxy rotation is enabled and we have configured proxies
            if self.use_proxy_rotation and self.proxy_rotator:
                account, proxy = self.proxy_rotator.get_current_account(), self.proxy_rotator.get_current_proxy()
                
                # Check if proxy is configured
                if proxy:
                    proxy_url = f"http://{proxy.get('host')}:{proxy.get('port')}"
                    if 'username' in proxy and 'password' in proxy:
                        proxy_url = f"http://{proxy['username']}:{proxy['password']}@{proxy['host']}:{proxy['port']}"
                    
                    launch_options['args'].append(f'--proxy-server={proxy_url}')
                    logger.info(f"Using proxy: {proxy['host']}:{proxy['port']}")
            
            # Launch the browser
            self.browser = await launch(launch_options)
            
            # Create a new page
            self.page = await self.browser.newPage()
            
            # Set a realistic viewport
            await self.page.setViewport({
                'width': 1366,
                'height': 768
            })
            
            # Apply stealth measures if enabled
            if self.use_stealth_plugins and self.stealth_enhancer:
                await self.stealth_enhancer.enhance_browser(self.page)
            
            # Set timeout
            await self.page.setDefaultNavigationTimeout(self.timeout * 1000)
            
            logger.info("Browser initialized with anti-detection measures")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            return False
    
    async def _scrape_async(self):
        """Async implementation of the scraping process."""
        try:
            # Initialize browser with anti-bot protection
            success = await self._initialize_browser()
            if not success:
                return []
            
            # Navigate to Google Maps page
            await self._navigate_to_reviews_page()
            
            # Handle any cookie popups
            await self._handle_cookies_popup()
            
            # Handle any other popups
            await self._handle_popups()
            
            # Sort reviews by newest first if possible
            await self._filter_reviews()
            
            # Scroll to load more reviews
            await self._scroll_reviews()
            
            # Extract review data
            reviews = await self._extract_review_data()
            
            return reviews
            
        except Exception as e:
            logger.error(f"Error during async Google scraping: {e}", exc_info=True)
            
            # Take a screenshot to help with debugging
            try:
                if self.page:
                    await self.page.screenshot({'path': 'google_scraping_error.png'})
                    logger.info("Saved error screenshot to google_scraping_error.png")
            except:
                pass
                
            return []
        finally:
            # Close browser if it exists
            if self.browser:
                await self.browser.close()
                logger.info("Browser closed")
    
    def scrape(self):
        """Scrape reviews from Google Maps using anti-bot measures.
        
        Returns:
            list: List of review dictionaries.
        """
        reviews = []
        
        try:
            # Create event loop
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                # If no event loop exists, create a new one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
            # Run scraping in async mode
            reviews = loop.run_until_complete(self._scrape_async())
            
            # Save reviews to CSV if configured
            if reviews and 'csv_file_path' in self.config:
                self._save_to_csv(reviews, self.config['csv_file_path'])
                
        except Exception as e:
            logger.error(f"Error during Google scraping: {e}", exc_info=True)
        
        return reviews
    
    def _save_to_csv(self, reviews, filepath=None):
        """Save reviews to a CSV file."""
        import csv
        from pathlib import Path
        
        if not reviews:
            logger.warning("No reviews to save")
            return
            
        # Use provided filepath or default
        if not filepath:
            filepath = f"{self.config.get('restaurant_name', 'restaurant').replace(' ', '_')}_google_reviews.csv"
            
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        
        try:
            # Write to CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = list(reviews[0].keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(reviews)
                
            logger.info(f"Successfully saved {len(reviews)} reviews to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to save reviews to CSV: {e}")
            return None


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
