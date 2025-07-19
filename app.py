from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
from reportlab.pdfgen import canvas
from io import BytesIO
import pandas as pd
from flask import send_file  # Añade esto junto a las otras importaciones

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Conexión a la base de datos
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']
        
        conn = get_db_connection()
        
        if user_type == 'admin':
            admin = conn.execute('SELECT * FROM administradores WHERE email = ?', (email,)).fetchone()
            if admin and check_password_hash(admin['password'], password):
                session['user_id'] = admin['id']
                session['user_type'] = 'admin'
                conn.close()
                return redirect(url_for('admin_dashboard'))
        else:
            docente = conn.execute('SELECT * FROM docentes WHERE email = ?', (email,)).fetchone()
            if docente and check_password_hash(docente['password'], password):
                session['user_id'] = docente['id']
                session['user_type'] = 'docente'
                conn.close()
                return redirect(url_for('perfil_docente', docente_id=docente['id']))
        
        conn.close()
        flash('Credenciales incorrectas', 'error')
        return redirect(url_for('login'))
    
    return render_template('login.html')

# Perfil docente
@app.route('/docente/<int:docente_id>')
def perfil_docente(docente_id):
    if 'user_type' not in session or session['user_type'] != 'docente' or session['user_id'] != docente_id:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    docente = conn.execute('SELECT * FROM docentes WHERE id = ?', (docente_id,)).fetchone()
    archivos = conn.execute('SELECT * FROM archivos_docentes WHERE docente_id = ?', (docente_id,)).fetchall()
    cursos = conn.execute('''
        SELECT c.id, c.nombre 
        FROM cursos c
        JOIN docente_curso dc ON c.id = dc.curso_id
        WHERE dc.docente_id = ?
    ''', (docente_id,)).fetchall()
    conn.close()
    
    return render_template('perfil.html', docente=docente, archivos=archivos, cursos=cursos)

