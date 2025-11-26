import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query, Body
from fastapi.middleware.cors import CORSMiddleware
import httpx
from datetime import datetime
from bs4 import BeautifulSoup
import random
import hashlib
from typing import List, Dict, Optional
import time
import os
from pydantic import BaseModel

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# GROQ API Key - Get free key from https://console.groq.com/
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# ✅ NO API KEYS NEEDED for most features! All data sources are completely free:
# - News: saurav.tech/NewsAPI (free, no key) + RSS feeds
# - Market Prices: Simulated realistic prices
# - Hospitals: OpenStreetMap Overpass API (free, no key)

# --- CACHES ---
NEWS_CACHE = {
    'english': [],
    'telugu': [],
    'last_updated': None
}

MARKET_CACHE = {
    'data': {},
    'last_updated': None
}

HOSPITAL_CACHE = {
    'data': {},
    'last_updated': None
}

# --- CONFIGURATION ---
LOCATIONS = {
    "visakhapatnam": {"lat": 17.6868, "lon": 83.2185, "state": "Andhra Pradesh", "modifier": 1.08},
    "vijayawada": {"lat": 16.5062, "lon": 80.6480, "state": "Andhra Pradesh", "modifier": 1.05},
    "guntur": {"lat": 16.3067, "lon": 80.4365, "state": "Andhra Pradesh", "modifier": 1.02},
    "tirupati": {"lat": 13.6288, "lon": 79.4192, "state": "Andhra Pradesh", "modifier": 1.04},
    "hyderabad": {"lat": 17.3850, "lon": 78.4867, "state": "Telangana", "modifier": 1.12},
}

NEWS_CATEGORIES = ['all', 'education', 'technology', 'science', 'politics', 'sports']

# RSS feeds for Telugu news (free, no API key needed)
TELUGU_RSS_FEEDS = [
    'https://www.eenadu.net/telangana/rss.xml',
    'https://www.andhrajyothy.com/rss/andhra-pradesh-news.xml',
    'https://telugu.oneindia.com/rss/telugu-news-fb.xml',
    'https://www.ntv.co.in/rss/andhrapradesh.xml',
]

ENGLISH_RSS_FEEDS = [
    'https://timesofindia.indiatimes.com/rssfeedstopstories.cms',
    'https://www.thehindu.com/news/national/feeder/default.rss',
    'https://indianexpress.com/feed/',
]

