import json
import random
import time
from libary import record_audio_and_play
import tkinter as tk
import playsound
import sqlite3


# TODO ADMINS must be able to add new users
# TODO teachers must be able to assign tasks
# TODO change menu messages to native language
# TODO make subject selection menu
# TODO add percentage completion label on each of the activities


class SampleApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None
        self.switch_frame(LoginPage)
        self.index = 1
        self.score = 0
        self.user_level = ""
        self.title = ""
        self.correct = 0
        self.user_ans = ""
        self.language = tk.StringVar()
        self.words = {}

    def switch_frame(self, frame_class, index=1):
        """Destroys current frame and replaces it with a new one."""
        self.index = index
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.grid()

    def next_slide(self, eng_text=None, foreign_text=None, image=None, unec_frame=None, activity=None):
        if self.index == len(self.words):
            for widget in self._frame.winfo_children():
                widget.destroy()
            temp_frame = self._frame
            if activity == "Activity3":
                score = tk.Label(temp_frame, text="Your score is: " + str(self.score))
                button = tk.Button(temp_frame, text="Return to start page", command=lambda: self.switch_frame(MainPage))
                score.grid()
                button.grid()
            else:
                label = tk.Label(temp_frame, text="Thank you for completing activity\n "
                                                  "please press the continue button to return to the main menu")
                button = tk.Button(temp_frame, text="Continue", command=lambda: self.switch_frame(MainPage))
                label.grid()
                button.grid()
        else:
            self.index += 1
            if eng_text is not None:
                eng_text.configure(text=self.words[str(self.index)][1])
            if foreign_text is not None:
                foreign_text.configure(text=self.words[str(self.index)][0])
            if image is not None:
                new_image = tk.PhotoImage(file=self.words[str(self.index)][3])
                new_image.image = new_image
                image.configure(image=new_image)
            if unec_frame is not None:
                unec_frame.destroy()

    def check_entry(self, entry, label=None, native_word=None, image=None, entry_widget=None):
        if entry.lower() != self.words[str(self.index)][1].lower():
            if label is not None:
                label.config(text="Incorrect, try again")
            if entry_widget is not None:
                entry_widget.delete(0, 'end')
        else:
            if entry_widget is not None:
                entry_widget.delete(0, 'end')
            if label is not None:
                self.next_slide(foreign_text=native_word, image=image)
                label.config(text="Please enter the word in English associated with this image")
            return True

    def check_login(self, user_username, user_password, label):
        conn = sqlite3.connect("test.db")
        c = conn.cursor()
        usernames_passwords = {}
        for i in c.execute("SELECT * FROM users"):
            user_id = i[0]
            first_name = i[1]
            last_name = i[2]
            username = str(last_name[0] + first_name).lower()
            password = (last_name + str(user_id)).lower()
            usernames_passwords[username] = password
        conn.close()
        if user_username in usernames_passwords.keys() and user_password in usernames_passwords.values():
            user_username = user_username.split(user_username[0])[1]
            conn = sqlite3.connect("test.db")
            name = (user_username.title(),)
            c = conn.cursor()
            c.execute("SELECT permission_level FROM users WHERE first_name =?", name)
            self.user_level = c.fetchone()[0]
            c.execute("SELECT user_type FROM users WHERE first_name =?", name)
            self.title = c.fetchone()[0]
            self.switch_frame(LangPage)
        else:
            print("fail")
            label.config(text="Incorrect username and password combination please try again")

    # TODO fix logic error
    def calc_score(self, start_time, correct_ans=None):  # The lower the score the better
        multiplier = 1000
        current_time = time.strftime("%H:%M:%S", time.localtime()).split(":")
        if abs(int(start_time[0]) - int(current_time[0])) > 1:
            current_time[1] = int(current_time[1]) + (60 * abs(int(start_time[0]) - int(current_time[0])))
        min_diff = abs(int(current_time[1]) - int(start_time[1]))
        sec_diff = abs(int(current_time[2]) - int(start_time[2]))
        if correct_ans is True:
            self.correct += 1
        if self.index == len(self.words):
            score = (multiplier * min_diff) + (multiplier * (sec_diff / 60))
            self.score += round(score)
            incorrect = len(self.words) - self.correct
            self.score += incorrect * 1000

    def set_ans(self, ans, start_time, eng_text=None):
        self.user_ans = ans
        if self.check_entry(ans) is True:
            correct_ans = True
        else:
            correct_ans = False
        self.calc_score(start_time, correct_ans)
        self.next_slide(eng_text=eng_text, activity="Activity3")

    def generate_dict(self, language):
        self.words = json.load(open(str(language.get()) + ' Dict'))
        self.switch_frame(MainPage)

    def add_user(self, first_name, last_name, user_level):
        conn = sqlite3.connect("test.db")
        c = conn.cursor()


