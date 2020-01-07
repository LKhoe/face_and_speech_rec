#

import face_recognition
import cv2
import numpy as np
import os
import speech_recognition as sr
import time

def search_for_faces(rgb_small_frame, fast = False):
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    face_names = []
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"
        if (fast):
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]
        else:
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            if(face_distances.size > 0): 
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
        face_names.append(name)

    return face_locations, face_names

def process_faces(face_locations, face_names, rgb_small_frame, frame):
    global unknown_counter
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        if (name == "Unknown"):
            new_image = rgb_small_frame[top:bottom, left:right]
            tmp = face_recognition.face_encodings(new_image)
            if(len(tmp) > 0):
                new_face_encoding = tmp[0]
                known_face_encodings.append(new_face_encoding)
                known_face_names.append(name+str(unknown_counter))
                cv2.imwrite("pictures"+os.sep+"unknown"+os.sep+name+str(unknown_counter)+".jpg",new_image)
                unknown_counter += 1
                print("unknown counter: ",unknown_counter)
        else:
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

def teach_name(name, new_name):
    os.rename("pictures"+os.sep+"unknown"+os.sep+name+".jpg", "pictures"+os.sep+"known"+os.sep+new_name+".jpg")
    known_face_names[known_face_names.index(name)] = new_name

def listen_to_cam(process_every_frame = True):
    video_capture = cv2.VideoCapture(0) 
    process_this_frame = True

    while True:
        _, frame = video_capture.read()

        if (process_this_frame):
            rgb_small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)[:, :, ::-1]
            face_locations, face_names = search_for_faces(rgb_small_frame)
            process_faces(face_locations, face_names, rgb_small_frame, frame)

        if (not process_every_frame):
            process_this_frame = not process_this_frame

        cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            video_capture.release()
            cv2.destroyAllWindows()
            break

def process_audio(recognizer, audio):
    try:
        phrase = recognizer.recognize_google(audio,language='pt-BR')
        print("U said: " + phrase)
        teach_name("Unknown"+str(unknown_counter-1),phrase)
    except sr.UnknownValueError:
        print("Google could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google service")



#Create Folders (if they don't exist)
if not os.path.exists("pictures"):
    try:
        os.mkdir("pictures")
        os.mkdir("pictures"+os.sep+"known")
        os.mkdir("pictures"+os.sep+"unknown")
    except OSError as e:
        print("Could not create a folder")
        exit()

#Initialize global variables
known_face_encodings = []
known_face_names = []
unknown_counter = 0

#Learn saved images (on all subdirs of pictures)
for subdir, dirs, files in os.walk("pictures"):
    for file in files:
        filepath = subdir + os.sep + file
        if filepath.endswith(".jpg"):
            loaded_image = face_recognition.load_image_file(filepath)[:, :, ::-1]
            tmp = face_recognition.face_encodings(loaded_image)
            if (len(tmp) > 0):
                loaded_face_encoding = tmp[0]
                known_face_encodings.append(loaded_face_encoding)
                known_face_names.append(file[:-4])
            else:
                print("Could not learn from "+file)

#Set listener
r = sr.Recognizer()
mic = sr.Microphone()

#Calibrate the mic
with mic as source:
    r.adjust_for_ambient_noise(source)

#Start listening
stop_listening = r.listen_in_background(mic, process_audio)

#Start the cam loop
listen_to_cam()

#Stop audio cap
stop_listening(wait_for_stop=False)

#Delete Unknown faces
for file in os.listdir("pictures"+os.sep+"unknown"):
    filename = os.fsdecode(file)
    os.remove("pictures"+os.sep+"unknown"+os.sep+filename)