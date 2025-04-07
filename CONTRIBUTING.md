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
   pip install -r requirements_browserbase.txt
   pip install -r requirements-dev.txt  # For development-specific packages
   ```

3. Create a local configuration file:
   ```bash
   cp config_browserbase_sample.yaml config.yaml
   ```

4. Edit the configuration file with your test credentials and settings.

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

1. Create a new scraper class in `src/scrapers/`:
   - Use the existing scrapers as templates
   - Follow the same naming convention: `platform_browserbase_scraper.py`

2. Implement these key methods:
   - `__init__`: Set up the scraper with appropriate selectors
   - `scrape_reviews`: Main scraping logic
   - Helper methods for parsing and extracting data

3. Update `src/main_browserbase.py` to include your new platform:
   - Import your new scraper
   - Add a new scraping function
   - Update the `platforms_to_scrape` list and related logic

4. Add platform-specific configuration to `config_browserbase_sample.yaml`.

5. Write tests for your new scraper in the `tests/` directory.

6. Update documentation to include the new platform.

## Code Style Guidelines

### Python

- Follow PEP 8 guidelines
- Use type hints for function parameters and return values
- Write docstrings for all classes and methods
- Maximum line length of 100 characters
- Use meaningful variable and function names

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
