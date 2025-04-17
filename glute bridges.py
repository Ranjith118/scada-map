import cv2
import mediapipe as mp
import numpy as np
import pyttsx3
import threading

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 170)
engine.setProperty('volume', 0.9)

def speak_feedback(text):
    threading.Thread(target=_speak, args=(text,), daemon=True).start()

def _speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to calculate angle between three points
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    return 360.0 - angle if angle > 180.0 else angle

# Workout variables
reps = 0
stage = None
feedback_given = None
person_detected = False

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)

    person_detected = False

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

        # Check if key landmarks are present
        required_landmarks = [mp_pose.PoseLandmark.LEFT_SHOULDER.value,
                               mp_pose.PoseLandmark.LEFT_HIP.value,
                               mp_pose.PoseLandmark.LEFT_KNEE.value]

        if all(landmarks[l].visibility > 0.5 for l in required_landmarks):
            person_detected = True

            # Extract key points and convert to pixel coordinates
            height, width, _ = frame.shape
            left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * width,
                              landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * height]
            left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x * width,
                         landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y * height]
            left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x * width,
                          landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y * height]

            # Calculate hip angle specifically for glute bridge
            hip_angle = calculate_angle(left_shoulder, left_hip, left_knee)

            # Provide real-time feedback and count repetitions
            if hip_angle > 170:  # Fully extended hip angle
                if stage == "down":
                    reps += 1
                    speak_feedback(f"Reps: {reps}. Great job!")
                    stage = "up"
                    feedback_given = None
            if hip_angle < 140:  # Lowered hip angle for glute bridge
                stage = "down"

            # Provide only necessary feedback
            if hip_angle < 130 and feedback_given != "position":
                speak_feedback("Get into position. Lie flat with knees bent.")
                feedback_given = "position"
            elif 140 <= hip_angle < 170 and feedback_given != "lift":
                speak_feedback("Lift your hips higher!")
                feedback_given = "lift"
            elif hip_angle >= 170 and feedback_given != "hold":
                speak_feedback("Great form! Hold the position.")
                feedback_given = "hold"

    # Provide feedback if person is not in the frame
    if not person_detected and feedback_given != "no_person":
        speak_feedback("Person not detected. Please position yourself correctly in front of the camera.")
        feedback_given = "no_person"

    # Display rep count
    cv2.putText(frame, f"Reps: {reps}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow('Glute Bridge Workout', frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
