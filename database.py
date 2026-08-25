import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
import os

class Database:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.init_db()
    
    def get_connection(self):
        """Get database connection"""
        if self.db_url.startswith('sqlite:///'):
            db_path = self.db_url.replace('sqlite:///', '')
            return sqlite3.connect(db_path)
        else:
            # PostgreSQL support
            import psycopg2
            return psycopg2.connect(self.db_url)
    
    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Campaigns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT NOT NULL,
                details TEXT,
                audience TEXT,
                style TEXT,
                color TEXT,
                dimension TEXT,
                image_url TEXT,
                copy_text TEXT,
                status TEXT DEFAULT 'created',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                campaign_id INTEGER,
                rating INTEGER,
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (campaign_id) REFERENCES campaigns (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id: int, username: str, first_name: str, last_name: str = None):
        """Add or update user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, username, first_name, last_name, last_active)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, username, first_name, last_name))
        
        conn.commit()
        conn.close()
    
    def save_campaign(self, user_id: int, name: str, details: str, audience: str,
                     style: str, color: str, dimension: str, image_url: str,
                     copy_text: str) -> int:
        """Save campaign to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO campaigns (user_id, name, details, audience, style, color, 
                                 dimension, image_url, copy_text, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, name, details, audience, style, color, 
              dimension, image_url, copy_text, 'generated'))
        
        campaign_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return campaign_id
    
    def get_user_campaigns(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get user's campaigns"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, style, color, dimension, status, created_at
            FROM campaigns
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        campaigns = []
        for row in rows:
            campaigns.append({
                'id': row[0],
                'name': row[1],
                'style': row[2],
                'color': row[3],
                'dimension': row[4],
                'status': row[5],
                'created_at': row[6]
            })
        
        return campaigns
    
    def save_feedback(self, user_id: int, campaign_id: int, rating: int, comment: str):
        """Save user feedback"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO feedback (user_id, campaign_id, rating, comment)
            VALUES (?, ?, ?, ?)
        ''', (user_id, campaign_id, rating, comment))
        
        conn.commit()
        conn.close()
