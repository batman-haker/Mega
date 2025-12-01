"""
STOCKANALYZER - Stock Data Collector

Wrapper dla Yahoo Finance + Smart Stock Analyzer.
Pobiera dane giełdowe i wykonuje kompleksową analizę.

Użycie:
    from collectors.stock_collector import get_stock_data

    data = get_stock_data('AAPL')
    print(f"Score: {data['overall_score']}/100")
    print(f"Recommendation: {data['recommendation']}")
"""

import yfinance as yf
import pandas as pd
import json
from typing import Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from .stock_analyzer import StockAnalyzer, AnalysisResult, Recommendation
from database.db import DatabaseSession
from database.models import StockCache


def get_stock_data(ticker: str, period: str = "3mo", use_cache: bool = True) -> Dict[str, Any]:
    """
    Pobiera kompletne dane akcji z Yahoo Finance i wykonuje smart analysis.

    CACHE STRATEGY:
    - TTL: 15 minut (real-time quotes potrzebują częstej aktualizacji)
    - Sprawdza DB przed API call
    - Zapisuje do DB po pobraniu

    Args:
        ticker: Symbol giełdowy (np. 'AAPL', 'MSFT', 'PKO.WA')
        period: Okres historyczny ('1mo', '3mo', '6mo', '1y', '5y')
        use_cache: Czy użyć cache z DB (default: True)

    Returns:
        Dictionary z:
            - Podstawowe info (ticker, nazwa, sektor, cena)
            - Smart analysis (score, recommendation, strengths, weaknesses)
            - Breakdown scores (valuation, health, growth, momentum, sentiment)
            - Dane dla wykresów (candlestick history, fundamentals, technicals)

    Example:
        >>> data = get_stock_data('AAPL')
        >>> print(f"{data['company_name']}: {data['overall_score']:.0f}/100")
        >>> print(data['recommendation'])
        Apple Inc.: 78/100
        🟢 STRONG BUY
    """

    # Normalizuj ticker (uppercase)
    ticker = ticker.upper()

    # 0. Sprawdź CACHE (jeśli use_cache=True)
    from_cache = False
    if use_cache:
        cached_data = _get_from_cache(ticker)
        if cached_data:
            # Cache HIT! Używamy cached RAW data
            info, history = cached_data
            from_cache = True
            print(f"[CACHE] Using cached data for {ticker}")
        else:
            # Cache MISS - pobierz z Yahoo Finance
            stock = yf.Ticker(ticker)
            info = stock.info
            history = stock.history(period=period)
    else:
        # Cache disabled - pobierz z Yahoo Finance
        stock = yf.Ticker(ticker)
        info = stock.info
        history = stock.history(period=period)

    if history.empty:
        raise ValueError(f"Nie znaleziono danych dla tickera: {ticker}")

    # 2. Oblicz performance metrics (potrzebne dla momentum analysis)
    info['performance_1w'] = _calculate_performance(history, days=7)
    info['performance_1m'] = _calculate_performance(history, days=30)
    info['performance_3m'] = _calculate_performance(history, days=90)

    # 3. Run Smart Analysis (wykorzystujemy gotowy StockAnalyzer!)
    analyzer = StockAnalyzer(info)
    analysis: AnalysisResult = analyzer.analyze()

    # 4. Extract fundamentals i technicals do wyświetlenia
    fundamentals = _extract_fundamentals(info)
    technicals = _extract_technicals(info, history)

    # 5. Format candlestick data dla Plotly
    candlestick_data = _format_candlestick_data(history)

    # 6. Prepare complete package
    result = {
        # Basic Info
        'ticker': ticker.upper(),
        'company_name': info.get('longName', ticker),
        'sector': analysis.sector,
        'industry': analysis.industry,
        'current_price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
        'currency': info.get('currency', 'USD'),
        'market_cap': info.get('marketCap', 0),
        'logo_url': info.get('logo_url', ''),

        # Smart Analysis Results (z stock_analyzer.py)
        'overall_score': round(analysis.overall_score, 1),
        'recommendation': analysis.recommendation.value,  # String: "🟢 STRONG BUY"
        'recommendation_enum': analysis.recommendation,   # Enum object
        'summary': analysis.summary,

        # Strengths & Weaknesses
        'strengths': analysis.strengths,
        'weaknesses': analysis.weaknesses,
        'red_flags': analysis.red_flags,
        'catalysts': analysis.catalysts,
        'sector_comparison': analysis.sector_comparison,

        # Category Scores (breakdown)
        'valuation_score': round(analysis.valuation_score, 1),
        'financial_health_score': round(analysis.financial_health_score, 1),
        'growth_score': round(analysis.growth_score, 1),
        'momentum_score': round(analysis.momentum_score, 1),
        'sentiment_score': round(analysis.sentiment_score, 1),

        # Data for charts
        'fundamentals': fundamentals,
        'technicals': technicals,
        'history': candlestick_data,

        # Timestamp
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),

        # Cache metadata
        'from_cache': from_cache
    }

    # 7. Zapisz do cache (jeśli use_cache=True i nie było z cache)
    if use_cache and not from_cache:
        _save_to_cache(ticker, info, history)

    return result


