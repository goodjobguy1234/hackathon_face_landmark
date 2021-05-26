import face_recognition as face
import cv2
import dlib
import numpy as np
from PIL import Image, ImageDraw

video_capture = cv2.VideoCapture(0)
color = (0, 255, 0)
thickness = 2
process = True

def draweye(mark):
    for i in range(0, len(mark)):
        p1_x, p2_x = mark[i - 1]
        p1_y, p2_y = mark[i]
        x = (p1_x * 2, p2_x * 2)
        y = (p1_y * 2, p2_y * 2)
        cv2.line(frame, y, x, color, thickness)


def drawface(mark):
    for i in range(1, len(mark)):
        p1_x, p2_x = mark[i - 1]
        p1_y, p2_y = mark[i]
        x = (p1_x * 2, p2_x * 2)
        y = (p1_y * 2, p2_y * 2)
        cv2.line(frame, y, x, color, thickness)

def plot(mark):
    for (x, y) in mark:
        cv2.circle(frame, (x * 2, y * 2), 2, color, -1)

def is_between(nose):
    global color
    p28_x = nose[0][0]
    p29_x = nose[1][0]
    p30_x = nose[2][0]
    p31_x = nose[3][0]

    if p28_x == p29_x == p30_x == p31_x:
        color = (0,255, 0)
    else:
        color = (0,0,255)

while True:
    ret, frame = video_capture.read()
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    rgb_small_frame = small_frame[:, :, ::-1]

    if process:
        face_landmarks_list = face.face_landmarks(rgb_small_frame)

        for face_landmarks in face_landmarks_list:

            for facial_feature in face_landmarks.keys():

                # print("The {} in this face has the following points: {}".format(facial_feature,
                #                                                                 face_landmarks[facial_feature]))
                # for point in face_landmarks[facial_feature]:
                #     print(point)
                #     cv2.circle(frame, point, 1, color, -1)

                # for i in range(1 ,len(face_landmarks[facial_feature])):
                #     p1 = face_landmarks[facial_feature][i-1]
                #     p2 = face_landmarks[facial_feature][i]
                #     cv2.line(frame, p1, p2, color, 2)
                mark = face_landmarks[facial_feature]
                nose = face_landmarks['nose_bridge']

                is_between(nose)

                plot(mark)
                if facial_feature != 'left_eye' and facial_feature != 'right_eye':
                    drawface(mark)
                else:
                    draweye(mark)
            cv2.imshow('vdo', frame)
    process = not process

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
