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
    Deploy function creates Users', Items', Requests', Purchases', and Reports' tables.
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
    used TEXT,  
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
        cursor.execute('SELECT role FROM Users WHERE email = ?', (email,))
        role = cursor.fetchone()[0]
        return {"success": True, 
                "message": "Авторизация успешна.",
                "role": role,
                "email": email}, 200
        
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
@app.route('/login', methods=['POST'])
def admin(email: str):
    """help function, checks that user is an admin"""
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute('SELECT role FROM Users WHERE email=?', (email,))
    result = cursor.fetchone()  # Сохраняем результат в переменную
    
    if not result:
        return False, 'email не существует'
    
    role = result[0]  # Берем значение из сохраненного результата
    if role != "admin": 
        return False, 'не админ'
    return True, 'Успешно'

@app.route('/setitems', methods=['GET', 'POST'])
def add_new_items():
    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        amount = data.get('amount')
        email = data.get('email')

        if not name or not amount or not email:
            return jsonify(success=False, message='empty data'), 400

        connection = sqlite3.connect(path)
        cursor = connection.cursor()
        cursor.execute('SELECT MAX(id) FROM Items')
        result = cursor.fetchone()
        item_id = (result[0] + 1) if result[0] is not None else 1

        try:
            # Инициализируем used как JSON-массив
            used_json = json.dumps([])
            cursor.execute('BEGIN')
            cursor.execute(
                'INSERT INTO Items (id, name, new, used, broken) VALUES (?, ?, ?, ?, ?)',
                (item_id, name, amount, used_json, 0)
            )
            cursor.execute('COMMIT')
        except sqlite3.Error as error:
            cursor.execute('ROLLBACK')
            return jsonify(success=False, message=f"Ошибка при добавлении предмета: {str(error)}"), 500

        # Получаем обновленный список предметов
        cursor.execute('SELECT id, name, new, used, broken FROM Items')
        rows = cursor.fetchall()
        items = []
        for row in rows:
            items.append({
                'id': row[0],
                'name': row[1],
                'new': row[2],
                'used': row[3],  # Возвращаем сырую JSON строку
                'broken': row[4]
            })

        connection.close()
        return jsonify(success=True, items=items), 200

    elif request.method == 'GET':
        connection = sqlite3.connect(path)
        cursor = connection.cursor()
        cursor.execute('SELECT id, name, new, used, broken FROM Items')
        rows = cursor.fetchall()
        
        items = []
        for row in rows:
            items.append({
                'id': row[0],
                'name': row[1],
                'new': row[2],
                'used': row[3],  # Возвращаем сырую JSON строку
                'broken': row[4]
            })

        connection.close()
        return jsonify(success=True, items=items), 200
    
@app.route('/setitems', methods=['GET'])
def get_items():
    try:
        connection = sqlite3.connect(path)
        cursor = connection.cursor()
        cursor.execute('SELECT id, name, new, used, broken FROM Items')
        rows = cursor.fetchall()
        
        items = []
        for row in rows:
            # Проверка и исправление формата used
            used = row[3]
            try:
                json.loads(used)
            except:
                used = json.dumps([])
            
            items.append({
                'id': row[0],
                'name': row[1],
                'new': row[2],
                'used': used,
                'broken': row[4]
            })

        connection.close()
        return jsonify(success=True, items=items), 200
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500

@app.route('/users', methods=['GET'])
def get_users():
    try:
        connection = sqlite3.connect(path)
        cursor = connection.cursor()
        cursor.execute('SELECT email, FIO FROM Users WHERE role = "user"')
        users = [{'email': row[0], 'name': row[1]} for row in cursor.fetchall()]
        return jsonify(success=True, users=users), 200
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500

