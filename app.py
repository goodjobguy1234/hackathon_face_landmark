import time
from tkinter import *
import PIL
import cv2
from PIL import ImageTk, Image
import face_recognition as face

class App:
    def __init__(self,window,window_title):
        self.window = window
        self.window.title(window_title)
        self.video_source = 0
        self.vid = my_video_capture(self.video_source)
        self.canvas = Canvas(window, width=self.vid.width, height=self.vid.height)
        self.canvas.pack()
        self.btn_snapshot = Button(window, text="Snapshot", width=50, command=self.snapshot)
        self.btn_snapshot.pack(anchor=CENTER, expand=True)
        self.delay = 15
        self.update()
        self.window.mainloop()

    def snapshot(self):
        ret, frame = self.vid.get_frame()
        if ret:
            cv2.imwrite("frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg",
                        cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

    def update(self):
        ret, frame = self.vid.get_frame()
        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=NW)
        self.window.after(self.delay, self.update)

class my_video_capture:
    def __init__(self,video_source=0):
        self.vid = cv2.VideoCapture(video_source)
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

        self.color = (0, 255, 0)
        self.thickness = 1
        self.multiply = 2

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            self.process_landmark(frame)
            # return draw cv here
            if ret:
                return ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                return ret, None
        else:
            return False, None

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

    def process_landmark(self,frame):
        resize = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_small_frame = resize[:, :, ::-1]
        face_landmarks_list = face.face_landmarks(rgb_small_frame)

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
        else:
            self.color = (0, 0, 255)

if __name__ == '__main__':
    root = Tk()
    title = "myapp"
    App(root,title)
