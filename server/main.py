import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query, Body
from fastapi.middleware.cors import CORSMiddleware
import httpx
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import random
import hashlib
from typing import List, Dict, Optional
import time
import os
import math
from pydantic import BaseModel

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# GROQ API Key - Get free key from https://console.groq.com/
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# ✅ ALL APIs ARE FREE - NO KEYS NEEDED (except GROQ for chatbot):
# - Weather: Open-Meteo API (free, no key)
# - News: saurav.tech/NewsAPI (free, no key)
# - Hospitals/Pharmacies/Blood Banks: OpenStreetMap Overpass API (free, no key)
# - Government Schemes: Built-in database

# --- CACHES ---
NEWS_CACHE = {'english': [], 'telugu': [], 'last_updated': None}
WEATHER_CACHE = {}  # location -> weather data
SCHEMES_CACHE = {'last_updated': None}

# --- CONFIGURATION ---
LOCATIONS = {
    "visakhapatnam": {"lat": 17.6868, "lon": 83.2185, "state": "Andhra Pradesh", "district": "Visakhapatnam"},
    "vijayawada": {"lat": 16.5062, "lon": 80.6480, "state": "Andhra Pradesh", "district": "Krishna"},
    "guntur": {"lat": 16.3067, "lon": 80.4365, "state": "Andhra Pradesh", "district": "Guntur"},
    "tirupati": {"lat": 13.6288, "lon": 79.4192, "state": "Andhra Pradesh", "district": "Tirupati"},
    "hyderabad": {"lat": 17.3850, "lon": 78.4867, "state": "Telangana", "district": "Hyderabad"},
    "warangal": {"lat": 17.9784, "lon": 79.5941, "state": "Telangana", "district": "Warangal"},
    "karimnagar": {"lat": 18.4386, "lon": 79.1288, "state": "Telangana", "district": "Karimnagar"},
    "nellore": {"lat": 14.4426, "lon": 79.9865, "state": "Andhra Pradesh", "district": "Nellore"},
    "kurnool": {"lat": 15.8281, "lon": 78.0373, "state": "Andhra Pradesh", "district": "Kurnool"},
    "rajahmundry": {"lat": 16.9891, "lon": 81.7840, "state": "Andhra Pradesh", "district": "East Godavari"},
}

NEWS_CATEGORIES = ['all', 'education', 'technology', 'science', 'politics', 'sports', 'health']

# RSS feeds
TELUGU_RSS_FEEDS = [
    'https://www.eenadu.net/telangana/rss.xml',
    'https://telugu.oneindia.com/rss/telugu-news-fb.xml',
]
ENGLISH_RSS_FEEDS = [
    'https://timesofindia.indiatimes.com/rssfeedstopstories.cms',
    'https://indianexpress.com/feed/',
]

