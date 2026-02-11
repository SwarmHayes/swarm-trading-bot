"""
SWARM SCORE Calculation Algorithm
Weights: 40% SEC, 35% Technical, 15% Financial, 10% News
"""

import yfinance as yf
import pandas as pd
from pathlib import Path
import os
import re
import json
from datetime import datetime, timedelta
import logging

# Weighting configuration
WEIGHTS = {
    'sec': 0.40,        # 40 points max
    'technical': 0.35,  # 35 points max
    'financial': 0.15,  # 15 points max
    'news': 0.10,       # 10 points max
}

# SEC Filing keywords and their scores
SEC_KEYWORDS = {
    'merger': 10,
    'acquisition': 10,
    'strategic alternatives': 8,
    'bankruptcy': 10,
    'chapter 11': 10,
    'fda approval': 10,
    'fda': 7,
    'phase iii': 8,
    'phase 3': 8,
    'clinical trial': 5,
    'offering': 6,
    'private placement': 5,
    'share repurchase': 7,
    'ceo': 3,
    'cfo': 3,
    'resignation': 5,
    'lawsuit': 4,
    'settlement': 4,
    'dividend': 3,
    'stock split': 4,
}


async def calculate_swarm_score(ticker: str) -> dict:
    """
    Calculate comprehensive SWARM SCORE for a ticker
    
    Returns dict with:
    - score: Overall 0-100 score
    - sec_score: SEC signal component (0-40)
    - technical_score: Technical component (0-35)
    - financial_score: Financial health component (0-15)
    - news_score: News momentum component (0-10)
    - confidence: Confidence level
    - breakdown: Detailed scoring breakdown
    """
    
    try:
        # Calculate each component
        sec_score = await calculate_sec_score(ticker)
        technical_score = await calculate_technical_score(ticker)
        financial_score = await calculate_financial_score(ticker)
        news_score = await calculate_news_score(ticker)
        
        # Calculate total score
        total_score = sec_score + technical_score + financial_score + news_score
        
        # Determine confidence level
        confidence = get_confidence_level(total_score, sec_score, technical_score)
        
        return {
            'score': int(total_score),
            'sec_score': int(sec_score),
            'technical_score': int(technical_score),
            'financial_score': int(financial_score),
            'news_score': int(news_score),
            'confidence': confidence,
            'breakdown': {
                'sec': get_sec_breakdown(ticker),
                'technical': get_technical_breakdown(ticker),
                'financial': get_financial_breakdown(ticker),
            }
        }
        
    except Exception as e:
        logging.error(f'Error calculating SWARM SCORE for {ticker}: {e}')
        return {
            'score': 0,
            'sec_score': 0,
            'technical_score': 0,
            'financial_score': 0,
            'news_score': 0,
            'confidence': 'Unknown',
            'breakdown': {}
        }


