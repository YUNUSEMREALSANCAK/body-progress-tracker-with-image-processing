import mediapipe as mp
try:
    print(f"mp.solutions: {mp.solutions}")
except AttributeError:
    print("mp.solutions NOT found")

try:
    from mediapipe import solutions
    print(f"solutions imported: {solutions}")
except ImportError:
    print("from mediapipe import solutions FAILED")
