import json
import random
from libary import record_audio_and_play
import tkinter as tk
import playsound
import sqlite3
import glob
import time

# TODO change menu messages to native language
# TODO once a task has been completed automatically remove from task (could be after feedback)
# TODO play sound after completion of activity
# TODO add a scoreboard for activity 3
# TODO randomize order to engage user


class SampleApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None
        self.switch_frame(LoginPage)
        self.index = 1
        self.score = 0
        self.user_level = ""
        self.name = ""
        self.title = "Teacher"
        self.correct = 0
        self.user_ans = ""
        self.language = tk.StringVar()
        self.words = {}
        self.user_id = 0
        self.percentage_complete = 10
        self.subject = ""
        self.activity = ""

    def switch_frame(self, frame_class, lang=None, index=1):
        """Destroys current frame and replaces it with a new one."""
        if lang is not None:
            self.language = lang
        self.index = index
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.grid()

    def next_slide(self, eng_text=None, foreign_text=None, image=None, unec_frame=None, percentage=None):
        if self.index == len(self.words):
            for widget in self._frame.winfo_children():
                widget.destroy()
            temp_frame = self._frame
            if self.activity == "Activity 3":
                out_of_10 = tk.Label(temp_frame, text="You got " + str(self.correct) + " out of 10 right")
                score = tk.Label(temp_frame, text="Your score is: " + str(self.score))
                button = tk.Button(temp_frame, text="Return to start page", command=lambda: self.switch_frame(MainPage))
                out_of_10.grid()
                score.grid()
                button.grid()
            else:
                label = tk.Label(temp_frame, text="Thank you for completing activity\n "
                                                  "please press the continue button to return to the main menu")
                button = tk.Button(temp_frame, text="Continue", command=lambda: self.switch_frame(MainPage))
                label.grid()
                button.grid()
            conn = sqlite3.connect("test.db")
            c = conn.cursor()
            items = [str(self.subject+" "+self.activity), str(self.user_id)]
            c.execute("SELECT tasks_completed FROM users WHERE user_id = ?", (items[1],))  #Issue occurring if user_id is over 9 possibly counter all users with 1
            old_tasks_completed = c.fetchone()[0]
            if old_tasks_completed is not None:
                if items[0] not in old_tasks_completed:
                    items[0] = str(old_tasks_completed + ", " + items[0])
                    c.execute("UPDATE users SET tasks_completed = ? WHERE user_id = ?", items)
            else:
                c.execute("UPDATE users SET tasks_completed = ? WHERE user_id = ?", items)
            conn.commit()
            conn.close()
        else:
            self.index += 1
            if eng_text is not None:
                eng_text.configure(text="English Word")
            if foreign_text is not None:
                foreign_text.configure(text=self.words[str(self.index)][0])
            if image is not None:
                new_image = tk.PhotoImage(file=self.words[str(self.index)][3])
                new_image.image = new_image
                image.configure(image=new_image)
                image.lift()
            if unec_frame is not None:
                unec_frame.destroy()
            if percentage is not None:
                percentage_complete = str(int((self.index / len(self.words)) * 100)) + '%'
                percentage.config(text=percentage_complete)
                percentage.grid()

    def check_entry(self, entry, label=None, native_word=None, image=None, entry_widget=None, percentage=None):
        if entry.lower() != self.words[str(self.index)][1].lower():
            if label is not None:
                label.config(text="Incorrect, try again")
            if entry_widget is not None:
                entry_widget.delete(0, 'end')
        else:
            if entry_widget is not None:
                entry_widget.delete(0, 'end')
            if label is not None:
                self.next_slide(foreign_text=native_word, image=image, percentage=percentage)
                label.config(text="Please enter the word in English associated with this image")
            return True

    def check_login(self, permission):
        if permission == "Teacher":
            self.title = permission
        else:
            self.user_level = "USER"
            self.title = "Student"
        self.switch_frame(LangPage)

    def calc_score(self, start_time, correct_ans=None):  # The lower the score the better
        if self.index == 1:
            start_time = time.strftime("%H:%M:%S", time.localtime()).split(":")
        multiplier = 1000
        if correct_ans is True:
            self.correct += 1
        if self.index == len(self.words):
            current_time = time.strftime("%H:%M:%S", time.localtime()).split(":")
            start_secs = int((int(start_time[0]) * (60**2)) + (int(start_time[1]) * 60) + (int(start_time[2])))
            current_secs = int((int(current_time[0]) * (60**2)) + (int(current_time[1]) * 60) + (int(current_time[2])))
            sec_diff = current_secs - start_secs
            score = (sec_diff/60) * multiplier
            self.score += round(score)
            incorrect = len(self.words) - self.correct
            self.score += incorrect * 1000

    def set_ans(self, ans, start_time, eng_text=None):
        self.user_ans = ans
        correct_ans = True
        self.calc_score(start_time, correct_ans)
        self.next_slide(eng_text=eng_text)

    def generate_dict(self, subject):
        self.words = json.load(open('%s/%s' % (self.language, subject)))
        self.subject = subject
        self.switch_frame(ActivitySelector)

    def add_user(self, first_name="", last_name="", user_level="", tasks=None, tasks_completed=None):
        self.switch_frame(MainPage)

    def select_assignment(self):
        self._frame.destroy()
        self._frame = tk.Frame()
        scrollbar = tk.Scrollbar(self._frame)
        label = tk.Label(self._frame, text="Please click the subject for the tasks you want to assign the users\n"
                                    "The subject highlighted are the subject selected")
        my_list = tk.Listbox(self._frame, selectmode=tk.MULTIPLE, yscrollcommand=scrollbar.set, width=30, height=3)
        next_button = tk.Button(self._frame, text="Next",
                                  command=lambda: self.switch_frame(MainPage))
        label.grid()
        my_list.grid()
        next_button.grid()
        self._frame.grid()

    def select_task(self, user_id, subject_list, task_selection):
        self._frame.destroy()
        self._frame = tk.Frame()
        label = tk.Label(self._frame, text="Please select the tasks for want for the user to do in the chosen subject")
        list_box_2 = tk.Listbox(self._frame, selectmode=tk.MULTIPLE, height=3, width=30)
        assign_button = tk.Button(self._frame, text="Assign task",
                        command=lambda: self.assign_tasks())
        label.grid()
        list_box_2.grid()
        assign_button.grid()
        self._frame.grid()

    def get_users(self, use):
        if use == "Assign Tasks":
            self.select_assignment()
        elif use == "View Tasks":
            self.view_tasks()

    def assign_tasks(self):
        self.switch_frame(MainPage)

    def view_tasks(self):
        self._frame.destroy()
        self._frame = tk.Frame()
        scrollbar = tk.Scrollbar(self._frame)
        label = tk.Label(self._frame, text="Here are the tasks that\nthe user with the ID (insert later) has completed")
        my_list = tk.Listbox(self._frame, selectmode=tk.MULTIPLE, yscrollcommand=scrollbar.set, width=30, height=3)
        next_button = tk.Button(self._frame, text="Return", command=lambda: self.switch_frame(MainPage))
        my_list.grid(column=0, columnspan=1, row=2)
        scrollbar.config(command=my_list.yview)
        scrollbar.grid(column=1, row=2)
        next_button.grid()
        label.grid(row=0, columnspan=2, rowspan=2, column=0)
        self._frame.grid()

    def task_complete(self, tasks, task_list):
        conn = sqlite3.connect("test.db")
        c = conn.cursor()
        task_list = [task_list.remove(task) for task in tasks]
        c.execute("UPDATE users SET tasks = ? WHERE user_id = ?", (str(task_list), self.user_id,))
        conn.commit()
        conn.close()
        self.switch_frame(MainPage)


class LoginPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        label = tk.Label(self, text="Please enter your username and password.\n "
                                    "Your username is the first initial of your surname then your full first name"
                                    "\n e.g. John Smith is sjohn. Your password is your full last name and the userID\n"
                                    "the teacher provided you e.g. smith1")
        username = tk.StringVar()
        username_entry = tk.Entry(self, textvariable=username)
        username_label = tk.Label(self, text="Username:")
        password = tk.StringVar()
        password_entry = tk.Entry(self, textvariable=password)
        password_label = tk.Label(self, text="Password:")
        button_1 = tk.Button(self, text="Teacher Login", command=lambda: master.check_login("Teacher"))
        button_2 = tk.Button(self, text="Student Login", command=lambda: master.check_login("USER"))
        label.grid(row=0, column=0, columnspan=8)
        username_label.grid(column=4, row=2)
        username_entry.grid(column=5, row=2)
        password_entry.grid(column=5, row=3)
        password_label.grid(column=4, row=3)
        button_1.grid(row=4, column=0, columnspan=8, pady=5)
        button_2.grid(row=5, column=0, columnspan=8, pady=5)


class LangPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        label = tk.Label(self, text="Please select your native language")
        self.language = tk.StringVar(self)
        self.language.set("Italian")
        menu = tk.OptionMenu(self, self.language, "Italian", "Polish", command=lambda x: master.switch_frame(MainPage,
                                                                                self.language.get()))
        menu.place(x=10, y=10)
        label.grid()
        menu.grid()

