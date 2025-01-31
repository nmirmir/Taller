""" API INVENTORY MANAGEMENT SYSTEM"""
from datetime import datetime
from sqlite3 import Error
from BD_2 import(
    create_connection,
    create_table,
    add_object,
    update_object,
    delete_object,
    add_zone,
    update_zone,
    delete_zone,
    add_status,
    add_category,
    list_objects,
    list_zones
)

def display_menu():
    print("--------------------------------")
    #print("Hello world por culpa de SHAUME")
    print("Inventory Management System")
    print("1. Add new object")
    print("2. Update object")
    print("3. Delete object")
    print("4. Add new zone")
    print("5. Update zone")
    print("6. Delete zone")
    print("7. List objects")
    print("8. List zones")
    print("9. Exit")
    print("--------------------------------")

def handle_user_input():
    while True:
        display_menu()
        choice = input("Enter your choice: ")
        
        if choice == '1':
            # Add new object
            try:
                
                name = input("Enter the name of the object: ")
                description = input("Enter the description of the object: ")
                price = float(input("Enter the price of the object: "))
                quantity = int(input("Enter the quantity of the object: "))
                #status = int(input("Enter status of the object: "))        MEJORA
                #list_statuses(conn)
                
                conn = create_connection()
                # Show available zones
                list_zones(conn)
                
                zone_id = int(input("Enter the ID of the zone: "))
                if conn:
                    object_data = {
                        'name': name,
                        'description': description,
                        'zone_id': zone_id,
                        'price': price,
                        'quantity': quantity,
                        'status_id': 1  # Default status
                    }
                    
                    object_id = add_object(conn, object_data)
                    if object_id:
                        print(f"\nObject {name} added successfully with ID {object_id}")
                    else:
                        print(f"\nFailed to add object {name}")
                    conn.close()
                else:
                    print("Failed to connect to database")
            except ValueError as e:
                print(f"\nInvalid input: Please enter numbers for price and quantity")
            except Exception as e:
                print(f"\nError: {e}")

        elif choice == '2':
            # Update object
            conn = create_connection()
            if conn:
                objects = list_objects(conn)
                print("Objects:")
                for object in objects:
                    print(f"ID: {object[0]}, Name: {object[1]}, Description: {object[2]}, Price: {object[3]}, Quantity: {object[4]}, Zone: {object[5]}, Status: {object[6]}")
                print("Enter the ID of the object to update:")
                object_id = input()
                print("What you want to update?")
                print("1. Name")
                print("2. Description")
                print("3. Price")
                print("4. Quantity")
                print("5. Zone")
                print("6. Status")
                print("7. Comment")
                update_choice = input("Enter the number of the field to update:")
                if update_choice == '1':
                    name = input("Enter the new name:")
                elif update_choice == '2':
                    description = input("Enter the new description:")
                elif update_choice == '3':
                    price = input("Enter the new price:")
                elif update_choice == '4':
                    quantity = input("Enter the new quantity:")
                elif update_choice == '5':
                    zone_id = input("Enter the new zone ID:")
                elif update_choice == '6':
                    status = input("Enter the new status:")
                elif update_choice == '7':
                    comment = input("Enter the new comment:")
                update_object(object_id, name, description, zone_id, price, quantity, status, comment)
                print(f"Object {name} updated successfully")
            else:
                print("Failed to connect to database")
        elif choice == '3':
            # Delete object
            conn = create_connection()
            if conn:
                objects = list_objects(conn)
                print("Objects:")
                for object in objects:
                    print(f"ID: {object[0]}, Name: {object[1]}, Description: {object[2]}, Price: {object[3]}, Quantity: {object[4]}, Zone: {object[5]}, Status: {object[6]}")
                print("Enter the ID of the object to delete:")
                object_id = input()
                delete_object(object_id)
                print(f"Object {object_id} deleted successfully")
            else:
                print("Failed to connect to database")
        elif choice == '4':
            # Add new zone
            conn = create_connection()
            if conn:
                zones = list_zones(conn)
                if zones:
                    print("Zones:")
                    for zone in zones:
                        print(f"ID: {zone[0]}, Name: {zone[1]}")
                name = input("Enter the name of the zone:")
                add_new_zone(name)
            else:
                print("Failed to connect to database")
        elif choice == '5':
            # Update zone
            conn = create_connection()
            if conn:
                zones = list_zones(conn)
                if zones:
                    print("Zones:")
                    for zone in zones:
                        print(f"ID: {zone[0]}, Name: {zone[1]}")
                else:
                    print("No zones found")
                zone_id = input("Enter the ID of the zone to update:")
                print("What you want to update?")
                print("1. Name")
                print("2. Comment")
                update_choice = input("Enter the number of the field to update:")
                if update_choice == '1':
                    name = input("Enter the new name:")
                elif update_choice == '2':
                    comment = input("Enter the new comment:")
                update_zone(zone_id, name, comment)
                print(f"Zone {name} updated successfully")
            else:
                print("Failed to connect to database")

        elif choice == '6':
            # Delete zone
            conn = create_connection()
            if conn:
                zones = list_zones(conn)
                if zones:
                    print("Zones:")
                    for zone in zones:
                        print(f"ID: {zone[0]}, Name: {zone[1]}")
                else:
                    print("No zones found")
                zone_id = input("Enter the ID of the zone to delete:")
                delete_zone(zone_id)
                print(f"Zone {zone_id} deleted successfully")
            else:
                print("Failed to connect to database")
        elif choice == '7':
            # List objects
            conn = create_connection()
            if conn:
                list_objects(conn)
            else:
                print("Failed to connect to database")
        elif choice == '8':
            # List zones
            conn = create_connection()
            if conn:
                try:
                    zones = list_zones(conn)
                    print(f"Zones: {zones}")
                except Error as e:
                    print(f"Error listing zones: {e}")
                finally:
                    conn.close()
        elif choice == '9':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

