import time
from tkinter import *
from PIL import Image, ImageTk
import face_recognition as face
import cv2
from scipy.spatial import distance as dist
import csv
import requests
import sys
from os import path

draw_face_landmark_highlight = True
video_path = None
video_capture = None
color = (0, 255, 0)
thickness = 1
multiply = 2
left_closed_count = 0
right_closed_count = 0
counter = 0
send_amount = 0
triggered_time = None
elapsed_time = 0
trigger_time_period = 10 #second

def argument_import():
    global video_capture, draw_face_landmark_highlight,video_path
    # print(f"Arguments {len(sys.argv)}",sys.argv)
    if len(sys.argv) > 2:
        # expect 2 arguments, -q that is
        arg = sys.argv[1]
        video_path = sys.argv[2]
        if arg == '-q': # expect only -q for now
            print("Suppress face landmark highlight")
            draw_face_landmark_highlight = False
            if path.exists(video_path):
                video_capture = cv2.VideoCapture(video_path)
            else:
                print(f"video file = {video_path} does not exist")
                exit()        

    elif len(sys.argv) > 1:
        # use only one argument
        arg = sys.argv[1]
        if arg == '-h':
            print("Show help message")
        elif arg == '-q':
            print("Suppress face landmark highlight")
            draw_face_landmark_highlight = False
            video_capture = cv2.VideoCapture(0)
        else:   # expect the video file path
            video_path = sys.argv[1]
            print(f"video file = {video_path}")

            if path.exists(video_path):
                video_capture = cv2.VideoCapture(video_path)
            else:
                print(f"video file = {video_path} does not exist")
                exit()

    else:
        print("No arguments, open webcam")
        video_capture = cv2.VideoCapture(0)
      
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

def find_eye_distance(bottom_eye,lip):
    return bottom_eye - lip

def check_mount(top_lip, bottom_lip, to_left):
    for i in range(1,len(top_lip)):
        if top_lip[i-1][1] <= bottom_lip[i-1][i] and to_left:
            return True

        elif top_lip[i-1][1] >= bottom_lip[i-1][i] and not to_left:
            return True

        else:
            return False

def send_notification():
    r = requests.get('https://line-notifier.herokuapp.com/line/send?m=Obvious twitching detected! Medical attention is recommened.')
    print(f"Send Notification {r.status_code}")
    if r.status_code != 200:
        print("Cannot send notification")

alert_text_switch = 0
def alert_text():
    global alert_text_switch
    if alert_text_switch % 5 == 0:
        cv2.putText(frame, 'Twitching', (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 100, 100), 2, cv2.LINE_AA)
    alert_text_switch += 1

if __name__ == '__main__':
    argument_import()

    while video_capture.isOpened():
        ret, frame = video_capture.read()
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_small_frame = small_frame[:, :, ::-1]


        face_landmarks_list = face.face_landmarks(rgb_small_frame)

        for face_landmarks in face_landmarks_list:

            left_eye = face_landmarks['left_eye']
            right_eye = face_landmarks['right_eye']

            top_lip = face_landmarks['top_lip']
            bottom_lip = face_landmarks['bottom_lip']

            left_tip_bottom = left_eye[0][1]
            right_tip_bottom = right_eye[3][1]
            top_lip_left = top_lip[0][1]
            top_lip_right = top_lip[6][1]

            distance_left = find_eye_distance(left_tip_bottom,top_lip_left)
            distance_right = find_eye_distance(right_tip_bottom,top_lip_right)

            ear_left = get_ear(left_eye)
            ear_right = get_ear(right_eye)

            left_closed = ear_left < 0.20 
            right_closed = ear_right < 0.20

            if ((left_closed and not right_closed) and distance_left <= distance_right):
                left_closed_count += 1

            elif (not left_closed and right_closed) and distance_left >= distance_right:
                right_closed_count += 1
            
            if counter >=2:
                # frame = alert_text(frame)
                alert_text()
                if left_closed_count > right_closed_count:

                    if triggered_time == None:
                        triggered_time = time.time()
                        # print(f"CASE 1 -- clicker time is {triggered_time}")
                        send_notification()
                        # r = requests.get('https://line-notifier.herokuapp.com/line/send?m=Obvious twitching detected! Medical attention is recommened.')
                        # if r.status_code != 200:
                        #     print("Cannot send notification")

                    else:
                        elapsed_time = time.time() - triggered_time
                        if elapsed_time > trigger_time_period:
                            # print(f"CASE 2 -- clicker time is {elapsed_time}")
                            send_notification()
                            # r = requests.get('https://line-notifier.herokuapp.com/line/send?m=Obvious twitching detected! Medical attention is recommened.')
                            # if r.status_code != 200:
                            #     print("Cannot send notification")
                            triggered_time = None
                            elapsed_time = 0

                    print(f"Twitching Detected")

                else:
                    if triggered_time == None:
                        # print(f"CASE 3 -- clicker time is {triggered_time}")
                        triggered_time = time.time()
                        send_notification()
                        # r = requests.get('https://line-notifier.herokuapp.com/line/send?m=Obvious twitching detected! Medical attention is recommened.')
                        # if r.status_code != 200:
                        #     print("Cannot send notification")

                    else:
                        elapsed_time = time.time() - triggered_time
                        if elapsed_time > trigger_time_period:
                            # print(f"CASE 4 -- clicker time is {elapsed_time}")
                            send_notification()
                            # r = requests.get('https://line-notifier.herokuapp.com/line/send?m=Obvious twitching detected! Medical attention is recommened.')
                            # if r.status_code != 200:
                            #     print("Cannot send notification")
                            triggered_time = None
                    print(f"Twitching Detected")
                        
                counter = 0
            
            if left_closed and right_closed:
                left_closed_count = 0
                right_closed_count = 0

            if left_closed_count >= 3:
                print("your left eye is twitching")
                counter +=1
                left_closed_count = 0

            if right_closed_count >= 3:
                print("your right eye is twitching")
                counter +=1
                right_closed_count = 0

            # draw face high light
            if draw_face_landmark_highlight:
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

    
