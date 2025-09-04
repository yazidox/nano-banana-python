import argparse
import os
import time
import requests
from google import genai
from google.genai import types
import mimetypes
import tempfile

MODEL_NAME = "gemini-2.5-flash-image-preview"

def add_glasses_to_image(
    image_url: str,
    glasses_path: str,
    output_dir: str,
):
    """
    Adds glasses to a person in an image from URL using Google Generative AI.
    
    Args:
        image_url: URL of the image to add glasses to
        glasses_path: Path to the glasses.png file
        output_dir: Directory to save the output image
    """
    # Hardcoded API key - no need to export anymore
    api_key = "AIzaSyDnL0OD9FthrNAujYn_EaHy38dTxuKe5wc"
    
    client = genai.Client(api_key=api_key)
    
    # Download image from URL
    print(f"Downloading image from: {image_url}")
    response = requests.get(image_url)
    response.raise_for_status()
    
    # Save to temporary file to determine mime type
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        tmp_file.write(response.content)
        temp_path = tmp_file.name
    
    try:
        # Load both images
        contents = []
        
        # Load downloaded image
        with open(temp_path, "rb") as f:
            image_data = f.read()
        mime_type = _get_mime_type(temp_path)
        contents.append(
            types.Part(inline_data=types.Blob(data=image_data, mime_type=mime_type))
        )
        
        # Load glasses image
        with open(glasses_path, "rb") as f:
            glasses_data = f.read()
        glasses_mime = _get_mime_type(glasses_path)
        contents.append(
            types.Part(inline_data=types.Blob(data=glasses_data, mime_type=glasses_mime))
        )
        
        # Add the prompt
        prompt = """Take the first image (the person) and add the glasses from the second image onto their face. 
        The glasses should be positioned naturally where glasses would normally sit on a person's face. 
        Maintain the exact same style and appearance of the glasses from the second image.
        Keep everything else about the person and background exactly the same, just add the glasses."""
        
        contents.append(genai.types.Part.from_text(text=prompt))
        
        generate_content_config = types.GenerateContentConfig(
            response_modalities=["IMAGE"],
        )
        
        print("Adding glasses to the image...")
        
        stream = client.models.generate_content_stream(
            model=MODEL_NAME,
            contents=contents,
            config=generate_content_config,
        )
        
        _process_api_stream_response(stream, output_dir)
        
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

def _process_api_stream_response(stream, output_dir: str):
    """Processes the streaming response from the GenAI API, saving images."""
    file_index = 0
    for chunk in stream:
        if (
            chunk.candidates is None
            or chunk.candidates[0].content is None
            or chunk.candidates[0].content.parts is None
        ):
            continue
        
        for part in chunk.candidates[0].content.parts:
            if part.inline_data and part.inline_data.data:
                timestamp = int(time.time())
                file_extension = mimetypes.guess_extension(part.inline_data.mime_type)
                file_name = os.path.join(
                    output_dir,
                    f"with_glasses_{timestamp}_{file_index}{file_extension}",
                )
                _save_binary_file(file_name, part.inline_data.data)
                file_index += 1
            elif part.text:
                print(part.text)

def _save_binary_file(file_name: str, data: bytes):
    """Saves binary data to a specified file."""
    with open(file_name, "wb") as f:
        f.write(data)
    print(f"✅ Image with glasses saved to: {file_name}")

def _get_mime_type(file_path: str) -> str:
    """Guesses the MIME type of a file based on its extension."""
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        # Default to JPEG for images
        return "image/jpeg"
    return mime_type

def main():
    parser = argparse.ArgumentParser(
        description="Add glasses to any image from a URL using Google Generative AI."
    )
    parser.add_argument(
        "--url",
        type=str,
        required=True,
        help="URL of the image to add glasses to",
    )
    parser.add_argument(
        "--glasses",
        type=str,
        default="images/glasses.png",
        help="Path to glasses image (default: images/glasses.png)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="Directory to save the output image (default: output)",
    )
    
    args = parser.parse_args()
    
    # Check if glasses file exists
    if not os.path.exists(args.glasses):
        parser.error(f"Glasses file not found: {args.glasses}")
    
    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    
    add_glasses_to_image(
        image_url=args.url,
        glasses_path=args.glasses,
        output_dir=args.output_dir,
    )

if __name__ == "__main__":
    main()