# UI Translations for English and Telugu
UI_TRANSLATIONS = {
    'english': {
        # Header
        'app_title': 'Rural Management Dashboard',
        'app_subtitle': 'Your gateway to rural information and services',
        
        # Navigation
        'nav_education': 'Education & News',
        'nav_agriculture': 'Agriculture & Market',
        'nav_health': 'Health & Medical',
        'nav_chatbot': 'Ask Assistant',
        
        # Common
        'refresh': 'Refresh',
        'loading': 'Loading...',
        'last_updated': 'Last updated',
        'no_data': 'No data available',
        'try_again': 'Try Again',
        'read_more': 'Read more',
        'source': 'Source',
        
        # Education & News Page
        'news_title': 'Education & News',
        'language': 'Language',
        'category': 'Category',
        'fetching_news': 'Fetching latest news...',
        'no_news': 'No news articles found for this category.',
        'categories': {
            'all': 'All',
            'education': 'Education',
            'technology': 'Technology',
            'science': 'Science',
            'politics': 'Politics',
            'sports': 'Sports',
            'general': 'General'
        },
        
        # Agriculture & Market Page
        'market_title': 'Agriculture & Market',
        'select_location': 'Select Location',
        'live_prices': 'Live prices from',
        'market': 'market',
        'fetching_prices': 'Fetching market prices...',
        'no_prices': 'No price data available for this location.',
        'per_kg': '/kg',
        'per_liter': '/liter',
        'per_dozen': '/dozen',
        'commodity_names': {
            'Tomato': 'Tomato',
            'Onion': 'Onion',
            'Potato': 'Potato',
            'Carrot': 'Carrot',
            'Cabbage': 'Cabbage',
            'Rice': 'Rice',
            'Wheat': 'Wheat',
            'Milk': 'Milk',
            'Eggs': 'Eggs'
        },
        
        # Health & Medical Page
        'health_title': 'Health & Medical',
        'your_location': 'Your Location',
        'emergency_call': 'Emergency: Call 108',
        'ambulance_service': '24/7 Ambulance Service',
        'nearest_hospitals': 'Nearest Hospitals in',
        'found': 'found',
        'finding_hospitals': 'Finding nearby hospitals...',
        'no_hospitals': 'No hospitals found for this location.',
        'emergency_24x7': '24/7 Emergency',
        'away': 'away',
        'get_directions': 'Get Directions',
        'data_updated': 'Data updated',
        'hospital_types': {
            'General': 'General',
            'Multi-specialty': 'Multi-specialty'
        },
        
        # Health Resources
        'find_doctor': 'Find a Doctor',
        'find_doctor_desc': 'Search specialists by specialty and location',
        'book_appointment': 'Book Appointment',
        'book_appointment_desc': 'Schedule online appointments with ease',
        'health_records': 'Health Records',
        'health_records_desc': 'Access your medical history securely',
        
        # Locations
        'locations': {
            'visakhapatnam': 'Visakhapatnam',
            'vijayawada': 'Vijayawada',
            'guntur': 'Guntur',
            'tirupati': 'Tirupati',
            'hyderabad': 'Hyderabad'
        },
        
        # Chatbot Page
        'chatbot_title': 'Ask Assistant',
        'chatbot_subtitle': 'Ask any question about agriculture, health, education, or government schemes',
        'chatbot_placeholder': 'Type your question or click the microphone to speak...',
        'chatbot_send': 'Send',
        'chatbot_listening': 'Listening...',
        'chatbot_thinking': 'Thinking...',
        'chatbot_error': 'Sorry, I could not process your request. Please try again.',
        'chatbot_welcome': 'Hello! I am your Rural Assistant. How can I help you today?',
        'chatbot_suggestions': ['What government schemes are available for farmers?', 'How to apply for health insurance?', 'What are today\'s vegetable prices?', 'Nearest hospital in my area?'],
        'voice_not_supported': 'Voice input is not supported in your browser'
    },
    'telugu': {
        # Header
        'app_title': 'గ్రామీణ నిర్వహణ డాష్‌బోర్డ్',
        'app_subtitle': 'గ్రామీణ సమాచారం మరియు సేవలకు మీ గేట్‌వే',
        
        # Navigation
        'nav_education': 'విద్య & వార్తలు',
        'nav_agriculture': 'వ్యవసాయం & మార్కెట్',
        'nav_health': 'ఆరోగ్యం & వైద్యం',
        'nav_chatbot': 'సహాయకుడిని అడగండి',
        
        # Common
        'refresh': 'రిఫ్రెష్',
        'loading': 'లోడ్ అవుతోంది...',
        'last_updated': 'చివరిగా అప్‌డేట్ చేయబడింది',
        'no_data': 'డేటా అందుబాటులో లేదు',
        'try_again': 'మళ్ళీ ప్రయత్నించండి',
        'read_more': 'మరింత చదవండి',
        'source': 'మూలం',
        
        # Education & News Page
        'news_title': 'విద్య & వార్తలు',
        'language': 'భాష',
        'category': 'వర్గం',
        'fetching_news': 'తాజా వార్తలు పొందుతోంది...',
        'no_news': 'ఈ వర్గానికి వార్తా కథనాలు కనుగొనబడలేదు.',
        'categories': {
            'all': 'అన్నీ',
            'education': 'విద్య',
            'technology': 'టెక్నాలజీ',
            'science': 'సైన్స్',
            'politics': 'రాజకీయాలు',
            'sports': 'క్రీడలు',
            'general': 'సాధారణ'
        },
        
        # Agriculture & Market Page
        'market_title': 'వ్యవసాయం & మార్కెట్',
        'select_location': 'ప్రదేశాన్ని ఎంచుకోండి',
        'live_prices': 'లైవ్ ధరలు',
        'market': 'మార్కెట్',
        'fetching_prices': 'మార్కెట్ ధరలు పొందుతోంది...',
        'no_prices': 'ఈ ప్రదేశానికి ధర డేటా అందుబాటులో లేదు.',
        'per_kg': '/కిలో',
        'per_liter': '/లీటర్',
        'per_dozen': '/డజన్',
        'commodity_names': {
            'Tomato': 'టమాటో',
            'Onion': 'ఉల్లిపాయ',
            'Potato': 'బంగాళదుంప',
            'Carrot': 'క్యారెట్',
            'Cabbage': 'క్యాబేజీ',
            'Rice': 'బియ్యం',
            'Wheat': 'గోధుమ',
            'Milk': 'పాలు',
            'Eggs': 'గుడ్లు'
        },
        
        # Health & Medical Page
        'health_title': 'ఆరోగ్యం & వైద్యం',
        'your_location': 'మీ ప్రదేశం',
        'emergency_call': 'అత్యవసరం: 108 కు కాల్ చేయండి',
        'ambulance_service': '24/7 అంబులెన్స్ సేవ',
        'nearest_hospitals': 'సమీపంలోని ఆసుపత్రులు',
        'found': 'కనుగొనబడింది',
        'finding_hospitals': 'సమీపంలోని ఆసుపత్రులను కనుగొంటోంది...',
        'no_hospitals': 'ఈ ప్రదేశానికి ఆసుపత్రులు కనుగొనబడలేదు.',
        'emergency_24x7': '24/7 అత్యవసర',
        'away': 'దూరంలో',
        'get_directions': 'దిశలు పొందండి',
        'data_updated': 'డేటా అప్‌డేట్ చేయబడింది',
        'hospital_types': {
            'General': 'జనరల్',
            'Multi-specialty': 'మల్టీ-స్పెషాలిటీ'
        },
        
        # Health Resources
        'find_doctor': 'డాక్టర్‌ను కనుగొనండి',
        'find_doctor_desc': 'స్పెషాలిటీ మరియు ప్రదేశం ద్వారా నిపుణులను శోధించండి',
        'book_appointment': 'అపాయింట్‌మెంట్ బుక్ చేయండి',
        'book_appointment_desc': 'సులభంగా ఆన్‌లైన్ అపాయింట్‌మెంట్‌లను షెడ్యూల్ చేయండి',
        'health_records': 'ఆరోగ్య రికార్డులు',
        'health_records_desc': 'మీ వైద్య చరిత్రను సురక్షితంగా యాక్సెస్ చేయండి',
        
        # Locations
        'locations': {
            'visakhapatnam': 'విశాఖపట్నం',
            'vijayawada': 'విజయవాడ',
            'guntur': 'గుంటూరు',
            'tirupati': 'తిరుపతి',
            'hyderabad': 'హైదరాబాద్'
        },
        
        # Chatbot Page
        'chatbot_title': 'సహాయకుడిని అడగండి',
        'chatbot_subtitle': 'వ్యవసాయం, ఆరోగ్యం, విద్య లేదా ప్రభుత్వ పథకాల గురించి ఏదైనా ప్రశ్న అడగండి',
        'chatbot_placeholder': 'మీ ప్రశ్నను టైప్ చేయండి లేదా మాట్లాడటానికి మైక్రోఫోన్ క్లిక్ చేయండి...',
        'chatbot_send': 'పంపండి',
        'chatbot_listening': 'వింటోంది...',
        'chatbot_thinking': 'ఆలోచిస్తోంది...',
        'chatbot_error': 'క్షమించండి, మీ అభ్యర్థనను ప్రాసెస్ చేయడం సాధ్యం కాలేదు. దయచేసి మళ్ళీ ప్రయత్నించండి.',
        'chatbot_welcome': 'నమస్కారం! నేను మీ గ్రామీణ సహాయకుడిని. నేను మీకు ఎలా సహాయం చేయగలను?',
        'chatbot_suggestions': ['రైతులకు ఏ ప్రభుత్వ పథకాలు అందుబాటులో ఉన్నాయి?', 'ఆరోగ్య బీమా కోసం ఎలా దరఖాస్తు చేయాలి?', 'నేటి కూరగాయల ధరలు ఏమిటి?', 'నా ప్రాంతంలో సమీపంలోని ఆసుపత్రి?'],
        'voice_not_supported': 'మీ బ్రౌజర్‌లో వాయిస్ ఇన్‌పుట్ మద్దతు లేదు'
    }
}


