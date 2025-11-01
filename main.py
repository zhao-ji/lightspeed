import os
import sqlite3

from flask import Flask, jsonify, request

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

def serialize(rows):
    data = [dict(row) for row in rows]
    return jsonify(data)

@app.route('/products', methods=['GET'])
def get_products():
    """Get current products"""
    conn = get_db_connection()
    products = conn.execute('SELECT id, name, price FROM products').fetchall()
    conn.close()
    return serialize(products)

@app.route('/products', methods=['POST'])
def add_products():
    new_product = request.json
    if "name" not in new_product or not new_product["name"]:
        return jsonify({"error": "name should not be empty"}), 400
    if "price" not in new_product or not new_product["price"]:
        return jsonify({"error": "price should not be empty"}), 400

    conn = get_db_connection()
    data = (new_product["name"], new_product["price"])
    conn.execute('INSERT INTO products(name, price) values(?, ?)', data)
    conn.commit()
    conn.close()

    return jsonify(new_product), 201 # 201 Created

def main():
    init_database()
    app.run(debug=True, host="0.0.0.0", port="8001")


if __name__ == '__main__':
    main()
