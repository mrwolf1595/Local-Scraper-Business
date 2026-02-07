"""Google Maps Scraper Engine - Enhanced Version"""

import asyncio
import random
import re
from urllib.parse import quote, urlparse
from typing import Callable, Optional, Dict, List, Set
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from config import *

# Regex patterns
EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
PHONE_REGEX = r'(\+?[\d\s-]{8,})'  # Simple phone regex, can be improved

class GoogleMapsScraper:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.playwright = None
        self.is_running = False
        self.seen_ids = set()
        self.results = []
        
        # Concurrency control
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT_PAGES)
        
        # Callbacks for UI updates
        self.on_status_update: Optional[Callable] = None
        self.on_data_found: Optional[Callable] = None
        self.on_complete: Optional[Callable] = None
        
    async def initialize(self):
        """Initialize the browser"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=HEADLESS,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        # Create context with anti-detection measures
        self.context = await self.browser.new_context(
            viewport={'width': VIEWPORT_WIDTH, 'height': VIEWPORT_HEIGHT},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US'
        )
        
        # Stealth mode: hide webdriver
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
    async def close(self):
        """Close the browser"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
            
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
        cid_match = re.search(r'!1s(0x[a-f0-9:]+)', url)
        if cid_match:
            return cid_match.group(1)
        place_match = re.search(r'place_id:([A-Za-z0-9_-]+)', url)
        if place_match:
            return place_match.group(1)
        return url
        
    async def _handle_cookie_consent(self, page: Page):
        """Handle the cookie consent popup"""
        try:
            accept_button = page.locator('button:has-text("Accept all"), button:has-text("قبول الكل")')
            if await accept_button.count() > 0:
                await accept_button.click(timeout=3000)
                await asyncio.sleep(0.5)
        except Exception:
            pass

    async def _extract_emails_from_text(self, text: str) -> Set[str]:
        """Extract unique emails from text"""
        return set(re.findall(EMAIL_REGEX, text))

    async def _visit_website_for_contacts(self, website_url: str) -> Dict[str, any]:
        """Visit the business website to find emails and social links"""
        emails = set()
        socials = []
        
        if not website_url:
            return {'emails': [], 'socials': []}

        page = None
        try:
            # Open a new page for website extraction
            page = await self.context.new_page()
            
            # Quick timeout for websites - we don't want to hang too long
            await page.goto(website_url, wait_until='domcontentloaded', timeout=10000)
            
            content = await page.content()
            emails.update(await self._extract_emails_from_text(content))
            
            # Check for "Contact" or "About" pages if no email found on home
            if not emails:
                contact_links = await page.locator('a[href*="contact"], a[href*="about"]').all()
                for link in contact_links[:2]: # Check max 2 links
                    try:
                        href = await link.get_attribute('href')
                        if href:
                            # Construct full URL if relative
                            full_contact_url = href if href.startswith('http') else website_url.rstrip('/') + '/' + href.lstrip('/')
                            await page.goto(full_contact_url, wait_until='domcontentloaded', timeout=8000)
                            content = await page.content()
                            emails.update(await self._extract_emails_from_text(content))
                    except Exception:
                        continue

            # Social media detection (basic)
            social_domains = ['facebook.com', 'instagram.com', 'twitter.com', 'linkedin.com', 'tiktok.com']
            for domain in social_domains:
                if domain in content:
                    # Try to find the exact link
                     links = await page.locator(f'a[href*="{domain}"]').all()
                     for link in links:
                         href = await link.get_attribute('href')
                         if href and href not in socials:
                             socials.append(href)

        except Exception as e:
            # Website might be down or blocking
            pass
        finally:
            if page:
                await page.close()
                
        return {
            'emails': list(emails),
            'socials': socials
        }

    async def _process_place(self, url: str) -> Optional[Dict]:
        """Process a single place URL (Extract Details + Website Data)"""
        if not self.is_running:
            return None

        async with self.semaphore:  # Limit concurrency
            page = None
            try:
                page = await self.context.new_page()
                
                # Navigate to the place
                full_url = f"https://www.google.com{url}" if url.startswith('/') else url
                await page.goto(full_url, wait_until='domcontentloaded', timeout=20000)
                
                # Random short delay
                await asyncio.sleep(random.uniform(CLICK_DELAY_MIN, CLICK_DELAY_MAX))
                
                # Extract Data
                
                # Name
                name = "N/A"
                try:
                    name_elem = page.locator('h1').first
                    name = await name_elem.inner_text(timeout=2000)
                except: pass
                
                # Phone
                phone = "N/A"
                try:
                     phone_elem = page.locator('button[data-item-id*="phone"]').first
                     phone_text = await phone_elem.inner_text(timeout=2000)
                     phone = re.sub(r'[^\d+\s()-]', '', phone_text)
                except: pass
                
                # Address
                address = "N/A"
                try:
                    address_elem = page.locator('button[data-item-id*="address"]').first
                    address = await address_elem.inner_text(timeout=2000)
                except: pass
                
                # Website
                website = None
                try:
                    website_elem = page.locator('a[data-item-id="authority"]').first
                    website = await website_elem.get_attribute('href', timeout=2000)
                except: pass
                
                # Coordinates
                coords_match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', page.url)
                latitude = coords_match.group(1) if coords_match else None
                longitude = coords_match.group(2) if coords_match else None
                
                # Enhanced Data: Visit website for emails
                emails = []
                socials = []
                if website:
                     web_data = await self._visit_website_for_contacts(website)
                     emails = web_data['emails']
                     socials = web_data['socials']

                details = {
                    'name': name,
                    'phone': phone,
                    'address': address,
                    'website': website or 'N/A',
                    'emails': ", ".join(emails) if emails else 'N/A',
                    'socials': ", ".join(socials) if socials else 'N/A',
                    'latitude': latitude,
                    'longitude': longitude,
                    'url': page.url
                }
                
                return details

            except Exception as e:
                self._emit_status(f"Error processing {url}: {str(e)}")
                return None
            finally:
                if page:
                    await page.close()

    async def _scroll_results(self, page: Page) -> List[str]:
        """Scroll through results and collect all place URLs"""
        self._emit_status("Scrolling through results...")
        
        try:
            await page.wait_for_selector('div[role="feed"]', timeout=10000)
            scrollable_div = page.locator('div[role="feed"]').first
        except Exception as e:
            self._emit_status(f"Could not find results list: {str(e)}")
            return []
        
        place_urls = set()
        last_height = 0
        no_change_count = 0
        
        while self.is_running:
            # Scroll
            await scrollable_div.evaluate('el => el.scrollTo(0, el.scrollHeight)')
            await asyncio.sleep(random.uniform(SCROLL_PAUSE_MIN, SCROLL_PAUSE_MAX))
            
            # Check height
            current_height = await scrollable_div.evaluate('el => el.scrollHeight')
            if current_height == last_height:
                no_change_count += 1
                if no_change_count >= MAX_SCROLL_ATTEMPTS:
                    break
            else:
                no_change_count = 0
            last_height = current_height
            
            # Collect links dynamically to show progress
            links = await page.locator('a[href*="/maps/place/"]').all()
            for link in links:
                href = await link.get_attribute('href')
                if href:
                     # Remove specific query params to deduplicate better
                     # clean_href = href.split('?')[0] 
                     # Google maps URLs are complex, standard href is usually fine for uniqueness check initially
                     place_urls.add(href)

            self._emit_status(f"Found {len(place_urls)} places so far...")
            
            # Check for end
            if await page.locator('text=/You\'ve reached the end|النهاية/i').count() > 0:
                self._emit_status("Reached end of results list")
                break
                
        return list(place_urls)

    async def search(self, business_tag: str, region: str, city: str, district: str = ""):
        """Main search function"""
        if not self.browser:
            await self.initialize()
            
        self.is_running = True
        self.results.clear()
        self.seen_ids.clear()
        
        # Main search page
        page = await self.context.new_page()
        
        try:
            # Construct Query
            if district and district.strip():
                query = f"{business_tag} in {district}, {city}"
                self._emit_status(f"Searching: {query}")
            else:
                query = f"{business_tag} in {city}, {region}"
                self._emit_status(f"Searching: {query}")
                
            maps_url = f"https://www.google.com/maps/search/{quote(query)}?hl=en"
            await page.goto(maps_url, wait_until='domcontentloaded', timeout=60000)
            await self._handle_cookie_consent(page)
            
            # 1. Collect all URLs first
            place_urls = await self._scroll_results(page)
            
            if not place_urls:
                self._emit_status("No results found")
                if self.on_complete: self.on_complete()
                return

            self._emit_status(f"Starting extraction for {len(place_urls)} places...")
            await page.close() # Close search page to free memory
            
            # 2. Process in parallel batches
            tasks = []
            for url in place_urls:
                if not self.is_running: break
                
                # Check duplication (rudimentary check using URL ID)
                place_id = self._extract_place_id(url)
                if place_id in self.seen_ids:
                    continue
                self.seen_ids.add(place_id)
                
                # Create Task
                task = asyncio.create_task(self._process_place(url))
                tasks.append(task)
            
            # Execute tasks with progress tracking
            completed = 0
            total = len(tasks)
            
            # Use as_completed to update UI as they finish
            for task in asyncio.as_completed(tasks):
                if not self.is_running: break
                
                result = await task
                completed += 1
                self._emit_status(f"Processing... ({completed}/{total})")
                
                if result:
                    self.results.append(result)
                    self._emit_data(result)
            
            self._emit_status(f"Completed! Extracted {len(self.results)} businesses with enhanced data.")

        except Exception as e:
            self._emit_status(f"Error during search: {str(e)}")
        finally:
             if self.on_complete:
                 self.on_complete()
            
    def stop(self):
        """Stop the scraping process"""
        self.is_running = False
        self._emit_status("Stopping...")
