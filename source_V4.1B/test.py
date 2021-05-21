import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw

path = filedialog.askopenfilename()

f = open(path, "rb")
c= f.read(2048)
print (c)
c = [i for i in c]
print(c)

input("prompt: ")