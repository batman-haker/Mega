"""
Educational content for financial indicators and metrics.
Wyjaśnienia wskaźników i ich interpretacja.
"""

# ============================================
# FUNDAMENTALS EDUCATION
# ============================================

FUNDAMENTALS_GLOSSARY = {
    'pe_ratio': {
        'name': 'P/E Ratio (Price-to-Earnings)',
        'description': 'Wskaźnik ceny do zysków. Pokazuje ile płacisz za 1$ zysku firmy.',
        'interpretation': {
            'low': (0, 15, '🟢 NISKI - Może być niedowartościowana'),
            'medium': (15, 25, '🟡 ŚREDNI - Typowa wycena'),
            'high': (25, 999, '🔴 WYSOKI - Może być przewartościowana lub fast-growth')
        },
        'example': 'P/E = 20 oznacza: płacisz 20$ za każdy 1$ rocznego zysku. Niższe = tańsze, wyższe = droższe.',
        'good_bad': 'Niższe = lepsze (tańsze), ale uwaga na sektor! Tech ma wyższe P/E niż banki.'
    },

    'peg_ratio': {
        'name': 'PEG Ratio (P/E to Growth)',
        'description': 'P/E podzielone przez tempo wzrostu zysków. Uwzględnia przyszły wzrost.',
        'interpretation': {
            'low': (0, 1, '🟢 NISKI - Niedowartościowana względem wzrostu'),
            'medium': (1, 2, '🟡 ŚREDNI - Fair value'),
            'high': (2, 999, '🔴 WYSOKI - Przewartościowana względem wzrostu')
        },
        'example': 'PEG < 1 = niedowartościowana, PEG = 1 = fair value, PEG > 2 = droga',
        'good_bad': 'PEG < 1 jest uważane za atrakcyjne. Łączy wycenę z tempem wzrostu.'
    },

    'pb_ratio': {
        'name': 'P/B Ratio (Price-to-Book)',
        'description': 'Cena do wartości księgowej. Ile płacisz za $1 aktywów netto firmy.',
        'interpretation': {
            'low': (0, 1, '🟢 NISKI - Poniżej wartości księgowej'),
            'medium': (1, 3, '🟡 ŚREDNI - Typowa wycena'),
            'high': (3, 999, '🔴 WYSOKI - Powyżej wartości księgowej')
        },
        'example': 'P/B = 2 oznacza: płacisz 2x więcej niż wartość aktywów. P/B < 1 = akcje tańsze niż aktywa.',
        'good_bad': 'Niższe = lepsze. P/B < 1 może oznaczać okazję (lub problemy!).'
    },

    'roe': {
        'name': 'ROE (Return on Equity)',
        'description': 'Zwrot z kapitału własnego. Ile zysku firma generuje z każdego $1 kapitału.',
        'interpretation': {
            'low': (0, 10, '🔴 NISKI - Słaba efektywność'),
            'medium': (10, 20, '🟡 ŚREDNI - OK efektywność'),
            'high': (20, 100, '🟢 WYSOKI - Świetna efektywność')
        },
        'example': 'ROE = 15% oznacza: na każde $100 kapitału firma zarabia $15 zysku rocznie.',
        'good_bad': 'Wyższe = lepsze! ROE > 15% jest dobre, >20% świetne.'
    },

    'debt_to_equity': {
        'name': 'Debt/Equity (Wskaźnik zadłużenia)',
        'description': 'Stosunek długu do kapitału własnego. Mierzy dźwignię finansową.',
        'interpretation': {
            'low': (0, 0.5, '🟢 NISKI - Konserwatywne zadłużenie'),
            'medium': (0.5, 1.5, '🟡 ŚREDNI - Umiarkowane zadłużenie'),
            'high': (1.5, 999, '🔴 WYSOKI - Wysokie ryzyko finansowe')
        },
        'example': 'D/E = 0.5 oznacza: na każde $1 kapitału firma ma $0.50 długu. < 1 = więcej kapitału niż długu.',
        'good_bad': 'Niższe = lepsze (mniej ryzyka). Ale zależy od sektora - tech może mieć niskie, utility wysokie.'
    },

    'profit_margin': {
        'name': 'Profit Margin (Marża zysku)',
        'description': 'Procent przychodów pozostający jako zysk netto.',
        'interpretation': {
            'low': (0, 5, '🔴 NISKA - Niska rentowność'),
            'medium': (5, 15, '🟡 ŚREDNIA - OK rentowność'),
            'high': (15, 100, '🟢 WYSOKA - Świetna rentowność')
        },
        'example': 'Marża 10% oznacza: ze $100 sprzedaży zostaje $10 czystego zysku.',
        'good_bad': 'Wyższa = lepsza! >20% to świetna marża. Zależy od branży.'
    },

    'revenue_growth': {
        'name': 'Revenue Growth (Wzrost przychodów)',
        'description': 'Roczne tempo wzrostu przychodów (YoY).',
        'interpretation': {
            'low': (-999, 5, '🔴 NISKI - Stagnacja lub spadek'),
            'medium': (5, 15, '🟡 ŚREDNI - Umiarkowany wzrost'),
            'high': (15, 999, '🟢 WYSOKI - Silny wzrost')
        },
        'example': 'Wzrost 20% oznacza: przychody rosną o 20% rocznie.',
        'good_bad': 'Wyższy = lepszy! >15% to strong growth, >30% to hypergrowth.'
    },
}