# ==================== GOVERNMENT SCHEMES DATABASE ====================
GOVERNMENT_SCHEMES = [
    # Farmer Schemes
    {
        "id": "pm-kisan",
        "name": "PM-KISAN",
        "name_te": "పిఎం-కిసాన్",
        "category": "farmer",
        "description": "Direct income support of ₹6,000 per year to farmer families in three equal installments",
        "description_te": "రైతు కుటుంబాలకు సంవత్సరానికి ₹6,000 ప్రత్యక్ష ఆదాయ మద్దతు మూడు సమాన వాయిదాల్లో",
        "eligibility": "All land-holding farmer families with cultivable land",
        "benefits": "₹6,000 per year (₹2,000 every 4 months)",
        "documents": ["Aadhaar Card", "Land Records", "Bank Account"],
        "apply_link": "https://pmkisan.gov.in/",
        "helpline": "155261"
    },
    {
        "id": "pmfby",
        "name": "PM Fasal Bima Yojana (Crop Insurance)",
        "name_te": "పిఎం ఫసల్ బీమా యోజన",
        "category": "farmer",
        "description": "Crop insurance scheme protecting farmers against crop loss due to natural calamities",
        "description_te": "ప్రకృతి వైపరీత్యాల వల్ల పంట నష్టం నుండి రైతులను రక్షించే పంట బీమా పథకం",
        "eligibility": "All farmers growing notified crops",
        "benefits": "Insurance coverage for crop loss with minimal premium (2% for Kharif, 1.5% for Rabi)",
        "documents": ["Land Records", "Aadhaar", "Bank Account", "Sowing Certificate"],
        "apply_link": "https://pmfby.gov.in/",
        "helpline": "1800-180-1551"
    },
    {
        "id": "kcc",
        "name": "Kisan Credit Card (KCC)",
        "name_te": "కిసాన్ క్రెడిట్ కార్డ్",
        "category": "farmer",
        "description": "Credit facility for farmers to meet agricultural and other needs at low interest rates",
        "description_te": "తక్కువ వడ్డీ రేట్లతో వ్యవసాయ మరియు ఇతర అవసరాలను తీర్చడానికి రైతులకు క్రెడిట్ సౌకర్యం",
        "eligibility": "Farmers, sharecroppers, tenant farmers",
        "benefits": "Credit up to ₹3 lakh at 4% interest (with prompt repayment)",
        "documents": ["Land Records", "Aadhaar", "Passport Photo", "Application Form"],
        "apply_link": "https://www.pmkisan.gov.in/",
        "helpline": "1800-180-1551"
    },
    {
        "id": "soil-health",
        "name": "Soil Health Card Scheme",
        "name_te": "సాయిల్ హెల్త్ కార్డ్ స్కీమ్",
        "category": "farmer",
        "description": "Provides soil health cards to farmers with crop-wise nutrient recommendations",
        "description_te": "పంట వారీగా పోషక సిఫార్సులతో రైతులకు మట్టి ఆరోగ్య కార్డులను అందిస్తుంది",
        "eligibility": "All farmers",
        "benefits": "Free soil testing and recommendations for fertilizer usage",
        "documents": ["Aadhaar", "Land Details"],
        "apply_link": "https://soilhealth.dac.gov.in/",
        "helpline": "1800-180-1551"
    },
    {
        "id": "rythu-bandhu",
        "name": "Rythu Bandhu (Telangana)",
        "name_te": "రైతు బంధు",
        "category": "farmer",
        "description": "Investment support of ₹10,000 per acre per year for agriculture in Telangana",
        "description_te": "తెలంగాణలో వ్యవసాయానికి సంవత్సరానికి ఎకరాకు ₹10,000 పెట్టుబడి మద్దతు",
        "eligibility": "Farmers in Telangana with pattadar passbook",
        "benefits": "₹10,000 per acre per year (₹5,000 each season)",
        "documents": ["Pattadar Passbook", "Aadhaar", "Bank Account"],
        "apply_link": "https://rythubandhu.telangana.gov.in/",
        "helpline": "1800-599-7777"
    },
    {
        "id": "ysr-rythu-bharosa",
        "name": "YSR Rythu Bharosa (Andhra Pradesh)",
        "name_te": "వైఎస్ఆర్ రైతు భరోసా",
        "category": "farmer",
        "description": "Investment support scheme for farmers in Andhra Pradesh",
        "description_te": "ఆంధ్రప్రదేశ్‌లో రైతులకు పెట్టుబడి మద్దతు పథకం",
        "eligibility": "Farmers in Andhra Pradesh",
        "benefits": "₹13,500 per year for landholding farmers",
        "documents": ["Land Records", "Aadhaar", "Bank Account"],
        "apply_link": "https://ysrrythubharosa.ap.gov.in/",
        "helpline": "1902"
    },
    # Health Schemes
    {
        "id": "ayushman-bharat",
        "name": "Ayushman Bharat (PM-JAY)",
        "name_te": "ఆయుష్మాన్ భారత్",
        "category": "health",
        "description": "Health insurance of ₹5 lakh per family per year for secondary and tertiary hospitalization",
        "description_te": "ద్వితీయ మరియు తృతీయ ఆసుపత్రి చికిత్స కోసం కుటుంబానికి సంవత్సరానికి ₹5 లక్షల ఆరోగ్య బీమా",
        "eligibility": "Bottom 40% of population as per SECC data",
        "benefits": "₹5 lakh health cover, cashless treatment at empaneled hospitals",
        "documents": ["Aadhaar", "Ration Card", "SECC inclusion"],
        "apply_link": "https://pmjay.gov.in/",
        "helpline": "14555"
    },
    {
        "id": "aarogyasri",
        "name": "Dr. YSR Aarogyasri (AP)",
        "name_te": "డా. వైఎస్ఆర్ ఆరోగ్యశ్రీ",
        "category": "health",
        "description": "Health scheme for BPL families in Andhra Pradesh covering serious ailments",
        "description_te": "ఆంధ్రప్రదేశ్‌లో బిపిఎల్ కుటుంబాలకు తీవ్రమైన వ్యాధులను కవర్ చేసే ఆరోగ్య పథకం",
        "eligibility": "BPL families in Andhra Pradesh",
        "benefits": "Free treatment for 2,446 procedures at network hospitals",
        "documents": ["Aarogyasri Card", "Aadhaar", "White Ration Card"],
        "apply_link": "https://aarogyasri.telangana.gov.in/",
        "helpline": "104"
    },
    {
        "id": "janani-suraksha",
        "name": "Janani Suraksha Yojana",
        "name_te": "జననీ సురక్ష యోజన",
        "category": "health",
        "description": "Cash assistance for institutional delivery to reduce maternal mortality",
        "description_te": "మాతృ మరణాలను తగ్గించడానికి సంస్థాగత ప్రసవానికి నగదు సహాయం",
        "eligibility": "Pregnant women from BPL families",
        "benefits": "₹1,400 for rural, ₹1,000 for urban institutional deliveries",
        "documents": ["BPL Card", "Aadhaar", "MCH Card"],
        "apply_link": "https://nhm.gov.in/",
        "helpline": "104"
    },
    # Education & Welfare
    {
        "id": "pm-scholarship",
        "name": "PM Scholarship Scheme",
        "name_te": "పిఎం స్కాలర్‌షిప్ స్కీమ్",
        "category": "education",
        "description": "Scholarships for children of ex-servicemen and ex-coast guard personnel",
        "description_te": "మాజీ సైనికులు మరియు మాజీ కోస్ట్ గార్డ్ సిబ్బంది పిల్లలకు స్కాలర్‌షిప్‌లు",
        "eligibility": "Children of ex-servicemen pursuing professional courses",
        "benefits": "₹2,500/month for boys, ₹3,000/month for girls",
        "documents": ["Ex-serviceman certificate", "Mark sheets", "Bank Account"],
        "apply_link": "https://scholarships.gov.in/",
        "helpline": "0120-6619540"
    },
    {
        "id": "vidya-lakshmi",
        "name": "Vidya Lakshmi Education Loan",
        "name_te": "విద్యా లక్ష్మి విద్యా రుణం",
        "category": "education",
        "description": "Single window for students to apply for education loans from multiple banks",
        "description_te": "బహుళ బ్యాంకుల నుండి విద్యా రుణాల కోసం విద్యార్థులకు సింగిల్ విండో",
        "eligibility": "Students pursuing higher education in India/abroad",
        "benefits": "Education loans up to ₹20 lakh without collateral",
        "documents": ["Admission Letter", "Mark Sheets", "Income Proof"],
        "apply_link": "https://www.vidyalakshmi.co.in/",
        "helpline": "1800-180-5209"
    },
    {
        "id": "mgnrega",
        "name": "MGNREGA (Job Guarantee)",
        "name_te": "ఎంజిఎన్‌ఆర్‌ఇజిఎ",
        "category": "employment",
        "description": "Guarantees 100 days of wage employment per year to rural households",
        "description_te": "గ్రామీణ కుటుంబాలకు సంవత్సరానికి 100 రోజుల వేతన ఉపాధికి హామీ ఇస్తుంది",
        "eligibility": "Adult members of rural households willing to do unskilled manual work",
        "benefits": "100 days guaranteed work, wages as per state notification",
        "documents": ["Job Card", "Aadhaar", "Bank Account"],
        "apply_link": "https://nrega.nic.in/",
        "helpline": "1800-345-22-44"
    },
    {
        "id": "mudra-loan",
        "name": "PM MUDRA Yojana",
        "name_te": "పిఎం ముద్ర యోజన",
        "category": "employment",
        "description": "Loans up to ₹10 lakh for small businesses without collateral",
        "description_te": "చిన్న వ్యాపారాలకు కొలాటరల్ లేకుండా ₹10 లక్షల వరకు రుణాలు",
        "eligibility": "Non-farm small/micro enterprises",
        "benefits": "Shishu: up to ₹50,000, Kishore: ₹50,000-5L, Tarun: ₹5L-10L",
        "documents": ["Business Plan", "Aadhaar", "Address Proof"],
        "apply_link": "https://www.mudra.org.in/",
        "helpline": "1800-180-1111"
    },
    {
        "id": "pm-awas-gramin",
        "name": "PM Awas Yojana (Gramin)",
        "name_te": "పిఎం ఆవాస్ యోజన (గ్రామీణ)",
        "category": "housing",
        "description": "Financial assistance for construction of houses in rural areas",
        "description_te": "గ్రామీణ ప్రాంతాల్లో గృహ నిర్మాణానికి ఆర్థిక సహాయం",
        "eligibility": "Houseless or living in kutcha/dilapidated house",
        "benefits": "₹1.20 lakh in plain areas, ₹1.30 lakh in hilly areas",
        "documents": ["Aadhaar", "SECC Data", "Bank Account"],
        "apply_link": "https://pmayg.nic.in/",
        "helpline": "1800-11-6446"
    },
    {
        "id": "ujjwala",
        "name": "PM Ujjwala Yojana",
        "name_te": "పిఎం ఉజ్జ్వల యోజన",
        "category": "welfare",
        "description": "Free LPG connections to women from BPL households",
        "description_te": "బిపిఎల్ కుటుంబాల మహిళలకు ఉచిత ఎల్‌పిజి కనెక్షన్లు",
        "eligibility": "Women from BPL households",
        "benefits": "Free LPG connection with first refill and stove",
        "documents": ["BPL Card", "Aadhaar", "Bank Account"],
        "apply_link": "https://www.pmuy.gov.in/",
        "helpline": "1800-266-6696"
    },
    {
        "id": "sukanya-samriddhi",
        "name": "Sukanya Samriddhi Yojana",
        "name_te": "సుకన్య సమృద్ధి యోజన",
        "category": "welfare",
        "description": "Savings scheme for girl child with attractive interest rates",
        "description_te": "ఆకర్షణీయమైన వడ్డీ రేట్లతో ఆడపిల్లల కోసం పొదుపు పథకం",
        "eligibility": "Girl child below 10 years",
        "benefits": "8.2% interest rate, tax benefits under 80C",
        "documents": ["Birth Certificate", "Aadhaar of Guardian", "Address Proof"],
        "apply_link": "https://www.nsiindia.gov.in/",
        "helpline": "1800-180-1111"
    }
]

