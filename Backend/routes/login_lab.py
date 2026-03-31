from flask import Blueprint, request, jsonify, session
import sqlite3
import hashlib
import uuid
import json

login_lab_bp = Blueprint('login_lab', __name__)

# Session key for storing database connections
DB_SESSION_KEY = 'login_lab_db'
PRODUCTS_DB_KEY = 'login_lab_products'
ORDERS_DB_KEY = 'login_lab_orders'
ACCOUNTS_DB_KEY = 'login_lab_accounts'

# Sample data for different pages
SAMPLE_PRODUCTS = [
    (1, 'Laptop', 999.99),
    (2, 'Mouse', 25.50),
    (3, 'Keyboard', 75.00),
    (4, 'Monitor', 299.99),
    (5, 'USB Cable', 9.99)
]

SAMPLE_ORDERS = [
    (1, 'admin', 'Laptop', 1),
    (2, 'admin', 'Mouse', 2),
    (3, 'user', 'Keyboard', 1),
    (4, 'user', 'USB Cable', 3),
    (5, 'admin', 'Monitor', 1)
]

SAMPLE_ACCOUNTS = [
    ('admin', 'admin@nullbox.com', 1500.00),
    ('user', 'user@example.com', 500.00)
]

DB_PATH = 'lab.db'

def get_in_memory_db():
    """Get or create the in-memory database for login lab"""
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row

    # Create users table
    conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT
    )
    ''')

    # Insert default users
    default_users = [
        ('admin', 'admin123'),
        ('user', 'pass123')
    ]
    conn.executemany('INSERT INTO users (username, password) VALUES (?, ?)', default_users)
    conn.commit()

    return conn

# ===== LOGIN PAGE ENDPOINTS =====

@login_lab_bp.route('/api/login/init', methods=['GET'])
def init_login():
    """Reset the lab database (users, products, etc.)"""
    try:
        # Remove the DB file if it exists
        import os
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        conn = get_in_memory_db()
        # Insert default users
        default_users = [
            ('admin', 'admin123'),
            ('user', 'pass123')
        ]
        conn.executemany('INSERT INTO users (username, password) VALUES (?, ?)', default_users)
        conn.commit()
        conn.close()
        return jsonify({"status": "initialized"}), 200
    except Exception as e:
        return jsonify({"status": "initialized", "warning": str(e)}), 200

@login_lab_bp.route('/api/login', methods=['POST'])
def login():
    """Handle user login"""
    try:
        data = request.get_json()
        username = data.get('username', '')
        password = data.get('password', '')

        conn = get_in_memory_db()
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        cursor = conn.execute(query)
        user = cursor.fetchone()
        conn.close()

        if user:
            return jsonify({
                "success": True,
                "username": user['username'],
                "query": query
            }), 200
        else:
            return jsonify({
                "success": False,
                "query": query
            }), 401
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@login_lab_bp.route('/api/register', methods=['POST'])
def register_user():
    """Register a new user"""
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400


    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    # Build vulnerable SQL query
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"

    conn = get_in_memory_db()
    try:
        cursor = conn.execute(query)
        user = cursor.fetchone()

        if user:
            result = {
                "success": True,
                "username": user['username'],
                "query": query
            }
        else:
            result = {
                "success": False,
                "query": query
            }

        conn.close()
        return jsonify(result)
    except Exception as e:
        conn.close()
        return jsonify({"success": False, "query": query, "error": str(e)}), 500

# ===== DASHBOARD =====

@login_lab_bp.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """Get dashboard data"""
    username = request.args.get('username', 'guest')
    return jsonify({
        "username": username,
        "welcome_message": f"Welcome, {username}!"
    })

# ===== PRODUCTS PAGE =====

@login_lab_bp.route('/api/products/init', methods=['GET'])
def init_products():
    """Initialize products database"""
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row

    conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            price REAL
        )
    ''')

    # Insert sample products
    conn.executemany('INSERT INTO products (id, name, price) VALUES (?, ?, ?)', SAMPLE_PRODUCTS)
    conn.commit()

    return jsonify({"status": "initialized"})

