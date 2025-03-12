from flask import Flask, request, jsonify

import os, json, shutil, sqlite3, datetime
from hashlib import sha256
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

DATABASE = "modest_game.db"
DB_FOLDER = "./db"
DB_PATH = f"{DB_FOLDER}/{DATABASE}"

def deploy_function():
    if not os.path.exists(DB_FOLDER):
        os.mkdir(DB_FOLDER)
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Lights (
    date TEXT NOT NULL,
    lights TEXT NOT NULL
    )
    ''')

    #pulling dataset, i.e. {floor: [[false, true, false], [true, true, true], [false, false, false]]}
    set1 = {
        1: [[False], [True], [False, True, False, True], [False, False]],
        2: [[True], [True], [False, False, False, False], [False, False]],
        3: [[False], [False], [True, False, True, True], [True, True]],
        4: [[True], [True], [False, True, False, False], [False, False]]
        }
    set1_string = json.dumps(set1, separators=(",", ":"))
    date1 = datetime.datetime.strftime(datetime.date(2025, 1, 1))
    cursor.execute("""
            INSERT INTO Lights (date, lights)
            VALUES (?, ?)
        """, (date1, set1_string))
    
    set2 = {
        1: [[True], [False], [False]],
        2: [[True], [True], [True]]
    }
    set2_string = json.dumps(set2, separators=(",", ":"))
    date2 = datetime.datetime.strftime(datetime.date(2025, 1, 2))
    cursor.execute("""
            INSERT INTO Lights (date, lights)
            VALUES (?, ?)
        """, (date2, set2_string))
    
    set3 = {
        1: [[True, False, False, True]]
    }
    set3_string = json.dumps(set3, separators=(",", ":"))
    date3 = datetime.datetime.strftime(datetime.date(2025, 1, 3))
    cursor.execute("""
            INSERT INTO Lights (date, lights)
            VALUES (?, ?)
        """, (date3, set3_string))
    connection.close()

@app.route('/any', methods=['POST'])
def lights(date: str):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute('SELECT lights FROM Lights WHERE date=?', (date,))
    results = cursor.fetchone()
    if not results:
        return jsonify({"success": False, "message": "wrong date"}), 400
    result = results[0]
    lights = json.loads(result)
    connection.close()
    return jsonify(success=True, items=lights), 200