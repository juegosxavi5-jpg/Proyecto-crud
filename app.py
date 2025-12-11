from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
from psycopg2 import Error
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'clave-secreta-desarrollo')

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'dpg-d4ta7j56ubrc73ehbn4g-a.frankfurt-postgres.render.com',
    'user': 'xavi',
    'password': 'RO2D74OsWx2ulRGM81YZ0dvS3X0lnevP',
    'database': 'tareas_nut8',
    'port': 5432 
}

def get_db_connection():
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def init_db():
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tareas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(200) NOT NULL
            )
        ''')
        connection.commit()
        cursor.close()
        connection.close()

@app.route('/')
def index():
    connection = get_db_connection()
    tareas = []
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM tareas ORDER BY id DESC')
        tareas = cursor.fetchall()
        cursor.close()
        connection.close()
    return render_template('index.html', tareas=tareas)

@app.route('/agregar', methods=['POST'])
def agregar():
    name = request.form.get('name')
    if name:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute('INSERT INTO tareas (name) VALUES (%s)', (name,))
            connection.commit()
            cursor.close()
            connection.close()
            flash('Tarea agregada correctamente', 'success')
    else:
        flash('El nombre de la tarea no puede estar vacío', 'error')
    return redirect(url_for('index'))

@app.route('/modificar/<int:id>', methods=['GET', 'POST'])
def modificar(id):
    connection = get_db_connection()
    if request.method == 'POST':
        name = request.form.get('name')
        if name and connection:
            cursor = connection.cursor()
            cursor.execute('UPDATE tareas SET name = %s WHERE id = %s', (name, id))
            connection.commit()
            cursor.close()
            connection.close()
            flash('Tarea modificada correctamente', 'success')
            return redirect(url_for('index'))
    
    tarea = None
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM tareas WHERE id = %s', (id,))
        tarea = cursor.fetchone()
        cursor.close()
        connection.close()
    
    return render_template('modificar.html', tarea=tarea)

@app.route('/eliminar/<int:id>')
def eliminar(id):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute('DELETE FROM tareas WHERE id = %s', (id,))
        connection.commit()
        cursor.close()
        connection.close()
        flash('Tarea eliminada correctamente', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))