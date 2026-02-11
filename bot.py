"""
SWARM Intelligence Discord Bot
Professional trading intelligence with SEC filing analysis edge
"""

import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
import asyncio
from datetime import datetime, timedelta
import json
from pathlib import Path
from swarm_score import calculate_swarm_score
from database import Database, Alert, Ticker
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('swarm_bot.log'),
        logging.StreamHandler()
    ]
)

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)
db = Database()

# Channel IDs (set these after creating channels)
CHANNEL_IDS = {
    'critical_setups': None,      # 90+ scores
    'active_setups': None,         # 75-89 scores
    'watchlist': None,             # 60-74 scores
    'sec_filings': None,           # CHIRP alerts
    'momentum_scanner': None,      # FLOCK results
    'technical_setups': None,      # SKY_SCRAPER
    'news_feed': None,             # News alerts
    'financial_health': None,      # 4/4 rated tickers
    'top_gainers': None,           # Live dashboard
    'top_losers': None,            # Live dashboard
    'community_watch': None,       # Member watchlists
    'daily_context': None,         # Morning briefings
}

# Role IDs (set these after creating roles)
ROLE_IDS = {
    'pro': None,
    'free': None,
}

# Professional trader voice templates
ALERT_TEMPLATES = {
    'critical': """🎯 SWARM SCORE: {score} - High Probability Setup

{ticker} - {setup_type}

Setup Analysis:
{sec_analysis}
{technical_analysis}
{financial_analysis}

Risk Parameters:
├─ Entry Zone: ${entry_low:.2f} - ${entry_high:.2f}
├─ Stop Loss: ${stop_loss:.2f} (below support, -{stop_risk:.1f}% risk)
├─ Initial Target: ${target_1:.2f} (+{target_1_gain:.1f}%)
├─ Extended Target: ${target_2:.2f} (+{target_2_gain:.1f}%)
├─ Risk:Reward = {risk_reward:.1f}:1
└─ Position Size: Maximum 1-2% account risk

Probability Assessment:
Based on {sample_size} historical comparable setups:
├─ Win Rate: {win_rate}% ({wins}/{sample_size})
├─ Average Gain: +{avg_gain:.1f}%
├─ Average Hold Time: {avg_hold_time} hours
└─ Largest Winner: +{max_win:.1f}%

{execution_plan}

This is a high-probability setup with defined risk.
Trade your plan, manage your risk, honor your stops.""",

    'active': """📊 SWARM SCORE: {score} - Worth Monitoring

{ticker} - {setup_type}

Current Analysis:
{analysis}

Context:
{context}

Watch for:
{watch_criteria}

Risk Assessment:
{risk_assessment}

Status: {status}""",

    'watchlist': """📋 SWARM SCORE: {score} - Early Stage

{ticker} - {setup_type}

{brief_analysis}

Status: Monitor only. Not actionable yet.""",
}

@bot.event
async def on_ready():
    """Bot initialization"""
    logging.info(f'✅ SWARM Bot logged in as {bot.user}')
    logging.info(f'Connected to {len(bot.guilds)} guild(s)')
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        logging.info(f'Synced {len(synced)} command(s)')
    except Exception as e:
        logging.error(f'Failed to sync commands: {e}')
    
    # Start background tasks
    check_for_alerts.start()
    post_daily_context.start()


@tasks.loop(minutes=5)
async def check_for_alerts():
    """
    Check for new alerts from:
    - FLOCK (filtered_tickers.csv)
    - SKY_SCRAPER (filtered_tickers_breakout/swing/bounce.csv)
    - CHIRP (SEC filings analysis)
    """
    try:
        # Check FLOCK results
        flock_file = Path.home() / 'SEC' / 'Swarm' / 'Nest' / 'filtered_tickers.csv'
        if flock_file.exists():
            await process_flock_results(flock_file)
        
        # Check SKY_SCRAPER results
        for strategy in ['breakout', 'swing', 'bounce']:
            scanner_file = Path.home() / 'SEC' / 'Swarm' / 'Nest' / f'filtered_tickers_{strategy}.csv'
            if scanner_file.exists():
                await process_scanner_results(scanner_file, strategy)
        
        # Check for new SEC filings (CHIRP would create alerts)
        # This would integrate with your existing CHIRP output
        
    except Exception as e:
        logging.error(f'Error in check_for_alerts: {e}')