# ============================================
# TECHNICALS EDUCATION
# ============================================

TECHNICALS_GLOSSARY = {
    'rsi': {
        'name': 'RSI (Relative Strength Index)',
        'description': 'Wskaźnik siły względnej. Mierzy momentum - czy akcja jest wykupiona czy wyprzedana.',
        'interpretation': {
            'oversold': (0, 30, '🟢 OVERSOLD - Wyprzedane, potencjalny odwrót w górę'),
            'neutral': (30, 70, '🟡 NEUTRAL - Normalna strefa'),
            'overbought': (70, 100, '🔴 OVERBOUGHT - Wykupione, potencjalny odwrót w dół')
        },
        'example': 'RSI = 75 oznacza wykupienie - cena mocno wzrosła, może nastąpić korekta.',
        'good_bad': 'RSI < 30 = sygnał kupna (oversold), RSI > 70 = sygnał sprzedaży (overbought)'
    },

    'macd': {
        'name': 'MACD (Moving Average Convergence Divergence)',
        'description': 'Wskaźnik momentum bazujący na różnicy między średnimi kroczącymi.',
        'interpretation': {
            'bearish': (-999, 0, '🔴 BEARISH - Histogram < 0, trend spadkowy'),
            'bullish': (0, 999, '🟢 BULLISH - Histogram > 0, trend wzrostowy')
        },
        'example': 'MACD > Signal = bullish (kupuj), MACD < Signal = bearish (sprzedaj). Histogram pokazuje siłę.',
        'good_bad': 'Przecięcie MACD powyżej linii sygnału = sygnał kupna. Poniżej = sygnał sprzedaży.'
    },

    'bollinger_bands': {
        'name': 'Bollinger Bands (Wstęgi Bollingera)',
        'description': 'Wstęgi zmienności. Pokazują zakres normalnych ruchów ceny (±2 odchylenia standardowe).',
        'interpretation': {
            'squeeze': (0, 5, '🟡 SQUEEZE - Wąskie pasmo, spodziewany wybuch zmienności'),
            'normal': (5, 10, '🟢 NORMAL - Typowa zmienność'),
            'volatile': (10, 999, '🔴 HIGH VOLATILITY - Szerokie pasmo, duża zmienność')
        },
        'example': 'Cena przy górnej wstędze = potencjalne wykupienie. Przy dolnej = potencjalne wyprzedanie.',
        'good_bad': 'Wąskie pasmo = mała zmienność, spodziewany ruch. Cena przy krawędziach = ekstremum.'
    },

    'ma_50': {
        'name': 'MA 50 (50-Day Moving Average)',
        'description': '50-dniowa średnia krocząca. Pokazuje średnioterminowy trend.',
        'interpretation': {
            'below': 'Cena poniżej MA50 = trend spadkowy lub słabość',
            'above': 'Cena powyżej MA50 = trend wzrostowy lub siła'
        },
        'example': 'Cena przekracza MA50 od dołu = potencjalny sygnał kupna (golden cross mini).',
        'good_bad': 'MA50 to średnioterminowy trend. Cena powyżej = bullish, poniżej = bearish.'
    },

    'ma_200': {
        'name': 'MA 200 (200-Day Moving Average)',
        'description': '200-dniowa średnia krocząca. Pokazuje długoterminowy trend.',
        'interpretation': {
            'below': 'Cena poniżej MA200 = długoterminowy trend spadkowy (bear market)',
            'above': 'Cena powyżej MA200 = długoterminowy trend wzrostowy (bull market)'
        },
        'example': 'MA50 przekracza MA200 od dołu = Golden Cross (silny sygnał kupna).',
        'good_bad': 'MA200 to "kreska na piasku" między bull a bear market. Najważniejszy wskaźnik trendu.'
    },

    'golden_cross': {
        'name': 'Golden Cross',
        'description': 'MA50 przekracza MA200 od dołu - bardzo silny sygnał kupna.',
        'interpretation': 'Sugeruje początek długoterminowego trendu wzrostowego.',
        'example': 'Historycznie golden cross prowadził do średnio +15-20% wzrostów w ciągu roku.',
        'good_bad': '🟢 BARDZO BULLISH - jeden z najsilniejszych sygnałów kupna.'
    },

    'death_cross': {
        'name': 'Death Cross',
        'description': 'MA50 przekracza MA200 od góry - silny sygnał sprzedaży.',
        'interpretation': 'Sugeruje początek długoterminowego trendu spadkowego.',
        'example': 'Historycznie death cross prowadził do kontynuacji spadków.',
        'good_bad': '🔴 BARDZO BEARISH - silny sygnał ostrzegawczy.'
    },

    'beta': {
        'name': 'Beta (Wskaźnik zmienności)',
        'description': 'Mierzy zmienność akcji względem rynku (S&P 500 = 1.0).',
        'interpretation': {
            'low': (0, 0.8, '🟢 LOW VOLATILITY - Mniej zmienne niż rynek'),
            'medium': (0.8, 1.2, '🟡 AVERAGE - Podobna zmienność do rynku'),
            'high': (1.2, 999, '🔴 HIGH VOLATILITY - Bardziej zmienne niż rynek')
        },
        'example': 'Beta = 1.5 oznacza: jeśli rynek rośnie 10%, akcja rośnie ~15%. I odwrotnie przy spadkach!',
        'good_bad': 'Beta < 1 = mniejsze ryzyko, Beta > 1 = większe ryzyko i potencjał zysku.'
    },
}

