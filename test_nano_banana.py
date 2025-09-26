#!/usr/bin/env python3
"""
Test script for the nano-banana glasses overlay endpoint.
"""

import requests
import json
import time
import os

# Configuration
API_BASE_URL = "http://localhost:8000"  # Change this to your API URL
TEST_IMAGE_URL = "https://example.com/photo_2025-09-24_22-59-53.jpg"  # Replace with actual image URL

def test_nano_banana_endpoint():
    """Test the nano-banana glasses overlay endpoint"""
    
    print("🧪 Testing nano-banana glasses overlay endpoint...")
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Test Image URL: {TEST_IMAGE_URL}")
    print("-" * 50)
    
    # Prepare the request
    endpoint = f"{API_BASE_URL}/add-glasses"
    payload = {
        "image_url": TEST_IMAGE_URL
    }
    
    print("📤 Sending request to nano-banana endpoint...")
    print(f"Endpoint: {endpoint}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        # Send the request
        start_time = time.time()
        response = requests.post(endpoint, json=payload, timeout=120)  # 2 minute timeout
        end_time = time.time()
        
        processing_time = end_time - start_time
        print(f"⏱️  Processing time: {processing_time:.2f} seconds")
        
        # Check response status
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success! Response:")
            print(json.dumps(result, indent=2))
            
            if result.get("success") and result.get("image_url"):
                print(f"🖼️  Generated image URL: {result['image_url']}")
                print(f"📁 Local path: {result.get('local_path', 'N/A')}")
                
                # Try to verify the image exists
                try:
                    img_response = requests.head(result["image_url"], timeout=10)
                    if img_response.status_code == 200:
                        print("✅ Generated image is accessible!")
                    else:
                        print(f"⚠️  Generated image returned status: {img_response.status_code}")
                except Exception as e:
                    print(f"⚠️  Could not verify image accessibility: {e}")
            else:
                print("⚠️  Success response but missing image URL")
        else:
            print("❌ Request failed!")
            try:
                error_result = response.json()
                print("Error response:")
                print(json.dumps(error_result, indent=2))
            except:
                print(f"Raw response: {response.text}")
                
    except requests.exceptions.Timeout:
        print("⏰ Request timed out (>2 minutes)")
    except requests.exceptions.ConnectionError:
        print("🔌 Could not connect to the API. Make sure the server is running.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_health_endpoint():
    """Test the health endpoint to verify API is running"""
    print("🔍 Testing health endpoint...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("✅ API is healthy!")
            print(json.dumps(result, indent=2))
            return True
        else:
            print(f"⚠️  Health check returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_root_endpoint():
    """Test the root endpoint to see available endpoints"""
    print("📋 Testing root endpoint for API info...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("✅ API info retrieved!")
            print(json.dumps(result, indent=2))
            return True
        else:
            print(f"⚠️  Root endpoint returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting nano-banana API tests...")
    print("=" * 60)
    
    # Test health endpoint first
    if test_health_endpoint():
        print("\n" + "=" * 60)
        
        # Test root endpoint
        test_root_endpoint()
        print("\n" + "=" * 60)
        
        # Test nano-banana endpoint
        test_nano_banana_endpoint()
    else:
        print("\n❌ API health check failed. Make sure the server is running with:")
        print("   python src/api.py")
        print("   or")
        print("   uvicorn src.api:app --host 0.0.0.0 --port 8000")
    
    print("\n🏁 Tests completed!")
