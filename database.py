"""
Database layer for SWARM Intelligence
PostgreSQL with SQLAlchemy ORM
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import os
import logging

Base = declarative_base()

class Alert(Base):
    """SWARM alerts posted to Discord"""
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), index=True)
    score = Column(Integer)
    sec_score = Column(Float)
    technical_score = Column(Float)
    financial_score = Column(Float)
    news_score = Column(Float)
    alert_type = Column(String(50))
    channel = Column(String(50))
    score_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'ticker': self.ticker,
            'score': self.score,
            'sec_score': self.sec_score,
            'technical_score': self.technical_score,
            'financial_score': self.financial_score,
            'news_score': self.news_score,
            'alert_type': self.alert_type,
            'time': self.created_at.strftime('%H:%M'),
            'date': self.created_at.strftime('%Y-%m-%d')
        }


class Ticker(Base):
    """Ticker metadata and tracking"""
    __tablename__ = 'tickers'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), unique=True, index=True)
    company_name = Column(String(200))
    sector = Column(String(100))
    last_score = Column(Integer)
    avg_score = Column(Float)
    alert_count = Column(Integer, default=0)
    last_alert = Column(DateTime)
    is_active = Column(Boolean, default=True)
    ticker_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Watchlist(Base):
    """User watchlists"""
    __tablename__ = 'watchlists'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), index=True)  # Discord user ID
    ticker = Column(String(10), index=True)
    added_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)


class CommunityWatch(Base):
    """Community watching activity (anonymous)"""
    __tablename__ = 'community_watch'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), index=True)
    watch_count = Column(Integer, default=1)
    last_watched = Column(DateTime, default=datetime.utcnow)


class TradeLog(Base):
    """Optional personal trade logging"""
    __tablename__ = 'trade_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), index=True)
    ticker = Column(String(10), index=True)
    entry_date = Column(DateTime)
    entry_price = Column(Float)
    shares = Column(Integer)
    exit_date = Column(DateTime, nullable=True)
    exit_price = Column(Float, nullable=True)
    pnl = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Database:
    """Database interface"""
    
    def __init__(self):
        """Initialize database connection"""
        database_url = os.getenv('DATABASE_URL')
        
        if not database_url:
            # Default to SQLite for local development
            database_url = 'sqlite:///swarm.db'
            logging.warning('Using SQLite database for development')
        
        # Fix Railway PostgreSQL URL format
        if database_url and database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        self.engine = create_engine(database_url, echo=False)
        Base.metadata.create_all(self.engine)
        
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        logging.info('Database initialized successfully')
    
    def save_alert(self, ticker, score, score_data, alert_type):
        """Save new alert to database"""
        try:
            alert = Alert(
                ticker=ticker,
                score=score,
                sec_score=score_data.get('sec_score', 0),
                technical_score=score_data.get('technical_score', 0),
                financial_score=score_data.get('financial_score', 0),
                news_score=score_data.get('news_score', 0),
                alert_type=alert_type,
                score_data=score_data
            )
            
            self.session.add(alert)
            self.session.commit()
            
            # Update ticker metadata
            self.update_ticker_metadata(ticker, score)
            
            logging.info(f'Saved alert for {ticker} (score: {score})')
            
        except Exception as e:
            self.session.rollback()
            logging.error(f'Error saving alert: {e}')
    
    def get_recent_alerts(self, ticker, hours=4):
        """Get recent alerts for a ticker"""
        try:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            alerts = self.session.query(Alert)\
                .filter(Alert.ticker == ticker)\
                .filter(Alert.created_at >= cutoff)\
                .order_by(Alert.created_at.desc())\
                .all()
            
            return [a.to_dict() for a in alerts]
            
        except Exception as e:
            logging.error(f'Error getting recent alerts: {e}')
            return []
    
    def get_todays_alerts(self, min_score=0):
        """Get today's alerts"""
        try:
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            
            alerts = self.session.query(Alert)\
                .filter(Alert.created_at >= today)\
                .filter(Alert.score >= min_score)\
                .order_by(Alert.score.desc())\
                .all()
            
            return [a.to_dict() for a in alerts]
            
        except Exception as e:
            logging.error(f'Error getting today\'s alerts: {e}')
            return []
    
    def get_ticker_history(self, ticker, days=30):
        """Get historical scores for a ticker"""
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)
            
            alerts = self.session.query(Alert)\
                .filter(Alert.ticker == ticker)\
                .filter(Alert.created_at >= cutoff)\
                .order_by(Alert.created_at.desc())\
                .all()
            
            return [a.to_dict() for a in alerts]
            
        except Exception as e:
            logging.error(f'Error getting ticker history: {e}')
            return []
    
    def update_ticker_metadata(self, ticker, score):
        """Update ticker metadata after new alert"""
        try:
            ticker_obj = self.session.query(Ticker)\
                .filter(Ticker.ticker == ticker)\
                .first()
            
            if not ticker_obj:
                ticker_obj = Ticker(ticker=ticker)
                self.session.add(ticker_obj)
            
            ticker_obj.last_score = score
            ticker_obj.alert_count += 1
            ticker_obj.last_alert = datetime.utcnow()
            
            # Calculate average score
            all_alerts = self.session.query(Alert)\
                .filter(Alert.ticker == ticker)\
                .all()
            
            if all_alerts:
                ticker_obj.avg_score = sum(a.score for a in all_alerts) / len(all_alerts)
            
            self.session.commit()
            
        except Exception as e:
            self.session.rollback()
            logging.error(f'Error updating ticker metadata: {e}')
    
    def add_to_watchlist(self, user_id, ticker):
        """Add ticker to user's watchlist"""
        try:
            # Check if already exists
            exists = self.session.query(Watchlist)\
                .filter(Watchlist.user_id == str(user_id))\
                .filter(Watchlist.ticker == ticker)\
                .first()
            
            if exists:
                logging.info(f'{ticker} already in watchlist for user {user_id}')
                return
            
            watch = Watchlist(user_id=str(user_id), ticker=ticker)
            self.session.add(watch)
            self.session.commit()
            
            # Update community watch count
            self.increment_community_watch(ticker)
            
            logging.info(f'Added {ticker} to watchlist for user {user_id}')
            
        except Exception as e:
            self.session.rollback()
            logging.error(f'Error adding to watchlist: {e}')
            raise
    
    def increment_community_watch(self, ticker):
        """Increment community watch count (anonymous)"""
        try:
            watch = self.session.query(CommunityWatch)\
                .filter(CommunityWatch.ticker == ticker)\
                .first()
            
            if watch:
                watch.watch_count += 1
                watch.last_watched = datetime.utcnow()
            else:
                watch = CommunityWatch(ticker=ticker, watch_count=1)
                self.session.add(watch)
            
            self.session.commit()
            
        except Exception as e:
            self.session.rollback()
            logging.error(f'Error updating community watch: {e}')
    
    def get_community_trending(self, limit=10):
        """Get most-watched tickers by community"""
        try:
            # Get tickers watched in last 7 days
            cutoff = datetime.utcnow() - timedelta(days=7)
            
            trending = self.session.query(CommunityWatch)\
                .filter(CommunityWatch.last_watched >= cutoff)\
                .order_by(CommunityWatch.watch_count.desc())\
                .limit(limit)\
                .all()
            
            return [(t.ticker, t.watch_count) for t in trending]
            
        except Exception as e:
            logging.error(f'Error getting community trending: {e}')
            return []
    
    def log_trade_entry(self, user_id, ticker, price, shares, notes=None):
        """Log trade entry"""
        try:
            trade = TradeLog(
                user_id=str(user_id),
                ticker=ticker,
                entry_date=datetime.utcnow(),
                entry_price=price,
                shares=shares,
                notes=notes
            )
            
            self.session.add(trade)
            self.session.commit()
            
            logging.info(f'Logged trade entry for {ticker} by user {user_id}')
            return trade.id
            
        except Exception as e:
            self.session.rollback()
            logging.error(f'Error logging trade entry: {e}')
            raise
    
    def log_trade_exit(self, trade_id, price):
        """Log trade exit"""
        try:
            trade = self.session.query(TradeLog)\
                .filter(TradeLog.id == trade_id)\
                .first()
            
            if not trade:
                raise ValueError(f'Trade {trade_id} not found')
            
            trade.exit_date = datetime.utcnow()
            trade.exit_price = price
            trade.pnl = (price - trade.entry_price) * trade.shares
            
            self.session.commit()
            
            logging.info(f'Logged trade exit for trade {trade_id}')
            
        except Exception as e:
            self.session.rollback()
            logging.error(f'Error logging trade exit: {e}')
            raise
    
    def get_user_stats(self, user_id):
        """Get user's trading statistics"""
        try:
            trades = self.session.query(TradeLog)\
                .filter(TradeLog.user_id == str(user_id))\
                .filter(TradeLog.exit_price.isnot(None))\
                .all()
            
            if not trades:
                return None
            
            total_trades = len(trades)
            winners = [t for t in trades if t.pnl > 0]
            losers = [t for t in trades if t.pnl <= 0]
            
            total_pnl = sum(t.pnl for t in trades)
            avg_win = sum(t.pnl for t in winners) / len(winners) if winners else 0
            avg_loss = sum(t.pnl for t in losers) / len(losers) if losers else 0
            
            return {
                'total_trades': total_trades,
                'winners': len(winners),
                'losers': len(losers),
                'win_rate': len(winners) / total_trades * 100,
                'total_pnl': total_pnl,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
            }
            
        except Exception as e:
            logging.error(f'Error getting user stats: {e}')
            return None


if __name__ == "__main__":
    # Test database
    db = Database()
    print("✅ Database initialized successfully")
    
    # Test saving alert
    db.save_alert('TEST', 85, {
        'sec_score': 30,
        'technical_score': 28,
        'financial_score': 15,
        'news_score': 7
    }, 'test')
    
    print("✅ Alert saved successfully")
