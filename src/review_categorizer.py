#!/usr/bin/env python3
"""
Review Categorizer Module

This module handles the categorization and sentiment analysis of reviews.
"""

import logging
import re
from collections import Counter
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

logger = logging.getLogger(__name__)

# Ensure NLTK resources are downloaded
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')


class ReviewCategorizer:
    """Review categorizer for assigning categories and sentiment scores to reviews."""
    
    def __init__(self, config):
        """Initialize the review categorizer.
        
        Args:
            config (dict): Configuration dictionary.
        """
        self.config = config
        self.categories = config.get('categories', [
            'Food Quality',
            'Wait Times',
            'Pricing',
            'Service',
            'Environment/Atmosphere',
            'Product Availability',
            'Cleanliness',
            'Other'
        ])
        self.category_keywords = config.get('category_keywords', {})
        self.positive_threshold = config.get('sentiment_thresholds', {}).get('positive_threshold', 0.5)
        
        # Default keywords if not specified in config
        if not self.category_keywords:
            self._initialize_default_keywords()
        
        # Initialize sentiment analysis resources
        self._initialize_sentiment_resources()
    
    def _initialize_default_keywords(self):
        """Initialize default category keywords if not specified in config."""
        self.category_keywords = {
            'Food Quality': [
                'food', 'dish', 'meal', 'taste', 'flavor', 'fresh', 'cooked',
                'fried', 'shrimp', 'oyster', 'seafood', 'crab', 'fish',
                'hush puppy', 'frogmore', 'delicious', 'bland', 'salty',
                'undercooked', 'overcooked', 'portion', 'cold', 'hot'
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
            'Product Availability': [
                'out of', 'sold out', 'unavailable', 'menu', 'selection',
                'options', 'available', 'seasonal'
            ],
            'Cleanliness': [
                'clean', 'dirty', 'bathroom', 'restroom', 'sanitary', 'hygiene',
                'mess', 'table', 'floor', 'wiped'
            ]
        }
    
    def _initialize_sentiment_resources(self):
        """Initialize sentiment analysis resources."""
        # Positive and negative word lists for simple sentiment analysis
        self.positive_words = [
            'good', 'great', 'excellent', 'amazing', 'awesome', 'fantastic',
            'wonderful', 'delicious', 'tasty', 'friendly', 'helpful', 'perfect',
            'favorite', 'best', 'love', 'enjoy', 'recommend', 'satisfied',
            'fresh', 'clean', 'nice', 'attentive', 'quick', 'fast', 'warm', 
            'reasonable', 'worth', 'like', 'pleasant', 'beautiful'
        ]
        
        self.negative_words = [
            'bad', 'poor', 'terrible', 'awful', 'horrible', 'disappointing',
            'disappointing', 'mediocre', 'slow', 'rude', 'unfriendly', 'dirty',
            'expensive', 'overpriced', 'cold', 'undercooked', 'overcooked',
            'bland', 'salty', 'greasy', 'stale', 'wait', 'waited', 'waiting',
            'never', 'worst', 'avoid', 'mistake', 'wrong', 'unhappy', 'upset',
            'sick', 'dry', 'tough', 'hard', 'not good', 'not worth', 'not fresh'
        ]
        
        # Negation words that flip sentiment
        self.negation_words = [
            'not', 'no', 'never', 'none', 'nobody', 'nothing', 'nowhere',
            'neither', 'hardly', 'barely', 'scarcely', 'didn\'t', 'doesn\'t',
            'haven\'t', 'hasn\'t', 'hadn\'t', 'can\'t', 'couldn\'t', 'won\'t',
            'wouldn\'t', 'shouldn\'t', 'isn\'t', 'aren\'t', 'wasn\'t', 'weren\'t'
        ]
    
    def categorize(self, text):
        """Categorize a review based on its content.
        
        Args:
            text (str): The review text.
            
        Returns:
            str: The assigned category.
        """
        if not text:
            return 'Other'
        
        text = text.lower()
        
        # Initialize category scores
        category_scores = {category: 0 for category in self.categories}
        
        # Process each category
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                # Look for whole words matching the keyword
                pattern = r'\b{}\b'.format(re.escape(keyword))
                matches = re.findall(pattern, text)
                category_scores[category] += len(matches)
        
        # Find the category with the highest score
        max_score = max(category_scores.values())
        if max_score == 0:
            return 'Other'
        
        # Get all categories with the max score
        top_categories = [c for c, s in category_scores.items() if s == max_score]
        
        # If there's a tie, use the first one in the original categories list
        for category in self.categories:
            if category in top_categories:
                return category
        
        return 'Other'
    
    def analyze_sentiment(self, text):
        """Analyze the sentiment of a review.
        
        Args:
            text (str): The review text.
            
        Returns:
            bool: True for positive sentiment, False for negative sentiment.
        """
        if not text:
            return True  # Default to positive
        
        text = text.lower()
        
        # Tokenize the text
        try:
            tokens = word_tokenize(text)
        except Exception:
            # Fall back to simple whitespace tokenization if NLTK fails
            tokens = text.split()
        
        # Remove stopwords
        try:
            stop_words = set(stopwords.words('english'))
            tokens = [token for token in tokens if token not in stop_words]
        except Exception:
            # Continue with all tokens if stopwords removal fails
            pass
        
        # Count positive and negative words
        positive_count = 0
        negative_count = 0
        
        # Track negation state
        negation = False
        
        for i, token in enumerate(tokens):
            # Check for negation
            if token in self.negation_words:
                negation = True
                continue
            
            # Reset negation after 3 tokens
            if negation and i > 0 and i % 3 == 0:
                negation = False
            
            # Check sentiment, accounting for negation
            if token in self.positive_words:
                if negation:
                    negative_count += 1
                else:
                    positive_count += 1
            
            elif token in self.negative_words:
                if negation:
                    positive_count += 1
                else:
                    negative_count += 1
        
        # Calculate sentiment score (normalized to 0-1)
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            return True  # Default to positive if no sentiment words
        
        sentiment_score = positive_count / total_sentiment_words
        
        # Return boolean based on threshold
        return sentiment_score >= self.positive_threshold


if __name__ == "__main__":
    # Standalone usage example
    import yaml
    
    logging.basicConfig(level=logging.INFO)
    
    with open("config.yaml", 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    
    categorizer = ReviewCategorizer(config)
    
    # Sample reviews for testing
    sample_reviews = [
        "The food was excellent but we had to wait almost an hour for our table.",
        "Great atmosphere with stunning views, but the prices are too high for what you get.",
        "The staff was incredibly friendly and attentive. Will definitely come back!",
        "Oysters were fresh and delicious. Best seafood in town!",
        "The restaurant was freezing cold and the bathrooms were dirty.",
    ]
    
    for review in sample_reviews:
        category = categorizer.categorize(review)
        sentiment = categorizer.analyze_sentiment(review)
        sentiment_label = "Positive" if sentiment else "Negative"
        
        print(f"Review: {review}")
        print(f"Category: {category}")
        print(f"Sentiment: {sentiment_label}")
        print("---")
