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

        # Process grouped URLs for backward compatibility
        self._process_url_groups()

    def _process_url_groups(self):
        """Process website groups and create a flat URL list for backward compatibility."""
        if 'website_groups' in self.config:
            # New grouped format
            all_urls = []
            self.url_groups = {}

            for group_key, group_data in self.config['website_groups'].items():
                group_name = group_data.get('name', group_key)
                group_urls = group_data.get('urls', [])

                # Store group information
                self.url_groups[group_key] = {
                    'name': group_name,
                    'urls': group_urls
                }

                # Add to flat list for backward compatibility
                all_urls.extend(group_urls)

            # Set the flat URL list for existing code compatibility
            self.config['urls'] = all_urls
        else:
            # Legacy format - create a single default group
            urls = self.config.get('urls', [])
            self.url_groups = {
                'default': {
                    'name': 'Default Group',
                    'urls': urls
                }
            }

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
    
    def normalize_content(self, content: str) -> str:
        """
        Normalize content by removing dynamic elements that change frequently.
        Enhanced for gambling/promotional sites with additional dynamic content patterns.
        """
        import re

        # Remove common dynamic content patterns
        normalized = content

        # Remove timestamps (various formats) - Enhanced patterns
        normalized = re.sub(r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}[.\d]*[Z]?', '[TIMESTAMP]', normalized)
        normalized = re.sub(r'\d{1,2}/\d{1,2}/\d{4}', '[DATE]', normalized)
        normalized = re.sub(r'\d{1,2}-\d{1,2}-\d{4}', '[DATE]', normalized)
        normalized = re.sub(r'\d{1,2}\.\d{1,2}\.\d{4}', '[DATE]', normalized)

        # Remove time-only patterns (HH:MM:SS, HH:MM)
        normalized = re.sub(r'\b\d{1,2}:\d{2}(:\d{2})?\s*(AM|PM|am|pm)?\b', '[TIME]', normalized)

        # Remove Unix timestamps and epoch times
        normalized = re.sub(r'\b\d{10,13}\b', '[TIMESTAMP]', normalized)

        # Remove session IDs and tokens - Enhanced
        normalized = re.sub(r'sessionid=[a-zA-Z0-9]+', 'sessionid=[SESSION]', normalized)
        normalized = re.sub(r'token=[a-zA-Z0-9]+', 'token=[TOKEN]', normalized)
        normalized = re.sub(r'csrf[_-]?token["\']?\s*[:=]\s*["\']?[a-zA-Z0-9]+', 'csrf_token=[TOKEN]', normalized)
        normalized = re.sub(r'auth[_-]?token["\']?\s*[:=]\s*["\']?[a-zA-Z0-9]+', 'auth_token=[TOKEN]', normalized)

        # Remove cache busters and version numbers - Enhanced
        normalized = re.sub(r'[?&]v=\d+', '', normalized)
        normalized = re.sub(r'[?&]_=\d+', '', normalized)
        normalized = re.sub(r'[?&]t=\d+', '', normalized)
        normalized = re.sub(r'[?&]cb=\d+', '', normalized)
        normalized = re.sub(r'[?&]cache=\d+', '', normalized)
        normalized = re.sub(r'[?&]timestamp=\d+', '', normalized)

        # Remove random IDs and UUIDs - Enhanced
        normalized = re.sub(r'id="[a-zA-Z0-9-]{8,}"', 'id="[RANDOM_ID]"', normalized)
        normalized = re.sub(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', '[UUID]', normalized)
        normalized = re.sub(r'data-id="[a-zA-Z0-9-]+"', 'data-id="[DATA_ID]"', normalized)

        # Remove nonce values - Enhanced
        normalized = re.sub(r'nonce=["\']?[a-zA-Z0-9+/=]+["\']?', 'nonce="[NONCE]"', normalized)
        normalized = re.sub(r'data-nonce=["\']?[a-zA-Z0-9+/=]+["\']?', 'data-nonce="[NONCE]"', normalized)

        # Remove current time indicators - Enhanced
        normalized = re.sub(r'Last updated:?\s*[^<\n]+', 'Last updated: [TIME]', normalized, flags=re.IGNORECASE)
        normalized = re.sub(r'Generated at:?\s*[^<\n]+', 'Generated at: [TIME]', normalized, flags=re.IGNORECASE)
        normalized = re.sub(r'Current time:?\s*[^<\n]+', 'Current time: [TIME]', normalized, flags=re.IGNORECASE)

        # Gambling/Promotional site specific patterns
        # Remove live odds, jackpot amounts, player counts
        normalized = re.sub(r'\$[\d,]+\.?\d*', '$[AMOUNT]', normalized)  # Dollar amounts
        normalized = re.sub(r'RM\s*[\d,]+\.?\d*', 'RM[AMOUNT]', normalized)  # Malaysian Ringgit
        normalized = re.sub(r'€[\d,]+\.?\d*', '€[AMOUNT]', normalized)  # Euro amounts
        normalized = re.sub(r'£[\d,]+\.?\d*', '£[AMOUNT]', normalized)  # Pound amounts

        # Remove player/user counts
        normalized = re.sub(r'\b\d+\s*(players?|users?|online)\b', '[COUNT] players', normalized, flags=re.IGNORECASE)
        normalized = re.sub(r'\b(players?|users?|online):\s*\d+', 'players: [COUNT]', normalized, flags=re.IGNORECASE)

        # Remove live statistics and counters
        normalized = re.sub(r'\b\d+\s*(views?|clicks?|visits?)\b', '[COUNT] views', normalized, flags=re.IGNORECASE)

        # Remove promotional countdown timers
        normalized = re.sub(r'\b\d{1,2}[hms]\s*\d{0,2}[ms]?\s*\d{0,2}s?\b', '[COUNTDOWN]', normalized)

        # Remove JavaScript timestamps and random values
        normalized = re.sub(r'Date\.now\(\)', 'Date.now()', normalized)
        normalized = re.sub(r'Math\.random\(\)', 'Math.random()', normalized)

        # Remove analytics and tracking parameters
        normalized = re.sub(r'[?&]utm_[^&=]*=[^&]*', '', normalized)
        normalized = re.sub(r'[?&]ga_[^&=]*=[^&]*', '', normalized)
        normalized = re.sub(r'[?&]fbclid=[^&]*', '', normalized)

        # Additional aggressive patterns for gambling sites
        # Remove any numbers that might be dynamic counters, IDs, or amounts
        normalized = re.sub(r'\b\d{4,}\b', '[NUMBER]', normalized)  # Any 4+ digit numbers

        # Remove common gambling site dynamic elements
        normalized = re.sub(r'data-[a-zA-Z-]+=[\'""][^\'""]*[\'""]', 'data-attr="[DATA]"', normalized)
        normalized = re.sub(r'class=[\'""][^\'""]*[\'""]', 'class="[CLASS]"', normalized)
        normalized = re.sub(r'style=[\'""][^\'""]*[\'""]', 'style="[STYLE]"', normalized)

        # Remove script content that might contain dynamic data
        normalized = re.sub(r'<script[^>]*>.*?</script>', '<script>[SCRIPT]</script>', normalized, flags=re.DOTALL)

        # Remove any JSON-like data structures
        normalized = re.sub(r'\{[^{}]*\}', '{[JSON]}', normalized)

        # Remove query parameters entirely
        normalized = re.sub(r'\?[^"\s<>]*', '', normalized)

        # Remove hash fragments
        normalized = re.sub(r'#[^"\s<>]*', '', normalized)

        # Remove whitespace variations
        normalized = re.sub(r'\s+', ' ', normalized)
        normalized = normalized.strip()

        return normalized

    def extract_meta_info(self, content: str) -> dict:
        """Extract meta information (title, description) from HTML content."""
        from bs4 import BeautifulSoup

        try:
            soup = BeautifulSoup(content, 'html.parser')

            # Extract title
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else ""

            # Extract meta description
            meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
            if not meta_desc_tag:
                meta_desc_tag = soup.find('meta', attrs={'property': 'og:description'})
            description = meta_desc_tag.get('content', '').strip() if meta_desc_tag else ""

            # Extract meta keywords
            meta_keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
            keywords = meta_keywords_tag.get('content', '').strip() if meta_keywords_tag else ""

            return {
                'title': title,
                'description': description,
                'keywords': keywords
            }
        except Exception as e:
            logger.warning(f"Error extracting meta info: {e}")
            return {'title': '', 'description': '', 'keywords': ''}

    def calculate_content_hash(self, content: str) -> str:
        """Calculate MD5 hash of normalized content."""
        normalized_content = self.normalize_content(content)
        return hashlib.md5(normalized_content.encode('utf-8')).hexdigest()

    def calculate_meta_hash(self, meta_info: dict) -> str:
        """Calculate MD5 hash of meta information."""
        meta_string = f"{meta_info['title']}|{meta_info['description']}|{meta_info['keywords']}"
        return hashlib.md5(meta_string.encode('utf-8')).hexdigest()

    def get_content_diff_sample(self, old_content: str, new_content: str, max_chars: int = 500) -> str:
        """
        Get a sample of what changed between old and new content for debugging.
        """
        import difflib

        # Normalize both contents
        old_normalized = self.normalize_content(old_content)
        new_normalized = self.normalize_content(new_content)

        # If normalized content is the same, show raw difference sample
        if old_normalized == new_normalized:
            return "Content identical after normalization (false positive detected)"

        # Get a diff sample
        old_lines = old_normalized.split('\n')[:20]  # First 20 lines
        new_lines = new_normalized.split('\n')[:20]  # First 20 lines

        diff = list(difflib.unified_diff(old_lines, new_lines, lineterm='', n=2))
        diff_text = '\n'.join(diff[:15])  # First 15 diff lines

        if len(diff_text) > max_chars:
            diff_text = diff_text[:max_chars] + "..."

        return diff_text if diff_text else "No significant differences found"

    def create_content_snapshot(self, content: str, url: str, snapshot_type: str = "current") -> dict:
        """
        Create a snapshot of content for before/after comparison.

        Args:
            content: The HTML content to snapshot
            url: The URL this content is from
            snapshot_type: Type of snapshot ("before" or "after")

        Returns:
            Dict with snapshot information
        """
        from bs4 import BeautifulSoup
        import re

        try:
            soup = BeautifulSoup(content, 'html.parser')

            # Extract key content sections
            snapshot = {
                'type': snapshot_type,
                'timestamp': datetime.now().isoformat(),
                'url': url,
                'content_length': len(content),
                'sections': {}
            }

            # Extract main content areas
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main', re.I))
            if main_content:
                snapshot['sections']['main_content'] = main_content.get_text(strip=True)[:1000]

            # Extract headings
            headings = []
            for tag in ['h1', 'h2', 'h3']:
                for heading in soup.find_all(tag):
                    headings.append(f"{tag.upper()}: {heading.get_text(strip=True)}")
            snapshot['sections']['headings'] = headings[:10]  # First 10 headings

            # Extract key text content (paragraphs)
            paragraphs = []
            for p in soup.find_all('p')[:5]:  # First 5 paragraphs
                text = p.get_text(strip=True)
                if len(text) > 20:  # Only meaningful paragraphs
                    paragraphs.append(text[:200])  # First 200 chars
            snapshot['sections']['paragraphs'] = paragraphs

            # Extract any promotional/dynamic content
            promo_selectors = [
                'div[class*="promo"]', 'div[class*="offer"]', 'div[class*="bonus"]',
                'div[class*="jackpot"]', 'div[class*="amount"]', 'span[class*="price"]'
            ]
            promo_content = []
            for selector in promo_selectors:
                elements = soup.select(selector)
                for elem in elements[:3]:  # Max 3 per selector
                    text = elem.get_text(strip=True)
                    if text and len(text) > 5:
                        promo_content.append(text[:100])
            snapshot['sections']['promotional'] = promo_content

            # Extract navigation/menu items
            nav_items = []
            nav = soup.find('nav') or soup.find('ul', class_=re.compile(r'menu|nav', re.I))
            if nav:
                for link in nav.find_all('a')[:10]:  # First 10 nav items
                    text = link.get_text(strip=True)
                    if text:
                        nav_items.append(text)
            snapshot['sections']['navigation'] = nav_items

            return snapshot

        except Exception as e:
            logger.warning(f"Error creating content snapshot: {e}")
            return {
                'type': snapshot_type,
                'timestamp': datetime.now().isoformat(),
                'url': url,
                'content_length': len(content),
                'error': str(e),
                'sections': {}
            }

    def compare_content_snapshots(self, before_snapshot: dict, after_snapshot: dict) -> str:
        """
        Compare two content snapshots and return a detailed diff report.

        Args:
            before_snapshot: Snapshot taken before the change
            after_snapshot: Snapshot taken after the change

        Returns:
            Formatted string describing the differences
        """
        if not before_snapshot or not after_snapshot:
            return "Unable to compare snapshots - missing data"

        changes = []

        # Compare content length
        before_len = before_snapshot.get('content_length', 0)
        after_len = after_snapshot.get('content_length', 0)
        if before_len != after_len:
            changes.append(f"📏 Content size: {before_len:,} → {after_len:,} bytes ({after_len-before_len:+,})")

        # Compare sections
        before_sections = before_snapshot.get('sections', {})
        after_sections = after_snapshot.get('sections', {})

        # Compare headings
        before_headings = before_sections.get('headings', [])
        after_headings = after_sections.get('headings', [])
        if before_headings != after_headings:
            changes.append("📋 Headings changed:")
            # Show added/removed headings
            added = set(after_headings) - set(before_headings)
            removed = set(before_headings) - set(after_headings)
            if added:
                changes.append(f"   ➕ Added: {list(added)[:3]}")
            if removed:
                changes.append(f"   ➖ Removed: {list(removed)[:3]}")

        # Compare main content
        before_main = before_sections.get('main_content', '')
        after_main = after_sections.get('main_content', '')
        if before_main != after_main:
            changes.append("📄 Main content changed:")
            if len(before_main) > 0 and len(after_main) > 0:
                # Show a snippet of the change
                changes.append(f"   Before: {before_main[:100]}...")
                changes.append(f"   After:  {after_main[:100]}...")
            elif len(after_main) > len(before_main):
                changes.append(f"   ➕ Content added: {after_main[:100]}...")
            else:
                changes.append(f"   ➖ Content removed: {before_main[:100]}...")

        # Compare promotional content
        before_promo = before_sections.get('promotional', [])
        after_promo = after_sections.get('promotional', [])
        if before_promo != after_promo:
            changes.append("🎯 Promotional content changed:")
            if after_promo:
                changes.append(f"   Current: {after_promo[:2]}")
            if before_promo:
                changes.append(f"   Previous: {before_promo[:2]}")

        # Compare paragraphs
        before_paras = before_sections.get('paragraphs', [])
        after_paras = after_sections.get('paragraphs', [])
        if len(before_paras) != len(after_paras):
            changes.append(f"📝 Paragraph count: {len(before_paras)} → {len(after_paras)}")

        return '\n'.join(changes) if changes else "No significant structural changes detected"

    def _get_meta_change_details(self, old_meta: dict, new_meta: dict) -> str:
        """Get detailed information about what meta information changed."""
        changes = []

        if old_meta.get('title', '') != new_meta.get('title', ''):
            changes.append(f"Title: '{old_meta.get('title', '')[:50]}...' → '{new_meta.get('title', '')[:50]}...'")

        if old_meta.get('description', '') != new_meta.get('description', ''):
            old_desc = old_meta.get('description', '')[:100]
            new_desc = new_meta.get('description', '')[:100]
            changes.append(f"Description: '{old_desc}...' → '{new_desc}...'")

        if old_meta.get('keywords', '') != new_meta.get('keywords', ''):
            changes.append(f"Keywords: '{old_meta.get('keywords', '')[:50]}...' → '{new_meta.get('keywords', '')[:50]}...'")

        return "; ".join(changes) if changes else "Meta information changed"

    def _group_changes_by_website(self, changes: List[dict]) -> dict:
        """Group changes by website groups for better organization."""
        grouped = {}

        for change in changes:
            url = change['url']
            group_key = None
            group_name = "Unknown Group"

            # Find which group this URL belongs to
            for gkey, gdata in getattr(self, 'url_groups', {}).items():
                if url in gdata['urls']:
                    group_key = gkey
                    group_name = gdata['name']
                    break

            if not group_key:
                group_key = 'ungrouped'
                group_name = 'Ungrouped Sites'

            if group_key not in grouped:
                grouped[group_key] = {
                    'name': group_name,
                    'changes': []
                }

            grouped[group_key]['changes'].append(change)

        return grouped

    def check_website_changes(self, url: str) -> dict:
        """
        Check if a website has changed, distinguishing between meta and content changes.

        Args:
            url: The URL to check

        Returns:
            Dict with change information: {
                'changed': bool,
                'meta_changed': bool,
                'content_changed': bool,
                'change_type': str,
                'details': str
            }
        """
        logger.info(f"Checking {url}")

        content = self.get_website_content(url)
        if content is None:
            logger.warning(f"Could not fetch content for {url}")
            return {
                'changed': False,
                'meta_changed': False,
                'content_changed': False,
                'change_type': 'error',
                'details': 'Could not fetch content'
            }

        # Extract meta information and calculate hashes
        meta_info = self.extract_meta_info(content)
        current_content_hash = self.calculate_content_hash(content)
        current_meta_hash = self.calculate_meta_hash(meta_info)

        logger.debug(f"Current content hash for {url}: {current_content_hash}")
        logger.debug(f"Current meta hash for {url}: {current_meta_hash}")

        if url not in self.website_data:
            # First time checking this URL - establish baseline
            baseline_snapshot = self.create_content_snapshot(content, url, "baseline")
            self.website_data[url] = {
                'content_hash': current_content_hash,
                'meta_hash': current_meta_hash,
                'meta_info': meta_info,
                'last_checked': datetime.now().isoformat(),
                'last_changed': 'Never',
                'content_length': len(content),
                'check_count': 1,
                'last_content': content[:5000],  # Store first 5KB for comparison
                'last_snapshot': baseline_snapshot  # Store content snapshot
            }
            logger.info(f"First time tracking {url} - baseline established")
            logger.info(f"   Content hash: {current_content_hash[:8]}...")
            logger.info(f"   Meta hash: {current_meta_hash[:8]}...")
            logger.info(f"   Title: {meta_info['title'][:50]}...")
            return {
                'changed': False,
                'meta_changed': False,
                'content_changed': False,
                'change_type': 'first_time',
                'details': 'Baseline established'
            }

        # Get stored hashes
        stored_content_hash = self.website_data[url].get('content_hash', '')
        stored_meta_hash = self.website_data[url].get('meta_hash', '')
        stored_meta_info = self.website_data[url].get('meta_info', {})

        # Update tracking info
        self.website_data[url]['last_checked'] = datetime.now().isoformat()
        self.website_data[url]['check_count'] = self.website_data[url].get('check_count', 0) + 1
        self.website_data[url]['content_length'] = len(content)

        # Check for changes
        meta_changed = current_meta_hash != stored_meta_hash
        content_changed = current_content_hash != stored_content_hash
        any_changed = meta_changed or content_changed

        if any_changed:
            # Create current snapshot for comparison
            current_snapshot = self.create_content_snapshot(content, url, "after")
            before_snapshot = self.website_data[url].get('last_snapshot', {})

            # Update stored data
            self.website_data[url]['content_hash'] = current_content_hash
            self.website_data[url]['meta_hash'] = current_meta_hash
            self.website_data[url]['meta_info'] = meta_info
            self.website_data[url]['last_changed'] = datetime.now().isoformat()
            self.website_data[url]['last_content'] = content[:5000]
            self.website_data[url]['last_snapshot'] = current_snapshot

            # Determine change type and create detailed message
            if meta_changed and content_changed:
                change_type = "both_meta_and_content"
                details = "Both meta information and page content changed"
                # Add snapshot comparison for content changes
                if before_snapshot:
                    snapshot_diff = self.compare_content_snapshots(before_snapshot, current_snapshot)
                    details += f"\n\n📸 Content Changes:\n{snapshot_diff}"
            elif meta_changed:
                change_type = "meta_only"
                details = self._get_meta_change_details(stored_meta_info, meta_info)
            else:
                change_type = "content_only"
                details = "Page content changed (meta unchanged)"
                # Add detailed snapshot comparison for content-only changes
                if before_snapshot:
                    snapshot_diff = self.compare_content_snapshots(before_snapshot, current_snapshot)
                    details += f"\n\n📸 Content Changes:\n{snapshot_diff}"

            logger.info(f"✅ CHANGE detected for {url}")
            logger.info(f"   Change type: {change_type}")
            logger.info(f"   Meta changed: {meta_changed}")
            logger.info(f"   Content changed: {content_changed}")
            logger.info(f"   Details: {details}")

            # Get content diff if we have stored content (legacy diff for debugging)
            if content_changed and 'last_content' in self.website_data[url]:
                diff_sample = self.get_content_diff_sample(
                    self.website_data[url]['last_content'],
                    content
                )
                logger.info(f"   Content diff sample:\n{diff_sample}")

            return {
                'changed': True,
                'meta_changed': meta_changed,
                'content_changed': content_changed,
                'change_type': change_type,
                'details': details,
                'before_snapshot': before_snapshot,
                'after_snapshot': current_snapshot
            }

        logger.info(f"No changes detected for {url} (check #{self.website_data[url]['check_count']})")
        return {
            'changed': False,
            'meta_changed': False,
            'content_changed': False,
            'change_type': 'no_change',
            'details': f"No changes detected (check #{self.website_data[url]['check_count']})"
        }
    
    def send_discord_notification(self, changes: List[dict]):
        """
        Send Discord notification about changed websites.

        Args:
            changes: List of change dictionaries with URL and change details
        """
        try:
            webhook_url = self.config['notification'].get('discord_webhook_url')

            if not webhook_url or webhook_url == "YOUR_DISCORD_WEBHOOK_URL_HERE":
                logger.error("Discord webhook URL not configured properly")
                return False

            # Validate webhook URL format
            if not webhook_url.startswith('https://discord.com/api/webhooks/'):
                logger.error(f"Invalid Discord webhook URL format: {webhook_url[:50]}...")
                return False

            # Group changes by website groups
            grouped_changes = self._group_changes_by_website(changes)

            # Create Discord embed
            embed = {
                "title": f"🔔 Website Changes Detected",
                "description": f"**{len(changes)} website(s) have been updated across {len(grouped_changes)} group(s)**",
                "color": 0x00ff00,  # Green color
                "timestamp": datetime.now().isoformat(),
                "fields": [],
                "footer": {
                    "text": "Website Tracker Bot"
                }
            }

            # Add grouped changes as fields
            field_count = 0
            for group_key, group_data in grouped_changes.items():
                group_name = group_data['name']
                group_changes = group_data['changes']

                # Create a field for each group
                group_emoji = "🎯" if "lb33my" in group_key.lower() else "🎮" if "gamebet" in group_key.lower() else "🌐"

                # Create summary of changes in this group
                change_summaries = []
                for change in group_changes:
                    url = change['url']
                    change_info = change['change_info']

                    # Determine emoji based on change type
                    if change_info['change_type'] == 'meta_only':
                        emoji = "📝"
                    elif change_info['change_type'] == 'content_only':
                        emoji = "📄"
                    elif change_info['change_type'] == 'both_meta_and_content':
                        emoji = "🔄"
                    else:
                        emoji = "🌐"

                    # Shorten URL for display
                    display_url = url.replace('https://www.', '').replace('https://', '')
                    if len(display_url) > 60:
                        display_url = display_url[:57] + '...'

                    # Get key details
                    last_changed = self.website_data[url].get('last_changed', 'Unknown')
                    if isinstance(last_changed, str) and 'T' in last_changed:
                        # Format datetime string to be more readable
                        try:
                            from datetime import datetime
                            dt = datetime.fromisoformat(last_changed.replace('Z', '+00:00'))
                            last_changed = dt.strftime('%H:%M')
                        except:
                            last_changed = 'Now'

                    # Create concise summary
                    change_summaries.append(f"{emoji} **{display_url}** - {last_changed}")

                # Create field value with all changes in this group
                field_value = f"**{len(group_changes)} change(s) detected:**\n" + "\n".join(change_summaries)

                # Ensure field value doesn't exceed Discord limits (1024 chars)
                if len(field_value) > 1000:
                    # Truncate but show count
                    truncated_summaries = change_summaries[:3]  # Show first 3
                    remaining = len(change_summaries) - 3
                    field_value = f"**{len(group_changes)} change(s) detected:**\n" + "\n".join(truncated_summaries)
                    if remaining > 0:
                        field_value += f"\n... and {remaining} more changes"

                embed["fields"].append({
                    "name": f"{group_emoji} {group_name}",
                    "value": field_value,
                    "inline": False
                })

                field_count += 1

                # Discord has a limit of 25 fields per embed
                if field_count >= 25:
                    break

            # Prepare Discord webhook payload with user mentions for changes
            user_mentions = self.config['notification'].get('discord_user_mentions', [])
            mention_text = ""

            if user_mentions:
                # Create mention string for users
                mentions = [f"<@{user_id}>" for user_id in user_mentions if user_id and str(user_id).isdigit()]
                if mentions:
                    mention_text = " " + " ".join(mentions)

            payload = {
                "content": f"🚨 **{len(changes)} website(s) changed!**{mention_text}",
                "embeds": [embed]
            }

            # Send to Discord with timeout and better error handling
            logger.info(f"Sending Discord notification to webhook: {webhook_url[:50]}...")
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )

            logger.info(f"Discord API response: {response.status_code}")

            if response.status_code == 204:
                logger.info(f"✅ Discord notification sent successfully for {len(changes)} changed websites")
                return True
            else:
                logger.error(f"Discord API error: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.Timeout:
            logger.error("Discord notification timeout - webhook took too long to respond")
            return False
        except requests.exceptions.ConnectionError:
            logger.error("Discord notification connection error - check internet connection")
            return False
        except Exception as e:
            logger.error(f"Error sending Discord notification: {e}")
            return False

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

    def send_heartbeat_notification(self):
        """
        Send a heartbeat notification to confirm the tracker is running.
        """
        try:
            notification_type = self.config['notification'].get('type', 'discord')

            if notification_type == 'discord':
                self.send_discord_heartbeat()
            elif notification_type == 'email':
                self.send_email_heartbeat()
            else:
                logger.error(f"Unknown notification type: {notification_type}")

        except Exception as e:
            logger.error(f"Error sending heartbeat notification: {e}")

    def send_discord_heartbeat(self):
        """
        Send Discord heartbeat notification.
        """
        try:
            webhook_url = self.config['notification'].get('discord_webhook_url')

            if not webhook_url or webhook_url == "YOUR_DISCORD_WEBHOOK_URL_HERE":
                logger.error("Discord webhook URL not configured properly")
                return False

            # Validate webhook URL format
            if not webhook_url.startswith('https://discord.com/api/webhooks/'):
                logger.error(f"Invalid Discord webhook URL format: {webhook_url[:50]}...")
                return False

            # Create Discord embed for heartbeat with grouped information
            total_urls = len(self.config.get('urls', []))
            total_groups = len(getattr(self, 'url_groups', {}))

            embed = {
                "title": "✅ Website Tracker Heartbeat",
                "description": f"**Monitoring {total_urls} websites across {total_groups} group(s) - No changes detected**",
                "color": 0x0099ff,  # Blue color
                "timestamp": datetime.now().isoformat(),
                "fields": [
                    {
                        "name": "📊 Status",
                        "value": "All systems operational",
                        "inline": True
                    },
                    {
                        "name": "🌐 Total Websites",
                        "value": str(total_urls),
                        "inline": True
                    },
                    {
                        "name": "⏰ Next Check",
                        "value": "In 1 hour",
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "Website Tracker Bot • Heartbeat"
                }
            }

            # Add grouped website information
            if hasattr(self, 'url_groups') and self.url_groups:
                for group_key, group_data in self.url_groups.items():
                    group_name = group_data['name']
                    group_urls = group_data['urls']

                    # Create emoji for group
                    group_emoji = "🎯" if "lb33my" in group_key.lower() else "🎮" if "gamebet" in group_key.lower() else "🌐"

                    # Show sample URLs from this group
                    url_samples = []
                    for url in group_urls[:3]:  # Show first 3 URLs
                        display_url = url.replace('https://www.', '').replace('https://', '')
                        if len(display_url) > 45:
                            display_url = display_url[:42] + '...'
                        url_samples.append(f"• {display_url}")

                    if len(group_urls) > 3:
                        url_samples.append(f"• ... and {len(group_urls) - 3} more")

                    embed["fields"].append({
                        "name": f"{group_emoji} {group_name} ({len(group_urls)} sites)",
                        "value": "\n".join(url_samples),
                        "inline": False
                    })

            # Prepare Discord webhook payload
            payload = {
                "content": "💙 **Heartbeat** - All systems running normally",
                "embeds": [embed]
            }

            # Send to Discord with timeout and better error handling
            logger.info(f"Sending Discord heartbeat to webhook: {webhook_url[:50]}...")
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )

            logger.info(f"Discord heartbeat API response: {response.status_code}")

            if response.status_code == 204:
                logger.info("✅ Discord heartbeat notification sent successfully")
                return True
            else:
                logger.error(f"Discord heartbeat API error: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.Timeout:
            logger.error("Discord heartbeat timeout - webhook took too long to respond")
            return False
        except requests.exceptions.ConnectionError:
            logger.error("Discord heartbeat connection error - check internet connection")
            return False
        except Exception as e:
            logger.error(f"Error sending Discord heartbeat: {e}")
            return False

    def send_email_heartbeat(self):
        """
        Send email heartbeat notification.
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
            msg['Subject'] = "Website Tracker Heartbeat - System Running"

            # Create email body
            body = f"""
Website Tracker Heartbeat

✅ System Status: Operational
🌐 Websites Monitored: {len(self.config['urls'])}
⏰ Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📅 Next Check: In 1 hour

All systems are running normally. No changes detected in this check cycle.

This is an automated heartbeat message from your Website Tracker.
"""

            msg.attach(MIMEText(body, 'plain'))

            # Send email
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['sender_email'], email_config['sender_password'])
            text = msg.as_string()
            server.sendmail(email_config['sender_email'], email_config['recipient_email'], text)
            server.quit()

            logger.info("Email heartbeat notification sent")

        except Exception as e:
            logger.error(f"Error sending email heartbeat: {e}")

    def send_notification(self, changed_urls: List[str]):
        """
        Send notification about changed websites using configured method.

        Args:
            changed_urls: List of URLs that have changed
        """
        notification_type = self.config['notification'].get('type', 'discord')

        if notification_type == 'discord':
            # Convert to old format for backward compatibility
            changes = [{'url': url, 'change_info': {'change_type': 'unknown', 'details': 'Website changed'}} for url in changed_urls]
            self.send_discord_notification(changes)
        elif notification_type == 'email':
            self.send_email_notification(changed_urls)
        else:
            logger.error(f"Unknown notification type: {notification_type}")

    def send_notification_with_details(self, changes: List[dict]):
        """
        Send notification about changed websites with detailed change information.

        Args:
            changes: List of change dictionaries with URL and change details
        """
        notification_type = self.config['notification'].get('type', 'discord')

        if notification_type == 'discord':
            self.send_discord_notification(changes)
        elif notification_type == 'email':
            # Convert to old format for email notifications
            changed_urls = [change['url'] for change in changes]
            self.send_email_notification(changed_urls)
        else:
            logger.error(f"Unknown notification type: {notification_type}")
    
    def track_websites(self) -> List[str]:
        """
        Track all configured websites for changes.

        Returns:
            List of URLs that have changed
        """
        changes = []
        urls = self.config.get('urls', [])

        if not urls:
            logger.warning("No URLs configured for tracking")
            return []

        logger.info(f"Starting to track {len(urls)} websites")

        for url in urls:
            try:
                change_info = self.check_website_changes(url)
                if change_info['changed']:
                    changes.append({
                        'url': url,
                        'change_info': change_info
                    })
                # Small delay between requests to be respectful
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error checking {url}: {e}")

        # Save updated data
        self.save_website_data()

        # Send notification if changes detected
        if changes:
            self.send_notification_with_details(changes)
            logger.info(f"Tracking complete. {len(changes)} websites changed.")
        else:
            logger.info("Tracking complete. No changes detected.")

        # Return list of changed URLs for backward compatibility
        return [change['url'] for change in changes]
    
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
