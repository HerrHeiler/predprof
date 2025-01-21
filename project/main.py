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

    #item_amount_price {id: [amount, price]}
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Reports (
    id INTEGER PRIMARY KEY,
    text TEXT NOT NULL,
    date INTEGER
    )
    ''')
    connection.commit()
    
    connection.close()


def authorization(email: str, password: str):
    """
    autorization function
    requires email and password
    """
    if (not password) or (not email):
        return False, f'пустые данные {password, email}'
    connection = sqlite3.connect(path); cursor = connection.cursor()
    cursor.execute('SELECT password FROM Users WHERE email=?', (email,))
    if cursor.fetchone() is None: return False, 'email не существует'
    if sha256(password.encode()).hexdigest() != cursor.fetchone()[0]:
        return False, "Неверный пароль"
    return True

def registration(FIO: str, email: str, password: str):
    """
    registration function, used only for users, 
    requires user's data
    """
    if (not FIO) or (not password) or (not email):
        return False, f'пустые данные {FIO, password, email}'
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Users WHERE email=?', (email, ))
    if cursor.fetchone(): return False, 'email занят'
    try:
        cursor.execute('BEGIN')
        password_encode = sha256(password.encode()).hexdigest()
        list_of_items = json.dumps({})
        cursor.execute('SELECT MAX(id) FROM Users')
        id = cursor.fetchone()[0] + 1
        cursor.execute('INSERT INTO Users (id, FIO, email, password, role, list_of_items) VALUES (?, ?, ?, ?, ?, ?)', (id, FIO, email, password_encode, "user", list_of_items))
        cursor.execute('COMMIT')
    except sqlite3.Error as error:
        cursor.execute('ROLLBACK')
        return False, f'Ошибка при добавлении пользователя в базу данных {error}'
    return True


# admin's functions

def admin(email: str):
    """help function, checks that user is an admin"""
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute('SELECT role FROM Users WHERE email=?', (email, ))
    if cursor.fetchone() is None: return False, 'email не существует'
    if cursor.fetchone()[0] != "admin": return False, 'не админ'
    return True

def add_new_items(name: str, amount: int, email: str):
    """
    admin's function that adds new items to database
    requires name and amount of items and email of user who wants to add
    """
    if (not name) or (not amount) or (not email): return False, f'empty data {name, amount, email}'
    if (not admin(email)[0]): return admin(email)[1]
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute('SELECT MAX(id) FROM Items')
    id = cursor.fetchone()[0] + 1
    try:
        cursor.execute('BEGIN')
        cursor.execute('INSERT INTO Items (id, name, new, used, broken) VALUES (?, ?, ?, ?, ?)', (id, name, amount, 0, 0))
        cursor.execute('COMMIT')
    except sqlite3.Error as error:
        cursor.execute('ROLLBACK')
        return False, f'Ошибка при добавлении инвентаря в базу данных {error}'
    return True

def delete_broken(user_email: int, item_id: int, amount: int, email: str):
    if (not user_email) or (not item_id) or (not amount): return False, f'empty data {user_email, amount, item_id}'
    if (not admin(email)[0]): return admin(email)[1]
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute('SELECT list_of_items FROM Users WHERE email=?', (user_email))
    if cursor.fetchone() is None: return False, 'email не существует'
    items = dict(json.loads(cursor.fetchone[0]))
    if (not item_id in items.keys()): return False, f'у пользователя {user_email} нет такого {item_id} инвентаря'
    if amount > items[item_id][1]: return False, f'переданное кол-во {amount} больше существующего {items[item_id][-1]}'
    items[item_id][-1] -= amount
    items_str = json.dumps(items, separators=(",", ":"))
    try:
        cursor.execute('BEGIN')
        cursor.execute('UPDATE Users SET list_of_items = ? WHERE id = ?', (items_str, user_email))
        cursor.execute('COMMIT')
    except sqlite3.Error as error:
        cursor.execute('ROLLBACK')
        return False, f'Ошибка при изменении поля инвентаря у пользователя в базе данных {error}'
    return True

def change_name(item_id: int, new_name: str, email: str):
    if (not email) or (not item_id) or (not new_name): return False, f'empty data {email, new_name, item_id}'
    if (not admin(email)[0]): return admin(email)[1]
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute('SELECT name FROM Items WHERE id=?', (item_id, ))
    prev_name = cursor.fetchone[0]
    if prev_name == new_name: return False, 'одинаковые имена'
    try:
        cursor.execute('BEGIN')
        cursor.execute('UPDATE Items SET name = ? WHERE id = ?', (new_name, item_id))
        cursor.execute('COMMIT')
    except sqlite3.Error as error:
        cursor.execute('ROLLBACK')
        return False, f'Ошибка при изменении названия инвентаря {error}'
    return True

def attach_item_to_user(item_id: int, user_email: int, amount: int, email: str):
    if (not email) or (not item_id) or (not amount) or (not user_email): return False, f'empty data {email, amount, item_id, user_email}'
    if (not admin(email)[0]): return admin(email)[1]
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute('SELECT new, used FROM Items WHERE id=?', (item_id, ))
    (db_new, db_used) = cursor.fetchone()
    if amount > db_new: return False, f'запрашиваемое значение {amount} больше существующего {db_new}'
    db_used += amount; db_new -= amount
    cursor.execute('SELECT list_of_items FROM Users WHERE email=?', (user_email))
    list_of_items = dict(json.loads(cursor.fetchone()[0]))
    if item_id in list_of_items.keys():
        list_of_items[item_id][0] += amount
    else:
        list_of_items[item_id] = [amount, 0]
    list_of_items_str = json.dumps(list_of_items, separators=(",", ":"))
    try:
        cursor.execute('BEGIN')
        cursor.execute('UPDATE Items SET new, used = ? WHERE id = ?', (db_new, db_used, item_id))
        cursor.execute('UPDATE Users SET list_of_items = ? WHERE id = ?', (list_of_items_str, user_email))        
        cursor.execute('COMMIT')
    except sqlite3.Error as error:
        cursor.execute('ROLLBACK')
        return False, f'Ошибка при работе с бд {error}'
    return True

def create_plan(text: str, items: list, amounts: list, prices: list, deadline: int, email: str):
    if (not email) or (not items) or (not amounts) or (not prices): return False, f'empty data {email, amounts, items, prices}'
    if (not admin(email)[0]): return admin(email)[1]
    if len(items) != len(prices) or len(items) != len(amounts): return False, f'разные длины списков'
    start_date = datetime.datetime.timestamp(datetime.datetime.now())
    if deadline <= start_date: return False, f'wrong values of data {start_date} >= {deadline}'
    item_amount_price = {}
    for i in range(len(items)):
        item_amount_price[items[i]] = [amounts[i], prices[i]]
    item_amount_price_str = json.dumps(item_amount_price, separators=(",", ":"))
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute('SELECT MAX(id) FROM Users')
    id = cursor.fetchone()[0] + 1
    try:
        cursor.execute('BEGIN')
        cursor.execute('INSERT INTO Purchases (id, text, item_amount_price, start_date, deadline) VALUES (?, ?, ?, ?, ?)', (id, text, item_amount_price_str, start_date, deadline))
        cursor.execute('COMMIT')
    except sqlite3.Error as error:
        cursor.execute('ROLLBACK')
        return False, f' database error {error}'
    return True

def report(text: str, email: str):
    if (not email): return False, f'empty data {email}'
    if (not admin(email)[0]): return admin(email)[1]
    date = datetime.datetime.timestamp(datetime.datetime.now())
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute('SELECT MAX(id) FROM Reports')
    id = cursor.fetchone()[0] + 1
    try:
        cursor.execute('BEGIN')
        cursor.execute('INSERT INTO Reports (id, text, date) VALUES (?, ?, ?)', (id, text, date))
        cursor.execute('COMMIT')
    except sqlite3.Error as error:
        cursor.execute('ROLLBACK')
        return False, f' database error {error}'
    return True

# users' functions

def user(email: str):
    """help function, checks that user is an admin"""
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    info = cursor.execute('SELECT role FROM Users WHERE email=?', (email, ))
    if info.fetchone() is None:
        return False, 'email не существует'
    if info.fetchone()[0] != "user":
        return False, 'не пользователь'
    return True

def view_attached_items(email: str):
    if (not user(email)[0]): return user(email)[1]
    if not email: return False, f"empty data {email}"
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute('SELECT list_of_items FROM Users WHERE email=?', (email))
    return json.loads(cursor.fetchone()[0])

def request(text: str, amount: int, item_id: int, email: str):
    if (not user(email)[0]): return user(email)
    if (not email) or (not amount) or (not item_id): return False, f'empty data {amount} {item_id} {email}'
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute('SELECT MAX(id) FROM Requests')
    id = cursor.fetchone()[0] + 1
    try:
        cursor.execute('BEGIN')
        cursor.execute('INSERT INTO Requests (id, text, amount, item_id, user_email, status) VALUES (?, ?, ?, ?, ?, ?)', (id, text, amount, item_id, email, "unread"))
        cursor.execute('COMMIT')
    except sqlite3.Error as error:
        cursor.execute('ROLLBACK')
        return False, f'database error {error}'

def view_request_status(email: str):
    if (not user(email)[0]): return user(email)[1]
    if not email: return False, f"empty data {email}"
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute('SELECT list_of_items FROM Users WHERE email=?', (email))
    return json.loads(cursor.fetchone()[0])




if __name__ == "__main__" :
    deploy_function("iiii", "pwoef", "200")