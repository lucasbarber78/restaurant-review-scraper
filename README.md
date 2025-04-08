# Restaurant Review Scraper

A comprehensive solution for scraping reviews from TripAdvisor, Yelp, and Google Reviews and exporting them to Excel.

## Project Objectives

This project aims to solve the following challenges for restaurant owners and managers:

1. **Comprehensive Review Collection**: Automatically gather customer reviews across multiple platforms (TripAdvisor, Yelp, and Google Reviews) to ensure no valuable feedback is missed.

2. **Chronological Analysis**: Filter reviews by specific date ranges to analyze trends, track improvement efforts, and measure the impact of operational changes over time.

3. **Automated Categorization**: Automatically classify reviews into meaningful categories (Food Quality, Wait Times, Pricing, Service, Environment/Atmosphere, Product Availability, etc.) to identify specific areas of strength and weakness.

4. **Sentiment Analysis**: Determine whether reviews are positive or negative to quickly gauge overall customer satisfaction and identify problem areas.

5. **Consolidated Reporting**: Export all review data to a well-organized Excel file with multiple sheets for easy analysis, sharing, and presentation to stakeholders.

6. **Trend Identification**: Identify emerging issues or consistent problems by analyzing patterns in customer feedback across time periods and platforms.

7. **Operational Decision Support**: Provide actionable insights to guide operational improvements, staff training, menu adjustments, and other business decisions.

## Features

- Scrape reviews from multiple platforms:
  - TripAdvisor
  - Yelp
  - Google Reviews
- Filter reviews by date range
- Export reviews to Excel with detailed metadata:
  - Review date
  - Reviewer name
  - Review text
  - Rating
  - Review category (automatically classified)
  - Sentiment (positive/negative)
- Automated categorization of reviews based on content
- Anti-bot detection techniques for reliable scraping
- Configurable scraping parameters

## What's New - April 2025 Update

### Enhanced Anti-Bot Detection Scraper

We've added a new Puppeteer-based scraper with advanced anti-detection techniques that helps avoid TripAdvisor's bot protection mechanisms. Key improvements include:

- Browser fingerprint modification to appear more like a real user
- Randomized scrolling and timing behaviors
- Multiple selector strategies to adapt to changing HTML structures
- Headless browser operation with customizable launch options

### Restaurant-Specific Scraper

A new script specifically for Bowen's Island Restaurant has been added:

```bash
# Run the Bowen's Island Restaurant scraper
python src/scrape_bowens_island.py
```

This script not only scrapes reviews but also:
- Generates statistical analysis reports
- Creates visualizations of review data
- Provides specific recommendations based on review content

### CSV Output Format

Reviews are now exported to CSV format with enhanced metadata:
- Complete categorization of feedback (Food Quality, Service, etc.)
- Sentiment analysis (Positive, Neutral, Negative)
- Date-stamped files for tracking changes over time

## Requirements

- Python 3.8+
- Node.js 14+
- For basic scraping: Browserbase API key
- For enhanced scraping: Puppeteer

## Installation

```bash
# Clone the repository
git clone https://github.com/lucasbarber78/restaurant-review-scraper.git
cd restaurant-review-scraper

# Install dependencies
pip install -r requirements.txt
npm install
```

## Configuration

Edit the `config.yaml` file to set your preferences:

```yaml
# API keys
browserbase_api_key: "YOUR_API_KEY_HERE"

# Restaurant details
restaurant_name: "Bowens Island Restaurant"
tripadvisor_url: "https://www.tripadvisor.com/Restaurant_Review-g54171-d436679-Reviews-Bowens_Island_Restaurant-Charleston_South_Carolina.html"
yelp_url: "https://www.yelp.com/biz/bowens-island-restaurant-charleston-3"
google_place_id: "ChIJ6f1Hm-x-9ogRXCQlTnRq3vc"  # Replace with actual Google Place ID

# Scraping parameters
date_range:
  start: "2024-06-01"
  end: "2025-04-30"

# Export settings
excel_file_path: "reviews.xlsx"
```

## Usage

### Main Scraper (All Platforms)

Run the main script to start scraping:

```bash
python src/main.py
```

### Individual Platform Scrapers

Use individual scrapers for specific platforms:

