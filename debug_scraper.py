"""Debug script to analyze Google Maps page structure - Fixed version"""

import asyncio
from playwright.async_api import async_playwright
from urllib.parse import quote

async def debug_maps():
    print("=" * 60)
    print("DEBUG: Starting Google Maps Analysis")
    print("=" * 60)
    
    playwright = await async_playwright().start()
    
    browser = await playwright.chromium.launch(
        headless=False,
        args=['--disable-blink-features=AutomationControlled']
    )
    
    context = await browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        locale='en-US',
    )
    
    page = await context.new_page()
    
    # Search query
    query = "شركة مركبات المحميدية جدة"
    maps_url = f"https://www.google.com/maps/search/{quote(query)}?hl=en"
    
    print(f"\n1. Navigating to: {maps_url}")
    
    # FIX: Use domcontentloaded instead of networkidle
    await page.goto(maps_url, wait_until='domcontentloaded', timeout=30000)
    print(f"   Page DOM loaded!")
    
    print(f"\n2. Current URL: {page.url}")
    
    # Wait for results panel
    print("\n3. Waiting for results panel...")
    try:
        await page.wait_for_selector('div.m6QErb, div[role="feed"], div.Nv2PK', timeout=15000)
        print("   Results panel found!")
    except:
        print("   WARNING: Results panel not detected via selector")
    
    # Additional wait for dynamic content
    print("\n4. Waiting 5 seconds for dynamic content...")
    await asyncio.sleep(5)
    
    # Check for various container selectors
    print("\n5. Testing container selectors:")
    container_selectors = [
        'div[role="feed"]',
        'div[role="main"]',
        'div.m6QErb',
        'div.m6QErb.DxyBCb',
        'div[aria-label*="Results"]',
        'div.Nv2PK',
        'div.ecceSd',
    ]
    
    for selector in container_selectors:
        try:
            count = await page.locator(selector).count()
            print(f"   {selector}: {count} found")
        except Exception as e:
            print(f"   {selector}: ERROR - {str(e)[:50]}")
    
    # Check for link selectors
    print("\n6. Testing link selectors:")
    link_selectors = [
        'a[href*="/maps/place/"]',
        'a.hfpxzc',
        'a[data-value]',
        'div.Nv2PK a',
        'a[href*="maps"]',
        'div.bfdHYd a',
        'a[jsaction]',
    ]
    
    for selector in link_selectors:
        try:
            count = await page.locator(selector).count()
            print(f"   {selector}: {count} found")
            if count > 0 and count < 10:
                links = await page.locator(selector).all()
                for i, link in enumerate(links[:3]):
                    href = await link.get_attribute('href')
                    if href:
                        print(f"      Sample {i+1}: {href[:80]}...")
        except Exception as e:
            print(f"   {selector}: ERROR - {str(e)[:50]}")
    
    # Try to find ALL links on the page
    print("\n7. All links containing 'place' or 'maps':")
    try:
        all_links = await page.locator('a').all()
        print(f"   Total <a> tags on page: {len(all_links)}")
        
        place_links = []
        for link in all_links[:100]:  # Check first 100
            try:
                href = await link.get_attribute('href')
                if href and ('place' in href or '/maps/' in href):
                    place_links.append(href)
            except:
                pass
        
        print(f"   Links with 'place' or '/maps/': {len(place_links)}")
        for i, href in enumerate(place_links[:5]):
            print(f"      {i+1}: {href[:100]}...")
    except Exception as e:
        print(f"   ERROR: {str(e)}")
    
    # Check page content for links
    print("\n8. Searching in page HTML:")
    try:
        content = await page.content()
        import re
        
        # Find all href patterns
        hrefs = re.findall(r'href="([^"]*place[^"]*)"', content)
        print(f"   Found {len(hrefs)} href patterns with 'place'")
        for href in hrefs[:5]:
            print(f"      {href[:100]}...")
        
        # Check for specific patterns
        patterns = [
            (r'/maps/place/', "Standard place links"),
            (r'data-value=', "Data-value attributes"),
            (r'role="feed"', "Feed role containers"),
            (r'class="[^"]*hfpxzc[^"]*"', "hfpxzc class"),
            (r'class="[^"]*Nv2PK[^"]*"', "Nv2PK class (result cards)"),
        ]
        
        print("\n   Pattern matches in HTML:")
        for pattern, desc in patterns:
            matches = len(re.findall(pattern, content))
            print(f"      {desc}: {matches}")
    except Exception as e:
        print(f"   ERROR: {str(e)}")
    
    # Try scrolling and check again
    print("\n9. Scrolling the results panel...")
    try:
        # Find scrollable container
        scrollable = page.locator('div.m6QErb').first
        if await scrollable.count() > 0:
            for i in range(3):
                await scrollable.evaluate('el => el.scrollBy(0, 500)')
                await asyncio.sleep(1)
            
            # Check links again
            links_after = await page.locator('a[href*="/maps/place/"]').count()
            links_hfpxzc = await page.locator('a.hfpxzc').count()
            print(f"   Links after scroll (a[href*='/maps/place/']): {links_after}")
            print(f"   Links after scroll (a.hfpxzc): {links_hfpxzc}")
        else:
            print("   Could not find scrollable container")
    except Exception as e:
        print(f"   Scroll error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("DEBUG COMPLETE - Check the browser window")
    print("Press Enter to close...")
    print("=" * 60)
    
    input()
    
    await browser.close()
    await playwright.stop()

if __name__ == "__main__":
    asyncio.run(debug_maps())
