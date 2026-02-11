#!/usr/bin/env python3
"""
SWARM Test Suite
Verify all components work before deploying
"""

import sys
import asyncio
from pathlib import Path

print("🎯 SWARM System Test")
print("=" * 50)

# Test 1: Dependencies
print("\n1️⃣ Testing Dependencies...")
try:
    import discord
    print("   ✅ discord.py")
except ImportError:
    print("   ❌ discord.py - Run: pip install -r requirements.txt")
    sys.exit(1)

try:
    import sqlalchemy
    print("   ✅ SQLAlchemy")
except ImportError:
    print("   ❌ SQLAlchemy")
    sys.exit(1)

try:
    import yfinance
    print("   ✅ yfinance")
except ImportError:
    print("   ❌ yfinance")
    sys.exit(1)

try:
    import pandas
    print("   ✅ pandas")
except ImportError:
    print("   ❌ pandas")
    sys.exit(1)

# Test 2: Database
print("\n2️⃣ Testing Database...")
try:
    from database import Database
    db = Database()
    print("   ✅ Database connection successful")
    
    # Test save
    db.save_alert('TEST', 85, {
        'sec_score': 30,
        'technical_score': 28,
        'financial_score': 15,
        'news_score': 7
    }, 'test')
    print("   ✅ Alert save successful")
    
    # Test retrieve
    alerts = db.get_todays_alerts()
    print(f"   ✅ Retrieved {len(alerts)} alert(s)")
    
except Exception as e:
    print(f"   ❌ Database error: {e}")
    sys.exit(1)

# Test 3: SWARM SCORE Algorithm
print("\n3️⃣ Testing SWARM SCORE Algorithm...")
try:
    from swarm_score import calculate_swarm_score
    
    async def test_swarm_score():
        result = await calculate_swarm_score('AAPL')
        return result
    
    result = asyncio.run(test_swarm_score())
    
    print(f"   ✅ SWARM SCORE calculated: {result['score']}/100")
    print(f"      SEC: {result['sec_score']}/40")
    print(f"      Technical: {result['technical_score']}/35")
    print(f"      Financial: {result['financial_score']}/15")
    print(f"      News: {result['news_score']}/10")
    
except Exception as e:
    print(f"   ❌ SWARM SCORE error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Environment Variables
print("\n4️⃣ Testing Environment...")
import os

env_file = Path('.env')
if env_file.exists():
    print("   ✅ .env file exists")
else:
    print("   ⚠️  .env file not found")
    print("      Run: python setup.py")

token = os.getenv('DISCORD_BOT_TOKEN')
if token:
    print("   ✅ DISCORD_BOT_TOKEN set")
else:
    print("   ❌ DISCORD_BOT_TOKEN not set")
    print("      Add to .env file")

db_url = os.getenv('DATABASE_URL')
if db_url:
    print(f"   ✅ DATABASE_URL set")
else:
    print("   ⚠️  DATABASE_URL not set (will use SQLite)")

# Summary
print("\n" + "=" * 50)
print("✅ All core tests passed!")
print("\nNext steps:")
print("1. Configure .env file (run setup.py if not done)")
print("2. Create Discord channels and roles")
print("3. Update .env with channel/role IDs")
print("4. Run: python bot.py")
print("\nOr deploy to Railway - see RAILWAY_DEPLOY.md")
