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
stage = "down"
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

        # Check if key landmarks are visible
        required_landmarks = [mp_pose.PoseLandmark.LEFT_HIP.value,
                               mp_pose.PoseLandmark.LEFT_KNEE.value,
                               mp_pose.PoseLandmark.LEFT_ANKLE.value]

        if all(landmarks[l].visibility > 0.5 for l in required_landmarks):
            person_detected = True

            # Extract key points and convert to pixel coordinates
            height, width, _ = frame.shape
            left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x * width,
                        landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y * height]
            left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x * width,
                         landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y * height]
            left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x * width,
                          landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y * height]

            # Calculate knee angle for leg raises
            leg_angle = calculate_angle(left_hip, left_knee, left_ankle)

            # Draw the key points and angle visualization
            cv2.circle(frame, tuple(np.int32(left_hip)), 5, (0, 0, 255), -1)
            cv2.circle(frame, tuple(np.int32(left_knee)), 5, (0, 255, 0), -1)
            cv2.circle(frame, tuple(np.int32(left_ankle)), 5, (255, 0, 0), -1)

            # Draw the angle text on the frame
            cv2.putText(frame, f"Angle: {int(leg_angle)} degrees", 
                        tuple(np.int32(left_knee)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            # Ensure a full repetition is counted only when the movement goes down -> up -> down
            if leg_angle > 150:  # Fully extended leg (UP)
                if stage == "down":
                    stage = "up"
                feedback_given = None

            elif leg_angle < 60:  # Lowered position (DOWN)
                if stage == "up":
                    reps += 1
                    speak_feedback(f"Reps: {reps}. Great job!")
                    stage = "down"
                feedback_given = None

            # Provide only necessary feedback
            if leg_angle < 60 and feedback_given != "position":
                speak_feedback("Ensure your leg is straight in the lowered position.")
                feedback_given = "position"
            elif 70 <= leg_angle < 150 and feedback_given != "lift":
                speak_feedback("Raise your leg higher!")
                feedback_given = "lift"
            elif leg_angle >= 150 and feedback_given != "hold":
                speak_feedback("Great form! Hold it steady.")
                feedback_given = "hold"

    # Provide feedback if person is not in the frame
    if not person_detected and feedback_given != "no_person":
        speak_feedback("Person not detected. Please position yourself correctly in front of the camera.")
        feedback_given = "no_person"

    # Display rep count and workout stage
    cv2.putText(frame, f"Reps: {reps}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"Stage: {stage}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow('Leg Raise Workout', frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
