# Contributing to Restaurant Review Scraper

Thank you for your interest in contributing to the Restaurant Review Scraper project! This guide will help you understand how to contribute effectively.

## Code of Conduct

Please be respectful and considerate of others when participating in this project. We aim to create a welcoming and inclusive environment for all contributors.

## Getting Started

### Fork the Repository

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/restaurant-review-scraper.git
   cd restaurant-review-scraper
   ```
3. Set up the upstream remote:
   ```bash
   git remote add upstream https://github.com/lucasbarber78/restaurant-review-scraper.git
   ```

### Set Up Development Environment

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   npm install  # For Node.js dependencies
   ```

3. Create a local configuration file:
   ```bash
   cp config_sample.yaml config.yaml
   ```

4. Edit the configuration file with your test credentials and settings:
   ```yaml
   # Add anti-bot settings for testing
   anti_bot_settings:
     enable_random_delays: true
     enable_proxy_rotation: false
     enable_stealth_plugins: true
     headless_mode: false
   ```

## Development Workflow

### Creating a New Feature

1. Make sure your fork is up to date:
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. Make your changes, following the code style and guidelines below.

4. Write tests for your changes.

5. Run the tests:
   ```bash
   pytest
   ```

6. Commit your changes with a descriptive message:
   ```bash
   git commit -m "Add feature: Description of your feature"
   ```

7. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

8. Create a pull request on GitHub.

### Fixing a Bug

1. Find an issue to work on or create a new one.

2. Make sure your fork is up to date (see above).

3. Create a bugfix branch:
   ```bash
   git checkout -b fix/issue-description
   ```

4. Fix the bug and add a test that would have caught the bug.

5. Run the tests to ensure they pass.

6. Commit your changes:
   ```bash
   git commit -m "Fix: Description of the bug fix (fixes #123)"
   ```

7. Push to your fork and create a pull request.

## Adding a New Review Platform

To add support for a new review platform, follow these steps:

1. Create a new scraper class in `src/`:
   - Use the existing scrapers as templates
   - Follow the same naming convention: `platform_scraper_enhanced.py`

2. Implement these key methods:
   - `__init__`: Set up the scraper with appropriate selectors and anti-bot detection settings
   - `scrape`: Main entry point for scraping
   - `_initialize_browser`: Browser initialization with anti-bot protection
   - `_scrape_async`: Async implementation of the scraping process
   - Helper methods for parsing and extracting data

3. Update `src/main.py` to include your new platform:
   - Import your new scraper
   - Add conditional logic to use the enhanced version when appropriate
   - Update platform references throughout the code

4. Add platform-specific configuration to `config.yaml`.

5. Update anti-bot detection modules if needed:
   - Add platform-specific code to `src/utils/stealth_plugins.py`
   - Configure selectors for popup handling

6. Write tests for your new scraper in the `tests/` directory.

7. Update documentation to include the new platform.

## Working with Anti-Bot Detection Modules

The project includes three main anti-bot detection modules:

### 1. Random Delays (`src/utils/delay_utils.py`)

When adding features that involve browser interactions:

- Use `delay_between_actions()` before actions like clicking, scrolling, or typing
- Use `get_random_delay()` when you need a customized delay
- Use `simulate_human_typing()` for form inputs instead of direct `.fill()` methods
- Keep delays realistic (0.5-3s for most actions) to avoid detection

Example:
```python
# Instead of this:
await button.click()
await page.waitForTimeout(1000)

# Do this:
if self.use_random_delays:
    delay_between_actions("click")
await button.click()
await page.waitForTimeout(get_random_delay(1.0, 0.3) * 1000)
```

### 2. Proxy Rotation (`src/utils/proxy_rotation.py`)

When implementing features that need IP rotation:

- Use the `ProxyRotator` class to manage proxy rotation
- Check for rotation conditions using `should_rotate()`
- Apply new proxies at appropriate intervals
- Add proxy configurations to config files

Example:
```python
# Initialize rotator
self.proxy_rotator = ProxyRotator()

# Check for rotation
if self.use_proxy_rotation and self.proxy_rotator:
    if self.proxy_rotator.should_rotate():
        account, proxy = self.proxy_rotator.rotate()
        # Apply new proxy settings
```

### 3. Stealth Plugins (`src/utils/stealth_plugins.py`)

When enhancing browser fingerprinting and behavior simulation:

- Use the `StealthEnhancer` class with the appropriate platform
- Apply fingerprint modifications via `enhance_browser()`
- Implement platform-specific evasions in `_enhance_for_[platform]()`
- Periodically check for CAPTCHAs with `detect_and_handle_captcha()`

Example:
```python
# Initialize stealth enhancer
if self.use_stealth_plugins:
    self.stealth_enhancer = StealthEnhancer("platform_name")
    
# Apply stealth measures
await self.stealth_enhancer.enhance_browser(self.page)

# Check for CAPTCHAs
captcha_detected = await self.stealth_enhancer.detect_and_handle_captcha(self.page)
```

## Code Style Guidelines

### Python

- Follow PEP 8 guidelines
- Use type hints for function parameters and return values
- Write docstrings for all classes and methods
- Maximum line length of 100 characters
- Use meaningful variable and function names

### Anti-Bot Detection Code

- Document randomization techniques clearly
- Keep behavior simulation realistic and human-like
- Avoid hardcoded timing values (use configuration parameters)
- Handle errors gracefully with fallback mechanisms
- Use logging for debugging anti-bot detection issues

### Documentation

- Update relevant documentation when making changes
- Use Markdown for documentation files
- Include examples where appropriate
- Ensure documentation reflects the current behavior of the code

## Testing

We use pytest for testing. Please write tests for:

- New features you add
- Bug fixes you implement
- Edge cases and error handling

For anti-bot detection features, include tests for:

- Randomization functions (with fixed seeds for reproducibility)
- Proxy rotation logic
- Stealth plugin functionality (with mocked browser objects)
- CAPTCHA detection and handling

To run the tests:
```bash
pytest
```

For test coverage:
```bash
pytest --cov=src
```

## Pull Request Process

1. Ensure your code passes all tests.
2. Update documentation if necessary.
3. Ensure your code follows the style guidelines.
4. Fill out the pull request template completely.
5. Wait for code review and address any feedback.

## Common Contribution Opportunities

Here are some areas where contributions are particularly welcome:

### Scraper Improvements

- Update selectors for existing platforms when they change
- Add support for more review platforms
- Improve error handling and resilience
- Optimize performance and reduce resource usage

### Anti-Bot Detection Enhancements

- Implement additional stealth techniques for specific platforms
- Add support for CAPTCHA solving services
- Improve browser fingerprint randomization
- Add more sophisticated human behavior simulation
- Develop better proxy rotation strategies

### Data Analysis

- Enhance the review categorization logic
- Improve sentiment analysis accuracy
- Add new analysis features (topic modeling, entity recognition, etc.)
- Create visualizations for the review data

### User Experience

- Improve command-line interface
- Add a web interface or dashboard
- Create better error messages and logging
- Add progress indicators for long-running operations

### Documentation

- Improve existing documentation
- Add more examples and use cases
- Create video tutorials
- Translate documentation to other languages

## Licensing

By contributing to this project, you agree that your contributions will be licensed under the project's MIT license.
