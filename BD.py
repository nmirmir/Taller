import sqlite3
from sqlite3 import Error
from datetime import datetime


## CONEXION A LA BASE DE DATOS

def create_connection():
    """Create a database connection to a SQLite database
    
    Returns:
        Connection object or None if connection fails
    """
    try:
        conn = sqlite3.connect('inventory.db')
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None


## CREACION DE LAS TABLAS
def create_table(conn):
    """Create all necessary tables and add default values
    
    Args:
        conn: Database connection object
    """
    try:
        cursor = conn.cursor()
        
        # Enable foreign key support for referential integrity
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Create zones table - Stores different areas/locations
        create_zones_table = """
        CREATE TABLE IF NOT EXISTS zones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );
        """
        
        # Create categories table - Object classifications
        create_categories_table = """
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );
        """
        
        # Create statuses table - Current state of objects
        create_statuses_table = """
        CREATE TABLE IF NOT EXISTS statuses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );
        """
        
        # Create main objects table with all necessary fields and foreign keys
        create_objects_table = """
        CREATE TABLE IF NOT EXISTS objects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            quantity INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            zone_id INTEGER NOT NULL,
            status_id INTEGER NOT NULL,
            creation_user TEXT NOT NULL,
            modification_user TEXT NOT NULL,
            creation_date DATE NOT NULL,
            modification_date DATE NOT NULL,
            deletion_date DATE,
            deletion_user TEXT,
            FOREIGN KEY (category_id) REFERENCES categories(id),
            FOREIGN KEY (zone_id) REFERENCES zones(id),
            FOREIGN KEY (status_id) REFERENCES statuses(id)
        );
        """
        
        # Execute all create statements in correct order
        cursor.execute(create_categories_table)
        cursor.execute(create_statuses_table)
        cursor.execute(create_zones_table)
        cursor.execute(create_objects_table)
        
        # Insert default categories if they don't exist
        cursor.execute("""
        INSERT OR IGNORE INTO categories (id, name) 
        VALUES 
            (1, 'Tools'),
            (2, 'Materials'),
            (3, 'Consumables'),
            (4, 'Equipment');
        """)

        # Insert default statuses if they don't exist
        cursor.execute("""
        INSERT OR IGNORE INTO statuses (id, name) 
        VALUES 
            (1, 'Active'),
            (2, 'Maintenance'),
            (3, 'Out of Service'),
            (4, 'Reserved');
        """)

        # Insert default zones if they don't exist
        cursor.execute("""
        INSERT OR IGNORE INTO zones (id, name) 
        VALUES 
            (1, 'Zona de Mecanizado'),
            (2, 'Zona de Soldadura'),
            (3, 'Zona de Impresion'),
            (4, 'Zona del Laser');
        """)

        conn.commit()
        print("Tables and default values created successfully")
        
    except Error as e:
        print(f"Error creating tables: {e}")

## INSERTAR UN OBJETO
def add_object(conn, object_data):
    """Add a new object to the database
    
    Args:
        conn: Database connection object
        object_data: Tuple containing object details
        
    Returns:
        int: ID of the newly created object, or None if failed
    """
    try:
        cursor = conn.cursor()
        current_time = datetime.now().strftime('%Y-%m-%d')
        
        sql = """INSERT INTO objects(
            name, description, price, quantity, 
            category_id, zone_id, status_id,
            creation_user, modification_user,
            creation_date, modification_date,
            deletion_date, deletion_user
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)"""
        
        # Add creation_date, modification_date, and NULL for deletion fields
        complete_object = (
            *object_data,      # Original data
            current_time,      # creation_date
            current_time,      # modification_date
            None,             # deletion_date
            None              # deletion_user
        )
        
        cursor.execute(sql, complete_object)
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Error adding object: {e}")
        return None
## ELIMINAR UN OBJETO
def delete_object(conn, object_id, deletion_user):
    """Delete an object from the database"""
    try:
        cursor = conn.cursor()
        current_time = datetime.now().strftime('%Y-%m-%d')
        
        # First check if object exists and is not already deleted
        cursor.execute("""
            SELECT id FROM objects 
            WHERE id = ? AND deletion_date IS NULL
        """, (object_id,))
        
        if not cursor.fetchone():
            print("Object not found or already deleted")
            return False
        
        # Update the object with deletion info
        sql = """UPDATE objects 
                SET deletion_date = ?, 
                    deletion_user = ?
                WHERE id = ? 
                AND deletion_date IS NULL"""
                
        cursor.execute(sql, (current_time, deletion_user, object_id))
        conn.commit()
        
        if cursor.rowcount == 0:
            print("Failed to delete object")
            return False
            
        print(f"Object {object_id} marked as deleted by {deletion_user} on {current_time}")
        return True
    except Error as e:
        print(f"Error deleting object: {e}")
        return False

