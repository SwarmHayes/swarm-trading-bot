# 🚂 Railway Deployment Guide

## Quick Deploy (5 minutes)

### 1. Prepare Your Repo

```bash
# Clone SWARM to your GitHub
git clone <this-repo>
cd swarm-bot

# Push to YOUR GitHub (create new repo first)
git remote set-url origin https://github.com/YOUR_USERNAME/swarm-bot
git push -u origin main
```

### 2. Deploy to Railway

1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Choose your `swarm-bot` repo
6. Click **"Deploy Now"**

### 3. Add PostgreSQL

1. In your Railway project, click **"New"**
2. Select **"Database"** → **"PostgreSQL"**
3. Railway automatically creates `DATABASE_URL` variable

### 4. Configure Environment Variables

1. Click on your service (the bot)
2. Go to **"Variables"** tab
3. Click **"+ New Variable"**
4. Add these:

```
DISCORD_BOT_TOKEN=your_discord_token_here

# After creating Discord channels, add their IDs:
CHANNEL_CRITICAL_SETUPS=123456789012345678
CHANNEL_ACTIVE_SETUPS=123456789012345678
CHANNEL_WATCHLIST=123456789012345678
CHANNEL_SEC_FILINGS=123456789012345678
CHANNEL_MOMENTUM_SCANNER=123456789012345678
CHANNEL_TECHNICAL_SETUPS=123456789012345678
CHANNEL_NEWS_FEED=123456789012345678
CHANNEL_FINANCIAL_HEALTH=123456789012345678
CHANNEL_TOP_GAINERS=123456789012345678
CHANNEL_TOP_LOSERS=123456789012345678
CHANNEL_COMMUNITY_WATCH=123456789012345678
CHANNEL_DAILY_CONTEXT=123456789012345678

# After creating Discord roles, add their IDs:
ROLE_PRO=123456789012345678
ROLE_FREE=123456789012345678
```

### 5. Check Deployment

1. Go to **"Deployments"** tab
2. Click the most recent deployment
3. Click **"View Logs"**
4. Look for: `✅ SWARM Bot logged in as <bot-name>`

### 6. Test the Bot

In Discord:
```
/score NVDA
```

Should return SWARM SCORE for NVIDIA.

---

## Railway Free Tier Limits

- **$5 credit/month** (enough for SWARM)
- **500 hours/month** execution time
- **100 GB** bandwidth
- **1 GB** database storage

**SWARM uses ~$2-3/month on free tier.**

---

## Updating Code

```bash
# Make changes locally
git add .
git commit -m "Updated SWARM algorithm"
git push

# Railway auto-deploys on push
```

Watch deployment in Railway dashboard.

---

## Monitoring

### View Logs
```bash
# Real-time logs
railway logs --follow

# Or in dashboard:
Deployments → Click deployment → View Logs
```

### Database Access
```bash
# Connect to database
railway connect

# In railway shell:
python
>>> from database import Database
>>> db = Database()
>>> db.get_todays_alerts()
```

---

## Troubleshooting

### Bot Won't Start

**Check logs:**
```
railway logs
```

**Common issues:**
- `DISCORD_BOT_TOKEN` not set
- Missing intents in Discord Developer Portal
- Database connection failed

### Bot Online But Not Responding

**Check:**
1. Slash commands synced? (Bot needs to restart once)
2. Bot has permissions in channels?
3. Role hierarchy correct? (Bot role above Free/Pro)

### Database Errors

**Reset database:**
```bash
railway shell
python database.py
```

This recreates all tables.

---

## Scaling

### When You Get More Users:

**100+ members:**
- Upgrade to Railway **Hobby Plan** ($5/month)
- Adds more execution time

**500+ members:**
- Upgrade to Railway **Pro Plan** ($20/month)
- Unlimited execution time
- Better database performance

**1000+ members:**
- Consider dedicated hosting
- Or stay on Railway Pro (works fine)

---

## Cost Breakdown

```
Month 1-2: FREE (Railway credit)
Month 3+: $5/month (Hobby plan)

With 100 members @ $79/month:
Revenue: $7,900
Costs: $5 (Railway) + $30 (Mosquito/Nuntio) = $35
Profit: $7,865/month
```

**99.6% profit margin** 😱

---

## Backup Strategy

### Database Backups

Railway auto-backs up PostgreSQL daily.

**Manual backup:**
```bash
railway run pg_dump > backup.sql
```

### Code Backups

GitHub is your backup. Always commit:
```bash
git add .
git commit -m "Backup before changes"
git push
```

---

## Going Live Checklist

- [ ] Discord bot token set
- [ ] All channels created and IDs added
- [ ] Roles created and IDs added
- [ ] Bot has permissions in all channels
- [ ] Database connected
- [ ] Test `/score` command works
- [ ] Monitor logs for 24 hours
- [ ] Verify alerts are posting

---

**You're ready to launch! 🚀**
