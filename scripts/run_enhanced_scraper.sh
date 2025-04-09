#!/bin/bash
# Convenience script to run the restaurant review scraper with enhanced anti-bot detection

# Set script directory as base
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$(dirname "$SCRIPT_DIR")"

# Default options
PLATFORM="all"
MAX_REVIEWS=0
CONFIG_FILE="$BASE_DIR/config.yaml"
ENHANCED=true
HEADLESS=false
DISABLE_STEALTH=false
DISABLE_RANDOM_DELAYS=false
ENABLE_PROXY_ROTATION=false
DEBUG=false

# Parse command line options
while [[ $# -gt 0 ]]; do
  case $1 in
    --platform)
      PLATFORM="$2"
      shift 2
      ;;
    --max-reviews)
      MAX_REVIEWS="$2"
      shift 2
      ;;
    --config)
      CONFIG_FILE="$2"
      shift 2
      ;;
    --no-enhanced)
      ENHANCED=false
      shift
      ;;
    --headless)
      HEADLESS=true
      shift
      ;;
    --no-stealth)
      DISABLE_STEALTH=true
      shift
      ;;
    --no-random-delays)
      DISABLE_RANDOM_DELAYS=true
      shift
      ;;
    --enable-proxy-rotation)
      ENABLE_PROXY_ROTATION=true
      shift
      ;;
    --debug)
      DEBUG=true
      shift
      ;;
    --help)
      echo "Usage: $0 [OPTIONS]"
      echo "Run the restaurant review scraper with enhanced anti-bot protection."
      echo
      echo "Options:"
      echo "  --platform PLATFORM       Platform to scrape (tripadvisor, yelp, google, all)"
      echo "  --max-reviews NUM         Maximum number of reviews to scrape per platform"
      echo "  --config FILE             Path to configuration file"
      echo "  --no-enhanced             Disable enhanced mode (use standard scrapers)"
      echo "  --headless                Run browsers in headless mode"
      echo "  --no-stealth              Disable stealth plugins"
      echo "  --no-random-delays        Disable random delays"
      echo "  --enable-proxy-rotation   Enable proxy rotation"
      echo "  --debug                   Enable debug logging"
      echo "  --help                    Display this help and exit"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Build command
CMD="python $BASE_DIR/src/main.py"

# Add options
if $ENHANCED; then
  CMD+=" --enhanced"
fi

CMD+=" --platform $PLATFORM"

if [ "$MAX_REVIEWS" -gt 0 ]; then
  CMD+=" --max-reviews $MAX_REVIEWS"
fi

CMD+=" --config $CONFIG_FILE"

if $HEADLESS; then
  CMD+=" --headless"
fi

if $DISABLE_STEALTH; then
  CMD+=" --no-stealth"
fi

if $DISABLE_RANDOM_DELAYS; then
  CMD+=" --no-random-delays"
fi

if $ENABLE_PROXY_ROTATION; then
  CMD+=" --enable-proxy-rotation"
fi

if $DEBUG; then
  CMD+=" --debug"
fi

# Display command
echo "Running: $CMD"
echo

# Execute command
eval $CMD
