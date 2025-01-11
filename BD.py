"""
Inventory Management System - Database Operations
Admin Password for deletion operations: admin123
"""

import sqlite3
from sqlite3 import Error
from flask import g
from datetime import datetime


## CONEXION A LA BASE DE DATOS
def create_connection():
    """
    Creates a connection to the SQLite database.
    If the database doesn't exist, it will be created.
    
    Returns:
        sqlite3.Connection: Database connection object if successful
        None: If connection fails
    """
    try:
        conn = sqlite3.connect('inventory.db')
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None


## CREACION DE LAS TABLAS
def create_table(conn):
    """Create tables including a detailed history table"""
    try:
        cursor = conn.cursor()
        
        # Create history table for tracking all changes
        create_history_table = """
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zone_id INTEGER,
            object_id INTEGER,
            action_type TEXT NOT NULL,  -- 'CREATE', 'UPDATE', 'DELETE', 'ZONE_DELETED'
            field_modified TEXT,        -- NULL for CREATE/DELETE, field name for UPDATE
            old_value TEXT,            -- Previous value for updates
            new_value TEXT,            -- New value for updates
            modification_date DATETIME NOT NULL,
            modification_user TEXT NOT NULL,
            comment TEXT,
            FOREIGN KEY (zone_id) REFERENCES zones(id),
            FOREIGN KEY (object_id) REFERENCES objects(id)
        );
        """
        cursor.execute(create_history_table)
        
        # Create other tables
        create_zones_table = """
        CREATE TABLE IF NOT EXISTS zones (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        );
        """
        cursor.execute(create_zones_table)
        
        create_categories_table = """
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        );
        """
        cursor.execute(create_categories_table)
        
        create_statuses_table = """
        CREATE TABLE IF NOT EXISTS statuses (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        );
        """
        cursor.execute(create_statuses_table)
        
        create_objects_table = """
        CREATE TABLE IF NOT EXISTS objects (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            price REAL,
            quantity INTEGER,
            category_id INTEGER,
            zone_id INTEGER,
            status_id INTEGER,
            creation_user TEXT,
            modification_user TEXT,
            creation_date DATETIME,
            modification_date DATETIME,
            deletion_date DATETIME,
            deletion_user TEXT,
            FOREIGN KEY (category_id) REFERENCES categories (id),
            FOREIGN KEY (zone_id) REFERENCES zones (id),
            FOREIGN KEY (status_id) REFERENCES statuses (id)
        );
        """
        cursor.execute(create_objects_table)
        
        
        conn.commit()
        
    except Error as e:
        print(f"Error creating tables: {e}")