def search_tickers(query: str, limit: int = 10) -> list:
    """
    Wyszukuje tickery pasujące do zapytania.

    Args:
        query: Wyszukiwana fraza (np. 'apple', 'micro')
        limit: Max liczba wyników

    Returns:
        Lista dict: [{'ticker': 'AAPL', 'name': 'Apple Inc.'}, ...]
    """
    # TODO: Implementacja autocomplete
    # Można użyć yfinance Tickers() lub zewnętrznego API
    # Na razie zwracamy pustą listę
    return []


def _calculate_performance(history: pd.DataFrame, days: int) -> Optional[float]:
    """
    Oblicza % zmianę ceny za ostatnie N dni.

    Args:
        history: DataFrame z historical prices
        days: Liczba dni wstecz

    Returns:
        Zmiana procentowa lub None jeśli brak danych
    """
    if history.empty or len(history) < 2:
        return None

    try:
        # Ostatnia cena
        latest_price = history['Close'].iloc[-1]

        # Cena N dni temu
        target_date = history.index[-1] - timedelta(days=days)
        past_prices = history[history.index <= target_date]

        if past_prices.empty:
            # Jeśli nie mamy N dni historii, weź najstarszą dostępną
            past_price = history['Close'].iloc[0]
        else:
            past_price = past_prices['Close'].iloc[-1]

        # Oblicz % change
        performance = ((latest_price - past_price) / past_price) * 100
        return round(performance, 2)

    except (IndexError, KeyError, ZeroDivisionError):
        return None


def _extract_fundamentals(info: dict) -> Dict[str, Any]:
    """
    Wyciąga kluczowe wskaźniki fundamentalne.

    Returns:
        Dict z fundamentals: P/E, P/B, ROE, Debt/Equity, Margins, etc.
    """
    return {
        'pe_ratio': info.get('trailingPE'),
        'forward_pe': info.get('forwardPE'),
        'peg_ratio': info.get('pegRatio'),
        'pb_ratio': info.get('priceToBook'),
        'ps_ratio': info.get('priceToSalesTrailing12Months'),

        'roe': info.get('returnOnEquity'),
        'roa': info.get('returnOnAssets'),

        'debt_to_equity': info.get('debtToEquity'),
        'current_ratio': info.get('currentRatio'),
        'quick_ratio': info.get('quickRatio'),

        'profit_margin': info.get('profitMargins'),
        'operating_margin': info.get('operatingMargins'),
        'gross_margin': info.get('grossMargins'),

        'revenue_growth': info.get('revenueGrowth'),
        'earnings_growth': info.get('earningsGrowth'),

        'dividend_yield': info.get('dividendYield'),
        'payout_ratio': info.get('payoutRatio'),

        'free_cashflow': info.get('freeCashflow'),
        'operating_cashflow': info.get('operatingCashflow'),
    }


