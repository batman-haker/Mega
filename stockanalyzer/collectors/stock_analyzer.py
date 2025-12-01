#!/usr/bin/env python3
"""
Smart Stock Analyzer - Relative & Context-Aware Analysis
Analyzes stocks based on sector context, not absolute book values
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

class Recommendation(Enum):
    STRONG_BUY = "🟢 STRONG BUY"
    BUY = "🟡 BUY"
    HOLD = "⚪ HOLD"
    SELL = "🟠 SELL"
    STRONG_SELL = "🔴 STRONG SELL"

@dataclass
class AnalysisResult:
    """Results from stock analysis"""
    overall_score: float  # 0-100
    recommendation: Recommendation
    sector: str
    industry: str

    # Category scores (0-100 percentile)
    valuation_score: float
    financial_health_score: float
    growth_score: float
    momentum_score: float
    sentiment_score: float

    # Insights
    strengths: List[str]
    weaknesses: List[str]
    red_flags: List[str]
    catalysts: List[str]

    # Context
    sector_comparison: Dict[str, str]
    summary: str


# Sector Benchmarks - Realistic 2024 values
SECTOR_BENCHMARKS = {
    "Technology": {
        "pe_avg": 35, "pe_good": 25, "pe_bad": 60,
        "pb_avg": 8, "roe_avg": 20, "margin_avg": 25,
        "growth_avg": 15, "debt_equity_ok": 1.5
    },
    "Software": {
        "pe_avg": 45, "pe_good": 30, "pe_bad": 80,
        "pb_avg": 15, "roe_avg": 25, "margin_avg": 30,
        "growth_avg": 25, "debt_equity_ok": 1.0
    },
    "Finance": {
        "pe_avg": 12, "pe_good": 10, "pe_bad": 18,
        "pb_avg": 1.2, "roe_avg": 12, "margin_avg": 35,
        "growth_avg": 8, "debt_equity_ok": 3.0  # Banks have high leverage
    },
    "Consumer Cyclical": {
        "pe_avg": 20, "pe_good": 15, "pe_bad": 30,
        "pb_avg": 4, "roe_avg": 18, "margin_avg": 10,
        "growth_avg": 10, "debt_equity_ok": 1.2
    },
    "Healthcare": {
        "pe_avg": 22, "pe_good": 18, "pe_bad": 35,
        "pb_avg": 5, "roe_avg": 15, "margin_avg": 18,
        "growth_avg": 12, "debt_equity_ok": 0.8
    },
    "Energy": {
        "pe_avg": 15, "pe_good": 10, "pe_bad": 25,
        "pb_avg": 1.5, "roe_avg": 10, "margin_avg": 8,
        "growth_avg": 5, "debt_equity_ok": 1.0
    },
    "Industrials": {
        "pe_avg": 18, "pe_good": 15, "pe_bad": 25,
        "pb_avg": 3, "roe_avg": 14, "margin_avg": 12,
        "growth_avg": 8, "debt_equity_ok": 1.0
    },
    "Consumer Defensive": {
        "pe_avg": 22, "pe_good": 18, "pe_bad": 30,
        "pb_avg": 4, "roe_avg": 16, "margin_avg": 8,
        "growth_avg": 5, "debt_equity_ok": 0.8
    },
    "Communication Services": {
        "pe_avg": 25, "pe_good": 18, "pe_bad": 40,
        "pb_avg": 3, "roe_avg": 15, "margin_avg": 20,
        "growth_avg": 12, "debt_equity_ok": 1.2
    },
    "Utilities": {
        "pe_avg": 18, "pe_good": 15, "pe_bad": 25,
        "pb_avg": 1.8, "roe_avg": 10, "margin_avg": 12,
        "growth_avg": 3, "debt_equity_ok": 1.5
    },
    "Real Estate": {
        "pe_avg": 30, "pe_good": 20, "pe_bad": 50,
        "pb_avg": 2, "roe_avg": 8, "margin_avg": 15,
        "growth_avg": 5, "debt_equity_ok": 2.0
    },
    "Basic Materials": {
        "pe_avg": 16, "pe_good": 12, "pe_bad": 25,
        "pb_avg": 2, "roe_avg": 12, "margin_avg": 10,
        "growth_avg": 6, "debt_equity_ok": 0.8
    }
}

# Default fallback
DEFAULT_BENCHMARK = {
    "pe_avg": 25, "pe_good": 18, "pe_bad": 40,
    "pb_avg": 4, "roe_avg": 15, "margin_avg": 15,
    "growth_avg": 10, "debt_equity_ok": 1.0
}


class StockAnalyzer:
    """Main analyzer class"""

    def __init__(self, stock_data: Dict[str, Any]):
        """
        Initialize analyzer with stock data

        Args:
            stock_data: Dictionary with all stock metrics from Yahoo Finance
        """
        self.data = stock_data
        self.sector = stock_data.get('sector', 'Unknown')
        self.industry = stock_data.get('industry', 'Unknown')
        self.benchmarks = SECTOR_BENCHMARKS.get(self.sector, DEFAULT_BENCHMARK)

    def analyze(self) -> AnalysisResult:
        """Run complete analysis"""

        # Calculate category scores
        valuation = self._analyze_valuation()
        health = self._analyze_financial_health()
        growth = self._analyze_growth()
        momentum = self._analyze_momentum()
        sentiment = self._analyze_sentiment()

        # Calculate overall score (weighted average)
        overall = (
            valuation * 0.25 +
            health * 0.20 +
            growth * 0.25 +
            momentum * 0.15 +
            sentiment * 0.15
        )

        # Determine recommendation
        recommendation = self._get_recommendation(overall)

        # Find insights
        strengths, weaknesses = self._find_strengths_weaknesses()
        red_flags = self._find_red_flags()
        catalysts = self._find_catalysts()

        # Sector comparison
        sector_comp = self._sector_comparison()

        # Generate summary
        summary = self._generate_summary(overall, recommendation)

        return AnalysisResult(
            overall_score=overall,
            recommendation=recommendation,
            sector=self.sector,
            industry=self.industry,
            valuation_score=valuation,
            financial_health_score=health,
            growth_score=growth,
            momentum_score=momentum,
            sentiment_score=sentiment,
            strengths=strengths,
            weaknesses=weaknesses,
            red_flags=red_flags,
            catalysts=catalysts,
            sector_comparison=sector_comp,
            summary=summary
        )

    def _analyze_valuation(self) -> float:
        """Analyze valuation vs sector - returns 0-100 percentile"""
        score = 50  # neutral
        points = []

        # P/E Ratio (relative to sector)
        pe = self.data.get('trailingPE')
        if pe:
            pe_avg = self.benchmarks['pe_avg']
            pe_good = self.benchmarks['pe_good']

            if pe < pe_good:
                points.append(80)  # Cheap vs sector
            elif pe < pe_avg:
                points.append(60)  # Below average
            elif pe < self.benchmarks['pe_bad']:
                points.append(40)  # Acceptable
            else:
                points.append(20)  # Expensive

        # P/B Ratio
        pb = self.data.get('priceToBook')
        if pb:
            pb_avg = self.benchmarks['pb_avg']
            if pb < pb_avg * 0.7:
                points.append(80)
            elif pb < pb_avg:
                points.append(60)
            elif pb < pb_avg * 1.5:
                points.append(40)
            else:
                points.append(20)

        # PEG Ratio (growth adjusted)
        peg = self.data.get('pegRatio')
        if peg:
            if peg < 1:
                points.append(90)  # Undervalued vs growth
            elif peg < 1.5:
                points.append(70)
            elif peg < 2:
                points.append(50)
            else:
                points.append(30)

        # Forward P/E (future looking)
        forward_pe = self.data.get('forwardPE')
        if forward_pe and pe:
            if forward_pe < pe * 0.9:  # Improving
                points.append(70)
            elif forward_pe < pe:
                points.append(60)
            else:
                points.append(40)

        return sum(points) / len(points) if points else 50

    def _analyze_financial_health(self) -> float:
        """Analyze financial health - returns 0-100"""
        points = []

        # ROE (relative to sector)
        roe = self.data.get('returnOnEquity')
        if roe:
            roe_pct = roe * 100
            roe_avg = self.benchmarks['roe_avg']
            if roe_pct > roe_avg * 1.3:
                points.append(90)
            elif roe_pct > roe_avg:
                points.append(70)
            elif roe_pct > roe_avg * 0.7:
                points.append(50)
            else:
                points.append(30)

        # ROA
        roa = self.data.get('returnOnAssets')
        if roa:
            if roa > 0.15:
                points.append(85)
            elif roa > 0.10:
                points.append(70)
            elif roa > 0.05:
                points.append(50)
            else:
                points.append(30)

        # Debt/Equity (sector specific)
        debt_equity = self.data.get('debtToEquity')
        if debt_equity is not None:
            de_ok = self.benchmarks['debt_equity_ok']
            if debt_equity < de_ok * 0.5:
                points.append(90)
            elif debt_equity < de_ok:
                points.append(70)
            elif debt_equity < de_ok * 1.5:
                points.append(40)
            else:
                points.append(20)

        # Profit Margins (vs sector)
        margin = self.data.get('profitMargins')
        if margin:
            margin_pct = margin * 100
            margin_avg = self.benchmarks['margin_avg']
            if margin_pct > margin_avg * 1.3:
                points.append(90)
            elif margin_pct > margin_avg:
                points.append(70)
            elif margin_pct > margin_avg * 0.7:
                points.append(50)
            else:
                points.append(30)

        # Free Cash Flow (positive = good)
        fcf = self.data.get('freeCashflow')
        if fcf:
            if fcf > 0:
                points.append(70)
            else:
                points.append(20)

        return sum(points) / len(points) if points else 50

    def _analyze_growth(self) -> float:
        """Analyze growth metrics - returns 0-100"""
        points = []

        # Revenue Growth (vs sector expectation)
        rev_growth = self.data.get('revenueGrowth')
        if rev_growth:
            growth_pct = rev_growth * 100
            growth_avg = self.benchmarks['growth_avg']

            if growth_pct > growth_avg * 2:
                points.append(95)  # High growth
            elif growth_pct > growth_avg * 1.3:
                points.append(80)
            elif growth_pct > growth_avg:
                points.append(65)
            elif growth_pct > 0:
                points.append(45)
            else:
                points.append(20)  # Declining

        # Earnings Growth
        earnings_growth = self.data.get('earningsGrowth')
        if earnings_growth:
            eg_pct = earnings_growth * 100
            if eg_pct > 25:
                points.append(90)
            elif eg_pct > 15:
                points.append(75)
            elif eg_pct > 5:
                points.append(55)
            elif eg_pct > 0:
                points.append(40)
            else:
                points.append(25)

        # Gross Margins (expanding = good)
        gross_margin = self.data.get('grossMargins')
        if gross_margin:
            gm_pct = gross_margin * 100
            if gm_pct > 50:
                points.append(85)
            elif gm_pct > 30:
                points.append(70)
            elif gm_pct > 20:
                points.append(50)
            else:
                points.append(30)

        return sum(points) / len(points) if points else 50

    def _analyze_momentum(self) -> float:
        """Analyze price momentum - returns 0-100"""
        points = []

        # Price performance (from performance_data if available)
        perf_1w = self.data.get('performance_1w')
        perf_1m = self.data.get('performance_1m')
        perf_3m = self.data.get('performance_3m')

        for perf, weight in [(perf_1w, 1.2), (perf_1m, 1.0), (perf_3m, 0.8)]:
            if perf is not None:
                if perf > 10:
                    points.append(90 * weight)
                elif perf > 5:
                    points.append(75 * weight)
                elif perf > 0:
                    points.append(60 * weight)
                elif perf > -5:
                    points.append(40 * weight)
                else:
                    points.append(20 * weight)

        # Moving averages position
        ma_50 = self.data.get('fiftyDayAverage')
        ma_200 = self.data.get('twoHundredDayAverage')
        current_price = self.data.get('currentPrice')

        if all([ma_50, ma_200, current_price]):
            if current_price > ma_50 > ma_200:
                points.append(85)  # Golden cross territory
            elif current_price > ma_50:
                points.append(70)
            elif current_price > ma_200:
                points.append(55)
            else:
                points.append(30)

        return sum(points) / len(points) if points else 50

    def _analyze_sentiment(self) -> float:
        """Analyze market sentiment - returns 0-100"""
        points = []

        # Analyst recommendation
        rec_key = self.data.get('recommendationKey', '')
        rec_map = {
            'strong_buy': 95,
            'buy': 75,
            'hold': 50,
            'sell': 25,
            'strong_sell': 5
        }
        if rec_key:
            points.append(rec_map.get(rec_key.lower(), 50))

        # Target price vs current
        target_mean = self.data.get('targetMeanPrice')
        current = self.data.get('currentPrice')
        if target_mean and current:
            upside = ((target_mean - current) / current) * 100
            if upside > 30:
                points.append(95)
            elif upside > 15:
                points.append(80)
            elif upside > 5:
                points.append(65)
            elif upside > -5:
                points.append(45)
            else:
                points.append(25)

        # Institutional ownership (smart money)
        inst_pct = self.data.get('heldPercentInstitutions')
        if inst_pct:
            if inst_pct > 0.7:
                points.append(70)
            elif inst_pct > 0.5:
                points.append(60)
            else:
                points.append(45)

        # Short interest (high = bearish)
        short_pct = self.data.get('shortPercentOfFloat')
        if short_pct:
            if short_pct < 0.05:
                points.append(75)  # Low short interest
            elif short_pct < 0.10:
                points.append(60)
            elif short_pct > 0.20:
                points.append(30)  # Heavily shorted
            else:
                points.append(50)

        return sum(points) / len(points) if points else 50

    def _get_recommendation(self, score: float) -> Recommendation:
        """Convert score to recommendation"""
        if score >= 75:
            return Recommendation.STRONG_BUY
        elif score >= 60:
            return Recommendation.BUY
        elif score >= 40:
            return Recommendation.HOLD
        elif score >= 25:
            return Recommendation.SELL
        else:
            return Recommendation.STRONG_SELL

    def _find_strengths_weaknesses(self) -> Tuple[List[str], List[str]]:
        """Identify top strengths and weaknesses"""
        strengths = []
        weaknesses = []

        # Check each metric
        pe = self.data.get('trailingPE')
        if pe and pe < self.benchmarks['pe_good']:
            strengths.append(f"💎 Undervalued P/E: {pe:.1f} (sector avg: {self.benchmarks['pe_avg']})")
        elif pe and pe > self.benchmarks['pe_bad']:
            weaknesses.append(f"⚠️ High P/E: {pe:.1f} (sector avg: {self.benchmarks['pe_avg']})")

        rev_growth = self.data.get('revenueGrowth')
        if rev_growth:
            rg_pct = rev_growth * 100
            if rg_pct > self.benchmarks['growth_avg'] * 1.5:
                strengths.append(f"🚀 Strong Revenue Growth: {rg_pct:.1f}% (sector avg: {self.benchmarks['growth_avg']}%)")
            elif rg_pct < self.benchmarks['growth_avg'] * 0.5:
                weaknesses.append(f"📉 Weak Revenue Growth: {rg_pct:.1f}% (sector avg: {self.benchmarks['growth_avg']}%)")

        margin = self.data.get('profitMargins')
        if margin:
            m_pct = margin * 100
            if m_pct > self.benchmarks['margin_avg'] * 1.3:
                strengths.append(f"💰 Excellent Margins: {m_pct:.1f}% (sector avg: {self.benchmarks['margin_avg']}%)")
            elif m_pct < self.benchmarks['margin_avg'] * 0.7:
                weaknesses.append(f"⚠️ Low Margins: {m_pct:.1f}% (sector avg: {self.benchmarks['margin_avg']}%)")

        roe = self.data.get('returnOnEquity')
        if roe:
            roe_pct = roe * 100
            if roe_pct > self.benchmarks['roe_avg'] * 1.3:
                strengths.append(f"💪 Strong ROE: {roe_pct:.1f}% (sector avg: {self.benchmarks['roe_avg']}%)")
            elif roe_pct < self.benchmarks['roe_avg'] * 0.7:
                weaknesses.append(f"⚠️ Weak ROE: {roe_pct:.1f}% (sector avg: {self.benchmarks['roe_avg']}%)")

        peg = self.data.get('pegRatio')
        if peg and peg < 1:
            strengths.append(f"💎 Low PEG Ratio: {peg:.2f} (growth at reasonable price!)")

        return strengths[:3], weaknesses[:3]  # Top 3 each

    def _find_red_flags(self) -> List[str]:
        """Identify potential red flags"""
        flags = []

        # High debt
        debt_equity = self.data.get('debtToEquity')
        if debt_equity and debt_equity > self.benchmarks['debt_equity_ok'] * 2:
            flags.append(f"🚨 High Debt: D/E = {debt_equity:.1f} (sector ok: {self.benchmarks['debt_equity_ok']})")

        # Negative cash flow
        fcf = self.data.get('freeCashflow')
        if fcf and fcf < 0:
            flags.append(f"🚨 Negative Free Cash Flow: ${fcf/1e9:.2f}B")

        # Heavy short interest
        short_pct = self.data.get('shortPercentOfFloat')
        if short_pct and short_pct > 0.15:
            flags.append(f"🚨 High Short Interest: {short_pct*100:.1f}% of float")

        # Declining revenue
        rev_growth = self.data.get('revenueGrowth')
        if rev_growth and rev_growth < -0.05:
            flags.append(f"🚨 Revenue Declining: {rev_growth*100:.1f}%")

        # Price below 200 MA
        ma_200 = self.data.get('twoHundredDayAverage')
        current = self.data.get('currentPrice')
        if ma_200 and current and current < ma_200 * 0.9:
            flags.append(f"⚠️ Price {((current/ma_200 - 1)*100):.1f}% below 200-day MA (bearish trend)")

        return flags[:4]  # Top 4 flags

    def _find_catalysts(self) -> List[str]:
        """Identify potential positive catalysts"""
        catalysts = []

        # Strong momentum
        perf_3m = self.data.get('performance_3m')
        if perf_3m and perf_3m > 15:
            catalysts.append(f"🚀 Strong 3M Momentum: +{perf_3m:.1f}%")

        # Analyst upgrades (target > current)
        target = self.data.get('targetMeanPrice')
        current = self.data.get('currentPrice')
        if target and current:
            upside = ((target - current) / current) * 100
            if upside > 20:
                catalysts.append(f"🎯 Analyst Upside: {upside:.1f}% (target: ${target:.2f})")

        # Low valuation + growth
        peg = self.data.get('pegRatio')
        rev_growth = self.data.get('revenueGrowth')
        if peg and peg < 1.2 and rev_growth and rev_growth > 0.10:
            catalysts.append(f"💎 Growth at Value: PEG {peg:.2f} with {rev_growth*100:.0f}% growth")

        # Improving margins
        gross_margin = self.data.get('grossMargins')
        if gross_margin and gross_margin > 0.4:
            catalysts.append(f"💰 High Gross Margins: {gross_margin*100:.1f}% (pricing power)")

        # Strong buy rating
        rec_key = self.data.get('recommendationKey', '')
        if rec_key == 'strong_buy':
            catalysts.append("✅ Analyst Consensus: STRONG BUY")

        return catalysts[:4]  # Top 4 catalysts

    def _sector_comparison(self) -> Dict[str, str]:
        """Compare to sector benchmarks"""
        comparison = {}

        pe = self.data.get('trailingPE')
        if pe:
            pe_avg = self.benchmarks['pe_avg']
            diff = ((pe - pe_avg) / pe_avg) * 100
            if abs(diff) < 10:
                comparison['P/E'] = f"{pe:.1f} ≈ sector avg ({pe_avg})"
            elif pe < pe_avg:
                comparison['P/E'] = f"{pe:.1f} < sector avg ({pe_avg}) ✅ CHEAPER"
            else:
                comparison['P/E'] = f"{pe:.1f} > sector avg ({pe_avg}) ⚠️ PRICIER"

        margin = self.data.get('profitMargins')
        if margin:
            m_pct = margin * 100
            m_avg = self.benchmarks['margin_avg']
            if m_pct > m_avg:
                comparison['Margins'] = f"{m_pct:.1f}% > sector avg ({m_avg}%) ✅ BETTER"
            else:
                comparison['Margins'] = f"{m_pct:.1f}% < sector avg ({m_avg}%) ⚠️ WEAKER"

        growth = self.data.get('revenueGrowth')
        if growth:
            g_pct = growth * 100
            g_avg = self.benchmarks['growth_avg']
            if g_pct > g_avg * 1.2:
                comparison['Growth'] = f"{g_pct:.1f}% >> sector avg ({g_avg}%) 🚀 FAST"
            elif g_pct > g_avg:
                comparison['Growth'] = f"{g_pct:.1f}% > sector avg ({g_avg}%) ✅ GOOD"
            else:
                comparison['Growth'] = f"{g_pct:.1f}% < sector avg ({g_avg}%) ⚠️ SLOW"

        return comparison

    def _generate_summary(self, score: float, rec: Recommendation) -> str:
        """Generate executive summary"""
        if score >= 75:
            tone = "bardzo atrakcyjna"
            action = "Silna rekomendacja kupna"
        elif score >= 60:
            tone = "atrakcyjna"
            action = "Warto rozważyć zakup"
        elif score >= 40:
            tone = "neutralna"
            action = "Trzymaj lub czekaj na lepszy moment"
        elif score >= 25:
            tone = "słaba"
            action = "Rozważ redukcję pozycji"
        else:
            tone = "bardzo słaba"
            action = "Silna rekomendacja sprzedaży"

        return f"Na podstawie analizy względem sektora {self.sector}, akcja jest {tone} " \
               f"z oceną {score:.0f}/100. {action}."