# Subir archivos (docente)
@app.route('/subir_archivo/<int:docente_id>', methods=['POST'])
def subir_archivo(docente_id):
    if 'user_type' not in session or session['user_type'] != 'docente' or session['user_id'] != docente_id:
        return redirect(url_for('login'))
    
    if 'archivo' not in request.files:
        flash('No se seleccionó ningún archivo', 'error')
        return redirect(url_for('perfil_docente', docente_id=docente_id))
    
    archivo = request.files['archivo']
    tipo_archivo = request.form['tipo_archivo']
    
    if archivo.filename == '':
        flash('No se seleccionó ningún archivo', 'error')
        return redirect(url_for('perfil_docente', docente_id=docente_id))
    
    if archivo and allowed_file(archivo.filename):
        filename = secure_filename(f"{docente_id}_{tipo_archivo}_{archivo.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        archivo.save(filepath)
        
        conn = get_db_connection()
        conn.execute('DELETE FROM archivos_docentes WHERE docente_id = ? AND tipo = ?', 
                     (docente_id, tipo_archivo))
        conn.execute('INSERT INTO archivos_docentes (docente_id, tipo, ruta_archivo) VALUES (?, ?, ?)',
                    (docente_id, tipo_archivo, filename))
        conn.commit()
        conn.close()
        
        flash('Archivo subido correctamente', 'success')
    else:
        flash('Solo se permiten archivos PDF', 'error')
    
    return redirect(url_for('perfil_docente', docente_id=docente_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['pdf']

# Página de curso
@app.route('/curso/<int:docente_id>/<int:curso_id>')
def curso(docente_id, curso_id):
    if 'user_type' not in session or session['user_type'] != 'docente' or session['user_id'] != docente_id:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    curso = conn.execute('SELECT * FROM cursos WHERE id = ?', (curso_id,)).fetchone()
    conn.close()
    
    return render_template('curso.html', curso=curso)

# Panel del administrador
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    total_docentes = conn.execute('SELECT COUNT(*) FROM docentes').fetchone()[0]
    total_cursos = conn.execute('SELECT COUNT(*) FROM cursos').fetchone()[0]
    conn.close()
    
    return render_template('admin/dashboard.html', 
                         total_docentes=total_docentes, 
                         total_cursos=total_cursos)

# Gestión de docentes (admin)
@app.route('/admin/docentes')
def gestion_docentes():
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    docentes = conn.execute('SELECT * FROM docentes').fetchall()
    conn.close()
    
    return render_template('admin/gestion_docentes.html', docentes=docentes)

# Agregar docente (admin)
@app.route('/admin/agregar_docente', methods=['GET', 'POST'])
def agregar_docente():
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO docentes (nombre, email, password) VALUES (?, ?, ?)',
                        (nombre, email, password))
            conn.commit()
            flash('Docente agregado correctamente', 'success')
        except sqlite3.IntegrityError:
            flash('El correo ya está registrado', 'error')
        finally:
            conn.close()
        
        return redirect(url_for('gestion_docentes'))
    
    return render_template('admin/agregar_docente.html')

#asignar cursos
@app.route('/admin/asignar_cursos', methods=['GET', 'POST'])
def asignar_cursos():
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    if request.method == 'POST':
        docente_id = request.form['docente_id']
        curso_id = request.form['curso_id']
        
        try:
            conn.execute('INSERT OR IGNORE INTO docente_curso (docente_id, curso_id) VALUES (?, ?)', 
                         (docente_id, curso_id))
            conn.commit()
            flash('Curso asignado correctamente', 'success')
        except sqlite3.IntegrityError:
            flash('Esta asignación ya existe', 'error')
        
        return redirect(url_for('asignar_cursos'))
    
    # Obtener docentes y cursos para el formulario
    docentes = conn.execute('SELECT id, nombre FROM docentes').fetchall()
    cursos = conn.execute('SELECT id, nombre FROM cursos').fetchall()
    conn.close()
    
    return render_template('admin/asignar_cursos.html', docentes=docentes, cursos=cursos)

#generar reportes
@app.route('/admin/generar_reportes', methods=['GET', 'POST'])
def generar_reportes():
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        report_type = request.form.get('report_type')
        conn = get_db_connection()
        
        try:
            if report_type == 'docentes':
                data = conn.execute('SELECT id, nombre, email FROM docentes').fetchall()
                filename = 'reporte_docentes'
                columns = ['ID', 'Nombre', 'Email']
                
            elif report_type == 'cursos':
                data = conn.execute('''
                    SELECT c.nombre AS curso, d.nombre AS docente 
                    FROM cursos c
                    JOIN docente_curso dc ON c.id = dc.curso_id
                    JOIN docentes d ON d.id = dc.docente_id
                ''').fetchall()
                filename = 'reporte_cursos'
                columns = ['Curso', 'Docente']
                
            elif report_type == 'archivos':
                data = conn.execute('''
                    SELECT d.nombre AS docente, a.tipo, a.ruta_archivo
                    FROM archivos_docentes a
                    JOIN docentes d ON d.id = a.docente_id
                ''').fetchall()
                filename = 'reporte_archivos'
                columns = ['Docente', 'Tipo', 'Archivo']
            
            # Convertir a lista de diccionarios
            data = [dict(row) for row in data]
            
            if request.form.get('format') == 'pdf':
                from reportlab.lib.pagesizes import letter
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
                
                buffer = BytesIO()
                pdf = SimpleDocTemplate(buffer, pagesize=letter)
                
                # Preparar datos para la tabla
                table_data = [columns] + [[str(item[col]) for col in item.keys()] for item in data]
                
                # Crear tabla
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), '#800000'),
                    ('TEXTCOLOR', (0, 0), (-1, 0), (1, 1, 1)),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), '#f5f5f5'),
                    ('GRID', (0, 0), (-1, -1), 1, '#cccccc')
                ]))
                
                pdf.build([table])
                buffer.seek(0)
                return send_file(
                    buffer,
                    as_attachment=True,
                    download_name=f'{filename}.pdf',
                    mimetype='application/pdf'
                )
                
            else:  # Excel
                import pandas as pd
                
                output = BytesIO()
                df = pd.DataFrame(data)
                df.to_excel(output, index=False, engine='openpyxl')
                output.seek(0)
                
                return send_file(
                    output,
                    as_attachment=True,
                    download_name=f'{filename}.xlsx',
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                
        finally:
            conn.close()

    return render_template('admin/generar_reportes.html')
#crear curso
@app.route('/admin/crear_curso', methods=['GET', 'POST'])
def crear_curso():
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        nombre_curso = request.form['nombre']
        
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO cursos (nombre) VALUES (?)', (nombre_curso,))
            conn.commit()
            flash('Curso creado exitosamente', 'success')
        except sqlite3.IntegrityError:
            flash('Este curso ya existe', 'error')
        finally:
            conn.close()
        
        return redirect(url_for('crear_curso'))

    return render_template('admin/crear_curso.html')
# Listar cursos (ya lo tienes)
@app.route('/admin/cursos')
def listar_cursos():
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursos = conn.execute('SELECT * FROM cursos ORDER BY nombre').fetchall()
    conn.close()
    
    return render_template('admin/listar_cursos.html', cursos=cursos)

# Eliminar curso
@app.route('/admin/eliminar_curso/<int:curso_id>', methods=['POST'])
def eliminar_curso(curso_id):
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    try:
        # Verificar si el curso está asignado a docentes primero
        asignaciones = conn.execute('SELECT COUNT(*) FROM docente_curso WHERE curso_id = ?', (curso_id,)).fetchone()[0]
        
        if asignaciones > 0:
            flash('No se puede eliminar: el curso está asignado a docentes', 'error')
        else:
            conn.execute('DELETE FROM cursos WHERE id = ?', (curso_id,))
            conn.commit()
            flash('Curso eliminado correctamente', 'success')
    finally:
        conn.close()
    
    return redirect(url_for('listar_cursos'))

# Editar curso
@app.route('/admin/editar_curso/<int:curso_id>', methods=['GET', 'POST'])
def editar_curso(curso_id):
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    
    if request.method == 'POST':
        nuevo_nombre = request.form['nombre']
        try:
            conn.execute('UPDATE cursos SET nombre = ? WHERE id = ?', (nuevo_nombre, curso_id))
            conn.commit()
            flash('Curso actualizado correctamente', 'success')
            return redirect(url_for('listar_cursos'))
        except sqlite3.IntegrityError:
            flash('Ya existe un curso con ese nombre', 'error')
    
    curso = conn.execute('SELECT * FROM cursos WHERE id = ?', (curso_id,)).fetchone()
    conn.close()
    
    if not curso:
        flash('Curso no encontrado', 'error')
        return redirect(url_for('listar_cursos'))
    
    return render_template('admin/editar_curso.html', curso=curso)
#Agrega esta ruta para mostrar todos los cursos

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists('database.db'):
        from init_db import init_db
        init_db()
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)