# TODO 1st image disappears after using speaker widget only tested mic no impact, only occurs on first run of Activity 1


class MainPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        master.score = 0
        master.correct = 0
        start_label = tk.Label(self, text="Main Menu - %s" % master.title)
        page_1_button = tk.Button(self, text="Subject Selector",
                                  command=lambda: master.switch_frame(SubjectSelection))
        page_4_button = tk.Button(self, text="Re-select native language",
                                  command=lambda: master.switch_frame(LangPage))
        page_5_button = tk.Button(self, text="Add new user", command=lambda: master.switch_frame(AddUser))
        page_6_button = tk.Button(self, text="Assign tasks", command=lambda: master.switch_frame(AssignTask))
        page_7_button = tk.Button(self, text="View assigned tasks", command=lambda: master.switch_frame(ViewTasks))
        page_8_button = tk.Button(self, text="Logout", command=lambda: master.switch_frame(LoginPage))
        page_9_button = tk.Button(self, text="View Tasks Completed", command=lambda: master.switch_frame(ViewStudentsTasks))
        exit_button = tk.Button(self, text="Quit", command=self.quit)
        start_label.grid()
        page_1_button.grid()
        page_4_button.grid(pady=1, padx=5)
        if master.title == "Teacher":
            page_5_button.grid()
            page_9_button.grid()
            page_6_button.grid()
        if master.user_level == "USER":
            page_7_button.grid()
        page_8_button.grid()
        exit_button.grid(pady=2)


class SubjectSelection(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="Please select the subject you want").grid(row=0)
        subjects = glob.glob("Italian/*")
        subjects_buttons = []
        for subject in subjects:
            subject_name = ""
            for i in range(8, len(subject)):
                subject_name += subject[i]
            button = tk.Button(self, text=subject_name, command=lambda: master.generate_dict(button.cget('text')))
            subjects_buttons.append(button)
        for button in subjects_buttons:
            button.grid(pady=2)


