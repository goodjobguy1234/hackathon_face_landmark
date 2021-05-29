import time
from tkinter import *
import PIL
import cv2
from PIL import ImageTk, Image
import face_recognition as face
import csv
from os.path import exists as file_exists

class App:
    def __init__(self,window,window_title):
        self.window = window
        self.window.title(window_title)
        self.video_source = 0
        self.vid = my_video_capture(self.video_source)
        self.canvas = Canvas(window, width=self.vid.width, height=self.vid.height)
        self.canvas.pack()
        self.btn_snapshot = Button(window, text="Snapshot Normal Face", width=50, command=self.snapshot)
        self.btn_snapshot_bad = Button(window, text="Snapshot Abnormal Face", width=50, command=self.snapshot_abnormal_face)
        self.btn_snapshot.pack(anchor=CENTER, expand=True)
        self.btn_snapshot_bad.pack(anchor=CENTER, expand=True)
        self.delay = 5
        self.update()
        self.window.mainloop()

    def snapshot(self):
        writer = write_util(self.vid.landmark,True)
        ret,frame = self.vid.get_frame()
        is_straight = self.vid.is_straight
        
        if ret and is_straight:
            cv2.imwrite("Normal face-frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg",
                        cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            writer.write()
            

    def snapshot_abnormal_face(self):
        writer = write_util(self.vid.landmark,False)
        ret,frame = self.vid.get_frame()
        is_straight = self.vid.is_straight
        
        if ret and is_straight:
            cv2.imwrite("Abnormal face-frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg",
                        cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            writer.write()

    def update(self):
        ret,frame = self.vid.get_frame()
        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=NW)
        self.window.after(self.delay, self.update)

class my_video_capture:
    def __init__(self,video_source=0):
        self.vid = cv2.VideoCapture(video_source)
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.is_straight = False
        self.color = (0, 255, 0)
        self.thickness = 1
        self.multiply = 2
        self.landmark = None

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            self.process_landmark(frame)
            # return draw cv here
            if ret:
                return ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                return ret, None,None
        else:
            return False, None,None

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

    def process_landmark(self,frame):
        resize = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_small_frame = resize[:, :, ::-1]

        face_landmarks_list = face.face_landmarks(rgb_small_frame)
        self.landmark = face_landmarks_list

        for face_landmarks in face_landmarks_list:

            for facial_feature in face_landmarks.keys():
                mark = face_landmarks[facial_feature]
                nose = face_landmarks['nose_bridge']

                self.is_between(nose,frame)

                self.plot(mark,frame)
                if facial_feature != 'left_eye' and facial_feature != 'right_eye':
                    self.drawface(mark,frame)
                else:
                    self.draweye(mark,frame)
    
    def draweye(self,mark,frame):
        for i in range(0, len(mark)):
            p1_x, p2_x = mark[i - 1]
            p1_y, p2_y = mark[i]
            x = (p1_x * self.multiply, p2_x * self.multiply)
            y = (p1_y * self.multiply, p2_y * self.multiply)
            cv2.line(frame, y, x, self.color, self.thickness)

    def drawface(self,mark,frame):
        for i in range(1, len(mark)):
            p1_x, p2_x = mark[i - 1]
            p1_y, p2_y = mark[i]
            x = (p1_x * self.multiply, p2_x * self.multiply)
            y = (p1_y * self.multiply, p2_y * self.multiply)
            cv2.line(frame, y, x, self.color, self.thickness)

    def plot(self,mark,frame):
        for (x, y) in mark:
            cv2.circle(frame, (x * self.multiply, y * self.multiply), 2, self.color, -1)

    def is_between(self,nose,frame):
        p28_x = nose[0][0]
        p29_x = nose[1][0]
        p30_x = nose[2][0]
        p31_x = nose[3][0]

        if p28_x == p29_x == p30_x == p31_x:
            self.color = (0, 255, 0)
            self.is_straight = True

        else:
            self.color = (0, 0, 255)
            self.is_straight = False

class write_util:
    def __init__(self,landmark,is_normal=False):
        self.landmark_value = landmark
        self.isnormal = is_normal
        self.ab_file_name = 'abnormal facelandmark.csv'
        self.file_name = 'normal facelandmark.csv'
        self.field_name = [
            'chin','left_eyebrow','right_eyebrow','nose_bridge','nose_tip','left_eye','right_eye','top_lip',
            'bottom_lip'
        ]

    def write(self):
        f = None
        writer = None
        if self.isnormal:
            if self.is_exist():
                f = open('normal facelandmark.csv','a', encoding='UTF8', newline='')
                writer = csv.DictWriter(f, fieldnames=self.field_name)
                writer.writerows(self.landmark_value)
            else:
                f = open('normal facelandmark.csv','w', encoding='UTF8', newline='')
                writer = csv.DictWriter(f, fieldnames=self.field_name)

                writer.writeheader()
                writer.writerows(self.landmark_value)
        else:
            if self.is_exist():
                f = open('abnormal facelandmark.csv','a', encoding='UTF8', newline='')
                writer = csv.DictWriter(f, fieldnames=self.field_name)
                writer.writerows(self.landmark_value)
            else:
                f = open('abnormal facelandmark.csv','w', encoding='UTF8', newline='')
                writer = csv.DictWriter(f, fieldnames=self.field_name)

                writer.writeheader()
                writer.writerows(self.landmark_value)

    def is_exist(self):
        if self.isnormal:
            return file_exists(self.file_name)
        else:
            return file_exists(self.ab_file_name)
                     
if __name__ == '__main__':
    root = Tk()
    title = "myapp"
    App(root,title)
