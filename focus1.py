import cv2
import dlib
import numpy as np
from flask import Flask, Response
import os

app = Flask(__name__)

# Get the current directory of the script
current_directory = os.path.dirname(os.path.abspath(__file__))
# Construct the full path to the shape predictor file
predictor_path = os.path.join(current_directory, 'shape_predictor_68_face_landmarks.dat')

# Initialize the face detector and shape predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(predictor_path)

def detect_gaze(landmarks, frame, gray):
    left_eye_region = np.array([(landmarks.part(36).x, landmarks.part(36).y),
                                (landmarks.part(37).x, landmarks.part(37).y),
                                (landmarks.part(38).x, landmarks.part(38).y),
                                (landmarks.part(39).x, landmarks.part(39).y),
                                (landmarks.part(40).x, landmarks.part(40).y),
                                (landmarks.part(41).x, landmarks.part(41).y)], np.int32)
    right_eye_region = np.array([(landmarks.part(42).x, landmarks.part(42).y),
                                 (landmarks.part(43).x, landmarks.part(43).y),
                                 (landmarks.part(44).x, landmarks.part(44).y),
                                 (landmarks.part(45).x, landmarks.part(45).y),
                                 (landmarks.part(46).x, landmarks.part(46).y),
                                 (landmarks.part(47).x, landmarks.part(47).y)], np.int32)

    height, width = gray.shape
    mask = np.zeros((height, width), np.uint8)

    cv2.polylines(mask, [left_eye_region], True, 255, 2)
    cv2.fillPoly(mask, [left_eye_region], 255)
    left_eye = cv2.bitwise_and(gray, gray, mask=mask)

    cv2.polylines(mask, [right_eye_region], True, 255, 2)
    cv2.fillPoly(mask, [right_eye_region], 255)
    right_eye = cv2.bitwise_and(gray, gray, mask=mask)

    left_eye_center = (landmarks.part(36).x + landmarks.part(39).x) // 2, (landmarks.part(36).y + landmarks.part(39).y) // 2
    right_eye_center = (landmarks.part(42).x + landmarks.part(45).x) // 2, (landmarks.part(42).y + landmarks.part(45).y) // 2

    if left_eye_center[0] < width // 2:
        return "Focused"
    else:
        return "Not Focused"

def generate_frames():
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("Cannot open camera")
        return

    while True:
        success, frame = cap.read()
        if not success:
            print("Failed to capture image")
            break
        else:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)
            for face in faces:
                x, y, w, h = (face.left(), face.top(), face.width(), face.height())
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                landmarks = predictor(gray, face)
                for n in range(0, 68):
                    x = landmarks.part(n).x
                    y = landmarks.part(n).y
                    cv2.circle(frame, (x, y), 2, (0, 64, 100), -1)
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                print("Failed to encode frame")
                continue
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return "Gaze Detection Running"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
