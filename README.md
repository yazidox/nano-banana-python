# Glasses Overlay API - Add Glasses to Any Image

This project provides a FastAPI-based service that uses Google's Gemini AI to automatically add glasses to any person in an image from a URL.

## Setup

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd nano-banana-python
   ```

2. **Install dependencies using `uv`:**
   ```bash
   uv sync
   ```

   Note: The Gemini API key is already configured in the code, no need to set it up!

## Running the API

Start the API server:

```bash
uv run python src/api.py
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

## API Usage

### Add Glasses Endpoint

**POST** `/add-glasses`

Send a JSON request with an image URL:

```json
{
  "image_url": "https://example.com/person.jpg"
}
```

**Example using curl:**

```bash
curl -X POST "http://localhost:8000/add-glasses" \
     -H "Content-Type: application/json" \
     -d '{"image_url": "https://example.com/person.jpg"}'
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

### Health Check

**GET** `/health` - Check if the API is running

**GET** `/` - API information and available endpoints

## Frontend Integration

The API is designed to work seamlessly with frontend applications. See `frontend_example.html` for a complete example of how to integrate with a web frontend.

## How it works

1. The API receives an image URL via POST request
2. Downloads the image from the provided URL
3. Sends both the downloaded image and glasses.png to Gemini AI with advanced positioning prompts
4. Gemini intelligently places glasses on all detected faces with optimal positioning
5. Returns the processed image URL for immediate use

## Output

Processed images are saved in the `output` directory and served as static files through the API with filenames like:
- `with_glasses_[timestamp]_0.png`

## Requirements

- Python 3.10+
- Internet connection to download images and use the Gemini API
- (API key is already included in the code)