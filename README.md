# Glasses Overlay - Add Glasses to Any Image

This project uses Google's Gemini AI to automatically add glasses to any person in an image from a URL.

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

## Usage

The script takes an image URL and adds the glasses.png overlay to the person in the image.

### Basic Usage

```bash
uv run python src/mix_images.py --url "IMAGE_URL_HERE"
```

### Example with a real image URL

```bash
# Add glasses to any portrait image
uv run python src/mix_images.py --url "https://example.com/person.jpg"
```

### Custom output directory

```bash
uv run python src/mix_images.py --url "IMAGE_URL" --output-dir my_output
```

## How it works

1. The script downloads the image from the provided URL
2. Sends both the downloaded image and glasses.png to Gemini AI
3. Gemini intelligently places the glasses on the person's face
4. Saves the result in the output directory

## Output

The processed image will be saved in the `output` directory with a filename like:
- `with_glasses_[timestamp]_0.png`

## Requirements

- Python 3.10+
- Internet connection to download images and use the API
- (API key is already included in the code)