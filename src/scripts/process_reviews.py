#!/usr/bin/env python3
"""
Process Restaurant Reviews Script

This script processes the extracted restaurant reviews from CSV files,
categorizes them, performs sentiment analysis, and generates statistics.
"""

import pandas as pd
import numpy as np
import re
import os
import sys
import logging
from collections import Counter
from datetime import datetime
import matplotlib.pyplot as plt

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Category keywords for classification
CATEGORY_KEYWORDS = {
    'Food Quality': [
        'food', 'dish', 'meal', 'taste', 'flavor', 'fresh', 'cooked',
        'fried', 'shrimp', 'oyster', 'seafood', 'crab', 'fish',
        'delicious', 'bland', 'salty', 'undercooked', 'overcooked',
        'portion', 'cold', 'hot', 'grits', 'hush puppy', 'frogmore'
    ],
    'Service': [
        'service', 'staff', 'server', 'waiter', 'waitress', 'bartender',
        'friendly', 'rude', 'attentive', 'helpful', 'manager', 'owner',
        'wait', 'time', 'slow', 'quick', 'fast', 'ordered', 'tipped',
        'tip', 'cashier', 'customer service'
    ],
    'Environment/Atmosphere': [
        'atmosphere', 'ambiance', 'view', 'scenery', 'sunset', 'noise',
        'loud', 'quiet', 'rustic', 'charming', 'comfortable', 'temperature',
        'decor', 'seating', 'table', 'outdoor', 'indoor', 'patio', 'marsh',
        'water', 'vibe', 'mood', 'lowcountry', 'dive', 'bar'
    ],
    'Cleanliness': [
        'clean', 'dirty', 'bathroom', 'restroom', 'sanitary', 'hygiene',
        'mess', 'table', 'floor', 'wiped', 'sticky', 'gross', 'smell',
        'sewage', 'pipe', 'leaking', 'trash', 'dust'
    ],
    'Pricing': [
        'price', 'expensive', 'cheap', 'cost', 'worth', 'value',
        'overpriced', 'affordable', '$', 'money', 'paid', 'dollars',
        'bill', 'check'
    ]
}

# Positive and negative words for sentiment analysis
POSITIVE_WORDS = [
    'good', 'great', 'excellent', 'amazing', 'awesome', 'fantastic',
    'wonderful', 'delicious', 'tasty', 'friendly', 'helpful', 'perfect',
    'favorite', 'best', 'love', 'enjoy', 'recommend', 'satisfied',
    'fresh', 'clean', 'nice', 'attentive', 'quick', 'fast', 'warm', 
    'reasonable', 'worth', 'like', 'pleasant', 'beautiful', 'stunning',
    'awesome', 'incredible', 'phenomenal', 'stellar', 'impressive'
]

NEGATIVE_WORDS = [
    'bad', 'poor', 'terrible', 'awful', 'horrible', 'disappointing',
    'disappointing', 'mediocre', 'slow', 'rude', 'unfriendly', 'dirty',
    'expensive', 'overpriced', 'cold', 'undercooked', 'overcooked',
    'bland', 'salty', 'greasy', 'stale', 'wait', 'waited', 'waiting',
    'never', 'worst', 'avoid', 'mistake', 'wrong', 'unhappy', 'upset',
    'sick', 'dry', 'tough', 'hard', 'not good', 'not worth', 'not fresh',
    'gross', 'disgusting', 'filthy', 'messy', 'sticky'
]

NEGATION_WORDS = [
    'not', 'no', 'never', 'none', 'nobody', 'nothing', 'nowhere',
    'neither', 'hardly', 'barely', 'scarcely', "didn't", "doesn't",
    "haven't", "hasn't", "hadn't", "can't", "couldn't", "won't",
    "wouldn't", "shouldn't", "isn't", "aren't", "wasn't", "weren't"
]

def categorize_review(text, category_keywords=CATEGORY_KEYWORDS):
    """Categorize a review based on its text content."""
    if not text or not isinstance(text, str):
        return 'Other'
    
    text = text.lower()
    
    # Score each category based on keyword matches
    category_scores = {category: 0 for category in category_keywords}
    
    for category, keywords in category_keywords.items():
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
    for category in category_keywords.keys():
        if category in top_categories:
            return category
    
    return 'Other'

def analyze_sentiment(text, positive_words=POSITIVE_WORDS, 
                     negative_words=NEGATIVE_WORDS, 
                     negation_words=NEGATION_WORDS):
    """Analyze sentiment of review text."""
    if not text or not isinstance(text, str):
        return True  # Default to positive
    
    text = text.lower()
    words = text.split()
    
    positive_count = 0
    negative_count = 0
    negation = False
    
    for i, word in enumerate(words):
        # Check for negation
        if word in negation_words:
            negation = True
            continue
        
        # Reset negation after 3 words
        if negation and i > 0 and i % 3 == 0:
            negation = False
        
        # Count sentiment words, accounting for negation
        if word in positive_words:
            if negation:
                negative_count += 1
            else:
                positive_count += 1
        
        elif word in negative_words:
            if negation:
                positive_count += 1
            else:
                negative_count += 1
    
    # Calculate sentiment score
    total = positive_count + negative_count
    if total == 0:
        return True  # Default to positive
    
    sentiment_score = positive_count / total
    
    # Return sentiment label based on threshold
    return sentiment_score >= 0.5  # True for positive, False for negative

