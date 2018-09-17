import sqlite3
import tkinter as tk

# Provide users with a way of seeing their tasks
# How are tasks assigned?
# Teachers get list of students and select the subject and task
# Students have page where they see their tasks
# When the task of complete the tasks get removed from db
def get_users(users_selected, users):
    print(len(users_selected))
    print(users_selected)
    for i in users_selected:
        print(users[i])

root = tk.Tk()
scrollbar = tk.Scrollbar(root)
label = tk.Label(root, text="Please click the users you want to assign the tasks to\n"
                            "The users highlighted are the users selected")
my_list = tk.Listbox(root, selectmode=tk.MULTIPLE, yscrollcommand=scrollbar.set, width=30, height=3)
users = {}
conn = sqlite3.connect("test.db")
c = conn.cursor()
c.execute("SELECT user_id, first_name, last_name FROM users WHERE user_type = 'Student'")
list_index = 0
for i in c.fetchall():
    users[list_index] = (i[0], i[1], i[2])
    list_index += 1
    my_list.insert(tk.END, "UserID: %d Fullname: %s" % (i[0], str(i[1]+" "+i[2])))
conn.close()
next_button = tk.Button(root, text="Next", command=lambda: get_users(my_list.curselection(), users))  #Draws index in listbox
label.grid(row=0)
my_list.grid(row=1, column=0, columnspan=3)
scrollbar.config(command=my_list.yview)
scrollbar.grid(column=3, row=1)
next_button.grid(column=4)
tk.mainloop()
