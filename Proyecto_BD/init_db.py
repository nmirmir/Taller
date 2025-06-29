import sqlite3
from datetime import datetime

def init_db():
    # Create a new database connection
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    
    # Drop existing tables if they exist
    cursor.execute('DROP TABLE IF EXISTS history')
    cursor.execute('DROP TABLE IF EXISTS objects')
    cursor.execute('DROP TABLE IF EXISTS zones')
    
    # Create tables
    cursor.execute('''
        CREATE TABLE zones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE objects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            zone_id INTEGER,
            price REAL DEFAULT 0,
            quantity INTEGER DEFAULT 0,
            status TEXT DEFAULT 'Available',
            FOREIGN KEY (zone_id) REFERENCES zones (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            object_id INTEGER,
            zone_id INTEGER,
            action_type TEXT,
            modification_date DATETIME,
            comment TEXT,
            FOREIGN KEY (object_id) REFERENCES objects (id),
            FOREIGN KEY (zone_id) REFERENCES zones (id)
        )
    ''')
    
    # Insert some default data
    cursor.execute("INSERT INTO zones (name) VALUES ('Zona Soldadura')")
    cursor.execute("INSERT INTO zones (name) VALUES ('Zona Impresion')")
    cursor.execute("INSERT INTO zones (name) VALUES ('Zona Mecanizado')")
    cursor.execute("INSERT INTO zones (name) VALUES ('Zona del laser')")
    
    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db() 