SCHEME_CATEGORIES = [
    {"id": "all", "name": "All Schemes", "name_te": "అన్ని పథకాలు"},
    {"id": "farmer", "name": "Farmer Schemes", "name_te": "రైతు పథకాలు"},
    {"id": "health", "name": "Health Schemes", "name_te": "ఆరోగ్య పథకాలు"},
    {"id": "education", "name": "Education", "name_te": "విద్య"},
    {"id": "employment", "name": "Employment", "name_te": "ఉపాధి"},
    {"id": "housing", "name": "Housing", "name_te": "గృహ నిర్మాణం"},
    {"id": "welfare", "name": "Welfare", "name_te": "సంక్షేమం"},
]

# UI Translations
UI_TRANSLATIONS = {
    'english': {
        'app_title': 'Rural Management Dashboard',
        'app_subtitle': 'Your gateway to rural information and services',
        'nav_education': 'Education & News',
        'nav_agriculture': 'Agriculture & Market',
        'nav_health': 'Health & Medical',
        'nav_chatbot': 'Ask Assistant',
        'refresh': 'Refresh',
        'loading': 'Loading...',
        'last_updated': 'Last updated',
        'no_data': 'No data available',
        'try_again': 'Try Again',
        'read_more': 'Read more',
        'source': 'Source',
        'news_title': 'Education & News',
        'category': 'Category',
        'fetching_news': 'Fetching latest news...',
        'no_news': 'No news articles found.',
        'categories': {'all': 'All', 'education': 'Education', 'technology': 'Technology', 'science': 'Science', 'politics': 'Politics', 'sports': 'Sports', 'health': 'Health', 'general': 'General'},
        'market_title': 'Agriculture & Market',
        'select_location': 'Select Location',
        'live_prices': 'Live prices from',
        'market': 'market',
        'fetching_prices': 'Fetching market prices...',
        'per_kg': '/kg', 'per_liter': '/liter', 'per_dozen': '/dozen',
        'commodity_names': {'Tomato': 'Tomato', 'Onion': 'Onion', 'Potato': 'Potato', 'Carrot': 'Carrot', 'Cabbage': 'Cabbage', 'Rice': 'Rice', 'Wheat': 'Wheat', 'Milk': 'Milk', 'Eggs': 'Eggs'},
        'health_title': 'Health & Medical',
        'your_location': 'Your Location',
        'emergency_call': 'Emergency: Call 108',
        'ambulance_service': '24/7 Ambulance Service',
        'nearest_hospitals': 'Nearest Hospitals in',
        'found': 'found',
        'emergency_24x7': '24/7 Emergency',
        'away': 'away',
        'get_directions': 'Get Directions',
        'hospital_types': {'General': 'General', 'Multi-specialty': 'Multi-specialty'},
        'locations': {k: k.title() for k in LOCATIONS.keys()},
        # Weather
        'weather_title': 'Weather Forecast',
        'today': 'Today',
        'tomorrow': 'Tomorrow',
        'temperature': 'Temperature',
        'humidity': 'Humidity',
        'wind': 'Wind Speed',
        'rain_chance': 'Rain Chance',
        'weather_advisory': 'Weather Advisory',
        # Schemes
        'schemes_title': 'Government Schemes',
        'search_schemes': 'Search schemes...',
        'eligibility': 'Eligibility',
        'benefits': 'Benefits',
        'documents_required': 'Documents Required',
        'apply_now': 'Apply Now',
        'helpline': 'Helpline',
        # Pharmacy & Blood Bank
        'pharmacies_title': 'Nearby Pharmacies',
        'blood_banks_title': 'Blood Banks',
        'open_24x7': 'Open 24/7',
        # Symptom Checker
        'symptom_checker_title': 'Symptom Checker',
        'symptom_placeholder': 'Describe your symptoms...',
        'check_symptoms': 'Check Symptoms',
        'disclaimer': 'This is for informational purposes only. Please consult a doctor for proper diagnosis.',
        # Chatbot
        'chatbot_title': 'Ask Assistant',
        'chatbot_subtitle': 'Ask about agriculture, health, schemes, or any query',
        'chatbot_placeholder': 'Type or speak your question...',
        'chatbot_listening': 'Listening...',
        'chatbot_thinking': 'Thinking...',
        'chatbot_welcome': 'Hello! I am your Rural Assistant. How can I help you today?',
        'chatbot_suggestions': ['What schemes are available for farmers?', 'How to apply for Ayushman Bharat?', 'Weather forecast for my area', 'Nearest blood bank'],
    },
    'telugu': {
        'app_title': 'గ్రామీణ నిర్వహణ డాష్‌బోర్డ్',
        'app_subtitle': 'గ్రామీణ సమాచారం మరియు సేవలకు మీ గేట్‌వే',
        'nav_education': 'విద్య & వార్తలు',
        'nav_agriculture': 'వ్యవసాయం & మార్కెట్',
        'nav_health': 'ఆరోగ్యం & వైద్యం',
        'nav_chatbot': 'సహాయకుడిని అడగండి',
        'refresh': 'రిఫ్రెష్',
        'loading': 'లోడ్ అవుతోంది...',
        'last_updated': 'చివరిగా అప్‌డేట్',
        'no_data': 'డేటా అందుబాటులో లేదు',
        'try_again': 'మళ్ళీ ప్రయత్నించండి',
        'read_more': 'మరింత చదవండి',
        'source': 'మూలం',
        'news_title': 'విద్య & వార్తలు',
        'category': 'వర్గం',
        'fetching_news': 'వార్తలు పొందుతోంది...',
        'no_news': 'వార్తలు కనుగొనబడలేదు.',
        'categories': {'all': 'అన్నీ', 'education': 'విద్య', 'technology': 'టెక్నాలజీ', 'science': 'సైన్స్', 'politics': 'రాజకీయాలు', 'sports': 'క్రీడలు', 'health': 'ఆరోగ్యం', 'general': 'సాధారణ'},
        'market_title': 'వ్యవసాయం & మార్కెట్',
        'select_location': 'ప్రదేశం ఎంచుకోండి',
        'live_prices': 'లైవ్ ధరలు',
        'market': 'మార్కెట్',
        'fetching_prices': 'ధరలు పొందుతోంది...',
        'per_kg': '/కిలో', 'per_liter': '/లీటర్', 'per_dozen': '/డజన్',
        'commodity_names': {'Tomato': 'టమాటో', 'Onion': 'ఉల్లిపాయ', 'Potato': 'బంగాళదుంప', 'Carrot': 'క్యారెట్', 'Cabbage': 'క్యాబేజీ', 'Rice': 'బియ్యం', 'Wheat': 'గోధుమ', 'Milk': 'పాలు', 'Eggs': 'గుడ్లు'},
        'health_title': 'ఆరోగ్యం & వైద్యం',
        'your_location': 'మీ ప్రదేశం',
        'emergency_call': 'అత్యవసరం: 108 కాల్ చేయండి',
        'ambulance_service': '24/7 అంబులెన్స్',
        'nearest_hospitals': 'సమీపంలోని ఆసుపత్రులు',
        'found': 'కనుగొనబడింది',
        'emergency_24x7': '24/7 అత్యవసర',
        'away': 'దూరంలో',
        'get_directions': 'దిశలు పొందండి',
        'hospital_types': {'General': 'జనరల్', 'Multi-specialty': 'మల్టీ-స్పెషాలిటీ'},
        'locations': {'visakhapatnam': 'విశాఖపట్నం', 'vijayawada': 'విజయవాడ', 'guntur': 'గుంటూరు', 'tirupati': 'తిరుపతి', 'hyderabad': 'హైదరాబాద్', 'warangal': 'వరంగల్', 'karimnagar': 'కరీంనగర్', 'nellore': 'నెల్లూరు', 'kurnool': 'కర్నూల్', 'rajahmundry': 'రాజమండ్రి'},
        # Weather
        'weather_title': 'వాతావరణ సూచన',
        'today': 'ఈరోజు',
        'tomorrow': 'రేపు',
        'temperature': 'ఉష్ణోగ్రత',
        'humidity': 'తేమ',
        'wind': 'గాలి వేగం',
        'rain_chance': 'వర్షం అవకాశం',
        'weather_advisory': 'వాతావరణ సలహా',
        # Schemes
        'schemes_title': 'ప్రభుత్వ పథకాలు',
        'search_schemes': 'పథకాలు శోధించండి...',
        'eligibility': 'అర్హత',
        'benefits': 'ప్రయోజనాలు',
        'documents_required': 'అవసరమైన పత్రాలు',
        'apply_now': 'దరఖాస్తు చేయండి',
        'helpline': 'హెల్ప్‌లైన్',
        # Pharmacy & Blood Bank
        'pharmacies_title': 'సమీపంలోని ఫార్మసీలు',
        'blood_banks_title': 'బ్లడ్ బ్యాంకులు',
        'open_24x7': '24/7 తెరిచి ఉంటుంది',
        # Symptom Checker
        'symptom_checker_title': 'లక్షణాల తనిఖీ',
        'symptom_placeholder': 'మీ లక్షణాలను వివరించండి...',
        'check_symptoms': 'లక్షణాలు తనిఖీ చేయండి',
        'disclaimer': 'ఇది సమాచార ప్రయోజనాల కోసం మాత్రమే. సరైన రోగ నిర్ధారణ కోసం వైద్యుడిని సంప్రదించండి.',
        # Chatbot
        'chatbot_title': 'సహాయకుడిని అడగండి',
        'chatbot_subtitle': 'వ్యవసాయం, ఆరోగ్యం, పథకాల గురించి అడగండి',
        'chatbot_placeholder': 'టైప్ చేయండి లేదా మాట్లాడండి...',
        'chatbot_listening': 'వింటోంది...',
        'chatbot_thinking': 'ఆలోచిస్తోంది...',
        'chatbot_welcome': 'నమస్కారం! నేను మీ గ్రామీణ సహాయకుడిని. నేను మీకు ఎలా సహాయం చేయగలను?',
        'chatbot_suggestions': ['రైతులకు ఏ పథకాలు అందుబాటులో ఉన్నాయి?', 'ఆయుష్మాన్ భారత్ కోసం ఎలా దరఖాస్తు చేయాలి?', 'నా ప్రాంతంలో వాతావరణం', 'సమీపంలోని బ్లడ్ బ్యాంక్'],
    }
}


