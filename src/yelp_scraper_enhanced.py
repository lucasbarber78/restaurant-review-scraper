#!/usr/bin/env python3
"""
Enhanced Yelp Scraper Module

This module handles the scraping of reviews from Yelp using advanced anti-bot
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

class EnhancedYelpScraper:
    """Advanced scraper for Yelp reviews with anti-bot detection measures."""
    
    def __init__(self, config):
        """Initialize the enhanced Yelp scraper.
        
        Args:
            config (dict): Configuration dictionary.
        """
        self.config = config
        self.url = config['yelp_url']
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
            
        # Initialize stealth enhancer for Yelp
        self.stealth_enhancer = None
        if self.use_stealth_plugins:
            self.stealth_enhancer = StealthEnhancer("yelp")
            
        # Browser and page objects
        self.browser = None
        self.page = None
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(Exception)
    )
    async def _navigate_to_reviews_page(self):
        """Navigate to the Yelp page and find the reviews section."""
        logger.info(f"Navigating to Yelp URL: {self.url}")
        
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
        
        # Wait for reviews to load
        try:
            await self.page.waitForSelector('div.review', timeout=timeout_with_jitter * 1000)
            logger.info("Reviews section loaded successfully")
        except Exception as e:
            logger.warning(f"Error waiting for reviews to load: {e}")
            
            # Take screenshot for debugging
            await self.page.screenshot({'path': 'debug_yelp_navigation.png'})
            
            # Check if we need to navigate to reviews section specifically
            try:
                # Look for reviews tab or link
                review_links = await self.page.querySelectorAll('a[href*="reviews"], span:has-text("Reviews")')
                if len(review_links) > 0:
                    # Click the first reviews link
                    if self.use_random_delays:
                        delay_between_actions("click")
                    
                    await review_links[0].click()
                    logger.info("Clicked on reviews tab/link")
                    
                    # Wait for reviews to load after click
                    await self.page.waitForSelector('div.review', timeout=timeout_with_jitter * 1000)
            except Exception as e2:
                logger.warning(f"Error navigating to reviews section: {e2}")
                raise
    
    async def _handle_cookies_popup(self):
        """Handle cookie consent popups with human-like behavior."""
        try:
            # Look for various cookie consent buttons
            cookie_buttons = [
                'button[data-cookie-banner-action="accept"]',
                'button[id*="onetrust-accept"]',
                'button[id*="accept-cookies"]',
                'button[class*="cookie-consent"]',
                'button[aria-label*="Accept"]',
                'button:has-text("Accept All Cookies")',
                'button:has-text("Accept Cookies")'
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
                'button.ybtn.ybtn--secondary',  # "Close" button
                'button[aria-label="Close"]',
                'button.dismiss-link',
                'button.close-modal',
                '.login-form-container .close-button',
                'button:has-text("Maybe Later")',
                'button:has-text("Close")',
                'button:has-text("Skip")',
                'button:has-text("No Thanks")'
            ]
            
            for selector in signin_close_buttons:
                try:
                    button = await self.page.querySelector(selector)
                    if button:
                        # Add pre-click delay for human-like behavior
                        if self.use_random_delays:
                            delay_between_actions("click")
                            
                        await button.click()
                        logger.info("Closed sign-in/promotional popup")
                        
                        # Add post-click delay
                        await self.page.waitForTimeout(get_random_delay(1.0, 0.3) * 1000)
                        break
                except Exception:
                    continue
                    
            # Check for app download banners
            app_close_buttons = [
                'button.app-banner_close',
                'button[aria-label="Close app banner"]',
                'button[data-testid="app-download-close"]'
            ]
            
            for selector in app_close_buttons:
                try:
                    button = await self.page.querySelector(selector)
                    if button:
                        if self.use_random_delays:
                            delay_between_actions("click")
                            
                        await button.click()
                        logger.info("Closed app download banner")
                        
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
            
            # Open the sort dropdown
            sort_dropdown_selectors = [
                'button[aria-controls*="sort-by-dropdown"]',
                'button.dropdown_toggle--sort',
                'button:has-text("Sort by:")'
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
                    
                    # Find and click "Newest First" option
                    newest_option_selectors = [
                        'li[role="option"] button:has-text("Newest First")',
                        'a:has-text("Newest First")',
                        'span:has-text("Newest First")'
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
                            
                            # Verify that sort was applied
                            current_sort = await self.page.querySelector('button[aria-controls*="sort-by-dropdown"] span, button.dropdown_toggle--sort span')
                            if current_sort:
                                current_sort_text = await self.page.evaluate('el => el.textContent', current_sort)
                                if 'Newest First' not in current_sort_text:
                                    logger.warning("Failed to sort by newest first")
                            break
                    break
        except Exception as e:
            logger.warning(f"Error applying review filters: {e}")
    
    async def _scroll_reviews(self):
        """Scroll through reviews with human-like behavior."""
        previous_height = await self.page.evaluate('document.body.scrollHeight')
        reviews_loaded = 0
        last_review_count = 0
        stall_count = 0
        
        # Track scrolling behavior for realistic patterns
        scroll_count = 0
        
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
                    await self.page.evaluate(f'window.scrollBy(0, -{scroll_up_amount})')
                    await self.page.waitForTimeout(get_random_delay(0.8, 0.2) * 1000)
            
            # Scroll down with variable distance
            if self.use_random_delays and self.simulate_human:
                # Varied scroll distances instead of full viewport
                scroll_amount = random.randint(300, 800)
                await self.page.evaluate(f'window.scrollBy(0, {scroll_amount})')
            else:
                # Standard scroll by viewport height
                await self.page.evaluate('window.scrollBy(0, window.innerHeight)')
            
            # Randomized pause between scrolls
            if self.use_random_delays:
                await self.page.waitForTimeout(get_random_delay(self.scroll_pause_time, 0.5) * 1000)
            else:
                await self.page.waitForTimeout(self.scroll_pause_time * 1000)
            
            # Click "More" buttons if they exist to expand review text
            more_buttons = await self.page.querySelectorAll('button.css-1i7i0ah, button:has-text("more"), a.read-more-link')
            
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
            current_reviews = await self.page.querySelectorAll('div.review')
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
            
            # Check if we've reached the bottom of the page
            current_height = await self.page.evaluate('document.body.scrollHeight')
            if current_height == previous_height:
                # Try to click "Next" pagination button if it exists
                try:
                    next_button_selectors = [
                        'a.next-link', 
                        'a.pagination-link.next', 
                        'a[href*="&start="]',
                        'a.next_page',
                        'a[aria-label="Next page"]'
                    ]
                    
                    for selector in next_button_selectors:
                        next_button = await self.page.querySelector(selector)
                        if next_button:
                            # Add human-like delay before clicking
                            if self.use_random_delays:
                                delay_between_actions("click")
                                
                            await next_button.click()
                            logger.info("Clicked to next page of reviews")
                            
                            # Wait for page to load
                            if self.use_random_delays:
                                await self.page.waitForTimeout(get_random_delay(3.0, 0.5) * 1000)
                            else:
                                await self.page.waitForTimeout(3000)
                            
                            # Reset stall count when moving to a new page
                            stall_count = 0
                            break
                    else:
                        # No next page button found
                        logger.info("No 'next page' button found, reached end of reviews")
                        break
                except Exception as e:
                    logger.debug(f"Error clicking next page: {e}")
                    break
                    
            previous_height = current_height
            
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
        """Extract data from loaded Yelp reviews."""
        logger.info("Extracting review data from Yelp...")
        
        reviews = []
        review_elements = await self.page.querySelectorAll('div.review')
        
        # Process reviews with human-like variable timing
        for i, review_element in enumerate(review_elements):
            try:
                # Add slight delay between processing reviews
                if self.use_random_delays and i > 0 and i % 3 == 0:
                    await self.page.waitForTimeout(get_random_delay(0.3, 0.1) * 1000)
                
                # Extract review date
                date_element = await review_element.querySelector('span.css-chan6m')
                if not date_element:
                    # Try alternative selectors
                    date_element = await review_element.querySelector('.rating-qualifier')
                    if not date_element:
                        date_element = await review_element.querySelector('span:has-text("/")')
                
                date_text = await self.page.evaluate('el => el.textContent', date_element) if date_element else ""
                date_text = date_text.strip()
                
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
                name_element = await review_element.querySelector('a.css-1m051bw')
                if not name_element:
                    name_element = await review_element.querySelector('.user-passport-info .user-display-name')
                    if not name_element:
                        name_element = await review_element.querySelector('a[href*="/user_details"]')
                
                reviewer_name = await self.page.evaluate('el => el.textContent', name_element) if name_element else "Anonymous"
                
                # Extract rating
                rating_element = await review_element.querySelector('div[role="img"][aria-label*="star rating"]')
                if not rating_element:
                    rating_element = await review_element.querySelector('.i-stars')
                
                rating = 0  # Default value
                if rating_element:
                    rating_text = await self.page.evaluate('el => el.getAttribute("aria-label")', rating_element)
                    if rating_text:
                        rating_match = re.search(r'(\d+(\.\d+)?) star', rating_text)
                        if rating_match:
                            rating = float(rating_match.group(1))
                    else:
                        # Try to get rating from class
                        rating_class = await self.page.evaluate('el => el.className', rating_element)
                        star_match = re.search(r'stars_(\d+)', rating_class)
                        if star_match:
                            rating = float(star_match.group(1)) / 10
                
                # Extract review text
                text_element = await review_element.querySelector('span.raw__09f24__T4Ezm')
                if not text_element:
                    text_element = await review_element.querySelector('p.comment')
                    if not text_element:
                        text_element = await review_element.querySelector('.review-content p')
                
                review_text = await self.page.evaluate('el => el.textContent', text_element) if text_element else ""
                review_text = review_text.strip()
                
                # Create review object
                review = {
                    'platform': 'Yelp',
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
                logger.warning(f"Failed to extract Yelp review {i}: {e}")
        
        logger.info(f"Extracted {len(reviews)} Yelp reviews in the specified date range")
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
            
            # Set a custom user agent to avoid detection
            # Use a recent desktop user agent
            await self.page.setUserAgent(
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            # Apply stealth measures if enabled
            if self.use_stealth_plugins and self.stealth_enhancer:
                await self.stealth_enhancer.enhance_browser(self.page)
            
            # Set timeout
            await self.page.setDefaultNavigationTimeout(self.timeout * 1000)
            
            # Additional modifications to avoid detection
            await self.page.evaluateOnNewDocument("""
                () => {
                    // Overwrite the navigator properties
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => false
                    });
                    
                    // Overwrite Permissions API
                    if (window.Permissions && window.Permissions.prototype.query) {
                        const originalQuery = window.Permissions.prototype.query;
                        window.Permissions.prototype.query = (parameters) => {
                            return Promise.resolve({state: "granted", onchange: null});
                        };
                    }
                    
                    // Overwrite plugins
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => {
                            return [1, 2, 3, 4, 5];
                        }
                    });
                    
                    // Pass Chrome notification check
                    window.chrome = {
                        runtime: {}
                    };
                    
                    // Prevent iframe detection
                    Object.defineProperty(window, 'parent', {
                        get: () => window
                    });
                    
                    // Yelp-specific anti-detection
                    // Hide that we're using puppeteer
                    delete window.__REACT_DEVTOOLS_GLOBAL_HOOK__;
                    
                    // Add missing properties that Yelp might check
                    if (!window.screenX) window.screenX = 0;
                    if (!window.screenY) window.screenY = 0;
                }
            """)
            
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
            
            # Navigate to Yelp reviews page
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
            logger.error(f"Error during async Yelp scraping: {e}", exc_info=True)
            
            # Take a screenshot to help with debugging
            try:
                if self.page:
                    await self.page.screenshot({'path': 'yelp_scraping_error.png'})
                    logger.info("Saved error screenshot to yelp_scraping_error.png")
            except:
                pass
                
            return []
        finally:
            # Close browser if it exists
            if self.browser:
                await self.browser.close()
                logger.info("Browser closed")
    
    def scrape(self):
        """Scrape reviews from Yelp using anti-bot measures.
        
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
            logger.error(f"Error during Yelp scraping: {e}", exc_info=True)
        
        return reviews
    
    def _save_to_csv(self, reviews, filepath=None):
        """Save reviews to a CSV file.
        
        Args:
            reviews (list): List of review dictionaries.
            filepath (str, optional): Path to save the CSV file. Defaults to None.
            
        Returns:
            str: Path to the saved CSV file or None if save failed.
        """
        import csv
        from pathlib import Path
        
        if not reviews:
            logger.warning("No reviews to save")
            return
            
        # Use provided filepath or default
        if not filepath:
            filepath = f"{self.config.get('restaurant_name', 'restaurant').replace(' ', '_')}_yelp_reviews.csv"
            
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
            logging.FileHandler("yelp_scraper_enhanced.log"),
            logging.StreamHandler()
        ]
    )
    
    # Load configuration
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.yaml')
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        
        # Run the scraper
        scraper = EnhancedYelpScraper(config)
        reviews = scraper.scrape()
        
        print(f"Scraped {len(reviews)} reviews")
            
    except Exception as e:
        logging.error(f"Error running scraper: {e}", exc_info=True)
