# Migration Guide: Moving to the Browserbase Version

This guide will help you transition from the original Puppeteer-based version of the Restaurant Review Scraper to the new Browserbase-powered version.

## Why Migrate?

The Browserbase version offers several key advantages:

1. **More Reliable Scraping**: Less likely to be blocked by review sites that have anti-bot measures
2. **Simpler Setup**: No need to install or manage local browser instances
3. **Cross-Platform Compatibility**: Works consistently across operating systems
4. **Better Performance**: Faster and more efficient scraping with cloud-based browsers
5. **Lower Resource Usage**: Reduced CPU and memory consumption on your local machine

## Migration Steps

### 1. Get a Browserbase API Key

Before you begin migration, you'll need to:

1. Sign up for a Browserbase account at [browserbase.com](https://browserbase.com)
2. Create an API key in your dashboard
3. Copy the API key for use in your configuration

### 2. Update Your Configuration

1. Create a new configuration file based on the Browserbase sample:
   ```bash
   cp config_browserbase_sample.yaml config_browserbase.yaml
   ```

2. Transfer your existing settings from your old `config.yaml`:
   - Restaurant details (name, URLs)
   - Date range settings
   - Export file path
   - Categorization and sentiment configuration

3. Add your Browserbase API key:
   ```yaml
   browserbase_api_key: "your_api_key_here"
   ```

### 3. Install Updated Dependencies

Update your dependencies to ensure you have everything needed for the Browserbase version:

```bash
pip install -r requirements_browserbase.txt
```

Note: This will not remove your existing dependencies for the original version, allowing you to use both versions if needed.

### 4. Test the New Version

Run a test scrape with a small number of reviews:

```bash
python src/main_browserbase.py --max-reviews 10 --config config_browserbase.yaml
```

Check that the results are as expected before proceeding with full-scale scraping.

### 5. Switch Your Workflow

Once you've verified that the Browserbase version works correctly, you can switch your regular workflow:

1. Use `main_browserbase.py` instead of `main.py`
2. Use your new configuration file
3. Update any scripts or automation to use the new command

Example:
```bash
# Old command
python src/main.py --max-reviews 100

# New command
python src/main.py --max-reviews 100 --config config_browserbase.yaml
# OR
python src/main_browserbase.py --max-reviews 100
```

## Configuration Differences

### New Configuration Options

The Browserbase version adds these configuration options:

```yaml
# Required for Browserbase
browserbase_api_key: "your_api_key_here"
```

### Removed Configuration Options

These options from the original version are no longer needed:

```yaml
# Browser options (no longer needed)
browser:
  headless: true
  proxy: null
  user_agent: "Mozilla/5.0 ..."
```

## Code Differences

If you've made custom modifications to the original codebase, note these key differences:

### Directory Structure Changes

- New scrapers are in `src/scrapers/` directory
- Base Browserbase functionality is in `src/utils/browserbase_scraper.py`

### API Differences

The Browserbase API differs from Puppeteer in these ways:

1. Session management is handled differently
2. Some browser control methods have changed names
3. The way elements are selected and interacted with has been simplified

### Function Names and Parameters

If you've extended the original code, you may need to update function calls:

| Original (Puppeteer) | Browserbase Equivalent |
|----------------------|------------------------|
| `create_browser_session()` | `scraper.create_session()` |
| `page.goto(url)` | `scraper.navigate(url)` |
| `page.click(selector)` | `scraper.click(selector)` |
| `page.type(selector, text)` | `scraper.fill(selector, value)` |
| `browser.close()` | `scraper.close_session()` |

## Fallback Options

The original version is still available if you encounter any issues with the Browserbase version:

```bash
python src/main.py --config your_original_config.yaml
```

## Common Migration Issues

### 1. API Key Issues

**Symptom**: Error about invalid or missing API key.

**Solution**: 
- Double-check your API key
- Ensure it's correctly formatted in the config file
- Verify your Browserbase account is active

### 2. Selector Differences

**Symptom**: Reviews aren't being found or scraped correctly.

**Solution**:
- The Browserbase version may use slightly different selectors
- Check the logs for specific element selection errors
- Try with a smaller number of reviews first

### 3. Rate Limiting

**Symptom**: Scraping stops unexpectedly or returns fewer reviews than expected.

**Solution**:
- Browserbase has different rate limiting than local browsers
- Add delays between requests by modifying the scraper code
- Reduce the number of reviews per run
- Split your scraping into smaller batches

### 4. Dependency Conflicts

**Symptom**: Import errors or unexpected behavior.

**Solution**:
- Consider using a virtual environment to isolate dependencies
- Ensure you've installed all requirements from `requirements_browserbase.txt`
- Check for conflicting package versions

## Getting Help

If you encounter problems during migration:

1. Check the `scraper.log` file for detailed error messages
2. Review the updated documentation in the `docs` directory
3. Submit an issue on GitHub with details about your migration problem

## Reverting if Necessary

If you need to revert to the original version temporarily:

1. Keep both configuration files available
2. Use the original main script with your original config:
   ```bash
   python src/main.py --config config.yaml
   ```

## Future Considerations

The Browserbase version will be the primary supported version going forward. Future features and improvements will be focused on this version, so we recommend completing the migration when feasible.
