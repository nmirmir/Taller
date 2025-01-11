from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

def create_connection():
    try:
        # Print current working directory and check if database exists
        print(f"Current working directory: {os.getcwd()}")
        db_path = 'inventory.db'
        print(f"Database exists: {os.path.exists(db_path)}")
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Connection error: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/zones', methods=['GET'])
def get_zones():
    try:
        conn = create_connection()
        if not conn:
            return jsonify({"error": "Could not connect to database"}), 500
            
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM zones')
        zones = cursor.fetchall()
        print(f"Found zones: {zones}")  # Debug print
        
        result = [dict(row) for row in zones]
        return jsonify(result)
    except Exception as e:
        print(f"Error getting zones: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/objects', methods=['GET'])
def get_objects():
    try:
        conn = create_connection()
        if not conn:
            return jsonify({"error": "Could not connect to database"}), 500
            
        cursor = conn.cursor()
        cursor.execute('''
            SELECT o.*, z.name as zone_name 
            FROM objects o
            LEFT JOIN zones z ON o.zone_id = z.id
        ''')
        objects = cursor.fetchall()
        print(f"Found objects: {objects}")  # Debug print
        
        result = [dict(row) for row in objects]
        return jsonify(result)
    except Exception as e:
        print(f"Error getting objects: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/objects', methods=['POST'])
def add_object():
    conn = None
    try:
        data = request.get_json()
        print(f"Received data: {data}")  # Debug print
        
        conn = create_connection()
        if not conn:
            return jsonify({"error": "Could not connect to database"}), 500
            
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO objects (name, description, zone_id, price, quantity, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['name'],
            data.get('description', ''),
            data.get('zone_id') if data.get('zone_id') != '' else None,
            float(data.get('price', 0)),
            int(data.get('quantity', 0)),
            data.get('status', 'Available')
        ))
        
        object_id = cursor.lastrowid
        print(f"Created object with ID: {object_id}")  # Debug print
        
        cursor.execute('''
            INSERT INTO history (object_id, zone_id, action_type, modification_date, comment)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            object_id,
            data.get('zone_id') if data.get('zone_id') != '' else None,
            'CREATE',
            datetime.now(),
            data.get('comment', '')
        ))
        
        conn.commit()
        return jsonify({"success": True, "id": object_id}), 201
        
    except Exception as e:
        print(f"Error adding object: {e}")
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    # Check database on startup
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Available tables: {tables}")
        conn.close()
    
    app.run(debug=True) 