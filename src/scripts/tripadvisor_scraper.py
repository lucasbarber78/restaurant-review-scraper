#!/usr/bin/env python3
"""
TripAdvisor Review Scraper

This module provides functionality to scrape reviews from TripAdvisor using Browserbase.
"""

import logging
import re
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class TripAdvisorScraper:
    """
    Scraper for extracting reviews from TripAdvisor.
    
    This class is designed to be used with the BrowserbaseScraper class.
    """
    
    @staticmethod
    async def scrape_tripadvisor(scraper):
        """Scrape reviews from TripAdvisor."""
        reviews = []
        
        if not scraper.platform_urls['tripadvisor']:
            logger.warning("No TripAdvisor URL provided, skipping")
            return reviews
        
        try:
            # Navigate to TripAdvisor page
            url = scraper.platform_urls['tripadvisor']
            logger.info(f"Navigating to TripAdvisor URL: {url}")
            await scraper.page.goto(url, {'timeout': scraper.timeout * 1000})
            
            # Handle cookie consent
            await scraper.handle_cookies_popup()
            
            # Take a screenshot for debugging
            await scraper.take_screenshot("tripadvisor_initial.png")
            
            # Check if we need to click on "Reviews" tab
            try:
                reviews_tab = await scraper.page.querySelector('a[data-tab="TABS_REVIEWS"]')
                if reviews_tab:
                    await reviews_tab.click()
                    await scraper.page.waitForTimeout(2000)
            except Exception as e:
                logger.warning(f"Error clicking reviews tab: {e}")
            
            # Wait for reviews to load
            await scraper.page.waitForSelector('.reviewSelector', {'timeout': scraper.timeout * 1000})
            
            # Loop through pages
            page_num = 1
            while page_num <= scraper.max_pages:
                logger.info(f"Processing TripAdvisor reviews page {page_num}")
                
                # Extract reviews from current page
                page_reviews = await TripAdvisorScraper.extract_tripadvisor_reviews(scraper)
                reviews.extend(page_reviews)
                
                # Check if we've reached our maximum reviews
                if len(reviews) >= scraper.max_reviews:
                    logger.info(f"Reached maximum reviews limit ({scraper.max_reviews})")
                    break
                
                # Try to navigate to next page
                try:
                    next_button = await scraper.page.querySelector('.ui_pagination a.next')
                    if next_button:
                        await next_button.click()
                        await scraper.page.waitForSelector('.reviewSelector', {'timeout': scraper.timeout * 1000})
                        await scraper.page.waitForTimeout(3000)
                        page_num += 1
                    else:
                        logger.info("No more pages found")
                        break
                except Exception as e:
                    logger.warning(f"Error navigating to next page: {e}")
                    break
        
        except Exception as e:
            logger.error(f"Error scraping TripAdvisor: {e}", exc_info=True)
        
        return reviews
    
    @staticmethod
    async def extract_tripadvisor_reviews(scraper):
        """Extract reviews from the current TripAdvisor page."""
        page_reviews = []
        
        try:
            # Click "More" buttons to expand review text
            more_buttons = await scraper.page.querySelectorAll('span.taLnk.ulBlueLinks')
            for button in more_buttons:
                try:
                    await button.click()
                    await scraper.page.waitForTimeout(300)
                except Exception:
                    pass
            
            # Extract reviews
            reviews = await scraper.page.evaluate('''() => {
                const reviews = [];
                document.querySelectorAll('.reviewSelector').forEach(review => {
                    // Extract reviewer name
                    const nameElement = review.querySelector('.info_text');
                    let reviewerName = nameElement ? nameElement.textContent.trim() : 'Anonymous';
                    
                    // Extract review date
                    const dateElement = review.querySelector('.ratingDate');
                    let dateText = dateElement ? dateElement.getAttribute('title') || dateElement.textContent.trim() : '';
                    dateText = dateText.replace('Reviewed', '').trim();
                    
                    // Extract rating
                    const ratingElement = review.querySelector('.ui_bubble_rating');
                    const ratingClass = ratingElement ? ratingElement.className : '';
                    const ratingMatch = ratingClass.match(/bubble_(\\d+)/);
                    const rating = ratingMatch ? parseInt(ratingMatch[1]) / 10 : 0;
                    
                    // Extract review title
                    const titleElement = review.querySelector('.noQuotes');
                    const reviewTitle = titleElement ? titleElement.textContent.trim() : '';
                    
                    // Extract review text
                    const textElement = review.querySelector('.partial_entry');
                    const reviewText = textElement ? textElement.textContent.trim() : '';
                    
                    reviews.push({
                        reviewerName,
                        dateText,
                        rating,
                        reviewTitle,
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
                        # Try with dateutil parser
                        from dateutil import parser
                        review_date = parser.parse(date_text, fuzzy=True)
                    except:
                        # Fall back to our custom date parser
                        review_date = scraper._parse_relative_date(date_text)
                    
                    # Filter by date range
                    if not (scraper.start_date <= review_date.replace(tzinfo=None) <= scraper.end_date):
                        continue
                    
                    page_reviews.append({
                        'reviewer_name': review['reviewerName'],
                        'date': review_date.strftime('%Y-%m-%d'),
                        'rating': review['rating'],
                        'title': review['reviewTitle'],
                        'review_text': review['reviewText'],
                        'platform': 'TripAdvisor',
                        'raw_date': date_text
                    })
                    
                    if len(page_reviews) >= scraper.max_reviews:
                        break
                except Exception as e:
                    logger.warning(f"Error processing TripAdvisor review: {e}")
            
            logger.info(f"Extracted {len(page_reviews)} valid TripAdvisor reviews from current page")
        
        except Exception as e:
            logger.error(f"Error extracting TripAdvisor reviews: {e}", exc_info=True)
        
        return page_reviews