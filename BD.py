import sqlite3
from sqlite3 import Error
from datetime import datetime


## CONEXION A LA BASE DE DATOS

def create_connection():
    """Create a database connection to a SQLite database"""
    try:
        conn = sqlite3.connect('taller.db', timeout=20)
        conn.execute('PRAGMA foreign_keys = ON;')
        print("Successfully connected to SQLite database")
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None


## CREACION DE LAS TABLAS
def create_table(conn):
    """Create tables and add default values"""
    try:
        cursor = conn.cursor()
        
        # Enable foreign key support
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Creating the users table
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        );
        """
        
        # Creating the objects table with correct structure
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
            creation_date DATE DEFAULT CURRENT_TIMESTAMP,
            modification_date DATE DEFAULT CURRENT_TIMESTAMP,
            deletion_date DATE,
            deletion_user TEXT,
            FOREIGN KEY (category_id) REFERENCES categories(id),
            FOREIGN KEY (zone_id) REFERENCES zones(id),
            FOREIGN KEY (status_id) REFERENCES statuses(id)
        );
        """
        # Creating the categories table
        create_categories_table = """
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            creation_date DATE NOT NULL,
            creation_user TEXT NOT NULL
        );
        """
        # Creating the statuses table
        create_statuses_table = """
        CREATE TABLE IF NOT EXISTS statuses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );
        """
        # Creating Zona de mecanizado table
        create_zona_de_mecanizado_table = """
        CREATE TABLE IF NOT EXISTS zona_de_mecanizado (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            objects_id INTEGER NOT NULL,
            FOREIGN KEY (objects_id) 
                REFERENCES objects(id) 
                ON DELETE CASCADE 
                ON UPDATE CASCADE
        );
        """
        # Creating Zona de soldadura table
        create_zona_de_soldadura_table = """
        CREATE TABLE IF NOT EXISTS zona_de_soldadura (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            objects_id INTEGER NOT NULL,
            FOREIGN KEY (objects_id) 
                REFERENCES objects(id) 
                ON DELETE CASCADE 
                ON UPDATE CASCADE
        );
        """
        # Creating Zona de impresion table
        create_zona_de_impresion_table = """
        CREATE TABLE IF NOT EXISTS zona_de_impresion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            objects_id INTEGER NOT NULL,
            FOREIGN KEY (objects_id) 
                REFERENCES objects(id) 
                ON DELETE CASCADE 
                ON UPDATE CASCADE
        );
        """
        # Creating Zona del laser table
        create_zona_del_laser_table = """
        CREATE TABLE IF NOT EXISTS zona_del_laser (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            objects_id INTEGER NOT NULL,
            FOREIGN KEY (objects_id) 
                REFERENCES objects(id) 
                ON DELETE CASCADE 
                ON UPDATE CASCADE
        );
        """ 
        # Creating the objects table
        create_objects_table = """
        CREATE TABLE IF NOT EXISTS objects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            quantity INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            zone_id INTEGER NOT NULL,
            creation_date DATE NOT NULL,
            modification_date DATE NOT NULL,
            deletion_date DATE,
            status_id INTEGER NOT NULL,
            creation_user TEXT NOT NULL,
            modification_user TEXT NOT NULL,
            deletion_user TEXT,
            FOREIGN KEY (category_id) 
                REFERENCES categories(id) 
                ON DELETE CASCADE 
                ON UPDATE CASCADE,
            FOREIGN KEY (zone_id) 
                REFERENCES zones(id) 
                ON DELETE CASCADE 
                ON UPDATE CASCADE,
            FOREIGN KEY (status_id) 
                REFERENCES statuses(id) 
                ON DELETE CASCADE 
                ON UPDATE CASCADE
        );
        """
        # Creating the zones table
        create_zones_table = """
        CREATE TABLE IF NOT EXISTS zones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            creation_date DATE NOT NULL,
            creation_user TEXT NOT NULL
        );
        """

        
        # Execute all create table statements
        cursor.execute(create_users_table)
        cursor.execute(create_zones_table)
        cursor.execute(create_categories_table)
        cursor.execute(create_statuses_table)
        cursor.execute(create_zona_de_mecanizado_table)
        cursor.execute(create_zona_de_soldadura_table)
        cursor.execute(create_zona_de_impresion_table)
        cursor.execute(create_zona_del_laser_table)
        cursor.execute(create_objects_table)
        
        # Add default categories if they don't exist
        current_time = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("""
        INSERT OR IGNORE INTO categories (id, name, description, creation_date, creation_user) 
        VALUES 
            (1, 'Tools', 'Workshop tools and equipment', ?, 'system'),
            (2, 'Materials', 'Raw materials', ?, 'system'),
            (3, 'Consumables', 'Consumable items', ?, 'system'),
            (4, 'Equipment', 'Large equipment', ?, 'system');
        """, (current_time, current_time, current_time, current_time))

        # Add default statuses if they don't exist
        cursor.execute("""
        INSERT OR IGNORE INTO statuses (id, name) 
        VALUES 
            (1, 'Active'),
            (2, 'Maintenance'),
            (3, 'Out of Service'),
            (4, 'Reserved');
        """)

        # Add default zones if they don't exist
        cursor.execute("""
        INSERT OR IGNORE INTO zones (id, name, description, creation_date, creation_user) 
        VALUES 
            (1, 'Zona de Mecanizado', 'Area for machining operations', ?, 'system'),
            (2, 'Zona de Soldadura', 'Welding and joining area', ?, 'system'),
            (3, 'Zona de Impresion', 'Printing and additive manufacturing', ?, 'system'),
            (4, 'Zona del Laser', 'Laser cutting and engraving', ?, 'system');
        """, (current_time, current_time, current_time, current_time))

        conn.commit()
        print("Tables and default values created successfully")
        
    except Error as e:
        print(f"Error creating tables: {e}")

