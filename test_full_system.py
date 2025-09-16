#!/usr/bin/env python3
"""
Comprehensive test script to debug the entire notification system
"""

import json
import os
import sys
import requests
from datetime import datetime
from website_tracker import WebsiteTracker

def test_config_loading():
    """Test if configuration loads correctly."""
    print("🔧 Testing Configuration Loading...")
    
    try:
        if not os.path.exists('config.json'):
            print("   ❌ config.json not found!")
            return False
            
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        print("   ✅ config.json loaded successfully")
        
        # Check required fields
        if 'notification' not in config:
            print("   ❌ 'notification' section missing from config")
            return False
            
        if 'discord_webhook_url' not in config['notification']:
            print("   ❌ 'discord_webhook_url' missing from config")
            return False
            
        webhook_url = config['notification']['discord_webhook_url']
        if not webhook_url or webhook_url == "YOUR_DISCORD_WEBHOOK_URL_HERE":
            print("   ❌ Discord webhook URL not configured properly")
            print(f"   Current value: {webhook_url}")
            return False
            
        print(f"   ✅ Discord webhook URL configured")
        print(f"   📊 URLs to track: {len(config.get('urls', []))}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error loading config: {e}")
        return False

def test_discord_webhook_direct():
    """Test Discord webhook directly without using the tracker class."""
    print("\n🌐 Testing Discord Webhook Directly...")
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        webhook_url = config['notification']['discord_webhook_url']
        
        # Create test payload
        embed = {
            "title": "🧪 Direct Webhook Test",
            "description": "Testing Discord webhook directly",
            "color": 0xff9900,  # Orange color
            "timestamp": datetime.now().isoformat(),
            "fields": [
                {
                    "name": "🔧 Test Type",
                    "value": "Direct webhook test (bypassing tracker class)",
                    "inline": False
                },
                {
                    "name": "⏰ Timestamp",
                    "value": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "inline": False
                }
            ],
            "footer": {
                "text": "Direct Webhook Test"
            }
        }
        
        payload = {
            "content": "🧪 **Direct Webhook Test**",
            "embeds": [embed]
        }
        
        print("   📤 Sending test message to Discord...")
        response = requests.post(webhook_url, json=payload, timeout=10)
        
        print(f"   📊 Response status: {response.status_code}")
        
        if response.status_code == 204:
            print("   ✅ Direct webhook test successful!")
            print("   📱 Check your Discord channel for the orange test message")
            return True
        else:
            print(f"   ❌ Webhook failed with status {response.status_code}")
            print(f"   📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Direct webhook test failed: {e}")
        return False

def test_tracker_class():
    """Test the WebsiteTracker class initialization."""
    print("\n🏗️ Testing WebsiteTracker Class...")
    
    try:
        tracker = WebsiteTracker()
        print("   ✅ WebsiteTracker initialized successfully")
        
        # Test heartbeat notification
        print("   📤 Testing heartbeat notification...")
        tracker.send_heartbeat_notification()
        print("   ✅ Heartbeat notification sent!")
        print("   📱 Check your Discord channel for the blue heartbeat message")
        
        return True
        
    except Exception as e:
        print(f"   ❌ WebsiteTracker test failed: {e}")
        return False

def test_full_tracking_run():
    """Test a full tracking run."""
    print("\n🔍 Testing Full Tracking Run...")
    
    try:
        tracker = WebsiteTracker()
        
        print("   🚀 Running full website check...")
        changed_urls = tracker.track_websites()
        
        print(f"   📊 Results:")
        print(f"      URLs checked: {len(tracker.config.get('urls', []))}")
        print(f"      Changes detected: {len(changed_urls)}")
        
        if changed_urls:
            print("   🔔 Changes detected - notification should have been sent!")
            for url in changed_urls:
                print(f"      • {url}")
        else:
            print("   ℹ️ No changes detected")
            print("   📤 Testing heartbeat notification for no-change scenario...")
            tracker.send_heartbeat_notification()
            print("   ✅ Heartbeat sent for no-change scenario")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Full tracking test failed: {e}")
        return False

def simulate_github_actions():
    """Simulate what GitHub Actions does."""
    print("\n🤖 Simulating GitHub Actions Workflow...")
    
    try:
        # Step 1: Check if we have the template
        if not os.path.exists('config.template.json'):
            print("   ❌ config.template.json not found!")
            return False
        
        print("   ✅ config.template.json found")
        
        # Step 2: Simulate config creation (like GitHub Actions does)
        print("   🔧 Simulating config creation from template...")
        
        with open('config.template.json', 'r') as f:
            config = json.load(f)
        
        # Simulate replacing the webhook URL (like GitHub Actions does)
        webhook_url = "https://discord.com/api/webhooks/1408374257729409054/jEBqVBOIe3imVPCxzeX-lViyvp-DhTEKDSAhfdHPMasb5aygmWgRURUuvbHmpHj1pQvV"
        config['notification']['discord_webhook_url'] = webhook_url
        
        # Save temporary config
        with open('config_test.json', 'w') as f:
            json.dump(config, f, indent=4)
        
        print("   ✅ Test config created")
        
        # Step 3: Test with the simulated config
        print("   🧪 Testing with simulated GitHub Actions config...")
        
        # Temporarily rename files
        if os.path.exists('config.json'):
            os.rename('config.json', 'config_backup.json')
        os.rename('config_test.json', 'config.json')
        
        try:
            # Test the tracker with simulated config
            tracker = WebsiteTracker()
            print("   📤 Sending test heartbeat with simulated config...")
            tracker.send_heartbeat_notification()
            print("   ✅ Simulated GitHub Actions test successful!")
            
        finally:
            # Restore original config
            os.rename('config.json', 'config_test.json')
            if os.path.exists('config_backup.json'):
                os.rename('config_backup.json', 'config.json')
            os.remove('config_test.json')
        
        return True
        
    except Exception as e:
        print(f"   ❌ GitHub Actions simulation failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=== Website Tracker Debug Suite ===")
    print("This will test all components of the notification system\n")
    
    tests = [
        ("Configuration Loading", test_config_loading),
        ("Direct Discord Webhook", test_discord_webhook_direct),
        ("WebsiteTracker Class", test_tracker_class),
        ("Full Tracking Run", test_full_tracking_run),
        ("GitHub Actions Simulation", simulate_github_actions)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"   ❌ {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*50)
    print("🎯 TEST RESULTS SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your notification system should be working.")
        print("📱 Check your Discord channel for test messages.")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
        
    print("\n🔍 Next steps:")
    print("1. Check your Discord channel for test messages")
    print("2. If tests pass but GitHub Actions fails, check the Actions tab")
    print("3. Verify DISCORD_WEBHOOK_URL secret is set in GitHub")

if __name__ == "__main__":
    main()
