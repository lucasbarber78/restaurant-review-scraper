#!/usr/bin/env python3
"""
Browser Utilities Module

This module provides helper functions for browser automation.
"""

import logging
import os
import json
import asyncio
from puppeteer import launch

logger = logging.getLogger(__name__)


async def _create_browser_session_async(api_key=None):
    """Create an async browser session using puppeteer.
    
    Args:
        api_key (str, optional): Browserbase API key. Defaults to None.
        
    Returns:
        tuple: Browser and page objects.
    """
    launch_options = {
        'headless': True,
        'args': [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--no-zygote',
            '--disable-gpu',
            '--disable-infobars',
            '--window-size=1280,800',
            '--disable-web-security',
            '--disable-notifications'
        ]
    }
    
    # Add browserbase API key if provided
    if api_key:
        os.environ['BROWSERBASE_API_KEY'] = api_key
        # Additional browserbase settings can be set here
    
    # Launch browser
    browser = await launch(launch_options)
    
    # Create new page
    page = await browser.newPage()
    
    # Set user agent to avoid detection
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Set viewport
    await page.setViewport({'width': 1280, 'height': 800})
    
    # Set timeout for all operations
    await page.setDefaultTimeout(30000)
    
    # Enable JavaScript
    await page.setJavaScriptEnabled(True)
    
    return browser, page


def create_browser_session(api_key=None):
    """Create a browser session using puppeteer.
    
    Args:
        api_key (str, optional): Browserbase API key. Defaults to None.
        
    Returns:
        tuple: Browser and page objects.
    """
    try:
        # Run in an event loop
        loop = asyncio.get_event_loop()
        browser, page = loop.run_until_complete(_create_browser_session_async(api_key))
        
        logger.info("Browser session created successfully")
        return browser, page
        
    except Exception as e:
        logger.error(f"Error creating browser session: {e}", exc_info=True)
        raise


async def _close_browser_session_async(browser):
    """Close an async browser session.
    
    Args:
        browser: Browser object to close.
    """
    if browser:
        try:
            await browser.close()
        except Exception as e:
            logger.warning(f"Error closing browser: {e}")


def close_browser_session(browser):
    """Close a browser session.
    
    Args:
        browser: Browser object to close.
    """
    if browser:
        try:
            # Run in an event loop
            loop = asyncio.get_event_loop()
            loop.run_until_complete(_close_browser_session_async(browser))
            
            logger.info("Browser session closed successfully")
        except Exception as e:
            logger.warning(f"Error closing browser session: {e}")


async def take_screenshot(page, filename="screenshot.png"):
    """Take a screenshot of the current page.
    
    Args:
        page: Page object.
        filename (str, optional): Output filename. Defaults to "screenshot.png".
    """
    try:
        screenshots_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        
        screenshot_path = os.path.join(screenshots_dir, filename)
        await page.screenshot({'path': screenshot_path, 'fullPage': True})
        
        logger.info(f"Screenshot saved to {screenshot_path}")
    except Exception as e:
        logger.warning(f"Error taking screenshot: {e}")


async def save_html(page, filename="page.html"):
    """Save the current page HTML.
    
    Args:
        page: Page object.
        filename (str, optional): Output filename. Defaults to "page.html".
    """
    try:
        html_dir = os.path.join(os.getcwd(), "html")
        os.makedirs(html_dir, exist_ok=True)
        
        html_path = os.path.join(html_dir, filename)
        
        content = await page.content()
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"HTML saved to {html_path}")
    except Exception as e:
        logger.warning(f"Error saving HTML: {e}")


# Additional browser utility functions can be added here