## INSERTAR UN OBJETO
def add_object(conn, object_data):
    """Add a new object"""
    try:
        cursor = conn.cursor()
        
        sql = """INSERT INTO objects(
            name, description, price, quantity, 
            category_id, zone_id, status_id,
            creation_user, modification_user
        ) VALUES(?,?,?,?,?,?,?,?,?)"""
        
        cursor.execute(sql, object_data)
        conn.commit()
        print("Object added successfully")
        return cursor.lastrowid
    except Error as e:
        print(f"Error adding object: {e}")
        return None
## ELIMINAR UN OBJETO
def delete_object(conn, object_id, deletion_user):
    """Soft delete an object by updating its deletion information"""
    try:
        cursor = conn.cursor()
        current_time = datetime.now().strftime('%Y-%m-%d')
        
        sql = """UPDATE objects 
                SET deletion_date = ?,
                    deletion_user = ?,
                    status_id = ?
                WHERE id = ?"""
                
        cursor.execute(sql, (current_time, deletion_user, 0, object_id))  # Assuming status_id 0 means deleted
        conn.commit()
        print("Object deleted successfully")
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
    """Get all objects"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM objects")
    rows = cursor.fetchall()
    return rows #return the objects

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

## AGREGAR UNA ZONA
def add_zone(conn, zone_data):
    """Add a new zone"""
    try:
        cursor = conn.cursor()
        current_time = datetime.now().strftime('%Y-%m-%d')
        
        sql = """INSERT INTO zones(
            name, description, creation_date, creation_user
        ) VALUES(?,?,?,?)"""
        
        complete_zone = (
            *zone_data[:2],    # name, description
            current_time,      # creation_date
            zone_data[2]       # creation_user
        )
        
        cursor.execute(sql, complete_zone)
        conn.commit()
        print("Zone added successfully")
        return cursor.lastrowid
    except Error as e:
        print(f"Error adding zone: {e}")
        return None

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