async def process_flock_results(file_path):
    """Process FLOCK momentum scanner results"""
    try:
        import pandas as pd
        df = pd.read_csv(file_path)
        
        for _, row in df.iterrows():
            ticker = row['Ticker']
            
            # Calculate SWARM SCORE
            score_data = await calculate_swarm_score(ticker)
            
            if score_data['score'] >= 60:  # Minimum threshold
                await post_alert(ticker, score_data, 'momentum')
                
    except Exception as e:
        logging.error(f'Error processing FLOCK results: {e}')


async def process_scanner_results(file_path, strategy):
    """Process SKY_SCRAPER technical setup results"""
    try:
        import pandas as pd
        df = pd.read_csv(file_path)
        
        for _, row in df.iterrows():
            ticker = row['Ticker']
            
            score_data = await calculate_swarm_score(ticker)
            score_data['strategy'] = strategy
            
            if score_data['score'] >= 60:
                await post_alert(ticker, score_data, f'{strategy}_technical')
                
    except Exception as e:
        logging.error(f'Error processing scanner results: {e}')


async def post_alert(ticker, score_data, alert_type):
    """Post alert to appropriate channel based on SWARM SCORE"""
    try:
        score = score_data['score']
        
        # Determine channel based on score
        if score >= 90:
            channel_id = CHANNEL_IDS['critical_setups']
            template = 'critical'
        elif score >= 75:
            channel_id = CHANNEL_IDS['active_setups']
            template = 'active'
        else:
            channel_id = CHANNEL_IDS['watchlist']
            template = 'watchlist'
        
        if not channel_id:
            logging.warning(f'Channel ID not set for score {score}')
            return
        
        channel = bot.get_channel(channel_id)
        if not channel:
            logging.error(f'Channel {channel_id} not found')
            return
        
        # Format alert message
        message = format_alert(ticker, score_data, template)
        
        # Check if already posted recently (dedupe)
        if await is_duplicate_alert(ticker, score):
            logging.info(f'Skipping duplicate alert for {ticker}')
            return
        
        # Post to Discord
        await channel.send(message)
        
        # Save to database
        db.save_alert(ticker, score, score_data, alert_type)
        
        logging.info(f'Posted {template} alert for {ticker} (score: {score})')
        
    except Exception as e:
        logging.error(f'Error posting alert: {e}')


def format_alert(ticker, score_data, template):
    """Format alert using professional trader voice"""
    # This would be filled in with actual data from score_data
    # For now, return basic format
    score = score_data['score']
    
    if template == 'critical':
        return f"""🎯 SWARM SCORE: {score} - High Probability Setup

{ticker} - Multiple Convergence Event

Setup Analysis:
├─ SEC Signal: {score_data.get('sec_score', 0)}/35
├─ Technical: {score_data.get('technical_score', 0)}/35
├─ Financial: {score_data.get('financial_score', 0)}/15
└─ News: {score_data.get('news_score', 0)}/10

Historical pattern: {score_data.get('win_rate', 0)}% win rate on similar setups.

[Full analysis available to Pro members]
[Upgrade to Pro for entry zones, stops, and targets]"""
    
    elif template == 'active':
        return f"""📊 SWARM SCORE: {score} - Worth Monitoring

{ticker} - Developing Setup

Current Analysis:
├─ SEC: {score_data.get('sec_score', 0)}/35
├─ Technical: {score_data.get('technical_score', 0)}/35
├─ Financial: {score_data.get('financial_score', 0)}/15

[Full analysis for Pro members]"""
    
    else:
        return f"""📋 SWARM SCORE: {score} - Early Stage

{ticker} - Monitor Only

Score breakdown: SEC {score_data.get('sec_score', 0)} | Tech {score_data.get('technical_score', 0)} | Finance {score_data.get('financial_score', 0)}"""


