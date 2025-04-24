import string
import sqlite3
from datetime import datetime, timedelta

def base62_encode(num):
    chars = string.digits + string.ascii_letters
    base = len(chars)
    result = []
    while num > 0:
        num, rem = divmod(num, base)
        result.append(chars[rem])
    return ''.join(reversed(result)) or '0'

class URLShortener:
    def __init__(self):
        # Create in-memory SQLite database
        self.conn = sqlite3.connect(':memory:', check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        # Create URLs table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short_url TEXT UNIQUE,
                long_url TEXT,
                expiry_time TIMESTAMP
            )
        ''')
        self.conn.commit()
        self.count = 0
    
    def encode(self, url):
        self.count += 1
        return base62_encode(self.count)
        
    def shorten(self, url):
        # Check if URL already exists
        self.cursor.execute('SELECT short_url FROM urls WHERE long_url = ?', (url,))
        result = self.cursor.fetchone()
        
        if result:
            return result[0]
            
        # Generate new short URL
        encoded = self.encode(url)
        
        # Store in database
        expiry_time = datetime.now() + timedelta(seconds=20)
        self.cursor.execute(
            'INSERT INTO urls (short_url, long_url, expiry_time) VALUES (?, ?, ?)',
            (encoded, url, expiry_time)
        )
        self.conn.commit()
        return encoded
            
    def redirect(self, short_url):
        # Get URL and check expiry
        self.cursor.execute(
            'SELECT long_url, expiry_time FROM urls WHERE short_url = ?',
            (short_url,)
        )
        result = self.cursor.fetchone()
        
        if result:
            long_url, expiry_time = result
            if datetime.now() < datetime.fromisoformat(expiry_time):
                return long_url
            else:
                # Delete expired URL
                self.cursor.execute('DELETE FROM urls WHERE short_url = ?', (short_url,))
                self.conn.commit()
        return None
    
    def __del__(self):
        # Close database connection
        if hasattr(self, 'conn'):
            self.conn.close()