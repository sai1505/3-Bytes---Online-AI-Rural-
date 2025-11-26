import React, { useState, useEffect, createContext, useContext, useRef } from 'react';
import { Globe, TrendingUp, Heart, ChevronRight, MapPin, Calendar, RefreshCw, Loader2, ExternalLink, Languages, MessageCircle, Mic, MicOff, Send, Bot, User, Cloud, Droplets, Wind, Sun, Thermometer, Search, FileText, Phone, Clock, Pill, Activity, AlertCircle } from 'lucide-react';

const API_BASE = 'http://localhost:8000';
const LanguageContext = createContext();
const useLanguage = () => useContext(LanguageContext);

// Main App
export default function App() {
  const [activePage, setActivePage] = useState('education');
  const [language, setLanguage] = useState('english');
  const [translations, setTranslations] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE}/api/translations?language=${language}`)
      .then(r => r.json())
      .then(setTranslations)
      .catch(() => setTranslations({}))
      .finally(() => setLoading(false));
  }, [language]);

  const t = translations || {};
  const pages = [
    { id: 'education', name: t.nav_education || 'Education & News', icon: Globe },
    { id: 'agriculture', name: t.nav_agriculture || 'Agriculture & Market', icon: TrendingUp },
    { id: 'health', name: t.nav_health || 'Health & Medical', icon: Heart },
    { id: 'chatbot', name: t.nav_chatbot || 'Ask Assistant', icon: MessageCircle }
  ];

  if (loading) return <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center"><Loader2 className="w-10 h-10 text-emerald-400 animate-spin" /></div>;

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        {/* Header */}
        <header className="bg-slate-800/80 backdrop-blur-md border-b border-slate-700 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 py-3 flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">{t.app_title || 'Rural Management Dashboard'}</h1>
              <p className="text-slate-400 text-sm">{t.app_subtitle || 'Your gateway to rural services'}</p>
            </div>
            <div className="flex items-center gap-3">
              <Languages className="w-5 h-5 text-slate-400" />
              <select value={language} onChange={e => setLanguage(e.target.value)} className="bg-slate-700 text-white px-3 py-2 rounded-lg border border-slate-600 focus:ring-2 focus:ring-emerald-500">
                <option value="english">English</option>
                <option value="telugu">తెలుగు</option>
              </select>
            </div>
          </div>
        </header>

        {/* Navigation */}
        <nav className="bg-slate-800/50 backdrop-blur border-b border-slate-700">
          <div className="max-w-7xl mx-auto px-4 py-2 flex gap-2 overflow-x-auto">
            {pages.map(p => (
              <button key={p.id} onClick={() => setActivePage(p.id)} className={`flex items-center gap-2 px-5 py-2.5 rounded-lg font-medium transition-all whitespace-nowrap ${activePage === p.id ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-white shadow-lg shadow-emerald-500/25' : 'text-slate-300 hover:bg-slate-700'}`}>
                <p.icon className="w-5 h-5" />{p.name}
              </button>
            ))}
          </div>
        </nav>

        {/* Content */}
        <main className="max-w-7xl mx-auto px-4 py-6">
          {activePage === 'education' && <EducationNews />}
          {activePage === 'agriculture' && <AgricultureMarket />}
          {activePage === 'health' && <HealthMedical />}
          {activePage === 'chatbot' && <ChatBot />}
        </main>
      </div>
    </LanguageContext.Provider>
  );
}

// Reusable Components
const Card = ({ children, className = '' }) => <div className={`bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl ${className}`}>{children}</div>;
const LoadingSpinner = ({ msg }) => <div className="flex flex-col items-center py-12"><Loader2 className="w-8 h-8 text-emerald-400 animate-spin mb-3" /><p className="text-slate-400">{msg}</p></div>;

