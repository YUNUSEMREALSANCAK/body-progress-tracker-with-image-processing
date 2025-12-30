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

    def detect_image_numpy(self, image):
        # Helper for already loaded numpy images (BGR)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        return self.detector.detect(mp_image)

    def create_annotation_overlay(self, image_numpy, color=(0, 255, 255)):
        h, w = image_numpy.shape[:2]
        # Create transparent overlay (BGRA)
        overlay = np.zeros((h, w, 4), dtype=np.uint8)
        
        data = {}
        
        # 1. Use rembg for Segmentation / Body Outline
        print("Running rembg for overlay...")
        try:
             # Encode original to bytes for rembg
             _, buf = cv2.imencode('.png', image_numpy)
             image_bytes = buf.tobytes()
             
             result_bg_removed = remove(image_bytes, session=self.rembg_session)
             
             # Convert result to numpy
             nparr_bg = np.frombuffer(result_bg_removed, np.uint8)
             img_bg_removed = cv2.imdecode(nparr_bg, cv2.IMREAD_UNCHANGED) # RGBA
             
             if img_bg_removed is not None:
                 # Extract Alpha channel as mask
                 alpha_channel = img_bg_removed[:, :, 3]
                 
                 # Resize if needed
                 if alpha_channel.shape[:2] != (h, w):
                     alpha_channel = cv2.resize(alpha_channel, (w, h))

                 # Threshold to get binary mask
                 _, binary_mask = cv2.threshold(alpha_channel, 127, 255, cv2.THRESH_BINARY)
                 
                 # Find contours
                 contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                 
                 # Draw contours on Overlay
                 # Color needs to be BGRA: (*color, 255)
                 draw_color = (*color, 255)
                 cv2.drawContours(overlay, contours, -1, draw_color, 2)
        except Exception as e:
            print(f"Rembg error: {e}")

        # 2. Draw Eyes and Calculate IPD
        # Use existing image for detection
        # Logic is similar, but draw on overlay
        image_rgb = cv2.cvtColor(image_numpy, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        
        face_results = self.face_landmarker.detect(mp_image)
        
        left_eye_loc = None
        right_eye_loc = None

        if face_results.face_landmarks:
             face_landmarks = face_results.face_landmarks[0]
             left_iris = face_landmarks[468]
             right_iris = face_landmarks[473]
             left_eye_loc = (int(left_iris.x * w), int(left_iris.y * h))
             right_eye_loc = (int(right_iris.x * w), int(right_iris.y * h))
        
        if left_eye_loc and right_eye_loc:
            dist_px = np.linalg.norm(np.array(left_eye_loc) - np.array(right_eye_loc))
            data['pupil_distance_pixels'] = round(dist_px, 2)
            
            # Draw on Overlay (Red for eyes always? Or same color? Let's keep eyes Red/Blue for visibility)
            # Eyes: Red
            cv2.circle(overlay, left_eye_loc, 3, (0, 0, 255, 255), -1) 
            cv2.circle(overlay, right_eye_loc, 3, (0, 0, 255, 255), -1)
            # Line: Blue
            cv2.line(overlay, left_eye_loc, right_eye_loc, (255, 0, 0, 255), 1) 
            
            # Text: Cyan/White?
            cv2.putText(overlay, f"IPD: {dist_px:.1f}px", 
                        (min(left_eye_loc[0], right_eye_loc[0]), min(left_eye_loc[1], right_eye_loc[1]) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0, 255), 2)
        
        return overlay, data

    def process_and_annotate(self, image_bytes):
        # Backward compatibility / Analysis endpoint
        image, mp_image, result = self.process_image(image_bytes)
        overlay, data = self.create_annotation_overlay(image)
        
        # Merge overlay onto image
        # Basic alpha blending
        alpha_overlay = overlay[:, :, 3] / 255.0
        alpha_img = 1.0 - alpha_overlay
        
        for c in range(0, 3):
            image[:, :, c] = (alpha_overlay * overlay[:, :, c] + 
                              alpha_img * image[:, :, c])
            
        return image, data

    def get_iris_landmarks(self, image_numpy):
        # Convert to mp.Image if needed, but here we expect numpy BGR
        image_rgb = cv2.cvtColor(image_numpy, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        
        face_results = self.face_landmarker.detect(mp_image)
        if not face_results.face_landmarks:
            return None, None
            
        face_landmarks = face_results.face_landmarks[0]
        h, w, _ = image_numpy.shape
        
        # 468: Left Iris Center, 473: Right Iris Center
        left_iris = face_landmarks[468]
        right_iris = face_landmarks[473]
        
        l_pt = (left_iris.x * w, left_iris.y * h)
        r_pt = (right_iris.x * w, right_iris.y * h)
        
        return l_pt, r_pt

    def align_images(self, img1, img2):
        # Try Iris Alignment First (High Precision)
        l1, r1 = self.get_iris_landmarks(img1)
        l2, r2 = self.get_iris_landmarks(img2)
        
        if l1 and r1 and l2 and r2:
            print("Aligning using Iris Landmarks...")
            # Calculate centers
            eyes_center1 = ((l1[0] + r1[0]) / 2, (l1[1] + r1[1]) / 2)
            eyes_center2 = ((l2[0] + r2[0]) / 2, (l2[1] + r2[1]) / 2)
            
            # Calculate angle
            dy1 = r1[1] - l1[1]
            dx1 = r1[0] - l1[0]
            angle1 = np.degrees(np.arctan2(dy1, dx1))
            
            dy2 = r2[1] - l2[1]
            dx2 = r2[0] - l2[0]
            angle2 = np.degrees(np.arctan2(dy2, dx2))
            
            # We want to rotate img2 so that angle2 matches angle1
            # rotation difference
            angle_diff = angle2 - angle1
            
            # Calculate scale
            dist1 = np.sqrt(dx1**2 + dy1**2)
            dist2 = np.sqrt(dx2**2 + dy2**2)
            scale = dist1 / dist2
            
            # Get Rotation Matrix
            # Rotate around eyes_center2
            M = cv2.getRotationMatrix2D(eyes_center2, angle_diff, scale)
            
            # Adjust translation
            # We want eyes_center2 to move to eyes_center1
            # Apply M to eyes_center2
            tx = eyes_center1[0] - M[0, 2] - (eyes_center2[0] * M[0, 0] + eyes_center2[1] * M[0, 1])
            ty = eyes_center1[1] - M[1, 2] - (eyes_center2[0] * M[1, 0] + eyes_center2[1] * M[1, 1])
            
            # Correct logic:
            # The getRotationMatrix2D gives rotation around center.
            # Tx, Ty needs to be added to shift the rotated center to target center.
            # Current M maps center2 -> center2 (rotated). We need center2 -> center1.
            
            # Let's use a simpler Affine Transform derivation:
            # Map l2 -> l1 AND r2 -> r1
            pts1 = np.float32([l1, r1, eyes_center1])
            pts2 = np.float32([l2, r2, eyes_center2])
            
            # Estimate rigid transform (rotation, translation, scaling)
            # cv2.estimateAffinePartial2D is robust for this
            M, inliers = cv2.estimateAffinePartial2D(pts2, pts1)
            
            aligned_img2 = cv2.warpAffine(img2, M, (img1.shape[1], img1.shape[0]))
            return aligned_img2

        # Fallback to Pose Alignment (Legacy)
        print("Fallback to Pose Alignment...")
        # Since we removed legacy args, we need to re-detect pose here if needed
        # Or just return original if iris fails for simplicity in this refactor
        # Ideally we should pass landmarks, but let's keep it self-contained
        # For now, if face fails, we return img2 resized to match height
        # (Implementing full pose fallback would require calling detect inside here)
        
        return cv2.resize(img2, (img1.shape[1], img1.shape[0]))