async def is_duplicate_alert(ticker, score):
    """Check if alert was recently posted"""
    # Check database for alerts in last 4 hours
    recent = db.get_recent_alerts(ticker, hours=4)
    if recent and abs(recent[0]['score'] - score) < 5:
        return True
    return False


@tasks.loop(hours=24)
async def post_daily_context():
    """Post morning market context (7:00 AM ET)"""
    try:
        # Calculate time until 7 AM ET
        now = datetime.now()
        # This would post daily market context
        # Implement based on your needs
        
    except Exception as e:
        logging.error(f'Error in daily context: {e}')


# Slash Commands

@bot.tree.command(name="score", description="Get current SWARM SCORE for any ticker")
@app_commands.describe(ticker="Stock ticker symbol")
async def score_command(interaction: discord.Interaction, ticker: str):
    """Get SWARM SCORE for a ticker"""
    await interaction.response.defer()
    
    try:
        ticker = ticker.upper().strip()
        score_data = await calculate_swarm_score(ticker)
        
        message = f"""🎯 SWARM SCORE for {ticker}: {score_data['score']}/100

Breakdown:
├─ SEC Signal: {score_data.get('sec_score', 0)}/35
├─ Technical: {score_data.get('technical_score', 0)}/35
├─ Financial: {score_data.get('financial_score', 0)}/15
└─ News: {score_data.get('news_score', 0)}/10

Confidence: {score_data.get('confidence', 'Unknown')}"""
        
        await interaction.followup.send(message)
        
    except Exception as e:
        await interaction.followup.send(f"Error calculating score: {str(e)}")


@bot.tree.command(name="watch", description="Add ticker to your personal watchlist")
@app_commands.describe(ticker="Stock ticker symbol")
async def watch_command(interaction: discord.Interaction, ticker: str):
    """Add ticker to personal watchlist"""
    try:
        ticker = ticker.upper().strip()
        user_id = interaction.user.id
        
        db.add_to_watchlist(user_id, ticker)
        
        await interaction.response.send_message(
            f"✅ Added {ticker} to your watchlist", 
            ephemeral=True
        )
        
    except Exception as e:
        await interaction.response.send_message(
            f"Error: {str(e)}", 
            ephemeral=True
        )


@bot.tree.command(name="alerts", description="See today's high-scoring alerts")
async def alerts_command(interaction: discord.Interaction):
    """Show today's alerts"""
    await interaction.response.defer()
    
    try:
        alerts = db.get_todays_alerts(min_score=75)
        
        if not alerts:
            await interaction.followup.send("No high-scoring alerts today yet.")
            return
        
        message = "📊 Today's High-Priority Alerts:\n\n"
        for alert in alerts[:10]:  # Top 10
            message += f"• {alert['ticker']}: Score {alert['score']} ({alert['time']})\n"
        
        await interaction.followup.send(message)
        
    except Exception as e:
        await interaction.followup.send(f"Error: {str(e)}")


@bot.tree.command(name="history", description="See past SWARM SCORES for a ticker")
@app_commands.describe(ticker="Stock ticker symbol")
async def history_command(interaction: discord.Interaction, ticker: str):
    """Show historical SWARM SCORES"""
    await interaction.response.defer()
    
    try:
        ticker = ticker.upper().strip()
        history = db.get_ticker_history(ticker, days=30)
        
        if not history:
            await interaction.followup.send(f"No history found for {ticker}")
            return
        
        message = f"📈 SWARM SCORE History for {ticker} (Last 30 days):\n\n"
        for entry in history[:5]:  # Last 5
            message += f"• {entry['date']}: Score {entry['score']}\n"
        
        message += f"\nAverage Score: {sum(h['score'] for h in history)/len(history):.1f}"
        
        await interaction.followup.send(message)
        
    except Exception as e:
        await interaction.followup.send(f"Error: {str(e)}")


if __name__ == "__main__":
    # Load token from environment
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    if not TOKEN:
        logging.error("DISCORD_BOT_TOKEN not set in environment")
        exit(1)
    
    # Run bot
    bot.run(TOKEN)
