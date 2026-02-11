# 🎯 SWARM Intelligence Discord Bot

Professional trading intelligence platform with SEC filing analysis edge.

## 🔥 What is SWARM?

SWARM is a multi-layered trading intelligence system that provides:

- **SEC Filing Analysis** - 10-30 minute head start before news breaks (YOUR COMPETITIVE MOAT)
- **SWARM SCORE Algorithm** - Multi-source intelligence fusion (40% SEC, 35% Technical, 15% Financial, 10% News)
- **Professional Analysis** - Minervini-style risk parameters, not hype-based alerts
- **Real-Time Monitoring** - Integrates with your existing Python scripts (FLOCK, CHIRP, SKY_SCRAPER)

## 📊 SWARM SCORE Algorithm

```
SWARM SCORE = (SEC Signal × 40%) + (Technical × 35%) + (Financial × 15%) + (News × 10%)

Components:
├─ SEC Signal (0-40):     Keyword detection, filing timing, pattern matching
├─ Technical (0-35):      Price action, volume expansion, RSI, moving averages
├─ Financial (0-15):      Cash vs debt, balance sheet health
└─ News (0-10):           Mentions, sentiment, trending status
```

---

## 🚀 Quick Start (Railway.app Deployment)

### Prerequisites
- Discord account + server
- GitHub account
- Railway.app account (free tier)