@login_lab_bp.route('/api/products', methods=['GET'])
def get_products():
    """Get products with optional search"""
    try:
        search = request.args.get('search', '')
        conn = get_in_memory_db()
        # Always ensure products table exists
        conn.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT,
                price REAL
            )
        ''')
        # Insert sample products if table is empty
        cur = conn.execute('SELECT COUNT(*) as cnt FROM products')
        if cur.fetchone()['cnt'] == 0:
            conn.executemany('INSERT INTO products (id, name, price) VALUES (?, ?, ?)', SAMPLE_PRODUCTS)
            conn.commit()

        # Build vulnerable query
        if search:
            query = f"SELECT * FROM products WHERE name LIKE '%{search}%'"
        else:
            query = "SELECT * FROM products WHERE name LIKE '%'"

        cursor = conn.execute(query)
        products = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return jsonify({
            "products": products,
            "query": query
        })
    except Exception as e:
        return jsonify({
            "products": [],
            "query": query if 'query' in locals() else "",
            "error": str(e)
        }), 200

# ===== ORDERS PAGE =====

@login_lab_bp.route('/api/orders/init', methods=['GET'])
def init_orders():
    """Initialize orders database"""
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row

    conn.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            username TEXT,
            product TEXT,
            amount INTEGER
        )
    ''')

    # Insert sample orders
    conn.executemany('INSERT INTO orders (id, username, product, amount) VALUES (?, ?, ?, ?)', SAMPLE_ORDERS)
    conn.commit()

    return jsonify({"status": "initialized"})

@login_lab_bp.route('/api/orders', methods=['GET'])
def get_orders():
    """Get orders for a user"""
    try:
        username = request.args.get('username', '')
        conn = sqlite3.connect(':memory:')
        conn.row_factory = sqlite3.Row

        conn.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY,
                username TEXT,
                product TEXT,
                amount INTEGER
            )
        ''')

        conn.executemany('INSERT INTO orders (id, username, product, amount) VALUES (?, ?, ?, ?)', SAMPLE_ORDERS)
        conn.commit()

        # Build vulnerable query
        # Build vulnerable query
        search = request.args.get('search', '')
        if search:
            query = f"SELECT * FROM orders WHERE username = '{username}' AND product LIKE '%{search}%'"
        else:
            query = f"SELECT * FROM orders WHERE username = '{username}' AND product LIKE '%'"

        cursor = conn.execute(query)
        orders = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return jsonify({
            "orders": orders,
            "username": username,
            "query": query
        })
    except Exception as e:
        return jsonify({
            "orders": [],
            "username": username if 'username' in locals() else "",
            "query": query if 'query' in locals() else "",
            "error": str(e)
        }), 200

# ===== ACCOUNTS PAGE =====

@login_lab_bp.route('/api/accounts/init', methods=['GET'])
def init_accounts():
    """Initialize accounts database"""
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row

    conn.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            username TEXT PRIMARY KEY,
            email TEXT,
            balance REAL
        )
    ''')

    # Insert sample accounts
    conn.executemany('INSERT INTO accounts (username, email, balance) VALUES (?, ?, ?)', SAMPLE_ACCOUNTS)
    conn.commit()

    return jsonify({"status": "initialized"})

@login_lab_bp.route('/api/accounts', methods=['GET'])
def get_account():
    """Get account details for a user"""
    try:
        username = request.args.get('username', '')
        conn = sqlite3.connect(':memory:')
        conn.row_factory = sqlite3.Row

        conn.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                username TEXT PRIMARY KEY,
                email TEXT,
                balance REAL
            )
        ''')

        conn.executemany('INSERT INTO accounts (username, email, balance) VALUES (?, ?, ?)', SAMPLE_ACCOUNTS)
        conn.commit()

        # Build vulnerable query
        query = f"SELECT * FROM accounts WHERE username = '{username}'"

        cursor = conn.execute(query)
        account = cursor.fetchone()

        conn.close()
        return jsonify({
            "account": dict(account) if account else None,
            "username": username,
            "query": query
        })
    except Exception as e:
        return jsonify({
            "account": None,
            "username": username if 'username' in locals() else "",
            "query": query if 'query' in locals() else "",
            "error": str(e)
        }), 200
