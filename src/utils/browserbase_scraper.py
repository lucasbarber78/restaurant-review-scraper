#!/usr/bin/env python3
"""
Browserbase Scraper Module

This module provides a class to handle scraping with Browserbase API.
It implements a clean interface for browser automation tasks needed
for scraping review websites.
"""

import logging
import os
import time
import json
import yaml
from typing import Dict, List, Optional, Tuple, Union, Any

# Create logger
logger = logging.getLogger(__name__)


class BrowserbaseScraper:
    """
    A class to handle scraping operations using the Browserbase API.
    
    This class provides methods to automate browser interactions for
    scraping review websites like TripAdvisor, Yelp, and Google Reviews.
    """
    
    def __init__(self, api_key: Optional[str] = None, config_path: Optional[str] = None):
        """
        Initialize the BrowserbaseScraper with API key and configuration.
        
        Args:
            api_key (str, optional): Browserbase API key. If None, tries to get from env or config.
            config_path (str, optional): Path to config file. Defaults to 'config.yaml' in root.
        """
        self.session_id = None
        
        # Get API key from arguments, environment, or config file
        self.api_key = api_key or os.environ.get('BROWSERBASE_API_KEY')
        
        # Load config if path is provided
        self.config = {}
        if config_path:
            self._load_config(config_path)
        else:
            # Try to load from default location
            default_config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                'config.yaml'
            )
            if os.path.exists(default_config_path):
                self._load_config(default_config_path)
        
        # If API key is still None, try to get from config
        if not self.api_key and 'browserbase_api_key' in self.config:
            self.api_key = self.config.get('browserbase_api_key')
            
        if not self.api_key:
            raise ValueError("Browserbase API key is required. Provide it as an argument, "
                             "set BROWSERBASE_API_KEY environment variable, "
                             "or include it in config.yaml")
    
    def _load_config(self, config_path: str) -> None:
        """
        Load configuration from YAML file.
        
        Args:
            config_path (str): Path to the YAML config file.
        """
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            logger.error(f"Error loading config from {config_path}: {e}")
            self.config = {}
    
    def create_session(self) -> str:
        """
        Create a new browser session with Browserbase.
        
        Returns:
            str: Session ID of the created browser session.
        
        Raises:
            RuntimeError: If creation of the browser session fails.
        """
        try:
            from antml.function_calls import browserbase_create_session
            
            # Call the Browserbase function
            response = browserbase_create_session()
            
            # Store and return the session ID
            self.session_id = response['sessionId']
            logger.info(f"Created Browserbase session with ID: {self.session_id}")
            return self.session_id
            
        except Exception as e:
            logger.error(f"Error creating Browserbase session: {e}", exc_info=True)
            raise RuntimeError(f"Failed to create Browserbase session: {e}")
    
    def navigate(self, url: str) -> bool:
        """
        Navigate to a URL in the current session.
        
        Args:
            url (str): URL to navigate to.
            
        Returns:
            bool: True if navigation was successful, False otherwise.
            
        Raises:
            RuntimeError: If the browser session hasn't been created yet.
        """
        if not self.session_id:
            raise RuntimeError("Browser session not created. Call create_session() first.")
            
        try:
            from antml.function_calls import browserbase_navigate
            
            # Call the Browserbase function
            response = browserbase_navigate(url=url)
            
            logger.info(f"Navigated to {url}")
            return True
            
        except Exception as e:
            logger.error(f"Error navigating to {url}: {e}", exc_info=True)
            return False
    
    def click(self, selector: str, wait_time: float = 1.0) -> bool:
        """
        Click an element on the page.
        
        Args:
            selector (str): CSS selector for the element to click.
            wait_time (float, optional): Time to wait after clicking in seconds. Defaults to 1.0.
            
        Returns:
            bool: True if the click was successful, False otherwise.
            
        Raises:
            RuntimeError: If the browser session hasn't been created yet.
        """
        if not self.session_id:
            raise RuntimeError("Browser session not created. Call create_session() first.")
            
        try:
            from antml.function_calls import browserbase_click
            
            # Call the Browserbase function
            response = browserbase_click(selector=selector)
            
            # Wait for any animations or page changes to complete
            if wait_time > 0:
                time.sleep(wait_time)
                
            logger.info(f"Clicked element with selector: {selector}")
            return True
            
        except Exception as e:
            logger.error(f"Error clicking element with selector {selector}: {e}", exc_info=True)
            return False
    
    def fill(self, selector: str, value: str, wait_time: float = 0.5) -> bool:
        """
        Fill a form field with a value.
        
        Args:
            selector (str): CSS selector for the input field.
            value (str): Value to fill into the field.
            wait_time (float, optional): Time to wait after filling in seconds. Defaults to 0.5.
            
        Returns:
            bool: True if filling was successful, False otherwise.
            
        Raises:
            RuntimeError: If the browser session hasn't been created yet.
        """
        if not self.session_id:
            raise RuntimeError("Browser session not created. Call create_session() first.")
            
        try:
            from antml.function_calls import browserbase_fill
            
            # Call the Browserbase function
            response = browserbase_fill(selector=selector, value=value)
            
            # Wait for any processing to complete
            if wait_time > 0:
                time.sleep(wait_time)
                
            logger.info(f"Filled element {selector} with value: {value}")
            return True
            
        except Exception as e:
            logger.error(f"Error filling element {selector}: {e}", exc_info=True)
            return False
    
    def get_text(self) -> str:
        """
        Get all text content from the current page.
        
        Returns:
            str: The text content of the page.
            
        Raises:
            RuntimeError: If the browser session hasn't been created yet.
        """
        if not self.session_id:
            raise RuntimeError("Browser session not created. Call create_session() first.")
            
        try:
            from antml.function_calls import browserbase_get_text
            
            # Call the Browserbase function
            response = browserbase_get_text()
            
            logger.info("Retrieved page text content")
            return response['text']
            
        except Exception as e:
            logger.error(f"Error getting page text: {e}", exc_info=True)
            return ""
    
    def take_screenshot(self) -> Dict[str, Any]:
        """
        Take a screenshot of the current page.
        
        Returns:
            dict: Response containing screenshot data.
            
        Raises:
            RuntimeError: If the browser session hasn't been created yet.
        """
        if not self.session_id:
            raise RuntimeError("Browser session not created. Call create_session() first.")
            
        try:
            from antml.function_calls import browserbase_screenshot
            
            # Call the Browserbase function
            response = browserbase_screenshot()
            
            logger.info("Took screenshot of current page")
            return response
            
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}", exc_info=True)
            return {}
    
    def wait_for_selector(self, selector: str, timeout: int = 30) -> bool:
        """
        Wait for an element matching the selector to appear on the page.
        
        Args:
            selector (str): CSS selector to wait for.
            timeout (int, optional): Maximum time to wait in seconds. Defaults to 30.
            
        Returns:
            bool: True if the element appeared before timeout, False otherwise.
        """
        if not self.session_id:
            raise RuntimeError("Browser session not created. Call create_session() first.")
        
        # Implement waiting with timeouts
        start_time = time.time()
        
        while (time.time() - start_time) < timeout:
            try:
                # Take a screenshot to trigger a page evaluation
                self.take_screenshot()
                
                # Try clicking with a very small timeout to check if element exists
                from antml.function_calls import browserbase_click
                browserbase_click(selector=selector)
                
                # If we get here without an exception, the element exists
                logger.info(f"Element with selector {selector} found")
                return True
                
            except Exception:
                # Element not found yet, wait and retry
                time.sleep(1)
        
        logger.warning(f"Timed out waiting for selector: {selector}")
        return False
    
    def extract_data_by_selectors(self, selectors: Dict[str, str]) -> Dict[str, str]:
        """
        Extract data from the page using the provided CSS selectors.
        
        Args:
            selectors (Dict[str, str]): Dictionary mapping data keys to CSS selectors.
            
        Returns:
            Dict[str, str]: Dictionary with extracted data.
        """
        if not self.session_id:
            raise RuntimeError("Browser session not created. Call create_session() first.")
            
        result = {}
        
        # Get the full page text content
        page_text = self.get_text()
        
        # For now, we're just extracting text from the page
        # In a real implementation, this would need more sophisticated parsing
        # based on the structure of the page and the specific selectors
        
        # This is a placeholder implementation
        for key, selector in selectors.items():
            # In a real implementation, we would use selector to extract specific text
            # For now, just set a placeholder value
            result[key] = f"Data for {key} (selector: {selector})"
            
        return result
    
    def scroll_to_bottom(self, max_scrolls: int = 10, scroll_delay: float = 1.0) -> None:
        """
        Scroll to the bottom of the page, with a maximum number of scrolls.
        
        Args:
            max_scrolls (int, optional): Maximum number of scroll operations. Defaults to 10.
            scroll_delay (float, optional): Delay between scrolls in seconds. Defaults to 1.0.
        """
        if not self.session_id:
            raise RuntimeError("Browser session not created. Call create_session() first.")
            
        # We'll need to implement this with a combination of screenshots and checking
        # for changes in the page height
        
        # This is a simplified implementation that just scrolls a fixed number of times
        for i in range(max_scrolls):
            try:
                # Take a screenshot - this will evaluate the page
                self.take_screenshot()
                
                # Simulate scrolling by clicking at the bottom of the viewport
                # In a real implementation, you'd use JavaScript to scroll
                try:
                    # Try to click a "More" or "Load more" button if it exists
                    self.click("button:contains('More')", wait_time=scroll_delay)
                except:
                    # Otherwise just wait
                    time.sleep(scroll_delay)
                    
            except Exception as e:
                logger.warning(f"Error during scroll operation {i+1}: {e}")
                break
                
        logger.info(f"Completed {max_scrolls} scroll operations")
    
    def close_session(self) -> None:
        """
        Close the current browser session.
        
        Note: Browserbase automatically closes sessions after inactivity,
        so this method may not be strictly necessary, but it's good practice
        to explicitly close resources when done.
        """
        if self.session_id:
            # Note: There isn't a direct browserbase_close_session function
            # The session will time out on its own
            logger.info(f"Session {self.session_id} will close automatically after inactivity")
            self.session_id = None
        else:
            logger.warning("No active session to close")