### Step 1: Create Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Name it "SWARM Intelligence"
4. Go to "Bot" tab → "Add Bot"
5. Copy the **Token** (you'll need this)
6. Under "Privileged Gateway Intents" enable:
   - ✅ Presence Intent
   - ✅ Server Members Intent
   - ✅ Message Content Intent
7. Click "Save Changes"

### Step 2: Invite Bot to Your Server

1. Go to "OAuth2" → "URL Generator"
2. Select scopes:
   - ✅ `bot`
   - ✅ `applications.commands`
3. Select bot permissions:
   - ✅ Send Messages
   - ✅ Embed Links
   - ✅ Read Message History
   - ✅ Use Slash Commands
   - ✅ Manage Roles
4. Copy the generated URL
5. Open in browser and invite to your server

### Step 3: Create Discord Channels

In your Discord server, create these channels:

```
🎯 SWARM INTELLIGENCE
├─ 🔥-critical-setups      (90+ scores)
├─ 📊-active-setups         (75-89 scores)
├─ 📋-watchlist             (60-74 scores)
├─ 📄-sec-filings           (CHIRP alerts)
├─ 📈-momentum-scanner      (FLOCK results)
├─ 🎯-technical-setups      (SKY_SCRAPER)
├─ 📰-news-feed             (News alerts)
├─ 💰-financial-health      (4/4 ratings)
├─ 💎-top-gainers           (Live dashboard)
├─ 📉-top-losers            (Live dashboard)
└─ 🌊-community-watch       (Trending tickers)
```

**Get Channel IDs:**
1. Enable Developer Mode in Discord (Settings → Advanced → Developer Mode)
2. Right-click each channel → "Copy Channel ID"
3. Save these IDs for later

### Step 4: Create Discord Roles

Create two roles:
- **SWARM Pro** - Full access to all analysis
- **SWARM Free** - Limited preview access

**Get Role IDs:**
1. Right-click each role → "Copy Role ID"
2. Save for later

### Step 5: Deploy to Railway

1. **Fork this repo to your GitHub**

2. **Go to [Railway.app](https://railway.app)**
   - Sign in with GitHub
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your forked SWARM repo

3. **Add PostgreSQL database:**
   - Click "New"
   - Select "Database" → "PostgreSQL"
   - Railway auto-creates `DATABASE_URL`

4. **Set Environment Variables:**
   - Click on your service
   - Go to "Variables"
   - Add these variables:

```bash
DISCORD_BOT_TOKEN=your_bot_token_from_step_1

# Channel IDs (from Step 3)
CHANNEL_CRITICAL_SETUPS=123456789
CHANNEL_ACTIVE_SETUPS=123456789
# ... (add all channel IDs)

# Role IDs (from Step 4)
ROLE_PRO=123456789
ROLE_FREE=123456789
```

5. **Deploy:**
   - Railway automatically deploys
   - Check logs for errors
   - Bot should come online in Discord

### Step 6: Test the Bot

In Discord, try these slash commands:

```
/score NVDA        - Get SWARM SCORE for NVIDIA
/watch AAPL        - Add Apple to your watchlist
/alerts            - See today's high-scoring alerts
/history TSLA      - See Tesla's SWARM SCORE history
```

---

## 🏠 Local Development

### Setup

```bash
# Clone repo
git clone https://github.com/yourusername/swarm-bot
cd swarm-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your values
nano .env
```

### Run Locally

```bash
# Run bot
python bot.py

# Test SWARM SCORE algorithm
python swarm_score.py

# Test database
python database.py
```

---

## 🔗 Integration with Existing Scripts

SWARM integrates with your existing cron jobs:

### FLOCK Integration
```bash
# Your existing cron:
02 7 * * * cd ~/SEC/Swarm/Nest && ./flock.py

# SWARM reads from:
~/SEC/Swarm/Nest/filtered_tickers.csv
```

### CHIRP Integration
```bash
# Your existing cron:
15 7 * * * cd ~/SEC/Swarm/Nest && ./chirp.py

# SWARM reads SEC filings from:
~/SEC/Swarm/Nest/sec_filings/sec-edgar-filings/
```

### SKY_SCRAPER Integration
```bash
# Your existing cron:
39 9 * * * cd ~/SEC/Swarm/Nest && ./Sky_scraper.py

# SWARM reads from:
~/SEC/Swarm/Nest/filtered_tickers_breakout.csv
~/SEC/Swarm/Nest/filtered_tickers_swing.csv
~/SEC/Swarm/Nest/filtered_tickers_bounce.csv
```

**SWARM runs independently and monitors these files every 5 minutes.**

---

## 📈 Monetization Strategy

### Free Tier
- See alerts (ticker + score only)
- Top gainers/losers dashboards
- Community discussion
- **Purpose: Create FOMO**

### Pro Tier ($79/month)
- Full SWARM analysis
- Entry/exit zones
- Stop loss levels
- Risk parameters
- Historical patterns
- Slash commands
- **All the alpha**

### Revenue Model
```
100 members × $79/month = $7,900/month
Monthly costs: ~$30 (if using Mosquito/Nuntio)
Profit: $7,870/month ($94k/year)
```

---

## 🎯 Professional Voice Examples

### ✅ GOOD - Professional Trader Voice
```
🎯 SWARM SCORE: 94 - High Probability Setup

NVDA - SEC Filing + Technical Confirmation

Setup Analysis:
├─ SEC 8-K filed 08 minutes ago
├─ Keywords: "merger discussion" "strategic alternatives"
├─ Pattern Recognition: 15 of 17 similar setups moved >10%
└─ Historical Edge: Average 23-minute head start before news

Risk Parameters:
├─ Entry Zone: $142.00 - $143.50
├─ Stop Loss: $138.50 (R:R = 3.2:1)
└─ Position Size: 1-2% maximum

Probability: 88% win rate (15/17 historical)

Trade your plan, manage risk, honor stops.
```

### ❌ BAD - Hype Voice (Never Do This)
```
🚀🚀🚀 NVDA TO THE MOON 🚀🚀🚀

THIS IS PRINTING!! 🔥💰

GET IN NOW BEFORE IT'S TOO LATE!!!

🌙 $200 BY EOD 🌙

NOT FINANCIAL ADVICE BUT THIS CAN'T MISS!!!
```

---

## 🛠️ Tech Stack

- **Backend:** Python 3.11, discord.py, SQLAlchemy
- **Database:** PostgreSQL (Railway auto-provision)
- **Deployment:** Railway.app (free tier → $5/month)
- **Data:** yfinance (free), SEC Edgar (free), Finviz (free)

---

## 📝 Slash Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/score TICKER` | Get SWARM SCORE | `/score NVDA` |
| `/watch TICKER` | Add to watchlist | `/watch AAPL` |
| `/alerts` | Today's alerts | `/alerts` |
| `/history TICKER` | Historical scores | `/history TSLA` |

---

## 🔐 Security

- Never commit `.env` file
- Keep Discord token secret
- Use Railway's environment variables
- Database URL auto-injected by Railway

---

## 📊 Monitoring

**Railway Dashboard:**
- View logs in real-time
- Monitor CPU/memory usage
- Check database health
- Track deployments

**Discord:**
- Bot shows online status
- Logs posted to dedicated channel
- Alert frequency monitoring

---

## 🐛 Troubleshooting

### Bot Won't Start
```bash
# Check logs
railway logs

# Common issues:
- DISCORD_BOT_TOKEN not set
- DATABASE_URL not configured
- Missing required intents in Discord Developer Portal
```

### No Alerts Posting
```bash
# Verify channel IDs are set
railway variables

# Check permissions
- Bot has "Send Messages" in channels
- Bot role is above Free/Pro roles
```

### Database Errors
```bash
# Check connection
railway shell
python -c "from database import Database; db = Database()"

# Reset database (WARNING: deletes all data)
railway shell
dropdb swarm && createdb swarm
python database.py
```

---

## 📞 Support

Questions? Issues? Want to contribute?

- GitHub Issues: [github.com/yourusername/swarm-bot/issues]
- Discord: Your server
- Email: your@email.com

---

## 📜 License

MIT License - Use freely, attribution appreciated

---

## 🎯 Roadmap

### v1.0 (Current)
- [x] SWARM SCORE algorithm
- [x] Discord bot with slash commands
- [x] PostgreSQL database
- [x] Railway deployment
- [x] Free vs Pro tiers

### v1.1 (Next)
- [ ] Paid data integration (Polygon.io)
- [ ] Advanced charting
- [ ] Mobile push notifications
- [ ] Custom watchlist alerts

### v2.0 (Future)
- [ ] Web dashboard
- [ ] AI-powered pattern recognition
- [ ] Backtesting engine
- [ ] Premium tier ($149/month)

---

**Built with ❤️ for serious traders**

**Trade your plan. Manage your risk. Honor your stops.**
