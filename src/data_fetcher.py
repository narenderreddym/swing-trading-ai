import yfinance as yf
import pandas as pd
from bs4 import BeautifulSoup
import requests
from typing import Dict, List, Tuple
import numpy as np
from datetime import datetime, timedelta
import json

class DataFetcher:
    def __init__(self):
        self.session = requests.Session()

    def get_stock_data(self, symbol: str) -> Dict:
        """Fetch technical indicators and price data from yfinance"""
        stock = yf.Ticker(symbol)
        hist = stock.history(period="60d")
        
        # Calculate technical indicators
        hist['RSI'] = self._calculate_rsi(hist['Close'])
        hist['MACD'], hist['Signal'] = self._calculate_macd(hist['Close'])
        hist['EMA50'] = hist['Close'].ewm(span=50).mean()
        hist['EMA200'] = hist['Close'].ewm(span=200).mean()
        
        # Get last 30 candles for support/resistance
        last_30 = hist.tail(30)
        support_levels = self._find_support_levels(last_30)
        resistance_levels = self._find_resistance_levels(last_30)
        
        # Get last 5 sessions volume
        last_5_volume = hist['Volume'].tail(5).tolist()
        
        return {
            'current_price': hist['Close'].iloc[-1],
            'rsi': hist['RSI'].iloc[-1],
            'macd': hist['MACD'].iloc[-1],
            'macd_signal': hist['Signal'].iloc[-1],
            'ema50': hist['EMA50'].iloc[-1],
            'ema200': hist['EMA200'].iloc[-1],
            'volume_5d': last_5_volume,
            'support_levels': support_levels,
            'resistance_levels': resistance_levels,
            'trend': self._determine_trend(hist),
            'pattern': self._detect_pattern(hist),
            # Add OHLC data for charting
            'open': hist['Open'],
            'high': hist['High'],
            'low': hist['Low'],
            'close': hist['Close'],
            'rsi_series': hist['RSI'],
            'ema50_series': hist['EMA50'],
            'ema200_series': hist['EMA200']
        }

    def get_news_sentiment(self, symbol: str) -> List[Dict]:
        """Fetch and analyze news articles"""
        try:
            # Use yfinance news
            stock = yf.Ticker(symbol)
            news = stock.news
            
            articles = []
            if news:
                for item in news[:5]:
                    articles.append({
                        'title': item.get('title', ''),
                        'summary': item.get('description', '') if 'description' in item else '',
                        'sentiment': self._analyze_sentiment(item.get('title', ''))
                    })
            
            return articles
        except Exception as e:
            print(f"Error fetching news for {symbol}: {str(e)}")
            return []

    def get_fundamentals(self, symbol: str) -> Dict:
        """Fetch fundamental data from yfinance"""
        stock = yf.Ticker(symbol)
        info = stock.info
        
        return {
            'eps': info.get('trailingEps', None),
            'pe_ratio': info.get('trailingPE', None),
            'debt_to_equity': info.get('debtToEquity', None),
            'roe': info.get('returnOnEquity', None),
            'institutional_holders': info.get('institutionalHoldersPercentage', None)
        }

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def _calculate_macd(self, prices: pd.Series) -> Tuple[pd.Series, pd.Series]:
        """Calculate MACD and Signal line"""
        exp1 = prices.ewm(span=12, adjust=False).mean()
        exp2 = prices.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        return macd, signal

    def _find_support_levels(self, data: pd.DataFrame) -> List[float]:
        """Find potential support levels using local minima"""
        local_min = []
        for i in range(1, len(data) - 1):
            if data['Low'].iloc[i] < data['Low'].iloc[i-1] and \
               data['Low'].iloc[i] < data['Low'].iloc[i+1]:
                local_min.append(data['Low'].iloc[i])
        return sorted(list(set([round(x, 2) for x in local_min])))

    def _find_resistance_levels(self, data: pd.DataFrame) -> List[float]:
        """Find potential resistance levels using local maxima"""
        local_max = []
        for i in range(1, len(data) - 1):
            if data['High'].iloc[i] > data['High'].iloc[i-1] and \
               data['High'].iloc[i] > data['High'].iloc[i+1]:
                local_max.append(data['High'].iloc[i])
        return sorted(list(set([round(x, 2) for x in local_max])))

    def _determine_trend(self, data: pd.DataFrame) -> str:
        """Determine the overall trend direction"""
        last_50_close = data['Close'].tail(50)
        slope = np.polyfit(range(len(last_50_close)), last_50_close, 1)[0]
        
        if abs(slope) < 0.1:
            return "sideways"
        return "uptrend" if slope > 0 else "downtrend"

    def _detect_pattern(self, data: pd.DataFrame) -> str:
        """Simple pattern detection"""
        last_20 = data.tail(20)
        highs = last_20['High']
        lows = last_20['Low']
        
        # Check for common patterns
        if all(highs.iloc[i] > highs.iloc[i-1] for i in range(1, len(highs))):
            return "ascending channel"
        elif all(highs.iloc[i] < highs.iloc[i-1] for i in range(1, len(highs))):
            return "descending channel"
        elif max(highs) == highs.iloc[-1]:
            return "potential breakout"
        elif min(lows) == lows.iloc[-1]:
            return "potential breakdown"
        
        return "no clear pattern"

    def _get_news_urls(self, symbol: str) -> List[str]:
        """Get news URLs from Google News"""
        url = f"https://news.google.com/rss/search?q={symbol}+stock&hl=en-US&gl=US&ceid=US:en"
        response = self.session.get(url)
        soup = BeautifulSoup(response.text, 'xml')
        
        urls = []
        for item in soup.find_all('item'):
            urls.append(item.link.text)
        
        return urls

    def _analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis"""
        # This is a basic implementation. You might want to use a more sophisticated
        # approach like NLTK's VADER or a pre-trained transformer model
        positive_words = {'up', 'rise', 'gain', 'positive', 'growth', 'higher', 'surge'}
        negative_words = {'down', 'fall', 'drop', 'negative', 'decline', 'lower', 'plunge'}
        
        words = set(text.lower().split())
        pos_count = len(words.intersection(positive_words))
        neg_count = len(words.intersection(negative_words))
        
        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        return 'neutral'
    
    def get_stock_data_from_df(self, df: pd.DataFrame) -> Dict:
        """Generate technical data dict from custom dataframe"""
        df['RSI'] = self._calculate_rsi(df['Close'])
        df['MACD'], df['Signal'] = self._calculate_macd(df['Close'])
        df['EMA50'] = df['Close'].ewm(span=50).mean()
        df['EMA200'] = df['Close'].ewm(span=200).mean()

        support_levels = self._find_support_levels(df)
        resistance_levels = self._find_resistance_levels(df)

        return {
            'current_price': df['Close'].iloc[-1],
            'rsi': df['RSI'].iloc[-1],
            'macd': df['MACD'].iloc[-1],
            'macd_signal': df['Signal'].iloc[-1],
            'ema50': df['EMA50'].iloc[-1],
            'ema200': df['EMA200'].iloc[-1],
            'volume_5d': df['Volume'].tail(5).tolist(),
            'support_levels': support_levels,
            'resistance_levels': resistance_levels,
            'trend': self._determine_trend(df),
            'pattern': self._detect_pattern(df),
            'open': df['Open'],
            'high': df['High'],
            'low': df['Low'],
            'close': df['Close'],
            'rsi_series': df['RSI'],
            'ema50_series': df['EMA50'],
            'ema200_series': df['EMA200']
        }

