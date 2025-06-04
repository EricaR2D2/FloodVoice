#!/usr/bin/env python3
"""
Setup script to initialize the Public Health MVP authentication system
and create an initial admin user.
"""

import sys
import getpass
from models import init_user_db, create_admin_user, User

def main():
    print("🔧 Public Health MVP - Authentication Setup")
    print("=" * 50)
    
    # Initialize database
    print("\n1. Initializing user database...")
    if not init_user_db():
        print("❌ Failed to initialize database. Exiting.")
        sys.exit(1)
    
    # Check if admin user already exists
    existing_admin = User.get_by_username("admin")
    if existing_admin:
        print("\n⚠️  Admin user already exists!")
        choice = input("Do you want to create a new admin user with a different username? (y/n): ").lower()
        if choice != 'y':
            print("Setup cancelled.")
            sys.exit(0)
    
    # Get admin credentials
    print("\n2. Creating admin user...")
    
    while True:
        username = input("Enter admin username (default: admin): ").strip()
        if not username:
            username = "admin"
        
        if len(username) < 3:
            print("❌ Username must be at least 3 characters long.")
            continue
        
        # Check if username already exists
        if User.get_by_username(username):
            print(f"❌ Username '{username}' already exists. Please choose a different one.")
            continue
        
        break
    
    while True:
        password = getpass.getpass("Enter admin password (minimum 6 characters): ")
        if len(password) < 6:
            print("❌ Password must be at least 6 characters long.")
            continue
        
        confirm_password = getpass.getpass("Confirm admin password: ")
        if password != confirm_password:
            print("❌ Passwords do not match. Please try again.")
            continue
        
        break
    
    # Create admin user
    if create_admin_user(username, password):
        print(f"\n✅ Admin user '{username}' created successfully!")
        print("\n🎉 Authentication system setup complete!")
        print("\nYou can now:")
        print(f"  • Start the application: python app.py")
        print(f"  • Login at: http://localhost:5000/login")
        print(f"  • Username: {username}")
        print(f"  • Password: [the password you just set]")
        print("\n⚠️  Important: Keep your admin credentials secure!")
    else:
        print(f"\n❌ Failed to create admin user '{username}'.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        sys.exit(1)
