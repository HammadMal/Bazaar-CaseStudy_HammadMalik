# import sqlite3

# # Connect to the database
# conn = sqlite3.connect('example.db')

# # Create a new table
# cursor = conn.cursor()
# cursor.execute('''CREATE TABLE IF NOT EXISTS stocks
#                  (date text, trans text, symbol text, qty real, price real)''')
# conn.commit()

# # Insert a new record
# cursor.execute("INSERT INTO stocks VALUES ('2022-01-01','BUY','RHAT',100,35.14)")
# conn.commit()

# # Query the database
# cursor.execute('SELECT * FROM stocks')
# print(cursor.fetchall())

# # Close the connection
# conn.close()

#boilerplate taken from "https://medium.com/@hugoalmeidamoreira/boilerplate-for-sqlite-projects-enhancing-efficiency-and-scalability-616372c36177"



from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'bazaar-secret-key'

DB_PATH = 'inventory_stage1.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        category TEXT,
        unit TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 0,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products (id)
    );

    CREATE TABLE IF NOT EXISTS stock_movements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        movement_type TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        previous_quantity INTEGER NOT NULL,
        new_quantity INTEGER NOT NULL,
        reference_id TEXT,
        notes TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products (id)
    );

    CREATE TRIGGER IF NOT EXISTS update_inventory_timestamp
    AFTER UPDATE ON inventory
    BEGIN
        UPDATE inventory SET last_updated = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;
    """)
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = get_db_connection()
    products = conn.execute("""
        SELECT p.*, i.quantity FROM products p
        JOIN inventory i ON p.id = i.product_id
        ORDER BY p.name
    """).fetchall()
    conn.close()
    return render_template('index.html', products=products)

@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        sku = request.form['sku']
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']
        unit = request.form['unit']
        conn = get_db_connection()
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO products (sku, name, description, category, unit) VALUES (?, ?, ?, ?, ?)",
                        (sku, name, description, category, unit))
            product_id = cur.lastrowid
            cur.execute("INSERT INTO inventory (product_id, quantity) VALUES (?, 0)", (product_id,))
            conn.commit()
            flash('Product added successfully!', 'success')
        except sqlite3.IntegrityError:
            flash('SKU already exists!', 'danger')
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_product.html')

@app.route('/stock/<int:product_id>', methods=['POST'])
def stock_product(product_id):
    quantity = int(request.form['quantity'])
    reference_id = request.form['reference_id']
    notes = request.form['notes']
    conn = get_db_connection()
    cur = conn.cursor()
    current = cur.execute("SELECT quantity FROM inventory WHERE product_id = ?", (product_id,)).fetchone()
    if current:
        prev = current['quantity']
        new = prev + quantity
        cur.execute("""
            INSERT INTO stock_movements (product_id, movement_type, quantity, previous_quantity, new_quantity, reference_id, notes)
            VALUES (?, 'stock-in', ?, ?, ?, ?, ?)
        """, (product_id, quantity, prev, new, reference_id, notes))
        cur.execute("UPDATE inventory SET quantity = ? WHERE product_id = ?", (new, product_id))
        conn.commit()
        flash('Stock updated successfully!', 'success')
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    initialize_database()
    

@app.route('/sale/<int:product_id>', methods=['POST'])
def sale_product(product_id):
    quantity = int(request.form['quantity'])
    reference_id = request.form['reference_id']
    notes = request.form['notes']
    conn = get_db_connection()
    cur = conn.cursor()
    current = cur.execute("SELECT quantity FROM inventory WHERE product_id = ?", (product_id,)).fetchone()
    if current:
        prev = current['quantity']
        new = prev - quantity
        if new < 0:
            flash('Not enough stock for sale!', 'danger')
        else:
            cur.execute("""
                INSERT INTO stock_movements (product_id, movement_type, quantity, previous_quantity, new_quantity, reference_id, notes)
                VALUES (?, 'sale', ?, ?, ?, ?, ?)
            """, (product_id, quantity, prev, new, reference_id, notes))
            cur.execute("UPDATE inventory SET quantity = ? WHERE product_id = ?", (new, product_id))
            conn.commit()
            flash('Sale recorded successfully!', 'success')
    conn.close()
    return redirect(url_for('index'))

@app.route('/remove/<int:product_id>', methods=['POST'])
def remove_product(product_id):
    quantity = int(request.form['quantity'])
    notes = request.form['notes']
    conn = get_db_connection()
    cur = conn.cursor()
    current = cur.execute("SELECT quantity FROM inventory WHERE product_id = ?", (product_id,)).fetchone()
    if current:
        prev = current['quantity']
        new = prev - quantity
        if new < 0:
            flash('Not enough stock to remove!', 'danger')
        else:
            cur.execute("""
                INSERT INTO stock_movements (product_id, movement_type, quantity, previous_quantity, new_quantity, reference_id, notes)
                VALUES (?, 'removal', ?, ?, ?, NULL, ?)
            """, (product_id, quantity, prev, new, notes))
            cur.execute("UPDATE inventory SET quantity = ? WHERE product_id = ?", (new, product_id))
            conn.commit()
            flash('Stock removed successfully!', 'success')
    conn.close()
    return redirect(url_for('index'))

app.run(debug=True)