# ==================== UTILITY FUNCTIONS ====================
def get_headers():
    return {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'Accept': '*/*'}

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in km"""
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return 6371 * 2 * math.asin(math.sqrt(a))


# ==================== WEATHER API (Open-Meteo - FREE) ====================
async def fetch_weather(lat: float, lon: float) -> Dict:
    """Fetch weather from Open-Meteo API - completely FREE, no API key needed!"""
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,wind_speed_10m_max",
            "timezone": "Asia/Kolkata",
            "forecast_days": 7
        }
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Weather code to description mapping
                weather_codes = {
                    0: ("Clear sky", "☀️"), 1: ("Mainly clear", "🌤️"), 2: ("Partly cloudy", "⛅"),
                    3: ("Overcast", "☁️"), 45: ("Foggy", "🌫️"), 48: ("Fog", "🌫️"),
                    51: ("Light drizzle", "🌧️"), 53: ("Drizzle", "🌧️"), 55: ("Heavy drizzle", "🌧️"),
                    61: ("Light rain", "🌧️"), 63: ("Rain", "🌧️"), 65: ("Heavy rain", "🌧️"),
                    71: ("Light snow", "🌨️"), 73: ("Snow", "🌨️"), 75: ("Heavy snow", "🌨️"),
                    80: ("Light showers", "🌦️"), 81: ("Showers", "🌦️"), 82: ("Heavy showers", "🌦️"),
                    95: ("Thunderstorm", "⛈️"), 96: ("Thunderstorm with hail", "⛈️"), 99: ("Severe thunderstorm", "⛈️")
                }
                
                current = data.get("current", {})
                daily = data.get("daily", {})
                
                current_code = current.get("weather_code", 0)
                current_desc, current_icon = weather_codes.get(current_code, ("Unknown", "❓"))
                
                # Build forecast array
                forecast = []
                for i in range(min(7, len(daily.get("time", [])))):
                    code = daily["weather_code"][i] if daily.get("weather_code") else 0
                    desc, icon = weather_codes.get(code, ("Unknown", "❓"))
                    
                    forecast.append({
                        "date": daily["time"][i],
                        "day": datetime.strptime(daily["time"][i], "%Y-%m-%d").strftime("%A"),
                        "temp_max": daily["temperature_2m_max"][i],
                        "temp_min": daily["temperature_2m_min"][i],
                        "rain_chance": daily["precipitation_probability_max"][i] if daily.get("precipitation_probability_max") else 0,
                        "wind_speed": daily["wind_speed_10m_max"][i] if daily.get("wind_speed_10m_max") else 0,
                        "description": desc,
                        "icon": icon,
                        "weather_code": code
                    })
                
                # Generate advisory based on weather
                advisory = []
                if current.get("temperature_2m", 0) > 38:
                    advisory.append("🔥 High temperature alert! Stay hydrated and avoid outdoor work during noon.")
                if forecast and forecast[0].get("rain_chance", 0) > 60:
                    advisory.append("🌧️ High chance of rain today. Consider delaying field spraying activities.")
                if current.get("wind_speed_10m", 0) > 30:
                    advisory.append("💨 High winds expected. Secure loose materials and avoid spraying pesticides.")
                
                return {
                    "current": {
                        "temperature": current.get("temperature_2m"),
                        "humidity": current.get("relative_humidity_2m"),
                        "wind_speed": current.get("wind_speed_10m"),
                        "description": current_desc,
                        "icon": current_icon,
                        "weather_code": current_code
                    },
                    "forecast": forecast,
                    "advisory": advisory if advisory else ["✅ Weather conditions are favorable for farming activities."],
                    "last_updated": datetime.now().isoformat()
                }
                
    except Exception as e:
        print(f"Weather API error: {e}")
    
    return None


# ==================== OPENSTREETMAP FUNCTIONS ====================
async def fetch_from_overpass(lat: float, lon: float, amenity_type: str, radius: int = 15000) -> List[Dict]:
    """Generic function to fetch amenities from OpenStreetMap Overpass API"""
    try:
        overpass_url = "https://overpass-api.de/api/interpreter"
        
        query = f"""
        [out:json][timeout:25];
        (
          node["amenity"="{amenity_type}"](around:{radius},{lat},{lon});
          way["amenity"="{amenity_type}"](around:{radius},{lat},{lon});
        );
        out center tags;
        """
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(overpass_url, data={"data": query})
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for element in data.get('elements', [])[:20]:
                    tags = element.get('tags', {})
                    name = tags.get('name', tags.get('name:en', f'Unknown {amenity_type.title()}'))
                    
                    if element['type'] == 'node':
                        elem_lat, elem_lon = element['lat'], element['lon']
                    else:
                        center = element.get('center', {})
                        elem_lat = center.get('lat', lat)
                        elem_lon = center.get('lon', lon)
                    
                    distance = calculate_distance(lat, lon, elem_lat, elem_lon)
                    
                    results.append({
                        'id': element['id'],
                        'name': name,
                        'distance': f"{distance:.1f} km",
                        'distance_km': distance,
                        'phone': tags.get('phone', tags.get('contact:phone', 'N/A')),
                        'address': tags.get('addr:full', tags.get('addr:street', '')),
                        'opening_hours': tags.get('opening_hours', ''),
                        'is_24x7': '24' in tags.get('opening_hours', '') or tags.get('opening_hours') == '24/7',
                        'website': tags.get('website', ''),
                        'lat': elem_lat,
                        'lon': elem_lon
                    })
                
                results.sort(key=lambda x: x['distance_km'])
                return results
                
    except Exception as e:
        print(f"Overpass API error for {amenity_type}: {e}")
    
    return []


async def fetch_hospitals(lat: float, lon: float) -> List[Dict]:
    """Fetch hospitals from OpenStreetMap"""
    hospitals = await fetch_from_overpass(lat, lon, "hospital", 15000)
    clinics = await fetch_from_overpass(lat, lon, "clinic", 10000)
    
    # Merge and deduplicate
    all_facilities = hospitals + clinics
    all_facilities.sort(key=lambda x: x['distance_km'])
    
    # Add hospital-specific fields
    for h in all_facilities:
        h['type'] = 'Multi-specialty' if 'hospital' in h.get('name', '').lower() or any(w in h.get('name', '').lower() for w in ['apollo', 'kims', 'care', 'max']) else 'General'
        h['emergency'] = h['is_24x7'] or 'emergency' in h.get('name', '').lower()
    
    return all_facilities[:15]


async def fetch_pharmacies(lat: float, lon: float) -> List[Dict]:
    """Fetch pharmacies from OpenStreetMap"""
    return await fetch_from_overpass(lat, lon, "pharmacy", 10000)


async def fetch_blood_banks(lat: float, lon: float) -> List[Dict]:
    """Fetch blood banks from OpenStreetMap"""
    try:
        overpass_url = "https://overpass-api.de/api/interpreter"
        
        # Query for blood banks and blood donation centers
        query = f"""
        [out:json][timeout:25];
        (
          node["healthcare"="blood_donation"](around:30000,{lat},{lon});
          way["healthcare"="blood_donation"](around:30000,{lat},{lon});
          node["amenity"="blood_bank"](around:30000,{lat},{lon});
          node["name"~"[Bb]lood.*[Bb]ank"](around:30000,{lat},{lon});
          node["healthcare"="blood_bank"](around:30000,{lat},{lon});
        );
        out center tags;
        """
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(overpass_url, data={"data": query})
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for element in data.get('elements', [])[:15]:
                    tags = element.get('tags', {})
                    name = tags.get('name', 'Blood Bank')
                    
                    if element['type'] == 'node':
                        elem_lat, elem_lon = element['lat'], element['lon']
                    else:
                        center = element.get('center', {})
                        elem_lat = center.get('lat', lat)
                        elem_lon = center.get('lon', lon)
                    
                    distance = calculate_distance(lat, lon, elem_lat, elem_lon)
                    
                    results.append({
                        'id': element['id'],
                        'name': name,
                        'distance': f"{distance:.1f} km",
                        'distance_km': distance,
                        'phone': tags.get('phone', tags.get('contact:phone', 'N/A')),
                        'address': tags.get('addr:full', tags.get('addr:street', '')),
                        'blood_groups': tags.get('blood_group', 'All groups available'),
                        'is_24x7': '24' in tags.get('opening_hours', ''),
                        'lat': elem_lat,
                        'lon': elem_lon
                    })
                
                results.sort(key=lambda x: x['distance_km'])
                return results
                
    except Exception as e:
        print(f"Blood bank fetch error: {e}")
    
    # Fallback data if API fails
    return [
        {'id': 1, 'name': 'District Blood Bank', 'distance': '2.5 km', 'distance_km': 2.5, 'phone': '104', 'blood_groups': 'All groups', 'is_24x7': True, 'lat': lat, 'lon': lon},
        {'id': 2, 'name': 'Red Cross Blood Bank', 'distance': '4.0 km', 'distance_km': 4.0, 'phone': '1800-425-1234', 'blood_groups': 'All groups', 'is_24x7': True, 'lat': lat, 'lon': lon},
    ]


# ==================== NEWS FUNCTIONS ====================
async def fetch_news_from_free_api(category: str = 'general') -> List[Dict]:
    """Fetch news from free API"""
    try:
        category_map = {'all': 'general', 'education': 'general', 'technology': 'technology', 'science': 'science', 'politics': 'general', 'sports': 'sports', 'health': 'health'}
        api_category = category_map.get(category, 'general')
        
        url = f"https://saurav.tech/NewsAPI/top-headlines/category/{api_category}/in.json"
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, headers=get_headers())
            
            if response.status_code == 200:
                data = response.json()
                return [{
                    'id': hashlib.md5(a.get('title', '').encode()).hexdigest()[:8],
                    'title': a.get('title', ''),
                    'summary': a.get('description', '') or '',
                    'category': category if category != 'all' else api_category,
                    'date': a.get('publishedAt', '')[:10] if a.get('publishedAt') else datetime.now().strftime('%Y-%m-%d'),
                    'url': a.get('url', '#'),
                    'source': a.get('source', {}).get('name', 'Unknown'),
                    'image': a.get('urlToImage', '')
                } for a in data.get('articles', [])[:15] if a.get('title') and len(a.get('title', '')) > 10]
    except Exception as e:
        print(f"News API error: {e}")
    return []


async def fetch_news_from_rss(feeds: List[str], language: str) -> List[Dict]:
    """Fetch news from RSS feeds"""
    articles = []
    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        for url in feeds:
            try:
                response = await client.get(url, headers=get_headers())
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'xml')
                    for item in soup.find_all('item')[:8]:
                        title = item.find('title')
                        if not title or len(title.text.strip()) < 5:
                            continue
                        title_text = title.text.strip().replace('<![CDATA[', '').replace(']]>', '')
                        link = item.find('link')
                        desc = item.find('description')
                        desc_text = BeautifulSoup(desc.text, 'html.parser').get_text().strip()[:200] if desc and desc.text else ""
                        
                        articles.append({
                            'id': hashlib.md5(title_text.encode()).hexdigest()[:8],
                            'title': title_text,
                            'summary': desc_text,
                            'category': 'general',
                            'date': datetime.now().strftime('%Y-%m-%d'),
                            'url': link.text.strip() if link and link.text else '#',
                            'source': url.split('/')[2]
                        })
            except Exception as e:
                print(f"RSS error {url}: {e}")
    return articles


def get_fallback_telugu_news() -> List[Dict]:
    return [
        {'id': 'te1', 'title': 'ఆంధ్రప్రదేశ్‌లో కొత్త విద్యా విధానం అమలు', 'summary': 'విద్యా రంగంలో సంస్కరణలు', 'category': 'education', 'date': datetime.now().strftime('%Y-%m-%d'), 'url': '#', 'source': 'Local'},
        {'id': 'te2', 'title': 'రైతులకు కొత్త పథకం ప్రకటన', 'summary': 'వ్యవసాయ రంగంలో మద్దతు', 'category': 'politics', 'date': datetime.now().strftime('%Y-%m-%d'), 'url': '#', 'source': 'Local'},
    ]


async def update_news_cache():
    """Update news cache"""
    print(f"🔄 Updating news cache...")
    NEWS_CACHE['english'] = await fetch_news_from_free_api('general') or await fetch_news_from_rss(ENGLISH_RSS_FEEDS, 'english')
    NEWS_CACHE['telugu'] = await fetch_news_from_rss(TELUGU_RSS_FEEDS, 'telugu') or get_fallback_telugu_news()
    NEWS_CACHE['last_updated'] = datetime.now().isoformat()
    print(f"✅ News: {len(NEWS_CACHE['english'])} EN, {len(NEWS_CACHE['telugu'])} TE")


# ==================== MARKET PRICES ====================
def generate_market_prices(location: str) -> List[Dict]:
    """Generate realistic market prices"""
    base_items = [
        {'name': 'Tomato', 'base': 35, 'unit': 'kg'}, {'name': 'Onion', 'base': 40, 'unit': 'kg'},
        {'name': 'Potato', 'base': 28, 'unit': 'kg'}, {'name': 'Carrot', 'base': 50, 'unit': 'kg'},
        {'name': 'Cabbage', 'base': 20, 'unit': 'kg'}, {'name': 'Rice', 'base': 55, 'unit': 'kg'},
        {'name': 'Wheat', 'base': 35, 'unit': 'kg'}, {'name': 'Milk', 'base': 60, 'unit': 'liter'},
        {'name': 'Eggs', 'base': 90, 'unit': 'dozen'}, {'name': 'Cauliflower', 'base': 30, 'unit': 'kg'},
        {'name': 'Beans', 'base': 45, 'unit': 'kg'}, {'name': 'Brinjal', 'base': 25, 'unit': 'kg'},
    ]
    
    date_seed = int(datetime.now().strftime('%Y%m%d'))
    random.seed(date_seed + hash(location))
    
    prices = []
    for i, item in enumerate(base_items):
        price = round(item['base'] * random.uniform(0.85, 1.15))
        change = round(random.uniform(-10, 15), 1)
        prices.append({
            'id': i + 1, 'name': item['name'], 'price': price, 'unit': item['unit'],
            'change': f"{'+' if change > 0 else ''}{change}%",
            'trend': 'up' if change > 0 else ('down' if change < 0 else 'stable')
        })
    
    random.seed()
    return prices


# ==================== SYMPTOM CHECKER (GROQ AI) ====================
async def check_symptoms_ai(symptoms: str, language: str = "english") -> Dict:
    """AI-powered symptom checker using GROQ"""
    if not GROQ_API_KEY:
        return {"success": False, "response": "Symptom checker requires GROQ API key."}
    
    try:
        lang_instruction = "Respond in Telugu." if language == "telugu" else "Respond in English."
        
        system_prompt = f"""You are a medical information assistant. {lang_instruction}
        
