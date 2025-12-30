import mediapipe as mp
try:
    import mediapipe.python.solutions as solutions
    print("Found via direct import")
    print(solutions.pose)
except ImportError as e:
    print(f"ImportError: {e}")

try:
    from mediapipe import solutions
    print("Found via from import")
except ImportError as e:
    print(f"FromImportError: {e}")
except AttributeError as e:
    print(f"FromAttributeError: {e}")
