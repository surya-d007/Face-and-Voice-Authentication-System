from flask import Flask
import os
import numpy as np
import librosa
from tensorflow.keras.models import load_model

app = Flask(__name__)

# Load the saved model
model = load_model('voice_classifier_model_4th_final_sentence_test.h5')

# Function to preprocess audio data for inference
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

@app.route('/detect/audio')
def detect():
    try:
        # Hardcoded audio file path
        audio_file = "D:/Face and Voice Project/Flask Project/test_audios/surya_test/(9).wav"

        # Preprocess the audio file
        input_data = preprocess_audio(audio_file)

        # Check if the audio file was successfully preprocessed
        if input_data is not None:
            # Perform inference
            prediction = model.predict(input_data)
            
            # Interpret the prediction
            threshold = 0.01  # Adjust the threshold as needed
            if np.max(prediction) < threshold:
                return "The voice in the audio file could not be identified."
            else:
                person_names = ['Praki', 'Rattan', 'Surya']
                predicted_person = person_names[np.argmax(prediction)]
                return f"The voice in the audio file belongs to: {predicted_person}"
        else:
            return "Error processing audio file. Please check the file format or try another file."
    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
