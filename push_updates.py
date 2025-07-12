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
    
    # Create and checkout bugfix branch if not already on it
    if not run_command("git checkout bugfix 2>/dev/null || git checkout -b bugfix", "Switching to bugfix branch"):
        return
    
    # Add all changes
    if not run_command("git add .", "Adding all changes"):
        return
    
    # Commit changes
    commit_message = """Polish: Demo readiness improvements for Wednesday presentation

- Added data freshness verification with visual indicators
- Improved loading state with overlay and animations
- Standardized error handling with custom error pages

These polish improvements enhance the demo experience without adding new features."""

    if not run_command(f'git commit -m "{commit_message}"', "Committing changes"):
        print("ℹ️ No new changes to commit, or commit failed")
    
    # Push to GitHub
    if not run_command("git push origin bugfix", "Pushing to GitHub bugfix branch"):
        return
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! Your code is now on GitHub!")
    print("\n📍 BRANCH INFORMATION:")
    print("🔗 Branch: bugfix")
    print("🔗 https://github.com/EricaR2D2/PublicHealthMVP/tree/bugfix")
    print("\n📋 NEXT STEPS:")
    print("• Create a pull request when ready to merge to main")
    print("• Share the bugfix branch link for review before the demo")
    print("• Keep main branch stable until after Wednesday's presentation")

if __name__ == "__main__":
    main()