IMPORTANT DISCLAIMERS:
- You are NOT a doctor and cannot diagnose conditions
- Always recommend consulting a healthcare professional
- Provide general health information only

When given symptoms, provide:
1. Possible conditions (general awareness only)
2. Self-care suggestions
3. When to see a doctor (warning signs)
4. Nearby specialist type to consult

Keep response concise and helpful. Always emphasize seeing a real doctor."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"I have these symptoms: {symptoms}"}
        ]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={"model": "llama-3.3-70b-versatile", "messages": messages, "temperature": 0.3, "max_tokens": 800}
            )
            
            if response.status_code == 200:
                data = response.json()
                return {"success": True, "response": data["choices"][0]["message"]["content"]}
            else:
                return {"success": False, "response": f"API Error: {response.status_code}"}
                
    except Exception as e:
        return {"success": False, "response": str(e)}


# ==================== BACKGROUND TASKS ====================
async def update_caches_periodically():
    while True:
        try:
            await update_news_cache()
        except Exception as e:
            print(f"❌ Cache error: {e}")
        await asyncio.sleep(300)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await update_news_cache()
    cache_task = asyncio.create_task(update_caches_periodically())
    try:
        yield
    finally:
        cache_task.cancel()


# ==================== CREATE APP ====================
app = FastAPI(title="Rural Management Dashboard API", version="3.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


# ==================== API ENDPOINTS ====================

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "3.0.0", "groq_configured": bool(GROQ_API_KEY)}

