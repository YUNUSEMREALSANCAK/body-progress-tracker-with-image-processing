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
        
        # Process images
        img1, _, results1 = processor.process_image(before_bytes)
        img2, _, results2 = processor.process_image(after_bytes)
        
        if not results1.pose_landmarks or not results2.pose_landmarks:
             raise HTTPException(status_code=400, detail="Could not detect pose in one of the images.")
             
        landmarks1 = processor.get_landmarks(results1)
        landmarks2 = processor.get_landmarks(results2)
        
        # Align
        aligned_img2 = processor.align_images(img1, landmarks1, img2, landmarks2)
        
        # Encode back to JPEG to return
        _, encoded_img = cv2.imencode('.jpg', aligned_img2)
        return Response(content=encoded_img.tobytes(), media_type="image/jpeg")
        
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
