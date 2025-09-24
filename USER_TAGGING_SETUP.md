# 🏷️ Discord User Tagging Setup Guide

## Overview
The website tracker now supports **Discord user tagging** for change notifications. Users will be mentioned (pinged) when actual website changes are detected, but **NOT** for heartbeat messages.

## 🎯 When Users Get Tagged
- ✅ **Website content changes** - You get pinged immediately
- ✅ **Meta information changes** - You get pinged for title/description updates  
- ✅ **Both meta and content changes** - You get pinged for major updates
- ❌ **Heartbeat messages** - No ping (just "all systems running normally")

## 🔧 Setup Instructions

### Step 1: Get Your Discord User ID
1. **Enable Developer Mode** in Discord:
   - Go to Discord Settings → Advanced → Enable "Developer Mode"

2. **Get Your User ID**:
   - Right-click on your username in any Discord server
   - Click "Copy User ID"
   - You'll get something like: `123456789012345678`

### Step 2: Update Configuration
Edit your `config.json` file and add your user ID(s) to the notification section:

```json
{
    "notification": {
        "type": "discord",
        "discord_webhook_url": "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL",
        "discord_user_mentions": [
            "123456789012345678",
            "987654321098765432"
        ]
    }
}
```

### Step 3: Multiple Users (Optional)
You can tag multiple users by adding more user IDs to the array:

```json
"discord_user_mentions": [
    "123456789012345678",  // User 1
    "987654321098765432",  // User 2  
    "555666777888999000"   // User 3
]
```

## 📱 What You'll See

### 🚨 Change Notifications (WITH user tags)
```
🚨 **2 website(s) changed!** <@123456789012345678> <@987654321098765432>

📄 Website 1 - Page content changed
URL: https://example.com/live-blackjack
Type: Page content changed
Details: Page content changed (meta unchanged)

📸 Content Changes:
📏 Content size: 1,110 → 1,303 bytes (+193)
🎯 Promotional content changed:
   Current: ['Welcome Bonus: $750']
   Previous: ['Welcome Bonus: $500']
```

### 💙 Heartbeat Messages (NO user tags)
```
💙 **Heartbeat** - All systems running normally

✅ Website Tracker Heartbeat
Monitoring 11 websites - No changes detected
📊 Status: All systems operational
```

## 🛡️ Security Notes
- **User IDs are safe to share** - they're public identifiers
- **Keep webhook URLs private** - these should remain secret
- **Test with one user first** - make sure tagging works before adding multiple users

## 🧪 Testing
To test the user tagging:
1. Add your user ID to the config
2. Wait for the next scheduled run with changes
3. Or manually trigger a test (if you have changes to detect)

## ❓ Troubleshooting

### User Not Getting Tagged?
- ✅ Check user ID is correct (18-digit number)
- ✅ Ensure user is in the same server as the webhook
- ✅ Verify the webhook has permission to mention users
- ✅ Check the user ID is in quotes in the JSON config

### Getting Tagged for Heartbeats?
- ❌ This shouldn't happen - heartbeats don't include user mentions
- 🔧 If it does, there may be a configuration issue

## 🎉 Benefits
- **Instant notifications** for real changes
- **No spam** from heartbeat messages  
- **Multiple user support** for team monitoring
- **Clear distinction** between changes and status updates

---

**Ready to get pinged when your websites change? Add your Discord user ID to the config and you're all set!** 🚀
