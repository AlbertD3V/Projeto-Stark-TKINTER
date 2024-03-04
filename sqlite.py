import sqlite3


conn = sqlite3.connect('BaseData.db')


cursor = conn.cursor()


cursor.execute('''CREATE TABLE IF NOT EXISTS tarefas
                  (id INTEGER PRIMARY KEY, descricao TEXT, data_inicio TEXT, data_termino TEXT, status TEXT)''')


conn.commit()


conn.close()
