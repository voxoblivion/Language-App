import sqlite3
import tkinter as tk

root = tk.Tk()
frame = tk.Frame(root)
a = tk.StringVar()
entry = tk.Entry(root, textvariable=a, text="enter here:")
entry.pack()
root.mainloop()