#!/usr/bin/env python3
"""
Initial setup script for website tracking

This script will:
1. Test Discord notifications
2. Run initial baseline check for all URLs
3. Show tracking status
"""

import sys
import time
from website_tracker import WebsiteTracker

def main():
    print("=== Website Tracker Initial Setup ===")
    print("Setting up tracking for 10 websites...\n")
    
    try:
        # Initialize tracker
        tracker = WebsiteTracker()
        
        # Show configured URLs
        urls = tracker.config.get('urls', [])
        print(f"📋 Configured URLs ({len(urls)}):")
        for i, url in enumerate(urls, 1):
            print(f"  {i:2d}. {url}")
        
        print(f"\n🔔 Notifications will be sent to Discord via webhook")
        
        # Test Discord notification first
        print(f"\n🧪 Testing Discord notification...")
        test_urls = ["https://example.com/test"]  # Fake URL for testing
        try:
            tracker.send_discord_notification(test_urls)
            print("✅ Discord test notification sent successfully!")
            print("   Check your Discord channel for the test message.")
        except Exception as e:
            print(f"❌ Discord test failed: {e}")
            print("   Please check your webhook URL in config.json")
            return False
        
        # Wait a moment
        print(f"\n⏳ Waiting 3 seconds before starting baseline check...")
        time.sleep(3)
        
        # Run initial baseline check
        print(f"\n🔍 Running initial baseline check...")
        print("   This establishes the current state of each website.")
        print("   No notifications will be sent for this first check.\n")
        
        changed_urls = tracker.track_websites()
        
        # Show results
        print(f"\n📊 Initial Setup Results:")
        print(f"   Total URLs tracked: {len(urls)}")
        print(f"   Baseline established: ✅")
        print(f"   Changes detected: {len(changed_urls)} (expected: 0 for first run)")
        
        if changed_urls:
            print(f"   Note: Changes on first run usually indicate dynamic content")
        
        # Show status
        print(f"\n📈 Current Status:")
        status = tracker.get_status()
        for url in status['tracked_urls']:
            last_checked = status['last_check_times'].get(url, 'Never')
            print(f"   ✓ {url}")
            print(f"     Last checked: {last_checked}")
        
        print(f"\n🎉 Setup Complete!")
        print(f"   Your website tracker is now monitoring {len(urls)} websites.")
        print(f"   Future changes will trigger Discord notifications.")
        
        print(f"\n📋 Next Steps:")
        print(f"   • Test a change: python main.py --check")
        print(f"   • Start monitoring: python main.py --monitor")
        print(f"   • View status: python main.py --status")
        print(f"   • Add more URLs: python main.py --add-url <url>")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
