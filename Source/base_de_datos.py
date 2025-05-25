import sqlite3

def inicializar_repositorio(db_path="ensayos_clinicos.db", repositorio = "ensayos_PSC"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    if repositorio == "ensayos_PSC":
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS ensayos_PSC (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url VARCHAR(80),
                estudio_clinico TEXT,
                tipo_estudio VARCHAR(16),
                fase_estudio_clinico VARCHAR(32),
                condicion_primaria_estudio VARCHAR(32),
                condicion_secundaria_estudio VARCHAR(32),
                tipo_celula VARCHAR(32),
                pais VARCHAR(16),
                n_participantes INTEGER,
                edad_min_participante INTEGER,
                edad_max_participante INTEGER,
                genero_participante VARCHAR(32),
                n_patrocinadores INTEGER,
                fecha_inicio DATE,
                fecha_conclusion DATE
            )
        ''')
    else:
        #Para el caso en que haya que inicializar más repositositorios a través del curso
        print(f"Falta definir la sentencia SQL para inicializar el repositorio '{repositorio}'.")
    conn.commit()
    conn.close()

def agregar_registro_psc(data, db_path):
    inicializar_repositorio(db_path = db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Primero revisamos si ya el registro fue incluido con anterioridad
    cursor.execute("SELECT url FROM ensayos_PSC WHERE url = ? LIMIT 1", (data["url"],))
    ya_existe = cursor.fetchone() is not None

    if not ya_existe:
        columnas = ', '.join(data.keys())
        variables = ', '.join(['?'] * len(data))
        sql = f'INSERT INTO ensayos_PSC ({columnas}) VALUES ({variables})'
        cursor.execute(sql, tuple(data.values()))
        conn.commit()
        print("Nuevo registro añadido a 'ensayos_PSC'")

    conn.close()
