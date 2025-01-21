import sqlite3, json, os; path = ""

json.dumps("", separators=(",", ":"))

def q():
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    try:
        cursor.execute('BEGIN')
        cursor.execute('INSERT INTO  () VALUES ()', ())
        cursor.execute('COMMIT')
    except sqlite3.Error as error:
        cursor.execute('ROLLBACK')
        return False, f' database error {error}'
    qd = []
    cursor.execute('SELECT * FROM Users WHERE email=?', (email, ))
    cursor.fetchone()[0]

    cursor.execute('SELECT MAX(id) FROM Users')