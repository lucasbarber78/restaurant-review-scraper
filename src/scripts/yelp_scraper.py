#!/usr/bin/env python3
"""
Yelp Review Scraper

This module provides functionality to scrape reviews from Yelp using Browserbase.
"""

import logging
import re
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class YelpScraper:
    """
    Scraper for extracting reviews from Yelp.
    
    This class is designed to be used with the BrowserbaseScraper class.
    """
    
    @staticmethod
    async def scrape_yelp(scraper):
        """Scrape reviews from Yelp."""
        reviews = []
        
        if not scraper.platform_urls['yelp']:
            logger.warning("No Yelp URL provided, skipping")
            return reviews
        
        try:
            # Navigate to Yelp page
            url = scraper.platform_urls['yelp']
            logger.info(f"Navigating to Yelp URL: {url}")
            await scraper.page.goto(url, {'timeout': scraper.timeout * 1000})
            
            # Handle cookie consent
            await scraper.handle_cookies_popup()
            
            # Take a screenshot for debugging
            await scraper.take_screenshot("yelp_initial.png")
            
            # Click on reviews section if needed
            try:
                reviews_tab = await scraper.page.querySelector('a[href="#reviews"]')
                if reviews_tab:
                    await reviews_tab.click()
                    await scraper.page.waitForTimeout(2000)
            except Exception as e:
                logger.warning(f"Error clicking reviews tab: {e}")
            
            # Loop through pages
            page_num = 1
            while page_num <= scraper.max_pages:
                logger.info(f"Processing Yelp reviews page {page_num}")
                
                # Extract reviews from current page
                page_reviews = await YelpScraper.extract_yelp_reviews(scraper)
                reviews.extend(page_reviews)
                
                # Check if we've reached our maximum reviews
                if len(reviews) >= scraper.max_reviews:
                    logger.info(f"Reached maximum reviews limit ({scraper.max_reviews})")
                    break
                
                # Try to navigate to next page
                try:
                    next_button = await scraper.page.querySelector('a.next-link, a[href*="start="]')
                    if next_button:
                        await next_button.click()
                        await scraper.page.waitForTimeout(3000)
                        page_num += 1
                    else:
                        logger.info("No more pages found")
                        break
                except Exception as e:
                    logger.warning(f"Error navigating to next page: {e}")
                    break
        
        except Exception as e:
            logger.error(f"Error scraping Yelp: {e}", exc_info=True)
        
        return reviews
    
    @staticmethod
    async def extract_yelp_reviews(scraper):
        """Extract reviews from the current Yelp page."""
        page_reviews = []
        
        try:
            # Wait for reviews to load
            await scraper.page.waitForSelector('div.review', {'timeout': scraper.timeout * 1000})
            
            # Extract reviews
            reviews = await scraper.page.evaluate('''() => {
                const reviews = [];
                document.querySelectorAll('div.review').forEach(review => {
                    const nameEl = review.querySelector('a.css-1m051bw, .user-passport-info .css-166la90');
                    const dateEl = review.querySelector('span.css-chan6m');
                    const ratingEl = review.querySelector('[aria-label*="star rating"]');
                    const textEl = review.querySelector('span.raw__09f24__T4Ezm, p.comment__09f24__gu0rG');
                    
                    // Extract data if elements exist
                    const reviewerName = nameEl ? nameEl.textContent.trim() : 'Anonymous';
                    const dateText = dateEl ? dateEl.textContent.trim() : '';
                    const ratingText = ratingEl ? ratingEl.getAttribute('aria-label') : '';
                    const ratingValue = ratingText ? parseFloat(ratingText.match(/([\\d.]+) star/)[1]) : 0;
                    const reviewText = textEl ? textEl.textContent.trim() : '';
                    
                    reviews.push({
                        reviewerName,
                        dateText,
                        rating: ratingValue,
                        reviewText
                    });
                });
                return reviews;
            }''')
            
            # Process and filter reviews
            for review in reviews:
                try:
                    # Parse date
                    date_text = review['dateText']
                    try:
                        review_date = scraper._parse_relative_date(date_text)
                    except:
                        review_date = datetime.now()  # Default to current date if parsing fails
                    
                    # Filter by date range
                    if not (scraper.start_date <= review_date <= scraper.end_date):
                        continue
                    
                    page_reviews.append({
                        'reviewer_name': review['reviewerName'],
                        'date': review_date.strftime('%Y-%m-%d'),
                        'rating': review['rating'],
                        'review_text': review['reviewText'],
                        'platform': 'Yelp',
                        'raw_date': date_text
                    })
                    
                    if len(page_reviews) >= scraper.max_reviews:
                        break
                except Exception as e:
                    logger.warning(f"Error processing Yelp review: {e}")
            
            logger.info(f"Extracted {len(page_reviews)} valid Yelp reviews from current page")
        
        except Exception as e:
            logger.error(f"Error extracting Yelp reviews: {e}", exc_info=True)
        
        return page_reviews