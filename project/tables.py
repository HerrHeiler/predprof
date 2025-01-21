import sqlite3, json, shutil, os, datetime
from hashlib import sha256

path = 'db/inventory_managment.db'

def deploy_function(FIO: str, email: str, password: str):
"""
deploy function creates Users', items', requests' and complaints' databases
requires first admin's data
"""
if "db" in os.listdir("./"):
    shutil.rmtree("./db")
os.mkdir("./db")
connection = sqlite3.connect(path)
cursor = connection.cursor()
#role: admin/user
#list_of_items {id: [used, broken]}
cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
FIO TEXT NOT NULL,
email TEXT NOT NULL,
password TEXT NOT NULL,
role TEXT NOT NULL,
list_of_items TEXT NOT NULL
)
''')
password_encode = sha256(password.encode()).hexdigest()
list_of_items = json.dumps({})
cursor.execute('INSERT INTO Users (id, FIO, email, password, role, list_of_items) VALUES (?, ?, ?, ?, ?, ?)', (0, FIO, email, password_encode, "admin", list_of_items))
connection.commit()

# status: new/used/broken
cursor.execute('''
CREATE TABLE IF NOT EXISTS Items (
id INTEGER PRIMARY KEY,
name TEXT NOT NULL,
new INTEGER,
used INTEGER,
broken INTEGER
)
''')
connection.commit()

# status: unread/accepted/denied
cursor.execute('''
CREATE TABLE IF NOT EXISTS Requests (
id INTEGER PRIMARY KEY,
text TEXT NOT NULL,
amount INTEGER,
item_id INTEGER,
user_email TEXT NOT NULL,
status TEXT NOT NULL
)
''')
connection.commit()

# status: unread/accepted/denied
cursor.execute('''
CREATE TABLE IF NOT EXISTS Complaints (
id INTEGER PRIMARY KEY,
text TEXT NOT NULL,
amount INTEGER,
item_id INTEGER,
status TEXT NOT NULL
)
''')
connection.commit()

#item_amount_price {id: [amount, price]}
cursor.execute('''
CREATE TABLE IF NOT EXISTS Purchases (
id INTEGER PRIMARY KEY,
text TEXT NOT NULL,
item_amount_price TEXT NOT NULL,
start_date INTEGER,
deadline INTEGER
)
''')
connection.commit()