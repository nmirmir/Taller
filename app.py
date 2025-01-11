from flask import Flask, request, jsonify, render_template, g
from BD import (
    create_connection, create_table, add_object, update_object, 
    delete_object, get_all_objects, get_all_categories, 
    get_all_statuses, get_all_zones, add_zone, remove_zone,
    check_admin_password, delete_zone_objects, delete_category_objects,
    delete_status_objects, delete_all_objects, initialize_data, init_db, close_db,
    get_zones, get_objects
)
import sqlite3

app = Flask(__name__)
app.teardown_appcontext(close_db)

def get_db():
    """Create a new database connection for each request"""
    db = sqlite3.connect('inventory.db', check_same_thread=False)
    return db

# Initialize database on startup
with app.app_context():
    db = get_db()
    create_table(db)
    initialize_data(db)
    db.close()

# Initialize the database
with app.app_context():
    init_db(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/objects', methods=['GET', 'POST'])
def objects_endpoint():
    try:
        db = get_db()
        if request.method == 'POST':
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
                
            required_fields = ['name', 'price', 'quantity', 'status', 'zone_id', 'category_id']
            for field in required_fields:
                if field not in data:
                    return jsonify({"error": f"Missing required field: {field}"}), 400
                
            # Validate that zone_id and category_id are integers
            try:
                data['zone_id'] = int(data['zone_id'])
                data['category_id'] = int(data['category_id'])
            except (ValueError, TypeError):
                return jsonify({"error": "zone_id and category_id must be valid integers"}), 400
                
            object_id = add_object(db, data)
            return jsonify({
                "id": object_id,
                "name": data['name'],
                "description": data.get('description', ''),
                "zone_id": data['zone_id'],
                "category_id": data['category_id'],
                "price": data['price'],
                "quantity": data['quantity'],
                "status": data['status']
            }), 201
        else:
            objects = get_objects(db)
            return jsonify(objects)
            
    except Exception as e:
        print(f"Error in objects endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/objects/<int:object_id>', methods=['DELETE'])
def delete_object_endpoint(object_id):
    with get_db() as db:
        try:
            success = delete_object(db, object_id, request.json['deletion_user'])
            if success:
                return jsonify({"success": True}), 200
            else:
                return jsonify({"success": False, "error": "Could not delete object"}), 400
        except Exception as e:
            print(f"Error deleting object: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/zones', methods=['GET', 'POST'])
def zones():
    db = get_db()
    if request.method == 'POST':
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({"error": "Name is required"}), 400
            
        # Pass the name directly, not as a tuple
        zone_id = add_zone(db, data['name'])
        return jsonify({"id": zone_id, "name": data['name']}), 201
    else:
        zones = get_zones(db)
        return jsonify(zones)

@app.route('/api/zones/<int:zone_id>', methods=['DELETE'])
def delete_zone_endpoint(zone_id):
    with get_db() as db:
        try:
            success = remove_zone(db, zone_id)
            if success:
                return jsonify({"success": True}), 200
            else:
                return jsonify({"success": False, "error": "Could not delete zone"}), 400
        except Exception as e:
            print(f"Error deleting zone: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/categories', methods=['GET'])
def categories():
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT id, name FROM categories ORDER BY id")
        categories = cursor.fetchall()
        return jsonify([list(row) for row in categories])

@app.route('/api/statuses', methods=['GET'])
def statuses():
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT id, name FROM statuses ORDER BY id")
        statuses = cursor.fetchall()
        return jsonify([list(row) for row in statuses])

@app.route('/api/objects/<int:object_id>', methods=['GET'])
def get_object(object_id):
    with get_db() as db:
        try:
            cursor = db.cursor()
            cursor.execute("""
                SELECT o.*, s.name as status_name
                FROM objects o
                JOIN statuses s ON o.status_id = s.id
                WHERE o.id = ? AND o.deletion_date IS NULL
            """, (object_id,))
            object_data = cursor.fetchone()
            
            if object_data:
                return jsonify({
                    'id': object_data[0],
                    'name': object_data[1],
                    'description': object_data[2],
                    'price': object_data[3],
                    'quantity': object_data[4],
                    'category_id': object_data[5],
                    'zone_id': object_data[6],
                    'status_id': object_data[7]
                })
            return jsonify({'error': 'Object not found'}), 404
        except Exception as e:
            print(f"Error getting object: {e}")
            return jsonify({'error': str(e)}), 500

@app.route('/api/objects/<int:object_id>', methods=['PUT'])
def update_object_endpoint(object_id):
    with get_db() as db:
        try:
            data = request.json
            success = update_object(db, object_id, data['updates'], data['modification_user'])
            if success:
                return jsonify({"success": True}), 200
            return jsonify({"success": False, "error": "Could not update object"}), 400
        except Exception as e:
            print(f"Error updating object: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/bulk-delete/zone/<int:zone_id>', methods=['DELETE'])
def bulk_delete_zone_endpoint(zone_id):
    with get_db() as db:
        try:
            if not check_admin_password(request.json['admin_password']):
                return jsonify({"error": "Invalid admin password"}), 401
            success = delete_zone_objects(db, zone_id, request.json['admin_password'])
            if success:
                return jsonify({"success": True}), 200
            return jsonify({"error": "Could not delete zone objects"}), 400
        except Exception as e:
            print(f"Error in bulk delete zone: {e}")
            return jsonify({"error": str(e)}), 500

@app.route('/api/bulk-delete/category/<int:category_id>', methods=['DELETE'])
def bulk_delete_category_endpoint(category_id):
    with get_db() as db:
        try:
            if not check_admin_password(request.json['admin_password']):
                return jsonify({"error": "Invalid admin password"}), 401
            success = delete_category_objects(db, category_id, request.json['admin_password'])
            if success:
                return jsonify({"success": True}), 200
            return jsonify({"error": "Could not delete category objects"}), 400
        except Exception as e:
            print(f"Error in bulk delete category: {e}")
            return jsonify({"error": str(e)}), 500

@app.route('/api/bulk-delete/all', methods=['DELETE'])
def bulk_delete_all_endpoint():
    with get_db() as db:
        try:
            if not check_admin_password(request.json['admin_password']):
                return jsonify({"error": "Invalid admin password"}), 401
            success = delete_all_objects(db, request.json['admin_password'])
            if success:
                return jsonify({"success": True}), 200
            return jsonify({"error": "Could not delete all objects"}), 400
        except Exception as e:
            print(f"Error in bulk delete all: {e}")
            return jsonify({"error": str(e)}), 500

@app.route('/api/zones', methods=['POST'])
def add_zone_endpoint():
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
            
        data = request.get_json()
        print("Received data:", data)  # Debug log
        
        if not data or 'name' not in data:
            return jsonify({"error": "Zone name is required"}), 400
            
        name = data['name'].strip()
        if not name:
            return jsonify({"error": "Zone name cannot be empty"}), 400
            
        with get_db() as db:
            try:
                zone_id = add_zone(db, name)
                response = {
                    "success": True,
                    "id": zone_id,
                    "name": name
                }
                print("Response:", response)  # Debug log
                return jsonify(response), 201
            except Exception as e:
                return jsonify({"error": str(e)}), 400
            
    except Exception as e:
        print(f"Error in add_zone_endpoint: {e}")  # Debug log
        return jsonify({"error": "Server error occurred"}), 500

if __name__ == '__main__':
    app.run(debug=True) 