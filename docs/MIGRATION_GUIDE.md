# Migration Guide: Moving to Enhanced Anti-Bot Detection

This guide will help you transition from the original version of the Restaurant Review Scraper to the new enhanced version with advanced anti-bot detection features.

## Why Migrate?

The enhanced version offers several key advantages:

1. **More Reliable Scraping**: Less likely to be blocked by review sites that have anti-bot measures
2. **Customizable Anti-Bot Features**: Three distinct systems that can be enabled independently:
   - Random Delays
   - Proxy Rotation
   - Stealth Plugins
3. **Platform-Specific Optimizations**: Special handling for Yelp's advanced detection systems
4. **Human-Like Behavior**: Natural interaction patterns that reduce detection likelihood
5. **Better Success Rates**: Especially for sites with sophisticated anti-bot systems like Yelp

## Migration Steps

### 1. Update Your Dependencies

Ensure all dependencies are installed for the enhanced version:

```bash
pip install -r requirements.txt
```

New dependencies include:
- numpy (for Gaussian distribution in random delays)
- aiohttp (for async HTTP requests) 
- fake-useragent (for randomizing user agents)
- brotli (for decompression support)

### 2. Update Your Configuration

1. Add the anti-bot configuration section to your existing config file:

   ```yaml
   # Anti-bot detection settings
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
     
     # Proxy rotation settings (optional)
     enable_proxy_rotation: false
     proxy_rotation_interval_minutes: 30
     proxy_rotation_frequency: 10
     random_proxy_rotation: true
     
     # Stealth enhancement settings
     enable_stealth_plugins: true
     headless_mode: false
     simulate_human_behavior: true
     randomize_fingerprint: true
     platform_specific_stealth:
       yelp: true
       tripadvisor: true
       google: false
   ```

2. If you plan to use proxy rotation, add the proxy configuration:

   ```yaml
   # Multiple Browserbase accounts for rotation
   browserbase_accounts:
     - name: "Primary Account"
       api_key: "YOUR_API_KEY_HERE"
     # Add more accounts as needed
     # - name: "Secondary Account"
     #   api_key: "SECOND_API_KEY_HERE"

   # Proxy configurations
   proxies:
     # Example proxy entries (uncomment and fill in to use)
     # - host: "proxy1.example.com"
     #   port: 8080
     #   username: "user1"
     #   password: "pass1"
   ```

### 3. Test the New Version

Run a test scrape with the enhanced version and a small number of reviews:

```bash
python src/main.py --enhanced --max-reviews 10
```

Check that the results are as expected before proceeding with full-scale scraping.

### 4. Switch Your Workflow

Once you've verified that the enhanced version works correctly, you can switch your regular workflow:

1. Use `main.py --enhanced` instead of just `main.py`
2. Add any additional options you need

Example:
```bash
# Old command
python src/main.py --max-reviews 100

# New command
python src/main.py --enhanced --max-reviews 100
```

## Feature Comparison

| Feature | Original Version | Enhanced Version |
|---------|------------------|------------------|
| Anti-bot detection avoidance | Basic | Advanced |
| Yelp success rate | Low-Medium | High |
| TripAdvisor success rate | Medium | High |
| Google success rate | Medium | Medium-High |
| Configuration options | Limited | Extensive |
| Speed | Faster | Slightly slower due to human simulation |
| Reliability | Moderate | High |
| Resource usage | Lower | Slightly higher |

## New Configuration Options

The enhanced version adds these configuration options:

### Random Delay Settings

```yaml
enable_random_delays: true  # Enable/disable random delays
delay_base_values:
  click: 1.0                # Base delay for click actions (seconds)
  scroll: 1.5               # Base delay for scroll actions
  navigation: 3.0           # Base delay for page navigation
  typing: 0.2               # Base delay between keystrokes
  default: 1.0              # Default delay for other actions
delay_variance: 0.5         # Random variance factor
```

