"""Enterprise Configuration - Business Data Extractor"""

# ============================================
# SCRAPER PERFORMANCE SETTINGS
# ============================================

# Scroll timing (seconds) - Balanced for speed and reliability
SCROLL_PAUSE_MIN = 2.0
SCROLL_PAUSE_MAX = 3.5

# Click/navigation delay (seconds)
CLICK_DELAY_MIN = 1.0
CLICK_DELAY_MAX = 2.0

# How many times to try scrolling when no new results appear
# Higher = more thorough but slower
MAX_SCROLL_ATTEMPTS = 15

# Maximum results to extract (safety limit)
MAX_RESULTS = 5000

# ============================================
# CONCURRENCY SETTINGS
# ============================================

# Number of parallel browser tabs for extraction
# Recommended: 3-5 for stable performance
# Warning: >8 may trigger rate limiting
MAX_CONCURRENT_PAGES = 4

# ============================================
# BROWSER SETTINGS
# ============================================

# Run browser in background (True) or visible (False)
HEADLESS = False

# Browser viewport size
VIEWPORT_WIDTH = 1920
VIEWPORT_HEIGHT = 1080

# ============================================
# APPLICATION UI SETTINGS
# ============================================

# Window dimensions
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900

# Application branding
APP_TITLE = "Business Extractor Enterprise"

# ============================================
# DATA EXPORT SETTINGS
# ============================================

# Output directory for exported files
OUTPUT_DIR = "exports"

# ============================================
# ADVANCED SETTINGS (Modify with caution)
# ============================================

# Website scraping timeout (ms)
WEBSITE_TIMEOUT = 10000

# Maximum social media links to extract per business
MAX_SOCIALS = 5

# Enable detailed logging
DEBUG_MODE = False