class ActivitySelector(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        master.image = tk.PhotoImage(file="Images/placeholder.png")
        label = tk.Label(self, text="Please select an activity")
        ac1 = tk.Button(self, text="Activity 1", command=lambda: master.switch_frame(Activity1))
        ac2 = tk.Button(self, text="Activity 2", command=lambda: master.switch_frame(Activity2))
        ac3 = tk.Button(self, text="Activity 3", command=lambda: master.switch_frame(Activity3))
        master.percentage_complete = str(int((master.index/len(master.words)) * 100))+'%'
        label.grid()
        ac1.grid()
        ac2.grid()
        ac3.grid(pady=2)


class Activity1(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        master.activity = "Activity 1"
        ac1_native_word = tk.Label(self, text="Native Word")
        ac1_eng_word = tk.Label(self, text="English Word")
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
                                     command=lambda: master.next_slide())
        return_button = tk.Button(self, text="Return to start page", command=lambda: master.switch_frame(MainPage))
        percentage_label = tk.Label(self, text=master.percentage_complete)
        ac1_native_word.grid(row=0, column=2)
        ac1_eng_word.grid(row=1, column=2)
        ac1_mic.grid(row=2, column=1, padx=10)
        percentage_label.grid(row=2, column=2)
        ac1_speaker.grid(row=2, column=3, padx=10)
        ac1_image.grid(row=3, rowspan=10, column=0, columnspan=5)
        ac1_start_button.grid(row=14, column=2)
        return_button.grid(row=15, column=2, pady=2)


class Activity2(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        master.activity = "Activity 2"
        ac2_intro = tk.Label(self, text="Please enter the word in English associated\n"
                                        "with this image then press enter")
        ac2_label_2 = tk.Label(self, image=master.image)
        ac2_native_word = tk.Label(self, text="Native Word")
        ac2_image_2 = tk.PhotoImage(file='Images/Speaker.png')
        ac2_speaker = tk.Button(self, image=ac2_image_2)
        ac2_speaker.image = ac2_image_2
        ac2_user = tk.StringVar()
        ac2_entry_1 = tk.Entry(self, textvariable=ac2_user)
        ac2_entry_1.bind("<Return>",
                         lambda x: master.next_slide())
        return_button = tk.Button(self, text="Return to start page", command=lambda: master.switch_frame(MainPage))
        percentage_label = tk.Label(self, text=master.percentage_complete)
        ac2_intro.grid(row=0, rowspan=2)
        ac2_speaker.grid(row=8)
        ac2_native_word.grid(row=2)
        percentage_label.grid(row=3)
        ac2_label_2.grid(row=4)
        ac2_entry_1.grid(row=10, rowspan=2, pady=6)
        return_button.grid(row=14)


class Activity3(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        master.index = 0
        master.activity = "Activity 3"
        self.image_dirs = []
        self.button_list = []
        self.image_dict = {}
        self.start_time = time.strftime("%H:%M:%S", time.localtime()).split(":")
        for i in range(1, len(master.words.keys()) + 1):
            self.image_dirs.append(tk.PhotoImage(file="Images/placeholder.png").subsample(3))
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
        last_name_label = tk.Label(self, text="Last name:")
        last_name = tk.StringVar()
        last_name_entry = tk.Entry(self, textvariable=last_name)
        position_label = tk.Label(self, text="Position")
        position = tk.StringVar()
        position_entry = tk.OptionMenu(self, position, "Student", "Teacher", command=lambda x: position.get())
        add_button = tk.Button(self, text="Add User", command=lambda: master.add_user(first_name.get(), last_name.get(),
                                                                                      position.get()))
        return_button = tk.Button(self, text="Return to MainPage", command=lambda: master.switch_frame(MainPage))
        intro.grid(row=0, column=0, columnspan=2)
        first_name_label.grid(row=1, column=0)
        first_name_entry.grid(row=1, column=1)
        last_name_label.grid(row=2, column=0)
        last_name_entry.grid(row=2, column=1)
        position_label.grid(row=3, column=0)
        position_entry.grid(row=3, column=1)
        add_button.grid(row=4, column=0, columnspan=2, pady=10)
        return_button.grid(row=5, column=0, columnspan=2)


''' 
 Provide users with a way of seeing their tasks 
 Teachers get list of students and select the subject and task
 Take list of students selected and give them tasks in db 
 Once subjects and users are selected an additional page switch selects the tasks
 Students have page where they see their tasks
 When the task of complete the tasks get removed from db
 How to present all users to teachers
'''


class AssignTask(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        scrollbar = tk.Scrollbar(self)
        label = tk.Label(self, text="Please click the users you want to assign the tasks to\n"
                                    "The users highlighted are the users selected")
        my_list = tk.Listbox(self, selectmode=tk.MULTIPLE, yscrollcommand=scrollbar.set, width=30, height=3)
        next_button = tk.Button(self, text="Next", command=lambda: master.get_users(use="Assign Tasks"))
        label.grid(row=0)
        my_list.grid(row=1, column=0, columnspan=3)
        scrollbar.config(command=my_list.yview)
        scrollbar.grid(column=3, row=1)
        next_button.grid(row=3)


class ViewTasks(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        label = tk.Label(self, text="Currently assigned tasks for (insert later)")
        list_box = tk.Listbox(self, height=5, selectmode=tk.MULTIPLE)
        return_button = tk.Button(self, text="Return to home page", command=lambda: master.switch_frame(MainPage))
        activity_button = tk.Button(self, text="Go to subject selector",
                                    command=lambda: master.switch_frame(SubjectSelection))
        complete_button = tk.Button(self, text="Mark as completed",
                command=lambda: master.switch_frame(MainPage))
        label.grid(row=0)
        list_box.grid(row=1)
        activity_button.grid(row=2)
        complete_button.grid(row=3)
        return_button.grid(row=4)


class ViewStudentsTasks(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        scrollbar = tk.Scrollbar(self)
        label = tk.Label(self, text="Please click the users you want to view their tasks completed\n"
                                    "the user highlighted is the user selected")
        my_list = tk.Listbox(self, selectmode=tk.BROWSE, yscrollcommand=scrollbar.set, width=30, height=3)
        next_button = tk.Button(self, text="Next", command=lambda: master.get_users(use="View Tasks"))
        label.grid(row=0)
        my_list.grid(row=1, column=0, columnspan=3)
        scrollbar.config(command=my_list.yview)
        scrollbar.grid(column=3, row=1)
        next_button.grid(row=3)


app = SampleApp()
app.mainloop()
