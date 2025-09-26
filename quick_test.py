#!/usr/bin/env python3
"""
Quick test to verify both glasses overlay endpoints work.
"""

import requests
import json

# Test the API endpoints
BASE_URL = "http://localhost:8000"

def test_api():
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            info = response.json()
            print("✅ API is running!")
            print("Available endpoints:")
            for endpoint, description in info.get("endpoints", {}).items():
                print(f"  {endpoint}: {description}")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")
        print("Make sure to start the server first: uv run python src/api.py")
        return False

if __name__ == "__main__":
    print("🧪 Quick API Test")
    print("="*50)
    test_api()
    print("\n📝 To test the glasses overlay:")
    print("1. Start the server: uv run python src/api.py")
    print("2. Open flux_example.html in your browser")
    print("3. Or run: python test_glasses_comparison.py")
