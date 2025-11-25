import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
from datetime import datetime, date
from bs4 import BeautifulSoup
import random
import hashlib
from typing import List, Dict, Optional
import time

# --- CONFIGURATION ---

DAILY_PRICE_CACHE = {}
NEWS_CACHE = {
    'en': [],
    'hi': [],
    'te': [],
    'last_updated': None
}

LOCATIONS = {
    "Andhra Pradesh": {
        "Visakhapatnam": {"modifier": 1.08}, "Vijayawada": {"modifier": 1.05},
        "Guntur": {"modifier": 1.02}, "Nellore": {"modifier": 1.03},
        "Kurnool": {"modifier": 0.98}, "Tirupati": {"modifier": 1.04},
        "Kakinada": {"modifier": 1.01}, "Rajahmundry": {"modifier": 1.02},
        "Kadapa": {"modifier": 0.99}, "Anantapur": {"modifier": 0.97},
    },
    "Telangana": {
        "Hyderabad": {"modifier": 1.12}, "Warangal": {"modifier": 1.03},
        "Nizamabad": {"modifier": 1.00}, "Karimnagar": {"modifier": 1.01},
    },
    # ... (You can add the other states back here easily)
}

TRANSLATIONS = {
    'en': {
        'dashboard_title': 'Rural Education Dashboard', 'refresh': 'Refresh',
        'last_updated': 'Last Updated', 'news_today': "Today's News",
        'prices_today': "Today's Prices", 'read_more': 'Read More',
        'per_kg': 'per kg', 'per_liter': 'per liter', 'per_dozen': 'per dozen',
        'increase': 'increase', 'decrease': 'decrease', 'local_mandi': 'Mandi',
        'location': 'Location', 'select_location': 'Select Location',
    },
    'hi': {
        'dashboard_title': 'ग्रामीण शिक्षा डैशबोर्ड', 'refresh': 'ताज़ा करें',
        'last_updated': 'अंतिम अपडेट', 'news_today': 'आज की खबरें',
        'prices_today': 'आज के भाव', 'read_more': 'पूरा पढ़ें',
        'per_kg': 'प्रति किलो', 'per_liter': 'प्रति लीटर', 'per_dozen': 'प्रति दर्जन',
        'increase': 'वृद्धि', 'decrease': 'कमी', 'local_mandi': 'मंडी',
        'location': 'स्थान', 'select_location': 'स्थान चुनें',
    },
    'te': {
        'dashboard_title': 'గ్రామీణ విద్యా డాష్‌బోర్డ్', 'refresh': 'రిఫ్రెష్',
        'last_updated': 'చివరిగా నవీకరించబడింది', 'news_today': 'నేటి వార్తలు',
        'prices_today': 'నేటి ధరలు', 'read_more': 'మరింత చదవండి',
        'per_kg': 'కిలోకు', 'per_liter': 'లీటరుకు', 'per_dozen': 'డజనుకు',
        'increase': 'పెరుగుదల', 'decrease': 'తగ్గుదల', 'local_mandi': 'మండి',
        'location': 'ప్రదేశం', 'select_location': 'ప్రదేశం ఎంచుకోండి',
    }
}

