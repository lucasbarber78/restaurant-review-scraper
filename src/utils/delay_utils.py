#!/usr/bin/env python3
"""
Delay Utilities Module

This module provides functions for creating randomized, human-like delays
to avoid anti-bot detection during web scraping.
"""

import random
import time
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

def get_random_delay(base_delay: float = 2.0, variance: float = 1.0) -> float:
    """Generate a random delay with Gaussian distribution around the base delay.
    
    Args:
        base_delay (float): The base delay time in seconds.
        variance (float): The variance for randomization.
        
    Returns:
        float: A randomized delay value.
    """
    # Use Gaussian distribution for more human-like randomness
    delay = random.gauss(base_delay, variance)
    
    # Ensure delay is not negative or too short
    return max(0.5, delay)

def humanized_delay(min_delay: float = 1.0, max_delay: float = 5.0) -> float:
    """Generate a humanized delay between actions.
    
    Args:
        min_delay (float): Minimum delay in seconds.
        max_delay (float): Maximum delay in seconds.
        
    Returns:
        float: A humanized delay value.
    """
    # Base delay with some randomness
    delay = random.uniform(min_delay, max_delay)
    
    # Add occasional longer pauses to simulate human behavior
    if random.random() < 0.1:  # 10% chance of a longer pause
        delay += random.uniform(1.0, 3.0)
        
    return delay

def delay_between_actions(action_type: str = "default") -> float:
    """Add an appropriate delay between different types of browser actions.
    
    Args:
        action_type (str): Type of action ("click", "scroll", "type", "navigation", "default").
        
    Returns:
        float: The delay in seconds.
    """
    # Different action types have different typical human delay patterns
    if action_type == "click":
        # Clicking is usually quick
        delay = humanized_delay(0.5, 2.0)
    elif action_type == "scroll":
        # Scrolling often has varied timing
        delay = humanized_delay(0.8, 3.0)
    elif action_type == "type":
        # Typing has varied timing between keystrokes
        delay = humanized_delay(0.1, 0.3)
    elif action_type == "navigation":
        # Navigation typically has longer delays for page loads
        delay = humanized_delay(2.0, 5.0)
    else:  # default
        delay = humanized_delay(1.0, 3.0)
        
    # Apply the delay
    time.sleep(delay)
    return delay

def typing_delay(text_length: int) -> Tuple[float, float]:
    """Calculate realistic typing delay for a given text length.
    
    Args:
        text_length (int): Length of text to be typed.
        
    Returns:
        Tuple[float, float]: Tuple of (per_character_delay, pause_probability).
    """
    # Average typing speed ranges (characters per second)
    # Slow: 2-4, Average: 4-8, Fast: 8-12
    typing_speed = random.uniform(4.0, 8.0)  # Average typing speed
    
    # Calculate delay per character (seconds)
    per_character_delay = 1.0 / typing_speed
    
    # Probability of a pause while typing (simulate thinking)
    pause_probability = 0.1  # 10% chance of pausing
    
    return (per_character_delay, pause_probability)

def simulate_human_typing(page, selector: str, text: str, clear_first: bool = True) -> None:
    """Simulate human typing with realistic delays.
    
    Args:
        page: The page object (from puppeteer or similar).
        selector (str): CSS selector for the input field.
        text (str): Text to type.
        clear_first (bool): Whether to clear the field first.
    """
    # First, click on the field to focus it
    try:
        delay_between_actions("click")
        page.click(selector)
        
        # Clear the field if requested
        if clear_first:
            page.evaluate(f'document.querySelector("{selector}").value = ""')
            
        # Get typing delays
        per_char_delay, pause_prob = typing_delay(len(text))
        
        # Type the text with realistic timing
        for char in text:
            # Type the character
            page.type(selector, char)
            
            # Basic delay between characters
            time.sleep(per_char_delay)
            
            # Occasional pause (simulating thinking or distraction)
            if random.random() < pause_prob:
                time.sleep(random.uniform(0.5, 2.0))
                
    except Exception as e:
        logger.error(f"Error during human typing simulation: {e}")
        # Fall back to regular typing
        page.fill(selector, text)
