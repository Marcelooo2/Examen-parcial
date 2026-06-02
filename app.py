from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta_2024'

DB = 'database.db'

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        nombre TEXT NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        precio REAL,
        stock INTEGER,
        categoria TEXT
    )''')
    c.execute("INSERT OR IGNORE INTO usuarios (username, password, nombre) VALUES ('admin','1234','Administrador')")
    c.execute("INSERT OR IGNORE INTO productos VALUES (NULL,'P001','Laptop HP','Laptop 15 pulgadas Intel Core i5',2500.00,10,'Tecnología')")
    c.execute("INSERT OR IGNORE INTO productos VALUES (NULL,'P002','Mouse Logitech','Mouse inalámbrico ergonómico',89.90,50,'Periféricos')")
    c.execute("INSERT OR IGNORE INTO productos VALUES (NULL,'P003','Teclado Mecánico','Teclado mecánico RGB switches blue',199.90,25,'Periféricos')")
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = request.form['username']
        pwd  = request.form['password']
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (user, pwd))
        row = c.fetchone()
        conn.close()
        if row:
            session['usuario'] = row[1]
            session['nombre']   = row[3]
            return redirect(url_for('principal'))
        else:
            error = 'Usuario o contraseña incorrectos'
    return render_template('login.html', error=error)

@app.route('/principal')
def principal():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('principal.html', nombre=session['nombre'])

@app.route('/buscador')
def buscador():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('buscador.html')

@app.route('/api/buscar_producto', methods=['POST'])
def buscar_producto():
    codigo = request.json.get('codigo', '').upper()
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM productos WHERE codigo=?", (codigo,))
    row = c.fetchone()
    conn.close()
    if row:
        return jsonify({'encontrado': True, 'codigo': row[1], 'nombre': row[2],
                        'descripcion': row[3], 'precio': row[4],
                        'stock': row[5], 'categoria': row[6]})
    return jsonify({'encontrado': False})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)