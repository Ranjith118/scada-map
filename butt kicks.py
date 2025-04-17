import cv2
import mediapipe as mp
import numpy as np
import pyttsx3

# Initialize Mediapipe Pose module
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Initialize Text-to-Speech Engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 0.9)

# Helper function for voice feedback
def speak_feedback(text):
    engine.say(text)
    engine.runAndWait()

# Rep counters for left and right butt kicks
left_butt_kick_reps = 0
right_butt_kick_reps = 0
left_butt_kick_down = False
right_butt_kick_down = False

# Angle calculation function
def calculate_angle(a, b, c):
    a = np.array(a)  # First point
    b = np.array(b)  # Mid point
    c = np.array(c)  # End point

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle

# Start video capture
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the image to RGB
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False

    # Process the frame and find pose landmarks
    results = pose.process(image)

    # Convert back to BGR for rendering
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # Extract landmarks
    landmarks = results.pose_landmarks
    if landmarks:
        mp_drawing.draw_landmarks(image, landmarks, mp_pose.POSE_CONNECTIONS)

        # Extract key points for butt kicks (left and right legs)
        landmarks = results.pose_landmarks.landmark

        # Get coordinates for left leg
        left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
        left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
        left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

        # Get coordinates for right leg
        right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
        right_knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
        right_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

        # Calculate angles
        left_knee_angle = calculate_angle(left_hip, left_knee, left_ankle)
        right_knee_angle = calculate_angle(right_hip, right_knee, right_ankle)

        # Butt Kicks Detection for Left Leg
        if left_knee_angle < 50 and not left_butt_kick_down:
            left_butt_kick_reps += 1
            left_butt_kick_down = True
            speak_feedback(f"Left Butt Kick rep {left_butt_kick_reps} completed.")
        if left_knee_angle > 120:
            left_butt_kick_down = False

        # Butt Kicks Detection for Right Leg
        if right_knee_angle < 50 and not right_butt_kick_down:
            right_butt_kick_reps += 1
            right_butt_kick_down = True
            speak_feedback(f"Right Butt Kick rep {right_butt_kick_reps} completed.")
        if right_knee_angle > 120:
            right_butt_kick_down = False

    # Display rep counts for both sides
    cv2.putText(image, f'Left Butt Kicks: {left_butt_kick_reps}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(image, f'Right Butt Kicks: {right_butt_kick_reps}', (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Show the frame
    cv2.imshow('Butt Kicks Detection (Left & Right)', image)

    # Break on pressing 'q'
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
engine.stop()