def _extract_technicals(info: dict, history: pd.DataFrame) -> Dict[str, Any]:
    """
    Oblicza wskaźniki techniczne.

    Returns:
        Dict z technicals: MA, RSI, MACD, Bollinger Bands, etc.
    """
    technicals = {}

    # Moving Averages z info
    technicals['ma_50'] = info.get('fiftyDayAverage')
    technicals['ma_200'] = info.get('twoHundredDayAverage')

    # Oblicz MA20 z history
    if not history.empty and len(history) >= 20:
        technicals['ma_20'] = history['Close'].rolling(window=20).mean().iloc[-1]
    else:
        technicals['ma_20'] = None

    # Golden/Death Cross detection
    current_price = info.get('currentPrice', history['Close'].iloc[-1] if not history.empty else None)
    ma_50 = technicals['ma_50']
    ma_200 = technicals['ma_200']

    if all([current_price, ma_50, ma_200]):
        if current_price > ma_50 > ma_200:
            technicals['cross_signal'] = 'Golden Cross 🟢'
        elif current_price < ma_50 < ma_200:
            technicals['cross_signal'] = 'Death Cross 🔴'
        elif current_price > ma_50:
            technicals['cross_signal'] = 'Above MA50 🟡'
        else:
            technicals['cross_signal'] = 'Below MA50 ⚪'
    else:
        technicals['cross_signal'] = 'N/A'

    # RSI calculation (simplified - idealne byłoby użyć ta-lib)
    if not history.empty and len(history) >= 14:
        technicals['rsi'] = _calculate_rsi(history['Close'], period=14)
    else:
        technicals['rsi'] = None

    # MACD calculation
    if not history.empty and len(history) >= 26:
        macd_data = _calculate_macd(history['Close'])
        technicals['macd'] = macd_data
    else:
        technicals['macd'] = None

    # Bollinger Bands calculation
    if not history.empty and len(history) >= 20:
        bb_data = _calculate_bollinger_bands(history['Close'], period=20, std_dev=2)
        technicals['bollinger_bands'] = bb_data
    else:
        technicals['bollinger_bands'] = None

    # Volume analysis
    if not history.empty:
        technicals['avg_volume'] = history['Volume'].tail(30).mean()
        technicals['latest_volume'] = history['Volume'].iloc[-1]

        if technicals['avg_volume'] > 0:
            vol_ratio = technicals['latest_volume'] / technicals['avg_volume']
            if vol_ratio > 1.5:
                technicals['volume_signal'] = 'High Volume 🔥'
            elif vol_ratio < 0.5:
                technicals['volume_signal'] = 'Low Volume 💤'
            else:
                technicals['volume_signal'] = 'Normal ✅'
        else:
            technicals['volume_signal'] = 'N/A'

    # 52-week high/low
    technicals['52w_high'] = info.get('fiftyTwoWeekHigh')
    technicals['52w_low'] = info.get('fiftyTwoWeekLow')

    # Beta (volatility vs market)
    technicals['beta'] = info.get('beta')

    return technicals


def _calculate_rsi(prices: pd.Series, period: int = 14) -> Optional[float]:
    """
    Oblicza Relative Strength Index (RSI).

    Args:
        prices: Series z cenami zamknięcia
        period: Okres dla RSI (default: 14)

    Returns:
        RSI value (0-100) lub None
    """
    if len(prices) < period + 1:
        return None

    try:
        # Oblicz dzienne zmiany
        delta = prices.diff()

        # Zyski i straty
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        # Średnie zyski i straty (EMA)
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()

        # RS = Average Gain / Average Loss
        rs = avg_gain / avg_loss

        # RSI = 100 - (100 / (1 + RS))
        rsi = 100 - (100 / (1 + rs))

        return round(rsi.iloc[-1], 2)

    except (ZeroDivisionError, IndexError, KeyError):
        return None


def _calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Optional[Dict[str, Any]]:
    """
    Oblicza MACD (Moving Average Convergence Divergence).

    Args:
        prices: Series z cenami zamknięcia
        fast: Okres dla szybkiej EMA (default: 12)
        slow: Okres dla wolnej EMA (default: 26)
        signal: Okres dla linii sygnału (default: 9)

    Returns:
        Dict z:
            - macd_line: Lista wartości MACD
            - signal_line: Lista wartości linii sygnału
            - histogram: Lista wartości histogramu
            - current_macd: Aktualna wartość MACD
            - current_signal: Aktualna wartość sygnału
            - current_histogram: Aktualna wartość histogramu
    """
    if len(prices) < slow:
        return None

    try:
        # Oblicz EMA
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()

        # MACD Line = EMA(12) - EMA(26)
        macd_line = ema_fast - ema_slow

        # Signal Line = EMA(9) of MACD Line
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()

        # Histogram = MACD - Signal
        histogram = macd_line - signal_line

        return {
            'macd_line': macd_line.tolist(),
            'signal_line': signal_line.tolist(),
            'histogram': histogram.tolist(),
            'current_macd': round(macd_line.iloc[-1], 4),
            'current_signal': round(signal_line.iloc[-1], 4),
            'current_histogram': round(histogram.iloc[-1], 4),
        }

    except (IndexError, KeyError):
        return None


