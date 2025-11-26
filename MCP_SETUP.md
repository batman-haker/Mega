# MCP Servers Setup for MEGABOT

This document explains how to configure Model Context Protocol (MCP) servers to enhance MEGABOT's capabilities.

## What is MCP?

Model Context Protocol (MCP) allows Claude Code to connect to external tools and data sources, providing enhanced capabilities for file management, API calls, and reasoning.

## Configured MCP Servers

MEGABOT uses four MCP servers:

### 1. Filesystem MCP
**Purpose:** Direct access to data files, logs, and Twitter cache

**Configured paths:**
- `C:\MEGABOT\data` - Analysis results
- `C:\MEGABOT\logs` - Application logs
- `C:\Xscrap\x-financial-analyzer\data\cache` - Twitter data cache

**Benefits:**
- Fast file operations
- Better data management
- Efficient cache access

### 2. Sequential Thinking MCP
**Purpose:** Enhanced reasoning for complex analysis

**Use cases:**
- Multi-step financial analysis
- Investment decision reasoning
- Risk assessment logic
- Scenario planning

**Benefits:**
- Structured thinking process
- Better explanations
- Improved decision quality

### 3. Memory MCP
**Purpose:** Persistent knowledge graph for maintaining context across sessions

**Use cases:**
- Remembering previous analyses
- Tracking portfolio changes over time
- Building knowledge about stocks and patterns
- Maintaining user preferences and insights

**Benefits:**
- Context persistence across sessions
- Better long-term analysis
- Learning from past decisions

### 4. Gemini MCP
**Purpose:** Direct integration with Google Gemini AI API

**Use cases:**
- Alternative AI analysis using Gemini models
- Comparison between Claude and Gemini recommendations
- Cost optimization (Gemini has free tier)
- Multi-model validation of investment decisions

**Benefits:**
- Access to Google's latest Gemini 2.0 models
- Free tier for development and testing
- Different AI perspective on market analysis
- Enhanced vision and multimodal capabilities

## Installation

### Prerequisites

1. **Node.js** (v18 or higher)
   ```bash
   node --version  # Should be v18+
   npm --version   # Should be v8+
   ```

2. **Claude Code** installed and configured

### Setup Steps

1. **Copy example configuration:**
   ```bash
   copy .claude\settings.example.json .claude\settings.local.json
   ```

2. **Customize paths** (if needed):
   Edit `.claude\settings.local.json` and update paths to match your system:
   ```json
   "args": [
     "-y",
     "@modelcontextprotocol/server-filesystem",
     "YOUR_PATH\\MEGABOT\\data",
     "YOUR_PATH\\MEGABOT\\logs",
     "YOUR_PATH\\Xscrap\\x-financial-analyzer\\data\\cache"
   ]
   ```

3. **Restart Claude Code:**
   - Close Claude Code completely
   - Reopen in the MEGABOT directory
   - MCP servers will initialize automatically

4. **Verify MCP servers:**
   MCP servers will be available as tools. You can check Claude Code status to see active MCP connections.

## Usage Examples

### Filesystem MCP

Claude can now directly access files:
```
"Read the latest analysis from data/"
"List all JSON files in the cache"
"Show me the most recent log file"
```

### Fetch MCP

Claude can make HTTP requests:
```
"Fetch current VIX data from FRED API"
"Get latest stock price for AAPL"
"Check API rate limits"
```

### Sequential Thinking MCP

Claude will use structured reasoning:
```
"Analyze AAPL investment opportunity step-by-step"
"Walk through the risk assessment for this position"
"Explain your investment recommendation reasoning"
```

### Gemini MCP

Claude can invoke Gemini for analysis:
```
"Use Gemini to analyze AAPL fundamentals"
"Compare your AAPL recommendation with Gemini's"
"Get Gemini's perspective on this market scenario"
```

## Troubleshooting

### MCP servers not starting

1. **Check Node.js:**
   ```bash
   node --version
   npm --version
   ```

2. **Test npx:**
   ```bash
   npx -y @modelcontextprotocol/server-filesystem --help
   ```

3. **Check paths:**
   Ensure all paths in `settings.local.json` exist:
   ```bash
   dir C:\MEGABOT\data
   dir C:\MEGABOT\logs
   ```

### Permission errors

1. **Update permissions** in `settings.local.json`:
   ```json
   "allow": [
     "Read(//c/MEGABOT/data/**)",
     "Read(//c/MEGABOT/logs/**)"
   ]
   ```

2. **Restart Claude Code**

### MCP server crashes

1. **Check logs** in Claude Code console
2. **Update MCP packages:**
   ```bash
   npx -y @modelcontextprotocol/server-filesystem@latest
   ```

## Advanced Configuration

### Adding Custom MCP Servers

You can add more MCP servers to `.claude\settings.local.json`:

```json
{
  "mcp": {
    "servers": {
      "your-custom-server": {
        "command": "npx",
        "args": ["-y", "@your-org/your-mcp-server"],
        "env": {
          "API_KEY": "your-api-key"
        }
      }
    }
  }
}
```

### Useful MCP Servers for Finance

Currently installed:
- ✅ **`@modelcontextprotocol/server-filesystem`** - File operations
- ✅ **`@modelcontextprotocol/server-sequential-thinking`** - Structured reasoning
- ✅ **`@modelcontextprotocol/server-memory`** - Persistent memory and knowledge graph
- ✅ **`github:aliargun/mcp-server-gemini`** - Google Gemini AI integration

Additional servers (community/experimental):
- **Puppeteer MCP** - Browser automation for web scraping
- **Custom Finance APIs** - Build your own for Bloomberg, Reuters, etc.

## Security Notes

- `.claude/settings.local.json` is in `.gitignore` (contains local paths)
- Never commit API keys in MCP configuration
- Use environment variables for sensitive data
- Restrict filesystem access to necessary directories only

## Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [Official MCP Servers](https://github.com/modelcontextprotocol/servers)
- [Claude Code MCP Guide](https://code.claude.com/docs)

## Support

If you encounter issues with MCP setup:
1. Check this document first
2. Review Claude Code documentation
3. Open an issue on GitHub: https://github.com/batman-haker/Mega/issues

---

**Happy analyzing with enhanced MCP capabilities!** 🚀
