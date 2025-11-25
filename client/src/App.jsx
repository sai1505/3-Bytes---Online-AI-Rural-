// App.jsx - Complete Single File Rural Education Dashboard
import React, { useState, useEffect } from 'react';

const API_BASE = 'http://localhost:8000';

function App() {
  const [language, setLanguage] = useState('en');
  const [state, setState] = useState('Andhra Pradesh');
  const [city, setCity] = useState('Vijayawada');
  const [locations, setLocations] = useState({});
  const [translations, setTranslations] = useState({});
  const [lastUpdated, setLastUpdated] = useState('');
  const [news, setNews] = useState([]);
  const [prices, setPrices] = useState([]);
  const [loadingNews, setLoadingNews] = useState(true);
  const [loadingPrices, setLoadingPrices] = useState(true);

  // Fetch initial data
  useEffect(() => {
    fetchLocations();
    fetchTranslations(language);
  }, []);

  useEffect(() => {
    fetchTranslations(language);
    fetchNews();
  }, [language]);

  useEffect(() => {
    fetchPrices();
  }, [language, state, city]);

  const fetchLocations = async () => {
    try {
      const response = await fetch(`${API_BASE}/locations`);
      const data = await response.json();
      setLocations(data);
      if (data['Andhra Pradesh'] && !city) {
        setCity(Object.keys(data['Andhra Pradesh'])[0]);
      }
    } catch (error) {
      console.error('Error fetching locations:', error);
    }
  };

  const fetchTranslations = async (lang) => {
    try {
      const response = await fetch(`${API_BASE}/translations?lang=${lang}`);
      const data = await response.json();
      setTranslations(data);
    } catch (error) {
      console.error('Error fetching translations:', error);
    }
  };

  const fetchNews = async () => {
    try {
      setLoadingNews(true);
      const response = await fetch(`${API_BASE}/news?lang=${language}`);
      const data = await response.json();
      setNews(data);
      if (data.length && data[0].publishedAt) {
        setLastUpdated(new Date(data[0].publishedAt).toLocaleString());
      }
    } catch (error) {
      console.error('Error fetching news:', error);
      setNews([{ title: "News loading...", description: "Please wait..." }]);
    } finally {
      setLoadingNews(false);
    }
  };

  const fetchPrices = async () => {
    try {
      setLoadingPrices(true);
      const response = await fetch(
        `${API_BASE}/food-prices?lang=${language}&state=${encodeURIComponent(state)}&city=${encodeURIComponent(city)}`
      );
      const data = await response.json();
      setPrices(data);
    } catch (error) {
      console.error('Error fetching prices:', error);
    } finally {
      setLoadingPrices(false);
    }
  };

  const handleRefresh = () => {
    fetchLocations();
    fetchTranslations(language);
    fetchNews();
    fetchPrices();
  };

  const getChangeColor = (change) => {
    if (change > 0) return 'text-green-600';
    if (change < 0) return 'text-red-600';
    return 'text-gray-500';
  };

  const LanguageSelector = () => {
    const languages = [
      { code: 'en', label: 'English', flag: '🇺🇸' },
      { code: 'hi', label: 'हिंदी', flag: '🇮🇳' },
      { code: 'te', label: 'తెలుగు', flag: '🇮🇳' }
    ];

    return (
      <select
        value={language}
        onChange={(e) => {
          setLanguage(e.target.value);
          fetchTranslations(e.target.value);
          fetchNews();
        }}
        className="px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white shadow-sm"
      >
        {languages.map(({ code, label, flag }) => (
          <option key={code} value={code}>
            {flag} {label}
          </option>
        ))}
      </select>
    );
  };

  const LocationSelector = () => {
    const states = Object.keys(locations);

    const handleStateChange = (e) => {
      const newState = e.target.value;
      setState(newState);
      const cities = Object.keys(locations[newState] || {});
      if (cities.length > 0 && city !== cities[0]) {
        setCity(cities[0]);
      }
    };

    const handleCityChange = (e) => {
      setCity(e.target.value);
    };

    return (
      <div className="flex flex-col sm:flex-row gap-2">
        <select
          value={state}
          onChange={handleStateChange}
          className="px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white shadow-sm min-w-[140px]"
        >
          {states.map((stateName) => (
            <option key={stateName} value={stateName}>
              {stateName}
            </option>
          ))}
        </select>

        <select
          value={city}
          onChange={handleCityChange}
          disabled={!state || !locations[state]}
          className="px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white shadow-sm min-w-[140px] disabled:bg-gray-100 disabled:cursor-not-allowed"
        >
          {state && locations[state] && Object.keys(locations[state]).map((cityName) => (
            <option key={cityName} value={cityName}>
              {cityName}
            </option>
          ))}
        </select>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <header className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent mb-4">
            {translations.dashboard_title || 'Rural Education Dashboard'}
          </h1>
          <div className="flex flex-wrap gap-4 justify-center items-center mb-6">
            <LanguageSelector />
            <LocationSelector />
            <button
              onClick={handleRefresh}
              className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-xl font-semibold transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              {translations.refresh || 'Refresh'}
            </button>
          </div>
          {lastUpdated && (
            <p className="text-sm text-gray-600">
              {translations.last_updated || 'Last Updated'}: {lastUpdated}
            </p>
          )}
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* News Section */}
          <section className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100 hover:shadow-2xl transition-all duration-300">
            <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-3">
              📰 {translations.news_today || "Today's News"}
            </h2>

            <div className="space-y-4 max-h-96 overflow-y-auto">
              {loadingNews ? (
                <div className="flex items-center justify-center py-12">
                  <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-green-600"></div>
                </div>
              ) : news.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No news available</p>
              ) : (
                news.map((article, index) => (
                  <article key={index} className="group">
                    <a
                      href={article.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block p-4 rounded-xl hover:bg-gray-50 transition-all duration-200 border-l-4 border-green-500"
                    >
                      <h3 className="font-semibold text-gray-900 group-hover:text-green-600 text-lg mb-2 line-clamp-2">
                        {article.title}
                      </h3>
                      <p className="text-gray-600 text-sm line-clamp-2 mb-3">
                        {article.description}
                      </p>
                      <span className="text-xs text-blue-600 font-medium hover:underline">
                        {translations.read_more || 'Read More'} →
                      </span>
                    </a>
                  </article>
                ))
              )}
            </div>
          </section>

          {/* Prices Section */}
          <section className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100 hover:shadow-2xl transition-all duration-300">
            <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-3">
              💰 {translations.prices_today || "Today's Prices"}
            </h2>

            {loadingPrices ? (
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-2 gap-4">
                {[...Array(6)].map((_, i) => (
                  <div key={i} className="animate-pulse bg-gray-200 h-20 rounded-xl"></div>
                ))}
              </div>
            ) : prices.length === 0 ? (
              <p className="text-gray-500 text-center py-12">No prices available</p>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 gap-4">
                {prices.map((item, index) => (
                  <div key={index} className="group p-4 border border-gray-200 rounded-xl hover:shadow-md transition-all duration-200 hover:border-green-300">
                    <div className="flex items-start gap-3 mb-3">
                      <span className="text-2xl group-hover:scale-110 transition-transform">{item.icon}</span>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-gray-900 text-lg line-clamp-1 mb-1">
                          {item.display_name}
                        </h3>
                        <p className="text-xs text-gray-500">{item.market}</p>
                      </div>
                    </div>
                    <div className="flex items-baseline justify-between">
                      <span className="text-2xl font-bold text-green-600">
                        ₹{item.price}
                      </span>
                      <span className="text-sm font-medium px-2 py-1 rounded-full bg-gray-100">
                        {item.unit}
                      </span>
                    </div>
                    <div className={`text-sm mt-2 flex items-center gap-1 ${getChangeColor(item.change)}`}>
                      {item.change > 0 ? '↑' : item.change < 0 ? '↓' : '→'}
                      {item.change.toFixed(1)}%
                      <span className="ml-1 text-xs">
                        {item.change > 0 ? translations.increase : translations.decrease || (item.change > 0 ? 'increase' : 'decrease')}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}

export default App;
