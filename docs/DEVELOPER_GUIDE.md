# Restaurant Review Scraper: Developer Guide

This document provides technical details about the design, architecture, and implementation of the Restaurant Review Scraper project for developers who want to understand, modify, or extend the codebase.

## Architecture Overview

The project follows a modular design with clear separation of concerns:

```
┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐
│                   │     │                   │     │                   │
│  Platform-Specific│     │  Data Processing  │     │  Data Export      │
│  Scrapers         │     │  & Analysis       │     │  & Visualization  │
│                   │     │                   │     │                   │
└─────────┬─────────┘     └─────────┬─────────┘     └─────────┬─────────┘
          │                         │                         │
          │                         │                         │
          ▼                         ▼                         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                       Configuration & Orchestration                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Components

1. **Browser Automation Layer**
   - `browser_utils.py` (Puppeteer version)
   - `browserbase_scraper.py` (Browserbase version)

2. **Platform-Specific Scrapers**
   - TripAdvisor scrapers
   - Yelp scrapers
   - Google Reviews scrapers

3. **Data Processing**
   - `review_categorizer.py` (text categorization and sentiment analysis)
   - `date_utils.py` (date parsing and normalization)
   - `date_range_utils.py` (smart date range determination and user prompting)

4. **Data Export**
   - `excel_exporter.py` (structured data export to Excel)

5. **Main Orchestration**
   - `main.py` (Puppeteer version)
   - `main_browserbase.py` (Browserbase version)

## Design Principles

The project follows these key design principles:

1. **Single Responsibility Principle**: Each class has a clear and focused responsibility.
2. **Encapsulation**: Implementation details are hidden behind clean interfaces.
3. **Configurability**: All behavior can be adjusted through the configuration file.
4. **Error Resilience**: Robust error handling to deal with inconsistencies in scraped data.
5. **Modularity**: Easy to extend with new platforms or features.
6. **Smart Defaults**: The system provides intelligent default values based on context.
7. **User Interaction**: Interactive features are optional and have non-interactive fallbacks.

## Browser Automation Approaches

### Puppeteer (Original)

The original implementation uses Puppeteer (via the `pyppeteer` Python bindings) to control a local Chromium browser instance. This approach:

- Provides full control over the browser
- Requires local browser installation
- Is vulnerable to detection by anti-bot mechanisms
- May have stability issues on certain platforms

### Browserbase (New)

The Browserbase version uses a cloud-based browser automation service that:

- Provides pre-configured browser sessions with anti-detection measures
- Eliminates the need for local browser installation
- Offers better stability and reliability
- Requires an API key and may incur usage costs

## Data Extraction Logic

The data extraction process follows these steps:

1. **Navigation**: Go to the review page for a restaurant
2. **Authentication/Cookies**: Handle any login requirements or cookie consent banners
3. **Discovery**: Find elements containing reviews
4. **Pagination**: Load more reviews by scrolling, clicking "Next", etc.
5. **Extraction**: Extract structured data from review elements
6. **Filtering**: Apply date range and other filters
7. **Normalization**: Standardize data across platforms

### Platform-Specific Challenges

#### TripAdvisor

- Reviews are initially truncated and require clicking "More" to expand
- Date formats vary by region and language
- Multiple pagination approaches (infinite scroll + pagination)

#### Yelp

- Aggressively detects and blocks automated browsers
- Review translation features can interfere with extraction
- Inconsistent DOM structure across different restaurant pages

#### Google Reviews

- Highly dynamic content loaded via AJAX
- No direct URLs for review sections
- Requires sophisticated scrolling to load all reviews

## Categorization and Sentiment Analysis

The `review_categorizer.py` implements:

1. **Keyword-Based Categorization**: Maps reviews to categories based on configured keywords
2. **Sentiment Analysis**: Determines positive/negative sentiment using:
   - Dictionary-based approach with positive/negative word lists
   - Negation handling ("not good" → negative)
   - Rating score consideration

In future versions, this could be enhanced with:
- Named entity recognition (identifying specific dishes, staff, etc.)
- More sophisticated NLP techniques (embedding models, etc.)
- Fine-tuned restaurant-specific sentiment models

## Date Range Handling

The date range handling system consists of two main components:

1. **Date Parsing (`date_utils.py`)**: 
   - Converts various date formats to standardized datetime objects
   - Handles relative dates ("2 days ago", "last week", etc.)
   - Normalizes across different platforms' date formats

2. **Smart Date Range Detection (`date_range_utils.py`)**:
   - Determines optimal date ranges based on existing data
   - Provides interactive prompting for user input
   - Implements incremental scraping by detecting the most recent review date

### Incremental Scraping Implementation

The system implements incremental scraping through these key functions:

- **`get_smart_date_range(excel_file_path)`**: 
  ```python
  def get_smart_date_range(excel_file_path: str) -> Tuple[datetime, datetime]:
      """
      Determine smart defaults for date range based on existing data and current date.
      
      Args:
          excel_file_path (str): Path to the Excel file with existing reviews.
          
      Returns:
          tuple: (start_date, end_date) as datetime objects with smart defaults.
      """
  ```
  This function:
  - Checks for the existence of the Excel file
  - Reads the "All Reviews" sheet if present
  - Identifies the date column
  - Finds the most recent review date
  - Sets default start date to the day after the latest review
  - Sets default end date to yesterday
  - Falls back to 30 days ago if no existing data is found

- **`prompt_for_date_range(excel_file_path)`**:
  ```python
  def prompt_for_date_range(excel_file_path: str) -> Tuple[datetime, datetime]:
      """
      Prompt the user for date range with smart defaults.
      
      Args:
          excel_file_path (str): Path to the Excel file with existing reviews.
          
      Returns:
          tuple: (start_date, end_date) as datetime objects.
      """
  ```
  This function:
  - Gets smart defaults from `get_smart_date_range`
  - Presents these defaults to the user
  - Accepts user input or uses defaults if none provided
  - Validates the input (format, logical range)
  - Returns the configured date range

These components work together to provide an intelligent date range selection system that makes incremental scraping convenient and automatic.

## Error Handling Strategy

The project implements a multi-layered error handling approach:

1. **Function-Level**: Try/except blocks around critical operations
2. **Component-Level**: Error recovery mechanisms in scrapers
3. **Script-Level**: Graceful degradation in main scripts
4. **Comprehensive Logging**: Detailed logs for debugging

## Extension Points

Developers can extend the system in several ways:

1. **New Platforms**: Create new scraper classes following the existing pattern
2. **Enhanced Analysis**: Improve the categorization and sentiment analysis
3. **Alternative Exports**: Add new exporters (JSON, database, etc.)
4. **Visualization**: Add data visualization and dashboards
5. **Scheduling**: Implement periodic scraping and trend analysis
6. **User Interface**: Develop a web interface or GUI
7. **Better Date Handling**: Extend date parsing for additional formats

### Adding a New Scraper

To add a new review platform scraper:

1. Create a new file in `src/scrapers/` named `[platform]_browserbase_scraper.py`
2. Implement a class that follows the pattern of existing scrapers:
   ```python
   class NewPlatformBrowserbaseScraper:
       def __init__(self, api_key=None, config_path=None):
           self.scraper = BrowserbaseScraper(api_key, config_path)
           self.config = self.scraper.config
           self.selectors = {
               # Platform-specific selectors
           }
       
       def scrape_reviews(self, url=None, max_reviews=100):
           # Implementation
           pass
   ```
3. Update `main_browserbase.py` to include your new platform:
   - Import the new scraper
   - Add a scraping function
   - Update the command-line arguments
   - Add to the platforms dictionary

### Improving Date Range Handling

To extend the date range functionality:

1. Enhance `date_range_utils.py` with additional features:
   - Calendar-based UI selection
   - Automatic scheduling
   - Custom date range presets (last month, last quarter, etc.)

2. Add functions to provide more context about the date range:
   - Statistics about existing data
   - Visualization of review distribution over time
   - Preview of potential new review count

## Performance Considerations

- Scraping is inherently I/O bound and network dependent
- The code uses appropriate timeouts and retries
- Parallel scraping of different platforms could improve performance
- Rate limiting is essential to avoid being blocked
- Smart date ranges can significantly reduce unnecessary scraping

## Testing Strategy

The project includes unit tests for:
- Date parsing logic
- Categorization algorithms
- Excel export functionality
- Date range utilities

Integration tests cover:
- End-to-end scraping workflows (with reduced review counts)
- Configuration loading and validation
- Excel file processing

Tests use mock responses for network operations to ensure reliability.

## Security Considerations

- API keys are managed through configuration files or environment variables
- No personal data is collected beyond what's publicly available
- Network requests use HTTPS
- Input validation prevents injection attacks
- Excel files are validated before reading to prevent formula injection

## Licensing and Legal Considerations

- The project is released under the MIT license
- Developers should review the Terms of Service for each platform
- Rate limiting is implemented to minimize impact on target websites
- The tool is designed for legitimate business intelligence, not for scraping at scale
