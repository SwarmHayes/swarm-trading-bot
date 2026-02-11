#!/usr/bin/env python3
"""
Manual Alert Example
Shows how to manually post a SWARM alert for testing
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

async def post_manual_alert():
    """Post a manual alert for testing"""
    
    # This simulates what happens when your scripts (FLOCK, CHIRP, etc.) find something
    
    ticker = "NVDA"
    
    print(f"🎯 Posting manual alert for {ticker}...")
    
    # Calculate SWARM SCORE
    from swarm_score import calculate_swarm_score
    score_data = await calculate_swarm_score(ticker)
    
    print(f"\nSWARM SCORE: {score_data['score']}/100")
    print(f"  SEC: {score_data['sec_score']}/40")
    print(f"  Technical: {score_data['technical_score']}/35")
    print(f"  Financial: {score_data['financial_score']}/15")
    print(f"  News: {score_data['news_score']}/10")
    
    # Save to database
    from database import Database
    db = Database()
    db.save_alert(ticker, score_data['score'], score_data, 'manual_test')
    
    print(f"\n✅ Alert saved to database")
    
    # Format the alert message
    score = score_data['score']
    
    if score >= 90:
        message = f"""🎯 SWARM SCORE: {score} - High Probability Setup

{ticker} - Multiple Convergence Event

Setup Analysis:
├─ SEC Signal: {score_data['sec_score']}/40
├─ Technical: {score_data['technical_score']}/35
├─ Financial: {score_data['financial_score']}/15
└─ News: {score_data['news_score']}/10

Historical pattern analysis shows strong probability.

[Full analysis available to Pro members]
[Upgrade to Pro for entry zones, stops, and targets]

Trade your plan. Manage your risk. Honor your stops."""
    
    elif score >= 75:
        message = f"""📊 SWARM SCORE: {score} - Worth Monitoring

{ticker} - Developing Setup

Current Analysis:
├─ SEC: {score_data['sec_score']}/40
├─ Technical: {score_data['technical_score']}/35
├─ Financial: {score_data['financial_score']}/15

[Full analysis for Pro members]"""
    
    else:
        message = f"""📋 SWARM SCORE: {score} - Early Stage

{ticker} - Monitor Only

Score breakdown: SEC {score_data['sec_score']} | Tech {score_data['technical_score']} | Finance {score_data['financial_score']}"""
    
    print(f"\n📨 Alert Message:")
    print("=" * 60)
    print(message)
    print("=" * 60)
    
    print(f"\n✅ This is what would be posted to Discord")
    print(f"   Channel: {'critical-setups' if score >= 90 else 'active-setups' if score >= 75 else 'watchlist'}")
    

if __name__ == "__main__":
    asyncio.run(post_manual_alert())
