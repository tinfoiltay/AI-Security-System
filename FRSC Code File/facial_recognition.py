import socket
import pickle
import struct
import cv2
import numpy as np
import face_recognition
from picamera2 import Picamera2
import time
import csv
import os



SERVER_IP   = "10.226.6.192" #Basestation IP
SERVER_PORT = 5000           #Basestation Port
CAMERA_WING = "Admin"     #Camera Location

#colour uses BGR format
COLOUR_ALLOWED = (0, 255, 0)     # Green
COLOUR_DENIED = (0, 255,255)     #Yellow
COLOUR_UNKNOWN  = (0, 165, 255)  # Orange
COLOUR_INTRUDER = (0, 0, 255)    # Red


SECURITY_DB     = "SecurityDatabase.csv" #Contains all names and access levels that are in the base station
ACCESS_LEVEL_DB = "accesslevel_database.csv" #access levels hold room permissions



client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))
print("Connected!") #Connects to the base sation


def load_access_levels(filepath):
    #"""Returns {1: ["Admin", "Security", ...], 2: [...], ...}"""
    access_levels = {}
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            level = int(row["Access ID level"].strip())
            wings = [wing.strip() for wing in row["Valid Wings"].split(",")]
            access_levels[level] = wings
    return access_levels

def load_people(filepath):
    #"""Returns {"Taylor Rees": 1, "Angie Carpio": 2, ...}"""
    people = {}
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            full_name      = row["First Name"].strip() + " " + row["Surname"].strip()
            security_level = int(row["Security Level"].strip())
            people[full_name] = security_level
    return people

access_levels = load_access_levels(ACCESS_LEVEL_DB)
people        = load_people(SECURITY_DB)
#print(f"Loaded {len(people)} people and {len(access_levels)} access levels.")



with open("encodings.pickle", "rb") as f: #encodings holds all the relevant trained data on the camera
    face_data = pickle.loads(f.read())

known_encodings = face_data["encodings"]
known_names     = face_data["names"]
#print(f"Loaded {len(known_names)} known faces.")



picam2 = Picamera2()
picam2.configure(
    picam2.create_preview_configuration(
        main={"format": "XRGB8888", "size": (640, 480)}
    )
)
picam2.start() #starts camera feed

SHRINK_BY = 4 #shrinks frame so AI can identify easier

last_face_locations = []
last_face_names     = []

frame_count = 0 #number of frames recorded
start_time  = time.time() #time elapsed
fps         = 0 #frames per second counter


def get_colour_for_person(name):
    if name == "Unknown":
        return COLOUR_INTRUDER, "UNKNOWN" #if recognised as a human face but not in database

    security_level = people.get(name)
    if security_level is None:
        return COLOUR_UNKNOWN, "NOT IN DATABASE" #if recognised as registered face but not in database

    allowed_wings = access_levels.get(security_level, [])
    if CAMERA_WING in allowed_wings:
        return COLOUR_ALLOWED, "ALLOWED" #if registered face and in allowed wing
    else:
        return COLOUR_DENIED, "DENIED" #if registered face but in disapproved wing


def scan_for_faces(frame):
    global last_face_locations, last_face_names

    small_frame = cv2.resize(frame, (0, 0), fx=1/SHRINK_BY, fy=1/SHRINK_BY) 
    rgb_frame   = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    last_face_locations = face_recognition.face_locations(rgb_frame)
    encodings = face_recognition.face_encodings(rgb_frame, last_face_locations, model="large")

    last_face_names = []
    for encoding in encodings:
        matches    = face_recognition.compare_faces(known_encodings, encoding)
        distances  = face_recognition.face_distance(known_encodings, encoding)
        best_match = np.argmin(distances)

        name = known_names[best_match] if matches[best_match] else "Unknown" #appears when a face matches multiple entries in the database
        last_face_names.append(name)


def draw_boxes_on_frame(frame):
    for (top, right, bottom, left), name in zip(last_face_locations, last_face_names):
        top    *= SHRINK_BY
        right  *= SHRINK_BY
        bottom *= SHRINK_BY
        left   *= SHRINK_BY

        colour, label = get_colour_for_person(name) #looks up what colour should be attached to what name
        display_text  = f"{name}" #attached name to ID box

        cv2.rectangle(frame, (left, top), (right, bottom), colour, 3) # draws the box
        cv2.rectangle(frame, (left - 3, top - 35), (right + 3, top), colour, cv2.FILLED)
        cv2.putText(frame, display_text, (left + 6, top - 6), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 0 ,0), 1) #attaches black text
    return frame


def update_fps():
    global frame_count, start_time, fps
    frame_count += 1
    elapsed = time.time() - start_time
    if elapsed > 1:
        fps         = frame_count / elapsed
        frame_count = 0
        start_time  = time.time()
    return fps #displays the new fps count with each fram to ensure it remains accurate



def Camera_Start():
    print("Camera started — watching wing", CAMERA_WING)
    print("Streaming to server... Press Ctrl+C to stop.")

    try:
        while True:
            frame = picam2.capture_array()

            scan_for_faces(frame)
            frame = draw_boxes_on_frame(frame)

            current_fps = update_fps()
            cv2.putText(frame, f"FPS: {current_fps:.1f}  |  Wing: {CAMERA_WING}",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            _, compressed = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            data          = pickle.dumps(compressed)
            client_socket.sendall(struct.pack("Q", len(data)) + data)

    finally:
        print("Stopping...")
        client_socket.close()
