#!/usr/bin/env python3
"""
Test script for the new Flux Image Mixer glasses overlay functionality.
"""

import requests
import json
import time

# API endpoint
BASE_URL = "http://localhost:8000"
FLUX_ENDPOINT = f"{BASE_URL}/add-glasses-flux"

def test_flux_image_mixer():
    """Test the Flux Image Mixer endpoint"""
    
    # Test with a portrait image
    test_image_url = "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=500&h=500&fit=crop"
    
    # Request payload
    payload = {
        "image_url": test_image_url
    }
    
    print(f"Testing Flux Image Mixer endpoint: {FLUX_ENDPOINT}")
    print(f"Image URL: {test_image_url}")
    print("This will blend the glasses.png with the input image...")
    print("Sending request...")
    
    try:
        # Send request
        start_time = time.time()
        response = requests.post(FLUX_ENDPOINT, json=payload, timeout=120)
        end_time = time.time()
        
        print(f"Response received in {end_time - start_time:.2f} seconds")
        print(f"Status code: {response.status_code}")
        
        # Parse response
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if result.get("success"):
            print(f"✅ Success! Images mixed: {result.get('image_url')}")
            print(f"Local path: {result.get('local_path')}")
        else:
            print(f"❌ Failed: {result.get('message')}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (>120s)")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON response: {response.text}")

def test_api_info():
    """Test the root endpoint to see available endpoints"""
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            info = response.json()
            print("API Information:")
            print(json.dumps(info, indent=2))
        else:
            print(f"Failed to get API info: {response.status_code}")
    except Exception as e:
        print(f"Error getting API info: {e}")

if __name__ == "__main__":
    print("🚀 Testing Flux Image Mixer - Glasses Blending")
    print("="*60)
    
    # First, check if API is running
    print("1. Checking API status...")
    test_api_info()
    print()
    
    # Then test Flux image mixing
    print("2. Testing Flux Image Mixer...")
    test_flux_image_mixer()
    print()
    
    print("📝 Note:")
    print("- This uses lambdal/image-mixer model to blend glasses.png with your photo")
    print("- Same glasses file as Gemini for direct comparison")
    print("- Should produce seamless blending results")
    print("- Requires REPLICATE_API_TOKEN to be set")
