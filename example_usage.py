#!/usr/bin/env python3
"""
Example usage of the Website Tracker

This script demonstrates how to use the WebsiteTracker class programmatically.
"""

from website_tracker import WebsiteTracker
import time

def example_usage():
    """Demonstrate basic usage of the website tracker."""
    
    # Initialize the tracker
    print("Initializing Website Tracker...")
    tracker = WebsiteTracker()
    
    # Add some example URLs (you can replace these with your actual URLs)
    example_urls = [
        "https://httpbin.org/uuid",  # This URL returns different content each time
        "https://httpbin.org/json",  # This URL returns static content
    ]
    
    print(f"\nAdding {len(example_urls)} URLs to track...")
    for url in example_urls:
        tracker.add_url(url)
    
    # Show current status
    print("\nCurrent tracking status:")
    status = tracker.get_status()
    print(f"Total URLs: {status['total_urls']}")
    for url in status['tracked_urls']:
        print(f"  - {url}")
    
    # Run first check (establishes baseline)
    print("\nRunning initial check (establishes baseline)...")
    changed_urls = tracker.track_websites()
    print(f"Initial check complete. {len(changed_urls)} changes detected (expected: 0 for first run)")
    
    # Wait a moment and check again
    print("\nWaiting 5 seconds before second check...")
    time.sleep(5)
    
    print("Running second check...")
    changed_urls = tracker.track_websites()
    print(f"Second check complete. {len(changed_urls)} changes detected")
    
    if changed_urls:
        print("Changed URLs:")
        for url in changed_urls:
            print(f"  - {url}")
    
    # Show final status
    print("\nFinal status:")
    status = tracker.get_status()
    for url in status['tracked_urls']:
        last_checked = status['last_check_times'].get(url, 'Never')
        last_changed = status['last_change_times'].get(url, 'Never')
        print(f"  {url}")
        print(f"    Last checked: {last_checked}")
        print(f"    Last changed: {last_changed}")

def example_with_real_websites():
    """Example with real websites (commented out by default)."""
    
    # Uncomment and modify these URLs as needed
    real_urls = [
        # "https://news.ycombinator.com",
        # "https://www.reddit.com",
        # "https://github.com/trending",
    ]
    
    if not real_urls:
        print("No real URLs configured. Edit this function to add URLs you want to track.")
        return
    
    tracker = WebsiteTracker()
    
    for url in real_urls:
        tracker.add_url(url)
    
    print(f"Tracking {len(real_urls)} real websites...")
    changed_urls = tracker.track_websites()
    
    if changed_urls:
        print(f"Changes detected in {len(changed_urls)} websites!")
    else:
        print("No changes detected.")

if __name__ == "__main__":
    print("=== Website Tracker Example Usage ===\n")
    
    # Run the basic example
    example_usage()
    
    print("\n" + "="*50 + "\n")
    
    # Optionally run with real websites
    example_with_real_websites()
    
    print("\nExample complete!")
    print("\nTo use with your own URLs:")
    print("1. Edit config.json to add your email credentials")
    print("2. Use: python main.py --add-url <your-urls>")
    print("3. Use: python main.py --check")