## ACTUALIZAR UN OBJETO
def update_object(conn, object_id, update_data, modification_user):
    """Update an object's information and return detailed feedback"""
    try:
        cursor = conn.cursor()
        
        # First, get the original object data
        cursor.execute("SELECT * FROM objects WHERE id = ?", (object_id,))
        original_object = cursor.fetchone()
        
        if not original_object:
            print(f"No object found with ID {object_id}")
            return False
            
        # Get column names for better feedback
        cursor.execute("PRAGMA table_info(objects)")
        columns = [column[1] for column in cursor.fetchall()]
        original_dict = dict(zip(columns, original_object))
        
        current_time = datetime.now().strftime('%Y-%m-%d')
        
        # Build the update query dynamically based on the fields to update
        update_fields = [f"{field} = ?" for field in update_data.keys()]
        update_fields.append("modification_date = ?")
        update_fields.append("modification_user = ?")
        
        sql = f"""UPDATE objects 
                SET {', '.join(update_fields)}
                WHERE id = ?"""
        
        # Add the values in the correct order
        values = (*update_data.values(), current_time, modification_user, object_id)
        
        cursor.execute(sql, values)
        conn.commit()
        
        # Get the updated object data
        cursor.execute("SELECT * FROM objects WHERE id = ?", (object_id,))
        updated_object = cursor.fetchone()
        updated_dict = dict(zip(columns, updated_object))
        
        # Generate detailed feedback
        print(f"\nObject ID {object_id} updated successfully:")
        print("-" * 40)
        for field in update_data.keys():
            old_value = original_dict[field]
            new_value = updated_dict[field]
            print(f"{field}:")
            print(f"  Old value: {old_value}")
            print(f"  New value: {new_value}")
        print("-" * 40)
        print(f"Modified by: {modification_user}")
        print(f"Modified on: {current_time}")
        
        return True
    except Error as e:
        print(f"Error updating object: {e}")
        return False

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
    """Retrieve all non-deleted objects with their status
    
    Args:
        conn: Database connection object
        
    Returns:
        list: List of tuples containing object details
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.id, o.name, o.description, o.price, o.quantity, s.name as status
            FROM objects o
            JOIN statuses s ON o.status_id = s.id
            WHERE o.deletion_date IS NULL
            ORDER BY o.id
        """)
        objects = cursor.fetchall()
        if not objects:
            print("No objects found")
            return []
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
def add_zone(conn, zone_data):
    """Add a new zone"""
    try:
        cursor = conn.cursor()
        
        sql = """INSERT INTO zones(
            name
        ) VALUES(?)"""
        
        # Only use the name from zone_data
        cursor.execute(sql, (zone_data[0],))
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Error adding zone: {e}")
        return None

def get_zone_input():
    """Get zone details from user"""
    try:
        name = input("Enter zone name: ")
        return (name,)  # Return only the name as a tuple
    except ValueError:
        print("Invalid input! Please enter a valid name.")
        return None

def remove_zone(conn, zone_id):
    """Delete a zone if it has no active objects"""
    try:
        cursor = conn.cursor()
        
        # First disable foreign key constraints temporarily
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        # Check if zone exists
        cursor.execute("SELECT id FROM zones WHERE id = ?", (zone_id,))
        if not cursor.fetchone():
            print("Zone not found")
            return False
        
        # Delete the zone
        cursor.execute("DELETE FROM zones WHERE id = ?", (zone_id,))
        
        # Update any objects that were in this zone to zone_id = 1 (default zone)
        cursor.execute("""
            UPDATE objects 
            SET zone_id = 1 
            WHERE zone_id = ?
        """, (zone_id,))
        
        # Re-enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        
        conn.commit()
        print("Zone deleted successfully")
        return True
        
    except Error as e:
        print(f"Error deleting zone: {e}")
        cursor.execute("PRAGMA foreign_keys = ON")  # Make sure to re-enable foreign keys
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

if __name__ == '__main__':
    main()
