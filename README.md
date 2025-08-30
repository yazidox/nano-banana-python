# Nano Banana Python - Image Mixer

This project demonstrates how to remix two images using Google Generative AI.

## Setup

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd nano-banana-python
    ```

2.  **Install dependencies using `uv`:**

    ```bash
    uv sync
    ```

3.  **Set your Google Gemini API Key:**
    Ensure you have your `GEMINI_API_KEY` or `GOOGLE_API_KEY` set as an environment variable.

    ```bash
    export GEMINI_API_KEY="YOUR_API_KEY"
    # OR
    export GOOGLE_API_KEY="YOUR_API_KEY"
    ```

## Usage

Run the `mix_images.py` script with two input images and an optional prompt. The remixed image will be saved in the `output` directory (or a custom directory if specified).

### Example 1: Basic Remix

```bash
uv run python src/mix_images.py -i images/jacket.png -i images/person.png
```

### Example 2: Futuristic Cyberpunk Scene

```bash
uv run python src/mix_images.py -i images/jacket.png -i images/person.png --prompt "Remix these two images into a futuristic cyberpunk scene."
```

### Example 3: Specify Output Directory

```bash
uv run python src/mix_images.py -i images/jacket.png -i images/person.png --prompt "Remix these two images." --output-dir my_custom_output
```
