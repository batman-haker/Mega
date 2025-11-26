"""
MEGABOT AI Advisor
Sends prompts to Claude or Gemini API and gets investment recommendations
"""

import anthropic
import google.generativeai as genai
from typing import Dict, Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config.config import Config


class AIAdvisor:
    """AI-powered investment advisor using Claude or Gemini"""

    def __init__(self, provider: Optional[str] = None):
        """
        Initialize AI Advisor

        Args:
            provider: "claude" or "gemini" (if None, uses Config.DEFAULT_AI_PROVIDER)
        """
        self.config = Config()
        self.provider = provider or self.config.DEFAULT_AI_PROVIDER

        # Initialize API client
        if self.provider == "claude":
            if not self.config.ANTHROPIC_API_KEY:
                raise ValueError("[X] ANTHROPIC_API_KEY not set in .env!")

            self.client = anthropic.Anthropic(
                api_key=self.config.ANTHROPIC_API_KEY
            )
            self.model = self.config.CLAUDE_MODEL
            print(f"[AI] Initialized Claude ({self.model})")

        elif self.provider == "gemini":
            if not self.config.GOOGLE_API_KEY:
                raise ValueError("[X] GOOGLE_API_KEY not set in .env!")

            genai.configure(api_key=self.config.GOOGLE_API_KEY)
            self.client = genai.GenerativeModel(self.config.GEMINI_MODEL)
            self.model = self.config.GEMINI_MODEL
            print(f"[AI] Initialized Gemini ({self.model})")

        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def get_recommendation(self, prompt: str) -> Dict:
        """
        Get investment recommendation from AI

        Args:
            prompt: Investment analysis prompt

        Returns:
            {
                'provider': str,
                'model': str,
                'recommendation': str,
                'raw_response': str,
                'success': bool,
                'error': str (if failed)
            }
        """
        print(f"\n[AI] Sending prompt to {self.provider}...")
        print(f"[AI] Prompt length: {len(prompt)} characters")

        try:
            if self.provider == "claude":
                response = self._ask_claude(prompt)
            elif self.provider == "gemini":
                response = self._ask_gemini(prompt)
            else:
                raise ValueError(f"Unknown provider: {self.provider}")

            print(f"[AI] [OK] Received response ({len(response)} chars)")

            return {
                'provider': self.provider,
                'model': self.model,
                'recommendation': response,
                'raw_response': response,
                'success': True,
                'error': None
            }

        except Exception as e:
            print(f"[AI] [X] Error: {e}")
            return {
                'provider': self.provider,
                'model': self.model,
                'recommendation': None,
                'raw_response': None,
                'success': False,
                'error': str(e)
            }

    def _ask_claude(self, prompt: str) -> str:
        """Send prompt to Claude API"""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=self.config.MAX_TOKENS,
            temperature=self.config.TEMPERATURE,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # Extract text from response
        response_text = message.content[0].text

        return response_text

    def _ask_gemini(self, prompt: str) -> str:
        """Send prompt to Gemini API"""
        generation_config = {
            "temperature": self.config.TEMPERATURE,
            "max_output_tokens": self.config.MAX_TOKENS,
        }

        response = self.client.generate_content(
            prompt,
            generation_config=generation_config
        )

        return response.text

    def analyze_with_prompt(self, prompt: str, ticker: str) -> Dict:
        """
        Complete analysis workflow with structured output

        Args:
            prompt: Analysis prompt
            ticker: Stock ticker being analyzed

        Returns:
            {
                'ticker': str,
                'provider': str,
                'model': str,
                'recommendation': str,
                'full_response': str,
                'success': bool,
                'error': str,
                'timestamp': str
            }
        """
        from datetime import datetime

        result = self.get_recommendation(prompt)

        # Add metadata
        result['ticker'] = ticker
        result['timestamp'] = datetime.now().isoformat()

        # Try to extract key recommendation
        if result['success']:
            recommendation_text = result['recommendation']

            # Try to parse recommendation type
            if 'MOCNE KUP' in recommendation_text or 'STRONG BUY' in recommendation_text:
                result['action'] = 'STRONG_BUY'
                result['action_emoji'] = '🚀'
            elif 'KUP' in recommendation_text or 'BUY' in recommendation_text:
                result['action'] = 'BUY'
                result['action_emoji'] = '🟢'
            elif 'TRZYMAJ' in recommendation_text or 'HOLD' in recommendation_text:
                result['action'] = 'HOLD'
                result['action_emoji'] = '🟡'
            elif 'SPRZEDAJ' in recommendation_text or 'SELL' in recommendation_text:
                result['action'] = 'SELL'
                result['action_emoji'] = '🔴'
            elif 'MOCNE SPRZEDAJ' in recommendation_text or 'STRONG SELL' in recommendation_text:
                result['action'] = 'STRONG_SELL'
                result['action_emoji'] = '🔻'
            else:
                result['action'] = 'UNKNOWN'
                result['action_emoji'] = '❓'

        return result


if __name__ == "__main__":
    # Test AI Advisor
    import json
    from datetime import datetime

    # Simple test prompt
    test_prompt = """Jesteś ekspertem finansowym. Przeanalizuj poniższe dane i powiedz czy kupować akcje AAPL:

MAKRO:
- Liquidity Score: +45 (dobre warunki)
- VIX: 18 (spokój)
- Yield Curve: +0.4% (pozytywna)

STOCK: AAPL
- Cena: $180
- P/E: 28 (wysoki)
- RSI: 55 (neutralny)
- Golden Cross: TAK

TWITTER SENTIMENT: +60 (bullish)

CZY KUPOWAĆ? Odpowiedź krótko (3-5 zdań).
"""

    print("="*70)
    print("Testing AI Advisor")
    print("="*70)

    # Test with Claude (if available)
    try:
        advisor = AIAdvisor(provider="claude")
        result = advisor.analyze_with_prompt(test_prompt, "AAPL")

        print(f"\n{'='*70}")
        print(f"Provider: {result['provider']}")
        print(f"Action: {result.get('action_emoji', '')} {result.get('action', 'N/A')}")
        print(f"{'='*70}")
        print(result['recommendation'])
        print(f"{'='*70}")

        # Save result
        output_file = Config.DATA_DIR / f"test_ai_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"\n📁 Saved to: {output_file}")

    except Exception as e:
        print(f"[X] Claude test failed: {e}")

        # Try Gemini as fallback
        try:
            print("\nTrying Gemini...")
            advisor = AIAdvisor(provider="gemini")
            result = advisor.analyze_with_prompt(test_prompt, "AAPL")

            print(f"\n{'='*70}")
            print(f"Provider: {result['provider']}")
            print(f"Action: {result.get('action_emoji', '')} {result.get('action', 'N/A')}")
            print(f"{'='*70}")
            print(result['recommendation'])
            print(f"{'='*70}")

        except Exception as e2:
            print(f"[X] Gemini test also failed: {e2}")
            print("\n⚠️  Make sure you have API keys set in .env!")