def process_reviews(csv_path):
    """Process reviews from CSV file."""
    # Load CSV file
    df = pd.read_csv(csv_path)
    
    # Count reviews by category
    category_counts = df['category'].value_counts()
    logger.info(f"Reviews by category:\n{category_counts}")
    
    # Count reviews by sentiment
    sentiment_counts = df['sentiment'].value_counts()
    logger.info(f"Reviews by sentiment:\n{sentiment_counts}")
    
    # Count reviews by rating
    rating_counts = Counter()
    for rating in df['rating']:
        # Round to nearest whole star if necessary
        try:
            star = int(float(rating))
            rating_counts[star] += 1
        except (ValueError, TypeError):
            # Skip if rating can't be converted to float
            continue
    
    logger.info(f"Reviews by rating:\n{rating_counts}")
    
    # Get average rating
    try:
        avg_rating = df['rating'].astype(float).mean()
        logger.info(f"Average rating: {avg_rating:.1f}")
    except:
        logger.warning("Could not calculate average rating")
    
    # Get top keywords mentioned
    all_text = ' '.join(df['review_text'].dropna().astype(str))
    words = re.findall(r'\b\w+\b', all_text.lower())
    
    # Remove common stop words
    stop_words = {'the', 'and', 'a', 'to', 'of', 'was', 'is', 'in', 'it', 'i', 'for', 
                 'on', 'with', 'my', 'this', 'that', 'but', 'had', 'have', 'we', 'were',
                 'they', 'there', 'their', 'our', 'your', 'at', 'be', 'as', 'or', 'by',
                 'so', 'if', 'an', 'not', 'from', 'are', 'you', 'when', 'what', 'would',
                 'could', 'should', 'very', 'just', 'get', 'got', 'then', 'than', 'them',
                 'will', 'about', 'all', 'one', 'some', 'can', 'out', 'up', 'down', 'more',
                 'very', 'really', 'here', 'now', 'been', 'being', 'do', 'does', 'did'}
    
    filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
    word_counts = Counter(filtered_words).most_common(20)
    
    logger.info(f"Top 20 keywords:")
    for word, count in word_counts:
        logger.info(f"{word}: {count}")
    
    return {
        'category_counts': category_counts,
        'sentiment_counts': sentiment_counts,
        'rating_counts': rating_counts,
        'avg_rating': avg_rating,
        'word_counts': word_counts,
        'review_count': len(df)
    }

def add_missing_categories(df, categories=CATEGORY_KEYWORDS):
    """Add category and sentiment to reviews where missing."""
    for i, row in df.iterrows():
        # Add category if missing
        if pd.isna(row['category']) or row['category'] == '':
            df.at[i, 'category'] = categorize_review(row['review_text'])
        
        # Add sentiment if missing
        if pd.isna(row['sentiment']) or row['sentiment'] == '':
            sentiment = analyze_sentiment(row['review_text'])
            df.at[i, 'sentiment'] = 'Positive' if sentiment else 'Negative'
    
    return df

def format_sentiment(value):
    """Format sentiment values to Positive/Negative."""
    if isinstance(value, bool):
        return 'Positive' if value else 'Negative'
    elif isinstance(value, str):
        if value.lower() in ['true', 'positive', 't', 'yes', 'y', '1']:
            return 'Positive'
        elif value.lower() in ['false', 'negative', 'f', 'no', 'n', '0']:
            return 'Negative'
    return 'Neutral'  # Default

def clean_data(df):
    """Clean and standardize the DataFrame."""
    # Standardize column names
    df.columns = [col.lower().strip() for col in df.columns]
    
    # Rename columns if needed for consistency
    column_mapping = {
        'name': 'reviewer_name',
        'reviewer': 'reviewer_name',
        'comment': 'review_text',
        'text': 'review_text',
        'content': 'review_text',
        'stars': 'rating',
        'score': 'rating',
        'platform_name': 'platform',
        'source': 'platform',
    }
    
    df = df.rename(columns={old: new for old, new in column_mapping.items() 
                           if old in df.columns and new not in df.columns})
    
    # Ensure required columns exist
    required_cols = ['reviewer_name', 'date', 'rating', 'review_text', 'platform']
    for col in required_cols:
        if col not in df.columns:
            df[col] = ''
    
    # Clean rating values
    if 'rating' in df.columns:
        df['rating'] = df['rating'].apply(lambda x: 
            float(str(x).replace('stars', '').replace('star', '').strip()) 
            if isinstance(x, (str, int, float)) else 0
        )
    
    # Clean dates
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    
    # Format sentiment values
    if 'sentiment' in df.columns:
        df['sentiment'] = df['sentiment'].apply(format_sentiment)
    
    return df

