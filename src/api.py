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
