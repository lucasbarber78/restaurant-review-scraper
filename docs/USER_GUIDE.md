# Restaurant Review Scraper: User Guide

This guide provides practical instructions for restaurant owners, managers, and marketers who want to use the Restaurant Review Scraper to gather and analyze customer feedback from multiple platforms.

## Getting Started

### Prerequisites

Before using the Restaurant Review Scraper, you'll need:

1. **Python 3.8 or higher** installed on your computer
2. **Browserbase API key** (for the Browserbase version)
3. **URLs/IDs for your restaurant** on TripAdvisor, Yelp, and Google Maps

### Installation

#### Option 1: Enhanced Version with Anti-Bot Detection (Recommended)

1. Clone or download the repository:
   ```bash
   git clone https://github.com/lucasbarber78/restaurant-review-scraper.git
   cd restaurant-review-scraper
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy the sample configuration file:
   ```bash
   cp config_sample.yaml config.yaml
   ```

4. Edit the configuration file with your information (see Configuration section below).

#### Option 2: Browserbase Version 

1. Clone or download the repository:
   ```bash
   git clone https://github.com/lucasbarber78/restaurant-review-scraper.git
   cd restaurant-review-scraper
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements_browserbase.txt
   ```

3. Copy the sample configuration file:
   ```bash
   cp config_browserbase_sample.yaml config.yaml
   ```

4. Edit the configuration file with your information.

#### Option 3: Local Browser Version (Legacy)

1. Clone or download the repository:
   ```bash
   git clone https://github.com/lucasbarber78/restaurant-review-scraper.git
   cd restaurant-review-scraper
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy the sample configuration file:
   ```bash
   cp config_sample.yaml config.yaml
   ```

4. Edit the configuration file with your information, but do not enable the anti-bot features.

## Configuration

Open the `config.yaml` file in a text editor and fill in:

### Restaurant Information

```yaml
restaurant_name: "Your Restaurant Name"
tripadvisor_url: "https://www.tripadvisor.com/Restaurant_Review-g12345-d67890-Reviews-Your_Restaurant-City_State.html"
yelp_url: "https://www.yelp.com/biz/your-restaurant-city"
google_place_id: "ChIJ1234567890abcdefg"
```

