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
    add_zone
)

def print_menu():
    print("\n=== Database Management System ===")
    print("1. Add new object")
    print("2. Update object")
    print("3. Delete object")
    print("4. Add item to Zona de Mecanizado")
    print("5. Add item to Zona de Soldadura")
    print("6. Add item to Zona de Impresion")
    print("7. Add item to Zona del Laser")
    print("8. List all objects")
    print("9. List all categories")
    print("10. List items by zone")
    print("0. Exit")
    print("================================")

def get_object_input(zone_id):
    """Get object details from user with predefined zone"""
    try:
        name = input("Enter object name: ")
        description = input("Enter description: ")
        price = float(input("Enter price: "))
        quantity = int(input("Enter quantity: "))
        category_id = int(input("Enter category ID: "))
        status_id = int(input("Enter status ID: "))
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
        description = input("Enter zone description: ")
        user = input("Enter your username: ")
        
        return (name, description, user)
    except ValueError:
        print("Invalid input! Please enter correct data types.")
        return None

def list_zone_items(conn, zone_id, zone_name):
    """List all items in a specific zone"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, description, price, quantity 
            FROM objects 
            WHERE zone_id = ?
        """, (zone_id,))
        items = cursor.fetchall()
        
        print(f"\n=== Items in {zone_name} ===")
        if items:
            for item in items:
                print(f"\nID: {item[0]}")
                print(f"Name: {item[1]}")
                print(f"Description: {item[2]}")
                print(f"Price: ${item[3]}")
                print(f"Quantity: {item[4]}")
                print("-" * 30)
        else:
            print("No items found in this zone.")
    except Error as e:
        print(f"Error retrieving items: {e}")

def main():
    # Create database connection
    conn = create_connection()
    if conn is None:
        print("Error! Cannot create database connection.")
        return

    # Create tables
    create_table(conn)
    
    # Define zones
    ZONES = {
        4: ("Zona de Mecanizado", 1),
        5: ("Zona de Soldadura", 2),
        6: ("Zona de Impresion", 3),
        7: ("Zona del Laser", 4)
    }
    
    while True:
        print_menu()
        choice = input("Enter your choice (0-10): ")
        
        if choice == '0':
            break
            
        elif choice in ['4', '5', '6', '7']:
            zone_name, zone_id = ZONES[int(choice)]
            print(f"\n--- Adding new object to {zone_name} ---")
            object_data = get_object_input(zone_id)
            if object_data:
                object_id = add_object(conn, object_data)
                if object_id:
                    print(f"Successfully added object with ID: {object_id}")
            
        elif choice == '8':
            print("\n--- Listing all objects ---")
            objects = get_all_objects(conn)
            for obj in objects:
                print(f"\nID: {obj[0]}")
                print(f"Name: {obj[1]}")
                print(f"Description: {obj[2]}")
                print(f"Price: ${obj[3]}")
                print(f"Quantity: {obj[4]}")
                print("-" * 30)
            
        elif choice == '9':
            print("\n--- Listing all categories ---")
            categories = get_all_categories(conn)
            for category in categories:
                print(f"ID: {category[0]}, Name: {category[1]}")
            
        elif choice == '10':
            print("\n--- List items by zone ---")
            print("1. Zona de Mecanizado")
            print("2. Zona de Soldadura")
            print("3. Zona de Impresion")
            print("4. Zona del Laser")
            try:
                zone_choice = int(input("Select zone (1-4): "))
                if 1 <= zone_choice <= 4:
                    zone_name = list(ZONES.values())[zone_choice-1][0]
                    list_zone_items(conn, zone_choice, zone_name)
                else:
                    print("Invalid zone selection!")
            except ValueError:
                print("Invalid input! Please enter a number.")
            
        else:
            print("Invalid choice! Please try again.")
        
        input("\nPress Enter to continue...")
    
    # Close the connection
    conn.close()
    print("\nDatabase connection closed.")

if __name__ == "__main__":
    main() 