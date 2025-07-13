import sys
from datetime import datetime
from src.data_fetcher import DataFetcher
from src.analyzer import Analyzer
from src.sector_analyzer import SectorAnalyzer
import json
from pathlib import Path
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def analyze_stock(symbol: str, save_path: Path) -> None:
    """Analyze a stock and save the results"""
    print(f"\n{'='*50}")
    print(f"🔎 Starting Analysis for {symbol}")
    print(f"{'='*50}")
    
    # Initialize components
    fetcher = DataFetcher()
    analyzer = Analyzer()
    sector_analyzer = SectorAnalyzer()
    
    try:
        print("\n1️⃣ Fetching Technical Data...")
        technical_data = fetcher.get_stock_data(symbol)
        print(f"  • Current Price: {technical_data['current_price']:.2f}")
        print(f"  • RSI: {technical_data['rsi']:.2f}")
        print(f"  • MACD: {technical_data['macd']:.3f}")
        print(f"  • Trend: {technical_data['trend']}")
        print(f"  • Pattern: {technical_data['pattern']}")
        
        print("\n2️⃣ Fetching News Data...")
        news_data = fetcher.get_news_sentiment(symbol)
        if not news_data:
            print("  • No recent news found")
        
        print("\n3️⃣ Fetching Fundamental Data...")
        fundamental_data = fetcher.get_fundamentals(symbol)
        print(f"  • EPS: {fundamental_data['eps']}")
        print(f"  • P/E Ratio: {fundamental_data['pe_ratio']:.2f}" if fundamental_data['pe_ratio'] else "  • P/E Ratio: N/A")
        print(f"  • Debt/Equity: {fundamental_data['debt_to_equity']:.2f}" if fundamental_data['debt_to_equity'] else "  • Debt/Equity: N/A")
        print(f"  • ROE: {fundamental_data['roe']*100:.2f}%" if fundamental_data['roe'] else "  • ROE: N/A")
        
        print("\n4️⃣ Analyzing Sector Comparison...")
        sector_summary = sector_analyzer.get_sector_summary(fundamental_data)
        
        if sector_summary.get('pe_ratio'):
            print(f"  • P/E Ratio vs Sector: {sector_summary['pe_ratio']['assessment'].upper()}")
            print(f"    Stock: {sector_summary['pe_ratio']['stock']:.2f}")
            print(f"    Sector Median: {sector_summary['pe_ratio']['sector_median']:.2f}")
            print(f"    Percentile: {sector_summary['pe_ratio']['percentile']*100:.0f}%")
            
        if sector_summary.get('debt_equity'):
            print(f"  • Debt/Equity vs Sector: {sector_summary['debt_equity']['assessment'].upper()}")
            print(f"    Stock: {sector_summary['debt_equity']['stock']:.2f}")
            print(f"    Sector Median: {sector_summary['debt_equity']['sector_median']:.2f}")
            print(f"    Percentile: {sector_summary['debt_equity']['percentile']*100:.0f}%")
            
        if sector_summary.get('roe'):
            print(f"  • ROE vs Sector: {sector_summary['roe']['assessment'].upper()}")
            print(f"    Stock: {sector_summary['roe']['stock']*100:.2f}%")
            print(f"    Sector Median: {sector_summary['roe']['sector_median']*100:.2f}%")
            print(f"    Percentile: {sector_summary['roe']['percentile']*100:.0f}%")
        
        # Analyze the data
        analysis = analyzer.analyze_stock(technical_data, news_data, fundamental_data, sector_summary)
        
        # Prepare results
        results = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "technical_data": {
                "current_price": technical_data["current_price"],
                "rsi": technical_data["rsi"],
                "macd": technical_data["macd"],
                "macd_signal": technical_data["macd_signal"],
                "trend": technical_data["trend"],
                "pattern": technical_data["pattern"]
            },
            "support_resistance": {
                "support_levels": technical_data["support_levels"],
                "resistance_levels": technical_data["resistance_levels"]
            },
            "news": news_data,
            "fundamentals": fundamental_data,
            "analysis": {
                "technical_score": analysis["technical_score"],
                "news_score": analysis["news_score"],
                "fundamental_score": analysis["fundamental_score"],
                "overall_score": analysis["overall_score"],
                "recommendation": {
                    "rating": analysis["recommendation"].rating,
                    "entry_price": analysis["recommendation"].entry_price,
                    "target_price": analysis["recommendation"].target_price,
                    "stop_loss": analysis["recommendation"].stop_loss,
                    "risk_reward_ratio": analysis["recommendation"].risk_reward_ratio,
                    "reason": analysis["recommendation"].reason
                }
            }
        }
        
        # Save results
        output_file = save_path / f"{symbol}_analysis_{datetime.now().strftime('%Y%m%d')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=4)
        
        # Create visualization
        create_analysis_chart(symbol, technical_data, save_path)
        
        print(f"✅ Analysis completed for {symbol}")
        print(f"📈 Rating: {analysis['recommendation'].rating}")
        print(f"💰 Entry: {analysis['recommendation'].entry_price:.2f}")
        print(f"🎯 Target: {analysis['recommendation'].target_price:.2f}")
        print(f"🛑 Stop Loss: {analysis['recommendation'].stop_loss:.2f}")
        print(f"📊 Risk/Reward: {analysis['recommendation'].risk_reward_ratio}")
        print(f"📝 {analysis['recommendation'].reason}")
        print(f"\nDetailed analysis saved to {output_file}")
        
    except Exception as e:
        print(f"❌ Error analyzing {symbol}: {str(e)}")

def create_analysis_chart(symbol: str, technical_data: dict, save_path: Path):
    """Create and save a technical analysis chart"""
    # Create figure with secondary y-axis
    fig = make_subplots(rows=2, cols=1, 
                       vertical_spacing=0.03,
                       subplot_titles=(f'{symbol} Price', 'RSI'),
                       shared_xaxes=True)
    
    # Add candlestick
    fig.add_trace(go.Candlestick(
        open=technical_data['open'],
        high=technical_data['high'],
        low=technical_data['low'],
        close=technical_data['close'],
        name='Price'
    ), row=1, col=1)
    
    # Add EMA lines
    fig.add_trace(go.Scatter(
        y=technical_data['ema50_series'],
        name='50 EMA',
        line=dict(color='orange')
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        y=technical_data['ema200_series'],
        name='200 EMA',
        line=dict(color='blue')
    ), row=1, col=1)
    
    # Add RSI
    fig.add_trace(go.Scatter(
        y=technical_data['rsi_series'],
        name='RSI',
        line=dict(color='purple')
    ), row=2, col=1)
    
    # Add horizontal lines for RSI
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
    
    # Update layout
    fig.update_layout(
        title=f"{symbol} Technical Analysis - {datetime.now().strftime('%Y-%m-%d')}",
        yaxis_title="Price",
        yaxis2_title="RSI",
        xaxis_rangeslider_visible=False
    )
    
    # Save chart
    chart_path = save_path / f"{symbol}_chart_{datetime.now().strftime('%Y%m%d')}.html"
    fig.write_html(str(chart_path))

def main():
    if len(sys.argv) < 2:
        print("Please provide at least one stock symbol")
        print("Usage: python main.py SYMBOL1 [SYMBOL2 SYMBOL3 ...]")
        sys.exit(1)
    
    # Create output directory
    output_dir = Path("output") / datetime.now().strftime("%Y%m%d")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Analyze each symbol
    for symbol in sys.argv[1:]:
        analyze_stock(symbol.upper(), output_dir)

if __name__ == "__main__":
    main()
