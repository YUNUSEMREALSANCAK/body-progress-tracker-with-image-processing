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
        
        # 1. Process Before Image
        nparr1 = np.frombuffer(before_bytes, np.uint8)
        img1 = cv2.imdecode(nparr1, cv2.IMREAD_COLOR)
        
        # Create Overlay for Before (Yellow: 0, 255, 255) in BGR -> (0, 255, 255)
        # Processor colors are BGR.
        overlay1, _ = processor.create_annotation_overlay(img1, color=(0, 255, 255))
        
        # 2. Process After Image
        nparr2 = np.frombuffer(after_bytes, np.uint8)
        img2 = cv2.imdecode(nparr2, cv2.IMREAD_COLOR)
        
        # 3. Align
        aligned_img2 = processor.align_images(img1, img2)
        
        # 4. Create Overlay for Aligned After (Magenta: 255, 0, 255)
        overlay2, _ = processor.create_annotation_overlay(aligned_img2, color=(255, 0, 255))
        
        # 5. Encode all to Base64
        import base64
        
        def encode_img(img, ext='.jpg'):
            _, buf = cv2.imencode(ext, img)
            return base64.b64encode(buf).decode('utf-8')

        b64_before = encode_img(img1, '.jpg')
        b64_after = encode_img(aligned_img2, '.jpg')
        b64_overlay1 = encode_img(overlay1, '.png') # PNG for transparency
        b64_overlay2 = encode_img(overlay2, '.png')
        
        return {
            "before": f"data:image/jpeg;base64,{b64_before}",
            "after": f"data:image/jpeg;base64,{b64_after}",
            "beforeAnalysis": f"data:image/png;base64,{b64_overlay1}",
            "afterAnalysis": f"data:image/png;base64,{b64_overlay2}"
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
