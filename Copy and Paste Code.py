import sqlite3
import tkinter as tk

# Provide users with a way of seeing their tasks
# How are tasks assigned?
# Teachers get list of students and select the subject and task
# Students have page where they see their tasks
# When the task of complete the tasks get removed from db

def task_complete(tasks, task_list):
    conn = sqlite3.connect("test.db")
    c = conn.cursor()
    for task in tasks:
        task_list.remove(task)
    c.execute("UPDATE users SET tasks = ? WHERE user_id = ?", (str(task_list), 7,))
    conn.commit()
    conn.close()


root = tk.Tk()
conn = sqlite3.connect("test.db")
c = conn.cursor()
c.execute("SELECT first_name, last_name, tasks FROM users WHERE user_id = '%d'" % 7)
first_name, last_name, tasks = c.fetchall()[0]
full_name = "%s %s" % (first_name, last_name)
label = tk.Label(text="Currently assigned tasks for %s:" % full_name)
list_box = tk.Listbox(height=5, selectmode=tk.MULTIPLE)
tasks = tasks.split("'")
new_list = []
for i in tasks:
    if str.isalpha(i[0]) is True:
        new_list.append(i)
for data in new_list:
    list_box.insert(tk.END, data)

complete_button = tk.Button(text="Mark as completed")
conn.close()
label.grid(row=0)
list_box.grid(row=1)
complete_button.grid(row=3)
root.mainloop()