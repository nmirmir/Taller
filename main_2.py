""" API INVENTORY MANAGEMENT SYSTEM"""

from sqlite3 import Error
from BD_2 import(
    create_connection,
    create_tables,
    add_object,
    update_object,
    delete_object
)

import sqlite3
from datetime import datetime

def create_connection():
    return sqlite3.connect('inventory_2.db')

def init_db():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS zones (
            id INTEGER PRIMERY KEY AUTOINCREMENT,,
            name TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS objects (
            id PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL DEFAULT 0,
            quantity INTEGER DEFAULT 0,
            status TEXT DEFAULT 'Available',
            zone_id INTEGER,
            FOREIGN KEY (zone_id) REFERENCES zones (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history(
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

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()