# Restaurant Review Scraper - Browserbase Version

This is an enhanced version of the Restaurant Review Scraper that uses Browserbase for browser automation instead of Puppeteer. This change provides better stability, reliability, and ease of use for the scraping process.

## What is Browserbase?

Browserbase is a managed browser automation service that provides clean, pre-warmed browser sessions with sophisticated anti-detection mechanisms. Unlike running a local browser with Puppeteer, Browserbase handles the complexities of browser fingerprinting, residential proxies, and other anti-bot measures that review sites may employ.

## Key Benefits of This Version

1. **Improved Reliability**: Less likely to be blocked by review sites
2. **No Local Browser Needed**: All browser automation runs in the cloud
3. **Simplified Setup**: No need to install Chrome, Puppeteer, or other dependencies
4. **Better Scalability**: Can run multiple scraping jobs in parallel
5. **Reduced Resource Usage**: Lower CPU and memory usage on your local machine

## Setup Instructions

### 1. Get a Browserbase API Key

To use this version, you'll need a Browserbase API key:

1. Sign up at [browserbase.com](https://browserbase.com)
2. Create an API key in your dashboard
3. Copy the API key for use in the configuration file

### 2. Configure the Scraper

1. Copy the sample configuration file:
   ```bash
   cp config_browserbase_sample.yaml config.yaml
   ```

2. Edit `config.yaml` and add your Browserbase API key:
   ```yaml
   browserbase_api_key: "your_api_key_here"
   ```

3. Configure the restaurant details:
   ```yaml
   restaurant_name: "Your Restaurant Name"
   tripadvisor_url: "https://www.tripadvisor.com/Restaurant_Review-..."
   yelp_url: "https://www.yelp.com/biz/..."
   google_place_id: "your_google_place_id"
   ```

### 3. Install Dependencies

```bash
pip install -r requirements_browserbase.txt
```

## Usage

### Basic Usage

Run the scraper with default settings:

```bash
python src/main_browserbase.py
```

This will scrape reviews from all configured platforms (TripAdvisor, Yelp, and Google) and export them to an Excel file.

### Advanced Usage

Specify platforms to scrape:

```bash
python src/main_browserbase.py --platforms tripadvisor yelp
```

Set maximum number of reviews per platform:

```bash
python src/main_browserbase.py --max-reviews 50
```

Use a custom configuration file:

```bash
python src/main_browserbase.py --config my_config.yaml
```

## How It Works

1. The scraper creates a new browser session using the Browserbase API
2. For each review platform:
   - Navigates to the review page
   - Handles cookie consent banners and other popups
   - Sorts reviews by newest first (when available)
   - Loads more reviews by scrolling or clicking "More" buttons
   - Extracts review data including text, rating, date, and reviewer name
3. Reviews are categorized and sentiment analysis is performed
4. All data is exported to an Excel file with multiple sheets

## Directory Structure

```
restaurant-review-scraper/
├── README.md                            # Original README
├── README_BROWSERBASE.md                # This file
├── config.yaml                          # Your configuration
├── config_browserbase_sample.yaml       # Sample configuration
├── requirements.txt                     # Original requirements
├── requirements_browserbase.txt         # Browserbase requirements
├── src/
│   ├── main.py                          # Original main script
│   ├── main_browserbase.py              # Browserbase main script
│   ├── excel_exporter.py                # Excel export functionality
│   ├── review_categorizer.py            # Review categorization logic
│   ├── utils/
│   │   ├── browser_utils.py             # Original browser utilities
│   │   ├── browserbase_scraper.py       # Browserbase utilities
│   │   └── date_utils.py                # Date parsing utilities
│   └── scrapers/
│       ├── tripadvisor_browserbase_scraper.py  # TripAdvisor scraper
│       ├── yelp_browserbase_scraper.py         # Yelp scraper
│       └── google_browserbase_scraper.py       # Google scraper
```

## Troubleshooting

### Rate Limiting

If you encounter rate limiting or blocking:

1. Reduce the `max_reviews` parameter
2. Add delays between requests by modifying the scraper code
3. Use different Browserbase configurations (premium residential proxies)

### Missing Reviews

If some reviews are missing:

1. Check that the URL/Place ID is correct
2. Verify date ranges in the configuration
3. Inspect the log file for errors
4. Try running the scraper for individual platforms

## Future Enhancements

- Support for additional review platforms
- Better categorization using NLP techniques
- Real-time monitoring of scraping progress
- Incremental scraping to only get new reviews

## License

MIT
