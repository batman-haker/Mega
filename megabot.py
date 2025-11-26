#!/usr/bin/env python3
"""
MEGABOT - AI-Powered Investment Advisor
Combines FRED macro data, stock analysis, and Twitter sentiment
to provide investment recommendations via Claude/Gemini AI
"""

import json
import argparse
from datetime import datetime
from pathlib import Path

from collectors.data_collector import DataCollector
from analyzers.prompt_builder import PromptBuilder
from analyzers.ai_advisor import AIAdvisor
from config.config import Config


class MegaBot:
    """Main MEGABOT orchestrator"""

    def __init__(self, ai_provider: str = None):
        """
        Initialize MEGABOT

        Args:
            ai_provider: "claude" or "gemini" (defaults to Config.DEFAULT_AI_PROVIDER)
        """
        print("""
================================================================
                    MEGABOT v1.0
          AI-Powered Investment Advisor System
================================================================
        """)

        # Validate config
        if not Config.validate():
            raise ValueError("Configuration validation failed!")

        # Initialize components
        print("\n[INIT] Initializing components...")
        self.collector = DataCollector()
        self.prompt_builder = PromptBuilder()
        self.ai_advisor = AIAdvisor(provider=ai_provider)

        print("[INIT] [OK] MEGABOT ready!")

    def analyze_stock(self, ticker: str, save_results: bool = True) -> dict:
        """
        Complete analysis workflow for a stock

        Args:
            ticker: Stock ticker symbol (e.g. "AAPL")
            save_results: Whether to save results to file

        Returns:
            dict with complete analysis results
        """
        print(f"\n{'='*70}")
        print(f"[*] Analyzing {ticker}")
        print(f"{'='*70}\n")

        # Step 1: Collect data from all sources
        print("[1] STEP 1: Data Collection")
        print("-" * 70)
        data = self.collector.collect_all(ticker)

        if not data:
            print("\n[X] Failed to collect data!")
            return None

        # Step 2: Build AI prompt
        print("\n[2] STEP 2: Building AI Prompt")
        print("-" * 70)
        prompt = self.prompt_builder.build_investment_prompt(data)
        print(f"[PROMPT] Generated {len(prompt)} character prompt")

        # Step 3: Get AI recommendation
        print("\n[3] STEP 3: Getting AI Recommendation")
        print("-" * 70)
        ai_result = self.ai_advisor.analyze_with_prompt(prompt, ticker)

        if not ai_result['success']:
            print(f"\n[!] AI analysis failed: {ai_result['error']}")
            print("[!] Continuing with data analysis only...")
            # Create dummy AI result
            ai_result = {
                'provider': ai_result.get('provider', 'N/A'),
                'model': ai_result.get('model', 'N/A'),
                'recommendation': f"AI analysis unavailable: {ai_result['error']}",
                'success': False,
                'error': ai_result['error'],
                'action': 'UNKNOWN',
                'action_emoji': '?'
            }

        # Combine results
        final_result = {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            'data': data,
            'prompt': prompt,
            'ai_recommendation': ai_result,
            'combined_score': data['combined_score'],
        }

        # Step 4: Display results
        print("\n" + "="*70)
        print("[OK] ANALYSIS COMPLETE!")
        print("="*70)
        self._print_summary(final_result)

        # Step 5: Save results
        if save_results:
            output_file = self._save_results(final_result)
            print(f"\n[SAVE] Full results saved to: {output_file}")

        return final_result

    def _print_summary(self, result: dict):
        """Print analysis summary to console"""
        ticker = result['ticker']
        data = result['data']
        ai = result['ai_recommendation']

        print(f"\nTicker: {ticker}")
        print(f"Time: {result['timestamp']}")
        print(f"\n{'-'*70}")

        # Scores
        fred_score = data['fred']['score'] if data.get('fred') else None
        stock_score = data['stock']['score'] if data.get('stock') else None
        twitter_score = data['twitter']['sentiment_score'] if data.get('twitter') else None
        combined = result['combined_score']

        print(f"SCORES:")
        print(f"  FRED Liquidity:    {fred_score:>6.1f}/100" if fred_score else "  FRED: N/A")
        print(f"  Stock Technicals:  {stock_score:>6.1f}/100" if stock_score else "  Stock: N/A")
        print(f"  Twitter Sentiment: {twitter_score:>6.1f}/100" if twitter_score else "  Twitter: N/A")
        print(f"  {'-'*35}")
        print(f"  COMBINED SCORE:    {combined:>6.1f}/100")

        print(f"\n{'-'*70}")

        # AI Recommendation
        action = ai.get('action', 'UNKNOWN')
        action_emoji = ai.get('action_emoji', '?')

        print(f"AI RECOMMENDATION: {action_emoji} {action}")
        print(f"   Provider: {ai['provider'].upper()} ({ai['model']})")

        print(f"\n{'-'*70}")
        print("FULL AI ANALYSIS:")
        print(f"{'-'*70}\n")
        print(ai['recommendation'])
        print(f"\n{'-'*70}")

    def _save_results(self, result: dict) -> Path:
        """Save analysis results to JSON file"""
        ticker = result['ticker']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"analysis_{ticker}_{timestamp}.json"
        output_path = Config.DATA_DIR / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)

        return output_path

    def batch_analyze(self, tickers: list) -> dict:
        """
        Analyze multiple stocks

        Args:
            tickers: List of ticker symbols

        Returns:
            dict with results for each ticker
        """
        print(f"\n🎯 Batch Analysis: {len(tickers)} stocks")

        results = {}

        for i, ticker in enumerate(tickers, 1):
            print(f"\n{'='*70}")
            print(f"[{i}/{len(tickers)}] Analyzing {ticker}")
            print(f"{'='*70}")

            result = self.analyze_stock(ticker, save_results=True)

            if result:
                results[ticker] = result
            else:
                results[ticker] = {'error': 'Analysis failed'}

        # Summary
        print(f"\n{'='*70}")
        print(f"[OK] BATCH ANALYSIS COMPLETE")
        print(f"{'='*70}")
        print(f"\nSuccessful: {sum(1 for r in results.values() if 'error' not in r)}/{len(tickers)}")

        return results


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description='MEGABOT - AI-Powered Investment Advisor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze single stock
  python megabot.py AAPL

  # Analyze multiple stocks
  python megabot.py AAPL MSFT GOOGL

  # Use Gemini instead of Claude
  python megabot.py AAPL --provider gemini

  # Run dashboard
  streamlit run dashboard.py
        """
    )

    parser.add_argument(
        'tickers',
        nargs='+',
        help='Stock ticker symbols (e.g. AAPL MSFT)'
    )

    parser.add_argument(
        '--provider',
        choices=['claude', 'gemini'],
        help='AI provider to use (default: from config)'
    )

    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Do not save results to file'
    )

    args = parser.parse_args()

    try:
        # Initialize MEGABOT
        bot = MegaBot(ai_provider=args.provider)

        # Analyze
        if len(args.tickers) == 1:
            bot.analyze_stock(args.tickers[0], save_results=not args.no_save)
        else:
            bot.batch_analyze(args.tickers)

    except KeyboardInterrupt:
        print("\n\n[!] Interrupted by user")
    except Exception as e:
        print(f"\n[X] Error: {e}")
        raise


if __name__ == "__main__":
    main()
