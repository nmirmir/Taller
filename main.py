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
    remove_zone
)

def print_menu():
    print("\n=== Database Management System ===")
    print("1. Add new object")
    print("2. Update object")
    print("3. Delete object")
    print("4. List all objects")
    print("5. List all categories")
    print("6. List items by zone")
    print("7. Add category")
    print("8. Add zone")
    print("9. List all zones")
    print("10. Remove zone")
    print("0. Exit")
    print("================================")

def get_object_input():
    """Get object details from user"""
    try:
        print("\nAvailable zones:")
        zones = get_all_zones(conn)
        for zone in zones:
            print(f"ID: {zone[0]} - Name: {zone[1]}")
        
        zone_id = int(input("\nEnter zone ID: "))
        name = input("Enter object name: ")
        description = input("Enter description: ")
        price = float(input("Enter price: "))
        quantity = int(input("Enter quantity: "))
        
        print("\nAvailable categories:")
        categories = get_all_categories(conn)
        for category in categories:
            print(f"ID: {category[0]} - {category[1]}")
        category_id = int(input("\nEnter category ID: "))
        
        print("\nAvailable statuses:")
        statuses = get_all_statuses(conn)
        for status in statuses:
            print(f"ID: {status[0]} - {status[1]}")
        status_id = int(input("\nEnter status ID: "))
        
        user = input("Enter your username: ")
        
        return (name, description, price, quantity, 
                category_id, zone_id, status_id, 
                user, user)
    except ValueError:
        print("Invalid input! Please enter correct data types.")
        return None



def get_update_input():
    """Get update details from user"""
    updates = {}
    try:
        print("\nWhat would you like to update?")
        print("1. Price")
        print("2. Quantity")
        print("3. Both")
        choice = input("Enter choice (1-3): ")
        
        if choice in ['1', '3']:
            updates['price'] = float(input("Enter new price: "))
        if choice in ['2', '3']:
            updates['quantity'] = int(input("Enter new quantity: "))
            
        # Get modification user
        updates['modification_user'] = input("Enter your username: ")
            
        return updates
    except ValueError:
        print("Invalid input! Please enter correct data types.")
        return None

def get_category_input():
    """Get category details from user"""
    try:
        name = input("Enter category name: ")
        description = input("Enter category description: ")
        user = input("Enter your username: ")
        
        return (name, description, user)
    except ValueError:
        print("Invalid input! Please enter correct data types.")
        return None

def get_zone_input():
    """Get zone details from user"""
    try:
        name = input("Enter zone name: ")
        return (name,)  # Return only the name
    except ValueError:
        print("Invalid input! Please enter a valid name.")
        return None

def display_objects(objects):
    """Display objects in a consistent format"""
    if objects:
        for obj in objects:
            print(f"\nID: {obj[0]}")
            print(f"Name: {obj[1]}")
            print(f"Description: {obj[2]}")
            print(f"Price: ${obj[3]}")
            print(f"Quantity: {obj[4]}")
            print(f"Status: {obj[5]}")
            print("-" * 30)
    else:
        print("No objects found")

def get_zone_id(conn, zone_name):
    """Get the id of a zone by name"""
    zone = get_zone_by_id(conn, zone_name)
    return zone[0]

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
    global conn
    # Create database connection
    conn = create_connection()
    if conn is None:
        print("Error! Cannot create database connection.")
        return

    # Create tables
    create_table(conn)
    
    while True:
        print_menu()
        choice = input("Enter your choice (0-10): ")
        
        if choice == '0':
            break
            
        elif choice == '1':
            print("\n--- Adding new object ---")
            object_data = get_object_input()
            if object_data:
                object_id = add_object(conn, object_data)
                if object_id:
                    print(f"Successfully added object with ID: {object_id}")
            
        elif choice == '2':
            print("\n--- Updating object ---")
            try:
                object_id = int(input("Enter object ID to update: "))
                updates = get_update_input()
                if updates:
                    modification_user = updates.pop('modification_user')  # Remove and get modification_user
                    update_object(conn, object_id, updates, modification_user)
                    print("Object updated successfully.")
            except ValueError:
                print("Invalid input! Please enter a valid object ID.")
            
        elif choice == '3':
            print("\n--- Deleting object ---")
            # First show all objects
            print("\nAvailable objects:")
            objects = get_all_objects(conn)
            for obj in objects:
                print(f"\nID: {obj[0]}")
                print(f"Name: {obj[1]}")
                print(f"Description: {obj[2]}")
                print(f"Price: ${obj[3]}")
                print(f"Quantity: {obj[4]}")
                print("-" * 30)
            
            try:
                object_id = int(input("\nEnter object ID to delete: "))
                user = input("Enter your username: ")
                if delete_object(conn, object_id, user):
                    print("Object deleted successfully.")
                else:
                    print("Failed to delete object.")
            except ValueError:
                print("Invalid input! Please enter a valid object ID.")
            
        elif choice == '4':
            print("\n--- Listing all objects ---")
            objects = get_all_objects(conn)
            display_objects(objects)
            
        elif choice == '5':
            print("\n--- Listing all categories ---")
            categories = get_all_categories(conn)
            for category in categories:
                print(f"ID: {category[0]}, Name: {category[1]}")
            
        elif choice == '6':
            print("\n--- List items by zone ---")
            zones = get_all_zones(conn)
            for zone in zones:
                print(f"{zone[0]}. {zone[1]}")
            try:
                zone_choice = int(input("\nSelect zone ID: "))
                zone_exists = False
                zone_name = ""
                for zone in zones:
                    if zone[0] == zone_choice:
                        zone_exists = True
                        zone_name = zone[1]
                        break
                
                if zone_exists:
                    print(f"\n=== Items in {zone_name} ===")
                    items = list_zone_items(conn, zone_choice, zone_name)
                    display_objects(items)
                else:
                    print("Invalid zone selection!")
            except ValueError:
                print("Invalid input! Please enter a number.")
            
        elif choice == '7':
            print("\n--- Adding new category ---")
            category_data = get_category_input()
            if category_data:
                add_category(conn, category_data)
                print("Category added successfully.")
            
        elif choice == '8':
            print("\n--- Adding new zone ---")
            zone_data = get_zone_input()
            if zone_data:
                zone_id = add_zone(conn, zone_data)
                if zone_id:
                    print(f"Zone added successfully with ID: {zone_id}")
                else:
                    print("Failed to add zone")
            
        elif choice == '9':
            print("\n--- Listing all zones ---")
            zones = get_all_zones(conn)
            if zones:
                print("\nAvailable Zones:")
                print("-" * 40)
                for zone in zones:
                    print(f"ID: {zone[0]} - Name: {zone[1]}")
                    print("-" * 40)
            else:
                print("No zones found")
            
        elif choice == '10':
            print("\n--- Removing zone ---")
            # Show available zones first
            zones = get_all_zones(conn)
            if zones:
                print("\nAvailable Zones:")
                for zone in zones:
                    print(f"ID: {zone[0]} - Name: {zone[1]}")
                
                try:
                    zone_id = int(input("\nEnter zone ID to remove: "))
                    remove_zone(conn, zone_id)
                except ValueError:
                    print("Invalid input! Please enter a valid zone ID.")
            else:
                print("No zones available to remove.")
            
        else:
            print("Invalid choice! Please try again.")
        
        input("\nPress Enter to continue...")
    
    # Close the connection
    conn.close()
    print("\nDatabase connection closed.")

if __name__ == "__main__":
    conn = None  # Global connection variable
    main() 