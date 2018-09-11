import sqlite3
user_username = "sjohn"
user_password = "smith1"
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
    name = (user_username.title(), )
    print(name)
    c = conn.cursor()
    c.execute("SELECT permission_level FROM users WHERE first_name =?", name)

