from typing import Dict, List
from dataclasses import dataclass
import numpy as np
import time

@dataclass
class TradeRecommendation:
    entry_price: float
    target_price: float
    stop_loss: float
    risk_reward_ratio: float
    rating: str
    reason: str

class Analyzer:
    def analyze_stock(self, 
                     technical_data: Dict, 
                     news_data: List[Dict], 
                     fundamental_data: Dict,
                     sector_summary: Dict = None) -> Dict:
        """
        Analyze stock data and provide trading recommendations
        """
        print("\n🔍 Starting Stock Analysis...")
        
        # Analyze technical indicators
        print("\n1️⃣ Technical Analysis Phase")
        technical_score = self._analyze_technical(technical_data)
        
        # Analyze news sentiment
        print("\n2️⃣ News Sentiment Phase")
        news_score = self._analyze_news(news_data)
        
        # Analyze fundamentals
        print("\n3️⃣ Fundamental Analysis Phase")
        fundamental_score = self._analyze_fundamentals(fundamental_data)
        
        # Calculate overall score (weighted average)
        print("\n4️⃣ Calculating Overall Score")
        print("  • Technical Analysis Weight: 50%")
        print("  • News Sentiment Weight: 30%")
        print("  • Fundamental Analysis Weight: 20%")
        
        overall_score = (
            technical_score * 0.5 +  # 50% weight to technical analysis
            news_score * 0.3 +       # 30% weight to news sentiment
            fundamental_score * 0.2   # 20% weight to fundamentals
        )
        print(f"  📊 Overall Score: {overall_score:.2f}")
        
        # Generate trade recommendation
        print("\n5️⃣ Generating Trade Recommendation")
        recommendation = self._generate_recommendation(
            technical_data, 
            overall_score,
            sector_summary
        )
        
        return {
            'technical_score': technical_score,
            'news_score': news_score,
            'fundamental_score': fundamental_score,
            'overall_score': overall_score,
            'recommendation': recommendation
        }

    def _analyze_technical(self, data: Dict) -> float:
        """
        Analyze technical indicators and return a score between 0 and 1
        """
        score = 0
        analysis_log = []
        
        # RSI analysis (oversold < 30, overbought > 70)
        rsi = data['rsi']
        if 30 <= rsi <= 70:
            score += 0.2
            analysis_log.append(f"RSI at {rsi:.2f} - balanced conditions (+0.2)")
        elif rsi < 30:  # Oversold condition
            score += 0.15
            analysis_log.append(f"RSI at {rsi:.2f} - oversold condition (+0.15)")
        else:
            analysis_log.append(f"RSI at {rsi:.2f} - overbought condition (+0)")
        
        # MACD analysis
        if data['macd'] > data['macd_signal']:
            score += 0.2
            analysis_log.append(f"MACD ({data['macd']:.3f}) above signal ({data['macd_signal']:.3f}) - bullish (+0.2)")
        else:
            analysis_log.append(f"MACD ({data['macd']:.3f}) below signal ({data['macd_signal']:.3f}) - bearish (+0)")
        
        # EMA analysis
        if data['current_price'] > data['ema50'] > data['ema200']:
            score += 0.2
            analysis_log.append(f"Price > EMA50 > EMA200 - Strong uptrend (+0.2)")
        elif data['ema50'] < data['ema200'] and data['current_price'] < data['ema50']:
            score -= 0.1
            analysis_log.append(f"Price < EMA50 < EMA200 - Strong downtrend (-0.1)")
        else:
            analysis_log.append("EMAs show mixed signals (+0)")
        
        # Volume analysis
        avg_volume = np.mean(data['volume_5d'])
        if data['volume_5d'][-1] > avg_volume:
            score += 0.1
            analysis_log.append(f"Volume ({data['volume_5d'][-1]:.0f}) above 5-day average ({avg_volume:.0f}) (+0.1)")
        else:
            analysis_log.append(f"Volume ({data['volume_5d'][-1]:.0f}) below 5-day average ({avg_volume:.0f}) (+0)")
        
        # Trend analysis
        if data['trend'] == 'uptrend':
            score += 0.2
            analysis_log.append("Price in uptrend (+0.2)")
        elif data['trend'] == 'downtrend':
            score -= 0.1
            analysis_log.append("Price in downtrend (-0.1)")
        else:
            analysis_log.append("Price moving sideways (+0)")
        
        # Pattern analysis
        if data['pattern'] in ['potential breakout', 'ascending channel']:
            score += 0.1
            analysis_log.append(f"Detected {data['pattern']} pattern (+0.1)")
        else:
            analysis_log.append(f"Pattern: {data['pattern']} (+0)")
        
        print("\n📊 Technical Analysis:")
        for log in analysis_log:
            print(f"  • {log}")
        print(f"  📈 Technical Score: {score:.2f}")
        
        return max(0, min(1, score))  # Ensure score is between 0 and 1

    def _analyze_news(self, news_data: List[Dict]) -> float:
        """
        Enhanced news analysis that considers:
        - Sentiment intensity
        - Keywords and their impact
        - Source credibility
        - Article recency
        - Trading-related terms
        """
        print("\n📰 News Analysis:")
        if not news_data:
            print("  • No recent news articles found (neutral score: 0.5)")
            return 0.5

        # Source credibility weights
        source_weights = {
            'reuters': 1.0,
            'bloomberg': 1.0,
            'ft': 1.0,
            'wsj': 1.0,
            'moneycontrol': 0.9,
            'investing.com': 0.9,
            'yahoo': 0.8,
            'seekingalpha': 0.8,
            'default': 0.7
        }

        # Trading-related keywords and their impact weights
        positive_keywords = {
            'upgrade': 0.3,
            'buy rating': 0.3,
            'outperform': 0.3,
            'beat earnings': 0.4,
            'new contract': 0.2,
            'partnership': 0.2,
            'expansion': 0.2,
            'launch': 0.2,
            'positive guidance': 0.3,
            'strong growth': 0.3
        }

        negative_keywords = {
            'downgrade': -0.3,
            'sell rating': -0.3,
            'underperform': -0.3,
            'miss earnings': -0.4,
            'lawsuit': -0.2,
            'investigation': -0.2,
            'default': -0.4,
            'bankruptcy': -0.4,
            'negative guidance': -0.3,
            'weak outlook': -0.3
        }

        article_scores = []
        current_time = time.time()
        
        for article in news_data:
            # Base sentiment score
            base_score = {
                'positive': 0.7,
                'very positive': 0.9,
                'neutral': 0.5,
                'negative': 0.3,
                'very negative': 0.1
            }.get(article['sentiment'], 0.5)
            
            # Source credibility weighting
            source = article.get('source', '').lower()
            source_weight = next((weight for key, weight in source_weights.items() 
                               if key in source), source_weights['default'])
            
            # Keyword impact
            keyword_impact = 0
            title_and_summary = (article.get('title', '') + ' ' + 
                               article.get('summary', '')).lower()
            
            for keyword, impact in positive_keywords.items():
                if keyword in title_and_summary:
                    keyword_impact += impact
                    print(f"    📈 Found positive keyword: {keyword}")
            
            for keyword, impact in negative_keywords.items():
                if keyword in title_and_summary:
                    keyword_impact += impact
                    print(f"    📉 Found negative keyword: {keyword}")
            
            # Time decay factor (full weight for articles < 12h old, decreasing after)
            hours_old = (current_time - article.get('timestamp', current_time)) / 3600
            time_weight = min(1.0, max(0.5, 1 - (hours_old - 12) / 36))
            
            # Calculate final article score
            article_score = (base_score + keyword_impact) * source_weight * time_weight
            article_score = max(0, min(1, article_score))  # Clamp between 0 and 1
            
            article_scores.append(article_score)
            
            # Print detailed analysis
            print(f"  • {article['title'][:100]}...")
            print(f"    Base Sentiment: {article['sentiment']} (score: {base_score:.2f})")
            print(f"    Source: {article.get('source', 'Unknown')} (weight: {source_weight:.2f})")
            print(f"    Age: {hours_old:.1f}h (weight: {time_weight:.2f})")
            if keyword_impact != 0:
                print(f"    Keyword Impact: {keyword_impact:+.2f}")
            print(f"    Final Score: {article_score:.2f}")
        
        # Calculate weighted average, giving more weight to stronger sentiments
        if article_scores:
            sorted_scores = sorted(article_scores)
            weights = np.linspace(0.5, 1.0, len(sorted_scores))  # More weight to extreme scores
            avg_score = np.average(sorted_scores, weights=weights)
        else:
            avg_score = 0.5
        
        print(f"\n  📰 Final News Score: {avg_score:.2f}")
        return avg_score

    def _analyze_fundamentals(self, data: Dict) -> float:
        """
        Analyze fundamental data and return a score between 0 and 1
        """
        score = 0.5  # Start neutral
        analysis_log = ["Starting with neutral score (0.5)"]
        
        # PE Ratio analysis (assuming reasonable PE between 10-25)
        if data['pe_ratio']:
            if 10 <= data['pe_ratio'] <= 25:
                score += 0.1
                analysis_log.append(f"PE Ratio {data['pe_ratio']:.2f} is in healthy range (+0.1)")
            elif data['pe_ratio'] > 25:
                score -= 0.1
                analysis_log.append(f"PE Ratio {data['pe_ratio']:.2f} is high (-0.1)")
            else:
                analysis_log.append(f"PE Ratio {data['pe_ratio']:.2f} is low (+0)")
        else:
            analysis_log.append("PE Ratio not available")
        
        # Debt to Equity analysis
        if data['debt_to_equity']:
            if data['debt_to_equity'] < 1:
                score += 0.1
                analysis_log.append(f"Debt/Equity {data['debt_to_equity']:.2f} is low (+0.1)")
            elif data['debt_to_equity'] > 2:
                score -= 0.1
                analysis_log.append(f"Debt/Equity {data['debt_to_equity']:.2f} is high (-0.1)")
            else:
                analysis_log.append(f"Debt/Equity {data['debt_to_equity']:.2f} is moderate (+0)")
        else:
            analysis_log.append("Debt/Equity ratio not available")
        
        # ROE analysis
        if data['roe']:
            if data['roe'] > 0.15:  # 15% or better
                score += 0.1
                analysis_log.append(f"ROE {data['roe']*100:.1f}% is strong (+0.1)")
            elif data['roe'] < 0:
                score -= 0.1
                analysis_log.append(f"ROE {data['roe']*100:.1f}% is negative (-0.1)")
            else:
                analysis_log.append(f"ROE {data['roe']*100:.1f}% is moderate (+0)")
        else:
            analysis_log.append("ROE not available")
        
        # Institutional holders analysis
        if data['institutional_holders']:
            if data['institutional_holders'] > 0.7:  # More than 70% institutional holding
                score += 0.1
                analysis_log.append(f"Strong institutional holding at {data['institutional_holders']*100:.1f}% (+0.1)")
            else:
                analysis_log.append(f"Moderate institutional holding at {data['institutional_holders']*100:.1f}% (+0)")
        else:
            analysis_log.append("Institutional holding data not available")
        
        print("\n📝 Fundamental Analysis:")
        for log in analysis_log:
            print(f"  • {log}")
        print(f"  💼 Fundamental Score: {score:.2f}")
        
        return max(0, min(1, score))  # Ensure score is between 0 and 1

    def _generate_recommendation(self, 
                              technical_data: Dict, 
                              overall_score: float,
                              sector_summary: Dict = None) -> TradeRecommendation:
        """
        Generate trade recommendation based on analysis with enhanced risk management
        """
        current_price = technical_data['current_price']
        
        # Enhanced rating system with sector context
        base_rating = "Strong Buy" if overall_score >= 0.8 else \
                     "Buy" if overall_score >= 0.6 else \
                     "Avoid" if overall_score <= 0.3 else "Wait & Watch"
        
        # Adjust rating based on sector comparison
        if sector_summary:
            sector_concerns = []
            if sector_summary.get('pe_ratio', {}).get('assessment') == 'high':
                sector_concerns.append("high PE ratio vs sector")
            if sector_summary.get('debt_equity', {}).get('assessment') == 'high':
                sector_concerns.append("high debt vs sector")
            if sector_summary.get('roe', {}).get('assessment') == 'low':
                sector_concerns.append("below-sector ROE")
            
            # Downgrade rating if multiple sector concerns
            if len(sector_concerns) >= 2:
                if base_rating == "Strong Buy":
                    base_rating = "Buy"
                elif base_rating == "Buy":
                    base_rating = "Wait & Watch"
        
        # Enhanced support and resistance detection
        supports = technical_data['support_levels']
        resistances = technical_data['resistance_levels']
        
        # Find strongest support (multiple price touches)
        support_clusters = {}
        for s in supports:
            cluster_key = round(s, 1)  # Group similar levels
            support_clusters[cluster_key] = support_clusters.get(cluster_key, 0) + 1
        
        strongest_support = max(support_clusters.items(), key=lambda x: x[1])[0]
        nearest_support = max([s for s in supports if s < current_price] or [current_price * 0.95])
        
        # Find strongest resistance
        resistance_clusters = {}
        for r in resistances:
            cluster_key = round(r, 1)
            resistance_clusters[cluster_key] = resistance_clusters.get(cluster_key, 0) + 1
            
        strongest_resistance = min(resistance_clusters.items(), key=lambda x: x[1])[0]
        nearest_resistance = min([r for r in resistances if r > current_price] or [current_price * 1.05])
        
        # Set entry, target, and stop loss with enhanced risk management
        entry_price = current_price
        target_price = max(nearest_resistance, current_price * 1.02)  # At least 2% upside
        stop_loss = min(nearest_support * 0.99, current_price * 0.98)  # At most 2% downside
        
        # Calculate and validate risk/reward ratio
        risk = entry_price - stop_loss
        reward = target_price - entry_price
        risk_reward_ratio = round(reward / risk, 2) if risk > 0 else 0
        
        # Adjust rating based on risk/reward
        MIN_RISK_REWARD = 1.5  # Minimum 1.5:1 reward-to-risk ratio
        if risk_reward_ratio < MIN_RISK_REWARD:
            if base_rating in ["Strong Buy", "Buy"]:
                base_rating = "Wait & Watch"
        
        # Generate reason for recommendation
        reason = self._generate_reason(technical_data, base_rating, overall_score)
        
        return TradeRecommendation(
            entry_price=round(entry_price, 2),
            target_price=round(target_price, 2),
            stop_loss=round(stop_loss, 2),
            risk_reward_ratio=risk_reward_ratio,
            rating=base_rating,
            reason=reason
        )

    def _generate_reason(self, 
                        technical_data: Dict, 
                        rating: str, 
                        score: float) -> str:
        """
        Generate a reason for the trade recommendation
        """
        reasons = []
        
        # Technical reasons
        if technical_data['trend'] == 'uptrend':
            reasons.append("Stock is in an uptrend")
        if technical_data['macd'] > technical_data['macd_signal']:
            reasons.append("MACD shows bullish momentum")
        if 30 <= technical_data['rsi'] <= 70:
            reasons.append("RSI indicates balanced conditions")
        elif technical_data['rsi'] < 30:
            reasons.append("Stock is oversold")
        elif technical_data['rsi'] > 70:
            reasons.append("Stock is overbought")
        
        # Pattern reason
        if technical_data['pattern'] != 'no clear pattern':
            reasons.append(f"Showing {technical_data['pattern']} pattern")
        
        # Create final reason string
        if reasons:
            reason = f"{rating} recommendation ({score:.2f}) because: {'; '.join(reasons)}"
        else:
            reason = f"{rating} recommendation based on overall analysis score of {score:.2f}"
        
        return reason
