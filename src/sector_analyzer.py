from typing import Dict, List
import yfinance as yf
import pandas as pd
import numpy as np

class SectorAnalyzer:
    def __init__(self):
        # Indian energy/power sector peers
        self.peers = {
            'NTPC.NS': 'NTPC Limited',
            'TATAPOWER.NS': 'Tata Power',
            'TORNTPOWER.NS': 'Torrent Power',
            'ADANIGREEN.NS': 'Adani Green Energy',
            'NHPC.NS': 'NHPC Limited',
            'POWERGRID.NS': 'Power Grid Corporation'
        }

    def get_sector_data(self) -> Dict:
        """Fetch and analyze sector-wide metrics"""
        metrics = {
            'pe_ratios': [],
            'debt_equity': [],
            'roe': [],
            'market_caps': [],
            'year_returns': []
        }

        print("\n📊 Fetching Sector Data...")
        for symbol in self.peers.keys():
            try:
                stock = yf.Ticker(symbol)
                info = stock.info
                hist = stock.history(period="1y")
                
                # Get metrics
                metrics['pe_ratios'].append((symbol, info.get('trailingPE', None)))
                metrics['debt_equity'].append((symbol, info.get('debtToEquity', None)))
                metrics['roe'].append((symbol, info.get('returnOnEquity', None)))
                metrics['market_caps'].append((symbol, info.get('marketCap', None)))
                
                # Calculate 1-year return
                if not hist.empty:
                    year_return = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
                    metrics['year_returns'].append((symbol, year_return))
                
                print(f"  ✓ {self.peers[symbol]}")
            except Exception as e:
                print(f"  ✗ Error fetching {symbol}: {str(e)}")
        
        return self._analyze_sector_metrics(metrics)

    def _analyze_sector_metrics(self, metrics: Dict) -> Dict:
        """Analyze sector metrics and return insights"""
        analysis = {}
        
        # PE Ratio Analysis
        valid_pe = [(symbol, pe) for symbol, pe in metrics['pe_ratios'] if pe is not None]
        if valid_pe:
            pes = [pe for _, pe in valid_pe]
            analysis['pe_ratio'] = {
                'median': np.median(pes),
                'mean': np.mean(pes),
                'min': min(pes),
                'max': max(pes),
                'companies': dict(valid_pe)
            }
        
        # Debt/Equity Analysis
        valid_de = [(symbol, de) for symbol, de in metrics['debt_equity'] if de is not None]
        if valid_de:
            des = [de for _, de in valid_de]
            analysis['debt_equity'] = {
                'median': np.median(des),
                'mean': np.mean(des),
                'min': min(des),
                'max': max(des),
                'companies': dict(valid_de)
            }
        
        # ROE Analysis
        valid_roe = [(symbol, roe) for symbol, roe in metrics['roe'] if roe is not None]
        if valid_roe:
            roes = [roe for _, roe in valid_roe]
            analysis['roe'] = {
                'median': np.median(roes),
                'mean': np.mean(roes),
                'min': min(roes),
                'max': max(roes),
                'companies': dict(valid_roe)
            }
        
        # Year Returns Analysis
        valid_returns = [(symbol, ret) for symbol, ret in metrics['year_returns'] if ret is not None]
        if valid_returns:
            returns = [ret for _, ret in valid_returns]
            analysis['year_returns'] = {
                'median': np.median(returns),
                'mean': np.mean(returns),
                'min': min(returns),
                'max': max(returns),
                'companies': dict(valid_returns)
            }
        
        return analysis

    def get_sector_summary(self, stock_data: Dict) -> Dict:
        """Get sector comparison summary for a stock"""
        sector_data = self.get_sector_data()
        summary = {}
        
        # PE Ratio comparison
        if 'pe_ratio' in sector_data and stock_data.get('pe_ratio'):
            pe = stock_data['pe_ratio']
            sector_pe = sector_data['pe_ratio']
            pe_percentile = sum(1 for x in sector_pe['companies'].values() if x < pe) / len(sector_pe['companies'])
            summary['pe_ratio'] = {
                'stock': pe,
                'sector_median': sector_pe['median'],
                'percentile': pe_percentile,
                'assessment': 'high' if pe > sector_pe['median'] else 'low'
            }
        
        # Debt/Equity comparison
        if 'debt_equity' in sector_data and stock_data.get('debt_to_equity'):
            de = stock_data['debt_to_equity']
            sector_de = sector_data['debt_equity']
            de_percentile = sum(1 for x in sector_de['companies'].values() if x < de) / len(sector_de['companies'])
            summary['debt_equity'] = {
                'stock': de,
                'sector_median': sector_de['median'],
                'percentile': de_percentile,
                'assessment': 'high' if de > sector_de['median'] else 'low'
            }
        
        # ROE comparison
        if 'roe' in sector_data and stock_data.get('roe'):
            roe = stock_data['roe']
            sector_roe = sector_data['roe']
            roe_percentile = sum(1 for x in sector_roe['companies'].values() if x < roe) / len(sector_roe['companies'])
            summary['roe'] = {
                'stock': roe,
                'sector_median': sector_roe['median'],
                'percentile': roe_percentile,
                'assessment': 'high' if roe > sector_roe['median'] else 'low'
            }
        
        return summary
