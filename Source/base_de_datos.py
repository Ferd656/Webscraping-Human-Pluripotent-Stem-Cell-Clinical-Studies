import sqlite3

def crear_base_datos(nombre_db="ensayos_clinicos.db"):
    conn = sqlite3.connect(nombre_db)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ensayos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            estado_clinico TEXT,
            tipo_celula TEXT,
            n_participantes INTEGER,
            fecha_inicio TEXT,
            fecha_conclusion TEXT
        )
    ''')

    conn.commit()
    conn.close()