// Education & News
function EducationNews() {
  const { language, t } = useLanguage();
  const [category, setCategory] = useState('all');
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const categories = ['all', 'education', 'technology', 'science', 'politics', 'sports', 'health'];

  const fetchNews = () => {
    setLoading(true);
    fetch(`${API_BASE}/api/news?language=${language}&category=${category}`)
      .then(r => r.json())
      .then(d => setNews(d.articles || []))
      .catch(() => setNews([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchNews(); }, [language, category]);

  return (
    <Card className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-white">{t.news_title || 'Education & News'}</h2>
        <button onClick={fetchNews} className="flex items-center gap-2 px-4 py-2 bg-emerald-500/20 text-emerald-400 rounded-lg hover:bg-emerald-500/30"><RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />{t.refresh}</button>
      </div>
      
      <div className="mb-6">
        <select value={category} onChange={e => setCategory(e.target.value)} className="w-full md:w-64 bg-slate-700 text-white px-4 py-2 rounded-lg border border-slate-600">
          {categories.map(c => <option key={c} value={c}>{t.categories?.[c] || c.charAt(0).toUpperCase() + c.slice(1)}</option>)}
        </select>
      </div>

      {loading ? <LoadingSpinner msg={t.fetching_news} /> : news.length === 0 ? <p className="text-center text-slate-400 py-8">{t.no_news}</p> : (
        <div className="grid gap-4 md:grid-cols-2">
          {news.map((n, i) => (
            <div key={n.id || i} className="bg-slate-700/50 rounded-lg p-4 hover:bg-slate-700 transition-colors">
              <div className="flex justify-between items-start mb-2">
                <h3 className="font-semibold text-white flex-1 pr-2">{n.title}</h3>
                <span className="text-xs bg-emerald-500/20 text-emerald-400 px-2 py-1 rounded">{t.categories?.[n.category] || n.category}</span>
              </div>
              {n.summary && <p className="text-slate-400 text-sm mb-2 line-clamp-2">{n.summary}</p>}
              <div className="flex justify-between items-center text-xs text-slate-500">
                <span className="flex items-center gap-1"><Calendar className="w-3 h-3" />{n.date}</span>
                {n.url !== '#' && <a href={n.url} target="_blank" rel="noopener noreferrer" className="text-emerald-400 hover:text-emerald-300 flex items-center gap-1">{t.read_more}<ExternalLink className="w-3 h-3" /></a>}
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}

// Agriculture & Market (with Weather & Schemes)
function AgricultureMarket() {
  const { language, t } = useLanguage();
  const [location, setLocation] = useState('visakhapatnam');
  const [activeTab, setActiveTab] = useState('prices');
  const locations = Object.keys(useLanguage().t.locations || {}).length > 0 ? Object.keys(t.locations) : ['visakhapatnam', 'vijayawada', 'guntur', 'tirupati', 'hyderabad', 'warangal', 'karimnagar', 'nellore', 'kurnool', 'rajahmundry'];

  const tabs = [
    { id: 'prices', name: language === 'telugu' ? 'మార్కెట్ ధరలు' : 'Market Prices', icon: TrendingUp },
    { id: 'weather', name: language === 'telugu' ? 'వాతావరణం' : 'Weather', icon: Cloud },
    { id: 'schemes', name: language === 'telugu' ? 'పథకాలు' : 'Schemes', icon: FileText }
  ];

  return (
    <div className="space-y-4">
      {/* Location Selector */}
      <Card className="p-4">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2">
            <MapPin className="w-5 h-5 text-emerald-400" />
            <select value={location} onChange={e => setLocation(e.target.value)} className="bg-slate-700 text-white px-4 py-2 rounded-lg border border-slate-600">
              {locations.map(l => <option key={l} value={l}>{t.locations?.[l] || l.charAt(0).toUpperCase() + l.slice(1)}</option>)}
            </select>
          </div>
          <div className="flex gap-2">
            {tabs.map(tab => (
              <button key={tab.id} onClick={() => setActiveTab(tab.id)} className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${activeTab === tab.id ? 'bg-emerald-500 text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}`}>
                <tab.icon className="w-4 h-4" />{tab.name}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {activeTab === 'prices' && <MarketPrices location={location} />}
      {activeTab === 'weather' && <WeatherForecast location={location} />}
      {activeTab === 'schemes' && <GovernmentSchemes />}
    </div>
  );
}

// Market Prices Component
function MarketPrices({ location }) {
  const { t } = useLanguage();
  const [prices, setPrices] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetch(`${API_BASE}/api/market-prices?location=${location}`)
      .then(r => r.json())
      .then(d => setPrices(d.prices || []))
      .finally(() => setLoading(false));
  }, [location]);

  if (loading) return <Card className="p-6"><LoadingSpinner msg={t.fetching_prices} /></Card>;

  return (
    <Card className="p-6">
      <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2"><TrendingUp className="w-5 h-5 text-emerald-400" />{t.market_title}</h3>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {prices.map(p => (
          <div key={p.id} className="bg-slate-700/50 rounded-lg p-4">
            <div className="flex justify-between items-start mb-2">
              <span className="text-white font-medium">{t.commodity_names?.[p.name] || p.name}</span>
              <span className={`text-xs px-2 py-0.5 rounded ${p.trend === 'up' ? 'bg-green-500/20 text-green-400' : p.trend === 'down' ? 'bg-red-500/20 text-red-400' : 'bg-slate-600 text-slate-300'}`}>{p.change}</span>
            </div>
            <div className="text-2xl font-bold text-emerald-400">₹{p.price}<span className="text-sm text-slate-400 font-normal">{t[`per_${p.unit}`] || '/' + p.unit}</span></div>
          </div>
        ))}
      </div>
    </Card>
  );
}

// Weather Forecast Component
function WeatherForecast({ location }) {
  const { language, t } = useLanguage();
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetch(`${API_BASE}/api/weather?location=${location}`)
      .then(r => r.json())
      .then(setWeather)
      .finally(() => setLoading(false));
  }, [location]);

  if (loading) return <Card className="p-6"><LoadingSpinner msg={language === 'telugu' ? 'వాతావరణం లోడ్ అవుతోంది...' : 'Loading weather...'} /></Card>;
  if (!weather || weather.error) return <Card className="p-6"><p className="text-center text-slate-400">Weather unavailable</p></Card>;

  return (
    <Card className="p-6">
      <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2"><Cloud className="w-5 h-5 text-cyan-400" />{t.weather_title || 'Weather Forecast'}</h3>
      
      {/* Current Weather */}
      <div className="bg-gradient-to-r from-cyan-500/20 to-blue-500/20 rounded-xl p-6 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-sm">{t.today || 'Today'}</p>
            <div className="flex items-center gap-3">
              <span className="text-5xl">{weather.current?.icon}</span>
              <div>
                <p className="text-4xl font-bold text-white">{weather.current?.temperature}°C</p>
                <p className="text-slate-300">{weather.current?.description}</p>
              </div>
            </div>
          </div>
          <div className="text-right space-y-2">
            <div className="flex items-center gap-2 text-slate-300"><Droplets className="w-4 h-4 text-blue-400" />{weather.current?.humidity}%</div>
            <div className="flex items-center gap-2 text-slate-300"><Wind className="w-4 h-4 text-cyan-400" />{weather.current?.wind_speed} km/h</div>
          </div>
        </div>
      </div>

      {/* Advisory */}
      {weather.advisory?.length > 0 && (
        <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg p-4 mb-6">
          <h4 className="font-semibold text-amber-400 mb-2">{t.weather_advisory || 'Weather Advisory'}</h4>
          {weather.advisory.map((a, i) => <p key={i} className="text-slate-300 text-sm">{a}</p>)}
        </div>
      )}

      {/* 7-Day Forecast */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
        {weather.forecast?.slice(0, 7).map((day, i) => (
          <div key={i} className="bg-slate-700/50 rounded-lg p-3 text-center">
            <p className="text-slate-400 text-sm">{i === 0 ? (t.today || 'Today') : day.day?.slice(0, 3)}</p>
            <p className="text-3xl my-2">{day.icon}</p>
            <p className="text-white font-semibold">{day.temp_max}°</p>
            <p className="text-slate-400 text-sm">{day.temp_min}°</p>
            {day.rain_chance > 0 && <p className="text-blue-400 text-xs mt-1">💧 {day.rain_chance}%</p>}
          </div>
        ))}
      </div>
    </Card>
  );
}

// Government Schemes Component
function GovernmentSchemes() {
  const { language, t } = useLanguage();
  const [schemes, setSchemes] = useState([]);
  const [categories, setCategories] = useState([]);
  const [category, setCategory] = useState('all');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(null);

  useEffect(() => {
    setLoading(true);
    fetch(`${API_BASE}/api/schemes?category=${category}&search=${search}&language=${language}`)
      .then(r => r.json())
      .then(d => { setSchemes(d.schemes || []); setCategories(d.categories || []); })
      .finally(() => setLoading(false));
  }, [category, search, language]);

  return (
    <Card className="p-6">
      <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2"><FileText className="w-5 h-5 text-purple-400" />{t.schemes_title || 'Government Schemes'}</h3>
      
      <div className="flex flex-wrap gap-3 mb-6">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder={t.search_schemes || 'Search schemes...'} className="w-full bg-slate-700 text-white pl-10 pr-4 py-2 rounded-lg border border-slate-600 focus:ring-2 focus:ring-purple-500" />
        </div>
        <select value={category} onChange={e => setCategory(e.target.value)} className="bg-slate-700 text-white px-4 py-2 rounded-lg border border-slate-600">
          {categories.map(c => <option key={c.id} value={c.id}>{language === 'telugu' ? c.name_te : c.name}</option>)}
        </select>
      </div>

      {loading ? <LoadingSpinner msg="Loading schemes..." /> : (
        <div className="space-y-3">
          {schemes.map(s => (
            <div key={s.id} className="bg-slate-700/50 rounded-lg overflow-hidden">
              <button onClick={() => setExpanded(expanded === s.id ? null : s.id)} className="w-full p-4 text-left flex justify-between items-center hover:bg-slate-700/70">
                <div>
                  <h4 className="font-semibold text-white">{s.name}</h4>
                  <p className="text-slate-400 text-sm">{s.benefits?.slice(0, 60)}...</p>
                </div>
                <ChevronRight className={`w-5 h-5 text-slate-400 transition-transform ${expanded === s.id ? 'rotate-90' : ''}`} />
              </button>
              
              {expanded === s.id && (
                <div className="px-4 pb-4 border-t border-slate-600 pt-4">
                  <p className="text-slate-300 mb-4">{s.description}</p>
                  
                  <div className="grid md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <h5 className="text-emerald-400 font-medium mb-1">{t.eligibility || 'Eligibility'}</h5>
                      <p className="text-slate-300 text-sm">{s.eligibility}</p>
                    </div>
                    <div>
                      <h5 className="text-emerald-400 font-medium mb-1">{t.benefits || 'Benefits'}</h5>
                      <p className="text-slate-300 text-sm">{s.benefits}</p>
                    </div>
                  </div>
                  
                  <div className="mb-4">
                    <h5 className="text-emerald-400 font-medium mb-1">{t.documents_required || 'Documents Required'}</h5>
                    <div className="flex flex-wrap gap-2">{s.documents?.map((d, i) => <span key={i} className="bg-slate-600 text-slate-200 px-2 py-1 rounded text-sm">{d}</span>)}</div>
                  </div>
                  
                  <div className="flex flex-wrap gap-3">
                    {s.apply_link && <a href={s.apply_link} target="_blank" rel="noopener noreferrer" className="bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-2 rounded-lg flex items-center gap-2"><ExternalLink className="w-4 h-4" />{t.apply_now || 'Apply Now'}</a>}
                    {s.helpline && <span className="bg-slate-600 text-white px-4 py-2 rounded-lg flex items-center gap-2"><Phone className="w-4 h-4" />{t.helpline}: {s.helpline}</span>}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}

// Health & Medical (with Pharmacies, Blood Banks, Symptom Checker)
function HealthMedical() {
  const { language, t } = useLanguage();
  const [location, setLocation] = useState('visakhapatnam');
  const [activeTab, setActiveTab] = useState('hospitals');
  const locations = ['visakhapatnam', 'vijayawada', 'guntur', 'tirupati', 'hyderabad', 'warangal', 'karimnagar', 'nellore', 'kurnool', 'rajahmundry'];

  const tabs = [
    { id: 'hospitals', name: language === 'telugu' ? 'ఆసుపత్రులు' : 'Hospitals', icon: Heart },
    { id: 'pharmacies', name: language === 'telugu' ? 'ఫార్మసీలు' : 'Pharmacies', icon: Pill },
    { id: 'bloodbanks', name: language === 'telugu' ? 'బ్లడ్ బ్యాంకులు' : 'Blood Banks', icon: Activity },
    { id: 'symptoms', name: language === 'telugu' ? 'లక్షణాల తనిఖీ' : 'Symptom Checker', icon: AlertCircle }
  ];

  return (
    <div className="space-y-4">
      {/* Emergency Banner */}
      <Card className="p-4 bg-gradient-to-r from-red-500/20 to-orange-500/20 border-red-500/30">
        <div className="flex items-center gap-3">
          <Heart className="w-6 h-6 text-red-400" />
          <div>
            <p className="font-bold text-red-400">{t.emergency_call || 'Emergency: Call 108'}</p>
            <p className="text-slate-300 text-sm">{t.ambulance_service || '24/7 Ambulance Service'}</p>
          </div>
        </div>
      </Card>

      {/* Location & Tabs */}
      <Card className="p-4">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2">
            <MapPin className="w-5 h-5 text-red-400" />
            <select value={location} onChange={e => setLocation(e.target.value)} className="bg-slate-700 text-white px-4 py-2 rounded-lg border border-slate-600">
              {locations.map(l => <option key={l} value={l}>{t.locations?.[l] || l.charAt(0).toUpperCase() + l.slice(1)}</option>)}
            </select>
          </div>
          <div className="flex gap-2 flex-wrap">
            {tabs.map(tab => (
              <button key={tab.id} onClick={() => setActiveTab(tab.id)} className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${activeTab === tab.id ? 'bg-red-500 text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}`}>
                <tab.icon className="w-4 h-4" />{tab.name}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {activeTab === 'hospitals' && <HospitalsList location={location} />}
      {activeTab === 'pharmacies' && <PharmaciesList location={location} />}
      {activeTab === 'bloodbanks' && <BloodBanksList location={location} />}
      {activeTab === 'symptoms' && <SymptomChecker />}
    </div>
  );
}

// Hospitals List
function HospitalsList({ location }) {
  const { t } = useLanguage();
  const [hospitals, setHospitals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetch(`${API_BASE}/api/hospitals?location=${location}`)
      .then(r => r.json())
      .then(d => setHospitals(d.hospitals || []))
      .finally(() => setLoading(false));
  }, [location]);

  if (loading) return <Card className="p-6"><LoadingSpinner msg="Finding hospitals..." /></Card>;

  return (
    <Card className="p-6">
      <h3 className="text-xl font-bold text-white mb-4">{t.nearest_hospitals} {t.locations?.[location] || location.charAt(0).toUpperCase() + location.slice(1)} ({hospitals.length})</h3>
      <div className="space-y-3">
        {hospitals.map((h, i) => (
          <div key={h.id || i} className="bg-slate-700/50 rounded-lg p-4">
            <div className="flex justify-between items-start mb-2">
              <div>
                <h4 className="font-semibold text-white">{h.name}</h4>
                <p className="text-slate-400 text-sm">{t.hospital_types?.[h.type] || h.type}</p>
              </div>
              {h.emergency && <span className="bg-red-500/20 text-red-400 text-xs px-2 py-1 rounded">{t.emergency_24x7}</span>}
            </div>
            <div className="flex flex-wrap gap-4 text-sm text-slate-300 mb-3">
              <span className="flex items-center gap-1"><MapPin className="w-4 h-4" />{h.distance}</span>
              <span className="flex items-center gap-1"><Phone className="w-4 h-4" />{h.phone}</span>
            </div>
            <button onClick={() => window.open(`https://www.google.com/maps/dir/?api=1&destination=${h.lat},${h.lon}`, '_blank')} className="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 rounded-lg flex items-center justify-center gap-2">
              {t.get_directions}<ChevronRight className="w-4 h-4" />
            </button>
          </div>
        ))}
      </div>
    </Card>
  );
}

// Pharmacies List
function PharmaciesList({ location }) {
  const { language, t } = useLanguage();
  const [pharmacies, setPharmacies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetch(`${API_BASE}/api/pharmacies?location=${location}`)
      .then(r => r.json())
      .then(d => setPharmacies(d.pharmacies || []))
      .finally(() => setLoading(false));
  }, [location]);

  if (loading) return <Card className="p-6"><LoadingSpinner msg="Finding pharmacies..." /></Card>;

  return (
    <Card className="p-6">
      <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2"><Pill className="w-5 h-5 text-green-400" />{t.pharmacies_title || 'Nearby Pharmacies'} ({pharmacies.length})</h3>
      {pharmacies.length === 0 ? <p className="text-slate-400 text-center py-8">No pharmacies found nearby</p> : (
        <div className="grid md:grid-cols-2 gap-4">
          {pharmacies.map((p, i) => (
            <div key={p.id || i} className="bg-slate-700/50 rounded-lg p-4">
              <div className="flex justify-between items-start mb-2">
                <h4 className="font-semibold text-white">{p.name}</h4>
                {p.is_24x7 && <span className="bg-green-500/20 text-green-400 text-xs px-2 py-1 rounded flex items-center gap-1"><Clock className="w-3 h-3" />{t.open_24x7 || '24/7'}</span>}
              </div>
              <div className="text-sm text-slate-300 space-y-1">
                <p className="flex items-center gap-2"><MapPin className="w-4 h-4 text-slate-400" />{p.distance}</p>
                {p.phone !== 'N/A' && <p className="flex items-center gap-2"><Phone className="w-4 h-4 text-slate-400" />{p.phone}</p>}
              </div>
              <button onClick={() => window.open(`https://www.google.com/maps/dir/?api=1&destination=${p.lat},${p.lon}`, '_blank')} className="mt-3 w-full bg-green-500 hover:bg-green-600 text-white py-2 rounded-lg text-sm">
                {t.get_directions || 'Get Directions'}
              </button>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}

// Blood Banks List
function BloodBanksList({ location }) {
  const { language, t } = useLanguage();
  const [bloodBanks, setBloodBanks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetch(`${API_BASE}/api/blood-banks?location=${location}`)
      .then(r => r.json())
      .then(d => setBloodBanks(d.blood_banks || []))
      .finally(() => setLoading(false));
  }, [location]);

  if (loading) return <Card className="p-6"><LoadingSpinner msg="Finding blood banks..." /></Card>;

  return (
    <Card className="p-6">
      <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2"><Activity className="w-5 h-5 text-red-400" />{t.blood_banks_title || 'Blood Banks'} ({bloodBanks.length})</h3>
      <div className="grid md:grid-cols-2 gap-4">
        {bloodBanks.map((b, i) => (
          <div key={b.id || i} className="bg-slate-700/50 rounded-lg p-4">
            <div className="flex justify-between items-start mb-2">
              <h4 className="font-semibold text-white">{b.name}</h4>
              {b.is_24x7 && <span className="bg-red-500/20 text-red-400 text-xs px-2 py-1 rounded">24/7</span>}
            </div>
            <div className="text-sm text-slate-300 space-y-1 mb-3">
              <p className="flex items-center gap-2"><MapPin className="w-4 h-4 text-slate-400" />{b.distance}</p>
              {b.phone !== 'N/A' && <p className="flex items-center gap-2"><Phone className="w-4 h-4 text-slate-400" />{b.phone}</p>}
            </div>
            <button onClick={() => window.open(`https://www.google.com/maps/dir/?api=1&destination=${b.lat},${b.lon}`, '_blank')} className="w-full bg-red-500 hover:bg-red-600 text-white py-2 rounded-lg text-sm">
              {t.get_directions || 'Get Directions'}
            </button>
          </div>
        ))}
      </div>
    </Card>
  );
}

// Symptom Checker
function SymptomChecker() {
  const { language, t } = useLanguage();
  const [symptoms, setSymptoms] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const checkSymptoms = async () => {
    if (!symptoms.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/symptom-checker`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symptoms, language })
      });
      const data = await res.json();
      setResult(data);
    } catch (e) {
      setResult({ success: false, response: 'Error checking symptoms' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="p-6">
      <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2"><AlertCircle className="w-5 h-5 text-amber-400" />{t.symptom_checker_title || 'Symptom Checker'}</h3>
      
      <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg p-4 mb-6">
        <p className="text-amber-300 text-sm">⚠️ {t.disclaimer || 'This is for informational purposes only. Please consult a doctor for proper diagnosis.'}</p>
      </div>

      <div className="mb-4">
        <textarea value={symptoms} onChange={e => setSymptoms(e.target.value)} placeholder={t.symptom_placeholder || 'Describe your symptoms (e.g., headache, fever, body pain)...'} className="w-full bg-slate-700 text-white p-4 rounded-lg border border-slate-600 focus:ring-2 focus:ring-amber-500 h-32 resize-none" />
      </div>

      <button onClick={checkSymptoms} disabled={loading || !symptoms.trim()} className="w-full bg-amber-500 hover:bg-amber-600 disabled:bg-slate-600 text-white py-3 rounded-lg font-medium flex items-center justify-center gap-2">
        {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <AlertCircle className="w-5 h-5" />}
        {loading ? (t.chatbot_thinking || 'Analyzing...') : (t.check_symptoms || 'Check Symptoms')}
      </button>

      {result && (
        <div className={`mt-6 p-4 rounded-lg ${result.success ? 'bg-slate-700/50' : 'bg-red-500/20'}`}>
          <div className="prose prose-invert max-w-none">
            <pre className="whitespace-pre-wrap text-slate-300 text-sm font-sans">{result.response}</pre>
          </div>
        </div>
      )}
    </Card>
  );
}

// ChatBot
function ChatBot() {
  const { language, t } = useLanguage();
  const [messages, setMessages] = useState([{ role: 'assistant', content: t.chatbot_welcome || 'Hello! How can I help you today?' }]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);
  const messagesEnd = useRef(null);
  const recognition = useRef(null);

  useEffect(() => { messagesEnd.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  useEffect(() => {
    if ('webkitSpeechRecognition' in window) {
      recognition.current = new window.webkitSpeechRecognition();
      recognition.current.continuous = false;
      recognition.current.lang = language === 'telugu' ? 'te-IN' : 'en-IN';
      recognition.current.onresult = e => { setInput(e.results[0][0].transcript); setListening(false); };
      recognition.current.onend = () => setListening(false);
    }
  }, [language]);

  const toggleListen = () => {
    if (!recognition.current) return alert('Voice not supported');
    if (listening) { recognition.current.stop(); setListening(false); }
    else { recognition.current.lang = language === 'telugu' ? 'te-IN' : 'en-IN'; recognition.current.start(); setListening(true); }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const userMsg = input.trim();
    setInput('');
    setMessages(m => [...m, { role: 'user', content: userMsg }]);
    setLoading(true);
    
    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg, language })
      });
      const data = await res.json();
      setMessages(m => [...m, { role: 'assistant', content: data.response }]);
    } catch (e) {
      setMessages(m => [...m, { role: 'assistant', content: 'Error connecting to server' }]);
    }
    setLoading(false);
  };

  const suggestions = t.chatbot_suggestions || ['What schemes are available for farmers?', 'Weather forecast', 'Nearest hospital'];

  return (
    <Card className="flex flex-col" style={{ height: 'calc(100vh - 200px)', minHeight: '500px' }}>
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 p-4 rounded-t-xl">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center"><Bot className="w-6 h-6 text-white" /></div>
          <div>
            <h2 className="text-lg font-bold text-white">{t.chatbot_title || 'Ask Assistant'}</h2>
            <p className="text-white/70 text-sm">{t.chatbot_subtitle}</p>
          </div>
        </div>
      </div>

      {/* Suggestions */}
      {messages.length <= 1 && (
        <div className="p-4 border-b border-slate-700 flex flex-wrap gap-2">
          {suggestions.map((s, i) => <button key={i} onClick={() => setInput(s)} className="bg-slate-700 hover:bg-slate-600 text-slate-300 px-3 py-1.5 rounded-full text-sm">{s}</button>)}
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`flex items-start gap-2 max-w-[80%] ${m.role === 'user' ? 'flex-row-reverse' : ''}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${m.role === 'user' ? 'bg-purple-600' : 'bg-slate-600'}`}>
                {m.role === 'user' ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-white" />}
              </div>
              <div className={`rounded-2xl px-4 py-2 ${m.role === 'user' ? 'bg-purple-600 text-white' : 'bg-slate-700 text-slate-200'}`}>
                <pre className="whitespace-pre-wrap font-sans text-sm">{m.content}</pre>
              </div>
            </div>
          </div>
        ))}
        {loading && <div className="flex justify-start"><div className="bg-slate-700 rounded-2xl px-4 py-3 flex items-center gap-2"><Loader2 className="w-4 h-4 animate-spin text-purple-400" /><span className="text-slate-300">{t.chatbot_thinking}</span></div></div>}
        <div ref={messagesEnd} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-slate-700">
        <div className="flex gap-2">
          <button onClick={toggleListen} className={`p-3 rounded-full ${listening ? 'bg-red-500 animate-pulse' : 'bg-slate-700 hover:bg-slate-600'}`}>
            {listening ? <MicOff className="w-5 h-5 text-white" /> : <Mic className="w-5 h-5 text-slate-300" />}
          </button>
          <input type="text" value={input} onChange={e => setInput(e.target.value)} onKeyPress={e => e.key === 'Enter' && sendMessage()} placeholder={t.chatbot_placeholder} className="flex-1 bg-slate-700 text-white px-4 py-3 rounded-full border border-slate-600 focus:ring-2 focus:ring-purple-500" />
          <button onClick={sendMessage} disabled={!input.trim() || loading} className="p-3 bg-purple-600 hover:bg-purple-700 disabled:bg-slate-600 rounded-full">
            <Send className="w-5 h-5 text-white" />
          </button>
        </div>
      </div>
    </Card>
  );
}