def generate_charts(stats, output_dir='reports'):
    """Generate charts from review statistics."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Chart 1: Reviews by Category
    plt.figure(figsize=(10, 6))
    stats['category_counts'].plot(kind='bar')
    plt.title('Reviews by Category')
    plt.xlabel('Category')
    plt.ylabel('Number of Reviews')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'reviews_by_category.png'))
    plt.close()
    
    # Chart 2: Reviews by Sentiment
    plt.figure(figsize=(8, 8))
    stats['sentiment_counts'].plot(kind='pie', autopct='%1.1f%%')
    plt.title('Reviews by Sentiment')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'reviews_by_sentiment.png'))
    plt.close()
    
    # Chart 3: Reviews by Rating
    plt.figure(figsize=(10, 6))
    ratings = sorted(stats['rating_counts'].items())
    plt.bar([str(r[0]) for r in ratings], [r[1] for r in ratings])
    plt.title('Reviews by Rating')
    plt.xlabel('Stars')
    plt.ylabel('Number of Reviews')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'reviews_by_rating.png'))
    plt.close()
    
    # Chart 4: Word Cloud (optional)
    try:
        from wordcloud import WordCloud
        
        # Create word frequency dictionary
        word_freq = {word: count for word, count in stats['word_counts']}
        
        # Generate word cloud
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_freq)
        
        # Plot word cloud
        plt.figure(figsize=(10, 6))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'word_cloud.png'))
        plt.close()
    except ImportError:
        logger.warning("WordCloud package not available, skipping word cloud generation")

def generate_report(stats, output_path='reports/review_analysis_report.md'):
    """Generate a markdown report from review statistics."""
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Format report content
    report = f"""# Restaurant Review Analysis Report

## Overview

- **Total Reviews Analyzed**: {stats['review_count']}
- **Average Rating**: {stats['avg_rating']:.1f} / 5.0
- **Analysis Date**: {datetime.now().strftime('%Y-%m-%d')}

## Review Distribution

### By Category

{stats['category_counts'].to_string()}

### By Sentiment

{stats['sentiment_counts'].to_string()}

### By Rating

{pd.Series(stats['rating_counts']).to_string()}

## Key Insights

### Most Mentioned Keywords

| Keyword | Mentions |
|---------|----------|
"""
    
    # Add top 10 keywords
    for word, count in stats['word_counts'][:10]:
        report += f"| {word} | {count} |\n"
    
    # Add recommendations
    report += """
## Recommendations

Based on the analysis of customer reviews, here are key recommendations:

1. **Food Quality**: 
   - Focus on consistent preparation and freshness
   - Address specific menu items receiving negative feedback

2. **Service**: 
   - Improve staff training for efficiency and customer interactions
   - Reduce wait times during peak hours

3. **Environment/Atmosphere**: 
   - Leverage the view as a key selling point
   - Consider improvements to comfort (temperature, seating)

4. **Cleanliness**: 
   - Implement more rigorous cleaning protocols
   - Address specific areas mentioned in reviews (bathrooms, condiment stations)

5. **Pricing**: 
   - Evaluate price-to-value perception
   - Consider strategies to improve value perception without reducing prices

## Charts

See the generated charts in the reports directory for visual representations of this data.
"""
    
    # Write report to file
    with open(output_path, 'w') as f:
        f.write(report)
    
    logger.info(f"Report generated at {output_path}")

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Process restaurant reviews')
    parser.add_argument('--input', '-i', default='data/restaurant_reviews.csv',
                        help='Path to input CSV file')
    parser.add_argument('--output', '-o', default='data/processed_reviews.csv',
                        help='Path to output CSV file')
    parser.add_argument('--report', '-r', default='reports/review_analysis_report.md',
                        help='Path to output report file')
    parser.add_argument('--charts', '-c', action='store_true',
                        help='Generate charts')
    
    args = parser.parse_args()
    
    # Load and clean data
    logger.info(f"Loading reviews from {args.input}")
    df = pd.read_csv(args.input)
    
    # Clean and standardize data
    logger.info("Cleaning and standardizing data")
    df = clean_data(df)
    
    # Add missing categories and sentiment
    logger.info("Adding missing categories and sentiment analysis")
    df = add_missing_categories(df)
    
    # Save processed data
    logger.info(f"Saving processed data to {args.output}")
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    df.to_csv(args.output, index=False)
    
    # Process and analyze reviews
    logger.info("Processing and analyzing reviews")
    stats = process_reviews(args.output)
    
    # Generate report
    logger.info("Generating analysis report")
    generate_report(stats, args.report)
    
    # Generate charts if requested
    if args.charts:
        logger.info("Generating charts")
        generate_charts(stats)
    
    logger.info("Processing complete!")

if __name__ == "__main__":
    main()