# TODO depending on role grant permissions


class LoginPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        label = tk.Label(self, text="Please enter your username and password.\n "
                                    "Your username is the first initial of your surname then your full first name"
                                    "\n e.g. John Smith is sjohn. Your password is your full last name and the userID\n"
                                    "the teacher provided you e.g. smith1")
        username = tk.StringVar()
        username_entry = tk.Entry(self, textvariable=username)
        password = tk.StringVar()
        password_entry = tk.Entry(self, textvariable=password)
        username.set("sjohn")
        password.set("smith1")
        button = tk.Button(self, text="Login", command=lambda: master.check_login(user_username=username.get(),
                                                          user_password=password.get(), label=label))
        label.grid()
        username_entry.grid(pady=10)
        password_entry.grid()
        button.grid(pady=10)


class LangPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        label = tk.Label(self, text="Please select your native language")
        self.language = tk.StringVar(self)
        self.language.set("Italian")
        menu = tk.OptionMenu(self, self.language, "Italian", "Polish", command=lambda x: master.generate_dict(
            self.language))
        menu.place(x=10, y=10)
        label.grid()
        menu.grid()

# TODO 1st image disappears after using speaker widget only tested mic no impact, only occurs on first run of Activity1


class MainPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        master.image = tk.PhotoImage(file=master.words[str(master.index)][3])
        master.score = 0
        master.correct = 0
        start_label = tk.Label(self, text="This is the start page. Currently logged in as %s" % master.title)
        page_1_button = tk.Button(self, text="Open activity one",
                                  command=lambda: master.switch_frame(Activity1))
        page_2_button = tk.Button(self, text="Open activity two",
                                  command=lambda: master.switch_frame(Activity2))
        page_3_button = tk.Button(self, text="Open activity three",
                                  command=lambda: master.switch_frame(Activity3))
        page_4_button = tk.Button(self, text="Reselect native language",
                                  command=lambda: master.switch_frame(LangPage))
        page_5_button = tk.Button(self, text="Add new user", command=lambda: master.switch_frame(AddUser))
        page_6_button = tk.Button(self, text="Assign tasks")
        start_label.grid()
        page_1_button.grid()
        page_2_button.grid(pady=2)
        page_3_button.grid(pady=1)
        page_4_button.grid(pady=1)
        if master.user_level == "ADMIN":
            page_5_button.grid()
        if master.title == "Teacher":
            page_6_button.grid()


