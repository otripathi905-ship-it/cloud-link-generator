#!/usr/bin/env python3
import requests

SERVICE_URL = 'https://link-generator.onrender.com'

print(f"Checking: {SERVICE_URL}")
print("-" * 60)

# Try root endpoint
print("\n1. Testing root endpoint (/)...")
try:
    response = requests.get(SERVICE_URL, timeout=30)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   Error: {e}")

# Try health endpoint
print("\n2. Testing health endpoint (/health)...")
try:
    response = requests.get(f"{SERVICE_URL}/health", timeout=30)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   Error: {e}")

# Try API endpoint
print("\n3. Testing API endpoint (/api/create)...")
try:
    response = requests.post(
        f"{SERVICE_URL}/api/create",
        json={'fallback_url': 'https://example.com'},
        timeout=30
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "="*60)
print("If all return 404, the service may not be deployed yet.")
print("Check: https://dashboard.render.com")