### Proxy Rotation Settings

```yaml
enable_proxy_rotation: false                 # Enable/disable proxy rotation
proxy_rotation_interval_minutes: 30          # Time-based rotation interval
proxy_rotation_frequency: 10                 # Request-count-based rotation
random_proxy_rotation: true                  # Random vs. sequential selection
```

### Stealth Plugin Settings

```yaml
enable_stealth_plugins: true                 # Enable/disable stealth plugins
headless_mode: false                         # Run in headless mode
simulate_human_behavior: true                # Simulate human-like behaviors
randomize_fingerprint: true                  # Use random browser fingerprints
platform_specific_stealth:                   # Platform-specific optimizations
  yelp: true                                 # Enhanced protection for Yelp
  tripadvisor: true                          # Enhanced protection for TripAdvisor
  google: false                              # Standard protection for Google
```

## Command Line Options

The enhanced version adds these command line options:

```bash
--enhanced                 # Use enhanced anti-bot detection features
--headless                 # Run in headless mode (less visible but more detectable)
--no-stealth               # Disable stealth plugins (not recommended)
--no-random-delays         # Disable random delays (not recommended)
--enable-proxy-rotation    # Enable proxy rotation if configured
```

## Code Differences

If you've made custom modifications to the original codebase, note these key differences:

### New Files

- `src/utils/delay_utils.py`: Randomized human-like delays
- `src/utils/proxy_rotation.py`: Multi-account and proxy rotation
- `src/utils/stealth_plugins.py`: Advanced fingerprint and behavior simulation
- `src/yelp_scraper_enhanced.py`: Enhanced Yelp scraper with anti-bot features

### Modified Files

- `src/main.py`: Updated to support enhanced features
- `requirements.txt`: Added new dependencies

## Backwards Compatibility

The enhanced version is fully backwards compatible with the original version. You can use the original version by simply not including the `--enhanced` flag:

```bash
# Original version behavior
python src/main.py

# Enhanced version behavior
python src/main.py --enhanced
```

## Common Migration Issues

### 1. Dependency Issues

**Symptom**: Import errors when running the enhanced version.

**Solution**: 
- Ensure you've installed all requirements from `requirements.txt`
- If you're using a virtual environment, make sure it's activated
- Check for conflicting package versions with `pip list`

### 2. Configuration Errors

**Symptom**: Error loading configuration or unexpected behavior.

**Solution**:
- Verify your YAML syntax (spacing and indentation are important)
- Check that all required fields are present
- Try using the sample configuration as a template

### 3. Browser Control Issues

**Symptom**: Browser doesn't start or crashes during operation.

**Solution**:
- Try running in non-headless mode (`--headless false`)
- Check that you have a compatible browser installed
- Update your browser to the latest version
- Try with a smaller number of reviews first

### 4. Performance Concerns

**Symptom**: Scraping takes longer than with the original version.

**Solution**:
- This is expected - the enhanced version deliberately adds delays to simulate human behavior
- If speed is more important than avoiding detection, you can:
  - Reduce base delay values in the configuration
  - Disable certain features (e.g., `--no-random-delays`)
  - Note that these changes may increase your risk of detection

## Getting Help

If you encounter problems during migration:

1. Check the `scraper.log` file for detailed error messages
2. Review the updated documentation in the `docs` directory
3. Submit an issue on GitHub with details about your migration problem

## Reverting if Necessary

If you need to revert to the original version temporarily:

1. Simply run without the `--enhanced` flag:
   ```bash
   python src/main.py --config config.yaml
   ```

## Future Considerations

The enhanced anti-bot detection features will be the primary supported approach going forward. Future improvements may include:

- Additional stealth techniques for other review platforms
- More sophisticated human behavior simulation
- Integrated CAPTCHA solving capabilities
- Expanded proxy and VPN support
- AI-assisted fingerprint generation

We recommend completing the migration to take advantage of these current and future enhancements.
