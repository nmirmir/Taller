import sqlite3
from sqlite3 import Error


## CONEXION A LA BASE DE DATOS

def create_connection():
    """Create a database connection to a SQLite database"""
    try:
        conn = sqlite3.connect('my_database.db')
        print("Successfully connected to SQLite database")
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None


## CREACION DE LAS TABLAS
def create_table(conn):
    """Create a sample table"""
    try:
        cursor = conn.cursor()
        
        # Creating a simple users table
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            age INTEGER
        );
        """
        
        cursor.execute(create_users_table)
        conn.commit()
        print("Table created successfully")
        
    except Error as e:
        print(f"Error creating table: {e}")

## INSERTAR UN OBJETO
def add_object(conn, object):
    """Add a new object"""
    cursor = conn.cursor()
    cursor.execute("INSERT INTO objects(name, description, price, quantity, category, zone, creation_date, modification_date, deletion_date, status, creation_user, modification_user, deletion_user) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", object)
    conn.commit()
    return cursor.lastrowid


## INSERTAR UN USUARIO
def insert_user(conn, user):
    """Insert a new user into the users table"""
    sql = '''INSERT INTO users(name, email, age)
            VALUES(?,?,?)'''
    try:
        cursor = conn.cursor()
        cursor.execute(sql, user)
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

## OBTENER TODAS LAS ZONAS
def get_all_zones(conn):
    """Get all zones"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM zones")
    rows = cursor.fetchall()
    return rows #return the zones
    




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
