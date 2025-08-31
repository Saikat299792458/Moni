import numpy as np
import cv2
import os

def find_smallest_black_strip_width(frame):
    # Crop to central vertical region (ROI)
    frame_height, frame_width = frame.shape[:2]
    ROI_left = frame_width // 2 - 25
    ROI_right = frame_width // 2 + 25
    roi = frame[:, ROI_left:ROI_right]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    # Use a calibrated threshold for black strips
    _, binary = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    heights = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        # Filter out small noise, only consider strips with reasonable height
        if h > 5 and w > 10:
            heights.append(h)
    print(f"Detected strip heights: {heights}")
    if heights:
        min_height = min(heights)
        print(f"Smallest black strip height: {min_height} pixels")
    else:
        print("No black strips detected.")

# Set paths
video_path = "1us.mp4"  # Change to your desired video file
snaps_dir = "Snaps"

# Create Snaps directory if it doesn't exist
os.makedirs(snaps_dir, exist_ok=True)

cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("Error: Cannot open video.")
    exit()

frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
current_frame = 0

while True:
    cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
    ret, frame = cap.read()
    if not ret:
        print("End of video or cannot read frame.")
        break
    display_text = f"Frame {current_frame+1}/{frame_count}"
    frame_disp = frame.copy()
    cv2.putText(frame_disp, display_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
    cv2.imshow("Video Frame Navigator", frame_disp)
    key = cv2.waitKey(0) & 0xFF
    if key == 27:  # ESC to exit
        break
    elif key == ord('s') or key == ord('S'):
        snap_path = os.path.join(snaps_dir, f"frame_{current_frame+1}.png")
        cv2.imwrite(snap_path, frame)
        print(f"Saved: {snap_path}")
    elif key == ord('a'):  # Left navigation
        current_frame = max(0, current_frame - 1)
    elif key == ord('d'):  # Right navigation
        current_frame = min(frame_count - 1, current_frame + 1)
    elif key == ord('w'):
        find_smallest_black_strip_width(frame)

cap.release()
cv2.destroyAllWindows()
