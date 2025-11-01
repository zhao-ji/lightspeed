from flask import Flask, jsonify, request
import sqlite3
import os

app = Flask(__name__)

DATABASE_PATH = 'database/products.db'

def init_database():
    """Initialize database with schema if it doesn't exist"""
    if not os.path.exists('database'):
        os.makedirs('database')

    conn = sqlite3.connect(DATABASE_PATH)
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.close()

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/products', methods=['GET'])
def get_products():
    """Get current products"""
    conn = get_db_connection()
    products = conn.execute('SELECT id, name, price FROM products').fetchall()
    conn.close()
    return jsonify(products)

def main():
    init_database()
    app.run(debug=True, host="0.0.0.0", port="8001")


if __name__ == '__main__':
    main()
