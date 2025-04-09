"""
Utility modules for the restaurant review scraper.

This package contains various utility functions and classes used by the scraper.
"""

# Import basic utility modules
from src.utils.date_utils import parse_date, standardize_date_format
from src.utils.date_range_utils import get_smart_date_range, prompt_for_date_range

# Import browser utility modules
from src.utils.browser_utils import create_browser_session, close_browser_session, take_screenshot, save_html

# Import anti-bot detection utilities
from src.utils.delay_utils import get_random_delay, delay_between_actions, simulate_human_typing
from src.utils.proxy_rotation import ProxyRotator, get_browserbase_api_key
from src.utils.stealth_plugins import StealthEnhancer, apply_stealth_measures
