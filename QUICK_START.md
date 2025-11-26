# 🚀 MEGABOT Quick Start Guide

Get up and running in 5 minutes!

## Step 1: Install Dependencies

```bash
cd C:\MEGABOT
pip install -r requirements.txt
```

## Step 2: Setup .env File

```bash
copy .env.example .env
notepad .env
```

Add your API keys:
```
FRED_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_claude_key_here
```

## Step 3: Test Configuration

```bash
python config/config.py
```

You should see: `✅ Configuration validated successfully!`

## Step 4: Run Twitter Scraper (if needed)

Make sure you have recent Twitter data:

```bash
cd C:\Xscrap\x-financial-analyzer
python smart_tweet_collector.py
```

## Step 5: Run MEGABOT!

### Option A: Web Dashboard (Easiest)

```bash
cd C:\MEGABOT
streamlit run dashboard.py
```

Open browser → enter ticker → click Analyze!

### Option B: Command Line

```bash
python megabot.py AAPL
```

---

## 🎯 Example Usage

```bash
# Single stock
python megabot.py AAPL

# Multiple stocks
python megabot.py AAPL MSFT GOOGL

# Use Gemini instead of Claude
python megabot.py TSLA --provider gemini
```

---

## ⚡ Troubleshooting

**Problem:** "FRED_API_KEY not set"
→ **Solution:** Add it to `.env` file

**Problem:** "No Twitter data found"
→ **Solution:** Run Twitter scraper first (Step 4)

**Problem:** "ANTHROPIC_API_KEY not set"
→ **Solution:** Get Claude API key from https://console.anthropic.com/ OR use Gemini with `--provider gemini`

---

## 📚 Full Documentation

See [README.md](README.md) for complete documentation.

---

**That's it! You're ready to analyze stocks with AI! 🚀**