```bash
# Original TripAdvisor scraper
python src/tripadvisor_scraper.py

# Enhanced TripAdvisor scraper with anti-bot detection
python src/tripadvisor_puppeteer_scraper.py

# Yelp only
python src/yelp_scraper.py

# Google Reviews only
python src/google_scraper.py
```

### Bowen's Island Restaurant Scraper

For a complete analysis of Bowen's Island Restaurant:

```bash
python src/scrape_bowens_island.py
```

This script generates:
- CSV files with all reviews
- Statistical analysis summaries
- Visualization plots (if matplotlib is installed)

## Key Use Cases

### 1. Monthly Review Analysis

Restaurant managers can run the scraper at the end of each month to collect all reviews from the past 30 days. The generated Excel report provides a comprehensive view of customer feedback, helping identify:

- Recent trends in customer satisfaction
- Emerging issues that need immediate attention
- The impact of recent operational changes or promotions

### 2. Competitive Analysis

By modifying the configuration to target competitor restaurants, the tool can be used to gather and analyze competitive intelligence:

- Track competitor ratings and sentiment over time
- Identify competitors' strengths and weaknesses
- Discover operational best practices mentioned in positive reviews
- Learn from competitors' mistakes mentioned in negative reviews

### 3. Staff Training and Performance Evaluation

Reviews often mention specific staff interactions. By analyzing service-related reviews:

- Identify training opportunities for staff
- Recognize and reward excellent service mentioned in reviews
- Address recurring service issues

### 4. Menu Development

Food quality reviews provide valuable insights for menu development:

- Identify most praised and criticized dishes
- Discover customer preferences and expectations
- Guide menu updates and pricing strategies

### 5. Marketing and Reputation Management

The compiled review data supports marketing and reputation management:

- Identify authentic positive quotes for promotional materials
- Track the effectiveness of reputation management efforts
- Develop targeted responses to common criticisms

### 6. Operational Improvements

Categorized reviews help prioritize operational improvements:

- Focus on categories with the highest number of negative reviews
- Track improvement over time after implementing changes
- Identify seasonal patterns in customer satisfaction

## Future Enhancements

The Restaurant Review Scraper has significant potential for expansion with these planned enhancements:

### 1. Web Interface and Dashboard

- **Interactive Web Dashboard**: Develop a Flask or Streamlit web interface for non-technical users.
- **Real-time Visualization**: Add interactive charts and graphs to visualize trends.
- **Automated Report Generation**: Scheduled PDF reports delivered via email.
- **User Management**: Multi-user access with role-based permissions.

### 2. Advanced Analytics and AI

- **Advanced Sentiment Analysis**: Implement BERT or RoBERTa models for more accurate sentiment detection.
- **Topic Modeling**: Use LDA (Latent Dirichlet Allocation) to automatically discover common themes in reviews.
- **Named Entity Recognition**: Identify specific dishes, staff members, or restaurant features mentioned.
- **Predictive Analytics**: Forecast upcoming review trends based on historical patterns.
- **Competitor Benchmarking**: Automatically compare performance metrics against competitors.

### 3. Expanded Data Sources

- **Additional Platforms**: Add support for Facebook, OpenTable, and regional review sites.
- **Social Media Integration**: Incorporate mentions from Twitter, Instagram, and TikTok.
- **Integration with POS Data**: Correlate reviews with sales data for deeper insights.
- **Reservation Platform Data**: Connect with booking platforms to relate reviews to specific dining experiences.

### 4. Operational Integration

- **Response Management**: Generate AI-assisted response templates for reviews.
- **Staff Alert System**: Notify relevant team members of critical reviews in real-time.
- **REST API**: Build an API for integration with other business systems.
- **Mobile App**: Develop a companion mobile app for on-the-go insights.
- **CRM Integration**: Connect review data with customer relationship management systems.

### 5. Large-Scale Deployment

- **Docker Containerization**: Package the application for easy deployment.
- **Kubernetes Orchestration**: Enable scaling for enterprise-level use.
- **Multi-Restaurant Support**: Manage multiple locations from a single interface.
- **Cloud-based Architecture**: Migrate to a fully serverless architecture.
- **Distributed Scraping**: Implement parallel processing for faster data collection.

### 6. Natural Language Processing Enhancements

