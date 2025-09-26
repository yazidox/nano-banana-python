#!/usr/bin/env python3
"""
Test script to compare Gemini vs Flux for glasses overlay functionality.
"""

import requests
import json
import time

# API endpoints
BASE_URL = "http://localhost:8000"
GEMINI_ENDPOINT = f"{BASE_URL}/add-glasses"
FLUX_ENDPOINT = f"{BASE_URL}/add-glasses-flux"

def test_glasses_overlay(endpoint_name, endpoint_url, test_image_url):
    """Test a glasses overlay endpoint"""
    
    payload = {
        "image_url": test_image_url
    }
    
    print(f"\n🧪 Testing {endpoint_name} endpoint: {endpoint_url}")
    print(f"Image URL: {test_image_url}")
    print("Sending request...")
    
    try:
        # Send request
        start_time = time.time()
        response = requests.post(endpoint_url, json=payload, timeout=180)
        end_time = time.time()
        
        print(f"Response received in {end_time - start_time:.2f} seconds")
        print(f"Status code: {response.status_code}")
        
        # Parse response
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if result.get("success"):
            print(f"✅ Success! Glasses added: {result.get('image_url')}")
            print(f"Local path: {result.get('local_path')}")
            return True, result.get('image_url'), end_time - start_time
        else:
            print(f"❌ Failed: {result.get('message')}")
            return False, None, end_time - start_time
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (>180s)")
        return False, None, None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False, None, None
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON response: {response.text}")
        return False, None, None

def test_api_info():
    """Test the root endpoint to see available endpoints"""
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            info = response.json()
            print("API Information:")
            print(json.dumps(info, indent=2))
            return True
        else:
            print(f"Failed to get API info: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error getting API info: {e}")
        return False

def main():
    print("🚀 Testing Glasses Overlay API - Gemini vs Flux Comparison")
    print("="*70)
    
    # Test images (you can modify these)
    test_images = [
        "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=500&h=500&fit=crop",  # Portrait
        "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=500&h=500&fit=crop",  # Another portrait
    ]
    
    # First, check if API is running
    print("1. Checking API status...")
    if not test_api_info():
        print("❌ API is not running. Please start the server first.")
        return
    
    print("\n" + "="*70)
    
    results = []
    
    for i, test_image in enumerate(test_images, 1):
        print(f"\n🖼️  TEST IMAGE {i}")
        print("-" * 50)
        
        # Test Gemini
        gemini_success, gemini_url, gemini_time = test_glasses_overlay(
            "Gemini", GEMINI_ENDPOINT, test_image
        )
        
        # Test Flux
        flux_success, flux_url, flux_time = test_glasses_overlay(
            "Flux", FLUX_ENDPOINT, test_image
        )
        
        results.append({
            'image': i,
            'gemini_success': gemini_success,
            'gemini_time': gemini_time,
            'gemini_url': gemini_url,
            'flux_success': flux_success,
            'flux_time': flux_time,
            'flux_url': flux_url
        })
        
        print("\n" + "-" * 50)
    
    # Summary
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    
    for result in results:
        print(f"\nImage {result['image']}:")
        print(f"  Gemini: {'✅ Success' if result['gemini_success'] else '❌ Failed'} "
              f"({result['gemini_time']:.1f}s)" if result['gemini_time'] else "")
        print(f"  Flux:   {'✅ Success' if result['flux_success'] else '❌ Failed'} "
              f"({result['flux_time']:.1f}s)" if result['flux_time'] else "")
        
        if result['gemini_success'] and result['flux_success']:
            print(f"  🏆 Faster: {'Gemini' if result['gemini_time'] < result['flux_time'] else 'Flux'}")
    
    # Overall stats
    gemini_successes = sum(1 for r in results if r['gemini_success'])
    flux_successes = sum(1 for r in results if r['flux_success'])
    
    print(f"\nOverall Success Rate:")
    print(f"  Gemini: {gemini_successes}/{len(results)} ({gemini_successes/len(results)*100:.0f}%)")
    print(f"  Flux:   {flux_successes}/{len(results)} ({flux_successes/len(results)*100:.0f}%)")
    
    if gemini_successes > 0 and flux_successes > 0:
        avg_gemini_time = sum(r['gemini_time'] for r in results if r['gemini_time']) / gemini_successes
        avg_flux_time = sum(r['flux_time'] for r in results if r['flux_time']) / flux_successes
        print(f"\nAverage Processing Time:")
        print(f"  Gemini: {avg_gemini_time:.1f}s")
        print(f"  Flux:   {avg_flux_time:.1f}s")
    
    print("\n" + "="*70)
    print("🔗 Generated Images:")
    for result in results:
        print(f"\nImage {result['image']}:")
        if result['gemini_url']:
            print(f"  Gemini: {result['gemini_url']}")
        if result['flux_url']:
            print(f"  Flux:   {result['flux_url']}")

if __name__ == "__main__":
    main()
