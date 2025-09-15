from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
import os
import time
import requests
from google import genai
from google.genai import types
import mimetypes
import tempfile
import uvicorn

# Initialize FastAPI app
app = FastAPI(title="Glasses Overlay API", version="1.0.0")

# Get allowed origins from environment or use * for development
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the output directory as static files so we can serve the images
app.mount("/output", StaticFiles(directory="output"), name="output")

# Get configuration from environment variables with defaults
API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDnL0OD9FthrNAujYn_EaHy38dTxuKe5wc")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash-image-preview")
GLASSES_PATH = os.getenv("GLASSES_PATH", "images/glasses.png")
PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "0.0.0.0")

# Get the public URL for the API (Railway provides this)
PUBLIC_URL = os.getenv("RAILWAY_PUBLIC_DOMAIN", "localhost:8000")
if not PUBLIC_URL.startswith("http"):
    PUBLIC_URL = f"https://{PUBLIC_URL}" if "railway" in PUBLIC_URL else f"http://{PUBLIC_URL}"

class GlassesRequest(BaseModel):
    image_url: HttpUrl

class GlassesResponse(BaseModel):
    success: bool
    message: str
    image_url: str = None
    local_path: str = None

def add_glasses_to_image(image_url: str, output_dir: str = "output"):
    """
    Adds glasses to a person in an image from URL using Google Generative AI.
    Returns the path to the generated image.
    """
    client = genai.Client(api_key=API_KEY)
    
    # Download image from URL
    print(f"Downloading image from: {image_url}")
    response = requests.get(image_url, timeout=30)
    response.raise_for_status()
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        tmp_file.write(response.content)
        temp_path = tmp_file.name
    
    try:
        # Load both images
        contents = []
        
        # Load downloaded image
        with open(temp_path, "rb") as f:
            image_data = f.read()
        mime_type = mimetypes.guess_type(temp_path)[0] or "image/jpeg"
        contents.append(
            types.Part(inline_data=types.Blob(data=image_data, mime_type=mime_type))
        )
        
        # Load glasses image
        with open(GLASSES_PATH, "rb") as f:
            glasses_data = f.read()
        glasses_mime = mimetypes.guess_type(GLASSES_PATH)[0] or "image/png"
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
        
        🎯 REALISTIC 3D GLASSES POSITIONING - NATURAL FACE CONFORMITY:
        • The glasses must appear to REST NATURALLY on the face following 3D facial contours
        • Glasses should CURVE and BEND naturally around the nose bridge and face shape
        • The bridge should appear to rest ON TOP OF the nose bridge (not floating above it)
        • Lenses should follow the natural curve of the eye sockets and cheekbones
        • Temple arms should curve naturally around the sides of the head
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
           • Temple arms should extend toward ears naturally
        
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
        Think of this like real glasses that someone is actually wearing:
        - The glasses rest naturally on the nose bridge and ears
        - The frame curves and conforms to the 3D shape of the face
        - The bridge makes natural contact with the nose without being obstructed by it
        - Lenses follow the natural curve of the eye area and cheekbones
        - Temple arms curve naturally around the head shape
        - The glasses cast subtle, realistic shadows on the face
        - Despite the realistic fit, the complete glasses design remains fully visible
        - Each face gets its own perfectly fitted, naturally positioned glasses
        - The effect looks realistic, natural, and professionally fitted
        
        🔴 FINAL CRITICAL REMINDERS 🔴
        1. DETECT AND ADD GLASSES TO ALL FACES (don't miss anyone)
        2. GLASSES MUST BE PERFECT OVERLAYS (no facial obstruction)
        3. PRESERVE EXACT GLASSES DESIGN (no modifications)
        4. MAINTAIN ORIGINAL IMAGE DIMENSIONS (no cropping)
        
        IF YOU MISS ANY FACES, THE OUTPUT WILL BE REJECTED!
        IF FACIAL FEATURES OBSTRUCT THE GLASSES, THE OUTPUT WILL BE REJECTED!
        IF YOU CHANGE THE GLASSES DESIGN, THE OUTPUT WILL BE REJECTED!
        
        USE THE EXACT GLASSES FROM THE SECOND IMAGE AS PERFECT OVERLAYS ON ALL DETECTED FACES."""
        
        contents.append(genai.types.Part.from_text(text=prompt))
        
        generate_content_config = types.GenerateContentConfig(
            response_modalities=["IMAGE"],
        )
        
        print("Processing image with Gemini AI...")
        
        # Generate content
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=generate_content_config,
        )
        
        # Process the response and save the image
        output_filename = None
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.data:
                    timestamp = int(time.time())
                    file_extension = mimetypes.guess_extension(part.inline_data.mime_type) or '.png'
                    output_filename = f"with_glasses_{timestamp}_{0}{file_extension}"
                    output_path = os.path.join(output_dir, output_filename)
                    
                    with open(output_path, "wb") as f:
                        f.write(part.inline_data.data)
                    
                    print(f"Image saved to: {output_path}")
                    return output_filename
        
        raise Exception("No image was generated")
        
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Glasses Overlay API",
        "version": "1.0.0",
        "endpoints": {
            "POST /add-glasses": "Add glasses to an image from URL",
            "GET /health": "Health check endpoint"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "glasses-overlay-api"}

@app.post("/add-glasses", response_model=GlassesResponse)
async def add_glasses(request: GlassesRequest):
    """
    Add glasses to a person in an image.
    
    Args:
        request: GlassesRequest with image_url
        
    Returns:
        GlassesResponse with the URL of the processed image
    """
    try:
        # Ensure output directory exists
        os.makedirs("output", exist_ok=True)
        
        # Process the image
        output_filename = add_glasses_to_image(str(request.image_url))
        
        if output_filename:
            # Create the full URL for the generated image
            image_url = f"{PUBLIC_URL}/output/{output_filename}"
            
            return GlassesResponse(
                success=True,
                message="Glasses added successfully!",
                image_url=image_url,
                local_path=f"output/{output_filename}"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to generate image")
            
    except requests.exceptions.RequestException as e:
        return GlassesResponse(
            success=False,
            message=f"Failed to download image: {str(e)}"
        )
    except Exception as e:
        return GlassesResponse(
            success=False,
            message=f"Error processing image: {str(e)}"
        )

if __name__ == "__main__":
    print("Starting Glasses Overlay API server...")
    print(f"API will be available at: {PUBLIC_URL}")
    print(f"Documentation available at: {PUBLIC_URL}/docs")
    print(f"Port: {PORT}, Host: {HOST}")
    uvicorn.run(app, host=HOST, port=PORT)