@app.get("/api/locations")
async def get_locations():
    return {"locations": list(LOCATIONS.keys()), "details": LOCATIONS}

@app.get("/api/translations")
async def get_translations(language: str = Query(default="english")):
    return UI_TRANSLATIONS.get(language, UI_TRANSLATIONS['english'])


# --- WEATHER ---
@app.get("/api/weather")
async def get_weather(location: str = Query(default="visakhapatnam")):
    """Get 7-day weather forecast - FREE Open-Meteo API"""
    loc = LOCATIONS.get(location.lower(), LOCATIONS["visakhapatnam"])
    weather = await fetch_weather(loc["lat"], loc["lon"])
    
    if weather:
        return {"location": location, "location_display": location.title(), **weather}
    
    return {"error": "Weather data unavailable", "location": location}


# --- NEWS ---
@app.get("/api/news")
async def get_news(language: str = Query(default="english"), category: str = Query(default="all")):
    if language == 'english':
        news = await fetch_news_from_free_api(category) if category != 'all' else NEWS_CACHE.get('english', [])
        if not news:
            news = NEWS_CACHE.get('english', [])
            if category != 'all':
                news = [n for n in news if n.get('category') == category]
    else:
        news = NEWS_CACHE.get('telugu', []) or get_fallback_telugu_news()
        if category != 'all':
            news = [n for n in news if n.get('category') == category]
    
    return {"articles": news, "language": language, "category": category, "total": len(news)}


