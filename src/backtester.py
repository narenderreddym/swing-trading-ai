import yfinance as yf
import pandas as pd
from typing import List, Dict
from src.analyzer import Analyzer
from src.data_fetcher import DataFetcher
import matplotlib.pyplot as plt

class Backtester:
    def __init__(self, symbol: str, lookback_days: int = 60):
        self.symbol = symbol
        self.lookback_days = lookback_days
        self.analyzer = Analyzer()
        self.fetcher = DataFetcher()
        self.results = []

    def run(self):
        print(f"\n⏱ Running backtest on {self.symbol} for last {self.lookback_days} days...")

        # Download historical data
        stock = yf.Ticker(self.symbol)
        hist = stock.history(period=f"{self.lookback_days}d")

        # Simulate trades over a rolling window
        for i in range(30, len(hist) - 5):  # 30 days for context, 5 days holding
            test_slice = hist.iloc[i-30:i+1]  # 30-day context for indicators
            future_data = hist.iloc[i+1:i+6]  # next 5 days for simulation

            try:
                # Prepare mock technical data from 30-day window
                test_data = self.fetcher.get_stock_data_from_df(test_slice)
                dummy_news = []  # Skipping news for backtesting
                dummy_fundamentals = {
                    'pe_ratio': 20,
                    'debt_to_equity': 0.5,
                    'roe': 0.18,
                    'institutional_holders': 0.6
                }

                result = self.analyzer.analyze_stock(
                    technical_data=test_data,
                    news_data=dummy_news,
                    fundamental_data=dummy_fundamentals
                )

                reco = result['recommendation']
                if reco.rating in ["Strong Buy", "Buy"]:
                    self._simulate_trade(future_data, reco)

            except Exception as e:
                print(f"❌ Error on day {i}: {e}")
                continue

        self._report()

    def _simulate_trade(self, future_df: pd.DataFrame, reco) -> None:
        entry = reco.entry_price
        target = reco.target_price
        stop = reco.stop_loss
        hit_target = False
        hit_stop = False

        for _, row in future_df.iterrows():
            high, low = row['High'], row['Low']
            if low <= stop:
                hit_stop = True
                break
            elif high >= target:
                hit_target = True
                break

        pnl = 0
        if hit_target:
            pnl = target - entry
        elif hit_stop:
            pnl = stop - entry
        else:
            pnl = future_df['Close'].iloc[-1] - entry

        self.results.append({
            'Entry': entry,
            'Target': target,
            'Stop': stop,
            'Exit': entry + pnl,
            'PnL': pnl,
            'Result': 'Target' if hit_target else ('Stop Loss' if hit_stop else 'Hold')
        })

    def _report(self):
        df = pd.DataFrame(self.results)
        if df.empty:
            print("⚠️ No trades simulated.")
            return

        print("\n📊 Backtest Summary")
        print(df)
        print("\n✅ Trades Taken:", len(df))
        print("✔️ Wins:", len(df[df['Result'] == 'Target']))
        print("❌ Losses:", len(df[df['Result'] == 'Stop Loss']))
        print("📈 Avg Gain:", round(df[df['PnL'] > 0]['PnL'].mean(), 2))
        print("📉 Avg Loss:", round(df[df['PnL'] < 0]['PnL'].mean(), 2))
        print("🏁 Net PnL:", round(df['PnL'].sum(), 2))

        # Equity Curve
        df['Cumulative PnL'] = df['PnL'].cumsum()
        df['Cumulative PnL'].plot(title="Equity Curve", grid=True)
        plt.xlabel("Trade #")
        plt.ylabel("Profit/Loss")
        plt.show()
