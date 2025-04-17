import cv2
import numpy as np
import mediapipe as mp
import pyttsx3
import time

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.3, min_tracking_confidence=0.3)
mp_drawing = mp.solutions.drawing_utils

# Initialize Text-to-Speech
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 0.9)

# Feedback and Count Variables
right_knee_raises_count = 0
left_knee_raises_count = 0
right_knee_up = False
left_knee_up = False

# Helper function for voice feedback
def speak_feedback(text):
    engine.say(text)
    engine.runAndWait()

# Function to calculate angle between three points
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    return 360 - angle if angle > 180.0 else angle

# Open webcam
cap = cv2.VideoCapture(0)

speak_feedback("Starting knee raises detection. Please begin your exercise.")

# Increase frame skip for faster processing
frame_skip = 5  # Skip every 5 frames for faster processing
frame_count = 0

# Reduce image size further (optional)
resize_width = 320
resize_height = 180

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    if frame_count % frame_skip != 0:
        continue

    # Resize frame for faster processing (optional)
    frame = cv2.resize(frame, (resize_width, resize_height))
    
    # Recolor frame to RGB
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False

    # Pose detection
    results = pose.process(image)

    # Recolor back to BGR
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    try:
        landmarks = results.pose_landmarks.landmark

        # Extract relevant landmarks for both legs
        right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                     landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
        right_knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                      landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
        right_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                       landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

        left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                    landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
        left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
        left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                      landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

        # Calculate knee angles
        right_knee_angle = calculate_angle(right_hip, right_knee, right_ankle)
        left_knee_angle = calculate_angle(left_hip, left_knee, left_ankle)

        # Right knee raise detection
        if right_knee_angle > 160:
            right_knee_up = False
        if right_knee_angle < 100 and not right_knee_up:
            right_knee_raises_count += 1
            right_knee_up = True
            if right_knee_raises_count % 5 == 0:  # Provide feedback after every 5 reps
                speak_feedback(f"Good job! Right knee repetition {right_knee_raises_count}")

        # Left knee raise detection
        if left_knee_angle > 160:
            left_knee_up = False
        if left_knee_angle < 100 and not left_knee_up:
            left_knee_raises_count += 1
            left_knee_up = True
            if left_knee_raises_count % 5 == 0:  # Provide feedback after every 5 reps
                speak_feedback(f"Good job! Left knee repetition {left_knee_raises_count}")

    except Exception as e:
        pass

    # Display rep counts
    cv2.putText(image, f'Right Reps: {right_knee_raises_count}', 
                (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(image, f'Left Reps: {left_knee_raises_count}', 
                (50, 160), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Render pose landmarks
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # Show video feed
    cv2.imshow('Knee Raises Counter', image)

    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
speak_feedback("Exercise session ended. Great job!")