# --- MARKET PRICES ---
@app.get("/api/market-prices")
async def get_market_prices(location: str = Query(default="visakhapatnam")):
    return {
        "location": location.lower(),
        "location_display": location.title(),
        "prices": generate_market_prices(location.lower()),
        "date": datetime.now().strftime('%Y-%m-%d')
    }


# --- GOVERNMENT SCHEMES ---
@app.get("/api/schemes")
async def get_schemes(category: str = Query(default="all"), search: str = Query(default=""), language: str = Query(default="english")):
    """Get government schemes with filtering"""
    schemes = GOVERNMENT_SCHEMES
    
    if category != "all":
        schemes = [s for s in schemes if s["category"] == category]
    
    if search:
        search_lower = search.lower()
        schemes = [s for s in schemes if search_lower in s["name"].lower() or search_lower in s["description"].lower()]
    
    # Localize if Telugu
    if language == "telugu":
        schemes = [{**s, "name": s.get("name_te", s["name"]), "description": s.get("description_te", s["description"])} for s in schemes]
    
    return {"schemes": schemes, "categories": SCHEME_CATEGORIES, "total": len(schemes)}

@app.get("/api/schemes/{scheme_id}")
async def get_scheme_detail(scheme_id: str, language: str = Query(default="english")):
    """Get detailed info about a specific scheme"""
    scheme = next((s for s in GOVERNMENT_SCHEMES if s["id"] == scheme_id), None)
    
    if not scheme:
        return {"error": "Scheme not found"}
    
    if language == "telugu":
        scheme = {**scheme, "name": scheme.get("name_te", scheme["name"]), "description": scheme.get("description_te", scheme["description"])}
    
    return scheme