# ============================================
# SCORING EDUCATION
# ============================================

SCORING_GLOSSARY = {
    'overall_score': {
        'name': 'Overall Score (Ogólna ocena)',
        'description': 'Kompleksowa ocena akcji (0-100) uwzględniająca 5 kategorii: wycenę, zdrowie finansowe, wzrost, momentum i sentiment.',
        'interpretation': {
            'poor': (0, 40, '🔴 SŁABA - Unikaj lub sprzedawaj'),
            'fair': (40, 60, '🟡 PRZECIĘTNA - Neutralna, wymagana dodatkowa analiza'),
            'good': (60, 75, '🟢 DOBRA - Warta rozważenia'),
            'excellent': (75, 100, '🌟 ŚWIETNA - Strong buy candidate')
        },
        'weights': 'Valuation: 25% | Health: 20% | Growth: 25% | Momentum: 15% | Sentiment: 15%',
        'good_bad': '>75 = Strong Buy, 60-75 = Buy, 40-60 = Hold, <40 = Sell'
    },

    'valuation_score': {
        'name': 'Valuation Score (Ocena wyceny)',
        'description': 'Czy akcja jest tania czy droga? Analizuje P/E, P/B, PEG względem sektora.',
        'interpretation': {
            'expensive': (0, 40, '🔴 DROGA - Przewartościowana'),
            'fair': (40, 60, '🟡 FAIR VALUE - Uczciwa wycena'),
            'cheap': (60, 100, '🟢 TANIA - Niedowartościowana, potencjalna okazja')
        },
        'good_bad': 'Wyższy score = tańsza akcja = lepsza okazja (value investing)'
    },

    'financial_health_score': {
        'name': 'Financial Health Score (Zdrowie finansowe)',
        'description': 'Siła fundamentów: ROE, ROA, zadłużenie, marże, płynność.',
        'interpretation': {
            'weak': (0, 40, '🔴 SŁABE - Problemy finansowe'),
            'stable': (40, 60, '🟡 STABILNE - OK fundamenty'),
            'strong': (60, 100, '🟢 SILNE - Świetne fundamenty')
        },
        'good_bad': 'Wyższy score = silniejsza firma = mniejsze ryzyko'
    },

    'growth_score': {
        'name': 'Growth Score (Ocena wzrostu)',
        'description': 'Tempo wzrostu przychodów i zysków (historyczne i prognozowane).',
        'interpretation': {
            'stagnant': (0, 40, '🔴 STAGNACJA - Brak wzrostu'),
            'moderate': (40, 60, '🟡 UMIARKOWANY - Wolny wzrost'),
            'strong': (60, 100, '🟢 SILNY - Fast growth')
        },
        'good_bad': 'Wyższy score = szybszy wzrost = większy potencjał (growth investing)'
    },

    'momentum_score': {
        'name': 'Momentum Score (Ocena momentum)',
        'description': 'Analiza techniczna: trend, RSI, pozycja względem średnich.',
        'interpretation': {
            'bearish': (0, 40, '🔴 BEARISH - Trend spadkowy'),
            'neutral': (40, 60, '🟡 NEUTRAL - Brak wyraźnego trendu'),
            'bullish': (60, 100, '🟢 BULLISH - Trend wzrostowy')
        },
        'good_bad': 'Wyższy score = silniejszy trend wzrostowy = lepszy timing (momentum investing)'
    },

    'sentiment_score': {
        'name': 'Sentiment Score (Ocena sentymentu)',
        'description': 'Co myślą analitycy? Rekomendacje i target price.',
        'interpretation': {
            'negative': (0, 40, '🔴 NEGATYWNY - Analitycy sceptyczni'),
            'neutral': (40, 60, '🟡 NEUTRALNY - Brak konsensusu'),
            'positive': (60, 100, '🟢 POZYTYWNY - Analitycy optymistyczni')
        },
        'good_bad': 'Wyższy score = bardziej pozytywne rekomendacje analityków'
    },
}


