#!/usr/bin/env python3
"""
Date Range Utilities Module

This module provides functions for smart date range handling, including
determining defaults based on existing data and prompting users.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple

import pandas as pd

# Set up logger
logger = logging.getLogger(__name__)


def get_smart_date_range(excel_file_path: str) -> Tuple[datetime, datetime]:
    """
    Determine smart defaults for date range based on existing data and current date.
    
    Args:
        excel_file_path (str): Path to the Excel file with existing reviews.
        
    Returns:
        tuple: (start_date, end_date) as datetime objects with smart defaults.
    """
    # Default to yesterday as end date
    today = datetime.now()
    default_end_date = today - timedelta(days=1)
    
    # Try to get the latest review date from Excel file
    try:
        if os.path.exists(excel_file_path):
            logger.info(f"Checking existing Excel file: {excel_file_path}")
            
            # Read the Excel file
            try:
                df = pd.read_excel(excel_file_path, sheet_name="All Reviews")
                
                # Check if there are any reviews and if there's a date column
                if not df.empty and any(col.lower() == "date" for col in df.columns):
                    # Find the date column (case-insensitive)
                    date_col = next(col for col in df.columns if col.lower() == "date")
                    
                    # Convert string dates to datetime objects if needed
                    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
                        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                    
                    # Drop any rows with invalid dates
                    df = df.dropna(subset=[date_col])
                    
                    if not df.empty:
                        # Get the most recent date
                        latest_date = df[date_col].max()
                        
                        # Set default start date to the day after the latest review
                        default_start_date = latest_date + timedelta(days=1)
                        
                        logger.info(f"Found latest review date: {latest_date.strftime('%Y-%m-%d')}")
                        logger.info(f"Setting default start date to: {default_start_date.strftime('%Y-%m-%d')}")
                        
                        return default_start_date, default_end_date
            except Exception as e:
                logger.warning(f"Error reading Excel file: {e}")
    
    except Exception as e:
        logger.warning(f"Error determining date range from Excel file: {e}")
    
    # If we couldn't get a date from the Excel file or there was an error,
    # default to 30 days ago as the start date
    default_start_date = today - timedelta(days=30)
    logger.info(f"No existing data found. Setting default start date to 30 days ago: {default_start_date.strftime('%Y-%m-%d')}")
    
    return default_start_date, default_end_date


def prompt_for_date_range(excel_file_path: str) -> Tuple[datetime, datetime]:
    """
    Prompt the user for date range with smart defaults.
    
    Args:
        excel_file_path (str): Path to the Excel file with existing reviews.
        
    Returns:
        tuple: (start_date, end_date) as datetime objects.
    """
    # Get smart defaults
    default_start_date, default_end_date = get_smart_date_range(excel_file_path)
    
    # Format dates for display
    default_start_str = default_start_date.strftime('%Y-%m-%d')
    default_end_str = default_end_date.strftime('%Y-%m-%d')
    
    print("\n=== Date Range Configuration ===")
    print(f"Default date range determined as: {default_start_str} to {default_end_str}")
    
    # Prompt user for start date
    print(f"\nEnter start date (YYYY-MM-DD) [default: {default_start_str}]: ", end="")
    start_input = input().strip()
    
    # Prompt user for end date
    print(f"Enter end date (YYYY-MM-DD) [default: {default_end_str}]: ", end="")
    end_input = input().strip()
    
    # Use defaults if no input provided
    start_date = default_start_date
    end_date = default_end_date
    
    # Parse user input if provided
    if start_input:
        try:
            start_date = datetime.strptime(start_input, '%Y-%m-%d')
        except ValueError:
            print(f"Invalid date format. Using default start date: {default_start_str}")
    
    if end_input:
        try:
            end_date = datetime.strptime(end_input, '%Y-%m-%d')
        except ValueError:
            print(f"Invalid date format. Using default end date: {default_end_str}")
    
    # Validate date range
    if start_date > end_date:
        print("Warning: Start date is after end date. Swapping dates.")
        start_date, end_date = end_date, start_date
    
    print(f"\nScraping reviews from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    return start_date, end_date