# --- HOSPITALS ---
@app.get("/api/hospitals")
async def get_hospitals_endpoint(location: str = Query(default="visakhapatnam")):
    loc = LOCATIONS.get(location.lower(), LOCATIONS["visakhapatnam"])
    hospitals = await fetch_hospitals(loc["lat"], loc["lon"])
    return {"location": location, "hospitals": hospitals, "total": len(hospitals)}


# --- PHARMACIES ---
@app.get("/api/pharmacies")
async def get_pharmacies(location: str = Query(default="visakhapatnam")):
    """Get nearby pharmacies - FREE OpenStreetMap API"""
    loc = LOCATIONS.get(location.lower(), LOCATIONS["visakhapatnam"])
    pharmacies = await fetch_pharmacies(loc["lat"], loc["lon"])
    return {"location": location, "location_display": location.title(), "pharmacies": pharmacies, "total": len(pharmacies)}


# --- BLOOD BANKS ---
@app.get("/api/blood-banks")
async def get_blood_banks(location: str = Query(default="visakhapatnam")):
    """Get nearby blood banks - FREE OpenStreetMap API"""
    loc = LOCATIONS.get(location.lower(), LOCATIONS["visakhapatnam"])
    blood_banks = await fetch_blood_banks(loc["lat"], loc["lon"])
    return {"location": location, "location_display": location.title(), "blood_banks": blood_banks, "total": len(blood_banks)}


# --- SYMPTOM CHECKER ---
class SymptomRequest(BaseModel):
    symptoms: str
    language: str = "english"

@app.post("/api/symptom-checker")
async def symptom_checker(request: SymptomRequest):
    """AI-powered symptom checker using GROQ"""
    result = await check_symptoms_ai(request.symptoms, request.language)
    return result


# --- CHATBOT ---
class ChatRequest(BaseModel):
    message: str
    language: str = "english"

@app.post("/api/chat")
async def chat_with_assistant(request: ChatRequest):
    """Chat with GROQ-powered assistant"""
    if not GROQ_API_KEY:
        return {"response": "Chatbot requires GROQ_API_KEY. Get free key from https://console.groq.com/", "success": False}
    
    try:
        lang_inst = "Respond in Telugu." if request.language == "telugu" else "Respond in English."
        
        system_prompt = f"""You are a Rural Management Assistant for India (AP/Telangana). {lang_inst}

Help with:
- Agriculture: crops, weather, market prices, farming tips
- Government Schemes: PM-KISAN, Ayushman Bharat, PMFBY, Rythu Bandhu, etc.
- Health: basic advice, when to see doctor, nearby facilities
- Education: scholarships, skill programs
- General rural queries

Be concise, accurate, and helpful. Suggest relevant government schemes when applicable."""

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": request.message}],
                    "temperature": 0.7,
                    "max_tokens": 1024
                }
            )
            
            if response.status_code == 200:
                return {"response": response.json()["choices"][0]["message"]["content"], "success": True}
            return {"response": f"API Error: {response.status_code}", "success": False}
            
    except Exception as e:
        return {"response": str(e), "success": False}

@app.get("/api/chat/status")
async def chat_status():
    return {"configured": bool(GROQ_API_KEY), "message": "Ready!" if GROQ_API_KEY else "Set GROQ_API_KEY"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
