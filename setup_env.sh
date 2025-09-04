#!/bin/bash

# Setup script for nano-banana-python project

echo "======================================"
echo "Nano Banana Python - Environment Setup"
echo "======================================"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << 'EOF'
# Google Gemini API Configuration
# Get your API key from: https://aistudio.google.com/

# Set your Gemini API key here
GEMINI_API_KEY=your-gemini-api-key-here
EOF
    echo "✅ Created .env file"
    echo ""
fi

echo "📋 Setup Instructions:"
echo ""
echo "1. Get your Google Gemini API key:"
echo "   - Go to https://aistudio.google.com/"
echo "   - Sign in with your Google account"
echo "   - Click 'Get API key' in the left sidebar"
echo "   - Create a new API key or use an existing one"
echo ""
echo "2. Add your API key to the .env file:"
echo "   - Open .env file in your editor"
echo "   - Replace 'your-gemini-api-key-here' with your actual API key"
echo ""
echo "3. Install dependencies (if not already done):"
echo "   uv sync"
echo ""
echo "4. Run the project:"
echo "   # Example: Improve a single image"
echo "   uv run python src/mix_images.py -i images/man.jpeg"
echo ""
echo "   # Example: Combine multiple images"
echo "   uv run python src/mix_images.py -i images/man.jpeg -i images/cap.jpeg"
echo ""

# Check if API key is already set
if [ -n "$GEMINI_API_KEY" ]; then
    echo "✅ GEMINI_API_KEY is already set in your environment"
elif [ -f .env ] && grep -q "GEMINI_API_KEY=" .env && ! grep -q "GEMINI_API_KEY=your-gemini-api-key-here" .env; then
    echo "✅ GEMINI_API_KEY appears to be configured in .env file"
else
    echo "⚠️  Remember to set your GEMINI_API_KEY in the .env file!"
fi
