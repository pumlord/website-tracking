#!/usr/bin/env python3
"""
Test Discord notification functionality

This script tests if the Discord webhook is working correctly.
"""

import requests
import json
from datetime import datetime

def test_discord_webhook():
    """Test the Discord webhook with a sample notification."""
    
    # Load config
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return False
    
    webhook_url = config['notification'].get('discord_webhook_url')
    
    if not webhook_url or webhook_url == "YOUR_DISCORD_WEBHOOK_URL_HERE":
        print("Discord webhook URL not configured!")
        return False
    
    # Create test embed
    embed = {
        "title": "🧪 Website Tracker Test",
        "description": "**Testing Discord notifications**",
        "color": 0x00ff00,  # Green color
        "timestamp": datetime.now().isoformat(),
        "fields": [
            {
                "name": "✅ Status",
                "value": "Discord webhook is working correctly!",
                "inline": False
            },
            {
                "name": "🔧 Configuration",
                "value": f"Webhook URL configured\nNotification type: Discord",
                "inline": False
            }
        ],
        "footer": {
            "text": "Website Tracker Test - Setup Complete"
        }
    }
    
    # Prepare Discord webhook payload
    payload = {
        "content": "🎉 **Website Tracker Setup Complete!**",
        "embeds": [embed]
    }
    
    try:
        # Send to Discord
        print("Sending test notification to Discord...")
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        
        print("✅ Success! Discord notification sent successfully!")
        print("Check your Discord channel for the test message.")
        return True
        
    except Exception as e:
        print(f"❌ Error sending Discord notification: {e}")
        return False

if __name__ == "__main__":
    print("=== Discord Webhook Test ===")
    print("This will send a test message to your Discord channel.\n")
    
    success = test_discord_webhook()
    
    if success:
        print("\n🎉 Great! Your Discord notifications are working.")
        print("You can now add URLs to track and start monitoring!")
        print("\nNext steps:")
        print("1. Add URLs: python main.py --add-url <your-urls>")
        print("2. Run check: python main.py --check")
    else:
        print("\n❌ Discord test failed. Please check your webhook URL.")
