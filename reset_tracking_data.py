#!/usr/bin/env python3
"""
Reset tracking data to start fresh with improved change detection
"""

import os
import json
from datetime import datetime

def reset_tracking_data():
    """Reset the tracking data file."""
    
    print("🔄 Resetting Website Tracking Data")
    print("="*40)
    
    # Check if tracking data exists
    if os.path.exists('website_data.json'):
        # Backup existing data
        backup_name = f"website_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open('website_data.json', 'r') as f:
                old_data = json.load(f)
            
            with open(backup_name, 'w') as f:
                json.dump(old_data, f, indent=4)
            
            print(f"✅ Backed up existing data to: {backup_name}")
            print(f"📊 Previous data contained {len(old_data)} websites")
            
            # Show what was in the old data
            for url, data in old_data.items():
                last_changed = data.get('last_changed', 'Unknown')
                check_count = data.get('check_count', 'Unknown')
                print(f"   • {url[:60]}...")
                print(f"     Last changed: {last_changed}")
                print(f"     Check count: {check_count}")
            
        except Exception as e:
            print(f"⚠️ Error backing up data: {e}")
    
    # Create fresh tracking data
    fresh_data = {}
    
    try:
        with open('website_data.json', 'w') as f:
            json.dump(fresh_data, f, indent=4)
        
        print(f"\n✅ Created fresh tracking data file")
        print(f"🔄 Next check will establish new baselines for all websites")
        
    except Exception as e:
        print(f"❌ Error creating fresh data: {e}")
        return False
    
    return True

def show_current_config():
    """Show current configuration."""
    
    print(f"\n📋 Current Configuration")
    print("="*40)
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        urls = config.get('urls', [])
        webhook_url = config['notification'].get('discord_webhook_url', '')
        
        print(f"🌐 URLs to track: {len(urls)}")
        for i, url in enumerate(urls, 1):
            print(f"   {i:2d}. {url}")
        
        print(f"\n🔔 Notification: Discord webhook")
        print(f"   Webhook ID: {webhook_url.split('/')[-2] if '/' in webhook_url else 'Unknown'}")
        
        print(f"\n⏰ Check interval: {config.get('check_interval', 3600)} seconds")
        
    except Exception as e:
        print(f"❌ Error reading config: {e}")

def main():
    """Main function."""
    
    print("🔧 Website Tracker Data Reset Tool")
    print("This will reset tracking data to fix false positive detections")
    print("="*60)
    
    # Show current config
    show_current_config()
    
    # Reset data
    success = reset_tracking_data()
    
    if success:
        print(f"\n🎯 Next Steps:")
        print(f"1. Run: python main.py --check --debug")
        print(f"   This will establish fresh baselines with improved change detection")
        print(f"2. Check the logs for 'First time tracking' messages")
        print(f"3. Wait for next hourly check to see if false positives are fixed")
        print(f"4. Monitor Discord for more accurate change notifications")
        
        print(f"\n🔧 Improvements Made:")
        print(f"• Content normalization to filter dynamic elements")
        print(f"• Better hash comparison logic")
        print(f"• Enhanced logging and debugging")
        print(f"• 'Never' instead of timestamp for first-time tracking")
        
    else:
        print(f"\n❌ Reset failed. Check the errors above.")

if __name__ == "__main__":
    main()
