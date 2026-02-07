"""Google Maps Scraper Engine"""

import asyncio
import random
import re
from urllib.parse import quote
from typing import Callable, Optional, Dict, List
from playwright.async_api import async_playwright, Page, Browser
from config import *


class GoogleMapsScraper:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.is_running = False
        self.seen_ids = set()
        self.results = []
        
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
        context = await self.browser.new_context(
            viewport={'width': VIEWPORT_WIDTH, 'height': VIEWPORT_HEIGHT},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US'
        )
        
        # Stealth mode: hide webdriver
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        self.page = await context.new_page()
        
    async def close(self):
        """Close the browser"""
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
        # Try to extract CID
        cid_match = re.search(r'!1s(0x[a-f0-9:]+)', url)
        if cid_match:
            return cid_match.group(1)
        
        # Try to extract place_id
        place_match = re.search(r'place_id:([A-Za-z0-9_-]+)', url)
        if place_match:
            return place_match.group(1)
            
        # Fallback: use the full URL
        return url
        
    async def _handle_cookie_consent(self):
        """Handle the cookie consent popup"""
        try:
            # Wait for and click the accept button
            accept_button = self.page.locator('button:has-text("Accept all"), button:has-text("قبول الكل")')
            await accept_button.click(timeout=5000)
            await asyncio.sleep(1)
            self._emit_status("✓ Accepted cookies")
        except Exception:
            # Cookie popup might not appear
            pass
            
    async def _scroll_results(self) -> List[str]:
        """Scroll through results and collect all place URLs"""
        self._emit_status("🔄 Scrolling through results...")
        
        # Locate the scrollable container
        try:
            # Wait for results to load
            await self.page.wait_for_selector('div[role="feed"]', timeout=10000)
            scrollable_div = self.page.locator('div[role="feed"]').first
        except Exception as e:
            self._emit_status(f"❌ Could not find results: {str(e)}")
            return []
        
        place_urls = []
        last_height = 0
        no_change_count = 0
        scroll_attempts = 0
        while self.is_running:
            scroll_attempts += 1
            
            # Get current height
            current_height = await scrollable_div.evaluate('el => el.scrollHeight')
            
            # Scroll to bottom
            await scrollable_div.evaluate('el => el.scrollTo(0, el.scrollHeight)')
            
            # Random delay to mimic human behavior
            delay = random.uniform(SCROLL_PAUSE_MIN, SCROLL_PAUSE_MAX)
            await asyncio.sleep(delay)
            
            # Check if we've reached the end
            if current_height == last_height:
                no_change_count += 1
                if no_change_count >= MAX_SCROLL_ATTEMPTS:
                    break
            else:
                no_change_count = 0
                
            last_height = current_height
            
            # Count current results
            links = await self.page.locator('a[href*="/maps/place/"]').all()
            self._emit_status(f"📊 Found {len(links)} results so far...")
            
            # Check for "end of results" message
            try:
                end_message = self.page.locator('text=/You\'ve reached the end|النهاية/i')
                if await end_message.count() > 0:
                    self._emit_status("✓ Reached end of results")
                    break
            except Exception:
                pass
                
        # Extract all unique place URLs
        links = await self.page.locator('a[href*="/maps/place/"]').all()
        for link in links:
            href = await link.get_attribute('href')
            if href and href not in place_urls:
                place_urls.append(href)
                
        self._emit_status(f"✓ Collected {len(place_urls)} unique places")
        return place_urls
        
    async def _extract_place_details(self, url: str) -> Optional[Dict]:
        """Extract details from a specific place page"""
        try:
            # Navigate to the place
            full_url = f"https://www.google.com{url}" if url.startswith('/') else url
            await self.page.goto(full_url, wait_until='domcontentloaded', timeout=15000)
            
            # Random delay
            await asyncio.sleep(random.uniform(CLICK_DELAY_MIN, CLICK_DELAY_MAX))
            
            # Extract place ID for deduplication
            place_id = self._extract_place_id(self.page.url)
            
            # Check if already seen
            if place_id in self.seen_ids:
                return None
                
            self.seen_ids.add(place_id)
            
            # Extract name
            name = None
            try:
                name_elem = self.page.locator('h1').first
                name = await name_elem.inner_text(timeout=3000)
            except Exception:
                pass
                
            # Extract phone
            phone = None
            try:
                phone_elem = self.page.locator('button[data-item-id*="phone"]').first
                phone_text = await phone_elem.inner_text(timeout=3000)
                # Clean phone number
                phone = re.sub(r'[^\d+\s()-]', '', phone_text)
            except Exception:
                pass
                
            # Extract address
            address = None
            try:
                address_elem = self.page.locator('button[data-item-id*="address"]').first
                address = await address_elem.inner_text(timeout=3000)
            except Exception:
                pass
                
            # Extract coordinates from URL
            coords_match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', self.page.url)
            latitude = coords_match.group(1) if coords_match else None
            longitude = coords_match.group(2) if coords_match else None
            
            if name:  # Only return if we at least got the name
                return {
                    'id': place_id,
                    'name': name,
                    'phone': phone or 'N/A',
                    'address': address or 'N/A',
                    'latitude': latitude,
                    'longitude': longitude,
                    'url': self.page.url
                }
                
        except Exception as e:
            self._emit_status(f"⚠️ Error extracting details: {str(e)}")
            
        return None
        
    async def search(self, business_tag: str, region: str, city: str, district: str = ""):
        """Main search function"""
        if not self.page:
            await self.initialize()
            
        self.is_running = True
        self.results.clear()
        
        # Build strict search query
        # Using quotations for district can sometimes help exact matching in Google Maps, 
        # but standard "Keyword in District, City" is usually most effective.
        if district and district.strip():
            # Prioritize district in the query
            query = f"{business_tag} in {district}, {city}"
            self._emit_status(f"🔍 Searching for: {business_tag} in {district}, {city} (Strict Mode)")
        else:
            query = f"{business_tag} in {city}, {region}"
            self._emit_status(f"🔍 Searching for: {business_tag} in {city}, {region}")
            
        encoded_query = quote(query)
        
        # Navigate to Google Maps
        maps_url = f"https://www.google.com/maps/search/{encoded_query}?hl=en"
        try:
            await self.page.goto(maps_url, wait_until='domcontentloaded', timeout=60000)
        except Exception as e:
            self._emit_status(f"⚠️ Navigation error: {str(e)}")
            return
        
        # Handle cookie consent
        await self._handle_cookie_consent()
        
        # Wait for results to load
        await asyncio.sleep(3)
        
        # Scroll and collect URLs
        place_urls = await self._scroll_results()
        
        if not place_urls:
            self._emit_status("❌ No results found")
            if self.on_complete:
                self.on_complete()
            return
            
        # Filter out already seen places BEFORE visiting them to save time
        new_urls = []
        for url in place_urls:
            place_id = self._extract_place_id(url)
            if place_id and place_id not in self.seen_ids:
                new_urls.append(url)
            elif not place_id:
                # If we can't extract ID, we might visit it just in case, or skip. 
                # Better to skip if we want to be strict, but let's visit if ID extraction failed
                new_urls.append(url)
        
        if not new_urls:
            self._emit_status("⚠️ Found results but all were already collected (Duplicates skipped).")
            if self.on_complete:
                self.on_complete()
            return

        self._emit_status(f"📊 Found {len(new_urls)} new unique places to extract...")

        # Extract details from each place
        total = len(new_urls)
        for idx, url in enumerate(new_urls, 1):
            if not self.is_running:
                break
                
            self._emit_status(f"📝 Extracting {idx}/{total}...")
            
            details = await self._extract_place_details(url)
            if details:
                self.results.append(details)
                self._emit_data(details)
                
        self._emit_status(f"✅ Completed! Added {len(self.results)} new unique businesses")
        
        if self.on_complete:
            self.on_complete()
            
    def stop(self):
        """Stop the scraping process"""
        self.is_running = False
        self._emit_status("⏸️ Stopping...")
