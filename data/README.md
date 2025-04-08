# Data Directory

This directory stores all scraped review data and analysis results.

## Directory Structure

```
data/
├── Bowens_Island_TripAdvisor_Reviews_YYYYMMDD.csv    # Dated review exports
├── bowens_island_reviews_raw.csv                     # Raw review data
├── bowens_island_analysis_summary.txt                # Text analysis summary
└── plots/                                            # Visualization charts
    ├── ratings_distribution.png
    ├── category_distribution.png
    └── sentiment_distribution.png
```

## File Descriptions

### CSV Files

- **Bowens_Island_TripAdvisor_Reviews_YYYYMMDD.csv**: Primary export of all scraped reviews with the date of scraping.
  
- **bowens_island_reviews_raw.csv**: Raw data export with all review fields for further analysis.

### Analysis Files

- **bowens_island_analysis_summary.txt**: Comprehensive text-based analysis of reviews including:
  - Overall statistics (average rating, total reviews)
  - Ratings distribution
  - Review categories breakdown
  - Sentiment analysis
  - Recent trends
  - Top positive and negative reviews
  - Recommendations based on the data

### Visualization Charts

If matplotlib is installed, the following visualization charts will be generated:

- **ratings_distribution.png**: Bar chart showing the distribution of star ratings
- **category_distribution.png**: Horizontal bar chart of the top 10 mentioned categories
- **sentiment_distribution.png**: Pie chart of sentiment distribution (Positive, Neutral, Negative)

## Data Schema

The review CSV files contain the following fields:

- **platform**: The review platform (e.g., "TripAdvisor")
- **restaurant**: Restaurant name
- **reviewer_name**: Name of the reviewer
- **date**: Review date (YYYY-MM-DD format)
- **raw_date**: Original date text from the review
- **rating**: Numerical rating (1-5 scale)
- **title**: Review title
- **text**: Full review text
- **categories**: Comma-separated list of detected categories
- **sentiment**: Sentiment classification (Positive, Neutral, Negative)
- **url**: Source URL for the review
