import sqlite3
import tkinter as tk

# Provide users with a way of seeing their tasks
# How are tasks assigned?
# Teachers get list of students and select the subject and task
# Students have page where they see their tasks
# When the task of complete the tasks get removed from db


conn = sqlite3.connect("test.db")
c = conn.cursor()
c.execute("ALTER TABLE users ADD tasks_completed integer")
conn.commit()
conn.close()