To find your Google Place ID:
1. Go to [Google's Place ID Finder](https://developers.google.com/maps/documentation/javascript/examples/places-placeid-finder)
2. Search for your restaurant
3. Copy the Place ID that appears

### Date Range

```yaml
date_range:
  start: "2023-01-01"
  end: "2025-04-01"
```

This will only collect reviews within this date range. Use YYYY-MM-DD format.

Note: With the date range prompting feature, you can also set these values interactively when running the scraper. The values in the config file will be used as fallbacks if the prompting feature is disabled.

### Anti-Bot Detection Settings (NEW)

```yaml
anti_bot_settings:
  # Random delay settings
  enable_random_delays: true
  delay_base_values:
    click: 1.0
    scroll: 1.5
    navigation: 3.0
    typing: 0.2
    default: 1.0
  delay_variance: 0.5  # Random variance factor
  
  # Proxy rotation settings
  enable_proxy_rotation: false
  proxy_rotation_interval_minutes: 30  # Rotate proxy every 30 minutes
  proxy_rotation_frequency: 10  # Rotate after every 10 requests
  random_proxy_rotation: true  # Use random instead of sequential rotation
  
  # Stealth enhancement settings
  enable_stealth_plugins: true
  headless_mode: false  # Set to false to avoid detection (true for production)
  simulate_human_behavior: true
  randomize_fingerprint: true
  platform_specific_stealth:
    yelp: true
    tripadvisor: true
    google: false
```

### API Keys (Browserbase Version)

```yaml
browserbase_api_key: "your_api_key_here"
```

### Export Settings

```yaml
excel_file_path: "my_restaurant_reviews.xlsx"
```

## Basic Usage

### Running the Scraper

From the main directory, run:

#### Enhanced Version with Anti-Bot Detection (Recommended)
```bash
python src/main.py --enhanced
```

When you run the scraper, you'll be prompted to confirm or modify the date range:

```
=== Date Range Configuration ===
Default date range determined as: 2025-03-08 to 2025-04-06

Enter start date (YYYY-MM-DD) [default: 2025-03-08]: 
Enter end date (YYYY-MM-DD) [default: 2025-04-06]: 

Scraping reviews from 2025-03-08 to 2025-04-06
```

The default start date will be the day after your most recent review in the existing Excel file (if any), and the default end date will be yesterday. You can press Enter to accept the defaults or type a custom date.

#### Browserbase Version
```bash
python src/main_browserbase.py
```

#### Legacy Version
```bash
python src/main.py
```

### Command Line Options

Customize your scraping with these options:

```bash
# Use enhanced anti-bot detection (recommended for Yelp)
python src/main.py --enhanced

# Scrape only specific platforms
python src/main.py --enhanced --platform yelp

# Set maximum number of reviews per platform
python src/main.py --enhanced --max-reviews 50

# Use a custom configuration file
python src/main.py --enhanced --config my_custom_config.yaml

# Skip date range prompting and use values from config file
python src/main.py --enhanced --no-prompt

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

## Understanding the Results

The scraper generates an Excel file with multiple sheets:

1. **All Reviews**: Combined list of all reviews, sorted by date
2. **TripAdvisor**: Reviews from TripAdvisor only
3. **Yelp**: Reviews from Yelp only
4. **Google**: Reviews from Google only
5. **Summary**: Statistical breakdown with charts

### Review Data

Each review includes:
- **Platform**: Source of the review (TripAdvisor, Yelp, or Google)
- **Date**: When the review was posted
- **Reviewer Name**: Name of the reviewer
- **Rating**: Star rating (1-5)
- **Text**: Full review text
- **Category**: Automatically classified category
- **Sentiment**: Positive or negative
- **URL**: Link to the original review

### Automatic Categorization

Reviews are automatically categorized into these areas:
- Food Quality
- Service
- Wait Times
- Pricing
- Atmosphere
- Cleanliness
- Location/Accessibility

## Practical Use Cases

### Monthly Performance Tracking

1. Run the scraper at the end of each month
2. The scraper will automatically suggest scraping only the reviews since your last run
3. Compare current month's ratings and categories to previous months
4. Identify trends and changes in customer satisfaction

Example command:
```bash
python src/main.py --enhanced --max-reviews 200
```

### Post-Change Analysis

1. When prompted for date range, enter the period after making operational changes
2. Compare results to reviews from before the changes
3. Determine if the changes had the desired impact

Example date input:
```
Enter start date (YYYY-MM-DD) [default: 2025-03-08]: 2025-01-15
Enter end date (YYYY-MM-DD) [default: 2025-04-06]: 2025-04-01
```

### Competitor Analysis

1. Create a new config file (e.g., `competitor_config.yaml`)
2. Replace your restaurant's URLs with your competitor's
3. Run the scraper with the custom config
4. Compare results to understand your competitor's strengths and weaknesses

Example command:
```bash
python src/main.py --enhanced --config competitor_config.yaml
```

### Staff Training Support

1. Filter the Excel file to show only service-related reviews
2. Sort by sentiment (positive/negative)
3. Use negative reviews to identify training opportunities
4. Use positive reviews to recognize excellent staff performance

## Anti-Bot Detection Features (NEW)

The enhanced version includes advanced techniques to avoid being blocked by review sites:

### Random Delays

The system adds variable timing between actions to simulate human behavior:

- Creates natural pauses between clicks, scrolls, and typing
- Varies timing to appear less robotic
- Occasionally adds longer pauses to simulate reading behavior

### Proxy Rotation

For sites with IP-based blocking, the system can rotate through multiple accounts or proxies:

- Automatically change proxies after a configurable time interval
- Switch IP addresses after a certain number of requests
- Supports multiple Browserbase accounts

To use this feature, configure multiple accounts in your config.yaml:

```yaml
browserbase_accounts:
  - name: "Primary Account"
    api_key: "YOUR_API_KEY_HERE"
  - name: "Secondary Account"
    api_key: "SECOND_API_KEY_HERE"
```

### Stealth Plugins

The system uses sophisticated browser fingerprinting and behavior simulation:

- Prevents websites from detecting automation
- Simulates realistic browser properties
- Handles cookies and login prompts automatically
- Has special optimizations for Yelp's advanced detection systems

## Tips and Best Practices

### Getting the Most Accurate Results

- **Update URLs regularly**: Restaurant listing URLs can change over time
- **Set reasonable date ranges**: Scraping years of reviews can be time-consuming
- **Run during off-hours**: Websites may be more responsive during non-peak times
- **Use the enhanced version**: It's more reliable and less likely to be blocked for Yelp
- **Avoid headless mode**: Running with visible browser windows reduces detection likelihood

### Avoiding Common Issues

- **Rate limiting**: Don't scrape too frequently to avoid being blocked
- **Date parsing errors**: If dates aren't recognized correctly, try changing the language setting on the review site
- **Missing reviews**: Some platforms only show a subset of reviews; consider this in your analysis
- **Update selectors**: If the scraper stops working, website changes may have broken the selectors
- **Captcha detection**: If you encounter captchas frequently, enable more anti-bot features

### Recommended Settings for Different Sites

- **Yelp**: Use all anti-bot features (they have the most sophisticated detection)
  ```bash
  python src/main.py --enhanced --platform yelp
  ```

- **TripAdvisor**: Can use basic anti-bot features
  ```bash
  python src/main.py --enhanced --platform tripadvisor
  ```

- **Google**: Standard scraping usually works fine
  ```bash
  python src/main.py --platform google
  ```

### Incremental Scraping

The date range prompting feature makes incremental scraping easier:

1. Run the scraper whenever you want new reviews
2. The scraper will detect the most recent review date in your existing Excel file
3. It will suggest a date range starting from the day after that date
4. This ensures you only scrape new reviews without duplicates

### Data Privacy Considerations

- Only use this tool to scrape public review data
- Don't use scraped data in ways that violate the terms of service of review platforms
- Consider anonymizing reviewer names for internal reports

## Troubleshooting

### Error: "Failed to create browser session"

- Check your Browserbase API key
- Verify your internet connection
- Try again in a few minutes

### Error: "Bot detection encountered"

- Try running with enhanced anti-bot features:
  ```
  python src/main.py --enhanced
  ```
- Disable headless mode:
  ```
  # Don't add --headless flag
  ```
- Try reducing the number of reviews you're scraping at once

### Error: "No reviews found"

- Verify the URLs in your config file
- Check if the restaurant has any reviews on that platform
- Try running with just one platform to isolate the issue

### Warning: "Date parsing failed"

- This usually means the date format wasn't recognized
- The review will still be included but might not be filtered correctly by date
- Consider updating the date parsing patterns in `date_utils.py`

### Issue: "Excel file is empty or has incorrect date ranges"

- Make sure you didn't specify a date range with no reviews
- Check if your Excel file path is correct
- Try running with the `--no-prompt` flag to use the config file values

## Getting Help

If you encounter problems:

1. Check the `scraper.log` file for detailed error messages
2. Review the documentation in the `docs` directory
3. Submit an issue on GitHub with details about your problem

## Next Steps

After gathering your review data, consider:

1. **Present findings to staff**: Share positive feedback and areas for improvement
2. **Respond to reviews**: Use the gathered data to efficiently respond to reviews
3. **Track progress over time**: Run monthly or quarterly reports to measure improvement
4. **Adjust business operations**: Make data-driven decisions based on consistent feedback
5. **Market your strengths**: Use positive review themes in your marketing materials
