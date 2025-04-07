/**
 * Yelp Reviews Scraper for Browserbase
 * 
 * This script uses Browserbase to loop through all Yelp review pages for a restaurant,
 * extract review data, and save it to a CSV file.
 */

/**
 * Extract reviews from the current page
 * @returns {Array} Array of review objects
 */
async function extractReviewsFromCurrentPage() {
  console.log('Extracting reviews from current page...');
  
  // Extract all review elements
  const reviews = [];
  
  // Get all review containers on the page
  const reviewElements = document.querySelectorAll('[data-review-id]');
  console.log(`Found ${reviewElements.length} review elements on current page`);
  
  for (const element of reviewElements) {
    try {
      // Extract reviewer information
      const nameElement = element.querySelector('.css-1m051bw') || element.querySelector('.user-passport-info a');
      const reviewerName = nameElement ? nameElement.textContent.trim() : 'Anonymous';
      
      // Extract location
      const locationElement = element.querySelector('.css-n6i4z7');
      const location = locationElement ? locationElement.textContent.trim() : '';
      
      // Extract rating
      const ratingElement = element.querySelector('[aria-label*="star rating"]');
      let rating = 0;
      if (ratingElement) {
        const ratingMatch = ratingElement.getAttribute('aria-label').match(/([\d.]+) star/);
        rating = ratingMatch ? parseFloat(ratingMatch[1]) : 0;
      }
      
      // Extract date
      const dateElement = element.querySelector('.css-chan6m');
      const date = dateElement ? dateElement.textContent.trim() : '';
      
      // Extract review text
      const textElement = element.querySelector('.comment__09f24__gu0rG span');
      const reviewText = textElement ? textElement.textContent.trim() : '';
      
      if (reviewText) {
        reviews.push({
          platform: 'Yelp',
          reviewer_name: reviewerName,
          location: location,
          date: date,
          rating: rating,
          text: reviewText,
          url: window.location.href
        });
      }
    } catch (error) {
      console.error('Error extracting review:', error);
    }
  }
  
  return reviews;
}

/**
 * Navigate to the next page of reviews
 * @returns {Boolean} True if navigation was successful, false if there are no more pages
 */
async function goToNextPage() {
  // Find the "Next" button
  const nextButton = document.querySelector('a.next-link') || 
                     document.querySelector('.pagination__09f24__VZrF8 a[href*="start="]:last-child') ||
                     document.querySelector('a[href*="start="]:not(.prev-link)');
  
  if (nextButton) {
    console.log('Clicking Next button...');
    nextButton.click();
    return true;
  }
  
  console.log('No Next button found, reached the end of reviews');
  return false;
}

/**
 * Main scraping function
 * @param {Number} maxPages Maximum number of pages to scrape (0 for all pages)
 * @returns {Array} Array of all reviews across all pages
 */
async function scrapeAllReviews(maxPages = 0) {
  let allReviews = [];
  let currentPage = 1;
  let hasMorePages = true;
  
  console.log('Starting review scraping process...');
  
  // Wait for reviews to load on the initial page
  await new Promise(resolve => setTimeout(resolve, 3000));
  
  while (hasMorePages && (maxPages === 0 || currentPage <= maxPages)) {
    console.log(`Processing page ${currentPage}...`);
    
    // Extract reviews from current page
    const pageReviews = await extractReviewsFromCurrentPage();
    allReviews = allReviews.concat(pageReviews);
    console.log(`Extracted ${pageReviews.length} reviews (total: ${allReviews.length})`);
    
    // Try to navigate to next page
    if (currentPage < maxPages || maxPages === 0) {
      hasMorePages = await goToNextPage();
      if (hasMorePages) {
        // Wait for the next page to load
        await new Promise(resolve => setTimeout(resolve, 3000));
        currentPage++;
      }
    } else {
      hasMorePages = false;
    }
  }
  
  console.log(`Scraping complete! Total reviews collected: ${allReviews.length}`);
  return allReviews;
}

/**
 * Initialize the scraping process for a restaurant on Yelp
 * @param {String} restaurantUrl The Yelp URL of the restaurant
 * @param {Number} maxPages Maximum number of pages to scrape (0 for all)
 */
async function scrapeRestaurantReviews(restaurantUrl, maxPages = 0) {
  try {
    // Navigate to the restaurant page
    console.log(`Navigating to ${restaurantUrl}`);
    window.location.href = restaurantUrl;
    
    // Wait for page to load
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // Navigate to the reviews section if not already there
    const reviewsLink = document.querySelector('a[href="#reviews"]');
    if (reviewsLink) {
      console.log('Clicking on Reviews tab...');
      reviewsLink.click();
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
    
    // Begin scraping all reviews
    const allReviews = await scrapeAllReviews(maxPages);
    
    // Format for CSV
    console.log('Reviews collected:', allReviews);
    
    return allReviews;
  } catch (error) {
    console.error('Error during scraping:', error);
    return [];
  }
}

// Example usage (to be executed in the browser console via Browserbase)
// scrapeRestaurantReviews('https://www.yelp.com/biz/bowens-island-restaurant-charleston-3', 5)
//   .then(reviews => console.log('Final review count:', reviews.length));