class Activity1(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        ac1_native_word = tk.Label(self, text=master.words[str(master.index)][0])
        ac1_eng_word = tk.Label(self, text=master.words[str(master.index)][1])
        ac1_image_2 = tk.PhotoImage(file='Images/Speaker.png')
        ac1_speaker = tk.Button(self, image=ac1_image_2,
                                command=lambda: playsound.playsound(master.words[str(master.index)][2]))
        ac1_speaker.image = ac1_image_2
        ac1_image_1 = master.image
        ac1_image = tk.Label(self, image=ac1_image_1)
        ac1_image_1.image = ac1_image_1
        ac1_image_3 = tk.PhotoImage(file='Images/mic.png')
        ac1_mic = tk.Button(self, image=ac1_image_3, command=record_audio_and_play)
        ac1_mic.image = ac1_image_3
        ac1_start_button = tk.Button(self, text="Next Slide",
                                     command=lambda: master.next_slide(eng_text=ac1_eng_word,
                                                                       foreign_text=ac1_native_word, image=ac1_image,))
        return_button = tk.Button(self, text="Return to start page", command=lambda: master.switch_frame(MainPage))
        ac1_native_word.grid(row=0, column=2)
        ac1_eng_word.grid(row=1, column=2)
        ac1_mic.grid(row=2, column=1, padx=10)
        ac1_speaker.grid(row=2, column=3, padx=10)
        ac1_image.grid(row=3, rowspan=10, column=0, columnspan=5)
        ac1_start_button.grid(row=14, column=2)
        return_button.grid(row=15, column=2)


class Activity2(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        ac2_intro = tk.Label(self, text="Please enter the word in English associated with this image then press enter")
        ac2_label_2 = tk.Label(self, image=master.image)
        ac2_native_word = tk.Label(self, text=master.words[str(master.index)][0])
        ac2_image_2 = tk.PhotoImage(file='Images/Speaker.png')
        ac2_speaker = tk.Button(self, image=ac2_image_2,
                                command=lambda: playsound.playsound(master.words[str(master.index)][2]))
        ac2_speaker.image = ac2_image_2
        ac2_user = tk.StringVar()
        ac2_entry_1 = tk.Entry(self, textvariable=ac2_user)
        ac2_entry_1.bind("<Return>",
                         lambda x: master.check_entry(ac2_user.get(), ac2_intro, ac2_native_word, ac2_label_2,
                                                      ac2_entry_1))
        return_button = tk.Button(self, text="Return to start page", command=lambda: master.switch_frame(MainPage))
        ac2_intro.grid(row=0)
        ac2_speaker.grid(row=7)
        ac2_native_word.grid(row=1)
        ac2_label_2.grid(row=2)
        ac2_entry_1.grid(row=9, rowspan=2, pady=6)
        return_button.grid(row=13)


class Activity3(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        master.index = 0
        self.image_dirs = []
        self.button_list = []
        self.image_dict = {}
        self.start_time = time.strftime("%H:%M:%S", time.localtime()).split(":")
        for i in range(1, len(master.words.keys()) + 1):
            self.image_dirs.append(tk.PhotoImage(file=master.words[str(i)][3]).subsample(3))
            self.button_list.append(tk.Button(self, image=self.image_dirs[i - 1]))
            self.image_dict[self.button_list[i - 1]] = master.words[str(i)][1]
            current_button = self.button_list[i-1]
            self.button_list[i - 1].config(command=lambda ans=current_button:
                master.set_ans(self.image_dict[ans], self.start_time, ac3_label))
        random.shuffle(self.button_list)
        self.column = 0
        self.row = 0
        for j in range(1, len(master.words.keys()) + 1):
            self.button_list[j - 1].grid(column=self.column, row=self.row)
            if self.column == 4:
                self.column = 0
                self.row += 1
            else:
                self.column += 1
        ac3_label = tk.Label(self, text="Once you clicked the start button the game will begin please click the image "
                                        "corresponding to the word that appears.\n The game is time based so the quicker"
                                        " you complete the game the better score you will achieve, the lower the better")
        ac3_start_button = tk.Button(self, text="Start Game",
                                     command=lambda: master.next_slide(eng_text=ac3_label, unec_frame=ac3_start_button))
        return_button = tk.Button(self, text="Return to start page", command=lambda: master.switch_frame(MainPage))
        ac3_label.grid(row=3, columnspan=6, column=0, rowspan=2)
        ac3_start_button.grid(row=5, columnspan=6, column=0)
        return_button.grid(row=6, columnspan=6, column=0)


class AddUser(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        intro = tk.Label(self, text="Fill in the following fields to add a new user")
        first_name_label = tk.Label(self, text="First Name:")
        first_name = tk.StringVar()
        first_name_entry = tk.Entry(self, textvariable=first_name)
        last_name_label = tk.Label(self, text="Last name")
        last_name = tk.StringVar()
        last_name_entry = tk.Entry(self, textvariable=last_name)
        position_label = tk.Label(self, text="Position")
        position = tk.StringVar()
        position_entry = tk.OptionMenu(self, position, "Student", "Teacher", command=lambda x: position.get())
        add_button = tk.Button(self, text="Add User", command=lambda: master.add_user())
        intro.grid(row=0, column=0, columnspan=2)
        first_name_label.grid(row=1, column=0)
        first_name_entry.grid(row=1, column=1)
        last_name_label.grid(row=2, column=0)
        last_name_entry.grid(row=2, column=1)
        position_label.grid(row=3, column=0)
        position_entry.grid(row=3, column=1)


app = SampleApp()
app.mainloop()
