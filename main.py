#!/usr/bin/env python3
"""
Website Tracker - Main execution script

This script provides a command-line interface for the website tracking system.
It can run in different modes: single check, continuous monitoring, or management.
"""

import argparse
import time
import sys
from website_tracker import WebsiteTracker
import logging

logger = logging.getLogger(__name__)

def run_single_check(tracker: WebsiteTracker, send_heartbeat: bool = False):
    """Run a single check of all websites."""
    print("Running single website check...")
    changed_urls = tracker.track_websites()

    if changed_urls:
        print(f"\n✓ Changes detected in {len(changed_urls)} website(s):")
        for url in changed_urls:
            print(f"  - {url}")
        notification_type = tracker.config['notification'].get('type', 'discord')
        if notification_type == 'discord':
            print(f"\nDiscord notification sent via webhook")
        else:
            print(f"\nEmail notification sent to {tracker.config['notification']['email']['recipient_email']}")
    else:
        print("\n✓ No changes detected in any tracked websites.")

        # Send heartbeat notification if requested and no changes detected
        if send_heartbeat:
            print("Sending heartbeat notification...")
            tracker.send_heartbeat_notification()
            notification_type = tracker.config['notification'].get('type', 'discord')
            if notification_type == 'discord':
                print("✓ Discord heartbeat notification sent")
            else:
                print("✓ Email heartbeat notification sent")

    return len(changed_urls)

def run_continuous_monitoring(tracker: WebsiteTracker):
    """Run continuous monitoring with specified interval."""
    interval = tracker.config.get('check_interval', 3600)
    print(f"Starting continuous monitoring (checking every {interval} seconds)...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            print(f"\n--- Check started at {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
            changed_count = run_single_check(tracker)
            
            print(f"Next check in {interval} seconds...")
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user.")
        sys.exit(0)

def manage_urls(tracker: WebsiteTracker, args):
    """Manage the URL list."""
    if args.add_url:
        for url in args.add_url:
            tracker.add_url(url)
        print(f"Added {len(args.add_url)} URL(s) to tracking list.")
    
    if args.remove_url:
        for url in args.remove_url:
            tracker.remove_url(url)
        print(f"Removed {len(args.remove_url)} URL(s) from tracking list.")
    
    if args.list_urls:
        status = tracker.get_status()
        urls = status['tracked_urls']
        if urls:
            print(f"\nCurrently tracking {len(urls)} website(s):")
            for i, url in enumerate(urls, 1):
                last_checked = status['last_check_times'].get(url, 'Never')
                last_changed = status['last_change_times'].get(url, 'Never')
                print(f"  {i}. {url}")
                print(f"     Last checked: {last_checked}")
                print(f"     Last changed: {last_changed}")
        else:
            print("\nNo websites are currently being tracked.")
            print("Use --add-url to add websites to track.")

def show_status(tracker: WebsiteTracker):
    """Show current tracking status."""
    status = tracker.get_status()
    print(f"\n=== Website Tracker Status ===")
    print(f"Total URLs tracked: {status['total_urls']}")
    notification_type = tracker.config['notification'].get('type', 'discord')
    if notification_type == 'discord':
        print(f"Discord notifications enabled via webhook")
    else:
        print(f"Email notifications sent to: {tracker.config['notification']['email']['recipient_email']}")
    print(f"Check interval: {tracker.config.get('check_interval', 3600)} seconds")
    
    if status['tracked_urls']:
        print(f"\nTracked websites:")
        for url in status['tracked_urls']:
            last_checked = status['last_check_times'].get(url, 'Never')
            last_changed = status['last_change_times'].get(url, 'Never')
            print(f"  • {url}")
            print(f"    Last checked: {last_checked}")
            print(f"    Last changed: {last_changed}")
    else:
        print("\nNo websites are currently being tracked.")

def main():
    parser = argparse.ArgumentParser(
        description="Website Tracker - Monitor websites for changes and send email notifications",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --check                    # Run single check
  python main.py --check --heartbeat        # Run single check with heartbeat notification
  python main.py --monitor                  # Start continuous monitoring
  python main.py --add-url https://example.com https://test.com
  python main.py --list-urls                # Show tracked URLs
  python main.py --status                   # Show detailed status
  
Configuration:
  Edit config.json to set up email credentials and other settings.
        """
    )
    
    # Main actions
    parser.add_argument('--check', action='store_true',
                       help='Run a single check of all tracked websites')
    parser.add_argument('--monitor', action='store_true',
                       help='Start continuous monitoring (runs until stopped)')
    parser.add_argument('--heartbeat', action='store_true',
                       help='Send heartbeat notification along with check (useful for scheduled runs)')
    
    # URL management
    parser.add_argument('--add-url', nargs='+', metavar='URL',
                       help='Add one or more URLs to track')
    parser.add_argument('--remove-url', nargs='+', metavar='URL',
                       help='Remove one or more URLs from tracking')
    parser.add_argument('--list-urls', action='store_true',
                       help='List all currently tracked URLs')
    
    # Status and info
    parser.add_argument('--status', action='store_true',
                       help='Show detailed tracking status')
    
    # Configuration
    parser.add_argument('--config', default='config.json',
                       help='Path to configuration file (default: config.json)')
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    try:
        # Initialize tracker
        tracker = WebsiteTracker(args.config)
        
        # Execute requested action
        if args.check:
            run_single_check(tracker, send_heartbeat=args.heartbeat)
        
        elif args.monitor:
            run_continuous_monitoring(tracker)
        
        elif args.add_url or args.remove_url or args.list_urls:
            manage_urls(tracker, args)
        
        elif args.status:
            show_status(tracker)
        
        else:
            print("No action specified. Use --help for available options.")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
