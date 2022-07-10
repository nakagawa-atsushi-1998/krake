import time
import tkinter as tk
from PIL import Image, ImageTk

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
        self.frame.canvas=tk.Canvas(self.frame, width=800, height=300)
        self.frame.canvas.pack()
        self.frame.canvas.create_image(300,300, image=tk.PhotoImage(file="figure01.png"))

    def main(self):
        while True:
            time.sleep(10)
            self.frame.mainloop()

"""
def main():
    gui = GUI(tk.Tk())
    gui.mainloop()
main()
"""