FOOD_NAMES = {
    'en': {'Onion': 'Onion', 'Tomato': 'Tomato', 'Potato': 'Potato', 'Rice': 'Rice', 'Wheat': 'Wheat', 'Lentils (Dal)': 'Lentils (Dal)', 'Milk': 'Milk', 'Sugar': 'Sugar', 'Banana': 'Banana', 'Apple': 'Apple', 'Orange': 'Orange', 'Cabbage': 'Cabbage', 'Cauliflower': 'Cauliflower', 'Carrot': 'Carrot', 'Beans': 'Beans', 'Green Chili': 'Green Chili', 'Cooking Oil': 'Cooking Oil', 'Eggs': 'Eggs', 'Ginger': 'Ginger', 'Garlic': 'Garlic'},
    'hi': {'Onion': 'प्याज', 'Tomato': 'टमाटर', 'Potato': 'आलू', 'Rice': 'चावल', 'Wheat': 'गेहूं', 'Lentils (Dal)': 'दाल', 'Milk': 'दूध', 'Sugar': 'चीनी', 'Banana': 'केला', 'Apple': 'सेब', 'Orange': 'संतरा', 'Cabbage': 'पत्तागोभी', 'Cauliflower': 'फूलगोभी', 'Carrot': 'गाजर', 'Beans': 'बीन्स', 'Green Chili': 'हरी मिर्च', 'Cooking Oil': 'खाना पकाने का तेल', 'Eggs': 'अंडे', 'Ginger': 'अदरक', 'Garlic': 'लहसुन'},
    'te': {'Onion': 'ఉల్లిపాయ', 'Tomato': 'టమోటా', 'Potato': 'బంగాళాదుంప', 'Rice': 'బియ్యం', 'Wheat': 'గోధుమ', 'Lentils (Dal)': 'పప్పు', 'Milk': 'పాలు', 'Sugar': 'చక్కెర', 'Banana': 'అరటి', 'Apple': 'ఆపిల్', 'Orange': 'నారింజ', 'Cabbage': 'క్యాబేజీ', 'Cauliflower': 'కాలీఫ్లవర్', 'Carrot': 'క్యారెట్', 'Beans': 'బీన్స్', 'Green Chili': 'పచ్చిమిర్చి', 'Cooking Oil': 'వంట నూనె', 'Eggs': 'గుడ్లు', 'Ginger': 'అల్లం', 'Garlic': 'వెల్లుల్లి'}
}

NEWS_SOURCES = {
    'en': ['https://timesofindia.indiatimes.com/rssfeedstopstories.cms', 'https://www.news18.com/rss/india.xml'],
    'hi': ['https://www.jagran.com/rss_feed.xml', 'https://www.aajtak.in/rssfeeds/rssf.php'],
    'te': ['https://www.news18.com/rss/india.xml', 'https://timesofindia.indiatimes.com/rssfeedstopstories.cms'] # Fallback
}

# --- LIFESPAN MANAGER (BACKGROUND TASKS) ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Launch the news updater in the background
    task = asyncio.create_task(update_news_periodically())
    yield
    # Shutdown: Cancel task if needed (optional)
    task.cancel()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- UTILITY FUNCTIONS ---

def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/rss+xml,application/xml,text/xml',
    }

async def fetch_news_for_lang(lang: str, urls: List[str]):
    """Async news fetcher using HTTPX"""
    articles = []
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        for url in urls:
            try:
                # Add timestamp to prevent caching from the news server side
                bust_url = f"{url}?t={int(time.time())}"
                response = await client.get(bust_url, headers=get_headers())
                
                if response.status_code == 200:
                    # Use lxml for speed, fallback to html.parser
                    try:
                        soup = BeautifulSoup(response.content, 'xml')
                    except:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                    items = soup.find_all('item')[:4] # Take top 4 from each source
                    
                    for item in items:
                        title = item.title.text.strip() if item.title else ""
                        if len(title) < 10: continue
                        
                        link = item.link.text.strip() if item.link else "#"
                        desc = ""
                        if item.description:
                            # Clean HTML out of description
                            desc_soup = BeautifulSoup(item.description.text, 'html.parser')
                            desc = desc_soup.get_text()[:140] + "..."
                        
                        articles.append({
                            "title": title,
                            "description": desc,
                            "url": link,
                            "source": "News Feed",
                            "publishedAt": datetime.now().isoformat()
                        })
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                continue
    return articles

async def update_news_periodically():
    """Background loop that updates news every 60 seconds"""
    while True:
        print(f"🔄 Background Task: Updating News at {datetime.now().strftime('%H:%M:%S')}...")
        
        for lang in ['en', 'hi', 'te']:
            raw_articles = await fetch_news_for_lang(lang, NEWS_SOURCES.get(lang))
            
            # Deduplicate
            seen_hashes = set()
            unique_articles = []
            for art in raw_articles:
                h = hashlib.md5(art['title'].encode()).hexdigest()
                if h not in seen_hashes:
                    seen_hashes.add(h)
                    unique_articles.append(art)
            
            # Update Global Cache
            if unique_articles:
                NEWS_CACHE[lang] = unique_articles[:10]
        
        NEWS_CACHE['last_updated'] = datetime.now().isoformat()
        print("✅ News Updated.")
        
        # Wait for 60 seconds before next update
        await asyncio.sleep(60)

# --- API ENDPOINTS ---

