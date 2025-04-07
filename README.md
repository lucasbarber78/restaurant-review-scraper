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
- Headless browser automation with Browserbase
- Configurable scraping parameters

## Requirements

- Python 3.8+
- Node.js 14+
- Browserbase API key

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

Run the main script to start scraping:

```bash
python src/main.py
```

Or use individual scrapers:

```bash
# TripAdvisor only
python src/tripadvisor_scraper.py

# Yelp only
python src/yelp_scraper.py

# Google Reviews only
python src/google_scraper.py
```

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
├── src/
│   ├── main.py                  # Main entry point
│   ├── tripadvisor_scraper.py   # TripAdvisor scraper
│   ├── yelp_scraper.py          # Yelp scraper 
│   ├── google_scraper.py        # Google Reviews scraper
│   ├── excel_exporter.py        # Excel export functionality
│   ├── review_categorizer.py    # Review categorization logic
│   └── utils/                   # Utility functions
│       ├── browser_utils.py     # Browserbase utilities
│       └── date_utils.py        # Date parsing utilities
└── tests/                       # Unit tests
    ├── test_tripadvisor.py
    ├── test_yelp.py
    └── test_google.py
```

## How It Works

1. The scraper uses Browserbase to create a headless browser session
2. Navigates to the review pages for each platform
3. Scrolls through and extracts review data 
4. Processes and categorizes the reviews
5. Exports the data to an Excel file

## Expected Output

The Excel output file includes several sheets:

1. **All Reviews**: Combined list of all reviews from all platforms, sorted by date (newest first)
2. **TripAdvisor**: Reviews from TripAdvisor only
3. **Yelp**: Reviews from Yelp only
4. **Google**: Reviews from Google only
5. **Summary**: Statistical breakdown of reviews by platform, rating, category, and sentiment

## Analysis Techniques

The scraper uses several techniques to analyze reviews:

1. **Keyword Matching**: Reviews are categorized based on the presence of specific keywords (configured in config.yaml)
2. **Sentiment Analysis**: A basic sentiment analysis algorithm detects positive and negative language, accounting for negation
3. **Date Parsing**: Complex date expressions (e.g., "2 weeks ago") are converted to actual dates
4. **Statistical Aggregation**: Review counts and averages are calculated for the summary report

## Limitations

- Be aware of rate limits and terms of service for each platform
- Google Reviews requires additional authentication
- Review categorization is based on keyword matching and may require refinement
- Websites may change their HTML structure, requiring scraper updates

## Troubleshooting

Common issues and solutions:

- **Session Limits**: If you encounter session limit errors, try reducing the `max_reviews_per_platform` setting
- **Selector Errors**: If the scraper fails to find elements, it may need updates to match website changes
- **Date Parsing Errors**: For complex date formats, update the date parsing logic in date_utils.py
- **Memory Issues**: For very large datasets, try scraping one platform at a time

## License

MIT
