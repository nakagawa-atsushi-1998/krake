import time
import tkinter as tk
from PIL import Image, ImageTk
import os; cd=os.path.dirname(__file__)

class GUI(tk.Frame):
    def __init__(self, frame):
        super().__init__(frame)
        self.frame = frame
        self.initialize_format()
        self.create_widgets()

    def initialize_format(self):
        self.pack()
        self.frame.geometry("720x840")
        self.frame.title("krake") #キャンバスのサイズを取得

    def create_widgets(self):
        self.read_image1=Image.open(str(cd)+'/graph/latest.png')
        self.image1=ImageTk.PhotoImage(image=self.read_image1)
        self.canvas1=tk.Canvas(self, width=720, height=840, background="white")
        self.canvas1.create_image(0,-20,anchor='nw',image=self.image1)
        self.canvas1.pack()

    def main(self):
        self.frame.mainloop()
'''
def main():
    root=tk.Tk()
    gui = GUI(root)
    gui.main()
main()
'''