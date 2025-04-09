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
   - **NEW** Anti-Bot Detection Utilities:
     - `delay_utils.py` (Randomized human-like delays)
     - `proxy_rotation.py` (Multi-account and proxy rotation)
     - `stealth_plugins.py` (Advanced fingerprint and behavior simulation)

2. **Platform-Specific Scrapers**
   - TripAdvisor scrapers (`tripadvisor_scraper.py`, `tripadvisor_puppeteer_scraper.py`)
   - Yelp scrapers (`yelp_scraper.py`, **NEW** `yelp_scraper_enhanced.py`)
   - Google Reviews scrapers

3. **Data Processing**
   - `review_categorizer.py` (text categorization and sentiment analysis)
   - `date_utils.py` (date parsing and normalization)
   - `date_range_utils.py` (smart date range determination and user prompting)

4. **Data Export**
   - `excel_exporter.py` (structured data export to Excel)

5. **Main Orchestration**
   - `main.py` (Updated to support enhanced anti-bot features)
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

### Enhanced Anti-Bot Version (NEW)

The enhanced version builds on the Puppeteer approach but adds sophisticated anti-bot detection evasion mechanisms:

- **Random Delays**: Gaussian distribution for human-like timing patterns
- **Proxy Rotation**: Multiple account and proxy support
- **Stealth Plugins**: Browser fingerprint and automation indicator masking
- **Human-like Behavior Simulation**: Natural scrolling, clicking, and interaction patterns

### Browserbase (Alternative)

The Browserbase version uses a cloud-based browser automation service that:

- Provides pre-configured browser sessions with anti-detection measures
- Eliminates the need for local browser installation
- Offers better stability and reliability
- Requires an API key and may incur usage costs

## Anti-Bot Detection Systems (NEW)

The anti-bot detection mitigation system consists of three main components:

### 1. Random Delay System

The `delay_utils.py` module provides functions for generating human-like delays between actions:

- **Gaussian Distributions**: Uses bell curve randomization instead of uniform distribution for more natural timing
- **Action-Specific Delays**: Different delay patterns for different actions (clicking, scrolling, typing)
- **Natural Typing Simulation**: Variable typing speed with occasional pauses

Key Implementation:
```python
def get_random_delay(base_delay: float = 2.0, variance: float = 1.0) -> float:
    """Generate a random delay with Gaussian distribution around the base delay."""
    # Use Gaussian distribution for more human-like randomness
    delay = random.gauss(base_delay, variance)
    # Ensure delay is not negative or too short
    return max(0.5, delay)
```

### 2. Proxy Rotation System

The `proxy_rotation.py` module implements account and proxy rotation to avoid IP-based detection:

- **Time-Based Rotation**: Changes proxies after configured time intervals
- **Request-Count Rotation**: Rotates after specified number of operations
- **Multiple Account Support**: Manages multiple Browserbase accounts
- **Configurable Selection**: Sequential or random selection options

Key Implementation:
```python
class ProxyRotator:
    """Class for managing proxy rotation across multiple Browserbase accounts."""
    
    def __init__(self, config_path: Optional[str] = None):
        # Initialize proxy configuration
        
    def rotate(self) -> Tuple[Dict[str, Any], Optional[Dict[str, str]]]:
        """Rotate to a new account and/or proxy."""
        # Implementation for rotating accounts and proxies
```

### 3. Stealth Plugins System

The `stealth_plugins.py` module provides browser fingerprinting and behavior simulation:

- **WebGL Fingerprint Spoofing**: Consistent renderer/vendor data
- **Navigator Property Overrides**: Hides automation indicators
- **Canvas Fingerprinting Evasion**: Adds randomized noise to avoid fingerprinting
- **Platform-Specific Optimizations**: Custom handling for Yelp and TripAdvisor

Key Implementation:
```python
class StealthEnhancer:
    """Class for enhancing browser stealth capabilities beyond basic settings."""
    
    def __init__(self, platform: str = "general"):
        # Initialize stealth enhancer for specific platform
        
    async def enhance_browser(self, page):
        """Apply all stealth enhancements to a browser page."""
        # Implementation of stealth enhancement techniques
```

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
- **NEW**: Enhanced stealth handling specifically for Yelp's detection methods
- **NEW**: Special handling for cookie and login prompts

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
8. **NEW: Advanced Anti-Bot Techniques**: Extend stealth plugins for other platforms

### Adding a New Scraper with Anti-Bot Protection

To add a new review platform scraper with anti-bot protection:

1. Create a new file in `src/` named `[platform]_scraper_enhanced.py`
2. Implement a class that follows the pattern of the enhanced Yelp scraper:
   ```python
   class EnhancedNewPlatformScraper:
       def __init__(self, config):
           self.config = config
           self.anti_bot_settings = config.get('anti_bot_settings', {})
           self.use_random_delays = self.anti_bot_settings.get('enable_random_delays', True)
           self.use_proxy_rotation = self.anti_bot_settings.get('enable_proxy_rotation', False)
           self.use_stealth_plugins = self.anti_bot_settings.get('enable_stealth_plugins', True)
           
           # Initialize stealth enhancer for the specific platform
           if self.use_stealth_plugins:
               self.stealth_enhancer = StealthEnhancer("[platform]")
           
           # Initialize proxy rotator if enabled
           if self.use_proxy_rotation:
               self.proxy_rotator = ProxyRotator()
       
       def scrape(self):
           # Implementation with anti-bot techniques
           pass
   ```
3. Update `main.py` to include your new platform:
   - Import the new scraper
   - Add conditional logic to use either standard or enhanced version
   - Update the command-line arguments if needed

### Implementing New Anti-Bot Techniques

To implement additional anti-bot detection evasion techniques:

1. Identify the detection mechanism you want to target
2. Extend the appropriate utility module:
   - For timing-based techniques: `delay_utils.py`
   - For proxy or IP-based techniques: `proxy_rotation.py`
   - For browser fingerprinting and behavior: `stealth_plugins.py`
3. Add appropriate integration points in the enhanced scraper classes

## Performance Considerations

- Scraping is inherently I/O bound and network dependent
- The code uses appropriate timeouts and retries
- Parallel scraping of different platforms could improve performance
- Rate limiting is essential to avoid being blocked
- Smart date ranges can significantly reduce unnecessary scraping
- **NEW**: Anti-bot features may slightly impact performance but greatly improve reliability

## Testing Strategy

The project includes unit tests for:
- Date parsing logic
- Categorization algorithms
- Excel export functionality
- Date range utilities
- **NEW**: Anti-bot utility functions

Integration tests cover:
- End-to-end scraping workflows (with reduced review counts)
- Configuration loading and validation
- Excel file processing
- **NEW**: Anti-bot effectiveness against different platforms

Tests use mock responses for network operations to ensure reliability.

## Security Considerations

- API keys are managed through configuration files or environment variables
- No personal data is collected beyond what's publicly available
- Network requests use HTTPS
- Input validation prevents injection attacks
- Excel files are validated before reading to prevent formula injection
- **NEW**: Proxy credentials are handled securely

## Licensing and Legal Considerations

- The project is released under the MIT license
- Developers should review the Terms of Service for each platform
- Rate limiting is implemented to minimize impact on target websites
- The tool is designed for legitimate business intelligence, not for scraping at scale