# --- UTILITY FUNCTIONS ---
def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json,application/xml,text/xml',
    }


# ==================== NEWS FUNCTIONS ====================

async def fetch_news_from_free_api(category: str = 'general') -> List[Dict]:
    """
    Fetch news from saurav.tech/NewsAPI - FREE, NO API KEY NEEDED!
    Categories: business, entertainment, general, health, science, sports, technology
    """
    try:
        # Map our categories to API categories
        category_map = {
            'all': 'general',
            'education': 'general',
            'technology': 'technology',
            'science': 'science',
            'politics': 'general',
            'sports': 'sports',
            'health': 'health',
            'business': 'business'
        }
        
        api_category = category_map.get(category, 'general')
        
        # Free News API - no key required!
        url = f"https://saurav.tech/NewsAPI/top-headlines/category/{api_category}/in.json"
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, headers=get_headers())
            
            if response.status_code == 200:
                data = response.json()
                articles = []
                
                for article in data.get('articles', [])[:15]:
                    title = article.get('title', '')
                    if not title or len(title) < 10:
                        continue
                    
                    articles.append({
                        'id': hashlib.md5(title.encode()).hexdigest()[:8],
                        'title': title,
                        'summary': article.get('description', '') or '',
                        'category': category if category != 'all' else api_category,
                        'date': article.get('publishedAt', '')[:10] if article.get('publishedAt') else datetime.now().strftime('%Y-%m-%d'),
                        'url': article.get('url', '#'),
                        'source': article.get('source', {}).get('name', 'Unknown'),
                        'image': article.get('urlToImage', '')
                    })
                
                return articles
                
    except Exception as e:
        print(f"Free News API error: {e}")
    
    return []


