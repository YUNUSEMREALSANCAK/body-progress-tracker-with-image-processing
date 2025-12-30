from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from processor import ImageProcessor
import cv2
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

processor = ImageProcessor()

@app.get("/")
def read_root():
    return {"message": "BodyProgress Tracker API is running"}

@app.post("/align")
async def align_images_endpoint(before_image: UploadFile = File(...), after_image: UploadFile = File(...)):
    try:
        # Read bytes
        before_bytes = await before_image.read()
        after_bytes = await after_image.read()
        
        # 1. Process & Annotate Before Image
        # We need numpy image for processing
        nparr1 = np.frombuffer(before_bytes, np.uint8)
        img1 = cv2.imdecode(nparr1, cv2.IMREAD_COLOR)
        
        # Detect pose for fallback if needed (though annotate uses face mainly)
        # For full robustness we could call detect_image_numpy, but let's stick to annotate_image
        # which runs detection internally.
        annotated_before, _ = processor.annotate_image(img1)
        
        # 2. Process After Image (Just decode for alignment)
        nparr2 = np.frombuffer(after_bytes, np.uint8)
        img2 = cv2.imdecode(nparr2, cv2.IMREAD_COLOR)
        
        # 3. Align
        # New align_images takes (img1, img2) and handles detection internally
        aligned_img2 = processor.align_images(img1, img2)
        
        # 4. Annotate Aligned After Image
        annotated_after, _ = processor.annotate_image(aligned_img2)
        
        # 5. Encode both to Base64
        import base64
        
        _, buf_before = cv2.imencode('.jpg', annotated_before)
        b64_before = base64.b64encode(buf_before).decode('utf-8')
        
        _, buf_after = cv2.imencode('.jpg', annotated_after)
        b64_after = base64.b64encode(buf_after).decode('utf-8')
        
        return {
            "before": f"data:image/jpeg;base64,{b64_before}",
            "after": f"data:image/jpeg;base64,{b64_after}"
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
async def analyze_image_endpoint(image: UploadFile = File(...)):
    try:
        image_bytes = await image.read()
        annotated_img, data = processor.process_and_annotate(image_bytes)
        
        # Prepare headers with data (optional, but good for inspection)
        headers = {
            "X-Pupil-Distance-Px": str(data.get('pupil_distance_pixels', 0))
        }

        # Encode to JPEG
        _, encoded_img = cv2.imencode('.jpg', annotated_img)
        return Response(content=encoded_img.tobytes(), media_type="image/jpeg", headers=headers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
