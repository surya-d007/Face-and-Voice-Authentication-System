import cv2
import numpy as np
import yaml
import time

# Function to enroll faces and train the model
def enroll_train_faces():
    # Initialize OpenCV's face detector
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Initialize face recognizer
    recognizer = cv2.face.LBPHFaceRecognizer_create()

    # Initialize lists to hold face samples and corresponding labels
    face_samples = []
    labels = []

    # Initialize dictionary to map labels to names
    label_to_name = {}

    # Function to capture and enroll faces
    def enroll_faces(label):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

            for (x, y, w, h) in faces:
                face_roi = gray[y:y + h, x:x + w]
                face_samples.append(face_roi)
                labels.append(label)

                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            cv2.imshow('Enroll Faces', frame)
            key = cv2.waitKey(1)
            if key == 32:  # Break the loop when spacebar (ASCII code 32) is pressed
                break

        cap.release()
        cv2.destroyAllWindows()



    # Enroll multiple people
    num_people_to_enroll = 2
    for i in range(num_people_to_enroll):
        name = input(f"Enter the name of person {i + 1}: ")
        label = i  # Assign a unique identifier for each person
        label_to_name[label] = name
        print(f"Enrolling faces for {name}...")
        enroll_faces(label)

    # Convert labels to np.int32
    labels = np.array(labels)
   

    start_time = time.time()
    print('start')

    # Train the model
    recognizer.train(face_samples, labels)

    end_time = time.time()
    # Calculate the time taken
    time_taken = end_time - start_time
    print("Time taken by the for loop:", time_taken, "seconds")


    # Save the trained model
    recognizer.save('face_model.yml')

    # Save label_to_name mapping to a separate YAML file
    with open('label_to_name.yml', 'w') as file:
        yaml.dump(label_to_name, file)

if __name__ == "__main__":
    enroll_train_faces()