- **Multilingual Support**: Add capability to analyze reviews in multiple languages.
- **Review Summarization**: Generate concise summaries of lengthy reviews.
- **Emotion Detection**: Go beyond positive/negative to detect specific emotions.
- **Sarcasm Detection**: Identify and properly categorize sarcastic comments.
- **Image Analysis**: Extract and analyze images posted with reviews.

### 7. Compliance and Privacy Features

- **GDPR Compliance Tools**: Ensure all data collection meets privacy standards.
- **Data Anonymization**: Automatically remove personally identifiable information.
- **Ethical Scraping Controls**: Enhanced rate limiting and platform-specific compliance.
- **Data Retention Policies**: Automated data aging and deletion workflows.

## Project Structure

```
restaurant-review-scraper/
├── README.md
├── requirements.txt
├── package.json
├── config.yaml
├── data/
│   ├── README.md                             # Data directory documentation
│   ├── Bowens_Island_TripAdvisor_Reviews_*.csv  # Dated review exports
│   ├── bowens_island_reviews_raw.csv         # Raw review data 
│   ├── bowens_island_analysis_summary.txt    # Analysis summary
│   └── plots/                                # Visualization charts
│       ├── ratings_distribution.png
│       ├── category_distribution.png
│       └── sentiment_distribution.png
├── src/
│   ├── README.md                             # Source code documentation
│   ├── main.py                               # Main entry point
│   ├── tripadvisor_scraper.py                # Original TripAdvisor scraper
│   ├── tripadvisor_puppeteer_scraper.py      # Enhanced anti-bot TripAdvisor scraper
│   ├── scrape_bowens_island.py               # Bowen's Island specific scraper
│   ├── yelp_scraper.py                       # Yelp scraper 
│   ├── google_scraper.py                     # Google Reviews scraper
│   ├── excel_exporter.py                     # Excel export functionality
│   ├── review_categorizer.py                 # Review categorization logic
│   └── utils/                                # Utility functions
│       ├── browser_utils.py                  # Browser automation utilities
│       └── date_utils.py                     # Date parsing utilities
└── tests/                                    # Unit tests
    ├── test_tripadvisor.py
    ├── test_yelp.py
    └── test_google.py
```

## How It Works

1. The scraper uses either Browserbase or Puppeteer to create a browser session
2. Navigates to the review pages for each platform
3. Employs anti-bot detection techniques to avoid being blocked
4. Scrolls through and extracts review data 
5. Processes and categorizes the reviews
6. Exports the data to CSV or Excel format
7. Generates analysis reports and visualizations

## Expected Output

The standard output includes several files:

1. **CSV Files**: Reviews from each platform with detailed metadata
2. **Analysis Summary**: Text report with statistical breakdowns and trends
3. **Visualizations**: Charts showing ratings distribution, categories, and sentiment
4. **Excel File** (optional): Multi-sheet workbook with all data and summaries

## Analysis Techniques

The scraper uses several techniques to analyze reviews:

1. **Keyword Matching**: Reviews are categorized based on the presence of specific keywords (configured in config.yaml)
2. **Sentiment Analysis**: A basic sentiment analysis algorithm detects positive and negative language, accounting for negation
3. **Date Parsing**: Complex date expressions (e.g., "2 weeks ago") are converted to actual dates
4. **Statistical Aggregation**: Review counts and averages are calculated for the summary report

## Limitations and Considerations

- **Terms of Service**: Be aware of rate limits and terms of service for each platform
- **Authentication**: Google Reviews requires additional authentication steps
- **Evolving Websites**: Review sites frequently change their HTML structure, requiring scraper updates
- **Anti-Bot Measures**: Despite our techniques, some platforms may still detect and block automated access
- **Review Classification**: Keyword-based categorization has limitations and may require refinement

## Troubleshooting

Common issues and solutions:

- **Bot Detection**: If TripAdvisor blocks access, try the enhanced Puppeteer scraper with `headless: false` option
- **Session Limits**: If you encounter session limit errors, try reducing the `max_reviews_per_platform` setting
- **Selector Errors**: If the scraper fails to find elements, it may need updates to match website changes
- **Date Parsing Errors**: For complex date formats, update the date parsing logic in date_utils.py
- **Memory Issues**: For very large datasets, try scraping one platform at a time

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT
