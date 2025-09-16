#!/usr/bin/env python3
"""
Test the new Discord webhook URL directly
"""

import requests
import json
from datetime import datetime

def test_new_webhook_direct():
    """Test the new webhook URL directly."""
    
    # Your new webhook URL
    webhook_url = "https://discord.com/api/webhooks/1408374244592848968/gmYz2IoRgFGNBH5tBbWx5kW3PPC4tHvlLdYqiLz1z8-gXDEfHcu1v0qbe-_Rbu2_oJlw"
    
    print("🧪 Testing New Discord Webhook")
    print("="*40)
    print(f"Webhook URL: {webhook_url[:50]}...")
    
    # Test 1: Simple message
    print("\n1. 📤 Testing simple message...")
    try:
        simple_payload = {
            "content": "🧪 **Test Message 1** - Simple text message"
        }
        
        response = requests.post(
            webhook_url, 
            json=simple_payload, 
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 204:
            print("   ✅ Simple message sent successfully!")
        else:
            print(f"   ❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Embed message
    print("\n2. 📤 Testing embed message...")
    try:
        embed_payload = {
            "content": "🧪 **Test Message 2** - Embed test",
            "embeds": [{
                "title": "🔧 Webhook Test",
                "description": "Testing Discord webhook with embed",
                "color": 0xff9900,  # Orange
                "timestamp": datetime.now().isoformat(),
                "fields": [
                    {
                        "name": "🌐 Webhook ID",
                        "value": "1408374244592848968",
                        "inline": True
                    },
                    {
                        "name": "⏰ Test Time",
                        "value": datetime.now().strftime('%H:%M:%S'),
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "Direct Webhook Test"
                }
            }]
        }
        
        response = requests.post(
            webhook_url, 
            json=embed_payload, 
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 204:
            print("   ✅ Embed message sent successfully!")
        else:
            print(f"   ❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Website tracker style message
    print("\n3. 📤 Testing website tracker style message...")
    try:
        tracker_payload = {
            "content": "💙 **Heartbeat Test** - Website Tracker Style",
            "embeds": [{
                "title": "✅ Website Tracker Test",
                "description": "**Testing website tracker notification style**",
                "color": 0x0099ff,  # Blue
                "timestamp": datetime.now().isoformat(),
                "fields": [
                    {
                        "name": "📊 Status",
                        "value": "Testing new webhook URL",
                        "inline": True
                    },
                    {
                        "name": "🌐 Websites",
                        "value": "10 configured",
                        "inline": True
                    },
                    {
                        "name": "🔧 Test Type",
                        "value": "Direct webhook test",
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "Website Tracker Bot • Test"
                }
            }]
        }
        
        response = requests.post(
            webhook_url, 
            json=tracker_payload, 
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 204:
            print("   ✅ Tracker style message sent successfully!")
        else:
            print(f"   ❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "="*40)
    print("🎯 Test Complete!")
    print("Check your Discord channel for 3 test messages:")
    print("1. 🧪 Simple text message")
    print("2. 🟠 Orange embed message") 
    print("3. 🔵 Blue website tracker style message")

def test_with_website_tracker():
    """Test using the WebsiteTracker class."""
    print("\n🏗️ Testing with WebsiteTracker class...")
    
    try:
        from website_tracker import WebsiteTracker
        
        tracker = WebsiteTracker()
        print("   ✅ WebsiteTracker loaded")
        
        # Test heartbeat
        print("   📤 Sending heartbeat notification...")
        result = tracker.send_heartbeat_notification()
        
        if result:
            print("   ✅ Heartbeat sent successfully!")
        else:
            print("   ❌ Heartbeat failed")
            
        # Test change notification (fake)
        print("   📤 Sending fake change notification...")
        fake_urls = ["https://example.com/test"]
        result = tracker.send_discord_notification(fake_urls)
        
        if result:
            print("   ✅ Change notification sent successfully!")
        else:
            print("   ❌ Change notification failed")
            
    except Exception as e:
        print(f"   ❌ WebsiteTracker test failed: {e}")

if __name__ == "__main__":
    print("🔧 New Discord Webhook Test Suite")
    print("This will test your new webhook URL directly")
    print("="*50)
    
    # Test direct webhook
    test_new_webhook_direct()
    
    # Test with tracker class
    test_with_website_tracker()
    
    print("\n🎉 All tests complete!")
    print("📱 Check your Discord channel for test messages")
    print("🔍 If you don't see messages, check:")
    print("   • Discord server permissions")
    print("   • Webhook channel settings")
    print("   • Internet connection")
