# 📊 AI-Based Swing Trading Assistant Instructions

## 🎯 Objective:
Automate the analysis of stocks for **swing trading** by combining:
- Live market data
- 24-hour news sentiment
- Technical analysis (support, resistance, RSI, MACD, volume)
- Basic fundamental analysis
- Price pattern recognition
- Trade recommendation (entry, target, stop-loss)

---

## ✅ Required Inputs for Each Stock:

### 1. Stock Identity
- Stock Name / Symbol (e.g., INFY, TATAMOTORS)

### 2. 24-Hour News Summary
- Pull headlines and sentiment (positive/neutral/negative)
- Sources: Google News, Moneycontrol, Investing.com

### 3. Technical Indicators (From TradingView or `yfinance`)
- Current Price
- RSI (Relative Strength Index)
- MACD (MACD line & Signal line)
- 50 EMA & 200 EMA
- Volume (last 5 sessions)
- Candlestick pattern detection (optional)
- Chart pattern (breakout, wedge, flag, etc.)

### 4. Support & Resistance
- Recent swing highs/lows
- Manual or AI-derived from price action (last 30 candles)

### 5. Fundamentals (from Screener.in or TickerTape)
- EPS
- PE Ratio
- Debt-to-Equity Ratio
- ROE (Return on Equity)
- Promoter Holding %

---

## 🔍 AI Instructions for Full Analysis:

> **Analyze the stock '[Stock Name]' for swing trading.**  
> Give a complete breakdown of the following:
>
> 1. Summarize last 24-hour news sentiment.  
> 2. Give a technical analysis including:
>    - Support & Resistance levels
>    - Trend direction (uptrend, downtrend, sideways)
>    - RSI, MACD, volume, 50/200 EMA  
> 3. Mention any known chart patterns (e.g., breakout, flag, wedge).  
> 4. Provide key fundamentals: EPS, PE, Debt, ROE, Promoter Holding.  
> 5. Based on the data, recommend:
>    - Entry Price
>    - Target
>    - Stop Loss
>    - Risk/Reward ratio
> 6. Mention if current price is near a breakout or reversal zone.  
> 7. Give a final swing trade rating (Strong Buy / Buy / Avoid / Wait & Watch).

---

## 📈 Expected Output Format (Sample)