def get_indicator_help(indicator_key: str, category: str = 'fundamentals') -> dict:
    """
    Zwraca wyjaśnienie wskaźnika.

    Args:
        indicator_key: Klucz wskaźnika (np. 'pe_ratio', 'rsi')
        category: Kategoria ('fundamentals', 'technicals', 'scoring')

    Returns:
        Dict z wyjaśnieniem lub None
    """
    glossaries = {
        'fundamentals': FUNDAMENTALS_GLOSSARY,
        'technicals': TECHNICALS_GLOSSARY,
        'scoring': SCORING_GLOSSARY
    }

    glossary = glossaries.get(category, {})
    return glossary.get(indicator_key)


def interpret_value(indicator_key: str, value: float, category: str = 'fundamentals') -> str:
    """
    Interpretuje wartość wskaźnika i zwraca kolorową etykietę.

    Args:
        indicator_key: Klucz wskaźnika
        value: Wartość wskaźnika
        category: Kategoria

    Returns:
        String z interpretacją (np. "🟢 NISKI - Może być niedowartościowana")
    """
    help_info = get_indicator_help(indicator_key, category)

    if not help_info or 'interpretation' not in help_info:
        return ""

    interpretation = help_info['interpretation']

    # Interpretacje są różne dla różnych wskaźników
    for key, data in interpretation.items():
        if isinstance(data, tuple) and len(data) == 3:
            min_val, max_val, label = data
            if min_val <= value < max_val:
                return label

    return ""


def format_metric_with_context(value: float, indicator_key: str, category: str = 'fundamentals') -> dict:
    """
    Formatuje metrykę z kontekstem interpretacyjnym.

    Returns:
        Dict z: value, interpretation, color
    """
    interpretation = interpret_value(indicator_key, value, category)

    # Określ kolor na podstawie interpretacji
    if '🟢' in interpretation:
        color = 'normal'  # green
    elif '🔴' in interpretation:
        color = 'inverse'  # red
    else:
        color = 'off'  # neutral/yellow

    return {
        'value': value,
        'interpretation': interpretation,
        'color': color
    }