def _calculate_bollinger_bands(prices: pd.Series, period: int = 20, std_dev: float = 2) -> Optional[Dict[str, Any]]:
    """
    Oblicza Bollinger Bands.

    Args:
        prices: Series z cenami zamknięcia
        period: Okres dla SMA (default: 20)
        std_dev: Liczba odchyleń standardowych (default: 2)

    Returns:
        Dict z:
            - upper_band: Lista wartości górnego pasma
            - middle_band: Lista wartości środkowego pasma (SMA)
            - lower_band: Lista wartości dolnego pasma
            - current_upper: Aktualna wartość górnego pasma
            - current_middle: Aktualna wartość SMA
            - current_lower: Aktualna wartość dolnego pasma
            - bandwidth: Szerokość pasma (%)
    """
    if len(prices) < period:
        return None

    try:
        # Middle Band = SMA
        middle_band = prices.rolling(window=period).mean()

        # Standard Deviation
        std = prices.rolling(window=period).std()

        # Upper Band = SMA + (std_dev * STD)
        upper_band = middle_band + (std_dev * std)

        # Lower Band = SMA - (std_dev * STD)
        lower_band = middle_band - (std_dev * std)

        # Bandwidth % = ((Upper - Lower) / Middle) * 100
        current_middle = middle_band.iloc[-1]
        current_upper = upper_band.iloc[-1]
        current_lower = lower_band.iloc[-1]
        bandwidth = ((current_upper - current_lower) / current_middle) * 100 if current_middle > 0 else 0

        return {
            'upper_band': upper_band.tolist(),
            'middle_band': middle_band.tolist(),
            'lower_band': lower_band.tolist(),
            'current_upper': round(current_upper, 2),
            'current_middle': round(current_middle, 2),
            'current_lower': round(current_lower, 2),
            'bandwidth': round(bandwidth, 2),
        }

    except (IndexError, KeyError, ZeroDivisionError):
        return None


def _format_candlestick_data(history: pd.DataFrame) -> list:
    """
    Formatuje dane historyczne dla wykresu candlestick.

    Returns:
        Lista dict: [{'date': '2024-01-01', 'open': 150, 'high': 155, ...}, ...]
    """
    if history.empty:
        return []

    candlestick = []

    for date, row in history.iterrows():
        candlestick.append({
            'date': date.strftime('%Y-%m-%d'),
            'open': round(row['Open'], 2),
            'high': round(row['High'], 2),
            'low': round(row['Low'], 2),
            'close': round(row['Close'], 2),
            'volume': int(row['Volume'])
        })

    return candlestick


# ============================================
# CACHE FUNCTIONS
# ============================================

def _get_from_cache(ticker: str) -> Optional[Tuple[dict, pd.DataFrame]]:
    """
    Sprawdza czy RAW Yahoo data są w cache i są świeże.

    Returns RAW data (info dict, history DataFrame) zamiast przetworzonej analizy.
    Analysis jest zawsze wykonywany na świeżo (szybki), ale Yahoo API call jest cache'owany.

    Args:
        ticker: Symbol giełdowy (uppercase)

    Returns:
        Tuple (info_dict, history_df) lub None jeśli brak/stare dane
    """
    try:
        with DatabaseSession() as session:
            # Znajdź najnowszy cache entry dla tego tickera
            cache_entry = session.query(StockCache).filter(
                StockCache.ticker == ticker,
                StockCache.valid_until > datetime.now()
            ).order_by(StockCache.timestamp.desc()).first()

            if cache_entry:
                # Deserializuj RAW data
                info = json.loads(cache_entry.fundamentals_json) if cache_entry.fundamentals_json else {}
                history_list = json.loads(cache_entry.history_json) if cache_entry.history_json else []

                # Reconstruct history DataFrame
                if history_list:
                    history_df = pd.DataFrame(history_list)
                    history_df['date'] = pd.to_datetime(history_df['date'])
                    history_df = history_df.set_index('date')
                else:
                    history_df = pd.DataFrame()

                print(f"[CACHE HIT] {ticker} - dane z cache (expires: {cache_entry.valid_until})")
                return (info, history_df)

            return None

    except Exception as e:
        print(f"[CACHE ERROR] Błąd odczytu cache dla {ticker}: {e}")
        return None


