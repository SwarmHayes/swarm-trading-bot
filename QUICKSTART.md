# ⚡ SWARM Quick Start - 15 Minutes to Live

## 🎯 Goal
Get SWARM Discord bot running in 15 minutes.

---

## 📋 Prerequisites (2 minutes)

1. ✅ Discord account + server (where bot will live)
2. ✅ GitHub account (free)
3. ✅ Railway.app account (free) - Sign up at [railway.app](https://railway.app)

**That's it. No credit card needed for Railway free tier.**

---

## 🚀 Deployment Steps

### Step 1: Get Discord Bot Token (3 minutes)

1. Go to https://discord.com/developers/applications
2. Click **"New Application"**
3. Name: `SWARM Intelligence`
4. Go to **"Bot"** tab → Click **"Add Bot"** → **"Yes, do it!"**
5. **COPY THE TOKEN** (you'll need this)
6. Scroll down to **"Privileged Gateway Intents"**:
   - ✅ Presence Intent
   - ✅ Server Members Intent
   - ✅ Message Content Intent
7. Click **"Save Changes"**

### Step 2: Invite Bot to Server (1 minute)

1. Go to **"OAuth2"** → **"URL Generator"**
2. Check these scopes:
   - ✅ `bot`
   - ✅ `applications.commands`
3. Bot Permissions - check:
   - ✅ Send Messages
   - ✅ Embed Links
   - ✅ Read Message History
   - ✅ Use Slash Commands
   - ✅ Manage Roles
4. Copy the generated URL at bottom
5. Open in new tab → Select your server → **"Authorize"**

Bot is now in your server (offline for now).

### Step 3: Create Channels (2 minutes)

In your Discord server, create these channels:

**Copy/paste this structure:**
```
🎯 SWARM INTELLIGENCE
├─ 🔥-critical-setups
├─ 📊-active-setups
├─ 📋-watchlist
├─ 📄-sec-filings
├─ 📈-momentum-scanner
├─ 🎯-technical-setups
├─ 📰-news-feed
├─ 💰-financial-health
├─ 💎-top-gainers
├─ 📉-top-losers
└─ 🌊-community-watch
```

**Get Channel IDs:**
1. Enable Developer Mode: Settings → Advanced → ✅ Developer Mode
2. Right-click each channel → "Copy Channel ID"
3. **Save these in a text file** (you'll need them)

### Step 4: Create Roles (1 minute)

1. Server Settings → Roles → **"Create Role"**
2. Name: `SWARM Pro` (full access)
3. Create another: `SWARM Free` (limited)
4. Right-click each role → "Copy Role ID"
5. **Save these too**

### Step 5: Deploy to Railway (5 minutes)

#### A. Push Code to GitHub

```bash
# Option 1: Fork this repo on GitHub (easiest)
# Just click "Fork" button on GitHub

# Option 2: Clone and push to your own repo
git clone <this-repo>
cd swarm-bot
git remote set-url origin https://github.com/YOUR_USERNAME/swarm-bot
git push -u origin main
```

#### B. Deploy on Railway

1. Go to https://railway.app
2. Sign in with GitHub
3. Click **"New Project"**
4. **"Deploy from GitHub repo"**
5. Select your `swarm-bot` repo
6. Click **"Deploy Now"**

Railway will start building...

#### C. Add Database

1. In same Railway project, click **"New"**
2. **"Database"** → **"PostgreSQL"**
3. Done! Railway auto-connects it

#### D. Add Environment Variables

1. Click your service (the bot, not database)
2. **"Variables"** tab
3. Click **"+ New Variable"**
4. Add:

```
DISCORD_BOT_TOKEN=paste_your_token_from_step_1
```

5. Add all your channel IDs:

```
CHANNEL_CRITICAL_SETUPS=paste_channel_id_here
CHANNEL_ACTIVE_SETUPS=paste_channel_id_here
CHANNEL_WATCHLIST=paste_channel_id_here
CHANNEL_SEC_FILINGS=paste_channel_id_here
CHANNEL_MOMENTUM_SCANNER=paste_channel_id_here
CHANNEL_TECHNICAL_SETUPS=paste_channel_id_here
CHANNEL_NEWS_FEED=paste_channel_id_here
CHANNEL_FINANCIAL_HEALTH=paste_channel_id_here
CHANNEL_TOP_GAINERS=paste_channel_id_here
CHANNEL_TOP_LOSERS=paste_channel_id_here
CHANNEL_COMMUNITY_WATCH=paste_channel_id_here
```

6. Add role IDs:

```
ROLE_PRO=paste_role_id_here
ROLE_FREE=paste_role_id_here
```

#### E. Wait for Deployment

Watch **"Deployments"** tab. Should see:
```
✅ Build successful
✅ Deployment live
```

### Step 6: Verify (1 minute)

1. Check Discord - bot should be **ONLINE** 🟢
2. In any channel, type: `/score NVDA`
3. Should get SWARM SCORE response!

**🎉 YOU'RE LIVE!**

---

## 🎯 What Now?

### Test Commands

```
/score AAPL        - Apple stock SWARM SCORE
/watch TSLA        - Add Tesla to watchlist
/alerts            - Today's alerts
/history NVDA      - Historical scores
```

### Monitor Your Bot

**Railway Dashboard:**
- Click **"Deployments"**
- Click latest deployment
- **"View Logs"** - see everything happening

**Look for:**
```
✅ SWARM Bot logged in as SWARM Intelligence
✅ Synced 4 command(s)
```

### Connect Your Existing Scripts

Your existing cron jobs will feed data to SWARM:

```bash
# FLOCK runs (on your server)
7:02 AM → Outputs to ~/SEC/Swarm/Nest/filtered_tickers.csv

# SWARM reads this file
Every 5 min → Checks for new tickers → Posts alerts
```

**SWARM monitors these files:**
- `~/SEC/Swarm/Nest/filtered_tickers.csv` (FLOCK)
- `~/SEC/Swarm/Nest/filtered_tickers_breakout.csv` (SKY_SCRAPER)
- `~/SEC/Swarm/Nest/sec_filings/` (CHIRP)

**No changes needed to your existing scripts!**

---

## 💰 Start Monetizing

### 1. Set Role Permissions

**SWARM Pro role** gets:
- Full access to all channels
- See complete analysis

**SWARM Free role** gets:
- Read-only in alert channels
- See ticker + score only (not full analysis)

### 2. Pricing

```
Free Tier: $0 (teaser, create FOMO)
Pro Tier: $79/month (full alpha)
```

### 3. Payment

Use Stripe + Discord role automation:
- https://whop.com
- https://memberful.com
- Or Patreon integration

---

## 📊 Track Performance

### Daily Check:
```
/alerts           - See what was posted
Railway logs      - Check for errors
```

### Weekly:
- Monitor alert quality
- Adjust SWARM SCORE weights if needed
- Add/remove channels as needed

### Monthly:
- Review member feedback
- Consider paid data upgrades
- Scale Railway plan if needed

---

## 🆘 Common Issues

### Bot Won't Start
```
Check Railway logs:
"DISCORD_BOT_TOKEN not set"
→ Add token in Railway variables

"DATABASE_URL not configured"
→ Make sure PostgreSQL is added
```

### Bot Online But No Commands
```
Enable intents in Discord Developer Portal:
Bot → Privileged Gateway Intents → Enable all 3
```

### Alerts Not Posting
```
Check channel IDs are correct in Railway variables
Check bot has permissions in channels
Check bot role is ABOVE free/pro roles
```

---

## 🚀 You're Ready!

**Current status:**
- ✅ Bot running
- ✅ Commands working
- ✅ Database connected
- ✅ Channels created
- ✅ Roles configured

**Next 24 hours:**
- Test all slash commands
- Verify SWARM SCORE calculations
- Monitor logs for errors
- Post a test alert manually

**Next 7 days:**
- Connect your existing scripts
- Invite 5-10 beta testers (free)
- Gather feedback
- Adjust algorithm weights

**Next 30 days:**
- Launch Pro tier
- Start marketing
- Build to 50 members
- Profit: $3,950/month

---

**Welcome to SWARM Intelligence. Let's build something amazing. 🎯**
