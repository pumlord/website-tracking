# Website Tracker

A Python-based website monitoring system that tracks changes on specified websites and sends email notifications when changes are detected.

## Features

- **Website Change Detection**: Monitors multiple websites for content changes using MD5 hash comparison
- **Discord Notifications**: Sends rich Discord notifications via webhook when changes are detected (default)
- **Email Notifications**: Alternative email alerts support
- **Flexible Monitoring**: Supports both single checks and continuous monitoring
- **Easy URL Management**: Add, remove, and list tracked URLs via command line
- **Persistent Storage**: Stores website data and configuration in JSON files
- **Detailed Logging**: Comprehensive logging to file and console
- **Respectful Crawling**: Includes delays between requests and proper user agent headers

## Installation

### Local Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/pumlord/website-tracking.git
   cd website-tracking
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Discord webhook**:
   ```bash
   cp config.template.json config.json
   # Edit config.json and replace YOUR_DISCORD_WEBHOOK_URL_HERE with your actual webhook URL
   ```

### GitHub Actions Hosting (Automated)

This repository includes GitHub Actions for automated website tracking:

1. **Fork this repository** to your GitHub account
2. **Set up Discord webhook secret**:
   - Go to your repository Settings → Secrets and variables → Actions
   - Add a new secret named `DISCORD_WEBHOOK_URL`
   - Set the value to your Discord webhook URL
3. **Enable GitHub Actions** in your repository
4. The tracker will automatically run every hour and send Discord notifications

The GitHub Actions workflow will:
- ✅ Run every hour automatically
- ✅ Check all configured websites for changes
- ✅ Send Discord notifications when changes are detected
- ✅ Store tracking data in the repository
- ✅ No server costs - completely free hosting

## Configuration

### Discord Setup (Recommended)

1. **Create a Discord Webhook**:
   - Go to your Discord server
   - Right-click on the channel where you want notifications
   - Select "Edit Channel" → "Integrations" → "Create Webhook"
   - Copy the Webhook URL

2. **Edit `config.json`** and update the Discord webhook:
   ```json
   {
       "notification": {
           "type": "discord",
           "discord_webhook_url": "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL_HERE"
       }
   }
   ```

### Email Setup (Alternative)

1. **Edit `config.json`** and change notification type to email:
   ```json
   {
       "notification": {
           "type": "email",
           "email": {
               "smtp_server": "smtp.gmail.com",
               "smtp_port": 587,
               "sender_email": "your-email@gmail.com",
               "sender_password": "your-app-password",
               "recipient_email": "suretester00@gmail.com"
           }
       }
   }
   ```

2. **For Gmail users**:
   - Enable 2-factor authentication on your Google account
   - Generate an App Password: Go to Google Account Settings → Security → App passwords
   - Use the generated app password (not your regular password) in the config

### Other Settings

- `check_interval`: Time between checks in seconds (default: 3600 = 1 hour)
- `request_timeout`: HTTP request timeout in seconds (default: 30)
- `user_agent`: User agent string for web requests

## Usage

### Adding URLs to Track

```bash
# Add single URL
python main.py --add-url https://example.com

# Add multiple URLs
python main.py --add-url https://example.com https://another-site.com https://news.site.com
```

### Running Checks

```bash
# Run a single check of all tracked websites
python main.py --check

# Start continuous monitoring (runs until stopped with Ctrl+C)
python main.py --monitor
```

### Managing URLs

```bash
# List all tracked URLs with status
python main.py --list-urls

# Remove URLs from tracking
python main.py --remove-url https://example.com

# Show detailed status
python main.py --status
```

### Example Workflow

1. **Add websites to track**:
   ```bash
   python main.py --add-url https://example.com https://news.site.com
   ```

2. **Run initial check** (this establishes baseline):
   ```bash
   python main.py --check
   ```

3. **Start continuous monitoring**:
   ```bash
   python main.py --monitor
   ```

## How It Works

1. **First Run**: When a URL is first checked, the system stores a hash of the website content as a baseline
2. **Subsequent Checks**: The system fetches the website content and compares its hash with the stored baseline
3. **Change Detection**: If the hash differs, a change is detected
4. **Notification**: An email is sent to `suretester00@gmail.com` with details of which websites changed
5. **Data Storage**: All tracking data is stored in `website_data.json` for persistence

## Files Created

- `config.json`: Configuration settings
- `website_data.json`: Stored website hashes and tracking data
- `website_tracker.log`: Log file with detailed operation history

## Email Notification Format

When changes are detected, you'll receive an email with:
- Subject: "Website Changes Detected - X site(s) updated"
- List of changed websites with timestamps
- Total count of changed sites
- Check timestamp

## Troubleshooting

### Common Issues

1. **Email not sending**:
   - Verify email credentials in `config.json`
   - For Gmail, ensure you're using an App Password, not your regular password
   - Check that 2FA is enabled on your Google account

2. **Website not accessible**:
   - Some websites may block automated requests
   - Check the logs in `website_tracker.log` for specific error messages
   - The system will continue checking other URLs even if some fail

3. **False positives**:
   - Some websites have dynamic content (timestamps, ads) that change frequently
   - Consider the nature of the website when interpreting change notifications

### Logs

Check `website_tracker.log` for detailed information about:
- Successful checks
- Error messages
- Email sending status
- Change detection details

## Advanced Usage

### Custom Configuration File

```bash
python main.py --config my-config.json --check
```

### Scheduling with Cron (Linux/Mac)

Add to crontab to run every hour:
```bash
0 * * * * cd /path/to/website-tracker && python main.py --check
```

### Scheduling with Task Scheduler (Windows)

Create a scheduled task that runs:
```
python C:\path\to\website-tracker\main.py --check
```

## Security Notes

- Store email passwords securely
- Consider using environment variables for sensitive data
- The system stores website content hashes, not the actual content
- Log files may contain URLs and timestamps

## License

This project is provided as-is for personal use.
