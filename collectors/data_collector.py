"""
MEGABOT Data Collector
Collects data from 3 sources:
1. FRED - Macro liquidity indicators
2. OpenBB/yfinance - Stock data
3. Xscrap - Twitter expert tweets
"""

import sys
import json
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Add FRED to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "FRED"))

from liquidity_monitor import LiquidityMonitor

# Add config
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.config import Config


class DataCollector:
    """Unified data collector for all sources"""

    def __init__(self):
        self.config = Config()

        # Initialize FRED monitor
        self.fred_monitor = LiquidityMonitor(
            fred_api_key=self.config.FRED_API_KEY
        )

        print("[DataCollector] Initialized")

    # === 1. FRED DATA ===

    def collect_fred_data(self, days_back: int = 90) -> Dict:
        """
        Collect macro liquidity data from FRED

        Returns:
            {
                'indicators': {...},
                'analysis': {...},
                'score': float,
                'timestamp': str
            }
        """
        print("[FRED] Collecting liquidity indicators...")

        indicators = self.fred_monitor.get_all_indicators(days_back=days_back)

        if not indicators:
            print("[FRED] [!]  No data received!")
            return None

        # Analyze conditions
        analysis = self.fred_monitor.analyze_liquidity_conditions(indicators)

        # Extract key data
        result = {
            'timestamp': datetime.now().isoformat(),
            'score': analysis['overall_score'],
            'interpretation': analysis['interpretation'],
            'regime': analysis.get('market_regime', {}),
            'alerts': analysis.get('alerts', []),
            'signals': analysis.get('signals', []),
            'patterns': analysis.get('patterns', {}),
            'percentiles': analysis.get('percentiles', {}),

            # Key indicators (simplified)
            'indicators': {
                'reserves': indicators.get('reserves', {}).get('current'),
                'tga': indicators.get('tga', {}).get('current'),
                'reverse_repo': indicators.get('reverse_repo', {}).get('current'),
                'sofr_iorb_spread': indicators.get('sofr_iorb_spread', {}).get('current'),
                'vix': indicators.get('vix', {}).get('current'),
                'yield_curve': indicators.get('yield_curve', {}).get('current'),
                'nfci': indicators.get('fin_conditions', {}).get('current'),
                'm2': indicators.get('m2', {}).get('current'),
            }
        }

        print(f"[FRED] [OK] Score: {result['score']:.1f} | Regime: {result['regime'].get('regime', 'N/A')}")

        return result

    # === 2. STOCK DATA ===

    def collect_stock_data(self, ticker: str, period: str = "3mo") -> Dict:
        """
        Collect stock fundamentals and technicals using yfinance

        Args:
            ticker: Stock ticker (e.g. "AAPL")
            period: Data period ("1mo", "3mo", "1y", etc.)

        Returns:
            {
                'ticker': str,
                'price': float,
                'fundamentals': {...},
                'technicals': {...},
                'score': float,
                'timestamp': str
            }
        """
        print(f"[STOCK] Collecting data for {ticker}...")

        try:
            stock = yf.Ticker(ticker)

            # Get current data
            info = stock.info
            history = stock.history(period=period)

            if history.empty:
                print(f"[STOCK] [!]  No historical data for {ticker}")
                return None

            current_price = history['Close'].iloc[-1]

            # === FUNDAMENTALS ===
            fundamentals = {
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'peg_ratio': info.get('pegRatio'),
                'price_to_book': info.get('priceToBook'),
                'market_cap': info.get('marketCap'),
                'revenue': info.get('totalRevenue'),
                'profit_margin': info.get('profitMargins'),
                'roe': info.get('returnOnEquity'),
                'debt_to_equity': info.get('debtToEquity'),
                'beta': info.get('beta'),
                'dividend_yield': info.get('dividendYield'),
            }

            # === TECHNICALS ===
            technicals = self._calculate_technicals(history)

            # === SCORING ===
            score = self._score_stock(fundamentals, technicals, info)

            result = {
                'ticker': ticker,
                'timestamp': datetime.now().isoformat(),
                'price': float(current_price),
                'change_1d': float(history['Close'].pct_change().iloc[-1] * 100),
                'volume': int(history['Volume'].iloc[-1]),
                'fundamentals': fundamentals,
                'technicals': technicals,
                'score': score,
                'company': {
                    'name': info.get('longName', ticker),
                    'sector': info.get('sector'),
                    'industry': info.get('industry'),
                },
            }

            print(f"[STOCK] [OK] {ticker}: ${current_price:.2f} | Score: {score:.1f}")

            return result

        except Exception as e:
            print(f"[STOCK] [X] Error collecting {ticker}: {e}")
            return None

    def _calculate_technicals(self, history: pd.DataFrame) -> Dict:
        """Calculate technical indicators"""
        close = history['Close']

        # Moving averages
        ma_20 = close.rolling(20).mean().iloc[-1]
        ma_50 = close.rolling(50).mean().iloc[-1]
        ma_200 = close.rolling(200).mean().iloc[-1] if len(close) >= 200 else None

        current_price = close.iloc[-1]

        # RSI (14-day)
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        rsi_current = rsi.iloc[-1]

        # Bollinger Bands
        bb_middle = close.rolling(20).mean()
        bb_std = close.rolling(20).std()
        bb_upper = bb_middle + (2 * bb_std)
        bb_lower = bb_middle - (2 * bb_std)

        return {
            'ma_20': float(ma_20),
            'ma_50': float(ma_50),
            'ma_200': float(ma_200) if ma_200 else None,
            'price_vs_ma20': float((current_price / ma_20 - 1) * 100),
            'price_vs_ma50': float((current_price / ma_50 - 1) * 100),
            'rsi': float(rsi_current),
            'golden_cross': bool(ma_50 > ma_200) if ma_200 else None,
            'death_cross': bool(ma_50 < ma_200) if ma_200 else None,
            'bb_position': float((current_price - bb_lower.iloc[-1]) / (bb_upper.iloc[-1] - bb_lower.iloc[-1]))
        }

    def _score_stock(self, fundamentals: Dict, technicals: Dict, info: Dict) -> float:
        """
        Score stock from -100 to +100 based on fundamentals and technicals

        Positive = bullish, Negative = bearish
        """
        score = 0

        # === FUNDAMENTALS (max ±40 points) ===

        # P/E ratio (lower is better, but not too low)
        pe = fundamentals.get('pe_ratio')
        if pe:
            if pe < 15:
                score += 10
            elif pe < 25:
                score += 5
            elif pe > 40:
                score -= 10

        # ROE (higher is better)
        roe = fundamentals.get('roe')
        if roe:
            if roe > 0.20:
                score += 10
            elif roe > 0.15:
                score += 5
            elif roe < 0.05:
                score -= 10

        # Debt/Equity (lower is better)
        de = fundamentals.get('debt_to_equity')
        if de:
            if de < 0.5:
                score += 5
            elif de > 2.0:
                score -= 10

        # Profit margin
        pm = fundamentals.get('profit_margin')
        if pm:
            if pm > 0.20:
                score += 10
            elif pm > 0.10:
                score += 5
            elif pm < 0:
                score -= 15

        # === TECHNICALS (max ±60 points) ===

        # RSI
        rsi = technicals.get('rsi')
        if rsi:
            if rsi < 30:
                score += 20  # Oversold - bullish
            elif rsi < 40:
                score += 10
            elif rsi > 70:
                score -= 20  # Overbought - bearish
            elif rsi > 60:
                score -= 10

        # Price vs MA
        if technicals.get('price_vs_ma50', 0) > 0:
            score += 15  # Above MA50 - bullish
        else:
            score -= 15

        # Golden/Death cross
        if technicals.get('golden_cross'):
            score += 15
        elif technicals.get('death_cross'):
            score -= 15

        # Momentum (price vs MA20)
        ma20_diff = technicals.get('price_vs_ma20', 0)
        if ma20_diff > 5:
            score += 10  # Strong uptrend
        elif ma20_diff < -5:
            score -= 10  # Strong downtrend

        # Clamp to -100, 100
        return max(-100, min(100, score))

    # === 3. TWITTER DATA ===

    def collect_twitter_data(self, max_age_hours: int = 24) -> Dict:
        """
        Collect recent tweets from experts (from Xscrap JSON files)

        Args:
            max_age_hours: Only tweets from last N hours

        Returns:
            {
                'tweets': List[dict],
                'sentiment_score': float,
                'experts_count': int,
                'timestamp': str
            }
        """
        print("[TWITTER] Collecting expert tweets...")

        # Look for JSON files in Xscrap cache
        cache_dir = self.config.TWITTER_DATA_DIR

        if not cache_dir.exists():
            print(f"[TWITTER] [!]  Cache directory not found: {cache_dir}")
            return None

        # Find all JSON files
        json_files = list(cache_dir.glob("*.json"))

        if not json_files:
            print("[TWITTER] [!]  No JSON files found in cache")
            return None

        # Collect tweets from all files
        all_tweets = []
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    # Handle different JSON structures
                    if isinstance(data, list):
                        tweets = data
                    elif isinstance(data, dict) and 'tweets' in data:
                        tweets = data['tweets']
                    else:
                        continue

                    # Filter recent tweets
                    for tweet in tweets:
                        # Try to parse timestamp
                        tweet_time = self._parse_tweet_time(tweet)

                        if tweet_time:
                            # Remove timezone for comparison (if present)
                            tweet_time_naive = tweet_time.replace(tzinfo=None) if tweet_time.tzinfo else tweet_time
                            if tweet_time_naive > cutoff_time:
                                all_tweets.append(tweet)

            except Exception as e:
                print(f"[TWITTER] [!]  Error reading {json_file.name}: {e}")
                continue

        if not all_tweets:
            print("[TWITTER] [!]  No recent tweets found")
            return None

        # Analyze sentiment
        sentiment_score = self._analyze_twitter_sentiment(all_tweets)

        # Get unique experts
        experts = set(tweet.get('user', {}).get('username', '') for tweet in all_tweets)

        result = {
            'timestamp': datetime.now().isoformat(),
            'tweets': all_tweets[:50],  # Limit to 50 most recent
            'tweets_count': len(all_tweets),
            'experts_count': len(experts),
            'sentiment_score': sentiment_score,
            'experts': list(experts),
        }

        print(f"[TWITTER] [OK] {len(all_tweets)} tweets | {len(experts)} experts | Sentiment: {sentiment_score:.1f}")

        return result

    def _parse_tweet_time(self, tweet: Dict) -> Optional[datetime]:
        """Parse tweet timestamp (handles multiple formats)"""
        # Try different timestamp fields
        timestamp = tweet.get('created_at') or tweet.get('timestamp') or tweet.get('date')

        if not timestamp:
            return None

        try:
            # Try ISO format
            return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except:
            try:
                # Try Twitter format: "Wed Oct 10 20:19:24 +0000 2018"
                return datetime.strptime(timestamp, '%a %b %d %H:%M:%S %z %Y')
            except:
                return None

    def _analyze_twitter_sentiment(self, tweets: List[Dict]) -> float:
        """
        Analyze sentiment of tweets (simple keyword-based)
        Returns score from -100 (very bearish) to +100 (very bullish)
        """
        # Bullish keywords
        bullish_words = [
            'wzrost', 'rośnie', 'kupuj', 'buy', 'bullish', 'pump', 'moon',
            'wzrostowy', 'pozytywny', 'szansa', 'okazja', 'ath', 'breakout',
            'strong', 'mocny', 'ekspansja', 'liquid', 'płynność'
        ]

        # Bearish keywords
        bearish_words = [
            'spadek', 'spada', 'sprzedaj', 'sell', 'bearish', 'dump', 'crash',
            'spadkowy', 'negatywny', 'ryzyko', 'kryzys', 'correction', 'short',
            'weak', 'słaby', 'recesja', 'napięcia', 'stress'
        ]

        bullish_count = 0
        bearish_count = 0
        total_tweets = len(tweets)

        for tweet in tweets:
            text = tweet.get('text', '').lower()

            # Count keywords
            for word in bullish_words:
                if word in text:
                    bullish_count += 1

            for word in bearish_words:
                if word in text:
                    bearish_count += 1

        # Calculate sentiment
        if total_tweets == 0:
            return 0

        # Normalize to -100 to +100
        net_sentiment = bullish_count - bearish_count
        max_possible = total_tweets * 3  # Assume max 3 keywords per tweet

        sentiment_score = (net_sentiment / max_possible) * 100 if max_possible > 0 else 0

        return max(-100, min(100, sentiment_score))

    # === UNIFIED COLLECTION ===

    def collect_all(self, ticker: str) -> Dict:
        """
        Collect all data sources for a given stock ticker

        Returns:
            {
                'timestamp': str,
                'ticker': str,
                'fred': {...},
                'stock': {...},
                'twitter': {...},
                'combined_score': float
            }
        """
        print(f"\n{'='*60}")
        print(f"[MEGABOT] Collecting all data for {ticker}")
        print(f"{'='*60}\n")

        # Collect from all sources
        fred_data = self.collect_fred_data()
        stock_data = self.collect_stock_data(ticker)
        twitter_data = self.collect_twitter_data()

        # Calculate combined score
        combined_score = self._calculate_combined_score(
            fred_data,
            stock_data,
            twitter_data
        )

        result = {
            'timestamp': datetime.now().isoformat(),
            'ticker': ticker,
            'fred': fred_data,
            'stock': stock_data,
            'twitter': twitter_data,
            'combined_score': combined_score,
        }

        print(f"\n{'='*60}")
        print(f"[MEGABOT] [OK] Data collection complete!")
        fred_score = f"{fred_data['score']:.1f}" if fred_data else "N/A"
        stock_score = f"{stock_data['score']:.1f}" if stock_data else "N/A"
        twitter_score = f"{twitter_data['sentiment_score']:.1f}" if twitter_data else "N/A"
        print(f"  FRED Score: {fred_score}")
        print(f"  Stock Score: {stock_score}")
        print(f"  Twitter Sentiment: {twitter_score}")
        print(f"  COMBINED SCORE: {combined_score:.1f}")
        print(f"{'='*60}\n")

        return result

    def _calculate_combined_score(self, fred_data, stock_data, twitter_data) -> float:
        """Calculate weighted combined score from all sources"""
        weights = self.config.WEIGHTS

        fred_score = fred_data['score'] if fred_data else 0
        stock_score = stock_data['score'] if stock_data else 0
        twitter_score = twitter_data['sentiment_score'] if twitter_data else 0

        # Weighted average
        combined = (
            fred_score * weights['fred_liquidity'] +
            stock_score * weights['stock_technicals'] +
            twitter_score * weights['twitter_sentiment']
        )

        return combined


if __name__ == "__main__":
    # Test data collector
    collector = DataCollector()

    # Test with AAPL
    data = collector.collect_all("AAPL")

    # Save to file
    output_file = Config.DATA_DIR / f"test_collection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2, default=str)

    print(f"\n📁 Saved to: {output_file}")
