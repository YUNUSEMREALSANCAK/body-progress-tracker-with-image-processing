import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import os

from rembg import remove, new_session

class ImageProcessor:
    def __init__(self):
        # Pose Detector
        pose_model_path = os.path.join(os.path.dirname(__file__), 'pose_landmarker_lite.task')
        pose_base_options = python.BaseOptions(model_asset_path=pose_model_path)
        pose_options = vision.PoseLandmarkerOptions(
            base_options=pose_base_options,
            output_segmentation_masks=False)
        self.detector = vision.PoseLandmarker.create_from_options(pose_options)

        # Face Detector (Tasks API)
        face_model_path = os.path.join(os.path.dirname(__file__), 'face_landmarker.task')
        face_base_options = python.BaseOptions(model_asset_path=face_model_path)
        face_options = vision.FaceLandmarkerOptions(
            base_options=face_base_options,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
            num_faces=1)
        self.face_landmarker = vision.FaceLandmarker.create_from_options(face_options)

        # Initialize rembg session
        self.rembg_session = new_session("u2netp")

    def process_image(self, image_bytes):
        print("Processing image request...")
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image is None:
            print("Error: Could not decode image")
            raise ValueError("Could not decode image")
        
        print(f"Image shape: {image.shape}")
        
        # Convert to RGB and then to mp.Image
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        
        print("Running detector...")
        # Detect
        detection_result = self.detector.detect(mp_image)
        print("Detection complete.")
        
        return image, mp_image, detection_result

    def process_and_annotate(self, image_bytes):
        image, mp_image, result = self.process_image(image_bytes)
        output_image = image.copy()
        data = {}
        h, w, _ = image.shape

        # 1. Use rembg for Segmentation / Body Outline
        print("Running rembg...")
        try:
             # rembg expects bytes or PIL image. We have bytes or numpy.
             # Using bytes directly is efficient.
             # Use the pre-initialized session
             result_bg_removed = remove(image_bytes, session=self.rembg_session)
             
             # Convert result to numpy
             nparr_bg = np.frombuffer(result_bg_removed, np.uint8)
             img_bg_removed = cv2.imdecode(nparr_bg, cv2.IMREAD_UNCHANGED) # RGBA
             
             if img_bg_removed is not None:
                 # Extract Alpha channel as mask
                 alpha_channel = img_bg_removed[:, :, 3]
                 
                 # Resize if needed (rembg shouldn't resize but good to be safe)
                 if alpha_channel.shape[:2] != (h, w):
                     alpha_channel = cv2.resize(alpha_channel, (w, h))

                 # Threshold to get binary mask
                 _, binary_mask = cv2.threshold(alpha_channel, 127, 255, cv2.THRESH_BINARY)
                 
                 # Find contours
                 contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                 
                 # Draw contours (Body Outline)
                 # Using thinner line for precision, yellow
                 cv2.drawContours(output_image, contours, -1, (0, 255, 255), 2)
        except Exception as e:
            print(f"Rembg error: {e}")

        # 2. Draw Eyes and Calculate IPD
        # Use FaceLandmarker (Tasks API) for high precision iris detection
        print("Running face detector...")
        face_results = self.face_landmarker.detect(mp_image)
        
        left_eye_loc = None
        right_eye_loc = None

        if face_results.face_landmarks:
             # Get first face
             face_landmarks = face_results.face_landmarks[0]
             
             # Iris landmarks (Refined)
             # 468: Left Iris Center
             # 473: Right Iris Center
             left_iris = face_landmarks[468]
             right_iris = face_landmarks[473]
             
             left_eye_loc = (int(left_iris.x * w), int(left_iris.y * h))
             right_eye_loc = (int(right_iris.x * w), int(right_iris.y * h))
        
        # Fallback to Pose if FaceMesh fails
        elif result.pose_landmarks:
            landmarks = result.pose_landmarks[0]
            left_eye = landmarks[2]
            right_eye = landmarks[5]
            left_eye_loc = (int(left_eye.x * w), int(left_eye.y * h))
            right_eye_loc = (int(right_eye.x * w), int(right_eye.y * h))

        if left_eye_loc and right_eye_loc:
            # Calculate Distance
            dist_px = np.linalg.norm(np.array(left_eye_loc) - np.array(right_eye_loc))
            data['pupil_distance_pixels'] = round(dist_px, 2)
            
            # Draw Eyes (Red dots strictly inside the pupil center)
            # Size 2 for precise point
            cv2.circle(output_image, left_eye_loc, 3, (0, 0, 255), -1) 
            cv2.circle(output_image, right_eye_loc, 3, (0, 0, 255), -1)
            
            # Draw Line (Blue)
            cv2.line(output_image, left_eye_loc, right_eye_loc, (255, 0, 0), 1) 
            
            # Text for distance
            cv2.putText(output_image, f"IPD: {dist_px:.1f}px", 
                        (min(left_eye_loc[0], right_eye_loc[0]), min(left_eye_loc[1], right_eye_loc[1]) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        return output_image, data

    def get_landmarks(self, results):
        if not results.pose_landmarks:
            return None
        
        # Get first detected person
        lm = results.pose_landmarks[0]
        
        # Indices for landmarks (BlazePose)
        # 11: left_shoulder, 12: right_shoulder, 0: nose
        # Tasks API uses the same index mapping as legacy
        
        landmarks = {}
        landmarks['nose'] = (lm[0].x, lm[0].y)
        landmarks['left_shoulder'] = (lm[11].x, lm[11].y)
        landmarks['right_shoulder'] = (lm[12].x, lm[12].y)
        
        return landmarks

    def align_images(self, img1, landmarks1, img2, landmarks2):
        # Calculate scale based on shoulder width
        width1 = np.linalg.norm(np.array(landmarks1['left_shoulder']) - np.array(landmarks1['right_shoulder']))
        width2 = np.linalg.norm(np.array(landmarks2['left_shoulder']) - np.array(landmarks2['right_shoulder']))
        
        if width2 == 0:
            return img2 
            
        scale_factor = width1 / width2
        
        # Resize img2
        height, width = img2.shape[:2]
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        img2_resized = cv2.resize(img2, (new_width, new_height))
        
        # Calculate translation (move img2 so nose matches img1)
        # Need to re-calculate pixel positions for resized img2
        nose1_pixel = (int(landmarks1['nose'][0] * img1.shape[1]), int(landmarks1['nose'][1] * img1.shape[0]))
        nose2_pixel = (int(landmarks2['nose'][0] * new_width), int(landmarks2['nose'][1] * new_height))
        
        dx = nose1_pixel[0] - nose2_pixel[0]
        dy = nose1_pixel[1] - nose2_pixel[1]
        
        M = np.float32([[1, 0, dx], [0, 1, dy]])
        
        # Use warpAffine with borderMode to handle edge cases
        aligned_img2 = cv2.warpAffine(img2_resized, M, (img1.shape[1], img1.shape[0]))
        
        return aligned_img2
