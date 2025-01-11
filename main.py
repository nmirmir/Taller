"""
Inventory Management System
This program manages an inventory database with objects, zones, categories, and statuses.
It provides a command-line interface for all CRUD operations.
"""

# Import necessary modules and functions from BD.py
from sqlite3 import Error
from BD import (
    create_connection, 
    create_table, 
    add_object, 
    update_object, 
    delete_object,
    get_all_objects,
    get_all_categories,
    get_all_statuses,
    get_zone_by_id,
    add_category,
    add_zone,
    get_all_zones,
    remove_zone,
    add_history,
    get_history_summary,
    delete_zone_objects,
    delete_category_objects,
    delete_status_objects,
    delete_all_objects
)
import sqlite3
from datetime import datetime

def create_connection():
    return sqlite3.connect('inventory.db')

def get_zones():
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, name FROM zones')
        
        zones = []
        for row in cursor.fetchall():
            zones.append({
                'id': row[0],
                'name': row[1]
            })
            
        return zones
        
    except Exception as e:
        print(f"Error in get_zones: {e}")
        return []
    finally:
        if conn:
            conn.close()

def init_db():
    conn = create_connection()
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS zones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS objects (
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
        CREATE TABLE IF NOT EXISTS history (
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
    
    # Insert a default zone if none exists
    cursor.execute('SELECT COUNT(*) FROM zones')
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO zones (name) VALUES ('Default Zone')")
    
    conn.commit()
    conn.close()

def add_object(name, description, zone_id, price, quantity, status, comment=None):
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        # Insert object
        cursor.execute('''
            INSERT INTO objects (name, description, zone_id, price, quantity, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, description, zone_id, price, quantity, status))
        
        object_id = cursor.lastrowid
        
        # Add history entry
        cursor.execute('''
            INSERT INTO history (object_id, zone_id, action_type, modification_date, comment)
            VALUES (?, ?, ?, ?, ?)
        ''', (object_id, zone_id, 'CREATE', datetime.now(), comment))
        
        conn.commit()
        return object_id
        
    except Exception as e:
        print(f"Error in add_object: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def get_objects():
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT o.*, z.name as zone_name 
            FROM objects o
            LEFT JOIN zones z ON o.zone_id = z.id
        ''')
        
        objects = []
        for row in cursor.fetchall():
            objects.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'zone_id': row[3],
                'price': row[4],
                'quantity': row[5],
                'status': row[6],
                'zone_name': row[7] if len(row) > 7 else ''
            })
            
        return objects
        
    except Exception as e:
        print(f"Error in get_objects: {e}")
        return []
    finally:
        if conn:
            conn.close() 
