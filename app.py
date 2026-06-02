from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
app.secret_key = 'clave_secreta_2024'
CORS(app, supports_credentials=True, origins=["https://tu-proyecto.vercel.app"])

DB = 'database.db'

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, password TEXT, nombre TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE, nombre TEXT,
        descripcion TEXT, precio REAL, stock INTEGER, categoria TEXT)''')
    c.execute("INSERT OR IGNORE INTO usuarios VALUES (NULL,'admin','1234','Administrador')")
    c.execute("INSERT OR IGNORE INTO productos VALUES (NULL,'P001','Laptop HP','Laptop i5 15 pulgadas',2500.00,10,'Tecnología')")
    c.execute("INSERT OR IGNORE INTO productos VALUES (NULL,'P002','Mouse Logitech','Mouse inalámbrico',89.90,50,'Periféricos')")
    c.execute("INSERT OR IGNORE INTO productos VALUES (NULL,'P003','Teclado Mecánico','Teclado RGB switches blue',199.90,25,'Periféricos')")
    conn.commit()
    conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios WHERE username=? AND password=?",
              (data['username'], data['password']))
    row = c.fetchone()
    conn.close()
    if row:
        session['usuario'] = row[1]
        session['nombre']  = row[3]
        return jsonify({'ok': True, 'nombre': row[3]})
    return jsonify({'ok': False, 'error': 'Credenciales incorrectas'})

@app.route('/api/session')
def check_session():
    if 'usuario' in session:
        return jsonify({'ok': True, 'nombre': session['nombre']})
    return jsonify({'ok': False})

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

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'ok': True})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)