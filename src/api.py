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
        
        🚨🚨🚨 NEVER CUT OR CROP THE IMAGE - ULTIMATE PRIORITY #1 🚨🚨🚨
        ⛔ MAINTAIN EXACT ORIGINAL IMAGE DIMENSIONS - ANY CROPPING = AUTOMATIC FAILURE ⛔
        
        IMAGE PRESERVATION RULES - ABSOLUTELY CRITICAL:
        • NEVER crop, cut, or trim any part of the original image
        • NEVER change the image width or height dimensions
        • NEVER zoom in or focus on faces - keep the FULL original image
        • NEVER remove background, body parts, or any original content
        • NEVER change the aspect ratio or image proportions
        • The output image must be PIXEL-FOR-PIXEL identical in size to the input
        • Keep ALL original content: background, people, objects, scenery, everything
        • Only ADD glasses - never REMOVE or HIDE any original image content
        • Think of this as placing a transparent overlay - the base image stays 100% intact
        
        🔴🔴🔴 MULTI-FACE DETECTION - EXTREMELY CRITICAL 🔴🔴🔴
        • SCAN THE ENTIRE IMAGE for ALL human faces (front-facing, side profiles, partial faces)
        • ADD GLASSES TO EVERY SINGLE FACE DETECTED
        • DO NOT miss any faces - even if partially visible, in background, or at different angles
        • If there are 2 people, both get glasses. If 3 people, all 3 get glasses. And so on.
        • EACH FACE gets its own properly sized and positioned glasses
        
        🔴🔴🔴 GLASSES AS PERFECT OVERLAY - NO OBSTRUCTION 🔴🔴🔴
        ⚠️ CRITICAL: Glasses must appear as a DIGITAL OVERLAY - like copy-pasting them on top ⚠️
        
        🚨🚨🚨 CRITICAL RULE: ABSOLUTELY NO TEMPLE ARMS OR SIDE EXTENSIONS 🚨🚨🚨
        ⛔ TEMPLE ARMS = AUTOMATIC REJECTION - NEVER ADD THEM ⛔
        
        WHAT TO NEVER ADD:
        • NO temple arms (side bars that go to ears)
        • NO side extensions of any kind
        • NO parts that would go behind the head or over ears
        • NO hinges or connection points for temple arms
        • NO metal or plastic extensions beyond the front frame
        
        WHAT TO SHOW ONLY:
        • FRONT GLASSES PORTION ONLY: lenses + bridge + front frame rim
        • The glasses should look like they were "cut off" at the sides
        • Imagine the original glasses image with temple arms completely removed/cropped out
        • Only the part that sits directly in front of the eyes should be visible
        • Think: "front-facing glasses view only" - no side profile elements
        
        🎯 REALISTIC 3D GLASSES POSITIONING - NATURAL FACE CONFORMITY:
        • The glasses must appear to REST NATURALLY on the face following 3D facial contours
        • Glasses should CURVE and BEND naturally around the nose bridge and face shape
        • The bridge should appear to rest ON TOP OF the nose bridge (not floating above it)
        • Lenses should follow the natural curve of the eye sockets and cheekbones
        • CRITICAL: While conforming to face shape, the glasses design must remain FULLY VISIBLE
        • NO part of the nose should "cut through" or obstruct the glasses frame or lenses
        
        🔴🔴🔴 GLASSES PRESERVATION - ULTIMATE PRIORITY 🔴🔴🔴
        ⚠️ NEVER CHANGE THE GLASSES SHAPE OR COLORS - THIS IS ABSOLUTELY CRITICAL! ⚠️
        
        🚨 SHAPE PRESERVATION IS THE #1 PRIORITY - FAILURE TO PRESERVE SHAPE WILL RESULT IN REJECTION 🚨
        
        GLASSES PRESERVATION RULES - FOLLOW EXACTLY:
        • PRESERVE THE EXACT ORIGINAL SHAPE - NO MODIFICATIONS WHATSOEVER
        • If glasses are rectangular/square → KEEP THEM RECTANGULAR/SQUARE
        • If glasses are round/oval → KEEP THEM ROUND/OVAL
        • If glasses are cat-eye shaped → KEEP THE EXACT CAT-EYE SHAPE
        • If glasses have unique geometric patterns → PRESERVE EVERY DETAIL
        • DO NOT ROUND CORNERS if they are sharp
        • DO NOT SHARPEN CORNERS if they are rounded
        • DO NOT ALTER ANY CURVES, ANGLES, OR GEOMETRIC FEATURES
        • PRESERVE EXACT FRAME THICKNESS - do not make thinner or thicker
        • PRESERVE EXACT COLORS - no color shifts, brightness changes, or tinting
        • PRESERVE EXACT LENS TRANSPARENCY/OPACITY
        • PRESERVE ANY DECORATIVE ELEMENTS, PATTERNS, OR DETAILS
        • The glasses must be PIXEL-PERFECT IDENTICAL to the input - just positioned on each face
        • Think of this as COPY-PASTE operation - the glasses design cannot change AT ALL
        
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
           🎯 CRITICAL: Move glasses 20% HIGHER than typical positioning
           • Position glasses to sit ABOVE the eyes, not directly on them
           • TOP of glasses frame: Should be positioned ABOVE the natural eyebrow line
           • BRIDGE: Should rest on the UPPER part of the nose bridge (higher than normal)
           • EYES: Should be visible in the LOWER 80% of each lens (not center)
           • The glasses should appear to "hover" slightly above the natural eye position
           • BOTTOM of glasses: Should be at or slightly above the natural eye level
           • Think: "glasses positioned higher on the face" for a more natural look
           • Glasses should appear to be resting on the upper nose bridge with realistic depth
        
        3. HORIZONTAL POSITIONING (LEFT TO RIGHT) - PER FACE:
           • CENTER the glasses PERFECTLY on each face - this is critical for realism
           • ADJUSTED EYE POSITIONING: Each eye pupil should be in the LOWER portion of its lens
           • Since glasses are positioned 20% higher, eyes will naturally appear in lower part of lenses
           • Use the bridge of the nose as the central reference point for alignment
           • Scale glasses proportionally to face size while maintaining perfect centering
           • NO TEMPLE ARMS - only show the front glasses portion (lenses + bridge + front frame)
           • The glasses should be perfectly symmetrical on the face
           • If one eye is slightly higher than the other, adjust glasses angle to match natural face geometry
        
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
        
        🎯 REALISTIC 3D VISUALIZATION GUIDE - CRITICAL FOR SUCCESS:
        Think of this like the FRONT PART ONLY of real glasses that someone is wearing:
        
        VISUAL ANALOGY: Imagine looking at someone wearing glasses from directly in front of them:
        - You see: lenses + bridge + front frame rim (the part covering their eyes)
        - You DON'T see: temple arms going to their ears (those are behind/to the side)
        
        TECHNICAL IMPLEMENTATION:
        - Only the front glasses portion is visible (lenses + bridge + front frame)
        - ABSOLUTELY NO temple arms or side extensions toward the ears
        - The frame curves and conforms to the 3D shape of the face naturally
        - The bridge makes natural contact with the nose without being obstructed by it
        - Lenses follow the natural curve of the eye area and cheekbones
        - The glasses cast subtle, realistic shadows on the face
        - Despite the realistic 3D fit, the complete FRONT glasses design remains 100% visible
        - Each face gets its own perfectly fitted, naturally positioned front glasses
        - The effect looks like someone wearing glasses but you only see the front-facing view
        - Think: "glasses image with temple arms completely cropped out"
        
        🚨 CRITICAL SHAPE PRESERVATION REMINDER: The glasses shape must remain PIXEL-PERFECT IDENTICAL to the input image - even the slightest modification will result in failure 🚨
        
        🔴 FINAL CRITICAL REMINDERS - ABSOLUTE REQUIREMENTS 🔴
        1. 🎯 GLASSES SHAPE: Must be PIXEL-PERFECT IDENTICAL to input - NO changes allowed
        2. 🚨 NO TEMPLE ARMS: Only front portion visible - temple arms = automatic failure
        3. 🎯 EYE POSITIONING: Each pupil must be in LOWER portion of its lens (glasses 20% higher)
        4. 🔍 DETECT ALL FACES: Scan entire image, add glasses to every single face found
        5. 💼 PERFECT OVERLAY: Glasses float on face like digital sticker, no obstruction
        6. 🚨 NEVER CUT IMAGE: Preserve EVERY pixel of original - no cropping/trimming allowed
        
        🚨 AUTOMATIC REJECTION CRITERIA - ANY OF THESE WILL CAUSE FAILURE: 🚨
        ❌ IF GLASSES SHAPE IS CHANGED IN ANY WAY (rounded corners, altered curves, etc.)
        ❌ IF TEMPLE ARMS OR SIDE EXTENSIONS ARE ADDED
        ❌ IF EYES ARE NOT POSITIONED IN LOWER PORTION OF LENSES (glasses must be 20% higher)
        ❌ IF ANY FACE IN THE IMAGE IS MISSED
        ❌ IF NOSE OR OTHER FACIAL FEATURES "CUT THROUGH" THE GLASSES
        ❌ IF GLASSES COLORS OR TRANSPARENCY ARE MODIFIED
        ❌ IF IMAGE IS CROPPED, TRIMMED, ZOOMED, OR DIMENSIONS CHANGED IN ANY WAY
        ❌ IF ANY PART OF THE ORIGINAL IMAGE IS CUT OFF OR REMOVED
        ❌ IF BACKGROUND OR ANY ORIGINAL CONTENT IS HIDDEN OR MISSING
        
        🎆 SUCCESS CRITERIA - ALL OF THESE MUST BE TRUE:
        ✅ Glasses shape is 100% identical to input image
        ✅ NO temple arms visible - only front glasses portion
        ✅ Eyes positioned in lower portion of lenses (glasses 20% higher than normal)
        ✅ All faces in image have glasses applied
        ✅ Glasses appear as clean digital overlays
        ✅ Original image dimensions preserved exactly (same width × height)
        ✅ ALL original image content visible (background, people, objects, everything)
        ✅ No cropping, trimming, zooming, or cutting of any kind
        
        USE THE EXACT GLASSES FROM THE SECOND IMAGE AS PERFECT OVERLAYS ON ALL DETECTED FACES.
        
        🔥 TRIPLE CHECK BEFORE SUBMITTING: 🔥
        1. Are the glasses EXACTLY the same shape as the input? (No rounding, no straightening, no alterations)
        2. Are there NO temple arms or side extensions visible?
        3. Are the eyes positioned in the LOWER portion of each lens (glasses 20% higher than normal)?
        4. Did I find and apply glasses to ALL faces in the image?
        5. Do the glasses look like clean digital overlays without facial obstruction?
        6. Is the ENTIRE original image preserved with NO cropping or cutting?
        7. Are the image dimensions exactly the same as the input?
        
        IF ANY ANSWER IS "NO" - DO NOT SUBMIT, FIX THE ISSUE FIRST!"""
        
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
