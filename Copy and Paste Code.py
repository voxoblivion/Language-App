import tkinter as tk
from PIL import Image
import time
'''
root = tk.Tk()
dir = "Images/mineral_water.png"
im_temp = Image.open(dir)
im_temp = im_temp.resize((250, 250), Image.ANTIALIAS)
im_temp.save(dir, "png")
photo = tk.PhotoImage(file=dir)
label1 = tk.Label(image=photo)
label1.photo = photo
label1.pack()
'''
# start_mins = int(time.strftime("%M", time.localtime()))
# start_secs = int(time.strftime("%S", time.localtime()))
# time.sleep(4)
# end_mins = int(time.strftime("%M", time.localtime()))
# end_secs = int(time.strftime("%S", time.localtime()))
# print(str(end_mins - start_mins) + str(end_secs - start_secs))

for i in range(1, 11):
    print(i)
