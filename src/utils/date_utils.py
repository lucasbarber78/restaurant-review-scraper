#!/usr/bin/env python3
"""
Date Utilities Module

This module provides helper functions for date parsing and manipulation.
"""

import logging
import re
from datetime import datetime, timedelta
from dateutil import parser

logger = logging.getLogger(__name__)


def parse_date(date_string, default=None):
    """Parse a date string into a datetime object.
    
    Args:
        date_string (str): Date string to parse.
        default (datetime, optional): Default date to return if parsing fails.
            Defaults to None (current date).
    
    Returns:
        datetime: Parsed date.
    """
    if not date_string:
        return default or datetime.now()
    
    try:
        # Try standard dateutil parser first
        return parser.parse(date_string, fuzzy=True)
        
    except (ValueError, TypeError):
        # If standard parsing fails, try to handle relative dates
        return parse_relative_date(date_string, default)


def parse_relative_date(date_string, default=None):
    """Parse a relative date string (e.g., "2 days ago") into a datetime object.
    
    Args:
        date_string (str): Relative date string to parse.
        default (datetime, optional): Default date to return if parsing fails.
            Defaults to None (current date).
            
    Returns:
        datetime: Parsed date.
    """
    if not date_string:
        return default or datetime.now()
    
    date_string = date_string.lower().strip()
    current_date = datetime.now()
    
    # Handle "today", "yesterday", etc.
    if "today" in date_string:
        return current_date
    
    if "yesterday" in date_string:
        return current_date - timedelta(days=1)
    
    # Handle "X days/weeks/months/years ago"
    days_match = re.search(r'(\d+)\s+days?\s+ago', date_string)
    if days_match:
        days = int(days_match.group(1))
        return current_date - timedelta(days=days)
    
    weeks_match = re.search(r'(\d+)\s+weeks?\s+ago', date_string)
    if weeks_match:
        weeks = int(weeks_match.group(1))
        return current_date - timedelta(weeks=weeks)
    
    months_match = re.search(r'(\d+)\s+months?\s+ago', date_string)
    if months_match:
        months = int(months_match.group(1))
        # Approximate month as 30 days
        return current_date - timedelta(days=months * 30)
    
    years_match = re.search(r'(\d+)\s+years?\s+ago', date_string)
    if years_match:
        years = int(years_match.group(1))
        # Approximate year as 365 days
        return current_date - timedelta(days=years * 365)
    
    # Handle "a week/month/year ago"
    if "a week ago" in date_string or "one week ago" in date_string:
        return current_date - timedelta(weeks=1)
    
    if "a month ago" in date_string or "one month ago" in date_string:
        return current_date - timedelta(days=30)
    
    if "a year ago" in date_string or "one year ago" in date_string:
        return current_date - timedelta(days=365)
    
    # Fall back to default
    return default or current_date


def format_date(date_obj, format_string='%Y-%m-%d'):
    """Format a datetime object as a string.
    
    Args:
        date_obj (datetime): Date to format.
        format_string (str, optional): Format string. Defaults to '%Y-%m-%d'.
    
    Returns:
        str: Formatted date string.
    """
    if not date_obj:
        return ""
    
    try:
        return date_obj.strftime(format_string)
    except Exception as e:
        logger.warning(f"Error formatting date: {e}")
        return str(date_obj)


def is_date_in_range(date_obj, start_date, end_date):
    """Check if a date is within a date range.
    
    Args:
        date_obj (datetime): Date to check.
        start_date (datetime): Start of range.
        end_date (datetime): End of range.
    
    Returns:
        bool: True if date is within range, False otherwise.
    """
    if not date_obj:
        return False
    
    # Convert to date only (no time) if full datetime objects
    if hasattr(date_obj, 'date'):
        date_obj = date_obj.date()
    if hasattr(start_date, 'date'):
        start_date = start_date.date()
    if hasattr(end_date, 'date'):
        end_date = end_date.date()
    
    return start_date <= date_obj <= end_date


def get_month_year_str(date_obj):
    """Get a 'Month Year' string from a datetime object.
    
    Args:
        date_obj (datetime): Date object.
    
    Returns:
        str: Formatted 'Month Year' string.
    """
    if not date_obj:
        return ""
    
    try:
        return date_obj.strftime('%B %Y')  # e.g., "January 2023"
    except Exception as e:
        logger.warning(f"Error formatting month-year: {e}")
        return str(date_obj)


def get_month_range(year, month):
    """Get the start and end dates for a given month.
    
    Args:
        year (int): Year.
        month (int): Month (1-12).
    
    Returns:
        tuple: (start_date, end_date) as datetime objects.
    """
    # Start date is the first day of the month
    start_date = datetime(year, month, 1)
    
    # End date is the first day of the next month minus one day
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)
    
    return start_date, end_date


def get_date_n_days_ago(n):
    """Get the date that was n days ago.
    
    Args:
        n (int): Number of days ago.
    
    Returns:
        datetime: Date n days ago.
    """
    return datetime.now() - timedelta(days=n)


if __name__ == "__main__":
    # Standalone usage example
    logging.basicConfig(level=logging.INFO)
    
    # Test date parsing
    date_strings = [
        "January 15, 2023",
        "2023-01-15",
        "15/01/2023",
        "yesterday",
        "2 days ago",
        "last week",
        "a month ago",
        "3 weeks ago"
    ]
    
    for date_string in date_strings:
        parsed_date = parse_date(date_string)
        print(f"Original: {date_string}, Parsed: {parsed_date}")
    
    # Test date range checking
    today = datetime.now()
    start_date = today - timedelta(days=30)
    end_date = today
    
    test_date = today - timedelta(days=15)
    in_range = is_date_in_range(test_date, start_date, end_date)
    print(f"Is {test_date} between {start_date} and {end_date}? {in_range}")