async def fetch_news_from_rss(feeds: List[str], language: str) -> List[Dict]:
    """Fetch news from RSS feeds (free, no API key needed)"""
    articles = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/rss+xml, application/xml, text/xml, */*',
        'Accept-Language': 'te,en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
    }
    
    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        for url in feeds:
            try:
                print(f"📰 Fetching from: {url}")
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    # Try XML parser first, then HTML parser
                    soup = BeautifulSoup(response.content, 'xml')
                    items = soup.find_all('item')
                    
                    if not items:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        items = soup.find_all('item')
                    
                    items = items[:8]  # Get more items
                    
                    for item in items:
                        title = item.find('title')
                        if not title:
                            continue
                        
                        title_text = title.text.strip() if title.text else ""
                        
                        # Clean CDATA
                        title_text = title_text.replace('<![CDATA[', '').replace(']]>', '').strip()
                        
                        if len(title_text) < 5:
                            continue
                        
                        link = item.find('link')
                        link_text = ""
                        if link:
                            link_text = link.text.strip() if link.text else (link.get('href', '#') if link.get('href') else '#')
                        
                        description = item.find('description')
                        pub_date = item.find('pubDate')
                        
                        desc_text = ""
                        if description and description.text:
                            desc_soup = BeautifulSoup(description.text, 'html.parser')
                            desc_text = desc_soup.get_text().strip()[:200]
                        
                        # Try to categorize based on keywords
                        category = 'general'
                        title_check = title_text.lower() + " " + desc_text.lower()
                        
                        if any(w in title_check for w in ['education', 'school', 'university', 'exam', 'విద్య', 'పరీక్ష', 'స్కూల్']):
                            category = 'education'
                        elif any(w in title_check for w in ['tech', 'ai', 'software', 'mobile', 'టెక్నాలజీ', 'మొబైల్']):
                            category = 'technology'
                        elif any(w in title_check for w in ['science', 'research', 'discovery', 'శాస్త్రం', 'పరిశోధన']):
                            category = 'science'
                        elif any(w in title_check for w in ['election', 'minister', 'parliament', 'cm', 'రాజకీయ', 'మంత్రి', 'ఎన్నిక']):
                            category = 'politics'
                        elif any(w in title_check for w in ['cricket', 'sports', 'match', 'ipl', 'క్రికెట్', 'క్రీడ']):
                            category = 'sports'
                        
                        articles.append({
                            'id': hashlib.md5(title_text.encode()).hexdigest()[:8],
                            'title': title_text,
                            'summary': desc_text,
                            'category': category,
                            'date': datetime.now().strftime('%Y-%m-%d'),
                            'url': link_text if link_text else '#',
                            'source': url.split('/')[2]
                        })
                else:
                    print(f"❌ RSS fetch failed for {url}: Status {response.status_code}")
                        
            except Exception as e:
                print(f"❌ RSS fetch error for {url}: {e}")
                continue
    
    print(f"📰 Total {language} articles fetched: {len(articles)}")
    return articles


def get_fallback_telugu_news() -> List[Dict]:
    """Fallback Telugu news if RSS feeds fail"""
    return [
        {
            'id': 'te1',
            'title': 'ఆంధ్రప్రదేశ్‌లో కొత్త విద్యా విధానం అమలు',
            'summary': 'రాష్ట్ర ప్రభుత్వం విద్యా రంగంలో సంస్కరణలు ప్రకటించింది',
            'category': 'education',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'url': '#',
            'source': 'Local News'
        },
        {
            'id': 'te2',
            'title': 'హైదరాబాద్‌లో టెక్నాలజీ సమ్మిట్ ప్రారంభం',
            'summary': 'AI మరియు మెషిన్ లెర్నింగ్ పై చర్చలు జరిగాయి',
            'category': 'technology',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'url': '#',
            'source': 'Tech News'
        },
        {
            'id': 'te3',
            'title': 'క్రికెట్: భారత జట్టు విజయం',
            'summary': 'టీమ్ ఇండియా అద్భుతమైన ప్రదర్శనతో గెలిచింది',
            'category': 'sports',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'url': '#',
            'source': 'Sports News'
        },
        {
            'id': 'te4',
            'title': 'రాష్ట్రంలో వ్యవసాయ రుణాల మాఫీ',
            'summary': 'రైతులకు ప్రభుత్వం మంచి వార్త అందించింది',
            'category': 'politics',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'url': '#',
            'source': 'Political News'
        },
        {
            'id': 'te5',
            'title': 'వైద్య రంగంలో కొత్త ఆవిష్కరణ',
            'summary': 'శాస్త్రవేత్తలు కొత్త చికిత్స పద్ధతిని కనుగొన్నారు',
            'category': 'science',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'url': '#',
            'source': 'Science News'
        }
    ]


async def update_news_cache():
    """Update news cache from free APIs (no keys needed!)"""
    print(f"🔄 Updating news cache at {datetime.now().strftime('%H:%M:%S')}...")
    
    # Fetch English news from FREE API (saurav.tech - no key needed!)
    english_news = await fetch_news_from_free_api('general')
    if not english_news:
        # Fallback to RSS feeds
        english_news = await fetch_news_from_rss(ENGLISH_RSS_FEEDS, 'english')
    
    if english_news:
        NEWS_CACHE['english'] = english_news
    
    # Fetch Telugu news (RSS feeds)
    telugu_news = await fetch_news_from_rss(TELUGU_RSS_FEEDS, 'telugu')
    
    # Use fallback if RSS feeds fail
    if not telugu_news:
        print("⚠️ Telugu RSS feeds failed, using fallback news")
        telugu_news = get_fallback_telugu_news()
    
    NEWS_CACHE['telugu'] = telugu_news
    
    NEWS_CACHE['last_updated'] = datetime.now().isoformat()
    print(f"✅ News cache updated: {len(NEWS_CACHE['english'])} English, {len(NEWS_CACHE['telugu'])} Telugu articles")


# ==================== MARKET PRICE FUNCTIONS ====================
# Using realistic simulated prices (no API key needed!)

def generate_simulated_prices(location: str) -> List[Dict]:
    """Generate realistic simulated prices based on location"""
    loc_data = LOCATIONS.get(location, {"modifier": 1.0})
    modifier = loc_data.get("modifier", 1.0)
    
    base_items = [
        {'name': 'Tomato', 'base': 35, 'unit': 'kg'},
        {'name': 'Onion', 'base': 40, 'unit': 'kg'},
        {'name': 'Potato', 'base': 28, 'unit': 'kg'},
        {'name': 'Carrot', 'base': 50, 'unit': 'kg'},
        {'name': 'Cabbage', 'base': 20, 'unit': 'kg'},
        {'name': 'Rice', 'base': 55, 'unit': 'kg'},
        {'name': 'Wheat', 'base': 35, 'unit': 'kg'},
        {'name': 'Milk', 'base': 60, 'unit': 'liter'},
        {'name': 'Eggs', 'base': 90, 'unit': 'dozen'},
    ]
    
    # Use date as seed for consistent daily prices
    date_seed = int(datetime.now().strftime('%Y%m%d'))
    random.seed(date_seed + hash(location))
    
    prices = []
    for item in base_items:
        variation = random.uniform(0.90, 1.10)
        price = round(item['base'] * modifier * variation)
        change_pct = round(random.uniform(-8, 12), 1)
        
        prices.append({
            'id': len(prices) + 1,
            'name': item['name'],
            'price': price,
            'unit': item['unit'],
            'change': f"{'+' if change_pct > 0 else ''}{change_pct}%",
            'trend': 'up' if change_pct > 0 else ('down' if change_pct < 0 else 'stable')
        })
    
    random.seed()  # Reset seed
    return prices


async def get_market_prices(location: str) -> List[Dict]:
    """Get market prices - realistic simulated prices based on location"""
    return generate_simulated_prices(location)


# ==================== HOSPITAL FUNCTIONS ====================
async def fetch_hospitals_from_overpass(lat: float, lon: float, radius: int = 10000) -> List[Dict]:
    """
    Fetch hospitals from OpenStreetMap Overpass API (completely free, no API key needed)
    """
    try:
        overpass_url = "https://overpass-api.de/api/interpreter"
        
        # Overpass QL query to find hospitals within radius
        query = f"""
        [out:json][timeout:25];
        (
          node["amenity"="hospital"](around:{radius},{lat},{lon});
          way["amenity"="hospital"](around:{radius},{lat},{lon});
          node["amenity"="clinic"](around:{radius},{lat},{lon});
          way["amenity"="clinic"](around:{radius},{lat},{lon});
        );
        out center tags;
        """
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(overpass_url, data={"data": query})
            
            if response.status_code == 200:
                data = response.json()
                hospitals = []
                
                for element in data.get('elements', [])[:15]:  # Limit to 15 results
                    tags = element.get('tags', {})
                    
                    name = tags.get('name', tags.get('name:en', 'Unknown Hospital'))
                    
                    # Get coordinates
                    if element['type'] == 'node':
                        elem_lat, elem_lon = element['lat'], element['lon']
                    else:
                        center = element.get('center', {})
                        elem_lat = center.get('lat', lat)
                        elem_lon = center.get('lon', lon)
                    
                    # Calculate approximate distance
                    import math
                    dlat = math.radians(elem_lat - lat)
                    dlon = math.radians(elem_lon - lon)
                    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat)) * math.cos(math.radians(elem_lat)) * math.sin(dlon/2)**2
                    c = 2 * math.asin(math.sqrt(a))
                    distance = 6371 * c  # Earth's radius in km
                    
                    # Determine hospital type
                    hospital_type = 'General'
                    if tags.get('healthcare:speciality'):
                        hospital_type = 'Multi-specialty'
                    elif 'multi' in name.lower() or 'specialty' in name.lower():
                        hospital_type = 'Multi-specialty'
                    
                    # Check for emergency
                    emergency = tags.get('emergency', '') == 'yes' or 'emergency' in name.lower()
                    
                    hospitals.append({
                        'id': element['id'],
                        'name': name,
                        'type': hospital_type,
                        'distance': f"{distance:.1f} km",
                        'distance_km': distance,
                        'phone': tags.get('phone', tags.get('contact:phone', 'N/A')),
                        'emergency': emergency,
                        'address': tags.get('addr:full', tags.get('addr:street', '')),
                        'website': tags.get('website', tags.get('contact:website', '')),
                        'lat': elem_lat,
                        'lon': elem_lon
                    })
                
                # Sort by distance
                hospitals.sort(key=lambda x: x['distance_km'])
                return hospitals
                
    except Exception as e:
        print(f"Overpass API error: {e}")
    
    return []


def generate_fallback_hospitals(location: str) -> List[Dict]:
    """Generate fallback hospital data if API fails"""
    hospital_templates = [
        {'name': 'Government General Hospital', 'type': 'General', 'emergency': True},
        {'name': 'Apollo Hospital', 'type': 'Multi-specialty', 'emergency': True},
        {'name': 'KIMS Hospital', 'type': 'Multi-specialty', 'emergency': True},
        {'name': 'Care Hospital', 'type': 'Multi-specialty', 'emergency': True},
        {'name': 'City Medical Center', 'type': 'General', 'emergency': False},
        {'name': 'District Hospital', 'type': 'General', 'emergency': True},
    ]
    
    location_title = location.title()
    hospitals = []
    
    for i, template in enumerate(hospital_templates):
        hospitals.append({
            'id': i + 1,
            'name': f"{template['name']}, {location_title}",
            'type': template['type'],
            'distance': f"{round(random.uniform(1, 8), 1)} km",
            'phone': f"0891-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            'emergency': template['emergency'],
            'address': f"{location_title}, Andhra Pradesh",
            'website': '',
            'lat': 0,
            'lon': 0
        })
    
    return hospitals


async def get_hospitals(location: str) -> List[Dict]:
    """Get hospitals for a location"""
    loc_data = LOCATIONS.get(location, {})
    
    if not loc_data:
        return generate_fallback_hospitals(location)
    
    lat = loc_data['lat']
    lon = loc_data['lon']
    
    # Try OpenStreetMap first
    hospitals = await fetch_hospitals_from_overpass(lat, lon)
    
    if hospitals:
        return hospitals
    
    # Fallback to generated data
    return generate_fallback_hospitals(location)


# ==================== BACKGROUND TASKS ====================
async def update_caches_periodically():
    """Background loop that updates caches every 5 minutes"""
    while True:
        try:
            await update_news_cache()
        except Exception as e:
            print(f"❌ Cache update error: {e}")
        
        await asyncio.sleep(300)  # 5 minutes


# --- LIFESPAN MANAGER ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initial cache population
    await update_news_cache()
    
    # Start background task
    cache_task = asyncio.create_task(update_caches_periodically())
    
    try:
        yield
    finally:
        cache_task.cancel()
        try:
            await cache_task
        except asyncio.CancelledError:
            pass


# --- CREATE APP ---
app = FastAPI(
    title="Unified Dashboard API",
    description="API for Education, Agriculture, and Health data",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== API ENDPOINTS ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "message": "All APIs are FREE - no keys needed!"
    }


@app.get("/api/locations")
async def get_locations():
    """Get available locations"""
    return {
        "locations": list(LOCATIONS.keys()),
        "details": LOCATIONS
    }


@app.get("/api/translations")
async def get_translations(
    language: str = Query(default="english", regex="^(english|telugu)$")
):
    """Get UI translations for the specified language"""
    return UI_TRANSLATIONS.get(language, UI_TRANSLATIONS['english'])


# --- NEWS ENDPOINTS ---
@app.get("/api/news")
async def get_news(
    language: str = Query(default="english", regex="^(english|telugu)$"),
    category: str = Query(default="all")
):
    """Get news articles - uses FREE API (no key needed!)"""
    
    if language == 'english':
        # For English, fetch by category from free API (supports category filtering)
        if category != 'all':
            # Fetch directly from API with category filter
            news = await fetch_news_from_free_api(category)
            if not news:
                # Fallback: filter from cache
                cached_news = NEWS_CACHE.get('english', [])
                news = [n for n in cached_news if n.get('category') == category]
        else:
            # Get all news from cache or fetch fresh
            news = NEWS_CACHE.get('english', [])
            if not news:
                news = await fetch_news_from_free_api('general')
                if not news:
                    news = await fetch_news_from_rss(ENGLISH_RSS_FEEDS, 'english')
    else:
        # Telugu - use cache or fetch from RSS
        news = NEWS_CACHE.get('telugu', [])
        if not news:
            news = await fetch_news_from_rss(TELUGU_RSS_FEEDS, 'telugu')
            if not news:
                news = get_fallback_telugu_news()
        
        # Filter Telugu news by category if needed
        if category != 'all':
            news = [n for n in news if n.get('category') == category]
    
    return {
        "articles": news,
        "language": language,
        "category": category,
        "last_updated": NEWS_CACHE.get('last_updated'),
        "total": len(news)
    }


@app.get("/api/news/categories")
async def get_news_categories():
    """Get available news categories"""
    return {"categories": NEWS_CATEGORIES}


# --- MARKET PRICE ENDPOINTS ---
@app.get("/api/market-prices")
async def get_market_prices_endpoint(
    location: str = Query(default="visakhapatnam")
):
    """Get market prices for a location"""
    location = location.lower()
    
    if location not in LOCATIONS:
        location = "visakhapatnam"
    
    prices = await get_market_prices(location)
    
    return {
        "location": location,
        "location_display": location.title(),
        "prices": prices,
        "date": datetime.now().strftime('%Y-%m-%d'),
        "last_updated": datetime.now().isoformat()
    }


# --- HOSPITAL ENDPOINTS ---
@app.get("/api/hospitals")
async def get_hospitals_endpoint(
    location: str = Query(default="visakhapatnam")
):
    """Get hospitals near a location"""
    location = location.lower()
    
    if location not in LOCATIONS:
        location = "visakhapatnam"
    
    hospitals = await get_hospitals(location)
    
    return {
        "location": location,
        "location_display": location.title(),
        "hospitals": hospitals,
        "total": len(hospitals),
        "last_updated": datetime.now().isoformat()
    }


# --- COMBINED DASHBOARD ENDPOINT ---
@app.get("/api/dashboard")
async def get_dashboard_data(
    location: str = Query(default="visakhapatnam"),
    language: str = Query(default="english")
):
    """Get all dashboard data in one call"""
    location = location.lower()
    
    # Fetch all data in parallel
    news_task = get_news(language, "all")
    prices_task = get_market_prices(location)
    hospitals_task = get_hospitals(location)
    
    news_data, prices, hospitals = await asyncio.gather(
        news_task, prices_task, hospitals_task
    )
    
    return {
        "location": location,
        "language": language,
        "news": news_data,
        "market_prices": {
            "location": location,
            "prices": prices
        },
        "hospitals": {
            "location": location,
            "hospitals": hospitals
        },
        "timestamp": datetime.now().isoformat()
    }


# ==================== CHATBOT ENDPOINT ====================

class ChatRequest(BaseModel):
    message: str
    language: str = "english"


class ChatResponse(BaseModel):
    response: str
    success: bool


@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest):
    """
    Chat with GROQ-powered AI assistant.
    Get your free API key from: https://console.groq.com/
    """
    if not GROQ_API_KEY:
        return ChatResponse(
            response="Chatbot is not configured. Please set GROQ_API_KEY in the server's .env file. Get your free key from https://console.groq.com/",
            success=False
        )
    
    try:
        # System prompt for rural management context
        system_prompt = """You are a helpful Rural Management Assistant for people in India, especially in Andhra Pradesh and Telangana. 
        
You help with:
- Agriculture: Crop information, farming techniques, market prices, weather
- Government Schemes: PM-KISAN, crop insurance, subsidies, MGNREGA
- Health: Basic health advice, nearby hospitals, government health schemes like Ayushman Bharat
- Education: School information, scholarships, skill development programs
- General queries: Any questions related to rural life and services

Be concise, helpful, and provide accurate information. If asked in Telugu, respond in Telugu.
If you don't know something, say so honestly and suggest where they might find help."""

        # Prepare messages for GROQ
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.message}
        ]
        
        # Call GROQ API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1024
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                assistant_message = data["choices"][0]["message"]["content"]
                return ChatResponse(response=assistant_message, success=True)
            else:
                error_msg = f"API Error: {response.status_code}"
                print(f"GROQ API Error: {response.text}")
                return ChatResponse(response=error_msg, success=False)
                
    except httpx.TimeoutException:
        return ChatResponse(
            response="Request timed out. Please try again.",
            success=False
        )
    except Exception as e:
        print(f"Chat error: {e}")
        return ChatResponse(
            response=f"An error occurred: {str(e)}",
            success=False
        )


@app.get("/api/chat/status")
async def chat_status():
    """Check if chatbot is configured"""
    return {
        "configured": bool(GROQ_API_KEY),
        "message": "Chatbot is ready!" if GROQ_API_KEY else "GROQ_API_KEY not set. Get your free key from https://console.groq.com/"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
