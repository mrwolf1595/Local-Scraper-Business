"""Configuration settings for the Google Maps Scraper"""

# Scraper Settings
SCROLL_PAUSE_MIN = 2.5
SCROLL_PAUSE_MAX = 4.5
CLICK_DELAY_MIN = 1.5
CLICK_DELAY_MAX = 3.0

# "MAX_SCROLL_ATTEMPTS" here refers to how many times we try scrolling
# when NO NEW results appear (to detect the end of the list).
# It does NOT limit the total number of results.
MAX_SCROLL_ATTEMPTS = 20

# Safety limit for total results (set very high for "unlimited")
MAX_RESULTS = 10000

# Concurrency Settings (New)
# Number of tabs to open simultaneously for faster extraction.
# Warning: Setting this too high (e.g., > 10) might get you blocked.
MAX_CONCURRENT_PAGES = 4

# Browser Settings
HEADLESS = False
VIEWPORT_WIDTH = 1920
VIEWPORT_HEIGHT = 1080

# UI Settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
APP_TITLE = "Business Data Extractor Enterprise"

# Data Export
OUTPUT_DIR = "exports"