async def calculate_sec_score(ticker: str) -> float:
    """
    Calculate SEC Signal Score (0-40 points)
    
    Based on:
    - Recent SEC filings (8-K, 10-K, 10-Q, S-1)
    - Keyword detection in filings
    - Filing timing (premarket bonus)
    - Historical pattern matching
    """
    
    score = 0
    max_score = 40
    
    try:
        # Check for recent SEC filings
        filings_path = Path.home() / 'SEC' / 'Swarm' / 'Nest' / 'sec_filings' / 'sec-edgar-filings' / ticker
        
        if not filings_path.exists():
            return 0
        
        # Find most recent filing
        recent_filing = find_recent_filing(filings_path)
        
        if not recent_filing:
            return 0
        
        # Read filing content
        with open(recent_filing, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read().lower()
        
        # Score based on keywords
        keyword_score = 0
        matched_keywords = []
        
        for keyword, points in SEC_KEYWORDS.items():
            if keyword.lower() in content:
                keyword_score += points
                matched_keywords.append(keyword)
        
        # Normalize keyword score to 0-30 range
        if keyword_score > 0:
            score += min(30, keyword_score)
        
        # Bonus for 8-K filing (usually more significant)
        if '8-K' in str(recent_filing) or '8-k' in str(recent_filing):
            score += 5
        
        # Bonus for filing timing (if filed in last 24 hours)
        file_age = datetime.now() - datetime.fromtimestamp(recent_filing.stat().st_mtime)
        if file_age < timedelta(hours=24):
            score += 5
        
        # Cap at max score
        score = min(score, max_score)
        
        logging.info(f'SEC score for {ticker}: {score}/40 (keywords: {matched_keywords})')
        return score
        
    except Exception as e:
        logging.error(f'Error calculating SEC score for {ticker}: {e}')
        return 0


async def calculate_technical_score(ticker: str) -> float:
    """
    Calculate Technical Score (0-35 points)
    
    Based on:
    - Price action (breakout, support/resistance)
    - Volume expansion
    - RSI levels
    - Moving averages
    """
    
    score = 0
    max_score = 35
    
    try:
        # Get price data
        stock = yf.Ticker(ticker)
        hist = stock.history(period='2mo')
        
        if hist.empty:
            return 0
        
        current_price = hist['Close'].iloc[-1]
        current_volume = hist['Volume'].iloc[-1]
        
        # Volume score (0-15 points)
        avg_volume = hist['Volume'].tail(20).mean()
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
        
        if volume_ratio > 3.0:
            score += 15
        elif volume_ratio > 2.0:
            score += 12
        elif volume_ratio > 1.5:
            score += 8
        elif volume_ratio > 1.2:
            score += 5
        
        # RSI score (0-10 points)
        rsi = calculate_rsi(hist['Close'])
        if rsi:
            if 40 <= rsi <= 60:  # Goldilocks zone
                score += 10
            elif 30 <= rsi <= 70:
                score += 7
            elif rsi < 30:  # Oversold
                score += 5
            else:  # Overbought
                score += 2
        
        # Price action score (0-10 points)
        # Check for breakout above 52-week high
        high_52w = hist['High'].max()
        if current_price >= high_52w * 0.98:  # Within 2% of 52W high
            score += 10
        elif current_price >= high_52w * 0.95:  # Within 5%
            score += 7
        
        # Check 50-day SMA
        if len(hist) >= 50:
            sma50 = hist['Close'].tail(50).mean()
            if current_price > sma50 * 1.10:  # 10% above SMA50
                score += 5
        
        score = min(score, max_score)
        
        logging.info(f'Technical score for {ticker}: {score}/35 (vol: {volume_ratio:.1f}x, RSI: {rsi})')
        return score
        
    except Exception as e:
        logging.error(f'Error calculating technical score for {ticker}: {e}')
        return 0


async def calculate_financial_score(ticker: str) -> float:
    """
    Calculate Financial Health Score (0-15 points)
    
    Based on:
    - Cash vs Debt ratio
    - Balance sheet health
    - Your existing 1-4 star rating system
    """
    
    score = 0
    max_score = 15
    
    try:
        # Try to read from your existing financial health analysis
        # This would integrate with your check_financial_health.py output
        
        # For now, use basic yfinance data
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Get cash and debt
        cash = info.get('totalCash', 0)
        debt = info.get('totalDebt', 0)
        
        if cash > 0 and debt >= 0:
            # Calculate debt-to-equity or cash-to-debt ratio
            if debt == 0:
                score = 15  # No debt = excellent
            else:
                ratio = cash / debt
                if ratio > 2.0:  # Cash > 2x debt
                    score = 15
                elif ratio > 1.0:  # Cash > debt
                    score = 12
                elif ratio > 0.5:  # Cash > 50% of debt
                    score = 8
                else:
                    score = 4
        
        # Alternative: map your 1-4 star rating
        # If you have a rating file, read it here
        # rating = get_financial_rating(ticker)
        # score = rating * 3.75  # 4 stars = 15 points
        
        logging.info(f'Financial score for {ticker}: {score}/15')
        return score
        
    except Exception as e:
        logging.error(f'Error calculating financial score for {ticker}: {e}')
        return 0


async def calculate_news_score(ticker: str) -> float:
    """
    Calculate News Momentum Score (0-10 points)
    
    Based on:
    - Number of recent mentions
    - News sentiment
    - Social media activity
    """
    
    score = 0
    max_score = 10
    
    try:
        # This would integrate with your Benzinga/PR monitor
        # For now, basic implementation
        
        # Check if ticker appears in recent news feeds
        # Check Benzinga output
        benzinga_file = Path.home() / 'SEC' / 'Swarm' / 'Nest' / 'benzinga_feed.json'
        if benzinga_file.exists():
            with open(benzinga_file, 'r') as f:
                benzinga_data = json.load(f)
            
            if ticker in benzinga_data:
                # Score based on urgency from benzinga
                urgency = benzinga_data[ticker].get('urgency', 0)
                score = min(urgency * 3, max_score)  # Scale urgency to 0-10
        
        logging.info(f'News score for {ticker}: {score}/10')
        return score
        
    except Exception as e:
        logging.error(f'Error calculating news score for {ticker}: {e}')
        return 0


def calculate_rsi(prices, periods=14):
    """Calculate RSI indicator"""
    try:
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
        
        if loss.iloc[-1] == 0:
            return None
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs.iloc[-1]))
        return rsi
    except:
        return None


def find_recent_filing(ticker_path: Path) -> Path:
    """Find most recent SEC filing for a ticker"""
    try:
        all_files = []
        
        for filing_type in ['8-K', '10-K', '10-Q', 'S-1']:
            filing_path = ticker_path / filing_type
            if filing_path.exists():
                for file in filing_path.rglob('*.txt'):
                    all_files.append(file)
        
        if not all_files:
            return None
        
        # Sort by modification time, return most recent
        all_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        return all_files[0]
        
    except Exception as e:
        logging.error(f'Error finding recent filing: {e}')
        return None


def get_confidence_level(score, sec_score, technical_score) -> str:
    """Determine confidence level based on score and components"""
    
    if score >= 90:
        return "VERY HIGH"
    elif score >= 80:
        if sec_score >= 30 and technical_score >= 25:
            return "HIGH"
        return "MODERATE-HIGH"
    elif score >= 70:
        return "MODERATE"
    elif score >= 60:
        return "LOW-MODERATE"
    else:
        return "LOW"


def get_sec_breakdown(ticker: str) -> dict:
    """Get detailed SEC component breakdown"""
    # Placeholder - would return detailed SEC analysis
    return {}


def get_technical_breakdown(ticker: str) -> dict:
    """Get detailed technical component breakdown"""
    # Placeholder - would return detailed technical analysis
    return {}


def get_financial_breakdown(ticker: str) -> dict:
    """Get detailed financial component breakdown"""
    # Placeholder - would return detailed financial analysis
    return {}


if __name__ == "__main__":
    # Test the scoring system
    import asyncio
    
    async def test():
        ticker = "NVDA"
        result = await calculate_swarm_score(ticker)
        print(f"\nSWARM SCORE for {ticker}:")
        print(f"Total: {result['score']}/100")
        print(f"  SEC: {result['sec_score']}/40")
        print(f"  Technical: {result['technical_score']}/35")
        print(f"  Financial: {result['financial_score']}/15")
        print(f"  News: {result['news_score']}/10")
        print(f"Confidence: {result['confidence']}")
    
    asyncio.run(test())
