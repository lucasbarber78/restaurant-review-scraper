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

### Enhanced Anti-Bot Detection System

We've significantly improved our anti-bot detection evasion capabilities with three major enhancements:

1. **Random Delays**: Implemented human-like variable timing between actions to evade bot detection:
   - Gaussian distribution for natural randomization
   - Contextual delays based on action type (clicking, scrolling, typing)
   - Occasional pauses to simulate human reading/thinking

2. **Proxy Rotation**: Added the ability to rotate through multiple Browserbase accounts and proxy configurations:
   - Time-based rotation (configurable intervals)
   - Request-count-based rotation
   - Support for multiple proxy types and authentication

3. **Stealth Plugins**: Integrated sophisticated browser fingerprinting and behavior simulation:
   - Realistic browser fingerprinting with consistent user-agent and headers
   - WebGL renderer and vendor spoofing to avoid canvas fingerprinting
   - JavaScript API modifications to hide automation indicators
   - Platform-specific stealth techniques for Yelp and TripAdvisor

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

# Anti-bot detection settings
anti_bot_settings:
  # Random delay settings
  enable_random_delays: true
  delay_base_values:
    click: 1.0
    scroll: 1.5
    navigation: 3.0
    typing: 0.2
  
  # Proxy rotation settings
  enable_proxy_rotation: false
  proxy_rotation_interval_minutes: 30
  
  # Stealth enhancement settings
  enable_stealth_plugins: true
  headless_mode: false
  simulate_human_behavior: true
  
# Export settings
excel_file_path: "reviews.xlsx"
```

## Usage

### Main Scraper (All Platforms) with Anti-Bot Detection

Run the main script with enhanced anti-bot detection:

```bash
python src/main.py --enhanced
```

### Command Line Options

The scraper now supports several command-line arguments for fine-tuning:

```bash
# Use enhanced anti-bot detection
python src/main.py --enhanced

# Scrape only Yelp reviews with enhanced protection
python src/main.py --enhanced --platform yelp

# Run in headless mode (less visible but more detectable)
python src/main.py --enhanced --headless

# Disable stealth plugins (not recommended)
python src/main.py --enhanced --no-stealth

# Disable random delays (not recommended)
python src/main.py --enhanced --no-random-delays

# Enable proxy rotation if configured in config.yaml
python src/main.py --enhanced --enable-proxy-rotation

# Show debug information
python src/main.py --enhanced --debug
```

### Individual Platform Scrapers

Use individual scrapers for specific platforms:

```bash
# Original TripAdvisor scraper
python src/tripadvisor_scraper.py

# Enhanced TripAdvisor scraper with anti-bot detection
python src/tripadvisor_puppeteer_scraper.py

# Enhanced Yelp scraper with anti-bot detection
python src/yelp_scraper_enhanced.py

# Original Yelp scraper
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

## Anti-Bot Detection Details

Our enhanced anti-bot detection system uses several sophisticated techniques:

### 1. Random Delays

The system adds variable timing between actions to simulate human behavior:

- **Gaussian Distribution**: Rather than using uniform randomness, we use a bell curve distribution that better matches human timing patterns
- **Context-Aware Delays**: Different types of actions (clicking, scrolling, typing) use different timing patterns
- **Reading Pauses**: Occasional longer pauses are added to simulate a human reading or considering content
- **Typing Simulation**: When entering text, the system varies the typing speed and adds occasional pauses

### 2. Proxy Rotation

For sites with IP-based detection, we can rotate through multiple proxies:

- **Time-Based Rotation**: Automatically change proxies after a configurable time interval
- **Request-Count Rotation**: Switch proxies after a certain number of requests
- **Multiple Account Support**: Rotate through multiple Browserbase accounts
- **Randomization**: Option to select proxies randomly rather than sequentially

### 3. Stealth Plugins

Advanced browser fingerprinting techniques to appear as a genuine browser:

- **WebGL Fingerprint Spoofing**: Consistent WebGL vendor and renderer information
- **Navigator Property Overrides**: Hide automation indicators in browser properties
- **Canvas Fingerprint Randomization**: Add subtle noise to canvas operations to evade fingerprinting
- **Headers and Cookies**: Platform-specific HTTP headers and cookie handling
- **JavaScript API Emulation**: Emulate expected JavaScript APIs that anti-bot systems check

### 4. Platform-Specific Measures

Tailored approaches for different review platforms:

- **Yelp-Specific Enhancements**: Special handling for Yelp's advanced detection systems
- **TripAdvisor Optimization**: Custom behavior patterns that match expected TripAdvisor user flows
- **Captcha Detection**: Automatic detection and handling of various CAPTCHA types

## Troubleshooting

Common issues and solutions:

- **Bot Detection**: If you're still experiencing blocks, try:
  - Disabling headless mode (`--headless false`)
  - Enabling proxy rotation if you have proxies configured
  - Reducing the number of reviews scraped per session
  
- **Session Limits**: If you encounter session limit errors, try reducing the `max_reviews_per_platform` setting

- **Selector Errors**: If the scraper fails to find elements, it may need updates to match website changes

- **Memory Issues**: For very large datasets, try scraping one platform at a time

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT
