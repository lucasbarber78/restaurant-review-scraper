# TripAdvisor Review Scraper with Anti-Bot Detection

This directory contains scripts for scraping restaurant reviews from TripAdvisor with enhanced anti-bot detection capabilities.

## Files in this Directory

- `tripadvisor_scraper.py` - Original TripAdvisor scraper using Browserbase
- `tripadvisor_puppeteer_scraper.py` - Enhanced scraper using Puppeteer with anti-detection methods
- `scrape_bowens_island.py` - Specific script to scrape and analyze Bowen's Island Restaurant reviews

## How to Run the Bowen's Island Restaurant Scraper

The Bowen's Island Restaurant scraper uses Puppeteer with anti-detection measures to collect reviews from TripAdvisor while avoiding bot detection.

### Prerequisites

1. Make sure you have all required dependencies installed:
   ```bash
   pip install pyyaml pandas pyppeteer dateutil
   ```

2. Make sure your `config.yaml` file (in the root directory) has the correct TripAdvisor URL and date range settings.

### Running the Scraper

Execute the script from the project root directory:

```bash
python src/scrape_bowens_island.py
```

### Output

The script will generate:

1. CSV files with scraped reviews in the `data/` directory:
   - `Bowens_Island_TripAdvisor_Reviews_YYYYMMDD.csv` - All scraped reviews with date of scraping
   - `bowens_island_reviews_raw.csv` - Raw data for further analysis

2. Analysis files:
   - `bowens_island_analysis_summary.txt` - A comprehensive text summary of review analysis
   - If matplotlib is installed, visualization charts will be saved in `data/plots/`

### Customizing the Scrape

You can modify the following in the `config.yaml` file:

- `date_range.start` - Start date for filtering reviews (YYYY-MM-DD)
- `date_range.end` - End date for filtering reviews (YYYY-MM-DD)
- `max_reviews_per_platform` - Maximum number of reviews to collect (0 for unlimited)

## Troubleshooting

### Bot Detection Issues

If TripAdvisor detects the scraper as a bot, try:

1. Modify the browser launch options in `tripadvisor_puppeteer_scraper.py`:
   - Consider using `headless: false` to run with visible browser
   - Add additional anti-detection methods in the `initialize_browser()` method

2. Add random delays between actions to mimic human behavior

3. Try using a different network connection or VPN

### Review Not Loading

If reviews aren't loading:

1. Check if the TripAdvisor URL in the config is correct
2. Increase `scroll_pause_time` to give the page more time to load
3. Try a small number of `max_reviews_per_platform` first (e.g., 10) to test

## How It Works

The scraper uses several techniques to avoid bot detection:

1. Puppeteer with custom configurations to look like a real browser
2. Randomized scrolling and waiting times
3. Custom user agent string
4. Browser fingerprint modifications
5. Multiple selectors to adapt to TripAdvisor's changing HTML structure