@app.route('/updateitem', methods=['PUT'])
def update_item():
    try:
        data = request.get_json()
        item_id = data.get('id')
        name = data.get('name')
        new_broken = data.get('broken')
        used_users = data.get('used', [])

        if not all([item_id, name, new_broken is not None]):
            return jsonify(success=False, message='Не заполнены обязательные поля'), 400

        connection = sqlite3.connect(path)
        cursor = connection.cursor()

        # Получаем текущие значения
        cursor.execute('SELECT new, used, broken FROM Items WHERE id = ?', (item_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify(success=False, message='Предмет не найден'), 404

        current_new = result[0]
        current_used_raw = result[1]
        current_broken = result[2]

        # Парсинг used
        try:
            current_used = json.loads(current_used_raw) if current_used_raw else []
        except:
            current_used = []

        # Валидация used
        valid_used = []
        total_used = 0
        for user in used_users:
            try:
                email = str(user['email'])
                amount = int(user['amount'])
                if amount < 0: continue
                valid_used.append({'email': email, 'amount': amount})
                total_used += amount
            except: continue

        # Проверка used
        used_diff = total_used - sum(u.get('amount', 0) for u in current_used)
        if used_diff > current_new:
            return jsonify(
                success=False,
                message=f'Недостаточно предметов для использования. Доступно: {current_new}'
            ), 400

        # Расчет изменений
        broken_diff = new_broken - current_broken
        if broken_diff > current_new:
            return jsonify(
                success=False,
                message=f'Недостаточно новых предметов. Доступно: {current_new}, требуется: {broken_diff}'
            ), 400

        updated_new = current_new - used_diff - broken_diff
        if updated_new < 0:
            return jsonify(success=False, message='Отрицательное количество новых предметов'), 400

        used_json = json.dumps(valid_used)

        try:
            cursor.execute('BEGIN')
            # Обновляем запись
            cursor.execute(
                'UPDATE Items SET name=?, new=?, used=?, broken=? WHERE id=?',
                (name, updated_new, used_json, new_broken, item_id)
            )

            # Обновляем пользователей
            cursor.execute('SELECT email, list_of_items FROM Users')
            for email, items_json in cursor.fetchall():
                items = json.loads(items_json) if items_json else {}
                if str(item_id) in items:
                    del items[str(item_id)]
                for user in valid_used:
                    if user['email'] == email:
                        items[str(item_id)] = user['amount']
                cursor.execute(
                    'UPDATE Users SET list_of_items=? WHERE email=?',
                    (json.dumps(items), email)
                )

            cursor.execute('COMMIT')
            return jsonify(success=True), 200

        except sqlite3.Error as error:
            cursor.execute('ROLLBACK')
            return jsonify(success=False, message=f"Ошибка базы данных: {str(error)}"), 500
        finally:
            connection.close()

    except Exception as e:
        return jsonify(success=False, message=f"Ошибка сервера: {str(e)}"), 500
    
def migrate_existing_items():
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    
    cursor.execute('SELECT id, used FROM Items')
    items = cursor.fetchall()
    
    for item_id, used in items:
        try:
            # Пробуем распарсить существующие данные
            json.loads(used)
        except:
            # Если не JSON, преобразуем в новый формат
            new_used = json.dumps([{'email': 'legacy', 'amount': int(used)}])
            cursor.execute('UPDATE Items SET used=? WHERE id=?', (new_used, item_id))
    
    connection.commit()
    connection.close()

@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    try:
        connection = sqlite3.connect(path)
        cursor = connection.cursor()
        
        # Удаляем предмет
        cursor.execute('DELETE FROM Items WHERE id = ?', (item_id,))
        
        # Удаляем упоминания у пользователей
        cursor.execute('SELECT email, list_of_items FROM Users')
        for email, items_json in cursor.fetchall():
            items = json.loads(items_json) if items_json else {}
            if str(item_id) in items:
                del items[str(item_id)]
                cursor.execute(
                    'UPDATE Users SET list_of_items = ? WHERE email = ?',
                    (json.dumps(items), email)
                )
        
        connection.commit()
        return jsonify(success=True), 200
        
    except sqlite3.Error as e:
        connection.rollback()
        return jsonify(success=False, message=f"Ошибка базы данных: {str(e)}"), 500
    finally:
        if connection:
            connection.close()

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
    db_used += amount
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

@app.route('/plan', methods=['GET', 'POST'])
def manage_plans():
    if request.method == 'POST':
        # Обработка POST запроса для создания плана
        data = request.get_json()
        text = data.get('text')
        items = data.get('items')
        amounts = data.get('amounts')
        prices = data.get('prices')
        deadline = data.get('deadline')
        email = data.get('email')

        if (not email) or (not items) or (not amounts) or (not prices):
            return jsonify(success=False, message='empty data'), 400


        if len(items) != len(prices) or len(items) != len(amounts):
            return jsonify(success=False, message='разные длины списков'), 400

        start_date = datetime.datetime.timestamp(datetime.datetime.now())
        if deadline <= start_date:
            return jsonify(success=False, message='wrong values of data'), 400

        item_amount_price = {}
        for i in range(len(items)):
            item_amount_price[items[i]] = [amounts[i], prices[i]]

        item_amount_price_str = json.dumps(item_amount_price, separators=(",", ":"))
        connection = sqlite3.connect(path)
        cursor = connection.cursor()
        cursor.execute('SELECT MAX(id) FROM Purchases')
        result = cursor.fetchone()
        if result[0] is None:
            id = 1  # Если нет записей, начинаем с 1
        else:
            id = result[0] + 1  # Если есть записи, увеличиваем максимальный id на 1

        try:
            cursor.execute('BEGIN')
            cursor.execute('INSERT INTO Purchases (id, text, item_amount_price, start_date, deadline) VALUES (?, ?, ?, ?, ?)',
                           (id, text, item_amount_price_str, start_date, deadline))
            cursor.execute('COMMIT')
        except sqlite3.Error as error:
            cursor.execute('ROLLBACK')
            return jsonify(success=False, message="Ошибка при добавлении в базу данных"), 500

        return jsonify(success=True), 200

    elif request.method == 'GET':
        connection = sqlite3.connect(path)
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM Purchases')
        plans = cursor.fetchall()
        
        # Отладочная информация
        print("Retrieved plans:", plans)

        return jsonify(plans), 200
    
@app.route('/plan/<int:plan_id>', methods=['DELETE'])
def delete_plan(plan_id):
    try:
        connection = sqlite3.connect(path)
        cursor = connection.cursor()
        
        cursor.execute('DELETE FROM Purchases WHERE id = ?', (plan_id,))
        connection.commit()
        
        if cursor.rowcount == 0:
            return jsonify(success=False, message="План не найден"), 404
            
        return jsonify(success=True), 200
        
    except sqlite3.Error as e:
        return jsonify(success=False, message=f"Ошибка базы данных: {str(e)}"), 500
    finally:
        if connection:
            connection.close()

@app.route('/reports', methods=['GET', 'POST'])
def handle_reports():
    if request.method == 'POST':
        data = request.get_json()
        text = data.get('text')
        email = data.get('email')  # Автоматически из токена

        if not text or len(text) < 10:
            return jsonify(success=False, message="Текст отчета слишком короткий"), 400

        connection = sqlite3.connect(path)
        cursor = connection.cursor()
        
        try:
            # ID generation
            cursor.execute('SELECT MAX(id) FROM Reports')
            report_id = (cursor.fetchone()[0] or 0) + 1
            
            # Insert report
            cursor.execute('''
                INSERT INTO Reports (id, text, date)
                VALUES (?, ?, ?)
            ''', (report_id, text, datetime.datetime.now().timestamp()))
            
            connection.commit()
            return jsonify(success=True), 200
            
        except sqlite3.Error as e:
            connection.rollback()
            return jsonify(success=False, message=f"Database error: {str(e)}"), 500
        finally:
            connection.close()

    elif request.method == 'GET':
        try:
            connection = sqlite3.connect(path)
            cursor = connection.cursor()
            cursor.execute('SELECT id, text, date FROM Reports ORDER BY date DESC')
            
            reports = []
            for row in cursor.fetchall():
                reports.append({
                    'id': row[0],
                    'text': row[1],
                    'date': row[2]
                })
                
            return jsonify(success=True, reports=reports), 200
            
        except Exception as e:
            return jsonify(success=False, message=str(e)), 500
        finally:
            if connection:
                connection.close()

@app.route('/reports/<int:report_id>', methods=['DELETE'])
def delete_report(report_id):
    try:
        connection = sqlite3.connect(path)
        cursor = connection.cursor()
        
        cursor.execute('DELETE FROM Reports WHERE id = ?', (report_id,))
        connection.commit()
        
        if cursor.rowcount == 0:
            return jsonify(success=False, message="Отчет не найден"), 404
            
        return jsonify(success=True), 200
        
    except sqlite3.Error as e:
        return jsonify(success=False, message=f"Ошибка базы данных: {str(e)}"), 500
    finally:
        if connection:
            connection.close()
# users' functions

def user(email: str):
    """help function, checks that user is an admin"""
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute('SELECT role FROM Users WHERE email=?', (email,))
    result = cursor.fetchone()
    
    if not result:
        return False, 'email не существует'
    
    role = result[0]
    if role != "user":
        return False, 'не пользователь'
    return True, 'Успешно'

def view_attached_items(email: str):
    if (not user(email)[0]): return user(email)[1]
    if not email: return False, f"empty data {email}"
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute('SELECT list_of_items FROM Users WHERE email=?', (email))
    return json.loads(cursor.fetchone()[0])


@app.route('/allrequests', methods=['GET'])
def get_all_requests():
    try:
        connection = sqlite3.connect(path)
        cursor = connection.cursor()
        
        cursor.execute('''
            SELECT r.id, r.text, r.amount, r.item_id, r.user_email, r.status, u.FIO, i.name 
            FROM Requests r
            LEFT JOIN Users u ON r.user_email = u.email
            LEFT JOIN Items i ON r.item_id = i.id
            ORDER BY r.id DESC
        ''')
        
        requests = []
        for row in cursor.fetchall():
            requests.append({
                'id': row[0],
                'text': row[1],
                'amount': row[2],
                'item_id': row[3],
                'user_email': row[4],
                'status': row[5],
                'user_name': row[6] or 'Неизвестный пользователь',
                'item_name': row[7] or 'Удалённый предмет'
            })
            
        return jsonify(success=True, requests=requests), 200
        
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500
    finally:
        if connection:
            connection.close()

@app.route('/requests/<int:request_id>', methods=['PUT'])
def update_request_status(request_id):
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status or new_status not in ['unread', 'approved', 'rejected']:
            return jsonify(success=False, message='Некорректный статус'), 400

        connection = sqlite3.connect(path)
        cursor = connection.cursor()
        
        cursor.execute('''
            UPDATE Requests 
            SET status = ?
            WHERE id = ?
        ''', (new_status, request_id))
        
        connection.commit()
        return jsonify(success=True), 200
        
    except sqlite3.Error as e:
        return jsonify(success=False, message=f"Ошибка базы данных: {str(e)}"), 500
    finally:
        if connection:
            connection.close()


def view_request_status(email: str):
    if (not user(email)[0]): return user(email)[1]
    if not email: return False, f"empty data {email}"
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute('SELECT list_of_items FROM Users WHERE email=?', (email))
    return json.loads(cursor.fetchone()[0])

@app.route('/setuseritems', methods=['GET'])
def get_user_items():
    try:
        connection = sqlite3.connect(path)
        cursor = connection.cursor()
        cursor.execute('SELECT id, name, new FROM Items')
        rows = cursor.fetchall()
        
        items = []
        for row in rows:
            items.append({
                'id': row[0],
                'name': f"{row[1]} (Доступно: {row[2]})",
                'new': row[2]
            })

        connection.close()
        return jsonify(success=True, items=items), 200
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500

@app.route('/requests', methods=['GET', 'POST'])
def handle_requests():
    if request.method == 'POST':
        # Обработка создания заявки
        data = request.get_json()
        text = data.get('text')
        amount = data.get('amount')
        item_id = data.get('item_id')
        email = data.get('email')

        # Проверка авторизации
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify(success=False, message='Требуется авторизация'), 401
        
        # Проверка существования пользователя
        connection = sqlite3.connect(path)
        cursor = connection.cursor()
        cursor.execute('SELECT email FROM Users WHERE email = ?', (email,))

        if not all([text, amount, item_id, email]):
            return jsonify(success=False, message='Не заполнены обязательные поля'), 400

        try:
            # Проверка доступного количества
            cursor.execute('SELECT new FROM Items WHERE id = ?', (item_id,))
            item = cursor.fetchone()
            if not item:
                return jsonify(success=False, message='Предмет не найден'), 404
                
            available = item[0]
            if int(amount) > available:
                return jsonify(success=False, 
                             message=f'Недостаточно предметов. Доступно: {available}'), 400

            # Создание заявки
            cursor.execute('SELECT MAX(id) FROM Requests')
            request_id = (cursor.fetchone()[0] or 0) + 1
            
            cursor.execute('''
                INSERT INTO Requests (id, text, amount, item_id, user_email, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (request_id, text, amount, item_id, email, 'unread'))
            
            connection.commit()
            return jsonify(success=True), 200
            
        except sqlite3.Error as e:
            connection.rollback()
            return jsonify(success=False, message=f"Ошибка базы данных: {str(e)}"), 500
        finally:
            connection.close()

    elif request.method == 'GET':
        # Обработка получения заявок
        try:
            email = request.args.get('email')
            if not email:
                return jsonify(success=False, message='Не указан email'), 400

            connection = sqlite3.connect(path)
            cursor = connection.cursor()
            
            cursor.execute('''
                SELECT r.id, r.text, r.amount, r.status, i.name 
                FROM Requests r
                JOIN Items i ON r.item_id = i.id
                WHERE r.user_email = ?
                ORDER BY r.id DESC
            ''', (email,))
            
            requests = []
            for row in cursor.fetchall():
                requests.append({
                    'id': row[0],
                    'text': row[1],
                    'amount': row[2],
                    'status': row[3],
                    'item_name': row[4]
                })
                
            return jsonify(success=True, requests=requests), 200
            
        except Exception as e:
            return jsonify(success=False, message=str(e)), 500
        finally:
            if connection:
                connection.close()

@app.route('/requests/<int:request_id>', methods=['DELETE'])
def delete_request(request_id):
    try:
        connection = sqlite3.connect(path)
        cursor = connection.cursor()
        
        cursor.execute('DELETE FROM Requests WHERE id = ?', (request_id,))
        connection.commit()
        
        if cursor.rowcount == 0:
            return jsonify(success=False, message="Заявка не найдена"), 404
            
        return jsonify(success=True), 200
        
    except sqlite3.Error as e:
        return jsonify(success=False, message=f"Ошибка базы данных: {str(e)}"), 500
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    deploy_function("iiii", "pwoef@dsa.com", "200")
    migrate_existing_items()
    app.run(debug=True, host='0.0.0.0', port=5000)