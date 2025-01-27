from flask import Flask, request, jsonify

import bcrypt
from hashlib import sha256
from flask_cors import CORS
import sqlite3, json, shutil, os, datetime
from hashlib import sha256

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

DATABASE = 'sport_item.db'
DB_FOLDER = "./db"
DB_PATH = f"{DB_FOLDER}/{DATABASE}"

import sqlite3, json, shutil, os, datetime
from hashlib import sha256

path = 'db/inventory_managment.db'


def deploy_function(FIO: str, email: str, password: str):
    """
    Deploy function creates Users', Items', Requests', Complaints', Purchases', and Reports' tables.
    Requires the first admin's data.
    """
    # Создаём папку для базы данных, если её нет
    if not os.path.exists(DB_FOLDER):
        os.mkdir(DB_FOLDER)

    # Проверяем, существует ли уже база данных
    is_new_db = not os.path.exists(DB_PATH)

    # Подключаемся к базе данных
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # Создаём таблицы, если они ещё не созданы
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    FIO TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL,
    list_of_items TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    new INTEGER,
    used INTEGER,
    broken INTEGER
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    amount INTEGER,
    item_id INTEGER,
    user_email TEXT NOT NULL,
    status TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    amount INTEGER,
    item_id INTEGER,
    status TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    item_amount_price TEXT NOT NULL,
    start_date INTEGER,
    deadline INTEGER
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    date INTEGER
    )
    ''')

    # Если база данных новая, добавляем первого администратора
    if is_new_db:
        password_encode = sha256(password.encode()).hexdigest()
        list_of_items = json.dumps({})
        cursor.execute(
            'INSERT INTO Users (id, FIO, email, password, role, list_of_items) VALUES (?, ?, ?, ?, ?, ?)',
            (0, FIO, email, password_encode, "admin", list_of_items)
        )
        connection.commit()

    # Закрываем соединение
    connection.close()

    if is_new_db:
        print("Database deployed successfully and initialized with admin data.")
    else:
        print("Database already exists. No changes were made.")


@app.route('/login', methods=['POST'])
def authorization():
    """
    Authorization function
    Validates email and password.
    """
    data = request.get_json()  # Получаем данные из тела запроса
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return {"success": False, "message": "Пустые данные для авторизации."}, 400

    try:
        # Подключение к базе данных
        connection = sqlite3.connect(path)
        cursor = connection.cursor()

        # Проверка существования email
        cursor.execute('SELECT password FROM Users WHERE email = ?', (email,))
        result = cursor.fetchone()
        if result is None:
            return {"success": False, "message": "Email не существует."}, 404

        # Проверка пароля
        hashed_password = sha256(password.encode()).hexdigest()
        if hashed_password != result[0]:
            return {"success": False, "message": "Неверный пароль."}, 401

        return {"success": True, "message": "Авторизация успешна."}, 200
    except Exception as e:
        # Обработка ошибок, связанных с базой данных
        return {"success": False, "message": f"Ошибка базы данных: {str(e)}"}, 500
    finally:
        # Закрытие соединения с базой данных
        if connection:
            connection.close()

@app.route('/register', methods=['POST'])
def registration():
    """
    Registration function for user sign-up.
    Requires 'FIO', 'email', and 'password' in the request body.
    """
    data = request.json
    if not data:
        return jsonify({"success": False, "message": "Данные не предоставлены"}), 400

    FIO = data.get('FIO')
    email = data.get('email')
    password = data.get('password')

    # Проверка на обязательные поля
    if not FIO or not email or not password:
        return jsonify({"success": False, "message": "Отсутствуют обязательные поля"}), 400

    # Подключение к базе данных
    try:
        connection = sqlite3.connect(path)
        cursor = connection.cursor()

        # Проверка на существующий email
        cursor.execute('SELECT * FROM Users WHERE email = ?', (email,))
        if cursor.fetchone():
            return jsonify({"success": False, "message": "Этот email уже занят"}), 409

        # Хэширование пароля
        password_hash = sha256(password.encode()).hexdigest()

        # Получение нового ID
        cursor.execute('SELECT COALESCE(MAX(id), 0) FROM Users')
        new_id = cursor.fetchone()[0] + 1

        # Добавление пользователя
        cursor.execute("""
            INSERT INTO Users (id, FIO, email, password, role, list_of_items)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (new_id, FIO, email, password_hash, "user", json.dumps({})))

        connection.commit()
        return jsonify({"success": True, "message": "Регистрация прошла успешно"}), 201

    except sqlite3.Error as e:
        connection.rollback()
        return jsonify({"success": False, "message": f"Ошибка базы данных: {str(e)}"}), 500

    finally:
        connection.close()


# admin's functions

def admin(email: str):
    """help function, checks that user is an admin"""
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute('SELECT role FROM Users WHERE email=?', (email,))
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
        cursor.execute('INSERT INTO Items (id, name, new, used, broken) VALUES (?, ?, ?, ?, ?)',
                       (id, name, amount, 0, 0))
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
    cursor.execute('SELECT name FROM Items WHERE id=?', (item_id,))
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
    if (not email) or (not item_id) or (not amount) or (
    not user_email): return False, f'empty data {email, amount, item_id, user_email}'
    if (not admin(email)[0]): return admin(email)[1]
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute('SELECT new, used FROM Items WHERE id=?', (item_id,))
    (db_new, db_used) = cursor.fetchone()
    if amount > db_new: return False, f'запрашиваемое значение {amount} больше существующего {db_new}'
    db_used += amount;
    db_new -= amount
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

@app.route('/plan', methods=['POST'])
def create_plan():
    try:
        # Получение данных из запроса
        data = request.get_json()
        text = data.get('text')
        items = data.get('items', [])
        amounts = data.get('amounts', [])
        prices = data.get('prices', [])
        deadline = data.get('deadline')
        email = data.get('email')

        # Проверка обязательных полей
        if not email or not items or not amounts or not prices:
            return jsonify(success=False, message=f"Empty data: {email, items, amounts, prices}"), 400

        # Проверка пользователя-администратора
        admin_status = admin(email)
        if not admin_status[0]:
            return jsonify(success=False, message=admin_status[1]), 403

        # Проверка корректности данных
        if len(items) != len(prices) or len(items) != len(amounts):
            return jsonify(success=False, message="Длины списков items, amounts и prices не совпадают"), 400

        start_date = datetime.datetime.timestamp(datetime.datetime.now())
        if deadline <= start_date:
            return jsonify(success=False, message=f"Неверное значение даты: {start_date} >= {deadline}"), 400

        # Подготовка данных для сохранения
        item_amount_price = {items[i]: [amounts[i], prices[i]] for i in range(len(items))}
        item_amount_price_str = json.dumps(item_amount_price, separators=(",", ":"))

        # Работа с базой данных
        connection = sqlite3.connect(path)
        cursor = connection.cursor()
        cursor.execute('SELECT MAX(id) FROM Purchases')
        id = cursor.fetchone()[0] or 0
        id += 1

        cursor.execute('BEGIN')
        cursor.execute(
            'INSERT INTO Purchases (id, text, item_amount_price, start_date, deadline) VALUES (?, ?, ?, ?, ?)',
            (id, text, item_amount_price_str, start_date, deadline)
        )
        cursor.execute('COMMIT')
        return jsonify(success=True, message="Запрос успешно создан"), 201
    except sqlite3.Error as error:
        return jsonify(success=False, message=f"Database error: {error}"), 500
    except Exception as error:
        return jsonify(success=False, message=f"Error: {error}"), 500


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
    info = cursor.execute('SELECT role FROM Users WHERE email=?', (email,))
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


def request_item(text: str, amount: int, item_id: int, email: str):
    if (not user(email)[0]): return user(email)
    if (not email) or (not amount) or (not item_id): return False, f'empty data {amount} {item_id} {email}'
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute('SELECT MAX(id) FROM Requests')
    id = cursor.fetchone()[0] + 1
    try:
        cursor.execute('BEGIN')
        cursor.execute('INSERT INTO Requests (id, text, amount, item_id, user_email, status) VALUES (?, ?, ?, ?, ?, ?)',
                       (id, text, amount, item_id, email, "unread"))
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


if __name__ == "__main__":
    deploy_function("iiii", "pwoef@dsa.com", "200")
    app.run(debug=True, host='0.0.0.0', port=5000)