## INSERTAR UN OBJETO
def add_object(conn, data):
    """Add a new object to the database"""
    try:
        cursor = conn.cursor()
        # Check if data is a tuple and convert it to a dictionary if needed
        if isinstance(data, tuple):
            data = {
                'name': data[0],
                'description': data[1],
                'zone_id': data[2],
                'category_id': data[3],
                'price': data[4],
                'quantity': data[5],
                'status': data[6]
            }
            
        cursor.execute('''
            INSERT INTO objects (
                name, 
                description, 
                zone_id, 
                category_id, 
                price, 
                quantity, 
                status
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['name'],
            data.get('description', ''),
            data['zone_id'],
            data['category_id'],
            data['price'],
            data['quantity'],
            data['status']
        ))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Database error in add_object: {e}")
        conn.rollback()
        raise Exception(f"Database error: {str(e)}")
## ELIMINAR UN OBJETO
def delete_object(conn, object_id, deletion_user):
    """
    Soft delete an object by setting its deletion date
    
    Args:
        conn: Database connection object
        object_id: ID of the object to delete
        deletion_user: Username of person performing deletion
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        cursor = conn.cursor()
        current_time = datetime.now().strftime('%Y-%m-%d')
        
        # Check if object exists and is not already deleted
        cursor.execute("""
            SELECT id FROM objects 
            WHERE id = ? AND deletion_date IS NULL
        """, (object_id,))
        
        if not cursor.fetchone():
            print(f"Object {object_id} not found or already deleted")
            return False
        
        # Soft delete by updating deletion fields
        cursor.execute("""
            UPDATE objects 
            SET deletion_date = ?,
                deletion_user = ?
            WHERE id = ?
        """, (current_time, deletion_user, object_id))
        
        conn.commit()
        return True
        
    except Error as e:
        print(f"Error deleting object: {e}")
        return False

## ACTUALIZAR UN OBJETO
def update_object(conn, object_id, updates, modification_user):
    """Update object and record history"""
    try:
        cursor = conn.cursor()
        
        # Get current object data for history
        cursor.execute("SELECT zone_id FROM objects WHERE id = ?", (object_id,))
        zone_id = cursor.fetchone()[0]
        
        # Record each field update separately in history
        for field, new_value in updates.items():
            cursor.execute(f"SELECT {field} FROM objects WHERE id = ?", (object_id,))
            old_value = cursor.fetchone()[0]
            
            add_history(
                conn, zone_id, object_id, 'UPDATE', 
                field, str(old_value), str(new_value), 
                modification_user
            )
        
        # Perform the update
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        sql = f"UPDATE objects SET {set_clause} WHERE id = ?"
        cursor.execute(sql, (*updates.values(), object_id))
        conn.commit()
        
        return True
    except Error as e:
        print(f"Error updating object: {e}")
        return False

## LISTAR TODAS LAS ZONAS
def list_zones(conn):
    """List all zones"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM zones")
    rows = cursor.fetchall()
    return rows #return the zones

## INSERTAR UN USUARIO
def insert_user(conn, user):
    """Insert a new user into the users table"""
    sql = '''INSERT INTO users(name, email)
            VALUES(?,?)'''
    try:
        cursor = conn.cursor()
        # Only use first two elements of user tuple (name, email)
        cursor.execute(sql, user[:2])
        conn.commit()
        print("Successfully inserted user")
        return cursor.lastrowid
    except Error as e:
        print(f"Error inserting user: {e}")
        return None

## LOGIN DE ADMIN
def admin_login(conn):
    """Admin login"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    return rows #return the users

## OBTENER TODOS LOS USUARIOS
def get_all_users(conn):
    """Get all users"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    return rows #return the users   

## OBTENER TODOS LOS OBJETOS
def get_all_objects(conn):
    """
    Retrieves all non-deleted objects from database.
    
    Args:
        conn: Database connection object
    
    Returns:
        list: List of tuples containing object details
        Empty list: If no objects found or error occurs
    """
    try:
        cursor = conn.cursor()
        # Select only non-deleted objects and join with status
        cursor.execute("""
            SELECT o.id, o.name, o.description, o.price, o.quantity, o.category_id, o.zone_id, o.status_id, s.name  as status
            FROM objects o
            JOIN statuses s ON o.status_id = s.id
            WHERE o.deletion_date IS NULL
            ORDER BY o.id
        """)
        objects = cursor.fetchall()
        if not objects:
            print("No objects found")
        return objects
    except Error as e:
        print(f"Error getting objects: {e}")
        return []

## OBTENER UNA ZONA POR SU ID
def get_zone_by_id(conn, id ):
    """Get a zone by id"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM zones WHERE id = ?", (id,))
    rows = cursor.fetchall()
    return rows #return the zone
    
## OBTENER TODAS LAS CATEGORIAS
def get_all_categories(conn):
    """Get all categories"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories")
    rows = cursor.fetchall()
    return rows #return the categories

## OBTENER TODOS LOS ESTADOS
def get_all_statuses(conn):
    """Get all statuses"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM statuses")
    rows = cursor.fetchall()
    return rows #return the statuses    

## OBTENER TODAS LAS ZONAS
def get_all_zones(conn):
    """Retrieve all zones from database
    
    Args:
        conn: Database connection object
        
    Returns:
        list: List of tuples containing zone details
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name 
            FROM zones 
            ORDER BY id
        """)
        return cursor.fetchall()
    except Error as e:
        print(f"Error getting zones: {e}")
        return []

## AGREGAR UNA ZONA
def add_zone(conn, name):
    """Add a new zone to the database"""
    try:
        cursor = conn.cursor()
        # Check if zone already exists - using simpler parameter binding
        cursor.execute('SELECT id FROM zones WHERE name = ?', [name])
        if cursor.fetchone():
            raise Exception("A zone with this name already exists")
            
        # Insert new zone - using simpler parameter binding
        cursor.execute('INSERT INTO zones (name) VALUES (?)', [name])
        conn.commit()
        
        # Get the id of the newly inserted zone
        zone_id = cursor.lastrowid
        return zone_id
        
    except sqlite3.Error as e:
        print(f"Database error in add_zone: {e}")
        conn.rollback()
        raise Exception(f"Database error: {str(e)}")
    except Exception as e:
        print(f"Error in add_zone: {e}")
        conn.rollback()
        raise

## OBTENER LOS DATOS DE LA ZONA
def get_zone_input():
    """Get zone details from user"""
    try:
        name = input("Enter zone name: ")
        return (name,)  # Return only the name as a tuple
    except ValueError:
        print("Invalid input! Please enter a valid name.")
        return None

## ELIMINAR UNA ZONA
def remove_zone(conn, zone_id):
    """Delete a zone and record in history"""
    try:
        cursor = conn.cursor()
        
        # Get zone name before deletion for history
        cursor.execute("SELECT name FROM zones WHERE id = ?", (zone_id,))
        zone_name = cursor.fetchone()
        if not zone_name:
            print("Zone not found")
            return False
            
        # Temporarily disable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        # Check if zone exists
        cursor.execute("SELECT id FROM zones WHERE id = ?", (zone_id,))
        if not cursor.fetchone():
            print("Zone not found")
            cursor.execute("PRAGMA foreign_keys = ON")  # Re-enable constraints
            return False
        
        # Check for active objects in the zone
        cursor.execute("""
            SELECT COUNT(*) 
            FROM objects 
            WHERE zone_id = ? 
            AND deletion_date IS NULL
        """, (zone_id,))
        
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"Cannot delete zone: {count} objects are still assigned to this zone")
            cursor.execute("PRAGMA foreign_keys = ON")  # Re-enable constraints
            return False
        
        # Update any objects that reference this zone to use zone_id = 1
        cursor.execute("""
            UPDATE objects 
            SET zone_id = 1 
            WHERE zone_id = ?
        """, (zone_id,))
        
        # Now delete the zone
        cursor.execute("DELETE FROM zones WHERE id = ?", (zone_id,))
        
        # Re-enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Record zone deletion in history
        add_history(
            conn,
            zone_id=zone_id,
            object_id=None,  # No specific object
            action_type='ZONE_DELETED',
            field_modified='zone',
            old_value=zone_name[0],
            new_value=None,
            modification_user='admin'  # Or pass the current user
        )
        
        conn.commit()
        print("Zone deleted successfully")
        return True
        
    except Error as e:
        print(f"Error deleting zone: {e}")
        cursor.execute("PRAGMA foreign_keys = ON")  # Make sure to re-enable constraints
        return False

## AGREGAR UNA CATEGORIA
def add_category(conn, category_data):
    """Add a new category"""
    try:
        cursor = conn.cursor()
        current_time = datetime.now().strftime('%Y-%m-%d')
        
        sql = """INSERT INTO categories(
            name, description, creation_date, creation_user
        ) VALUES(?,?,?,?)"""
        
        complete_category = (
            *category_data[:2],  # name, description
            current_time,       # creation_date
            category_data[2]    # creation_user
        )
        
        cursor.execute(sql, complete_category)
        conn.commit()
        print("Category added successfully")
        return cursor.lastrowid
    except Error as e:
        print(f"Error adding category: {e}")
        return None

## LISTAR LOS ITEMS DE UNA ZONA
def list_zone_items(conn, zone_id, zone_name):
    """List all items in a specific zone"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.id, o.name, o.description, o.price, o.quantity, s.name as status
            FROM objects o
            JOIN statuses s ON o.status_id = s.id
            WHERE o.zone_id = ? AND o.deletion_date IS NULL
            ORDER BY o.id
        """, (zone_id,))
        return cursor.fetchall()
    except Error as e:
        print(f"Error retrieving items: {e}")
        return []

## AGREGAR UNA HISTORIA
def add_history(conn, zone_id, object_id, action_type, modification_user='admin'):
    """Add an entry to history with optional comment"""
    try:
        cursor = conn.cursor()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Ask for optional comment
        want_comment = input("Would you like to add a comment? (y/n): ").lower()
        comment = None
        if want_comment == 'y':
            comment = input("Enter your comment: ")

        cursor.execute('''
            INSERT INTO action_history (
                zone_id,
                object_id,
                action_type,
                modification_user,
                comment,
                modification_date
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (zone_id, object_id, action_type, modification_user, comment, current_time))
        
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error adding history: {e}")
        return False

## OBTENER LA HISTORIA DE LOS CAMBIOS
def get_history(conn):
    """Get history of changes"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM history")
    return cursor.fetchall()

def check_admin_password(password):
    """Verify admin password for dangerous operations"""
    ADMIN_PASSWORD = "admin123"  # Default admin password
    return password == ADMIN_PASSWORD

def delete_zone_objects(conn, zone_id, admin_password):
    """Soft delete all objects in a specific zone with password protection"""
    try:
        if not check_admin_password(admin_password):
            print("Invalid admin password!")
            return False
            
        cursor = conn.cursor()
        current_time = datetime.now().strftime('%Y-%m-%d')
        
        # Get zone name for confirmation
        cursor.execute("SELECT name FROM zones WHERE id = ?", (zone_id,))
        zone_name = cursor.fetchone()
        if not zone_name:
            print("Zone not found")
            return False
            
        # Soft delete objects
        cursor.execute("""
            UPDATE objects 
            SET deletion_date = ?, 
                deletion_user = 'admin'
            WHERE zone_id = ? 
            AND deletion_date IS NULL
        """, (current_time, zone_id))
        
        affected = cursor.rowcount
        conn.commit()
        
        print(f"All objects ({affected}) in zone '{zone_name[0]}' have been deleted")
        return True
    except Error as e:
        print(f"Error deleting zone objects: {e}")
        return False

def delete_category_objects(conn, category_id, admin_password):
    """Soft delete all objects in a specific category with password protection"""
    try:
        if not check_admin_password(admin_password):
            print("Invalid admin password!")
            return False
            
        cursor = conn.cursor()
        current_time = datetime.now().strftime('%Y-%m-%d')
        
        # Get category name for confirmation
        cursor.execute("SELECT name FROM categories WHERE id = ?", (category_id,))
        category_name = cursor.fetchone()
        if not category_name:
            print("Category not found")
            return False
            
        # Soft delete objects
        cursor.execute("""
            UPDATE objects 
            SET deletion_date = ?, 
                deletion_user = 'admin'
            WHERE category_id = ? 
            AND deletion_date IS NULL
        """, (current_time, category_id))
        
        affected = cursor.rowcount
        conn.commit()
        
        print(f"All objects ({affected}) in category '{category_name[0]}' have been deleted")
        return True
    except Error as e:
        print(f"Error deleting category objects: {e}")
        return False

def delete_status_objects(conn, status_id, admin_password):
    """Soft delete all objects with a specific status with password protection"""
    try:
        if not check_admin_password(admin_password):
            print("Invalid admin password!")
            return False
            
        cursor = conn.cursor()
        current_time = datetime.now().strftime('%Y-%m-%d')
        
        # Get status name for confirmation
        cursor.execute("SELECT name FROM statuses WHERE id = ?", (status_id,))
        status_name = cursor.fetchone()
        if not status_name:
            print("Status not found")
            return False
            
        # Soft delete objects
        cursor.execute("""
            UPDATE objects 
            SET deletion_date = ?, 
                deletion_user = 'admin'
            WHERE status_id = ? 
            AND deletion_date IS NULL
        """, (current_time, status_id))
        
        affected = cursor.rowcount
        conn.commit()
        
        print(f"All objects ({affected}) with status '{status_name[0]}' have been deleted")
        return True
    except Error as e:
        print(f"Error deleting status objects: {e}")
        return False

def delete_all_objects(conn, admin_password):
    """Soft delete all objects with password protection"""
    try:
        if not check_admin_password(admin_password):
            print("Invalid admin password!")
            return False
            
        # Double confirmation for dangerous operation
        confirm = input("Are you sure you want to delete ALL objects? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Operation cancelled")
            return False
            
        cursor = conn.cursor()
        current_time = datetime.now().strftime('%Y-%m-%d')
        
        # Soft delete all objects
        cursor.execute("""
            UPDATE objects 
            SET deletion_date = ?, 
                deletion_user = 'admin'
            WHERE deletion_date IS NULL
        """, (current_time,))
        
        affected = cursor.rowcount
        conn.commit()
        
        print(f"All objects ({affected}) have been deleted")
        return True
    except Error as e:
        print(f"Error deleting all objects: {e}")
        return False

## MAIN
def main():
    # Create a database connection
    conn = create_connection()
    
    if conn is not None:
        # Create the users table
        create_table(conn)
        
        # Insert some sample users
        user1 = ('John Doe', 'john@example.com', 25)
        user2 = ('Jane Smith', 'jane@example.com', 30)
        
        insert_user(conn, user1)
        insert_user(conn, user2)
        
        
        # Close the connection
        conn.close()
    else:
        print("Error! Cannot create the database connection.")

def get_history_summary(conn):
    """Get grouped history of changes"""
    try:
        cursor = conn.cursor()
        sql = """
        SELECT 
            z.name as zone_name,
            ah.action_type,
            COUNT(*) as change_count,
            GROUP_CONCAT(o.name) as objects_modified,
            ah.modification_date,
            ah.modification_user,
            ah.comment
        FROM action_history ah
        JOIN zones z ON ah.zone_id = z.id
        JOIN objects o ON ah.object_id = o.id
        GROUP BY 
            z.id,
            ah.action_type,
            DATE(ah.modification_date),
            ah.comment
        ORDER BY 
            ah.modification_date DESC,
            z.name,
            ah.action_type
        """
        cursor.execute(sql)
        return cursor.fetchall()
    except Error as e:
        print(f"Error getting history: {e}")
        return []

def initialize_data(conn):
    """Initialize basic data in the database"""
    try:
        cursor = conn.cursor()
        
        # Add default statuses if they don't exist
        statuses = [
            (1, 'Available'),
            (2, 'In Use'),
            (3, 'Maintenance'),
            (4, 'Retired')
        ]
        cursor.executemany("""
            INSERT OR IGNORE INTO statuses (id, name)
            VALUES (?, ?)
        """, statuses)
        
        # Add default categories if they don't exist
        categories = [
            (1, 'Electronics'),
            (2, 'Furniture'),
            (3, 'Tools'),
            (4, 'Office Supplies')
        ]
        cursor.executemany("""
            INSERT OR IGNORE INTO categories (id, name)
            VALUES (?, ?)
        """, categories)
        
        # Add default zone if it doesn't exist
        zones = [
            (1, 'General Zone'),
            (2, 'Storage'),
            (3, 'Office')
        ]
        cursor.executemany("""
            INSERT OR IGNORE INTO zones (id, name)
            VALUES (?, ?)
        """, zones)
        
        conn.commit()
    except Error as e:
        print(f"Error initializing data: {e}")

def get_db():
    """Get database connection"""
    if 'db' not in g:
        g.db = sqlite3.connect('inventory.db')
        g.db.row_factory = sqlite3.Row
    return g.db

def init_db(app):
    """Initialize the database."""
    try:
        with app.app_context():
            db = get_db()
            with app.open_resource('schema.sql', mode='r') as f:
                db.executescript(f.read())
            
            # Add default zones
            cursor = db.cursor()
            default_zones = [
                ('Zona de Mecanizado',),
                ('Zona de Soldadura',),
                ('Zona de Impresion',),
                ('Zona del Laser',)
            ]
            cursor.executemany('INSERT INTO zones (name) VALUES (?)', default_zones)
            db.commit()
            print("Database initialized successfully with default zones")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

def close_db(e=None):
    """Close database connection"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def get_zones(conn):
    """Get all zones from the database"""
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM zones')
        zones = []
        for row in cursor.fetchall():
            zones.append({
                'id': row[0],
                'name': row[1]
            })
        return zones
    except sqlite3.Error as e:
        print(f"Database error getting zones: {e}")
        raise Exception(f"Database error: {str(e)}")
    except Exception as e:
        print(f"Error getting zones: {e}")
        raise

def get_objects(conn):
    """Get all objects from the database with their zone names"""
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT o.id, o.name, o.description, o.price, o.quantity, 
                o.status, z.name as zone_name 
            FROM objects o
            LEFT JOIN zones z ON o.zone_id = z.id
        ''')
        rows = cursor.fetchall()
        
        objects = []
        for row in rows:
            object_dict = {}
            for idx, column in enumerate(cursor.description):
                object_dict[column[0]] = row[idx]
            objects.append(object_dict)
            
        return objects
        
    except sqlite3.Error as e:
        print(f"Database error in get_objects: {e}")
        raise Exception(f"Database error: {str(e)}")

if __name__ == '__main__':
    main()

