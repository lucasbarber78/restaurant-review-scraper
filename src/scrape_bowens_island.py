#!/usr/bin/env python3
"""
Script to scrape Bowen's Island Restaurant reviews from TripAdvisor.

This script uses the enhanced TripAdvisor scraper with Puppeteer to avoid bot detection.
"""

import os
import sys
import yaml
import logging
import pandas as pd
from datetime import datetime
from pathlib import Path

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the TripAdvisor Puppeteer scraper
from src.tripadvisor_puppeteer_scraper import TripAdvisorPuppeteerScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bowens_island_scraper.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main function to run the scraper."""
    # Define paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    config_path = os.path.join(project_dir, 'config.yaml')
    output_dir = os.path.join(project_dir, 'data')
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Load configuration
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Set the CSV output path
        csv_output = os.path.join(output_dir, f"Bowens_Island_TripAdvisor_Reviews_{datetime.now().strftime('%Y%m%d')}.csv")
        config['csv_file_path'] = csv_output
        
        logger.info(f"Starting scrape for {config['restaurant_name']}")
        logger.info(f"Target URL: {config['tripadvisor_url']}")
        logger.info(f"Date range: {config['date_range']['start']} to {config['date_range']['end']}")
        logger.info(f"Output CSV: {csv_output}")
        
        # Run the scraper
        scraper = TripAdvisorPuppeteerScraper(config)
        reviews = TripAdvisorPuppeteerScraper.scrape(config)
        
        logger.info(f"Scraped {len(reviews)} reviews")
        
        # Generate additional analysis if reviews were found
        if reviews:
            analyze_reviews(reviews, output_dir)
        
    except Exception as e:
        logger.error(f"Error running scraper: {e}", exc_info=True)
        sys.exit(1)

def analyze_reviews(reviews, output_dir):
    """Analyze the scraped reviews and generate additional reports.
    
    Args:
        reviews (list): List of review dictionaries
        output_dir (str): Directory to save analysis reports
    """
    try:
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(reviews)
        
        # Save a copy of the raw data
        df.to_csv(os.path.join(output_dir, "bowens_island_reviews_raw.csv"), index=False)
        
        # Basic statistics
        total_reviews = len(df)
        avg_rating = df['rating'].mean()
        ratings_counts = df['rating'].value_counts().sort_index(ascending=False)
        
        # Analysis by category
        df['categories'] = df['categories'].fillna('Uncategorized')
        
        # Split categories column (comma-separated) into a list
        df['categories_list'] = df['categories'].str.split(', ')
        
        # Explode the DataFrame to get one row per category
        categories_df = df.explode('categories_list')
        category_counts = categories_df['categories_list'].value_counts()
        
        # Analysis by sentiment
        sentiment_counts = df['sentiment'].value_counts()
        
        # Recent trends - last 30 reviews
        recent_reviews = df.sort_values('date', ascending=False).head(30)
        recent_avg_rating = recent_reviews['rating'].mean()
        
        # Create summary report
        with open(os.path.join(output_dir, "bowens_island_analysis_summary.txt"), 'w') as f:
            f.write(f"BOWEN'S ISLAND RESTAURANT - TRIPADVISOR REVIEW ANALYSIS\n")
            f.write(f"=======================================================\n\n")
            f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d')}\n\n")
            
            f.write(f"OVERVIEW\n")
            f.write(f"--------\n")
            f.write(f"Total Reviews Analyzed: {total_reviews}\n")
            f.write(f"Average Rating: {avg_rating:.2f} / 5.0\n\n")
            
            f.write(f"RATINGS DISTRIBUTION\n")
            f.write(f"-------------------\n")
            for rating, count in ratings_counts.items():
                f.write(f"{rating} stars: {count} reviews ({count/total_reviews*100:.1f}%)\n")
            f.write("\n")
            
            f.write(f"REVIEW CATEGORIES\n")
            f.write(f"----------------\n")
            for category, count in category_counts.items():
                f.write(f"{category}: {count} mentions\n")
            f.write("\n")
            
            f.write(f"SENTIMENT ANALYSIS\n")
            f.write(f"------------------\n")
            for sentiment, count in sentiment_counts.items():
                f.write(f"{sentiment}: {count} reviews ({count/total_reviews*100:.1f}%)\n")
            f.write("\n")
            
            f.write(f"RECENT TRENDS (Last 30 Reviews)\n")
            f.write(f"-------------------------------\n")
            f.write(f"Recent Average Rating: {recent_avg_rating:.2f} / 5.0\n")
            f.write(f"Change from Overall: {recent_avg_rating - avg_rating:+.2f}\n\n")
            
            f.write(f"TOP POSITIVE REVIEWS\n")
            f.write(f"-----------------\n")
            top_positive = df[df['sentiment'] == 'Positive'].sort_values('rating', ascending=False).head(3)
            for i, review in top_positive.iterrows():
                f.write(f"★ \"{review['title']}\" - {review['date']} ({review['rating']} stars)\n")
                f.write(f"   {review['text'][:200]}...\n\n")
            
            f.write(f"TOP NEGATIVE REVIEWS\n")
            f.write(f"-----------------\n")
            top_negative = df[df['sentiment'] == 'Negative'].sort_values('rating').head(3)
            for i, review in top_negative.iterrows():
                f.write(f"★ \"{review['title']}\" - {review['date']} ({review['rating']} stars)\n")
                f.write(f"   {review['text'][:200]}...\n\n")
            
            f.write(f"RECOMMENDATIONS\n")
            f.write(f"--------------\n")
            
            # Generate recommendations based on the data
            # Look at the most common categories with negative sentiment
            negative_categories = categories_df[categories_df['sentiment'] == 'Negative']['categories_list'].value_counts()
            if len(negative_categories) > 0:
                f.write(f"Focus Areas for Improvement:\n")
                for category, count in negative_categories.items():
                    if count > 1:  # Only include categories with multiple negative reviews
                        f.write(f"- {category}: {count} negative mentions\n")
            
            f.write("\n")
            f.write("Generated by Restaurant Review Scraper\n")
        
        logger.info(f"Analysis complete. Summary saved to {output_dir}/bowens_island_analysis_summary.txt")
        
        # Generate visualizations if matplotlib is available
        try:
            import matplotlib.pyplot as plt
            
            # Create a directory for plots
            plots_dir = os.path.join(output_dir, "plots")
            os.makedirs(plots_dir, exist_ok=True)
            
            # Ratings distribution plot
            plt.figure(figsize=(10, 6))
            ratings_counts.plot(kind='bar', color='skyblue')
            plt.title('Ratings Distribution')
            plt.xlabel('Rating')
            plt.ylabel('Number of Reviews')
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            plt.savefig(os.path.join(plots_dir, 'ratings_distribution.png'))
            
            # Category distribution plot
            plt.figure(figsize=(12, 8))
            category_counts.head(10).plot(kind='barh', color='lightgreen')
            plt.title('Top 10 Mentioned Categories')
            plt.xlabel('Number of Mentions')
            plt.ylabel('Category')
            plt.grid(axis='x', linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.savefig(os.path.join(plots_dir, 'category_distribution.png'))
            
            # Sentiment distribution pie chart
            plt.figure(figsize=(8, 8))
            sentiment_counts.plot(kind='pie', autopct='%1.1f%%', colors=['lightgreen', 'lightblue', 'salmon'])
            plt.title('Sentiment Distribution')
            plt.ylabel('')
            plt.savefig(os.path.join(plots_dir, 'sentiment_distribution.png'))
            
            logger.info(f"Visualizations saved to {plots_dir}")
            
        except ImportError:
            logger.warning("Matplotlib not available. Skipping visualizations.")
            
    except Exception as e:
        logger.error(f"Error analyzing reviews: {e}", exc_info=True)

if __name__ == "__main__":
    main()
