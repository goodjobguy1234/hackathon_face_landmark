import time
from tkinter import *
import PIL
import cv2
from PIL import ImageTk, Image

delay = 15
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


def create_interface(root,window_title):
    window = root
    window.title(window_title)
    vid = my_video_capture(0)
    canvas = Canvas(window,width=vid.width, height=vid.height)
    canvas.pack()
    btn_snapshot = Button(window, text="Snapshot", width=50)
    btn_snapshot.pack(anchor=CENTER, expand=True)
    update(window, canvas,vid)
    window.mainloop()

def update(window,canvas,vid):
    ret, frame = vid.get_frame()
    if ret:
        photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
        canvas.create_image(0, 0, image=photo, anchor=NW)
    window.after(delay,update)


if __name__ == '__main__':
    create_interface(Tk(),"myWindow")