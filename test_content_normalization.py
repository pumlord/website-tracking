#!/usr/bin/env python3
"""
Test content normalization to verify it filters out dynamic content properly
"""

from website_tracker import WebsiteTracker
import hashlib

def test_normalization():
    """Test the content normalization function."""
    
    tracker = WebsiteTracker()
    
    # Test cases with dynamic content
    test_cases = [
        {
            "name": "Timestamps",
            "content1": '<div>Last updated: 2025-09-16T08:30:26.488011</div>',
            "content2": '<div>Last updated: 2025-09-16T09:11:19.520393</div>',
            "should_be_same": True
        },
        {
            "name": "Session IDs",
            "content1": '<script>sessionid=abc123def456</script>',
            "content2": '<script>sessionid=xyz789ghi012</script>',
            "should_be_same": True
        },
        {
            "name": "CSRF Tokens",
            "content1": '<input name="csrf_token" value="token123">',
            "content2": '<input name="csrf_token" value="token456">',
            "should_be_same": True
        },
        {
            "name": "Cache Busters",
            "content1": '<script src="app.js?v=123"></script>',
            "content2": '<script src="app.js?v=456"></script>',
            "should_be_same": True
        },
        {
            "name": "Real Content Change",
            "content1": '<h1>Welcome to our site</h1>',
            "content2": '<h1>Welcome to our NEW site</h1>',
            "should_be_same": False
        },
        {
            "name": "Whitespace Variations",
            "content1": '<div>   Hello    World   </div>',
            "content2": '<div>Hello World</div>',
            "should_be_same": True
        }
    ]
    
    print("🧪 Testing Content Normalization")
    print("="*50)
    
    passed = 0
    total = len(test_cases)
    
    for test in test_cases:
        print(f"\n📋 Test: {test['name']}")
        
        # Normalize both contents
        norm1 = tracker.normalize_content(test['content1'])
        norm2 = tracker.normalize_content(test['content2'])
        
        # Calculate hashes
        hash1 = hashlib.md5(norm1.encode('utf-8')).hexdigest()
        hash2 = hashlib.md5(norm2.encode('utf-8')).hexdigest()
        
        # Check if they're the same
        are_same = hash1 == hash2
        expected = test['should_be_same']
        
        print(f"   Original 1: {test['content1']}")
        print(f"   Original 2: {test['content2']}")
        print(f"   Normalized 1: {norm1}")
        print(f"   Normalized 2: {norm2}")
        print(f"   Hash 1: {hash1[:16]}...")
        print(f"   Hash 2: {hash2[:16]}...")
        print(f"   Same: {are_same}, Expected: {expected}")
        
        if are_same == expected:
            print(f"   ✅ PASS")
            passed += 1
        else:
            print(f"   ❌ FAIL")
    
    print(f"\n" + "="*50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All normalization tests passed!")
        return True
    else:
        print("⚠️ Some tests failed - normalization needs improvement")
        return False

def test_real_website():
    """Test with a real website to see content normalization in action."""
    
    print("\n🌐 Testing Real Website Content")
    print("="*50)
    
    tracker = WebsiteTracker()
    
    # Test with one of your URLs
    test_url = "https://www.business2communitymalaysia.com/en/gambling/online-baccarat-malaysia"
    
    print(f"📡 Fetching: {test_url}")
    
    try:
        # Fetch content twice
        content1 = tracker.get_website_content(test_url)
        if content1:
            print(f"✅ Content fetched: {len(content1):,} bytes")
            
            # Normalize and hash
            normalized = tracker.normalize_content(content1)
            hash1 = tracker.calculate_content_hash(content1)
            
            print(f"📊 Original length: {len(content1):,} bytes")
            print(f"📊 Normalized length: {len(normalized):,} bytes")
            print(f"🔑 Content hash: {hash1}")
            
            # Show a sample of what gets normalized
            if len(content1) != len(normalized):
                reduction = len(content1) - len(normalized)
                print(f"📉 Size reduction: {reduction:,} bytes ({reduction/len(content1)*100:.1f}%)")
            
            return True
        else:
            print("❌ Failed to fetch content")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Content Normalization Test Suite")
    print("This tests if dynamic content is properly filtered out")
    print("="*60)
    
    # Test normalization logic
    norm_success = test_normalization()
    
    # Test with real website
    real_success = test_real_website()
    
    print("\n🎯 Summary:")
    if norm_success and real_success:
        print("✅ Content normalization is working correctly!")
        print("🔄 This should reduce false positive change detections.")
    else:
        print("⚠️ Content normalization needs improvement.")
        print("🔧 Check the test results above for issues.")
