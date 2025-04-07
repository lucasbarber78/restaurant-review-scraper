# Restaurant Review Scraper

A comprehensive solution for scraping reviews from TripAdvisor, Yelp, and Google Reviews and exporting them to Excel.

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
google_place_id: "ChIJXXXXXXXXXXXXXXXXXX"  # Replace with actual Google Place ID

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

## Limitations

- Be aware of rate limits and terms of service for each platform
- Google Reviews requires additional authentication
- Review categorization is based on keyword matching and may require refinement

## License

MIT
