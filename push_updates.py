#!/usr/bin/env python3
"""
Quick script to push updates to GitHub for collaborative debugging
"""

import subprocess
import sys

def run_command(command, description):
    """Run a command and print the result"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=".")
        if result.returncode == 0:
            print(f"✅ {description} successful!")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
        else:
            print(f"❌ {description} failed!")
            print(f"Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False
    return True

def main():
    print("🚀 PUSHING NYC PUBLIC HEALTH MVP TO GITHUB")
    print("=" * 50)
    
    # Check git status
    print("\n📋 Checking current status...")
    subprocess.run("git status", shell=True)
    
    # Add all changes
    if not run_command("git add .", "Adding all changes"):
        return
    
    # Commit changes
    commit_message = """Fix: Advanced dashboard authentication and map initialization

- Added @login_required decorators to all advanced dashboard routes  
- Fixed Leaflet map container double initialization error
- Improved JavaScript error handling in map functions
- Ready for collaborative debugging session with friend

Key fixes:
- Authentication now works on /advanced-dashboard
- Map initialization error resolved
- All API endpoints properly protected
- Database has 6.6M+ records ready for testing"""

    if not run_command(f'git commit -m "{commit_message}"', "Committing changes"):
        print("ℹ️ No new changes to commit, or commit failed")
    
    # Push to GitHub
    if not run_command("git push origin main", "Pushing to GitHub"):
        return
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! Your code is now on GitHub!")
    print("\n📍 SHARE THIS LINK WITH YOUR FRIEND:")
    print("🔗 https://github.com/EricaR2D2/PublicHealthMVP")
    print("\n📋 DEBUGGING INFO FOR YOUR FRIEND:")
    print("• Login: testuser / testpass123")
    print("• Server: python app.py (runs on localhost:5000)")
    print("• Issue: Advanced dashboard map loading")
    print("• Focus: Leaflet.js initialization and API calls")
    print("• Database: 6.6M+ records in public_health_data.db")

if __name__ == "__main__":
    main()
