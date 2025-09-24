#!/bin/bash

# Script to test glasses API by generating 10 images
# Usage: ./test_10_images.sh

echo "🔥 Testing Glasses API - Generating 10 images..."
echo "=========================================="

IMAGE_URL="https://pbs.twimg.com/profile_images/1785089965619118080/NATKmh45_400x400.jpg"
API_URL="http://localhost:8000/add-glasses"

# Counter for successful and failed requests
SUCCESS_COUNT=0
FAIL_COUNT=0

# Array to store results
declare -a RESULTS

for i in {1..10}; do
    echo "🚀 Generating image $i/10..."
    
    # Make the API call and capture the response
    RESPONSE=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"image_url\": \"$IMAGE_URL\"}")
    
    # Check if the response contains success
    if echo "$RESPONSE" | jq -e '.success == true' > /dev/null 2>&1; then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        IMAGE_URL_RESULT=$(echo "$RESPONSE" | jq -r '.image_url')
        LOCAL_PATH=$(echo "$RESPONSE" | jq -r '.local_path')
        echo "✅ Success! Image saved to: $LOCAL_PATH"
        echo "🌐 URL: $IMAGE_URL_RESULT"
        RESULTS[$i]="✅ Image $i: SUCCESS - $LOCAL_PATH"
    else
        FAIL_COUNT=$((FAIL_COUNT + 1))
        ERROR_MSG=$(echo "$RESPONSE" | jq -r '.message // "Unknown error"')
        echo "❌ Failed! Error: $ERROR_MSG"
        RESULTS[$i]="❌ Image $i: FAILED - $ERROR_MSG"
    fi
    
    echo "----------------------------------------"
    
    # Small delay to avoid overwhelming the API
    sleep 1
done

echo ""
echo "🎯 FINAL RESULTS:"
echo "================="
echo "✅ Successful: $SUCCESS_COUNT/10"
echo "❌ Failed: $FAIL_COUNT/10"
echo ""

echo "📋 DETAILED RESULTS:"
echo "==================="
for i in {1..10}; do
    echo "${RESULTS[$i]}"
done

echo ""
if [ $SUCCESS_COUNT -gt 0 ]; then
    echo "🖼️  Generated images are in the 'output' directory"
    echo "📁 You can check them with: ls -la output/"
fi

echo ""
echo "🔍 To check for temple bars/arms in the results:"
echo "   Look at each generated image and count how many have unwanted temple bars"
echo "   Good images should only show the front part of glasses (no side arms)"
