# ============================================================
# PiSecure: IoT Smart Security System with Firebase Integration
# Raspberry Pi + Pi Camera + OpenCV + Firebase (Firestore/Storage)
# ============================================================

import cv2
import firebase_admin
from firebase_admin import credentials, firestore, storage
import datetime
import time
import os

# -------------------------------
# Firebase INITIALIZATION
# -------------------------------
cred = credentials.Certificate("path/to/your-key.json")

firebase_admin.initialize_app(cred, {
    "storageBucket": "pi-d6dc7.appspot.com"
})

db = firestore.client()
bucket = storage.bucket()

# -------------------------------
# CAMERA + FACE DETECTION SETUP
# -------------------------------
# Load Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Initialize Pi Camera
cap = cv2.VideoCapture(0)
cap.set(3, 640)   # width
cap.set(4, 480)   # height

print("[INFO] PiSecure system started...")
print("[INFO] Detecting faces and pushing logs to Firebase.")

# -------------------------------
# FUNCTION: Upload image to Firebase Storage
# -------------------------------
def upload_image(image_path):
    timestamp = str(datetime.datetime.now().timestamp())
    blob = bucket.blob(f"pi_secure_faces/{timestamp}.jpg")

    blob.upload_from_filename(image_path)
    blob.make_public()

    return blob.public_url


# -------------------------------
# FUNCTION: Log event to Firestore
# -------------------------------
def log_event(image_url=None):
    data = {
        "event": "face_detected",
        "timestamp": datetime.datetime.now().isoformat(),
        "device_id": "raspi-3b",
        "image_url": image_url,
    }
    db.collection("PiSecureEvents").add(data)
    print("[LOG] Event pushed to Firestore")


# -------------------------------
# MAIN LOOP
# -------------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        print("[ERROR] Camera not detected!")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    # Draw bounding boxes
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # -------------------------------
        # Save detected face locally
        # -------------------------------
        face_img = frame[y:y+h, x:x+w]
        save_path = "detected_face.jpg"
        cv2.imwrite(save_path, face_img)

        print("[INFO] Face Detected! Uploading...")

        # -------------------------------
        # Upload to Firebase
        # -------------------------------
        try:
            img_url = upload_image(save_path)
            log_event(img_url)
        except Exception as e:
            print("[ERROR] Firebase Upload Failed:", e)

        time.sleep(2)  # avoid spamming Firebase

    cv2.imshow("PiSecure Face Detection", frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

print("[INFO] PiSecure Program Ended.")