def init_db():
    conn = create_connection()  # Ensure create_connection() connects to your database
    if conn:
        try:
            # Create tables
            create_table(conn)

            # Add default zones
            cursor = conn.cursor()
            default_zones = [
                ("Machining Zone", "Zone for machining operations."),
                ("Welding Zone", "Zone for welding operations."),
                ("Printing Zone", "Zone for printing operations."),
                ("Laser Zone", "Zone for laser operations.")
            ]
            #print(f"default zones: {default_zones}")
            for name, description in default_zones:
                cursor.execute("SELECT id FROM zones WHERE name = ?", (name,))
                if not cursor.fetchone():                    
                    cursor.execute("""
                        INSERT INTO zones (name, description, creation_date, modification_date, deletion_date)
                        VALUES (?, ?, datetime('now'), datetime('now'), NULL)
                    """, (name, description))

            # Add default statuses
            default_statuses = ['Available', 'Not Available', 'In Repair', 'In Use']
            for status in default_statuses:
                add_status(conn, {'name': status})

            # Add default categories
            import datetime

            # Add default categories with current timestamps
            default_categories = [
                ('consumables', 'Something that has one use', datetime.datetime.now(), datetime.datetime.now(), None),
                ('tools', 'What you use for actions', datetime.datetime.now(), datetime.datetime.now(), None)
            ]

            for category in default_categories:
                add_category(conn,category)
            print(f"default_categories{default_categories}")

            conn.commit()
            print("Database initialized successfully.")
        except Error as e:
            print(f"Error initializing database: {e}")
            conn.rollback()
        finally:
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
            'name': name,
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

def add_categor(name):
    conn = create_connection()
    if conn:
        category_data = {
            'name': name,
        }
        category_id = add_category(conn, category_data)
        if category_id:
            print(f"Category {name} added successfully with ID {category_id}")
        else:
            print(f"Failed to add category {name}")
    else:
        print("Failed to connect to database")



def display_objects():
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




if __name__ == '__main__':
    # Initialize the database
    init_db()
    # Handle user input
    handle_user_input()
