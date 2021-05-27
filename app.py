import time
from tkinter import *
import PIL
import cv2
from PIL import ImageTk, Image

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
                        cv2.cvtColor(frame, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)))

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

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                return ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                return ret, None
        else:
            return False, None

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()


if __name__ == '__main__':
    root = Tk()
    title = "myapp"
    App(root,title)