def _save_to_cache(ticker: str, info: dict, history: pd.DataFrame):
    """
    Zapisuje RAW Yahoo data do cache w DB.

    Args:
        ticker: Symbol giełdowy
        info: Raw info dict z yfinance
        history: Raw history DataFrame z yfinance

    TTL: 15 minut

    CACHE STRATEGY: Zapisujemy RAW data (info + history), a nie processed analysis.
    Analysis jest szybki (~50ms), API call jest wolny (~2-3s). Cache'ujemy wolną część.
    """
    try:
        with DatabaseSession() as session:
            # Serialize history DataFrame to list of dicts
            history_list = []
            for date, row in history.iterrows():
                history_list.append({
                    'date': date.strftime('%Y-%m-%d %H:%M:%S'),
                    'Open': float(row['Open']),
                    'High': float(row['High']),
                    'Low': float(row['Low']),
                    'Close': float(row['Close']),
                    'Volume': int(row['Volume'])
                })

            # Utwórz nowy cache entry
            cache_entry = StockCache(
                ticker=ticker,
                current_price=info.get('currentPrice', info.get('regularMarketPrice')),
                price_change_pct=info.get('regularMarketChangePercent'),
                fundamentals_json=json.dumps(info),  # Save RAW info dict
                technicals_json=None,  # Not used for RAW cache
                history_json=json.dumps(history_list),  # Save RAW history
                timestamp=datetime.now(),
                valid_until=datetime.now() + timedelta(minutes=15)  # TTL: 15 minut
            )

            session.add(cache_entry)
            session.commit()

            print(f"[CACHE SAVE] {ticker} - zapisano RAW data do cache (TTL: 15 min, {len(history_list)} bars)")

    except Exception as e:
        print(f"[CACHE ERROR] Błąd zapisu cache dla {ticker}: {e}")
        # Nie przerywamy działania aplikacji - cache failure nie jest krytyczny


# ============================================
# TESTING
# ============================================

if __name__ == "__main__":
    print("Stock Collector - Testing")
    print("=" * 60)

    # Test AAPL
    print("\n📊 Testing: AAPL")
    try:
        data = get_stock_data('AAPL')

        print(f"\n{'='*60}")
        print(f"Company: {data['company_name']}")
        print(f"Sector: {data['sector']} | Industry: {data['industry']}")
        print(f"Price: ${data['current_price']:.2f}")
        print(f"\n{'='*60}")
        print(f"OVERALL SCORE: {data['overall_score']:.0f}/100")
        print(f"RECOMMENDATION: {data['recommendation']}")
        print(f"\n{data['summary']}")
        print(f"{'='*60}")

        print(f"\n📈 Category Scores:")
        print(f"  Valuation:       {data['valuation_score']:.0f}/100")
        print(f"  Financial Health: {data['financial_health_score']:.0f}/100")
        print(f"  Growth:          {data['growth_score']:.0f}/100")
        print(f"  Momentum:        {data['momentum_score']:.0f}/100")
        print(f"  Sentiment:       {data['sentiment_score']:.0f}/100")

        print(f"\n✅ Strengths ({len(data['strengths'])}):")
        for s in data['strengths']:
            print(f"  {s}")

        print(f"\n⚠️ Weaknesses ({len(data['weaknesses'])}):")
        for w in data['weaknesses']:
            print(f"  {w}")

        if data['red_flags']:
            print(f"\n🚨 Red Flags ({len(data['red_flags'])}):")
            for flag in data['red_flags']:
                print(f"  {flag}")

        if data['catalysts']:
            print(f"\n🚀 Catalysts ({len(data['catalysts'])}):")
            for cat in data['catalysts']:
                print(f"  {cat}")

        print(f"\n{'='*60}")
        print("✅ TEST PASSED!")

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
