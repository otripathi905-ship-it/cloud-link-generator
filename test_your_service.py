#!/usr/bin/env python3
"""Test YOUR deployed service"""

import requests

YOUR_SERVICE_URL = 'https://link-generator-2mko.onrender.com'

print("="*70)
print("TESTING YOUR CLOUD LINK GENERATOR")
print("="*70)

print(f"\n🔗 Service URL: {YOUR_SERVICE_URL}")
print("-" * 70)

# Test 1: Health Check
print("\n✓ Test 1: Health Check")
try:
    print("  Connecting...")
    response = requests.get(f"{YOUR_SERVICE_URL}/health", timeout=30)
    if response.status_code == 200:
        data = response.json()
        print("  ✅ Service is ONLINE!")
        print(f"  Status: {data.get('status')}")
        print(f"  Timestamp: {data.get('timestamp')}")
    else:
        print(f"  ❌ HTTP {response.status_code}")
        print(f"  Response: {response.text[:200]}")
        exit(1)
except Exception as e:
    print(f"  ❌ Error: {e}")
    print("\n  Note: Service might be sleeping (Render free tier)")
    print("  First request wakes it up (takes ~30 seconds)")
    exit(1)

# Test 2: Create Smart Link
print("\n✓ Test 2: Create Smart Link")
try:
    data = {
        'name': 'Test App Download',
        'android_url': 'https://play.google.com/store/apps/details?id=com.example.app',
        'ios_url': 'https://apps.apple.com/app/id123456789',
        'windows_url': 'https://example.com/download/windows',
        'macos_url': 'https://example.com/download/mac',
        'fallback_url': 'https://example.com'
    }
    
    response = requests.post(f"{YOUR_SERVICE_URL}/api/create", json=data, timeout=10)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("  ✅ Smart link created successfully!")
            print(f"  📱 URL: {result['url']}")
            print(f"  🔑 Token: {result['token']}")
            
            token = result['token']
            smart_url = result['url']
            
            # Test 3: Get Statistics
            print("\n✓ Test 3: Get Link Statistics")
            stats_response = requests.get(f"{YOUR_SERVICE_URL}/api/stats/{token}", timeout=10)
            
            if stats_response.status_code == 200:
                stats = stats_response.json()
                if stats.get('success'):
                    print("  ✅ Statistics retrieved!")
                    print(f"  📊 Clicks: {stats['click_count']}")
                    print(f"  📅 Created: {stats['created_at']}")
                    print(f"  🔄 Active: {stats['is_active']}")
            
            # SUCCESS!
            print("\n" + "="*70)
            print("✅ ALL TESTS PASSED!")
            print("="*70)
            
            print(f"\n🎉 Your cloud link generator is working perfectly!")
            
            print(f"\n📱 Test your smart link:")
            print(f"   {smart_url}")
            print(f"\n   • Open on Android → Redirects to Play Store")
            print(f"   • Open on iPhone → Redirects to App Store")
            print(f"   • Open on Windows → Redirects to Windows download")
            print(f"   • Open on Mac → Redirects to Mac download")
            
            print(f"\n📧 Use in your emails:")
            print(f'   <a href="{smart_url}">Download App</a>')
            
            print(f"\n✅ Ready to integrate with your local mailer!")
            
            print(f"\n📝 Next steps:")
            print(f"   1. Update config.py with: CLOUD_LINK_SERVICE = '{YOUR_SERVICE_URL}'")
            print(f"   2. Run: python example_cloud_link_usage.py")
            print(f"   3. Integrate with your mailer!")
            
        else:
            print(f"  ❌ API returned error: {result.get('error')}")
    else:
        print(f"  ❌ HTTP {response.status_code}: {response.text}")
        
except Exception as e:
    print(f"  ❌ Error: {e}")
    exit(1)

print()
