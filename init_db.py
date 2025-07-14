import sqlite3
from werkzeug.security import generate_password_hash

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Tabla de administradores
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS administradores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    
    # Tabla de docentes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS docentes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    
    # Tabla de archivos docentes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS archivos_docentes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        docente_id INTEGER NOT NULL,
        tipo TEXT NOT NULL,
        ruta_archivo TEXT NOT NULL,
        FOREIGN KEY (docente_id) REFERENCES docentes(id)
    )
    ''')
    
    # Tabla de cursos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cursos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL
    )
    ''')
    
    # Tabla de relación docente-curso
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS docente_curso (
        docente_id INTEGER NOT NULL,
        curso_id INTEGER NOT NULL,
        PRIMARY KEY (docente_id, curso_id),
        FOREIGN KEY (docente_id) REFERENCES docentes(id),
        FOREIGN KEY (curso_id) REFERENCES cursos(id)
    )
    ''')
    
    # Insertar admin por defecto
    cursor.execute("INSERT OR IGNORE INTO administradores (email, password) VALUES (?, ?)",
                  ('admin@unsaac.edu.pe', generate_password_hash('admin123')))
    
    # Insertar docente de ejemplo
    cursor.execute("INSERT OR IGNORE INTO docentes (nombre, email, password) VALUES (?, ?, ?)",
                  ('Jhoel Mamani', 'jhoel@unsaac.edu.pe', generate_password_hash('jhoel123')))
    
    # Insertar cursos de ejemplo
    cursor.execute("INSERT OR IGNORE INTO cursos (nombre) VALUES ('Algoritmos Paralelos')")
    cursor.execute("INSERT OR IGNORE INTO cursos (nombre) VALUES ('Base de Datos')")
    
    # Asignar cursos al docente
    cursor.execute("INSERT OR IGNORE INTO docente_curso (docente_id, curso_id) VALUES (1, 1)")
    cursor.execute("INSERT OR IGNORE INTO docente_curso (docente_id, curso_id) VALUES (1, 2)")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()