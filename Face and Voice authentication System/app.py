import cv2
import numpy as np
import yaml
from flask import Flask, request, jsonify



import os
import numpy as np
import librosa
from tensorflow.keras.models import load_model


#model = load_model('model2.h5')
#model = load_model('model3.h5')
model = load_model('111model8.h5')
#model = load_model('model7.h5')
#model = load_model('model8.h5')
#model = load_model('voice_classifier_model_4th_final_sentence_test.h5')

app = Flask(__name__)

# Initialize OpenCV's face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Initialize face recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()

# Load the trained model
recognizer.read('face_model.yml')

# Load label_to_name mapping from the YAML file
with open('label_to_name.yml', 'r') as file:
    label_to_name = yaml.safe_load(file)


def detect_faces(image_path):
    # Read the image
    image = cv2.imread(image_path)
    
    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces in the grayscale image
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    detected_faces = []

    # Iterate through detected faces and recognize them
    for (x, y, w, h) in faces:
        face_roi = gray[y:y + h, x:x + w]
        label, confidence = recognizer.predict(face_roi)
        if confidence < 100:
            name = label_to_name.get(label, "Unknown")
            detected_faces.append(str(name))
            break  # Convert face names to strings

    return detected_faces

@app.route('/detect/image/<image_name>', methods=['GET'])
def detect_face_in_image(image_name):
    #image_path = f'pictures/{image_name}'
    image_path = f'server/images/{image_name}'
    detected_faces = detect_faces(image_path)
    print(image_name , "  " , detected_faces )
    return jsonify(detected_faces)


def preprocess_audio(audio_file, sr=22050, duration=3, n_mfcc=40, max_frames=40):
    try:
        # Load audio file
        y, sr = librosa.load(audio_file, sr=sr, duration=duration)

        # Extract MFCCs
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)

        # Pad or truncate the MFCCs to a fixed number of frames
        if mfccs.shape[1] < max_frames:
            mfccs = np.pad(mfccs, ((0, 0), (0, max_frames - mfccs.shape[1])), mode='constant')
        else:
            mfccs = mfccs[:, :max_frames]

        # Reshape to match the input shape expected by the model
        mfccs = mfccs.reshape((1, mfccs.shape[0], mfccs.shape[1], 1))

        return mfccs
    except Exception as e:
        print(f"Error processing audio file {audio_file}: {str(e)}")
        return None



import json  # Import the json module

@app.route('/detect/audio')
def detect():
    try:
        # Hardcoded audio file path
        import os

        audio_file = os.path.join(os.getcwd(), 'server', 'audio', 'sampleaudio.wav')
        print(audio_file)

        #audio_file = "D:/Users/surya/Desktop/face - Copy/server/audio/sampleaudio.wav"
        #audio_file = "D:/Users/surya/Downloads/my_favourite_sport.wav"
    
        # Preprocess the audio file
        input_data = preprocess_audio(audio_file)

        # Check if the audio file was successfully preprocessed
        if input_data is not None:
            # Perform inference
            prediction = model.predict(input_data).tolist()  # Convert NumPy array to list
            
            # Interpret the prediction
            threshold = 0.01  # Adjust the threshold as needed
            if np.max(prediction) < threshold:
                return "The voice in the audio file could not be identified."
            else:
                person_names = ['Praki', 'Rattan', 'Surya']
                predicted_person = person_names[np.argmax(prediction)]
                #return f"The voice in the audio file belongs to: {predicted_person}"
                print(jsonify(predicted_person))
                return jsonify(predicted_person)
        else:
            return "Error processing audio file. Please check the file format or try another file."
    except Exception as e:
        return f"An error occurred: {str(e)}"





if __name__ == "__main__":
    app.run(debug=True)
