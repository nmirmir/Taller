import sqlite3
from sqlite3 import Error


def create_connection():
    try:
        conn = sqlite3.connect('inventory_2.db')
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

def create_table(conn):
    "Create tables " 
    try:
        cursor = conn.cursor()

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

        # Create zones table
        create_zones_table = """
        CREATE TABLE IF NOT EXISTS zones (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        );
        """
        
        

        

        # Create statuses table
        create_statuses_table = """
        CREATE TABLE IF NOT EXISTS statuses(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )

        """

        # Create categories table
        create_categories_table = """
        CREATE TABLE IF NOT EXISTS categories(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )

        """

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
            modification_date DATETIME NOT NULL
            comment TEXT,
            FOREIGN KEY (zone_id) REFERENCES zones (id),
            FOREIGN KEY (object_od) REFERENCES object (id)
        )
        """




        # Execute the queries
        cursor.execute(create_objects_table)
        cursor.execute(create_zones_table)
        cursor.execute(create_statuses_table)
        cursor.execute(create_categories_table)

    except Error as e:
        print(f"Error creating table: {e}")


