# Glasses Overlay API Documentation

## 🚀 Quick Start

### 1. Start the API Server
```bash
uv run python src/api.py
```

The API will be available at: `http://localhost:8000`

### 2. API Endpoints

#### **POST /add-glasses**
Add glasses to a person in an image.

**Request Body:**
```json
{
  "image_url": "https://example.com/portrait.jpg"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Glasses added successfully!",
  "image_url": "http://localhost:8000/output/with_glasses_1234567890_0.png",
  "local_path": "output/with_glasses_1234567890_0.png"
}
```

#### **GET /**
Returns API information

#### **GET /health**
Health check endpoint

## 📱 Frontend Integration Examples

### JavaScript/Fetch
```javascript
async function addGlasses(imageUrl) {
  const response = await fetch('http://localhost:8000/add-glasses', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ image_url: imageUrl })
  });
  
  const data = await response.json();
  console.log('Processed image URL:', data.image_url);
  return data;
}

// Usage
addGlasses('https://example.com/portrait.jpg')
  .then(data => {
    if (data.success) {
      // Display the image
      document.getElementById('result').src = data.image_url;
    }
  });
```

### React Example
```jsx
import { useState } from 'react';

function GlassesOverlay() {
  const [imageUrl, setImageUrl] = useState('');
  const [resultUrl, setResultUrl] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/add-glasses', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_url: imageUrl })
      });
      const data = await response.json();
      if (data.success) {
        setResultUrl(data.image_url);
      }
    } catch (error) {
      console.error('Error:', error);
    }
    setLoading(false);
  };

  return (
    <div>
      <input 
        value={imageUrl} 
        onChange={(e) => setImageUrl(e.target.value)}
        placeholder="Enter image URL"
      />
      <button onClick={handleSubmit} disabled={loading}>
        {loading ? 'Processing...' : 'Add Glasses'}
      </button>
      {resultUrl && <img src={resultUrl} alt="Result" />}
    </div>
  );
}
```

### cURL Example
```bash
curl -X POST "http://localhost:8000/add-glasses" \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://images.pexels.com/photos/614810/pexels-photo-614810.jpeg"}'
```

### Python Requests Example
```python
import requests

response = requests.post(
    'http://localhost:8000/add-glasses',
    json={'image_url': 'https://example.com/portrait.jpg'}
)

data = response.json()
if data['success']:
    print(f"Processed image: {data['image_url']}")
```

## 🌐 Testing with Frontend

1. Open `frontend_example.html` in your browser
2. Make sure the API server is running
3. Enter an image URL or use one of the examples
4. Click "Add Glasses" and see the result!

## 🔧 API Features

- **CORS Enabled**: Can be called from any frontend domain
- **Static File Serving**: Generated images are served directly from the API
- **Error Handling**: Graceful error messages for invalid URLs or processing errors
- **Fast Response**: Images are processed using Google's Gemini AI

## 📝 Notes

- The API key is hardcoded in `src/api.py`
- Generated images are saved in the `output/` directory
- The API serves static files from `/output` endpoint
- Default port is 8000 (can be changed in `api.py`)

## 🚢 Production Deployment

For production, consider:
1. Using environment variables for the API key
2. Setting specific CORS origins instead of "*"
3. Adding authentication/rate limiting
4. Using a production ASGI server like Gunicorn
5. Serving static files through a CDN or nginx
