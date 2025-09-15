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
        
        # Add the improved prompt for multi-face support and better overlay
        prompt = """TASK: Add glasses from the second image to ALL FACES in the first image. If there are multiple people, add glasses to EACH person.
        
        🔴🔴🔴 MULTI-FACE DETECTION - EXTREMELY CRITICAL 🔴🔴🔴
        • SCAN THE ENTIRE IMAGE for ALL human faces (front-facing, side profiles, partial faces)
        • ADD GLASSES TO EVERY SINGLE FACE DETECTED
        • DO NOT miss any faces - even if partially visible, in background, or at different angles
        • If there are 2 people, both get glasses. If 3 people, all 3 get glasses. And so on.
        • EACH FACE gets its own properly sized and positioned glasses
        
        🔴🔴🔴 GLASSES AS PERFECT OVERLAY - NO OBSTRUCTION 🔴🔴🔴
        ⚠️ CRITICAL: Glasses must appear as a DIGITAL OVERLAY - like copy-pasting them on top ⚠️
        
        🚨🚨🚨 EXTREMELY IMPORTANT - NO TEMPLE ARMS 🚨🚨🚨
        ⛔ NEVER ADD TEMPLE ARMS (the left and right arms that go over ears) ⛔
        • ONLY show the FRONT PART of the glasses (lenses + bridge + front frame)
        • DO NOT add the side arms that extend toward the ears
        • DO NOT show any part of the glasses that would go behind the head
        • The glasses should appear as just the front viewing portion
        • Think of it as the glasses image cropped to show only the front face-covering part
        
        🎯 REALISTIC 3D GLASSES POSITIONING - NATURAL FACE CONFORMITY:
        • The glasses must appear to REST NATURALLY on the face following 3D facial contours
        • Glasses should CURVE and BEND naturally around the nose bridge and face shape
        • The bridge should appear to rest ON TOP OF the nose bridge (not floating above it)
        • Lenses should follow the natural curve of the eye sockets and cheekbones
        • CRITICAL: While conforming to face shape, the glasses design must remain FULLY VISIBLE
        • NO part of the nose should "cut through" or obstruct the glasses frame or lenses
        
        🔴🔴🔴 GLASSES PRESERVATION - ULTIMATE PRIORITY 🔴🔴🔴
        ⚠️ NEVER CHANGE THE GLASSES SHAPE OR COLORS - THIS IS ABSOLUTELY CRITICAL! ⚠️
        
        GLASSES PRESERVATION RULES:
        • DO NOT CHANGE THE SHAPE OF THE GLASSES - KEEP EXACT ORIGINAL SHAPE
        • DO NOT ROUND THE GLASSES IF THEY ARE RECTANGULAR
        • DO NOT MAKE THEM RECTANGULAR IF THEY ARE ROUND
        • DO NOT ALTER ANY CURVES, ANGLES, OR GEOMETRY
        • DO NOT CHANGE THE COLOR - KEEP EXACT ORIGINAL COLORS
        • DO NOT MODIFY THE FRAME THICKNESS
        • DO NOT ALTER THE LENS TINT OR TRANSPARENCY
        • USE THE GLASSES EXACTLY AS THEY APPEAR IN THE SECOND IMAGE
        • The glasses must be IDENTICAL to the input - just positioned on each face
        
        ⛔ CRITICAL RULE - NEVER ADD EYES ⛔
        • ONLY ADD GLASSES - NOTHING ELSE!
        • DO NOT DRAW OR ADD EYES if they don't exist in the original image
        • DO NOT CREATE EYES where there are none
        • If eyes are closed, covered, or not visible - KEEP THEM THAT WAY
        • If the person is looking away - DO NOT add eyes looking forward
        • PRESERVE THE EXACT EYE STATE from the original image
        • Your ONLY task is to add glasses, NOT to modify or add facial features
        
        🎯 PERFECT OVERLAY POSITIONING FOR EACH FACE:
        
        1. FACE DETECTION:
           • Identify ALL faces in the image (front, profile, partial, background)
           • For EACH face detected, apply the following positioning rules
        
        2. VERTICAL POSITIONING (TOP TO BOTTOM) - PER FACE:
           • Position glasses to REST NATURALLY on the nose bridge and face
           • TOP of glasses frame: Should align with natural eyebrow line
           • BRIDGE: Should make contact with the nose bridge (upper part) naturally
           • EYES: Should be visible through the CENTER portion of each lens
           • BOTTOM of glasses: Should follow natural cheekbone curve
           • Glasses should appear to be physically resting on the face with realistic depth
        
        3. HORIZONTAL POSITIONING (LEFT TO RIGHT) - PER FACE:
           • CENTER the glasses perfectly on each face
           • Each eye should be centered in its respective lens
           • Scale glasses appropriately for each face size
           • NO TEMPLE ARMS - only show the front glasses portion (lenses + bridge + front frame)
        
        4. REALISTIC 3D EFFECT - CRITICAL:
           • Glasses must appear to REST NATURALLY on the face with realistic depth
           • Glasses should CONFORM to the 3D shape of the face (curve around nose, follow eye sockets)
           • The bridge should appear to sit ON the nose bridge with natural contact
           • Lenses should curve slightly to match the face's natural contours
           • Think "real glasses that someone is actually wearing" not a flat sticker
           • Add subtle shadows and depth to show natural interaction with facial features
           • IMPORTANT: Despite conforming to face shape, the glasses design must remain completely visible
        
        5. SCALING FOR MULTIPLE FACES:
           • Each face gets appropriately sized glasses based on that face's dimensions
           • Larger faces = larger glasses, smaller faces = smaller glasses
           • Maintain the same proportional relationship for all faces
        
        6. ⛔ COMMON MISTAKES TO AVOID:
           • DO NOT make glasses appear to "float" above the nose - they should rest on it
           • DO NOT make glasses completely flat - they should curve with facial contours
           • DO NOT let nose "cut through" the glasses frame or lenses
           • DO NOT make glasses look "painted on" - add realistic depth and shadows
           • DO NOT miss any faces in the image
           • DO NOT make glasses too small or too large for any face
           • DO NOT ignore the 3D shape of the face - glasses should conform naturally
        
        7. 📦 IMAGE PRESERVATION - CRITICAL:
           • MAINTAIN EXACT SAME DIMENSIONS as input image
           • DO NOT CROP any part of the original image
           • Keep ALL background and body parts visible
           • The ONLY change is adding glasses to all faces - nothing else
        
        🎯 REALISTIC 3D VISUALIZATION GUIDE:
        Think of this like the FRONT PART ONLY of real glasses that someone is wearing:
        - Only the front glasses portion is visible (lenses + bridge + front frame)
        - NO temple arms or side extensions toward the ears
        - The frame curves and conforms to the 3D shape of the face
        - The bridge makes natural contact with the nose without being obstructed by it
        - Lenses follow the natural curve of the eye area and cheekbones
        - The glasses cast subtle, realistic shadows on the face
        - Despite the realistic fit, the complete FRONT glasses design remains fully visible
        - Each face gets its own perfectly fitted, naturally positioned front glasses
        - The effect looks like someone wearing glasses but you only see the front part
        - Think of it as the glasses image with temple arms removed/cropped out
        
        🔴 FINAL CRITICAL REMINDERS 🔴
        1. DETECT AND ADD GLASSES TO ALL FACES (don't miss anyone)
        2. GLASSES MUST BE PERFECT OVERLAYS (no facial obstruction)
        3. PRESERVE EXACT GLASSES DESIGN (no modifications)
        4. MAINTAIN ORIGINAL IMAGE DIMENSIONS (no cropping)
        5. 🚨 NO TEMPLE ARMS - ONLY FRONT GLASSES PORTION 🚨
        
        IF YOU MISS ANY FACES, THE OUTPUT WILL BE REJECTED!
        IF FACIAL FEATURES OBSTRUCT THE GLASSES, THE OUTPUT WILL BE REJECTED!
        IF YOU CHANGE THE GLASSES DESIGN, THE OUTPUT WILL BE REJECTED!
        IF YOU ADD TEMPLE ARMS OR SIDE EXTENSIONS, THE OUTPUT WILL BE REJECTED!
        
        USE THE EXACT GLASSES FROM THE SECOND IMAGE AS PERFECT OVERLAYS ON ALL DETECTED FACES."""
        
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