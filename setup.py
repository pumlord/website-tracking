#!/usr/bin/env python3
"""
Setup script for Website Tracker

This script helps you set up the website tracker with initial configuration.
"""

import json
import os
import sys

def setup_email_config():
    """Interactive setup for email configuration."""
    print("=== Email Configuration Setup ===")
    print("The tracker will send notifications to: suretester00@gmail.com")
    print("You need to configure the sender email credentials.\n")
    
    sender_email = input("Enter your sender email address: ").strip()
    if not sender_email:
        print("Email address is required!")
        return None
    
    print(f"\nFor Gmail users:")
    print("1. Enable 2-factor authentication on your Google account")
    print("2. Go to Google Account Settings → Security → App passwords")
    print("3. Generate an App Password for this application")
    print("4. Use the generated app password (not your regular password)\n")
    
    sender_password = input("Enter your email password (or app password for Gmail): ").strip()
    if not sender_password:
        print("Password is required!")
        return None
    
    # Ask about SMTP settings
    print(f"\nSMTP Settings:")
    print("For Gmail, the default settings (smtp.gmail.com:587) should work.")
    use_default = input("Use default Gmail SMTP settings? (y/n): ").strip().lower()
    
    if use_default == 'y':
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
    else:
        smtp_server = input("Enter SMTP server: ").strip()
        smtp_port = int(input("Enter SMTP port: ").strip())
    
    return {
        "sender_email": sender_email,
        "sender_password": sender_password,
        "smtp_server": smtp_server,
        "smtp_port": smtp_port
    }

def setup_tracking_config():
    """Setup tracking configuration."""
    print("\n=== Tracking Configuration ===")
    
    # Check interval
    print("How often should the tracker check for changes?")
    print("1. Every 30 minutes (1800 seconds)")
    print("2. Every hour (3600 seconds) - Recommended")
    print("3. Every 6 hours (21600 seconds)")
    print("4. Every 24 hours (86400 seconds)")
    print("5. Custom interval")
    
    choice = input("Choose option (1-5): ").strip()
    
    intervals = {
        '1': 1800,
        '2': 3600,
        '3': 21600,
        '4': 86400
    }
    
    if choice in intervals:
        check_interval = intervals[choice]
    elif choice == '5':
        check_interval = int(input("Enter custom interval in seconds: ").strip())
    else:
        print("Invalid choice, using default (1 hour)")
        check_interval = 3600
    
    return {
        "check_interval": check_interval,
        "request_timeout": 30,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

def create_config_file():
    """Create the configuration file."""
    print("Website Tracker Setup")
    print("=" * 50)
    
    # Check if config already exists
    if os.path.exists('config.json'):
        overwrite = input("config.json already exists. Overwrite? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            return False
    
    # Get email configuration
    email_config = setup_email_config()
    if not email_config:
        print("Setup failed: Email configuration required.")
        return False
    
    # Get tracking configuration
    tracking_config = setup_tracking_config()
    
    # Create full configuration
    config = {
        "urls": [],
        "email": {
            "smtp_server": email_config["smtp_server"],
            "smtp_port": email_config["smtp_port"],
            "sender_email": email_config["sender_email"],
            "sender_password": email_config["sender_password"],
            "recipient_email": "suretester00@gmail.com"
        },
        "check_interval": tracking_config["check_interval"],
        "request_timeout": tracking_config["request_timeout"],
        "user_agent": tracking_config["user_agent"]
    }
    
    # Save configuration
    try:
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
        print(f"\n✓ Configuration saved to config.json")
        return True
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return False

def add_initial_urls():
    """Add initial URLs to track."""
    print(f"\n=== Add Initial URLs ===")
    print("You can add URLs to track now, or do it later using:")
    print("python main.py --add-url <url1> <url2> ...")
    
    add_now = input("\nAdd URLs now? (y/n): ").strip().lower()
    if add_now != 'y':
        return
    
    urls = []
    print("\nEnter URLs to track (press Enter with empty line to finish):")
    
    while True:
        url = input("URL: ").strip()
        if not url:
            break
        if url.startswith('http://') or url.startswith('https://'):
            urls.append(url)
            print(f"  Added: {url}")
        else:
            print("  Please enter a valid URL starting with http:// or https://")
    
    if urls:
        # Load and update config
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
            
            config['urls'] = urls
            
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)
            
            print(f"\n✓ Added {len(urls)} URLs to tracking list")
        except Exception as e:
            print(f"Error updating URLs: {e}")

def main():
    """Main setup function."""
    print("Website Tracker Setup Script")
    print("This will help you configure the website tracker.\n")
    
    # Create config file
    if not create_config_file():
        sys.exit(1)
    
    # Add initial URLs
    add_initial_urls()
    
    # Show next steps
    print(f"\n" + "=" * 50)
    print("Setup Complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Test the setup: python main.py --check")
    print("3. Add more URLs: python main.py --add-url <url>")
    print("4. Start monitoring: python main.py --monitor")
    print("\nFor help: python main.py --help")
    print("For status: python main.py --status")

if __name__ == "__main__":
    main()
