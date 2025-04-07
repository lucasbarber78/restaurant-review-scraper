#!/usr/bin/env python3
"""
Yelp Reviews Extraction Script

This script extracts reviews from Yelp restaurant pages and saves them to a CSV file.
It works with Browserbase for browser automation.
"""

import csv
import re
import os
from datetime import datetime
from typing import List, Dict, Any

def parse_yelp_reviews(page_text: str) -> List[Dict[str, Any]]:
    """
    Parse Yelp reviews from the page text.
    
    Args:
        page_text (str): The text content of the Yelp reviews page
        
    Returns:
        List[Dict[str, Any]]: List of review dictionaries
    """
    reviews = []
    
    # Find the review blocks
    review_blocks = re.finditer(
        r'([\w\s]+?)\n([\w\s,]+?)\n(\d+)[\s\n]+(\d+)[\s\n]+(\d+)[\s\n]+([\w\s,]+?)[\s\n]+(\d+ photos?)?(?:\n(\d+) check-ins?)?(?:\n(.*?)\n)',
        page_text
    )
    
    for block in review_blocks:
        try:
            reviewer_name = block.group(1).strip()
            location = block.group(2).strip()
            
            # Look for rating in the text - this is approximate
            rating_match = re.search(r'(\d+(?:\.\d+)?) star rating', page_text[block.start():block.start()+500])
            rating = float(rating_match.group(1)) if rating_match else 0.0
            
            # Look for date in the text
            date_match = re.search(r'(\w+ \d+, \d{4})', page_text[block.start():block.start()+500])
            review_date = date_match.group(1) if date_match else ""
            
            # Extract review text - this is the last capture group from the main regex
            review_text = block.group(9).strip() if block.group(9) else ""
            
            # Only add if we have valid review text
            if review_text and len(review_text) > 10:
                reviews.append({
                    'platform': 'Yelp',
                    'reviewer_name': reviewer_name,
                    'location': location,
                    'date': review_date,
                    'rating': rating,
                    'text': review_text,
                    'url': 'https://www.yelp.com/biz/bowens-island-restaurant-charleston-3'
                })
        except Exception as e:
            print(f"Error parsing review: {e}")
    
    return reviews

def categorize_review(text: str) -> str:
    """
    Categorize a review based on its text content.
    
    Args:
        text (str): Review text
        
    Returns:
        str: Category name
    """
    text = text.lower()
    
    # Define category keywords
    category_keywords = {
        'Food Quality': [
            'food', 'dish', 'meal', 'taste', 'flavor', 'fresh', 'cooked',
            'fried', 'shrimp', 'oyster', 'seafood', 'crab', 'fish',
            'delicious', 'bland', 'salty', 'undercooked', 'overcooked'
        ],
        'Wait Times': [
            'wait', 'time', 'long', 'slow', 'quick', 'fast', 'delay',
            'minute', 'hour', 'promptly', 'forever', 'waited'
        ],
        'Pricing': [
            'price', 'expensive', 'cheap', 'cost', 'worth', 'value',
            'overpriced', 'affordable', '$', 'money'
        ],
        'Service': [
            'service', 'staff', 'server', 'waiter', 'waitress', 'bartender',
            'friendly', 'rude', 'attentive', 'helpful', 'manager', 'owner'
        ],
        'Environment/Atmosphere': [
            'atmosphere', 'ambiance', 'view', 'scenery', 'sunset', 'noise',
            'loud', 'quiet', 'rustic', 'charming', 'comfortable', 'cold', 
            'hot', 'temperature', 'decor', 'seating', 'table', 'outdoor',
            'indoor', 'patio', 'marsh', 'water'
        ],
        'Cleanliness': [
            'clean', 'dirty', 'bathroom', 'restroom', 'sanitary', 'hygiene',
            'mess', 'table', 'floor', 'wiped'
        ]
    }
    
    # Score each category
    category_scores = {}
    for category, keywords in category_keywords.items():
        score = 0
        for keyword in keywords:
            if keyword in text:
                score += 1
        category_scores[category] = score
    
    # Find category with highest score
    max_score = max(category_scores.values())
    if max_score == 0:
        return 'Other'
    
    # Get all categories with max score
    max_categories = [c for c, s in category_scores.items() if s == max_score]
    return max_categories[0]  # Return the first max category

def analyze_sentiment(text: str) -> bool:
    """
    Simple sentiment analysis for review text.
    
    Args:
        text (str): Review text
        
    Returns:
        bool: True for positive sentiment, False for negative
    """
    text = text.lower()
    
    positive_words = [
        'good', 'great', 'excellent', 'amazing', 'awesome', 'fantastic',
        'wonderful', 'delicious', 'tasty', 'friendly', 'helpful', 'perfect',
        'favorite', 'best', 'love', 'enjoy', 'recommend', 'satisfied',
        'fresh', 'clean', 'nice', 'attentive', 'quick', 'fast', 'warm'
    ]
    
    negative_words = [
        'bad', 'poor', 'terrible', 'awful', 'horrible', 'disappointing',
        'mediocre', 'slow', 'rude', 'unfriendly', 'dirty', 'expensive',
        'overpriced', 'cold', 'undercooked', 'overcooked', 'bland', 'salty',
        'greasy', 'stale', 'wait', 'waited', 'waiting', 'never', 'worst'
    ]
    
    # Count positive and negative words
    positive_count = sum(1 for word in positive_words if word in text)
    negative_count = sum(1 for word in negative_words if word in text)
    
    # Calculate sentiment score
    total = positive_count + negative_count
    if total == 0:
        return True  # Default to positive
    
    sentiment_score = positive_count / total
    return sentiment_score >= 0.5  # True for positive, False for negative

def save_reviews_to_csv(reviews: List[Dict[str, Any]], filename: str):
    """
    Save reviews to CSV file.
    
    Args:
        reviews (List[Dict[str, Any]]): List of review dictionaries
        filename (str): Output CSV filename
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Define CSV headers
    fieldnames = [
        'platform', 'reviewer_name', 'location', 'date', 'rating', 
        'text', 'category', 'sentiment', 'url'
    ]
    
    # Write to CSV
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for review in reviews:
            # Add category and sentiment if not already present
            if 'category' not in review:
                review['category'] = categorize_review(review['text'])
            if 'sentiment' not in review:
                review['sentiment'] = 'Positive' if analyze_sentiment(review['text']) else 'Negative'
            writer.writerow(review)
    
    print(f"Saved {len(reviews)} reviews to {filename}")

# This script is intended to be used with extracted page text from Browserbase
if __name__ == "__main__":
    print("Yelp review scraper initialized. Use with Browserbase to extract reviews.")
