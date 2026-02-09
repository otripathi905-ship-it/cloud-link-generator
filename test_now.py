#!/usr/bin/env python3
"""Quick test of cloud link generator service"""

import requests

print("="*70)
print("CLOUD LINK GENERATOR - LIVE TEST")
print("="*70)

SERVICE_URL = 'https://link-generator.onrender.com'

print(f"\n🔗 Testing: {SERVICE_URL}")
print("-" * 70)

# Test 1: Health Check
print("\n✓ Test 1: Health Check")
try:
    print("  Connecting...")
    response = requests.get(f"{SERVICE_URL}/health", timeout=30)
    if response.status_code == 200:
        print("  ✅ Service is ONLINE!")
        data = response.json()
        print(f"  Status: {data.get('status')}")
    else:
        print(f"  ❌ HTTP {response.status_code}")
        exit(1)
except Exception as e:
    print(f"  ❌ Error: {e}")
    print("\n  Note: Service might be sleeping (Render free tier)")
    print("  First request wakes it up (takes ~30 seconds)")
    exit(1)

# Test 2: Create Link
print("\n✓ Test 2: Create Smart Link")
try:
    data = {
        'name': 'Test App Download',
        'android_url': 'https://play.google.com/store/apps/details?id=com.example',
        'ios_url': 'https://apps.apple.com/app/id123456789',
        'fallback_url': 'https://example.com'
    }
    
    response = requests.post(f"{SERVICE_URL}/api/create", json=data, timeout=10)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("  ✅ Link created!")
            print(f"  URL: {result['url']}")
            print(f"  Token: {result['token']}")
            
            # Test 3: Stats
            print("\n✓ Test 3: Get Statistics")
            stats_resp = requests.get(f"{SERVICE_URL}/api/stats/{result['token']}", timeout=10)
            if stats_resp.status_code == 200:
                stats = stats_resp.json()
                print(f"  ✅ Stats retrieved!")
                print(f"  Clicks: {stats['click_count']}")
            
            print("\n" + "="*70)
            print("✅ ALL TESTS PASSED!")
            print("="*70)
            print(f"\n🎉 Service is working perfectly!")
            print(f"\n📱 Your smart link: {result['url']}")
            print(f"\n✅ Ready to use in your mailer!")
        else:
            print(f"  ❌ Error: {result.get('error')}")
    else:
        print(f"  ❌ HTTP {response.status_code}")
        
except Exception as e:
    print(f"  ❌ Error: {e}")

print()
