#!/usr/bin/env python3
"""
Stealth Plugins Module

This module provides functions and classes to implement additional stealth measures
specifically for sites with strong anti-bot detection like Yelp.
"""

import logging
import random
import json
import re
import time
from typing import Dict, List, Optional, Any, Union

logger = logging.getLogger(__name__)

class StealthEnhancer:
    """Class for enhancing browser stealth capabilities beyond basic settings."""
    
    def __init__(self, platform: str = "general"):
        """Initialize the StealthEnhancer.
        
        Args:
            platform (str): Target platform ("yelp", "tripadvisor", "google", "general").
        """
        self.platform = platform.lower()
        self.scripts_applied = set()
        
        # Define browser fingerprints
        self._init_fingerprints()
    
    def _init_fingerprints(self):
        """Initialize realistic browser fingerprints."""
        # Common user agents
        self.user_agents = [
            # Chrome on Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            # Chrome on macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            # Firefox on Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
            # Safari on macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
            # Edge on Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
        ]
        
        # WebGL vendors and renderers
        self.webgl_data = [
            {"vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0, D3D11)"},
            {"vendor": "Google Inc. (AMD)", "renderer": "ANGLE (AMD, AMD Radeon RX 6800 XT Direct3D11 vs_5_0 ps_5_0, D3D11)"},
            {"vendor": "Google Inc. (Intel)", "renderer": "ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0, D3D11)"},
            {"vendor": "Apple", "renderer": "Apple M1"},
            {"vendor": "Intel Inc.", "renderer": "Intel Iris Pro OpenGL Engine"}
        ]
        
        # Platform specific data
        self.platform_data = {
            "yelp": {
                "cookies_to_preserve": ["__ycab", "bse", "_ga", "_gid"],
                "headers": {
                    "Accept-Language": "en-US,en;q=0.9",
                    "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"120\", \"Google Chrome\";v=\"120\"",
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": "\"Windows\"",
                }
            },
            "tripadvisor": {
                "cookies_to_preserve": ["TASession", "TASameSite", "TAUD", "TADCID"],
                "headers": {
                    "Accept-Language": "en-US,en;q=0.9",
                    "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"120\", \"Google Chrome\";v=\"120\"",
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": "\"Windows\"",
                }
            }
        }
    
    def get_browser_fingerprint(self) -> Dict[str, Any]:
        """Get a random realistic browser fingerprint.
        
        Returns:
            dict: A browser fingerprint configuration.
        """
        # Select a random user agent
        user_agent = random.choice(self.user_agents)
        
        # Select random WebGL data
        webgl = random.choice(self.webgl_data)
        
        # Determine OS and browser from user agent
        os_name = "Windows"
        if "Macintosh" in user_agent:
            os_name = "Mac OS"
        elif "Linux" in user_agent:
            os_name = "Linux"
            
        browser_name = "Chrome"
        if "Firefox" in user_agent:
            browser_name = "Firefox"
        elif "Safari" in user_agent and "Chrome" not in user_agent:
            browser_name = "Safari"
        elif "Edg" in user_agent:
            browser_name = "Edge"
        
        # Create a fingerprint dictionary
        fingerprint = {
            "userAgent": user_agent,
            "webgl": webgl,
            "platform": os_name,
            "browser": browser_name,
            "timezone": random.choice(["America/New_York", "America/Los_Angeles", "America/Chicago", "Europe/London"]),
            "screenResolution": random.choice(["1920x1080", "2560x1440", "1366x768", "1440x900", "1680x1050"]),
            "hardwareConcurrency": random.choice([4, 8, 12, 16]),
            "deviceMemory": random.choice([4, 8, 16, 32]),
            "language": "en-US",
            "doNotTrack": random.choice([None, "1", "0"])
        }
        
        # Add platform-specific headers if available
        if self.platform in self.platform_data:
            fingerprint["headers"] = self.platform_data[self.platform]["headers"]
            fingerprint["cookies_to_preserve"] = self.platform_data[self.platform]["cookies_to_preserve"]
        
        return fingerprint
    
    async def apply_stealth_js(self, page) -> bool:
        """Apply stealth JavaScript patches to the page.
        
        Args:
            page: The browser page object.
            
        Returns:
            bool: Success status.
        """
        # Basic anti-detection scripts
        scripts = [
            # Hide webdriver
            """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false,
            });
            """,
            
            # Add plugins array
            """
            Object.defineProperty(navigator, 'plugins', {
                get: () => {
                    const plugins = [
                        { name: 'Chrome PDF Plugin', description: 'Portable Document Format', filename: 'internal-pdf-viewer' },
                        { name: 'Chrome PDF Viewer', description: '', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
                        { name: 'Native Client', description: '', filename: 'internal-nacl-plugin' }
                    ];
                    plugins.refresh = () => {};
                    plugins.item = (index) => plugins[index];
                    plugins.namedItem = (name) => plugins.find(p => p.name === name);
                    plugins.__proto__ = PluginArray.prototype;
                    return plugins;
                }
            });
            """,
            
            # Add language properties
            """
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
            """
        ]
        
        # Platform-specific scripts
        if self.platform == "yelp":
            scripts.extend([
                # Yelp-specific evasions
                """
                // Emulate Yelp-specific browser behavior
                if (window.location.hostname.includes('yelp.com')) {
                    // Override fetch to hide automation signals
                    const originalFetch = window.fetch;
                    window.fetch = function() {
                        return originalFetch.apply(this, arguments)
                            .then(response => {
                                return response;
                            })
                            .catch(error => {
                                if (error.toString().includes('captcha')) {
                                    console.error('Captcha detected');
                                }
                                throw error;
                            });
                    };
                    
                    // Add specific Yelp behavior patterns
                    if (!window.yelpStealthInitialized) {
                        window.yelpStealthInitialized = true;
                        // Custom event handlers that Yelp might check
                        const events = ['mousemove', 'mousedown', 'mouseup', 'click'];
                        events.forEach(event => {
                            document.addEventListener(event, function() {}, { passive: true });
                        });
                    }
                }
                """
            ])
        elif self.platform == "tripadvisor":
            scripts.extend([
                # TripAdvisor-specific evasions
                """
                // TripAdvisor specific overrides
                if (window.location.hostname.includes('tripadvisor')) {
                    // Simulate normal browser behaviors
                    if (!window.taStealthInitialized) {
                        window.taStealthInitialized = true;
                        // Mimic normal scrolling behavior
                        let lastScrollTime = Date.now();
                        window.addEventListener('scroll', function() {
                            lastScrollTime = Date.now();
                        }, { passive: true });
                    }
                }
                """
            ])
        
        # Apply all stealth scripts
        try:
            for script in scripts:
                script_hash = hash(script)
                if script_hash not in self.scripts_applied:
                    await page.evaluateOnNewDocument(script)
                    self.scripts_applied.add(script_hash)
                    
            logger.info(f"Applied stealth JavaScript for {self.platform} platform")
            return True
        
        except Exception as e:
            logger.error(f"Error applying stealth scripts: {e}")
            return False
    
    async def apply_fingerprint(self, page, fingerprint: Optional[Dict[str, Any]] = None) -> bool:
        """Apply a browser fingerprint to the page.
        
        Args:
            page: The browser page object.
            fingerprint (dict, optional): Fingerprint to apply. If None, generates a new one.
            
        Returns:
            bool: Success status.
        """
        if fingerprint is None:
            fingerprint = self.get_browser_fingerprint()
            
        try:
            # Set user agent
            await page.setUserAgent(fingerprint['userAgent'])
            
            # Set WebGL vendor and renderer
            await page.evaluateOnNewDocument(f"""
                // Override WebGL vendor and renderer
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {{
                    if (parameter === 37445) {{
                        return "{fingerprint['webgl']['vendor']}";
                    }}
                    if (parameter === 37446) {{
                        return "{fingerprint['webgl']['renderer']}";
                    }}
                    return getParameter.apply(this, arguments);
                }};
            """)
            
            # Set platform
            await page.evaluateOnNewDocument(f"""
                Object.defineProperty(navigator, 'platform', {{
                    get: () => '{fingerprint['platform']}'
                }});
                
                Object.defineProperty(navigator, 'hardwareConcurrency', {{
                    get: () => {fingerprint['hardwareConcurrency']}
                }});
                
                // Only set deviceMemory if supported
                if ('deviceMemory' in navigator) {{
                    Object.defineProperty(navigator, 'deviceMemory', {{
                        get: () => {fingerprint['deviceMemory']}
                    }});
                }}
            """)
            
            # Set custom headers if available
            if "headers" in fingerprint:
                await page.setExtraHTTPHeaders(fingerprint["headers"])
            
            logger.info(f"Applied {fingerprint['browser']} on {fingerprint['platform']} fingerprint")
            return True
            
        except Exception as e:
            logger.error(f"Error applying fingerprint: {e}")
            return False
    
    async def simulate_human_behavior(self, page) -> bool:
        """Simulate human-like behavior on the page.
        
        Args:
            page: The browser page object.
            
        Returns:
            bool: Success status.
        """
        try:
            # Simulate random mouse movements
            await page.evaluate("""
                function simulateMouseMovement() {
                    const events = [];
                    const numMovements = Math.floor(Math.random() * 10) + 5;
                    
                    for (let i = 0; i < numMovements; i++) {
                        const x = Math.floor(Math.random() * window.innerWidth);
                        const y = Math.floor(Math.random() * window.innerHeight);
                        
                        const event = new MouseEvent('mousemove', {
                            view: window,
                            bubbles: true,
                            cancelable: true,
                            clientX: x,
                            clientY: y
                        });
                        
                        document.dispatchEvent(event);
                        events.push({ x, y, time: Date.now() });
                    }
                    
                    return events;
                }
                
                return simulateMouseMovement();
            """)
            
            # Random scrolling behavior
            await page.evaluate("""
                function simulateScrolling() {
                    const maxScrolls = Math.floor(Math.random() * 4) + 2;
                    const scrollEvents = [];
                    
                    for (let i = 0; i < maxScrolls; i++) {
                        const scrollAmount = Math.floor(Math.random() * 300) + 100;
                        window.scrollBy(0, scrollAmount);
                        scrollEvents.push({ amount: scrollAmount, time: Date.now() });
                    }
                    
                    return scrollEvents;
                }
                
                return simulateScrolling();
            """)
            
            # Random interactions with non-essential elements
            if random.random() < 0.3:  # 30% chance
                try:
                    # Find and interact with a random link or button that won't navigate away
                    await page.evaluate("""
                        function interactWithRandomElement() {
                            // Get all links and buttons
                            const elements = Array.from(document.querySelectorAll('a, button'));
                            
                            // Filter out elements that would navigate away or submit forms
                            const safeElements = elements.filter(el => {
                                if (el.tagName === 'A') {
                                    const href = el.getAttribute('href');
                                    return href === '#' || href === 'javascript:void(0)' || href === '' || href === null;
                                }
                                if (el.tagName === 'BUTTON') {
                                    const type = el.getAttribute('type');
                                    return type !== 'submit';
                                }
                                return true;
                            });
                            
                            if (safeElements.length > 0) {
                                // Pick a random element
                                const randomIndex = Math.floor(Math.random() * safeElements.length);
                                const element = safeElements[randomIndex];
                                
                                // Hover on the element
                                const hoverEvent = new MouseEvent('mouseover', {
                                    view: window,
                                    bubbles: true,
                                    cancelable: true
                                });
                                element.dispatchEvent(hoverEvent);
                                
                                // Sometimes click on it
                                if (Math.random() < 0.5) {
                                    const clickEvent = new MouseEvent('click', {
                                        view: window,
                                        bubbles: true,
                                        cancelable: true
                                    });
                                    element.dispatchEvent(clickEvent);
                                }
                                
                                return { interacted: true, element: element.outerHTML };
                            }
                            
                            return { interacted: false };
                        }
                        
                        return interactWithRandomElement();
                    """)
                except Exception as e:
                    logger.debug(f"Error during random element interaction: {e}")
            
            logger.info("Simulated human-like behavior on the page")
            return True
            
        except Exception as e:
            logger.error(f"Error simulating human behavior: {e}")
            return False
    
    async def detect_and_handle_captcha(self, page) -> bool:
        """Detect and handle CAPTCHAs if they appear.
        
        Args:
            page: The browser page object.
            
        Returns:
            bool: True if CAPTCHA was handled, False if not detected or couldn't be handled.
        """
        try:
            # Common CAPTCHA element selectors
            captcha_selectors = [
                'iframe[src*="captcha"]',
                'iframe[src*="recaptcha"]',
                'iframe[title*="recaptcha"]',
                'div.g-recaptcha',
                'div[class*="captcha"]',
                'div[id*="captcha"]',
                'input[captcha]',
                'img[alt*="captcha" i]'
            ]
            
            # Check if any CAPTCHA elements are present
            captcha_detected = await page.evaluate(f"""
                function detectCaptcha() {{
                    const selectors = {json.dumps(captcha_selectors)};
                    for (const selector of selectors) {{
                        if (document.querySelector(selector)) {{
                            return {{ detected: true, selector: selector }};
                        }}
                    }}
                    return {{ detected: false }};
                }}
                
                return detectCaptcha();
            """)
            
            if captcha_detected.get('detected', False):
                logger.warning(f"CAPTCHA detected on page using selector: {captcha_detected.get('selector')}")
                
                # For now, just log the detection
                # In a production environment, you would implement CAPTCHA solving logic here
                # or use Browserbase's built-in CAPTCHA solving capabilities
                
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error detecting CAPTCHA: {e}")
            return False
    
    async def enhance_browser(self, page):
        """Apply all stealth enhancements to a browser page.
        
        Args:
            page: The browser page object.
            
        Returns:
            bool: Success status.
        """
        try:
            # Get a fingerprint
            fingerprint = self.get_browser_fingerprint()
            
            # Apply stealth JavaScript
            await self.apply_stealth_js(page)
            
            # Apply fingerprint
            await self.apply_fingerprint(page, fingerprint)
            
            # Apply platform-specific handling
            if self.platform == "yelp":
                await self._enhance_for_yelp(page)
            elif self.platform == "tripadvisor":
                await self._enhance_for_tripadvisor(page)
                
            logger.info(f"Successfully applied all stealth enhancements for {self.platform}")
            return True
            
        except Exception as e:
            logger.error(f"Error enhancing browser stealth: {e}")
            return False
    
    async def _enhance_for_yelp(self, page):
        """Apply Yelp-specific enhancements.
        
        Args:
            page: The browser page object.
        """
        # Additional Yelp-specific JavaScript patches
        await page.evaluateOnNewDocument("""
            // Yelp-specific fixes
            
            // Fix for Yelp's device fingerprinting
            if (typeof CanvasRenderingContext2D !== 'undefined') {
                const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
                CanvasRenderingContext2D.prototype.getImageData = function (x, y, w, h) {
                    const imageData = originalGetImageData.call(this, x, y, w, h);
                    
                    // Add subtle "noise" to the image data to make fingerprinting harder
                    if (Math.random() < 0.1) {  // Only modify 10% of calls to avoid breaking functionality
                        for (let i = 0; i < imageData.data.length; i += 4) {
                            // Add very small random variations to RGB values
                            imageData.data[i] = Math.max(0, Math.min(255, imageData.data[i] + (Math.random() < 0.1 ? 1 : 0)));
                            imageData.data[i+1] = Math.max(0, Math.min(255, imageData.data[i+1] + (Math.random() < 0.1 ? 1 : 0)));
                            imageData.data[i+2] = Math.max(0, Math.min(255, imageData.data[i+2] + (Math.random() < 0.1 ? 1 : 0)));
                        }
                    }
                    
                    return imageData;
                };
            }
            
            // Override navigator properties Yelp checks
            const navigatorProps = {
                vendor: 'Google Inc.',
                maxTouchPoints: Math.floor(Math.random() * 5),
                hardwareConcurrency: 8,
                deviceMemory: 8,
                appVersion: '5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                userActivation: { hasBeenActive: true, isActive: true }
            };
            
            for (const [prop, value] of Object.entries(navigatorProps)) {
                if (prop in navigator) {
                    try {
                        Object.defineProperty(navigator, prop, { get: () => value });
                    } catch (e) {
                        // Some properties might not be configurable
                    }
                }
            }
        """)
        
        # Additional cookie handling
        await page.evaluate("""
            // Ensure cookies needed for Yelp are preserved
            function preserveYelpCookies() {
                if (document.cookie) {
                    try {
                        // Make sure important cookies persist longer
                        const importantCookies = ['__ycab', 'bse', '_ga', '_gid'];
                        const allCookies = document.cookie.split(';');
                        
                        for (const cookie of allCookies) {
                            const [name] = cookie.trim().split('=');
                            if (importantCookies.includes(name)) {
                                // Extend expiration date
                                const extendedDate = new Date();
                                extendedDate.setTime(extendedDate.getTime() + (7 * 24 * 60 * 60 * 1000)); // 7 days
                                document.cookie = `${name}=${document.cookie[name]}; expires=${extendedDate.toUTCString()}; path=/`;
                            }
                        }
                    } catch (e) {
                        console.error('Error preserving cookies:', e);
                    }
                }
            }
            
            // Run immediately and set interval to check regularly
            preserveYelpCookies();
            setInterval(preserveYelpCookies, 300000); // Check every 5 minutes
        """)
        
        logger.info("Applied Yelp-specific stealth enhancements")
    
    async def _enhance_for_tripadvisor(self, page):
        """Apply TripAdvisor-specific enhancements.
        
        Args:
            page: The browser page object.
        """
        # TripAdvisor-specific enhancements
        await page.evaluateOnNewDocument("""
            // TripAdvisor-specific fixes
            
            // Handle consent dialog automatically
            function handleTripAdvisorConsent() {
                const consentButtons = [
                    'button[id*="accept"]',
                    'button[data-test-target*="accept"]',
                    'button.evidon-banner-acceptbutton',
                    'button:has-text("Accept All")',
                    'button:has-text("Accept Cookies")'
                ];
                
                for (const selector of consentButtons) {
                    const button = document.querySelector(selector);
                    if (button) {
                        console.log('Clicking consent button:', selector);
                        button.click();
                        return true;
                    }
                }
                
                return false;
            }
            
            // Override specific TripAdvisor detection methods
            if (typeof navigator.sendBeacon === 'function') {
                const originalSendBeacon = navigator.sendBeacon;
                navigator.sendBeacon = function(url, data) {
                    // Allow normal beacon behavior but be selective about parameters
                    if (url.includes('eat.js') || url.includes('bat.js') || url.includes('analytics')) {
                        // Either block these analytics beacons or modify them
                        if (Math.random() < 0.5) {  // 50% chance to let them through
                            return originalSendBeacon.apply(this, arguments);
                        }
                        return true; // Pretend we sent it
                    }
                    
                    return originalSendBeacon.apply(this, arguments);
                };
            }
            
            // Set interval to check for the consent dialog regularly
            setInterval(handleTripAdvisorConsent, 2000);
        """)
        
        logger.info("Applied TripAdvisor-specific stealth enhancements")


async def apply_stealth_measures(page, platform):
    """Apply all stealth measures to a page.
    
    Args:
        page: Browser page object.
        platform (str): Target platform name.
        
    Returns:
        bool: Success status.
    """
    enhancer = StealthEnhancer(platform)
    
    try:
        # Apply all stealth enhancements
        success = await enhancer.enhance_browser(page)
        
        # Simulate human behavior
        if success:
            await enhancer.simulate_human_behavior(page)
            
        # Check for CAPTCHAs
        await enhancer.detect_and_handle_captcha(page)
        
        return success
    except Exception as e:
        logger.error(f"Error applying stealth measures: {e}")
        return False
