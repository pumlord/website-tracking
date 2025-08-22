import requests
import hashlib
import json
import os
import time
from datetime import datetime
from typing import List, Dict, Optional
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('website_tracker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WebsiteTracker:
    def __init__(self, config_file: str = 'config.json'):
        """
        Initialize the website tracker.
        
        Args:
            config_file: Path to the configuration file
        """
        self.config_file = config_file
        self.data_file = 'website_data.json'
        self.config = self.load_config()
        self.website_data = self.load_website_data()
        
    def load_config(self) -> Dict:
        """Load configuration from file."""
        default_config = {
            "urls": [],
            "notification": {
                "type": "discord",  # "discord" or "email"
                "discord_webhook_url": "",
                "email": {
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "sender_email": "",
                    "sender_password": "",
                    "recipient_email": "suretester00@gmail.com"
                }
            },
            "check_interval": 3600,  # 1 hour in seconds
            "request_timeout": 30,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                return default_config
        else:
            # Create default config file
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
            logger.info(f"Created default config file: {self.config_file}")
            return default_config
    
    def load_website_data(self) -> Dict:
        """Load stored website data from file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading website data: {e}")
                return {}
        return {}
    
    def save_website_data(self):
        """Save website data to file."""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.website_data, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving website data: {e}")
    
    def get_website_content(self, url: str) -> Optional[str]:
        """
        Fetch website content.
        
        Args:
            url: The URL to fetch
            
        Returns:
            The website content as string, or None if failed
        """
        try:
            headers = {
                'User-Agent': self.config.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            }
            
            response = requests.get(
                url, 
                headers=headers,
                timeout=self.config.get('request_timeout', 30)
            )
            response.raise_for_status()
            return response.text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def calculate_content_hash(self, content: str) -> str:
        """Calculate MD5 hash of content."""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def check_website_changes(self, url: str) -> bool:
        """
        Check if a website has changed.
        
        Args:
            url: The URL to check
            
        Returns:
            True if changed, False otherwise
        """
        logger.info(f"Checking {url}")
        
        content = self.get_website_content(url)
        if content is None:
            logger.warning(f"Could not fetch content for {url}")
            return False
        
        current_hash = self.calculate_content_hash(content)
        
        if url not in self.website_data:
            # First time checking this URL
            self.website_data[url] = {
                'hash': current_hash,
                'last_checked': datetime.now().isoformat(),
                'last_changed': datetime.now().isoformat()
            }
            logger.info(f"First time tracking {url}")
            return False
        
        stored_hash = self.website_data[url]['hash']
        self.website_data[url]['last_checked'] = datetime.now().isoformat()
        
        if current_hash != stored_hash:
            # Content has changed
            self.website_data[url]['hash'] = current_hash
            self.website_data[url]['last_changed'] = datetime.now().isoformat()
            logger.info(f"Change detected for {url}")
            return True
        
        logger.info(f"No changes detected for {url}")
        return False
    
    def send_discord_notification(self, changed_urls: List[str]):
        """
        Send Discord notification about changed websites.

        Args:
            changed_urls: List of URLs that have changed
        """
        try:
            webhook_url = self.config['notification'].get('discord_webhook_url')

            if not webhook_url:
                logger.error("Discord webhook URL not configured")
                return

            # Create Discord embed
            embed = {
                "title": f"🔔 Website Changes Detected",
                "description": f"**{len(changed_urls)} website(s) have been updated**",
                "color": 0x00ff00,  # Green color
                "timestamp": datetime.now().isoformat(),
                "fields": [],
                "footer": {
                    "text": "Website Tracker Bot"
                }
            }

            # Add changed URLs as fields
            for i, url in enumerate(changed_urls[:10]):  # Limit to 10 URLs to avoid Discord limits
                last_changed = self.website_data[url].get('last_changed', 'Unknown')
                embed["fields"].append({
                    "name": f"🌐 Website {i+1}",
                    "value": f"**URL:** {url}\n**Changed:** {last_changed}",
                    "inline": False
                })

            if len(changed_urls) > 10:
                embed["fields"].append({
                    "name": "📝 Note",
                    "value": f"... and {len(changed_urls) - 10} more websites",
                    "inline": False
                })

            # Prepare Discord webhook payload
            payload = {
                "embeds": [embed]
            }

            # Send to Discord
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()

            logger.info(f"Discord notification sent for {len(changed_urls)} changed websites")

        except Exception as e:
            logger.error(f"Error sending Discord notification: {e}")

    def send_email_notification(self, changed_urls: List[str]):
        """
        Send email notification about changed websites.

        Args:
            changed_urls: List of URLs that have changed
        """
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            email_config = self.config['notification']['email']

            if not email_config.get('sender_email') or not email_config.get('sender_password'):
                logger.error("Email credentials not configured")
                return

            # Create message
            msg = MIMEMultipart()
            msg['From'] = email_config['sender_email']
            msg['To'] = email_config['recipient_email']
            msg['Subject'] = f"Website Changes Detected - {len(changed_urls)} site(s) updated"

            # Create email body
            body = f"""
Website Change Notification

The following websites have been updated:

"""
            for url in changed_urls:
                last_changed = self.website_data[url].get('last_changed', 'Unknown')
                body += f"• {url}\n  Last changed: {last_changed}\n\n"

            body += f"""
Total websites changed: {len(changed_urls)}
Check time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is an automated message from your Website Tracker.
"""

            msg.attach(MIMEText(body, 'plain'))

            # Send email
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['sender_email'], email_config['sender_password'])
            text = msg.as_string()
            server.sendmail(email_config['sender_email'], email_config['recipient_email'], text)
            server.quit()

            logger.info(f"Email notification sent for {len(changed_urls)} changed websites")

        except Exception as e:
            logger.error(f"Error sending email notification: {e}")

    def send_notification(self, changed_urls: List[str]):
        """
        Send notification about changed websites using configured method.

        Args:
            changed_urls: List of URLs that have changed
        """
        notification_type = self.config['notification'].get('type', 'discord')

        if notification_type == 'discord':
            self.send_discord_notification(changed_urls)
        elif notification_type == 'email':
            self.send_email_notification(changed_urls)
        else:
            logger.error(f"Unknown notification type: {notification_type}")
    
    def track_websites(self) -> List[str]:
        """
        Track all configured websites for changes.
        
        Returns:
            List of URLs that have changed
        """
        changed_urls = []
        urls = self.config.get('urls', [])
        
        if not urls:
            logger.warning("No URLs configured for tracking")
            return changed_urls
        
        logger.info(f"Starting to track {len(urls)} websites")
        
        for url in urls:
            try:
                if self.check_website_changes(url):
                    changed_urls.append(url)
                # Small delay between requests to be respectful
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error checking {url}: {e}")
        
        # Save updated data
        self.save_website_data()
        
        # Send notification if changes detected
        if changed_urls:
            self.send_notification(changed_urls)
            logger.info(f"Tracking complete. {len(changed_urls)} websites changed.")
        else:
            logger.info("Tracking complete. No changes detected.")
        
        return changed_urls
    
    def add_url(self, url: str):
        """Add a URL to the tracking list."""
        if 'urls' not in self.config:
            self.config['urls'] = []
        
        if url not in self.config['urls']:
            self.config['urls'].append(url)
            self.save_config()
            logger.info(f"Added URL to tracking: {url}")
        else:
            logger.info(f"URL already being tracked: {url}")
    
    def remove_url(self, url: str):
        """Remove a URL from the tracking list."""
        if 'urls' in self.config and url in self.config['urls']:
            self.config['urls'].remove(url)
            self.save_config()
            # Also remove from stored data
            if url in self.website_data:
                del self.website_data[url]
                self.save_website_data()
            logger.info(f"Removed URL from tracking: {url}")
        else:
            logger.info(f"URL not found in tracking list: {url}")
    
    def save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def get_status(self) -> Dict:
        """Get current tracking status."""
        return {
            'total_urls': len(self.config.get('urls', [])),
            'tracked_urls': list(self.config.get('urls', [])),
            'last_check_times': {url: data.get('last_checked') for url, data in self.website_data.items()},
            'last_change_times': {url: data.get('last_changed') for url, data in self.website_data.items()}
        }
