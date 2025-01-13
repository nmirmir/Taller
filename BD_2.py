import sqlite3
from sqlite3 import Error


def create_connection():
    try:
        conn = sqlite3.connect('inventory_2.db')
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None


# Create tables
def create_table(conn):
    "Create tables " 
    try:
        cursor = conn.cursor()
# 1
        # Create objects table
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
            creation_date DATETIME,
            modification_date DATETIME,
            deletion_date DATETIME,
            FOREIGN KEY (category_id) REFERENCES categories (id),
            FOREIGN KEY (zone_id) REFERENCES zones (id),
            FOREiGN KEY (status_id) REFERENCES statuses (id)
        
        
        )

        """
# 2
        # Create zones table
        create_zones_table = """
        CREATE TABLE IF NOT EXISTS zones (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        );
        """
        
        

        
# 3
        # Create statuses table
        create_statuses_table = """
        CREATE TABLE IF NOT EXISTS statuses(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )

        """

# 4
        # Create categories table
        create_categories_table = """
        CREATE TABLE IF NOT EXISTS categories(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )

        """

# 5
        # Create history table
        create_history_table = """
        CREATE TABLE IF NOT EXISTS history(
            id INTEGER PRIMARY KEY,
            zone_id INTEGER,
            object_id INTEGER,
            action_type TEXT NOT NULL,
            field_modified TEXT,
            old_value TEXT,
            nex_value TEXT,
            modification_date DATETIME NOT NULL,
            comment TEXT,
            FOREIGN KEY (zone_id) REFERENCES zones (id),
            FOREIGN KEY (object_id) REFERENCES object (id)
        )
        """




        # Execute the queries
        cursor.execute(create_objects_table)
        cursor.execute(create_zones_table)
        cursor.execute(create_statuses_table)
        cursor.execute(create_categories_table)
        cursor.execute(create_history_table)

    except Error as e:
        print(f"Error creating table: {e}")


## OPERATIONS WITH OBJECTS
# Add a new object into database
def add_object(conn, data):
    """ Add a new object into database"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO objects (
                name,
                description, 
                price, 
                quantity,
                category_id, 
                zone_id, 
                status_id
            )
            VALUES (?,?,?,?,?,?,?)
        """,(
            data['name'],
            data['description'],
            data['price'],
            data['quantity'],
            data['category_id'],
            data['zone_id'],
            data['status_id']
        ))
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Error adding object: {e}")
        conn.rollback()
        print(f"Error adding object: {e}")

def update_object(conn,data):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE objects
                SET name = ?,
                    description = ?,
                    price = ?,
                    quantity = ?,
                    category_id = ?,
                    zone_id = ?,
                    status_id = ?
                WHERE id = ?

        """,(
            data['name'],
            data['description'],
            data['price'],
            data['quantity'],
            data['category_id'],
            data['zone_id'],
            data['status_id']
        ))
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Error updating object: {e}")
        conn.rollback()
        print(f"Error updating object: {e}")

def delete_object(conn,object_id):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM objects
            WHERE id = ? AND deletion_date IS NULL
        """,(object_id,))

        if not cursor.fetchone():
            print(f"Object {object_id} not found or already deleted")
            return False

        conn.commit()
        print(f"Object {object_id} deleted successfully")
        return True
    except Error as e:
        print(f"Error deleting object: {e}")
        conn.rollback()
        print(f"Error deleting object: {e}")
        return False


## OPERATIONS WITH ZONES
def add_zone(conn,data):
    try:
        cursor = conn.cursor()

        # Check if zone already exists
        cursor.execute("""
        SELECT id FROM zones WHERE name = ?
        """,(data['name']))
        if cursor.fetchone():
            raise Exception("A zone with this name already exists")
        
        # Insert new zone
        cursor.execute("""
            INSERT INTO zones (name)
            VALUES (?)
        """,(data['name'],))
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Error adding zone {e}")
        conn.rollback()
        print(f"Error adding zone {e}")
        return False

def update_zone(conn,data):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE zones
                SET name = ?
                WHERE id = ?
        """,(data['name'],data['id']))
        print(f"Zone {data['id']} updated successfully")
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Error updating zone {e}")
        conn.rollback()
        print(f"Error updating zone {e}")
        return False

def delete_zone(conn,zone_id):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM zones
            WHERE id = ? AND deletion_date IS NULL
        """,(zone_id))
        if not cursor.fetchone():
            print(f"Zone {zone_id} not found or already deleted")
            return False
        #Record zone deletion in history
        
        conn.commit()
        print(f"Zone {zone_id} deleted successfully")
        return True
    except Error as e:
        print(f"Error deleting zone {e}")
        conn.rollback()
        print(f"Error deleting zone {e}")
        return False

def list_objects(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.id, o.name, o.description, o.price, o.quantity, o.category_id, o.zone_id, o.status_id
            FROM objects o
            WHERE deletion_date IS NULL
            ORDER BY o.quantity DESC
        """,)
        objects = cursor.fetchall()
        if not objects:
            print("No objects found")
            return []
        return objects
    except Error as e:
        print(f"Error listing objects: {e}")
        return []

def list_zones(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name
            FROM zones
            WHERE deletion_date IS NULL
            ORDER BY name
        """)
        zones = cursor.fetchall()
        if not zones:
            print("No zones found")
            return []
        return zones
    except Error as e:
        print(f"Error listing zones: {e}")
        return []

