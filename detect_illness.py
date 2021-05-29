import time
from tkinter import *
from PIL import Image, ImageTk
import face_recognition as face
import cv2
from scipy.spatial import distance as dist

video_capture = cv2.VideoCapture(0)
color = (0, 255, 0)
thickness = 1
multiply = 2
closed_count = 0

def draweye(mark):
    for i in range(0, len(mark)):
        p1_x, p2_x = mark[i - 1]
        p1_y, p2_y = mark[i]
        x = (p1_x * multiply, p2_x * multiply)
        y = (p1_y * multiply, p2_y * multiply)
        cv2.line(frame, y, x, color, thickness)


def drawface(mark):
    for i in range(1, len(mark)):
        p1_x, p2_x = mark[i - 1]
        p1_y, p2_y = mark[i]
        x = (p1_x * multiply, p2_x * multiply)
        y = (p1_y * multiply, p2_y * multiply)
        cv2.line(frame, y, x, color, thickness)


def plot(mark):
    for (x, y) in mark:
        cv2.circle(frame, (x * multiply, y * multiply), 2, color, -1)


def is_between(nose):
    global color
    p28_x = nose[0][0]
    p29_x = nose[1][0]
    p30_x = nose[2][0]
    p31_x = nose[3][0]

    if p28_x == p29_x == p30_x == p31_x:
        color = (0, 255, 0)
        return True
    else:
        color = (0, 0, 255)
        return False

def get_ear(eye):

	# compute the euclidean distances between the two sets of
	# vertical eye landmarks (x, y)-coordinates
	A = dist.euclidean(eye[1], eye[5])
	B = dist.euclidean(eye[2], eye[4])
 
	# compute the euclidean distance between the horizontal
	# eye landmark (x, y)-coordinates
	C = dist.euclidean(eye[0], eye[3])
 
	# compute the eye aspect ratio
	ear = (A + B) / (2.0 * C)
 
	# return the eye aspect ratio
	return ear

while video_capture.isOpened():
    ret, frame = video_capture.read()
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    rgb_small_frame = small_frame[:, :, ::-1]


    face_landmarks_list = face.face_landmarks(rgb_small_frame)

    for face_landmarks in face_landmarks_list:

        left_eye = face_landmarks['left_eye']
        right_eye = face_landmarks['right_eye']

        ear_left = get_ear(left_eye)
        ear_right = get_ear(right_eye)
        closed = ear_left > 0.25 and ear_right > 0.25

        if(not closed):
            closed_count = 0

        if (closed) and is_between(face_landmarks['nose_bridge']):
            closed_count += 1
        
        if closed_count > 5:
            print("Eyebrowwww")
        
        for facial_feature in face_landmarks.keys():
            mark = face_landmarks[facial_feature]
            nose = face_landmarks['nose_bridge']
        
            is_between(nose)
            plot(mark)

            if facial_feature != 'left_eye' and facial_feature != 'right_eye':
                drawface(mark)
            else:
                draweye(mark)
    cv2.imshow('vdo', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()

    
