# -*- coding: utf-8 -*-
"""intel_1.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Y62qpXhPkVAn6spM1DCf_znxi7yVipN4
"""



import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Flatten, Dense
import os
from google.colab import files
from google.colab.patches import cv2_imshow

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# 1. Data Preprocessing
def preprocess_frame(frame):
    resized = cv2.resize(frame, (224, 224))
    normalized = resized / 255.0
    return normalized

# 2. Model Implementation
def create_entity_recognition_model():
    model = Sequential([
        Input(shape=(224, 224, 3)),
        Conv2D(32, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Conv2D(64, (3, 3), activation='relu'),
        Flatten(),
        Dense(64, activation='relu'),
        Dense(4, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def create_activity_recognition_model():
    model = Sequential([
        Input(shape=(224, 224, 3)),
        Conv2D(32, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Conv2D(64, (3, 3), activation='relu'),
        Flatten(),
        Dense(64, activation='relu'),
        Dense(3, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

# 3. Video File Validation
def is_valid_video(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File does not exist at path: {file_path}")
        return False

    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        print(f"Error: Unable to open video file: {file_path}")
        return False

    ret, frame = cap.read()
    if not ret:
        print(f"Error: Unable to read frames from video file: {file_path}")
        return False

    cap.release()
    return True

# 4. Draw grid overlay
def draw_grid(frame, cell_size=50, major_cell_size=150):
    h, w = frame.shape[:2]

    # Draw minor grid lines
    for x in range(0, w, cell_size):
        cv2.line(frame, (x, 0), (x, h), (0, 255, 255), 1)
    for y in range(0, h, cell_size):
        cv2.line(frame, (0, y), (w, y), (0, 255, 255), 1)

    # Draw major grid lines
    for x in range(0, w, major_cell_size):
        cv2.line(frame, (x, 0), (x, h), (0, 255, 0), 2)
    for y in range(0, h, major_cell_size):
        cv2.line(frame, (0, y), (w, y), (0, 255, 0), 2)

# 5. Video Processing Pipeline
def process_video(input_path, entity_model, activity_model):
    if not is_valid_video(input_path):
        return

    cap = cv2.VideoCapture(input_path)

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        processed_frame = preprocess_frame(frame)
        entity_prediction = entity_model.predict(np.expand_dims(processed_frame, axis=0), verbose=0)
        activity_prediction = activity_model.predict(np.expand_dims(processed_frame, axis=0), verbose=0)

        entity, activity = analyze_frame(entity_prediction, activity_prediction)

        # Draw bounding boxes
        h, w = frame.shape[:2]
        cv2.rectangle(frame, (int(w*0.3), int(h*0.3)), (int(w*0.7), int(h*0.7)), (0, 0, 255), 2)

        # Add text to the frame
        cv2.putText(frame, f"Person: {entity}", (int(w*0.3), int(h*0.3)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # Draw grid overlay
        draw_grid(frame)

        # Display the frame
        cv2_imshow(frame)

        print(f"Frame {frame_count}: Detected: {entity} - Activity: {activity}")

        alert = generate_alert(entity, activity)
        if alert:
            print(f"Frame {frame_count}: {alert}")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# 6. Real-time Analysis System
def analyze_frame(entity_prediction, activity_prediction):
    entities = ['nurse', 'doctor', 'patient', 'family']
    activities = ['resting', 'moving', 'distressed']

    entity = entities[np.argmax(entity_prediction)]
    activity = activities[np.argmax(activity_prediction)]

    return entity, activity

# 7. Basic Alert Generation
def generate_alert(entity, activity):
    if entity == 'patient' and activity == 'distressed':
        return "ALERT: Patient appears distressed!"
    return None

# 8. Main function
def main():
    entity_model = create_entity_recognition_model()
    activity_model = create_activity_recognition_model()

    print("Please upload a video file.")
    uploaded = files.upload()

    if not uploaded:
        print("No file was uploaded. Exiting.")
        return

    input_path = next(iter(uploaded))

    print(f"Starting video processing for file: {input_path}")
    try:
        process_video(input_path, entity_model, activity_model)
    except Exception as e:
        print(f"An error occurred during video processing: {str(e)}")
    finally:
        print("Video processing complete.")

if __name__ == "__main__":
    main()