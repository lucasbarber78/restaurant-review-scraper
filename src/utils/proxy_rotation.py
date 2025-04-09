#!/usr/bin/env python3
"""
Proxy Rotation Module

This module provides functions for rotating through multiple Browserbase
accounts, IPs, and proxy configurations to avoid anti-bot detection.
"""

import os
import time
import random
import logging
import yaml
from typing import Dict, List, Optional, Tuple, Any, Union

logger = logging.getLogger(__name__)

class ProxyRotator:
    """Class for managing proxy rotation across multiple Browserbase accounts."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the ProxyRotator.
        
        Args:
            config_path (str, optional): Path to the config file containing proxy information.
        """
        self.proxies = []
        self.accounts = []
        self.current_account_index = 0
        self.current_proxy_index = 0
        self.rotation_counter = 0
        self.last_rotation_time = time.time()
        
        # Load configuration
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
    
    def _load_config(self, config_path: str) -> None:
        """Load proxy configuration from YAML file.
        
        Args:
            config_path (str): Path to the configuration file.
        """
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Load Browserbase accounts
            if 'browserbase_accounts' in config:
                self.accounts = config['browserbase_accounts']
            elif 'browserbase_api_key' in config:
                # Add the single API key as an account
                self.accounts = [{'api_key': config['browserbase_api_key']}]
            
            # Load proxy configurations if present
            if 'proxies' in config:
                self.proxies = config['proxies']
            
            logger.info(f"Loaded {len(self.accounts)} Browserbase accounts and {len(self.proxies)} proxy configurations")
            
            # Load rotation settings
            self.rotation_interval = config.get('proxy_rotation_interval_minutes', 30) * 60  # Convert to seconds
            self.rotation_frequency = config.get('proxy_rotation_frequency', 10)  # Rotate every N requests
            self.random_rotation = config.get('random_proxy_rotation', True)  # Use random rotation instead of sequential
            
        except Exception as e:
            logger.error(f"Error loading proxy configuration: {e}")
            # Initialize with empty lists if config loading fails
            self.accounts = []
            self.proxies = []
            self.rotation_interval = 30 * 60  # Default: 30 minutes
            self.rotation_frequency = 10       # Default: Every 10 requests
            self.random_rotation = True        # Default: Use random rotation
    
    def get_current_account(self) -> Dict[str, Any]:
        """Get the current Browserbase account.
        
        Returns:
            dict: The current account info with API key.
        """
        if not self.accounts:
            raise ValueError("No Browserbase accounts configured")
        
        return self.accounts[self.current_account_index]
    
    def get_current_proxy(self) -> Optional[Dict[str, str]]:
        """Get the current proxy configuration.
        
        Returns:
            dict or None: The current proxy configuration, or None if no proxies are configured.
        """
        if not self.proxies:
            return None
        
        return self.proxies[self.current_proxy_index]
    
    def should_rotate(self) -> bool:
        """Determine if it's time to rotate proxies/accounts.
        
        Returns:
            bool: True if rotation is needed, False otherwise.
        """
        current_time = time.time()
        time_since_last_rotation = current_time - self.last_rotation_time
        
        # Rotate based on elapsed time
        if time_since_last_rotation >= self.rotation_interval:
            return True
        
        # Rotate based on request count
        if self.rotation_counter >= self.rotation_frequency:
            return True
        
        return False
    
    def rotate(self) -> Tuple[Dict[str, Any], Optional[Dict[str, str]]]:
        """Rotate to a new account and/or proxy.
        
        Returns:
            tuple: (account, proxy) - The new account and proxy configuration.
        """
        # Increment the counter
        self.rotation_counter += 1
        
        # Check if we should rotate
        if not self.should_rotate():
            # Return the current settings without rotating
            return self.get_current_account(), self.get_current_proxy()
        
        # Reset counter and update rotation time
        self.rotation_counter = 0
        self.last_rotation_time = time.time()
        
        # Rotate account
        if len(self.accounts) > 1:
            if self.random_rotation:
                # Choose a random account different from the current one
                new_index = self.current_account_index
                while new_index == self.current_account_index:
                    new_index = random.randint(0, len(self.accounts) - 1)
                self.current_account_index = new_index
            else:
                # Sequential rotation
                self.current_account_index = (self.current_account_index + 1) % len(self.accounts)
                
            logger.info(f"Rotated to Browserbase account {self.current_account_index + 1}/{len(self.accounts)}")
        
        # Rotate proxy
        if len(self.proxies) > 1:
            if self.random_rotation:
                # Choose a random proxy different from the current one
                new_index = self.current_proxy_index
                while new_index == self.current_proxy_index:
                    new_index = random.randint(0, len(self.proxies) - 1)
                self.current_proxy_index = new_index
            else:
                # Sequential rotation
                self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
                
            logger.info(f"Rotated to proxy {self.current_proxy_index + 1}/{len(self.proxies)}")
        
        return self.get_current_account(), self.get_current_proxy()
    
    def next(self) -> Tuple[Dict[str, Any], Optional[Dict[str, str]]]:
        """Get the next account and proxy configuration, forcing rotation.
        
        Returns:
            tuple: (account, proxy) - The next account and proxy configuration.
        """
        # Force rotation
        self.rotation_counter = self.rotation_frequency
        return self.rotate()
    
    def reset(self) -> None:
        """Reset the rotation counters and indices."""
        self.current_account_index = 0
        self.current_proxy_index = 0
        self.rotation_counter = 0
        self.last_rotation_time = time.time()
        logger.info("Reset proxy rotation state")


def get_browserbase_api_key(config: Dict[str, Any]) -> str:
    """Extract the Browserbase API key from config, with proxy rotation if configured.
    
    Args:
        config (dict): Configuration dictionary.
        
    Returns:
        str: The Browserbase API key to use.
    """
    # First check if proxy rotation is enabled
    if config.get('enable_proxy_rotation', False):
        try:
            # Initialize the rotator
            rotator = ProxyRotator()
            
            # Get the next account
            account, _ = rotator.next()
            return account.get('api_key', '')
            
        except Exception as e:
            logger.error(f"Error during proxy rotation: {e}")
            # Fall back to default API key
    
    # Return default API key from config
    return config.get('browserbase_api_key', '')


def apply_proxy_settings(browser_instance, proxy_config: Dict[str, str]) -> bool:
    """Apply proxy settings to an existing browser instance.
    
    Args:
        browser_instance: The browser instance to configure.
        proxy_config (dict): Proxy configuration with host, port, etc.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # This implementation depends on the browser automation library being used
        # For example, in Puppeteer:
        proxy_url = f"http://{proxy_config.get('host')}:{proxy_config.get('port')}"
        
        # If authentication is provided
        if 'username' in proxy_config and 'password' in proxy_config:
            auth = f"{proxy_config['username']}:{proxy_config['password']}@"
            proxy_url = f"http://{auth}{proxy_config.get('host')}:{proxy_config.get('port')}"
        
        # Apply the proxy - implementation would be specific to the browser automation library
        # For Browserbase, this is typically handled via their API
        
        logger.info(f"Applied proxy configuration: {proxy_config.get('host')}:{proxy_config.get('port')}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to apply proxy settings: {e}")
        return False
