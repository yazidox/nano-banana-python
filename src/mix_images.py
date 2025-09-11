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
        prompt = """⚠️ CRITICAL: DO NOT CROP THE IMAGE! The output MUST have the EXACT SAME dimensions as the input image!
        
        Task: Add the glasses from the second image onto the person's face in the first image.
        
        🚨 ABSOLUTE REQUIREMENTS - FAILURE TO FOLLOW WILL RESULT IN REJECTION:
        
        1. ⛔ NO CROPPING ALLOWED:
           - The output image MUST be the EXACT same size (width x height) as the input image
           - If the input shows a full body, the output MUST show the full body
           - If the input shows a person from head to waist, output MUST show head to waist
           - NEVER zoom in on just the face or upper portion
           - NEVER cut off any part of the original image
           - Keep ALL edges and borders exactly as they were
        
        2. FULL IMAGE PRESERVATION:
           - Include 100% of the original image content
           - Keep the ENTIRE background visible
           - Maintain ALL surrounding elements
           - Preserve the COMPLETE scene from edge to edge
           - The person should appear at the SAME size and position as in the original
        
        3. GLASSES REQUIREMENTS:
           - Size the glasses proportionally to fit the face naturally
           - The glasses width should span from temple to temple
           - Center the glasses on the face horizontally
           - Position at proper eye level with both eyes visible through lenses
           - Keep the exact style and appearance of the provided glasses
        
        👁️ MOST IMPORTANT - EYE VISIBILITY & POSITIONING:
           - BOTH EYES MUST BE CLEARLY VISIBLE IN THE CENTER OF THE GLASSES LENSES
           - The eyes should look through the CENTER of each lens, not near the edges
           - The glasses frames/borders MUST NOT hide or cover any part of the eyes
           - The eyes should be fully visible and unobstructed by the glasses frames
           - Position glasses so the pupils align with the center of each lens
           - Ensure the glasses bridge sits on the nose without blocking the eyes
           
           NATURAL SPACING - CRITICAL:
           - The top frame of the glasses should sit SLIGHTLY ABOVE the eyebrows
           - There should be a small natural gap between the eyes and the lens
           - The glasses should NOT sit too close or touch the eyes/eyelashes
           - Position the glasses as if they're resting naturally on the nose bridge
           - The bottom of the lenses should be positioned just below the lower eyelid
           - Maintain realistic distance as if the person is actually wearing glasses comfortably
        
        4. OUTPUT VERIFICATION:
           - The output dimensions MUST match input dimensions EXACTLY
           - If input is 1920x1080, output MUST be 1920x1080
           - If input is 800x1200, output MUST be 800x1200
           - The entire original composition must be preserved
        
        ⚠️ REMEMBER: The ONLY change should be adding glasses. EVERYTHING else including image dimensions, zoom level, framing, and visible content MUST remain EXACTLY the same as the original full image!"""
        
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