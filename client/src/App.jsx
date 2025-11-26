import React, { useState, useEffect, createContext, useContext, useRef } from 'react';
import { Globe, TrendingUp, Heart, ChevronRight, MapPin, Calendar, RefreshCw, Loader2, ExternalLink, Languages, MessageCircle, Mic, MicOff, Send, Bot, User } from 'lucide-react';

// API Base URL - change this if your server runs on different port
const API_BASE = 'http://localhost:8000';

// Language Context
const LanguageContext = createContext();

// Hook to use language
function useLanguage() {
  return useContext(LanguageContext);
}

// Main App Component
export default function UnifiedDashboard() {
  const [activePage, setActivePage] = useState('education');
  const [language, setLanguage] = useState('english');
  const [translations, setTranslations] = useState(null);
  const [loadingTranslations, setLoadingTranslations] = useState(true);

  // Fetch translations when language changes
  useEffect(() => {
    const fetchTranslations = async () => {
      setLoadingTranslations(true);
      try {
        const response = await fetch(`${API_BASE}/api/translations?language=${language}`);
        if (response.ok) {
          const data = await response.json();
          setTranslations(data);
        }
      } catch (err) {
        console.error('Failed to fetch translations:', err);
        setTranslations(getDefaultTranslations(language));
      } finally {
        setLoadingTranslations(false);
      }
    };
    fetchTranslations();
  }, [language]);

  // Default translations fallback
  const getDefaultTranslations = (lang) => {
    if (lang === 'telugu') {
      return {
        app_title: 'గ్రామీణ నిర్వహణ డాష్‌బోర్డ్',
        app_subtitle: 'గ్రామీణ సమాచారం మరియు సేవలకు మీ గేట్‌వే',
        nav_education: 'విద్య & వార్తలు',
        nav_agriculture: 'వ్యవసాయం & మార్కెట్',
        nav_health: 'ఆరోగ్యం & వైద్యం',
        nav_chatbot: 'సహాయకుడిని అడగండి',
        refresh: 'రిఫ్రెష్',
        loading: 'లోడ్ అవుతోంది...',
      };
    }
    return {
      app_title: 'Rural Management Dashboard',
      app_subtitle: 'Your gateway to rural information and services',
      nav_education: 'Education & News',
      nav_agriculture: 'Agriculture & Market',
      nav_health: 'Health & Medical',
      nav_chatbot: 'Ask Assistant',
      refresh: 'Refresh',
      loading: 'Loading...',
    };
  };

  const t = translations || getDefaultTranslations(language);

  const pages = [
    { id: 'education', name: t.nav_education, icon: Globe },
    { id: 'agriculture', name: t.nav_agriculture, icon: TrendingUp },
    { id: 'health', name: t.nav_health, icon: Heart },
    { id: 'chatbot', name: t.nav_chatbot, icon: MessageCircle }
  ];

  if (loadingTranslations && !translations) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-indigo-600 animate-spin" />
      </div>
    );
  }

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        {/* Header */}
        <header className="bg-white shadow-md">
          <div className="max-w-7xl mx-auto px-4 py-4">
            <div className="flex justify-between items-center">
              <div>
                <h1 className="text-3xl font-bold text-indigo-600">{t.app_title}</h1>
                <p className="text-gray-600 text-sm">{t.app_subtitle}</p>
              </div>
              
              {/* Language Switcher */}
              <div className="flex items-center space-x-2">
                <Languages className="w-5 h-5 text-gray-500" />
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-lg bg-white text-gray-700 focus:ring-2 focus:ring-indigo-500 focus:border-transparent font-medium"
                >
                  <option value="english">English</option>
                  <option value="telugu">తెలుగు</option>
                </select>
              </div>
            </div>
          </div>
        </header>

        {/* Navigation */}
        <nav className="bg-white shadow-sm mt-4 mx-4 rounded-lg">
          <div className="max-w-7xl mx-auto px-4">
            <div className="flex space-x-2 overflow-x-auto py-2">
              {pages.map((page) => {
                const Icon = page.icon;
                return (
                  <button
                    key={page.id}
                    onClick={() => setActivePage(page.id)}
                    className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all ${
                      activePage === page.id
                        ? 'bg-indigo-600 text-white shadow-lg'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="whitespace-nowrap">{page.name}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </nav>

        {/* Main Content */}
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

// Loading Spinner Component
function LoadingSpinner({ message }) {
  const { t } = useLanguage();
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <Loader2 className="w-8 h-8 text-indigo-600 animate-spin mb-3" />
      <p className="text-gray-600">{message || t.loading}</p>
    </div>
  );
}

// Error Component
function ErrorMessage({ message, onRetry }) {
  const { t } = useLanguage();
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
      <p className="text-red-600 mb-4">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          {t.try_again || 'Try Again'}
        </button>
      )}
    </div>
  );
}

// ChatBot Component with Voice Input
function ChatBot() {
  const { language, t } = useLanguage();
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [chatStatus, setChatStatus] = useState({ configured: false, message: '' });
  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);

  // Check chatbot status on mount
  useEffect(() => {
    const checkStatus = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/chat/status`);
        if (response.ok) {
          const data = await response.json();
          setChatStatus(data);
        }
      } catch (err) {
        console.error('Failed to check chat status:', err);
      }
    };
    checkStatus();
  }, []);

  // Initialize with welcome message
  useEffect(() => {
    const welcomeMsg = t.chatbot_welcome || 'Hello! I am your Rural Assistant. How can I help you today?';
    setMessages([{ role: 'assistant', content: welcomeMsg }]);
  }, [language, t.chatbot_welcome]);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Initialize speech recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = language === 'telugu' ? 'te-IN' : 'en-IN';

      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInputText(transcript);
        setIsListening(false);
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, [language]);

  const toggleListening = () => {
    if (!recognitionRef.current) {
      alert(t.voice_not_supported || 'Voice input is not supported in your browser');
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      recognitionRef.current.lang = language === 'telugu' ? 'te-IN' : 'en-IN';
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  const sendMessage = async () => {
    if (!inputText.trim() || isLoading) return;

    const userMessage = inputText.trim();
    setInputText('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          language: language
        }),
      });

      const data = await response.json();
      
      if (data.success) {
        setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
      } else {
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: data.response || t.chatbot_error || 'Sorry, I could not process your request.'
        }]);
      }
    } catch (err) {
      console.error('Chat error:', err);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: t.chatbot_error || 'Sorry, an error occurred. Please try again.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setInputText(suggestion);
  };

  const suggestions = t.chatbot_suggestions || [
    'What government schemes are available for farmers?',
    'How to apply for health insurance?',
    'What are today\'s vegetable prices?',
    'Nearest hospital in my area?'
  ];

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden flex flex-col" style={{ height: 'calc(100vh - 220px)', minHeight: '500px' }}>
      {/* Chat Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold">{t.chatbot_title || 'Ask Assistant'}</h2>
            <p className="text-sm text-white/80">{t.chatbot_subtitle || 'Ask any question about agriculture, health, education, or government schemes'}</p>
          </div>
        </div>
        {!chatStatus.configured && (
          <div className="mt-3 bg-yellow-500/20 border border-yellow-300/30 rounded-lg p-2 text-sm">
            ⚠️ {chatStatus.message}
          </div>
        )}
      </div>

      {/* Suggestions (show only when no messages except welcome) */}
      {messages.length <= 1 && (
        <div className="p-4 bg-gray-50 border-b">
          <p className="text-sm text-gray-600 mb-2">{language === 'telugu' ? 'సూచనలు:' : 'Suggestions:'}</p>
          <div className="flex flex-wrap gap-2">
            {suggestions.map((suggestion, idx) => (
              <button
                key={idx}
                onClick={() => handleSuggestionClick(suggestion)}
                className="px-3 py-1.5 bg-white border border-gray-200 rounded-full text-sm text-gray-700 hover:bg-indigo-50 hover:border-indigo-300 transition-colors"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`flex items-start space-x-2 max-w-[80%] ${msg.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                msg.role === 'user' ? 'bg-indigo-600' : 'bg-gray-200'
              }`}>
                {msg.role === 'user' ? (
                  <User className="w-4 h-4 text-white" />
                ) : (
                  <Bot className="w-4 h-4 text-gray-600" />
                )}
              </div>
              <div className={`rounded-2xl px-4 py-2 ${
                msg.role === 'user'
                  ? 'bg-indigo-600 text-white rounded-tr-sm'
                  : 'bg-gray-100 text-gray-800 rounded-tl-sm'
              }`}>
                <p className="whitespace-pre-wrap">{msg.content}</p>
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="flex items-start space-x-2">
              <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                <Bot className="w-4 h-4 text-gray-600" />
              </div>
              <div className="bg-gray-100 rounded-2xl rounded-tl-sm px-4 py-3">
                <div className="flex items-center space-x-2">
                  <Loader2 className="w-4 h-4 animate-spin text-indigo-600" />
                  <span className="text-gray-600">{t.chatbot_thinking || 'Thinking...'}</span>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t bg-white p-4">
        <div className="flex items-center space-x-2">
          {/* Voice Input Button */}
          <button
            onClick={toggleListening}
            className={`p-3 rounded-full transition-all ${
              isListening
                ? 'bg-red-500 text-white animate-pulse'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
            title={isListening ? (t.chatbot_listening || 'Listening...') : (language === 'telugu' ? 'మాట్లాడండి' : 'Speak')}
          >
            {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
          </button>

          {/* Text Input */}
          <div className="flex-1 relative">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={t.chatbot_placeholder || 'Type your question or click the microphone to speak...'}
              className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-full focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              disabled={isLoading}
            />
            {isListening && (
              <span className="absolute right-14 top-1/2 -translate-y-1/2 text-red-500 text-sm animate-pulse">
                {t.chatbot_listening || 'Listening...'}
              </span>
            )}
          </div>

          {/* Send Button */}
          <button
            onClick={sendMessage}
            disabled={!inputText.trim() || isLoading}
            className="p-3 bg-indigo-600 text-white rounded-full hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}

// Education & News Component
function EducationNews() {
  const { language, t } = useLanguage();
  const [category, setCategory] = useState('all');
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const categories = ['all', 'education', 'technology', 'science', 'politics', 'sports'];

  const fetchNews = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/api/news?language=${language}&category=${category}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch news');
      }
      
      const data = await response.json();
      setNews(data.articles || []);
      setLastUpdated(data.last_updated);
    } catch (err) {
      console.error('News fetch error:', err);
      setError(language === 'telugu' 
        ? 'వార్తలు లోడ్ చేయడం సాధ్యం కాలేదు. సర్వర్ రన్ అవుతుందో చెక్ చేయండి.'
        : 'Unable to load news. Make sure the server is running.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNews();
  }, [language, category]);

  const getCategoryName = (cat) => {
    return t.categories?.[cat] || cat.charAt(0).toUpperCase() + cat.slice(1);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">{t.news_title || 'Education & News'}</h2>
        <button
          onClick={fetchNews}
          disabled={loading}
          className="flex items-center space-x-2 px-4 py-2 bg-indigo-100 text-indigo-600 rounded-lg hover:bg-indigo-200 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>{t.refresh}</span>
        </button>
      </div>
      
      {/* Category Filter */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">{t.category || 'Category'}</label>
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="w-full md:w-1/2 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
        >
          {categories.map(cat => (
            <option key={cat} value={cat}>
              {getCategoryName(cat)}
            </option>
          ))}
        </select>
      </div>

      {/* Last Updated */}
      {lastUpdated && (
        <div className="text-xs text-gray-500 mb-4">
          {t.last_updated}: {new Date(lastUpdated).toLocaleString()}
        </div>
      )}

      {/* Content */}
      {loading ? (
        <LoadingSpinner message={t.fetching_news} />
      ) : error ? (
        <ErrorMessage message={error} onRetry={fetchNews} />
      ) : news.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          {t.no_news || 'No news articles found for this category.'}
        </div>
      ) : (
        <div className="space-y-4">
          {news.map((article, index) => (
            <div key={article.id || index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start mb-2">
                <h3 className="text-lg font-semibold text-gray-800 flex-1 pr-2">{article.title}</h3>
                <span className="text-xs bg-indigo-100 text-indigo-600 px-2 py-1 rounded whitespace-nowrap">
                  {getCategoryName(article.category)}
                </span>
              </div>
              {article.summary && (
                <p className="text-gray-600 text-sm mb-2">{article.summary}</p>
              )}
              <div className="flex items-center justify-between text-xs text-gray-500">
                <div className="flex items-center">
                  <Calendar className="w-4 h-4 mr-1" />
                  {article.date}
                </div>
                {article.url && article.url !== '#' && (
                  <a
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center text-indigo-600 hover:text-indigo-800"
                  >
                    {t.read_more} <ExternalLink className="w-3 h-3 ml-1" />
                  </a>
                )}
              </div>
              {article.source && (
                <div className="text-xs text-gray-400 mt-2">
                  {t.source}: {article.source}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Agriculture & Market Component
function AgricultureMarket() {
  const { language, t } = useLanguage();
  const [location, setLocation] = useState('visakhapatnam');
  const [prices, setPrices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const locations = ['visakhapatnam', 'vijayawada', 'guntur', 'tirupati', 'hyderabad'];

  const fetchPrices = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/api/market-prices?location=${location}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch market prices');
      }
      
      const data = await response.json();
      setPrices(data.prices || []);
      setLastUpdated(data.last_updated);
    } catch (err) {
      console.error('Market prices fetch error:', err);
      setError(language === 'telugu'
        ? 'మార్కెట్ ధరలు లోడ్ చేయడం సాధ్యం కాలేదు. సర్వర్ రన్ అవుతుందో చెక్ చేయండి.'
        : 'Unable to load market prices. Make sure the server is running.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPrices();
  }, [location]);

  const getLocationName = (loc) => {
    return t.locations?.[loc] || loc.charAt(0).toUpperCase() + loc.slice(1);
  };

  const getCommodityName = (name) => {
    return t.commodity_names?.[name] || name;
  };

  const getUnitLabel = (unit) => {
    if (unit === 'kg') return t.per_kg || '/kg';
    if (unit === 'liter') return t.per_liter || '/liter';
    if (unit === 'dozen') return t.per_dozen || '/dozen';
    return '/' + unit;
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">{t.market_title || 'Agriculture & Market'}</h2>
        <button
          onClick={fetchPrices}
          disabled={loading}
          className="flex items-center space-x-2 px-4 py-2 bg-green-100 text-green-600 rounded-lg hover:bg-green-200 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>{t.refresh}</span>
        </button>
      </div>
      
      {/* Location Selector */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">{t.select_location || 'Select Location'}</label>
        <select
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          className="w-full md:w-1/2 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
        >
          {locations.map(loc => (
            <option key={loc} value={loc}>
              {getLocationName(loc)}
            </option>
          ))}
        </select>
      </div>

      {/* Market Info Banner */}
      <div className="bg-green-50 rounded-lg p-4 mb-4">
        <div className="flex items-center text-sm text-gray-600">
          <MapPin className="w-4 h-4 mr-1" />
          {t.live_prices || 'Live prices from'} {getLocationName(location)} {t.market || 'market'}
        </div>
        {lastUpdated && (
          <div className="text-xs text-gray-500 mt-1">
            {t.last_updated}: {new Date(lastUpdated).toLocaleString()}
          </div>
        )}
      </div>

      {/* Content */}
      {loading ? (
        <LoadingSpinner message={t.fetching_prices} />
      ) : error ? (
        <ErrorMessage message={error} onRetry={fetchPrices} />
      ) : prices.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          {t.no_prices || 'No price data available for this location.'}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {prices.map((item) => (
            <div key={item.id || item.name} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start mb-2">
                <h3 className="text-lg font-semibold text-gray-800">{getCommodityName(item.name)}</h3>
                <span className={`text-xs px-2 py-1 rounded ${
                  item.trend === 'up' ? 'bg-green-100 text-green-600' :
                  item.trend === 'down' ? 'bg-red-100 text-red-600' :
                  'bg-gray-100 text-gray-600'
                }`}>
                  {item.change}
                </span>
              </div>
              <div className="text-2xl font-bold text-green-600">
                ₹{item.price}
                <span className="text-sm text-gray-500 font-normal">{getUnitLabel(item.unit)}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Health & Medical Component
function HealthMedical() {
  const { language, t } = useLanguage();
  const [userLocation, setUserLocation] = useState('visakhapatnam');
  const [hospitals, setHospitals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const locations = ['visakhapatnam', 'vijayawada', 'guntur', 'tirupati', 'hyderabad'];

  const fetchHospitals = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/api/hospitals?location=${userLocation}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch hospitals');
      }
      
      const data = await response.json();
      setHospitals(data.hospitals || []);
      setLastUpdated(data.last_updated);
    } catch (err) {
      console.error('Hospitals fetch error:', err);
      setError(language === 'telugu'
        ? 'ఆసుపత్రులు లోడ్ చేయడం సాధ్యం కాలేదు. సర్వర్ రన్ అవుతుందో చెక్ చేయండి.'
        : 'Unable to load hospitals. Make sure the server is running.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHospitals();
  }, [userLocation]);

  const getLocationName = (loc) => {
    return t.locations?.[loc] || loc.charAt(0).toUpperCase() + loc.slice(1);
  };

  const getHospitalType = (type) => {
    return t.hospital_types?.[type] || type;
  };

  const openDirections = (hospital) => {
    if (hospital.lat && hospital.lon) {
      window.open(`https://www.google.com/maps/dir/?api=1&destination=${hospital.lat},${hospital.lon}`, '_blank');
    } else {
      window.open(`https://www.google.com/maps/search/${encodeURIComponent(hospital.name + ' ' + userLocation)}`, '_blank');
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">{t.health_title || 'Health & Medical'}</h2>
        <button
          onClick={fetchHospitals}
          disabled={loading}
          className="flex items-center space-x-2 px-4 py-2 bg-red-100 text-red-600 rounded-lg hover:bg-red-200 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>{t.refresh}</span>
        </button>
      </div>
      
      {/* Location Selector */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">{t.your_location || 'Your Location'}</label>
        <select
          value={userLocation}
          onChange={(e) => setUserLocation(e.target.value)}
          className="w-full md:w-1/2 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
        >
          {locations.map(loc => (
            <option key={loc} value={loc}>
              {getLocationName(loc)}
            </option>
          ))}
        </select>
      </div>

      {/* Emergency Banner */}
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
        <div className="flex items-center">
          <Heart className="w-5 h-5 text-red-600 mr-2" />
          <div>
            <p className="font-semibold text-red-800">{t.emergency_call || 'Emergency: Call 108'}</p>
            <p className="text-sm text-red-600">{t.ambulance_service || '24/7 Ambulance Service'}</p>
          </div>
        </div>
      </div>

      {/* Content */}
      {loading ? (
        <LoadingSpinner message={t.finding_hospitals} />
      ) : error ? (
        <ErrorMessage message={error} onRetry={fetchHospitals} />
      ) : (
        <>
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            {t.nearest_hospitals || 'Nearest Hospitals in'} {getLocationName(userLocation)}
            <span className="text-sm font-normal text-gray-500 ml-2">({hospitals.length} {t.found || 'found'})</span>
          </h3>
          
          {hospitals.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              {t.no_hospitals || 'No hospitals found for this location.'}
            </div>
          ) : (
            <div className="space-y-4">
              {hospitals.map((hospital, index) => (
                <div key={hospital.id || index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h4 className="text-lg font-semibold text-gray-800">{hospital.name}</h4>
                      <p className="text-sm text-gray-600">{getHospitalType(hospital.type)}</p>
                    </div>
                    {hospital.emergency && (
                      <span className="bg-red-100 text-red-600 text-xs px-2 py-1 rounded font-medium">
                        {t.emergency_24x7 || '24/7 Emergency'}
                      </span>
                    )}
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 mt-3">
                    <div className="flex items-center text-sm text-gray-600">
                      <MapPin className="w-4 h-4 mr-1" />
                      {hospital.distance} {t.away || 'away'}
                    </div>
                    <div className="text-sm text-gray-600">
                      📞 {hospital.phone || 'N/A'}
                    </div>
                  </div>

                  {hospital.address && (
                    <div className="text-sm text-gray-500 mt-2">
                      📍 {hospital.address}
                    </div>
                  )}

                  {hospital.website && (
                    <a
                      href={hospital.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-indigo-600 hover:text-indigo-800 mt-2 inline-block"
                    >
                      🌐 {language === 'telugu' ? 'వెబ్‌సైట్ చూడండి' : 'Visit website'}
                    </a>
                  )}
                  
                  <button 
                    onClick={() => openDirections(hospital)}
                    className="mt-3 w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center"
                  >
                    {t.get_directions || 'Get Directions'}
                    <ChevronRight className="w-4 h-4 ml-1" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* Last Updated */}
      {lastUpdated && (
        <div className="text-xs text-gray-500 mt-4">
          {t.data_updated || 'Data updated'}: {new Date(lastUpdated).toLocaleString()}
        </div>
      )}

      {/* Health Resources */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-blue-50 rounded-lg p-4">
          <h4 className="font-semibold text-blue-800 mb-2">{t.find_doctor || 'Find a Doctor'}</h4>
          <p className="text-sm text-blue-600">{t.find_doctor_desc || 'Search specialists by specialty and location'}</p>
        </div>
        <div className="bg-green-50 rounded-lg p-4">
          <h4 className="font-semibold text-green-800 mb-2">{t.book_appointment || 'Book Appointment'}</h4>
          <p className="text-sm text-green-600">{t.book_appointment_desc || 'Schedule online appointments with ease'}</p>
        </div>
        <div className="bg-purple-50 rounded-lg p-4">
          <h4 className="font-semibold text-purple-800 mb-2">{t.health_records || 'Health Records'}</h4>
          <p className="text-sm text-purple-600">{t.health_records_desc || 'Access your medical history securely'}</p>
        </div>
      </div>
    </div>
  );
}
