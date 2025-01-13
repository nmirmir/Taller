""" API INVENTORY MANAGEMENT SYSTEM"""

from sqlite3 import Error
from BD_2 import(
    create_connection,
    create_tables,
    add_object,
    update_object,
    delete_object,
    add_zone,
    update_zone,
    delete_zone,
    list_objects,
    list_zones
)

import sqlite3
from datetime import datetime

def init_db():
    conn = create_connection()
    if conn:
        create_tables(conn)
        conn.close()
    else:
        print("Failed to connect to database")

def add_new_object(name,description,zone_id,price,quantity,status,comment=None):
    conn = create_connection()
    if conn: 
        try:
            object_data = {
                'name': name,
                'description': description,
                'zone_id': zone_id,
                'price': price,
                'quantity': quantity,
                'status': status,
                'comment': comment
            }
            object_id = add_object(conn, object_data)
            if object_id:
                print(f"Object {name} added successfully with ID {object_id}")
            else:
                print(f"Failed to add object {name}")
        except Error as e:
            print(f"Error adding object: {e}")
        finally:
            conn.close()
    else:
        print("Failed to connect to database")

def update_object(object_id, name, description, zone_id, price, quantity, status, comment=None):
    conn = create_connection()
    if conn:
        try:
            object_data = {
                'name': name,
                'description': description,
                'zone_id': zone_id,
                'price': price,
                'quantity': quantity,
                'status': status,
                'comment': comment
            }
            update_object(conn, object_data)
            print(f"Object {name} updated successfully")
        except Error as e:
            print(f"Error updating object: {e}")
        finally:
            conn.close()
    else:
        print("Failed to connect to database")

def delete_object(object_id):
    conn = create_connection()
    if conn:
        try:
            delete_object(conn, object_id)
            print(f"Object {object_id} deleted successfully")
        except Error as e:
            print(f"Error deleting object: {e}")
        finally:
            conn.close()
    else:
        print("Failed to connect to database")

def add_new_zone(name):
    conn = create_connection()
    if conn:
        zone_data = {
            'name': name
        }
        zone_id = add_zone(conn, zone_data)
        if zone_id:
            print(f"Zone {name} added successfully with ID {zone_id}")
        else:
            print(f"Failed to add zone {name}")
    else:
        print("Failed to connect to database")

def update_zone(zone_id, name):
    conn = create_connection()
    if conn:
        try:
            zone_data = {
                'name': name
            }
            update_zone(conn, zone_data)
            print(f"Zone {name} updated successfully")
        except Error as e:
            print(f"Error updating zone: {e}")
        finally:
            conn.close()
    else:
        print("Failed to connect to database")

def delete_zone(zone_id):
    conn = create_connection()
    if conn:
        delete_zone(conn, zone_id)
        print(f"Zone {zone_id} deleted successfully")
    else:
        print("Failed to connect to database")

def list_objects():
    conn = create_connection()
    if conn:
        objects = list_objects(conn)
        if objects:
            print("Objects:")
            for object in objects:
                print(f"ID: {object[0]}, Name: {object[1]}, Description: {object[2]}, Price: {object[3]}, Quantity: {object[4]}, Zone: {object[5]}, Status: {object[6]}")
        else:
            print("No objects found")
    else:
        print("Failed to connect to database")

def list_zones():
    conn = create_connection()
    if conn:
        zones = list_zones(conn)
        if zones:
            print("Zones:")
            for zone in zones:
                print(f"ID: {zone[0]}, Name: {zone[1]}")
        else:
            print("No zones found")
    else:
        print("Failed to connect to database")


if __name__ == '__main__':
    init_db()