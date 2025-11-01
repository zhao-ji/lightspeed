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

@app.route('/sales', methods=['POST'])
def add_sales():
    req = request.json
    discount = req.get("discount", 0)
    if discount < 0:
            return jsonify({"error": "discount should not be negative"}), 400
    sales = req["sales"]
    for sale in sales:
        if "id" not in sale or not sale["id"]:
            return jsonify({"error": "product id should not be empty"}), 400
        if "quantity" not in sale or not sale["quantity"]:
            return jsonify({"error": "quantity should not be empty"}), 400

    conn = get_db_connection()
    # Construct the SQL query with placeholders for the IDs
    # The '?' placeholders will be replaced by the values from id_list
    placeholders = ','.join('?' * len(sales))
    sql_query = f"SELECT id, name, price FROM products WHERE id IN ({placeholders})"
    # Execute the query, passing the id_list as parameters
    products = conn.execute(sql_query, [sale["id"] for sale in sales]).fetchall()
    conn.commit()
    conn.close()

    total = 0
    products_dict = {product["id"]: product for product in products}
    for sale in sales:
        product = products_dict[sale["id"]]
        sale_total = int(sale["quantity"]) * product["price"]
        sale["total"] = sale_total
        total += sale_total

    if discount > 0:
        for sale in sales:
            sale["discount"] = round(discount / total * sale["total"], 2)
            sale["real_price"] = round(sale["total"] - sale["discount"], 2)

    return jsonify({
        "sales": sales,
        "total": total - discount,
    }), 201 # 201 Created

def main():
    init_database()
    app.run(debug=True, host="0.0.0.0", port="8001")


if __name__ == '__main__':
    main()
