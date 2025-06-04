"""
User model and database utilities for Public Health MVP authentication system.
"""

import sqlite3
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

DATABASE_PATH = 'public_health_data.db'

class User(UserMixin):
    """User model for authentication."""
    
    def __init__(self, id, username, password_hash, created_at=None, last_login=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.created_at = created_at
        self.last_login = last_login
    
    def set_password(self, password):
        """Set password hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash."""
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def get(user_id):
        """Get user by ID."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, username, password_hash, created_at, last_login 
                FROM users WHERE id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            if row:
                return User(
                    id=row[0],
                    username=row[1],
                    password_hash=row[2],
                    created_at=row[3],
                    last_login=row[4]
                )
            return None
            
        finally:
            conn.close()
    
    @staticmethod
    def get_by_username(username):
        """Get user by username."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, username, password_hash, created_at, last_login 
                FROM users WHERE username = ?
            """, (username,))
            
            row = cursor.fetchone()
            if row:
                return User(
                    id=row[0],
                    username=row[1],
                    password_hash=row[2],
                    created_at=row[3],
                    last_login=row[4]
                )
            return None
            
        finally:
            conn.close()
    
    def save(self):
        """Save user to database."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        try:
            if self.id:
                # Update existing user
                cursor.execute("""
                    UPDATE users 
                    SET username = ?, password_hash = ?, last_login = ?
                    WHERE id = ?
                """, (self.username, self.password_hash, self.last_login, self.id))
            else:
                # Create new user
                cursor.execute("""
                    INSERT INTO users (username, password_hash, created_at)
                    VALUES (?, ?, ?)
                """, (self.username, self.password_hash, datetime.now().isoformat()))
                
                self.id = cursor.lastrowid
            
            conn.commit()
            return True
            
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def update_last_login(self):
        """Update last login timestamp."""
        self.last_login = datetime.now().isoformat()
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE users SET last_login = ? WHERE id = ?
            """, (self.last_login, self.id))
            conn.commit()
        finally:
            conn.close()

def init_user_db():
    """Initialize users table in database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_login TEXT
            )
        """)
        
        conn.commit()
        print("✅ Users table created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error creating users table: {e}")
        return False
    finally:
        conn.close()

def create_admin_user(username="admin", password="admin123"):
    """Create initial admin user."""
    # Check if admin user already exists
    existing_user = User.get_by_username(username)
    if existing_user:
        print(f"⚠️  User '{username}' already exists")
        return False
    
    # Create new admin user
    admin_user = User(
        id=None,
        username=username,
        password_hash=None,
        created_at=datetime.now().isoformat()
    )
    admin_user.set_password(password)
    
    if admin_user.save():
        print(f"✅ Admin user '{username}' created successfully")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print("   ⚠️  Please change the default password after first login!")
        return True
    else:
        print(f"❌ Failed to create admin user '{username}'")
        return False

if __name__ == "__main__":
    # Initialize database and create admin user
    print("🔧 Initializing user authentication system...")
    
    if init_user_db():
        create_admin_user()
        print("\n🎉 User authentication system initialized successfully!")
        print("   You can now log in to the application.")
    else:
        print("\n❌ Failed to initialize user authentication system.")