@app.get("/translations")
async def get_translations(lang: str = Query(default="en", pattern="^(en|hi|te)$")):
    return TRANSLATIONS.get(lang, TRANSLATIONS['en'])

@app.get("/locations")
async def get_locations():
    return LOCATIONS

@app.get("/news")
async def get_news(lang: str = Query(default="en", pattern="^(en|hi|te)$")):
    """Returns news instantly from the background cache"""
    news_data = NEWS_CACHE.get(lang, [])
    
    if not news_data:
        return [{"title": "News is loading...", "description": "Please wait a moment.", "url": "#"}]
        
    return news_data

@app.get("/food-prices")
async def get_food_prices(
    lang: str = Query(default="en", pattern="^(en|hi|te)$"),
    city: str = Query(default="Vijayawada"),
    state: str = Query(default="Andhra Pradesh")
):
    today_str = date.today().isoformat()
    cache_key = f"{today_str}_{state}_{city}"
    
    # 1. Check Cache
    if cache_key in DAILY_PRICE_CACHE:
        raw_prices = DAILY_PRICE_CACHE[cache_key]
    else:
        # 2. Generate and Cache if missing
        modifier = 1.0
        if state in LOCATIONS and city in LOCATIONS[state]:
            modifier = LOCATIONS[state][city]['modifier']
            
        raw_prices = generate_location_based_prices(city, modifier)
        
        # Cleanup old cache keys to save memory (keep only today's)
        keys_to_delete = [k for k in DAILY_PRICE_CACHE.keys() if not k.startswith(today_str)]
        for k in keys_to_delete:
            del DAILY_PRICE_CACHE[k]
            
        DAILY_PRICE_CACHE[cache_key] = raw_prices

    # 3. Translate and Return
    return translate_prices(raw_prices, lang, city, state)

def generate_location_based_prices(city: str, modifier: float) -> List[Dict]:
    """Generates deterministic prices based on Date + City"""
    today = date.today()
    seed_str = f"{city}_{today}"
    seed = int(hashlib.md5(seed_str.encode()).hexdigest(), 16) % (10**8)
    random.seed(seed)
    
    base_items = [
        {'name': 'Onion', 'base': 35, 'icon': '🧅', 'volatility': 8},
        {'name': 'Tomato', 'base': 28, 'icon': '🍅', 'volatility': 12},
        {'name': 'Potato', 'base': 22, 'icon': '🥔', 'volatility': 5},
        {'name': 'Rice', 'base': 45, 'icon': '🌾', 'volatility': 2},
        {'name': 'Lentils (Dal)', 'base': 85, 'icon': '🫘', 'volatility': 5},
        {'name': 'Milk', 'base': 55, 'icon': '🥛', 'unit': 'liter', 'volatility': 3},
        {'name': 'Eggs', 'base': 84, 'icon': '🥚', 'unit': 'dozen', 'volatility': 5},
        # Add more items as needed...
    ]
    
    results = []
    for item in base_items:
        # Random fluctuation based on volatility
        fluctuation = random.uniform(-item['volatility'], item['volatility']) / 100
        final_price = item['base'] * modifier * (1 + fluctuation)
        
        results.append({
            'name': item['name'],
            'icon': item['icon'],
            'price': round(final_price, 0), # Rounded to nearest rupee
            'unit': item.get('unit', 'kg'),
            'change': round(random.uniform(-5, 8), 1)
        })
    return results

def translate_prices(prices: List[Dict], lang: str, city: str, state: str) -> List[Dict]:
    lang_names = FOOD_NAMES.get(lang, FOOD_NAMES['en'])
    ui_text = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    
    translated = []
    for item in prices:
        unit_key = 'per_kg'
        if item['unit'] == 'liter': unit_key = 'per_liter'
        elif item['unit'] == 'dozen': unit_key = 'per_dozen'
        
        translated.append({
            'name': item['name'], # Internal ID
            'display_name': lang_names.get(item['name'], item['name']), # Translated Name
            'icon': item['icon'],
            'price': item['price'],
            'unit': ui_text.get(unit_key, ''),
            'market': f"{city} {ui_text.get('local_mandi', 'Mandi')}",
            'change': item['change']
        })
    return translated

if __name__ == "__main__":
    import uvicorn
    # Run the server
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)