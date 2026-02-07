"""Google Maps Scraper Engine - Enterprise Enhanced Version"""

import asyncio
import random
import re
from urllib.parse import quote, urlparse
from typing import Callable, Optional, Dict, List, Set
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from config import *

# Enhanced Regex patterns
EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
PHONE_REGEX = r'(\+?[\d\s\-()]{8,})'
SA_PHONE_REGEX = r'(?:\+?966|0)?[\s-]?(?:5\d{8}|1[1-9]\d{7})'  # Saudi phone format

class GoogleMapsScraper:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.playwright = None
        self.is_running = False
        self.seen_ids: Set[str] = set()
        self.seen_phones: Set[str] = set()  # Track seen phone numbers for deduplication
        self.seen_names: Set[str] = set()   # Track seen business names
        self.results: List[Dict] = []
        
        # Concurrency control
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT_PAGES)
        
        # Rate limiting
        self.request_count = 0
        self.last_request_time = None
        
        # Callbacks for UI updates
        self.on_status_update: Optional[Callable] = None
        self.on_data_found: Optional[Callable] = None
        self.on_complete: Optional[Callable] = None
        
    async def initialize(self):
        """Initialize the browser with enhanced stealth settings"""
        self.playwright = await async_playwright().start()
        
        # Enhanced browser launch options
        self.browser = await self.playwright.chromium.launch(
            headless=HEADLESS,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
            ]
        )
        
        # Enhanced context with better anti-detection
        self.context = await self.browser.new_context(
            viewport={'width': VIEWPORT_WIDTH, 'height': VIEWPORT_HEIGHT},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='Asia/Riyadh',
            geolocation={'latitude': 24.7136, 'longitude': 46.6753},  # Riyadh default
            permissions=['geolocation'],
        )
        
        # Enhanced stealth scripts
        await self.context.add_init_script("""
            // Hide webdriver
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            
            // Override plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en', 'ar']
            });
            
            // Override platform
            Object.defineProperty(navigator, 'platform', {
                get: () => 'Win32'
            });
            
            // Mock chrome object
            window.chrome = { runtime: {} };
            
            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)
        
    async def close(self):
        """Close the browser gracefully"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception:
            pass
            
    def _emit_status(self, message: str):
        """Emit status update to UI"""
        if self.on_status_update:
            self.on_status_update(message)
            
    def _emit_data(self, data: Dict):
        """Emit new data to UI"""
        if self.on_data_found:
            self.on_data_found(data)
            
    def _extract_place_id(self, url: str) -> Optional[str]:
        """Extract unique place ID from Google Maps URL"""
        # Try CID format
        cid_match = re.search(r'!1s(0x[a-f0-9:]+)', url)
        if cid_match:
            return cid_match.group(1)
        
        # Try place_id format
        place_match = re.search(r'place_id:([A-Za-z0-9_-]+)', url)
        if place_match:
            return place_match.group(1)
        
        # Try data format
        data_match = re.search(r'/data=!3m1!4b1!4m[^/]+!3m[^/]+!1s([^!]+)', url)
        if data_match:
            return data_match.group(1)
            
        return url
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number for comparison"""
        if not phone:
            return ""
        # Remove all non-digit characters except +
        normalized = re.sub(r'[^\d+]', '', phone)
        # Remove leading zeros after country code
        if normalized.startswith('+966'):
            normalized = '+966' + normalized[4:].lstrip('0')
        elif normalized.startswith('966'):
            normalized = '966' + normalized[3:].lstrip('0')
        elif normalized.startswith('0'):
            normalized = normalized.lstrip('0')
        return normalized
    
    def _is_duplicate(self, data: Dict) -> bool:
        """Check if this business is a duplicate"""
        # Check by phone
        phone = self._normalize_phone(data.get('phone', ''))
        if phone and len(phone) >= 8:
            if phone in self.seen_phones:
                return True
            self.seen_phones.add(phone)
        
        # Check by name (normalized)
        name = data.get('name', '').strip().lower()
        if name and len(name) > 3:
            # Create a simplified version for comparison
            simplified_name = re.sub(r'[^\w\s]', '', name)
            if simplified_name in self.seen_names:
                return True
            self.seen_names.add(simplified_name)
        
        return False
        
    async def _handle_cookie_consent(self, page: Page):
        """Handle the cookie consent popup"""
        try:
            accept_button = page.locator('button:has-text("Accept all"), button:has-text("قبول الكل"), button:has-text("Accept"), button:has-text("موافق")')
            if await accept_button.count() > 0:
                await accept_button.first.click(timeout=3000)
                await asyncio.sleep(0.5)
        except Exception:
            pass

    async def _extract_emails_from_text(self, text: str) -> Set[str]:
        """Extract unique valid emails from text"""
        emails = set()
        found = re.findall(EMAIL_REGEX, text.lower())
        
        # Filter out common false positives
        excluded_domains = ['example.com', 'test.com', 'domain.com', 'email.com', 
                          'yoursite.com', 'website.com', 'sample.com', 'placeholder.com']
        excluded_patterns = ['noreply@', 'no-reply@', 'donotreply@', 'mailer-daemon@']
        
        for email in found:
            # Skip excluded domains
            domain = email.split('@')[1] if '@' in email else ''
            if domain in excluded_domains:
                continue
            # Skip common system emails
            if any(pattern in email for pattern in excluded_patterns):
                continue
            # Skip very short local parts
            local_part = email.split('@')[0] if '@' in email else ''
            if len(local_part) < 2:
                continue
            emails.add(email)
            
        return emails

    async def _extract_phones_from_text(self, text: str) -> Set[str]:
        """Extract phone numbers from text with Saudi format preference"""
        phones = set()
        
        # Try Saudi phone format first
        sa_phones = re.findall(SA_PHONE_REGEX, text)
        for phone in sa_phones:
            cleaned = self._normalize_phone(phone)
            if len(cleaned) >= 9:
                phones.add(cleaned)
        
        return phones

    async def _visit_website_for_contacts(self, website_url: str) -> Dict[str, any]:
        """Visit the business website to find emails and social links - Enhanced version"""
        emails = set()
        socials = []
        extra_phones = set()
        
        if not website_url or website_url == 'N/A':
            return {'emails': [], 'socials': [], 'phones': []}

        page = None
        try:
            page = await self.context.new_page()
            
            # Set shorter timeout for external websites
            page.set_default_timeout(8000)
            
            # Navigate with domcontentloaded for speed
            await page.goto(website_url, wait_until='domcontentloaded', timeout=10000)
            
            # Get page content
            content = await page.content()
            
            # Extract emails
            emails.update(await self._extract_emails_from_text(content))
            
            # Extract additional phones from website
            extra_phones.update(await self._extract_phones_from_text(content))
            
            # If no email found on homepage, check contact/about pages
            if not emails:
                contact_selectors = [
                    'a[href*="contact"]',
                    'a[href*="about"]',
                    'a[href*="اتصل"]',
                    'a[href*="تواصل"]',
                    'a:has-text("Contact")',
                    'a:has-text("اتصل بنا")',
                ]
                
                for selector in contact_selectors:
                    try:
                        links = await page.locator(selector).all()
                        for link in links[:1]:  # Check only first match
                            href = await link.get_attribute('href')
                            if href:
                                full_url = href if href.startswith('http') else website_url.rstrip('/') + '/' + href.lstrip('/')
                                await page.goto(full_url, wait_until='domcontentloaded', timeout=6000)
                                content = await page.content()
                                emails.update(await self._extract_emails_from_text(content))
                                extra_phones.update(await self._extract_phones_from_text(content))
                                if emails:
                                    break
                    except Exception:
                        continue
                    if emails:
                        break

            # Social media detection - Enhanced
            social_patterns = {
                'facebook': r'facebook\.com/[^"\s<>]+',
                'instagram': r'instagram\.com/[^"\s<>]+',
                'twitter': r'(?:twitter\.com|x\.com)/[^"\s<>]+',
                'linkedin': r'linkedin\.com/[^"\s<>]+',
                'tiktok': r'tiktok\.com/@[^"\s<>]+',
                'youtube': r'youtube\.com/[^"\s<>]+',
                'snapchat': r'snapchat\.com/add/[^"\s<>]+',
            }
            
            for platform, pattern in social_patterns.items():
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches[:1]:  # Take first match per platform
                    clean_url = f"https://{match}"
                    if clean_url not in socials:
                        socials.append(clean_url)

        except Exception as e:
            # Website might be down, blocking, or timing out - this is expected
            pass
        finally:
            if page:
                try:
                    await page.close()
                except:
                    pass
                
        return {
            'emails': list(emails),
            'socials': socials,
            'phones': list(extra_phones)
        }

    async def _process_place(self, url: str) -> Optional[Dict]:
        """Process a single place URL - Enhanced with better extraction"""
        if not self.is_running:
            return None

        async with self.semaphore:
            page = None
            try:
                page = await self.context.new_page()
                
                # Navigate to the place
                full_url = f"https://www.google.com{url}" if url.startswith('/') else url
                await page.goto(full_url, wait_until='domcontentloaded', timeout=25000)
                
                # Smart delay based on request count
                delay = random.uniform(CLICK_DELAY_MIN, CLICK_DELAY_MAX)
                if self.request_count > 50:
                    delay *= 1.3  # Slow down after many requests
                await asyncio.sleep(delay)
                self.request_count += 1
                
                # Extract Data with multiple fallback selectors
                
                # Name - Multiple selectors
                name = "N/A"
                name_selectors = ['h1', 'h1.DUwDvf', '[data-attrid="title"]']
                for selector in name_selectors:
                    try:
                        elem = page.locator(selector).first
                        if await elem.count() > 0:
                            name = await elem.inner_text(timeout=2000)
                            name = name.strip()
                            if name:
                                break
                    except:
                        continue
                
                # Phone - Multiple methods
                phone = "N/A"
                phone_selectors = [
                    'button[data-item-id*="phone"]',
                    'a[href^="tel:"]',
                    '[data-tooltip*="phone"]',
                ]
                for selector in phone_selectors:
                    try:
                        elem = page.locator(selector).first
                        if await elem.count() > 0:
                            if selector.startswith('a[href'):
                                phone = await elem.get_attribute('href', timeout=2000)
                                phone = phone.replace('tel:', '').strip()
                            else:
                                phone = await elem.inner_text(timeout=2000)
                            phone = re.sub(r'[^\d+\s()-]', '', phone).strip()
                            if phone and len(phone) >= 8:
                                break
                    except:
                        continue
                
                # Address - Multiple selectors
                address = "N/A"
                address_selectors = [
                    'button[data-item-id*="address"]',
                    '[data-item-id*="address"]',
                    '.Io6YTe',
                ]
                for selector in address_selectors:
                    try:
                        elem = page.locator(selector).first
                        if await elem.count() > 0:
                            address = await elem.inner_text(timeout=2000)
                            address = address.strip()
                            if address:
                                break
                    except:
                        continue
                
                # Website
                website = None
                try:
                    website_elem = page.locator('a[data-item-id="authority"]').first
                    if await website_elem.count() > 0:
                        website = await website_elem.get_attribute('href', timeout=2000)
                except:
                    pass
                
                # Coordinates from URL
                coords_match = re.search(r'@(-?\d+\.?\d*),(-?\d+\.?\d*)', page.url)
                latitude = coords_match.group(1) if coords_match else None
                longitude = coords_match.group(2) if coords_match else None
                
                # Rating and reviews (bonus data)
                rating = None
                review_count = None
                try:
                    rating_elem = page.locator('span.ceNzKf, div.F7nice span').first
                    if await rating_elem.count() > 0:
                        rating_text = await rating_elem.get_attribute('aria-label', timeout=1000)
                        if rating_text:
                            rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                            if rating_match:
                                rating = rating_match.group(1)
                except:
                    pass
                
                # Enhanced Data: Visit website for emails
                emails = []
                socials = []
                website_phones = []
                
                if website:
                    web_data = await self._visit_website_for_contacts(website)
                    emails = web_data['emails']
                    socials = web_data['socials']
                    website_phones = web_data['phones']

                details = {
                    'name': name,
                    'phone': phone,
                    'address': address,
                    'website': website or 'N/A',
                    'emails': ", ".join(emails) if emails else 'N/A',
                    'socials': ", ".join(socials[:3]) if socials else 'N/A',  # Limit to 3 socials
                    'latitude': latitude,
                    'longitude': longitude,
                    'rating': rating,
                    'url': page.url
                }
                
                # Check for duplicates before returning
                if self._is_duplicate(details):
                    return None
                
                return details

            except Exception as e:
                # Don't spam the log with every error
                pass
            finally:
                if page:
                    try:
                        await page.close()
                    except:
                        pass
        
        return None

    async def _scroll_results(self, page: Page) -> List[str]:
        """Scroll through results and collect all place URLs - Enhanced with debugging"""
        self._emit_status("Scanning results list...")
        
        # Try multiple selectors for results container
        container_selectors = [
            'div[role="feed"]',
            'div[role="main"] div.m6QErb',
            'div.m6QErb.DxyBCb',
            'div.m6QErb',
            'div[aria-label*="Results"]',
            'div.Nv2PK',
        ]
        
        scrollable_div = None
        used_selector = None
        
        for selector in container_selectors:
            try:
                self._emit_status(f"Trying selector: {selector[:30]}...")
                await page.wait_for_selector(selector, timeout=5000)
                elem = page.locator(selector).first
                if await elem.count() > 0:
                    scrollable_div = elem
                    used_selector = selector
                    self._emit_status(f"Found container with: {selector[:30]}")
                    break
            except Exception:
                continue
        
        if not scrollable_div:
            self._emit_status("Could not find results container - trying page scroll")
            # Try scrolling the whole page as fallback
            scrollable_div = page.locator('body').first
            used_selector = "body"
        
        place_urls = set()
        last_height = 0
        no_change_count = 0
        scroll_count = 0
        
        # Link selectors to try
        link_selectors = [
            'a[href*="/maps/place/"]',
            'a.hfpxzc',
            'div.Nv2PK a',
            'a[data-value]',
        ]
        
        while self.is_running:
            scroll_count += 1
            
            # Smooth scroll with random variation
            scroll_amount = random.randint(300, 600)
            try:
                await scrollable_div.evaluate(f'el => el.scrollBy(0, {scroll_amount})')
            except:
                # Fallback to page scroll
                await page.evaluate(f'window.scrollBy(0, {scroll_amount})')
            
            # Variable delay
            await asyncio.sleep(random.uniform(SCROLL_PAUSE_MIN, SCROLL_PAUSE_MAX))
            
            # Check scroll height
            try:
                current_height = await scrollable_div.evaluate('el => el.scrollHeight')
            except:
                current_height = await page.evaluate('document.body.scrollHeight')
            
            if current_height == last_height:
                no_change_count += 1
                if no_change_count >= MAX_SCROLL_ATTEMPTS:
                    self._emit_status("Reached end of results")
                    break
            else:
                no_change_count = 0
            last_height = current_height
            
            # Try multiple link selectors
            for link_selector in link_selectors:
                try:
                    links = await page.locator(link_selector).all()
                    for link in links:
                        try:
                            href = await link.get_attribute('href')
                            if href and '/maps/place/' in href:
                                place_urls.add(href)
                        except:
                            continue
                    if place_urls:
                        break  # Found links with this selector
                except:
                    continue

            # Status update every few scrolls
            if scroll_count % 3 == 0:
                self._emit_status(f"Found {len(place_urls)} locations (scroll #{scroll_count})...")
            
            # Debug: Log if no results found after several scrolls
            if scroll_count == 5 and len(place_urls) == 0:
                self._emit_status("Warning: No results detected yet...")
            
            # Check for end markers
            end_markers = [
                'text=/You\'ve reached the end/i',
                'text=/No more results/i',
                'text=/النهاية/i',
                'text=/لقد وصلت إلى نهاية القائمة/i',
            ]
            for marker in end_markers:
                try:
                    if await page.locator(marker).count() > 0:
                        self._emit_status("Completed scanning all results")
                        return list(place_urls)
                except:
                    continue
                    
            # Safety limit
            if len(place_urls) >= MAX_RESULTS:
                self._emit_status(f"Reached maximum limit: {MAX_RESULTS}")
                break
                    
        return list(place_urls)

    async def search(self, business_tag: str, region: str, city: str, district: str = ""):
        """Main search function - Enhanced with better query building"""
        if not self.browser:
            await self.initialize()
            
        self.is_running = True
        self.results.clear()
        self.seen_ids.clear()
        self.seen_phones.clear()
        self.seen_names.clear()
        self.request_count = 0
        
        page = await self.context.new_page()
        
        try:
            # Build optimized search query
            if district and district.strip():
                # More specific search when district is provided
                query = f"{business_tag} {district} {city}"
                self._emit_status(f"Targeting: {district}, {city}")
            else:
                query = f"{business_tag} in {city}, {region}"
                self._emit_status(f"Searching: {city}, {region}")
            
            # Navigate to Maps with English locale for consistent parsing
            maps_url = f"https://www.google.com/maps/search/{quote(query)}?hl=en"
            self._emit_status(f"Opening Google Maps...")
            self._emit_status(f"Query: {query}")
            
            # IMPORTANT: Use 'domcontentloaded' instead of 'networkidle' because 
            # Google Maps continuously sends network requests and will never reach 'networkidle'
            await page.goto(maps_url, wait_until='domcontentloaded', timeout=30000)
            self._emit_status(f"Page loaded successfully")
            
            await self._handle_cookie_consent(page)
            
            # Wait for results panel to appear
            self._emit_status(f"Waiting for results to load...")
            try:
                # Wait for results container to be visible
                await page.wait_for_selector('div.m6QErb, div[role="feed"], div.Nv2PK', timeout=15000)
                self._emit_status(f"Results panel detected")
            except Exception as e:
                self._emit_status(f"Warning: Results panel not found, continuing anyway...")
            
            # Additional wait for dynamic content
            await asyncio.sleep(3)
            
            # Debug: Show current URL
            try:
                current_url = page.url
                self._emit_status(f"Current URL: {current_url[:50]}...")
            except:
                pass
            
            # Collect all URLs first
            place_urls = await self._scroll_results(page)
            
            if not place_urls:
                self._emit_status("No results found for this search")
                if self.on_complete: 
                    self.on_complete()
                return
            
            self._emit_status(f"Processing {len(place_urls)} locations...")
            await page.close()
            
            # Process in parallel with progress tracking
            tasks = []
            for url in place_urls:
                if not self.is_running:
                    break
                
                # Deduplicate by place ID
                place_id = self._extract_place_id(url)
                if place_id in self.seen_ids:
                    continue
                self.seen_ids.add(place_id)
                
                task = asyncio.create_task(self._process_place(url))
                tasks.append(task)
            
            # Process with progress updates
            completed = 0
            total = len(tasks)
            successful = 0
            
            for task in asyncio.as_completed(tasks):
                if not self.is_running:
                    break
                
                try:
                    result = await task
                    completed += 1
                    
                    # Progress update every 5 items
                    if completed % 5 == 0 or completed == total:
                        self._emit_status(f"Progress: {completed}/{total} ({successful} extracted)")
                    
                    if result:
                        successful += 1
                        self.results.append(result)
                        self._emit_data(result)
                        
                except Exception:
                    completed += 1
                    continue
            
            self._emit_status(f"Complete! Extracted {len(self.results)} unique businesses")

        except Exception as e:
            self._emit_status(f"Search error: {str(e)[:50]}")
        finally:
            if self.on_complete:
                self.on_complete()
            
    def stop(self):
        """Stop the scraping process"""
        self.is_running = False
        self._emit_status("Stopping extraction...")
