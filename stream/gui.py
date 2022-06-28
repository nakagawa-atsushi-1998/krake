import tkinter as tk

class GUI(tk.Frame):
    def __init__(self, frame=None):
        super().__init__(frame)
        self.frame = frame
        self.initialize_format()

    def initialize_format(self):
        self.pack()
        self.frame.geometry("720x840")
        self.frame.title("Test")

        self.canvas = tk.Canvas(self.frame, width=800, height=300)
        self.canvas.pack()
    
    def move(self,event):
        self.canvas.move("id1",5,5)

def main():
    gui = GUI(tk.Tk())
    gui.mainloop()

main()
