import cv2
import numpy as np
import yaml

# Function to test the trained model
def test_face_model():
    # Initialize OpenCV's face detector
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Initialize face recognizer
    recognizer = cv2.face.LBPHFaceRecognizer_create()

    # Load the trained model
    recognizer.read('face_model.yml')

    # Load label_to_name mapping from the YAML file
    with open('label_to_name.yml', 'r') as file:
        label_to_name = yaml.safe_load(file)

    # Capture video from webcam
    cap = cv2.VideoCapture(0)

    # Continuously show webcam feed until interrupted
    while True:
        # Capture frame from webcam
        ret, frame = cap.read()

        # Display the frame
        cv2.imshow('Test Face Model', frame)

        # Check if the user pressed a key
        key = cv2.waitKey(1)

        # If the user pressed 'q' to quit or ' ' (spacebar) to capture the image
        if key == ord('q') or key == ord(' '):
            break

    # Release the webcam
    cap.release()

    # Convert the last captured frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the grayscale frame
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Iterate through detected faces and recognize them
    for (x, y, w, h) in faces:
        face_roi = gray[y:y + h, x:x + w]
        label, confidence = recognizer.predict(face_roi)
        if confidence < 100:
            name = label_to_name.get(label, "Unknown")
            print("Recognized as:", name)
        else:
            print("Unknown face")

    # Display the frame with recognized faces
    cv2.imshow('Test Face Model', frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_face_model()
