"""
SWARM Intelligence Score Calculator
Uses Alpha Vantage API for market data
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class SwarmScore:
    """Calculate SWARM SCORE using Alpha Vantage API"""
    
    def __init__(self):
        self.api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        if not self.api_key:
            logger.warning("ALPHA_VANTAGE_API_KEY not set")
        else:
            logger.info(f"Alpha Vantage API key loaded: {self.api_key[:10]}...")
        self.base_url = "https://www.alphavantage.co/query"
    
    def _make_request(self, params: dict) -> Optional[dict]:
        """Make API request to Alpha Vantage"""
        try:
            params['apikey'] = self.api_key
            logger.info(f"Making Alpha Vantage request: {params.get('function')} for {params.get('symbol', 'N/A')}")
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            logger.info(f"Alpha Vantage response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Log first few keys to see what we got
                logger.info(f"Response keys: {list(data.keys())[:5]}")
                
                # Check for rate limit
                if 'Note' in data:
                    logger.warning(f"Alpha Vantage rate limit: {data['Note']}")
                    return None
                
                # Check for information message (also rate limit)
                if 'Information' in data:
                    logger.warning(f"Alpha Vantage info: {data['Information']}")
                    return None
                
                # Check for error message
                if 'Error Message' in data:
                    logger.error(f"Alpha Vantage error: {data['Error Message']}")
                    return None
                    
                return data
            else:
                logger.error(f"Alpha Vantage request failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Alpha Vantage request exception: {e}")
            return None
    
    def get_quote(self, symbol: str) -> Optional[dict]:
        """Get real-time quote data"""
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol
        }
        
        data = self._make_request(params)
        if data and 'Global Quote' in data:
            logger.info(f"Got quote data for {symbol}")
            return data['Global Quote']
        
        logger.error(f"No quote data for {symbol}")
        return None
    
    def get_daily_data(self, symbol: str) -> Optional[dict]:
        """Get daily time series data"""
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': 'compact'
        }
        
        data = self._make_request(params)
        
        if data:
            if 'Time Series (Daily)' in data:
                logger.info(f"Got daily data for {symbol} - {len(data['Time Series (Daily)'])} days")
                return data['Time Series (Daily)']
            else:
                logger.error(f"Response for {symbol} missing 'Time Series (Daily)'. Keys: {list(data.keys())}")
        else:
            logger.error(f"No response data for {symbol}")
        
        return None
    
    def get_company_overview(self, symbol: str) -> Optional[dict]:
        """Get company fundamental data"""
        params = {
            'function': 'OVERVIEW',
            'symbol': symbol
        }
        
        data = self._make_request(params)
        if data and 'Symbol' in data:
            logger.info(f"Got company overview for {symbol}")
            return data
        
        logger.error(f"No company overview for {symbol}")
        return None
    
    def calculate_technical_score(self, symbol: str) -> Tuple[int, str]:
        """Calculate technical analysis score (0-35)"""
        score = 0
        details = []
        
        try:
            # Get quote data
            quote = self.get_quote(symbol)
            if not quote:
                logger.error(f"No quote data for {symbol}")
                return 0, "No market data available"
            
            # Get daily data for volume analysis
            daily_data = self.get_daily_data(symbol)
            if not daily_data:
                logger.error(f"No daily data for {symbol}")
                return 0, "No historical data available"
            
            # Extract current metrics
            try:
                current_price = float(quote.get('05. price', 0))
                volume = int(quote.get('06. volume', 0))
                change_percent = float(quote.get('10. change percent', '0').replace('%', ''))
            except (ValueError, TypeError) as e:
                logger.error(f"Failed to parse quote data for {symbol}: {e}")
                return 0, "Invalid market data"
            
            # Calculate average volume (last 20 days)
            volumes = []
            for date_str, day_data in list(daily_data.items())[:20]:
                try:
                    volumes.append(int(day_data.get('5. volume', 0)))
                except (ValueError, TypeError):
                    continue
            
            avg_volume = sum(volumes) / len(volumes) if volumes else 0
            
            # Volume Score (0-15)
            if avg_volume > 0:
                volume_ratio = volume / avg_volume
                if volume_ratio >= 3.0:
                    score += 15
                    details.append(f"Volume 3x+ average ({volume_ratio:.1f}x)")
                elif volume_ratio >= 2.0:
                    score += 12
                    details.append(f"Volume 2x average ({volume_ratio:.1f}x)")
                elif volume_ratio >= 1.5:
                    score += 8
                    details.append(f"Volume 1.5x average ({volume_ratio:.1f}x)")
                elif volume_ratio >= 1.0:
                    score += 5
                    details.append(f"Above average volume ({volume_ratio:.1f}x)")
            
            # Price Action Score (0-10)
            if change_percent > 5:
                score += 10
                details.append(f"Strong rally (+{change_percent:.1f}%)")
            elif change_percent > 3:
                score += 8
                details.append(f"Good momentum (+{change_percent:.1f}%)")
            elif change_percent > 1:
                score += 5
                details.append(f"Positive movement (+{change_percent:.1f}%)")
            elif change_percent > 0:
                score += 3
                details.append(f"Slight gain (+{change_percent:.1f}%)")
            
            # Price Level Score (0-10)
            prices = []
            for date_str, day_data in list(daily_data.items())[:252]:
                try:
                    prices.append(float(day_data.get('2. high', 0)))
                    prices.append(float(day_data.get('3. low', 0)))
                except (ValueError, TypeError):
                    continue
            
            if prices:
                week_52_high = max(prices)
                week_52_low = min(prices)
                
                if week_52_high > week_52_low:
                    pct_from_high = ((week_52_high - current_price) / week_52_high) * 100
                    
                    if pct_from_high < 5:
                        score += 10
                        details.append(f"Near 52-week high (-{pct_from_high:.1f}%)")
                    elif pct_from_high < 10:
                        score += 7
                        details.append(f"Strong price level (-{pct_from_high:.1f}% from high)")
                    elif pct_from_high < 20:
                        score += 5
                        details.append(f"Decent price level (-{pct_from_high:.1f}% from high)")
            
            details_str = " | ".join(details) if details else "Limited data"
            logger.info(f"Technical score for {symbol}: {score}/35 - {details_str}")
            
            return score, details_str
            
        except Exception as e:
            logger.error(f"Error calculating technical score for {symbol}: {e}", exc_info=True)
            return 0, f"Error: {str(e)}"
    
    def calculate_financial_score(self, symbol: str) -> Tuple[int, str]:
        """Calculate financial health score (0-15)"""
        score = 0
        details = []
        
        try:
            overview = self.get_company_overview(symbol)
            if not overview:
                logger.error(f"No company overview for {symbol}")
                return 0, "No financial data available"
            
            # Market Cap Check (0-5)
            try:
                market_cap = float(overview.get('MarketCapitalization', 0))
                if market_cap > 10_000_000_000:
                    score += 5
                    details.append("Large cap (>$10B)")
                elif market_cap > 2_000_000_000:
                    score += 4
                    details.append("Mid cap (>$2B)")
                elif market_cap > 300_000_000:
                    score += 3
                    details.append("Small cap (>$300M)")
            except (ValueError, TypeError):
                pass
            
            # Profitability (0-5)
            try:
                profit_margin = float(overview.get('ProfitMargin', 0))
                if profit_margin > 0.15:
                    score += 5
                    details.append(f"Strong margins ({profit_margin*100:.1f}%)")
                elif profit_margin > 0.10:
                    score += 4
                    details.append(f"Good margins ({profit_margin*100:.1f}%)")
                elif profit_margin > 0.05:
                    score += 3
                    details.append(f"Positive margins ({profit_margin*100:.1f}%)")
                elif profit_margin > 0:
                    score += 2
                    details.append(f"Profitable ({profit_margin*100:.1f}%)")
            except (ValueError, TypeError):
                pass
            
            # Revenue Growth (0-5)
            try:
                revenue_growth = float(overview.get('QuarterlyRevenueGrowthYOY', 0))
                if revenue_growth > 0.25:
                    score += 5
                    details.append(f"Strong growth ({revenue_growth*100:.1f}%)")
                elif revenue_growth > 0.15:
                    score += 4
                    details.append(f"Good growth ({revenue_growth*100:.1f}%)")
                elif revenue_growth > 0.05:
                    score += 3
                    details.append(f"Growing ({revenue_growth*100:.1f}%)")
                elif revenue_growth > 0:
                    score += 2
                    details.append(f"Slight growth ({revenue_growth*100:.1f}%)")
            except (ValueError, TypeError):
                pass
            
            details_str = " | ".join(details) if details else "Limited financial data"
            logger.info(f"Financial score for {symbol}: {score}/15 - {details_str}")
            
            return score, details_str
            
        except Exception as e:
            logger.error(f"Error calculating financial score for {symbol}: {e}", exc_info=True)
            return 0, f"Error: {str(e)}"
    
    def calculate_sec_score(self, symbol: str, sec_filings_path: str = None) -> Tuple[int, str]:
        """Calculate SEC filing score (0-40)"""
        # For now, return 0 since we don't have SEC filing integration yet
        logger.info(f"SEC score for {symbol}: 0/40 - No SEC filings analyzed yet")
        return 0, "SEC analysis not yet integrated"
    
    def calculate_news_score(self, symbol: str) -> Tuple[int, str]:
        """Calculate news/sentiment score (0-10)"""
        # Simplified - just return 0 for now to avoid extra API calls
        logger.info(f"News score for {symbol}: 0/10")
        return 0, "News analysis temporarily disabled"
    
    def calculate_swarm_score(self, symbol: str, sec_filings_path: str = None) -> Dict:
        """
        Calculate complete SWARM SCORE
        
        SWARM SCORE = (SEC × 0.40) + (TECHNICAL × 0.35) + (FINANCIAL × 0.15) + (NEWS × 0.10)
        """
        logger.info(f"Calculating SWARM SCORE for {symbol}")
        
        # Calculate component scores
        sec_score, sec_details = self.calculate_sec_score(symbol, sec_filings_path)
        technical_score, technical_details = self.calculate_technical_score(symbol)
        financial_score, financial_details = self.calculate_financial_score(symbol)
        news_score, news_details = self.calculate_news_score(symbol)
        
        # Calculate weighted total
        total_score = int(
            (sec_score * 0.40) +
            (technical_score * 0.35) +
            (financial_score * 0.15) +
            (news_score * 0.10)
        )
        
        # Determine confidence level
        if total_score >= 75:
            confidence = "HIGH"
        elif total_score >= 60:
            confidence = "MODERATE"
        else:
            confidence = "LOW"
        
        result = {
            'symbol': symbol,
            'total_score': total_score,
            'confidence': confidence,
            'breakdown': {
                'sec': {'score': sec_score, 'max': 40, 'details': sec_details},
                'technical': {'score': technical_score, 'max': 35, 'details': technical_details},
                'financial': {'score': financial_score, 'max': 15, 'details': financial_details},
                'news': {'score': news_score, 'max': 10, 'details': news_details}
            },
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"SWARM SCORE for {symbol}: {total_score}/100 ({confidence})")
        logger.info(f"Breakdown - SEC: {sec_score}/40, Tech: {technical_score}/35, Fin: {financial_score}/15, News: {news_score}/10")
        
        return result
```

---

**Commit message:**
```
Add comprehensive debug logging to swarm_score
