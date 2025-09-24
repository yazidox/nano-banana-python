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
        
        # Enhanced prompt for perfect glasses overlay with maximum eye visibility
        prompt = """CRITICAL INSTRUCTION: Overlay ONLY the front portion of glasses from Image 2 onto all faces in Image 1.

🚨 ABSOLUTE REQUIREMENTS - FAILURE TO FOLLOW = COMPLETE FAILURE:

1. ABSOLUTELY NO TEMPLE BARS/ARMS/SIDE EXTENSIONS - THIS IS CRITICAL
   - Show ONLY: lenses + nose bridge + front rim (NOTHING ELSE)
   - NEVER EVER add: temple arms, ear pieces, side bars, hinges, extensions
   - DO NOT draw lines going to the ears - FORBIDDEN
   - DO NOT add any parts that weren't in the original glasses image
   - Even if it looks "incomplete" or "unrealistic", DO NOT add temple arms
   - The glasses should appear to "float" on the face rather than have temple arms
   - If you feel tempted to add temple arms for realism - DON'T DO IT
   - STOP ADDING TEMPLE BARS - IT'S RUINING THE RESULTS
   - NO SIDE EXTENSIONS MEANS NO SIDE EXTENSIONS - PERIOD

2. EYES MUST ALWAYS BE CRYSTAL CLEAR AND VISIBLE
   - Eyes MUST be completely unobstructed and clearly visible
   - NEVER hide, cover, or darken any part of the eyes
   - Position glasses BELOW the eyebrows, not covering them
   - Ensure pupils, iris, and entire eye area remain fully visible
   - If glasses would cover eyes, position them lower on the nose
   - Eyes should look exactly as they do in the original image

3. NO VISUAL EFFECTS ON GLASSES
   - Keep glasses EXACTLY as they appear in Image 2
   - NO shadows, reflections, or transparency effects
   - NO glass/lens effects, tinting, or opacity changes
   - NO lighting effects, glare, or shine on lenses
   - Glasses should appear flat and identical to the source image
   - Maintain original colors, patterns, and textures perfectly

4. PERFECT POSITIONING - GLASSES ALIGNED WITH EYES (CRITICAL)
   - PRIMARY RULE: Position glasses based on EYE LOCATION, not nose location
   - Each lens must be centered ABOVE the corresponding eye
   - Glasses bridge should connect the two lenses above the nose bridge
   - Eyes must be positioned in the CENTER of each lens area
   - If positioning conflicts: PRIORITIZE eye alignment over nose placement
   - Glasses must sit ON TOP of the nose bridge (not inside or middle)
   - Position glasses as an OVERLAY on the nose surface
   - The nose should be visible UNDER the glasses bridge
   - Glasses appear to rest ON the nose, not embedded IN the nose
   - Follow face perspective (tilt, angle, rotation)
   - No floating or misaligned glasses
   - Maintain original image dimensions
   - FAILURE CONDITION: If eyes are not properly centered in lenses = FAIL

5. PRESERVE ORIGINAL IMAGES & NO NEW ELEMENTS
   - Keep exact glasses appearance from Image 2 (no modifications)
   - NEVER add elements that don't exist in the original glasses image
   - If the original glasses don't have temple arms, DON'T ADD THEM
   - Only use the exact elements visible in the glasses source image
   - Do not crop, resize, or modify the base image
   - Process ALL faces in the image
   - Background and all other elements remain untouched

IMPLEMENTATION PRIORITY:
1. Extract ONLY the front view of glasses (no side parts, NO TEMPLE ARMS)
2. LOCATE BOTH EYES in the image first
3. Position each lens to be centered ABOVE each eye
4. Align glasses bridge to connect lenses above nose bridge
5. Scale appropriately so eyes are centered in lens areas
6. Apply perspective transformation while keeping glasses flat/opaque
7. Ensure MAXIMUM eye visibility - eyes centered in lenses
8. Keep glasses appearance 100% identical to source image
9. FINAL CHECK: Verify absolutely NO lines extend toward ears

CRITICAL SUCCESS CRITERIA:
- Every eye in the image remains completely visible and clear
- Each eye is CENTERED within its corresponding lens area
- Glasses are positioned based on EYE LOCATION, not just nose
- Glasses look exactly like the source image (no effects)
- ZERO temple arms, side extensions, or ear pieces - NONE WHATSOEVER
- No lines or elements going toward the ears
- Natural positioning on nose bridge with eye-based alignment
- Glasses appear as front-view only (like a sticker)

TEMPLE ARM CHECK: Before finishing, verify NO lines extend from glasses toward ears.

REMEMBER: 
1. Eye visibility is the absolute top priority
2. Position glasses based on EYE LOCATIONS - find eyes first, then position lenses
3. Each eye must be CENTERED in its lens area
4. NEVER add temple arms even if it looks incomplete
5. Position glasses ON TOP of nose as overlay, not embedded in nose
6. The glasses should look like a "front view cutout" placed on the face
7. STOP ADDING TEMPLE BARS - THEY ARE FORBIDDEN

POSITIONING WORKFLOW:
Step 1: Identify both eyes in the face
Step 2: Center each lens over each eye
Step 3: Connect lenses with bridge over nose
Step 4: Verify eyes are centered in lens areas

FINAL TEMPLE BAR CHECK: Before completing, scan the entire image for ANY lines extending from glasses toward ears. If found, REMOVE THEM."""
        
        contents.append(genai.types.Part.from_text(text=prompt))
        
        generate_content_config = types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            temperature=0.7,  # Low temperature for more consistent results
            top_p=0.1,       # Reduce randomness in token selection
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
