"""
MEGABOT Prompt Builder
Constructs detailed prompts for AI analysis based on collected data
"""

from typing import Dict, List
from datetime import datetime


class PromptBuilder:
    """Builds expert-level prompts for AI advisors"""

    def __init__(self):
        pass

    def build_investment_prompt(self, data: Dict) -> str:
        """
        Build a comprehensive investment analysis prompt

        Args:
            data: Dictionary from DataCollector.collect_all()

        Returns:
            str: Formatted prompt for AI
        """
        ticker = data['ticker']
        fred = data.get('fred', {})
        stock = data.get('stock', {})
        twitter = data.get('twitter', {})

        prompt = f"""Jesteś ekspertem finansowym z 20-letnim doświadczeniem w zarządzaniu portfelem i analizie rynków.
Twoim zadaniem jest ocena czy warto KUPIĆ akcje {ticker} w obecnych warunkach rynkowych.

Przeanalizuj poniższe dane i wydaj rekomendację:

{'='*70}
1. WARUNKI MAKROEKONOMICZNE (FRED - Analiza Płynności)
{'='*70}

{self._format_fred_section(fred)}

{'='*70}
2. ANALIZA SPÓŁKI: {ticker}
{'='*70}

{self._format_stock_section(stock)}

{'='*70}
3. SENTIMENT EKSPERTÓW (Twitter)
{'='*70}

{self._format_twitter_section(twitter)}

{'='*70}
TWOJE ZADANIE:
{'='*70}

Na podstawie powyższych danych odpowiedz na pytania:

1. **CZY KUPOWAĆ {ticker} TERAZ?**
   - Wydaj rekomendację: MOCNE KUP / KUP / TRZYMAJ / SPRZEDAJ / MOCNE SPRZEDAJ
   - Oceń pewność swojej decyzji w skali 1-10

2. **UZASADNIENIE**
   - Jakie są 3 NAJWAŻNIEJSZE argumenty ZA zakupem?
   - Jakie są 3 NAJWAŻNIEJSZE argumenty PRZECIW zakupowi?
   - Które czynniki (makro/fundamenty/sentiment) mają największy wpływ?

3. **ANALIZA RYZYKA**
   - Jaki jest poziom ryzyka: NISKI / ŚREDNI / WYSOKI?
   - Co może pójść nie tak? (top 3 ryzyka)
   - Czy jest to odpowiedni moment w cyklu rynkowym?

4. **TAKTYKA INWESTYCYJNA**
   - Jaki horyzont czasowy: krótki (1-3 mies) / średni (3-12 mies) / długi (1-3 lata)?
   - Jaki % portfela przeznaczyć na tę pozycję?
   - Czy wejść od razu czy czekać na lepszy moment?
   - Sugerowane poziomy: cena wejścia, stop-loss, take-profit

5. **SCENARIUSZE**
   - Scenariusz BULL: Co się stanie jeśli wszystko pójdzie dobrze? (+X%)
   - Scenariusz BASE: Najbardziej prawdopodobny rozwój? (+/-X%)
   - Scenariusz BEAR: Co w najgorszym przypadku? (-X%)

Odpowiedź podaj w STRUKTURALNY sposób z wyraźnymi sekcjami.
Bądź KONKRETNY i SZCZERY - jeśli coś jest ryzykowne, napisz to wprost.
Myśl jak profesjonalny zarządzający funduszem, który ryzykuje WŁASNE pieniądze.
"""

        return prompt

    def _format_fred_section(self, fred: Dict) -> str:
        """Format FRED liquidity data section"""
        if not fred:
            return "⚠️ Brak danych makroekonomicznych"

        score = fred.get('score', 0)
        regime = fred.get('regime', {})
        indicators = fred.get('indicators', {})
        alerts = fred.get('alerts', [])
        patterns = fred.get('patterns', {})

        # Score interpretation
        if score > 40:
            score_emoji = "🟢"
            score_text = "BARDZO DOBRE warunki płynności"
        elif score > 0:
            score_emoji = "🟡"
            score_text = "NEUTRALNE warunki płynności"
        elif score > -40:
            score_emoji = "🟠"
            score_text = "POGARSZAJĄCE SIĘ warunki"
        else:
            score_emoji = "🔴"
            score_text = "NAPIĘTE warunki - OSTROŻNIE!"

        section = f"""
Liquidity Score: {score_emoji} {score:.1f}/100 ({score_text})
Reżim rynkowy: {regime.get('name', 'N/A')}
Opis: {regime.get('description', '')}

Kluczowe wskaźniki:
  • Rezerwy banków: ${indicators.get('reserves', 0):.0f}B
  • TGA (konto rządu): ${indicators.get('tga', 0):.0f}B
  • Reverse Repo: ${indicators.get('reverse_repo', 0):.0f}B
  • SOFR-IORB spread: {indicators.get('sofr_iorb_spread', 0):.3f}% {'🚨 STRESS!' if indicators.get('sofr_iorb_spread', 0) > 0.20 else '✅ OK' if indicators.get('sofr_iorb_spread', 0) < 0.10 else '⚠️'}
  • VIX (strach): {indicators.get('vix', 0):.1f} {'🔴 PANIKA' if indicators.get('vix', 0) > 30 else '🟢 spokój' if indicators.get('vix', 0) < 20 else '🟡 podwyższony'}
  • Krzywa 10Y-2Y: {indicators.get('yield_curve', 0):.2f}% {'🔴 ODWRÓCONA (recesja!)' if indicators.get('yield_curve', 0) < 0 else '🟢 pozytywna'}
  • NFCI (warunki fin.): {indicators.get('nfci', 0):.2f} {'🔴 napięte' if indicators.get('nfci', 0) > 0 else '🟢 luźne'}
  • M2 Money Supply: ${indicators.get('m2', 0):.0f}B
"""

        # Add critical alerts
        if alerts:
            section += "\n⚠️ ALERTY KRYTYCZNE:\n"
            for alert in alerts[:3]:  # Top 3
                if alert.get('severity') == 'critical':
                    section += f"  🚨 {alert.get('message', '')}\n"

        # Add detected patterns
        if patterns:
            conflicts = patterns.get('conflicts', [])
            compound = patterns.get('compound_signals', [])

            if conflicts:
                section += "\n🔍 WYKRYTE PARADOKSY:\n"
                for conflict in conflicts[:2]:
                    section += f"  • {conflict.get('name')}: {conflict.get('interpretation')}\n"

            if compound:
                section += "\n⚡ COMPOUND SIGNALS:\n"
                for signal in compound[:2]:
                    section += f"  • {signal.get('name')}: {signal.get('interpretation')}\n"

        section += f"\n💡 INTERPRETACJA: {fred.get('interpretation', '')}"

        return section

    def _format_stock_section(self, stock: Dict) -> str:
        """Format stock analysis section"""
        if not stock:
            return "⚠️ Brak danych o spółce"

        ticker = stock.get('ticker')
        price = stock.get('price', 0)
        change = stock.get('change_1d', 0)
        fundamentals = stock.get('fundamentals', {})
        technicals = stock.get('technicals', {})
        score = stock.get('score', 0)
        company = stock.get('company', {})

        # Score interpretation
        if score > 50:
            score_emoji = "🟢"
            score_text = "MOCNE TECHNICALS"
        elif score > 0:
            score_emoji = "🟡"
            score_text = "neutralne"
        else:
            score_emoji = "🔴"
            score_text = "SŁABE TECHNICALS"

        section = f"""
Spółka: {company.get('name', ticker)}
Sektor: {company.get('sector', 'N/A')} | Branża: {company.get('industry', 'N/A')}

Cena: ${price:.2f} (zmiana 1d: {change:+.2f}%)
Stock Score: {score_emoji} {score:.1f}/100 ({score_text})

FUNDAMENTY:
  • P/E ratio: {fundamentals.get('pe_ratio', 'N/A')} {self._interpret_pe(fundamentals.get('pe_ratio'))}
  • Forward P/E: {fundamentals.get('forward_pe', 'N/A')}
  • PEG ratio: {fundamentals.get('peg_ratio', 'N/A')} {self._interpret_peg(fundamentals.get('peg_ratio'))}
  • Price/Book: {fundamentals.get('price_to_book', 'N/A')}
  • Market Cap: ${fundamentals.get('market_cap', 0)/1e9:.2f}B
  • Profit Margin: {fundamentals.get('profit_margin', 0)*100:.1f}% {self._interpret_margin(fundamentals.get('profit_margin'))}
  • ROE: {fundamentals.get('roe', 0)*100:.1f}% {self._interpret_roe(fundamentals.get('roe'))}
  • Debt/Equity: {fundamentals.get('debt_to_equity', 'N/A')} {self._interpret_debt(fundamentals.get('debt_to_equity'))}
  • Beta: {fundamentals.get('beta', 'N/A')} {self._interpret_beta(fundamentals.get('beta'))}
  • Dividend Yield: {fundamentals.get('dividend_yield', 0)*100:.2f}%

TECHNICALS:
  • RSI(14): {technicals.get('rsi', 0):.1f} {self._interpret_rsi(technicals.get('rsi'))}
  • MA(20): ${technicals.get('ma_20', 0):.2f} | Cena vs MA20: {technicals.get('price_vs_ma20', 0):+.1f}%
  • MA(50): ${technicals.get('ma_50', 0):.2f} | Cena vs MA50: {technicals.get('price_vs_ma50', 0):+.1f}%
  • MA(200): ${technicals.get('ma_200') or 'N/A'}
  • Golden Cross: {'✅ TAK (bullish!)' if technicals.get('golden_cross') else '❌ Nie'}
  • Death Cross: {'⚠️ TAK (bearish!)' if technicals.get('death_cross') else '✅ Nie'}
  • Bollinger Band Position: {technicals.get('bb_position', 0.5)*100:.0f}% {self._interpret_bb(technicals.get('bb_position'))}
"""

        return section

    def _format_twitter_section(self, twitter: Dict) -> str:
        """Format Twitter sentiment section"""
        if not twitter:
            return "⚠️ Brak danych z Twittera (eksperci nie tweetnęli ostatnio)"

        sentiment_score = twitter.get('sentiment_score', 0)
        tweets_count = twitter.get('tweets_count', 0)
        experts_count = twitter.get('experts_count', 0)
        experts = twitter.get('experts', [])
        recent_tweets = twitter.get('tweets', [])[:5]  # Top 5

        # Sentiment interpretation
        if sentiment_score > 30:
            sentiment_emoji = "🟢"
            sentiment_text = "BULLISH"
        elif sentiment_score > -30:
            sentiment_emoji = "🟡"
            sentiment_text = "NEUTRALNY"
        else:
            sentiment_emoji = "🔴"
            sentiment_text = "BEARISH"

        section = f"""
Sentiment Score: {sentiment_emoji} {sentiment_score:.1f}/100 ({sentiment_text})
Analizowano: {tweets_count} tweetów od {experts_count} ekspertów

Eksperci: {', '.join(['@' + e for e in experts[:5]])}

Najnowsze tweety ekspertów:
"""

        for i, tweet in enumerate(recent_tweets, 1):
            text = tweet.get('text', '')[:150]  # First 150 chars
            author = tweet.get('user', {}).get('username', 'unknown')
            section += f"\n  {i}. @{author}: \"{text}...\""

        section += "\n\n💡 Kluczowe obserwacje ekspertów: "
        if sentiment_score > 30:
            section += "Eksperci są optymistyczni, widzą szanse."
        elif sentiment_score < -30:
            section += "Eksperci ostrzegają, podnoszą czerwone flagi."
        else:
            section += "Eksperci ostrożni, sytuacja niejednoznaczna."

        return section

    # === INTERPRETATION HELPERS ===

    def _interpret_pe(self, pe):
        if not pe or pe <= 0:
            return ""
        if pe < 15:
            return "🟢 nisko (wartościowo)"
        elif pe < 25:
            return "🟡 OK"
        else:
            return "🔴 wysoko (drogie)"

    def _interpret_peg(self, peg):
        if not peg or peg <= 0:
            return ""
        if peg < 1.0:
            return "🟢 atrakcyjne"
        elif peg < 2.0:
            return "🟡 OK"
        else:
            return "🔴 drogie"

    def _interpret_margin(self, margin):
        if not margin:
            return ""
        if margin > 0.20:
            return "🟢 świetna"
        elif margin > 0.10:
            return "🟡 dobra"
        elif margin > 0:
            return "🟠 niska"
        else:
            return "🔴 stratna!"

    def _interpret_roe(self, roe):
        if not roe:
            return ""
        if roe > 0.20:
            return "🟢 doskonały"
        elif roe > 0.15:
            return "🟡 dobry"
        else:
            return "🔴 słaby"

    def _interpret_debt(self, de):
        if not de:
            return ""
        if de < 0.5:
            return "🟢 niski (bezpieczne)"
        elif de < 1.5:
            return "🟡 umiarkowany"
        else:
            return "🔴 wysoki (ryzyko)"

    def _interpret_beta(self, beta):
        if not beta:
            return ""
        if beta < 0.8:
            return "🟢 defensywna"
        elif beta < 1.2:
            return "🟡 rynkowa"
        else:
            return "🔴 zmiennaagresywna"

    def _interpret_rsi(self, rsi):
        if not rsi:
            return ""
        if rsi < 30:
            return "🟢 OVERSOLD (okazja!)"
        elif rsi < 40:
            return "🟡 słaba"
        elif rsi > 70:
            return "🔴 OVERBOUGHT (drogie!)"
        elif rsi > 60:
            return "🟠 mocna"
        else:
            return "🟡 neutralna"

    def _interpret_bb(self, bb_pos):
        if not bb_pos:
            return ""
        if bb_pos < 0.2:
            return "🟢 blisko dolnej (okazja?)"
        elif bb_pos > 0.8:
            return "🔴 blisko górnej (drogie?)"
        else:
            return "🟡 środek pasma"


if __name__ == "__main__":
    # Test prompt builder
    import json
    from pathlib import Path
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent))
    from config.config import Config

    # Try to load latest test data
    data_files = list(Config.DATA_DIR.glob("test_collection_*.json"))

    if data_files:
        latest = sorted(data_files)[-1]
        print(f"Loading test data: {latest}")

        with open(latest, 'r') as f:
            data = json.load(f)

        builder = PromptBuilder()
        prompt = builder.build_investment_prompt(data)

        print("\n" + "="*70)
        print("GENERATED PROMPT:")
        print("="*70)
        print(prompt)

        # Save prompt
        output_file = Config.DATA_DIR / f"test_prompt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(prompt)

        print(f"\n📁 Saved prompt to: {output_file}")
    else:
        print("No test data found. Run data_collector.py first!")
