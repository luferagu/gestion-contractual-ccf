import sqlite3

DB_NAME = "gestion_contractual.db"

def conectar_db():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def crear_tablas():

    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS procesos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_proceso TEXT UNIQUE,
        objeto TEXT,
        necesidad TEXT,
        justificacion TEXT,
        valor REAL,
        plazo INTEGER,
        fecha_estudio TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contratos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_proceso TEXT,
        tipo_contrato TEXT,
        supervisor TEXT,
        cdp TEXT,
        duracion TEXT,
        empresa TEXT,
        fecha_firma TEXT,
        FOREIGN KEY(id_proceso) REFERENCES procesos(id_proceso)
    )
    """)

    conn.commit()
    conn.close()
