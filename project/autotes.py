from main import delete_broken
import sqlite3, json

path = 'db/inventory_managment.db'

connection = sqlite3.connect(path)
cursor = connection.cursor()
pp = [[1, 23, 4], [2, 33, 0]]
list_of_items = json.dumps(pp, separators=(",", " "))
connection = sqlite3.connect(path)
cursor = connection.cursor()
# cursor.execute('BEGIN')
# cursor.execute('INSERT INTO Items (id, name, new, used, broken) VALUES (?, ?, ?, ?, ?)', (2, "name", 30, 2, 0))
# cursor.execute('COMMIT')
cursor.execute('SELECT new, used FROM Items WHERE id=?', (1, ))
# cursor.execute('SELECT list_of_items FROM Users WHERE id=?', (user_id))

print(cursor.fetchone())
connection.close()
# delete_broken(1, 1, 12, "iduw")