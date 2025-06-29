import socket
import netifaces
import xml.etree.ElementTree as ET
from lxml import etree
import hashlib
import os

# Hardcoded credentials for the single user
ADMIN_USERNAME = "admin"
# Generate a secure password hash (you should change this password)
ADMIN_PASSWORD_HASH = hashlib.sha256("your_secure_password".encode()).hexdigest()

# Load and validate XML schema
SCHEMA_FILE = "schema.xml"

## CARGAR EL ESQUEMA
def load_schema():
    """Load the XML schema for validation"""
    try:
        with open(SCHEMA_FILE, 'r') as schema_file:
            schema_doc = etree.parse(schema_file)
            schema = etree.XMLSchema(schema_doc)
            return schema
    except Exception as e:
        print(f"Error loading schema: {e}")
        return None

## VALIDAR EL OBJETO
def validate_object(xml_string, schema):
    """Validate an XML object against the schema"""
    try:
        root = ET.fromstring(xml_string)
        schema.assertValid(root)
        return True
    except Exception as e:
        print(f"Validation error: {e}")
        return False

## OBTENER LA SUBRED
def get_subnet():
    """Get the subnet of the server"""
    interfaces = netifaces.interfaces()
    for interface in interfaces:
        addrs = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addrs:
            for addr in addrs[netifaces.AF_INET]:
                ip = addr['addr']
                netmask = addr['netmask']
                # Return the first non-localhost subnet found
                if not ip.startswith('127.'):
                    return (ip, netmask)
    return None

## COMPROBAR SI EL CLIENTE ESTA EN LA MISMA SUBRED
def check_client_authorization(client_address):
    """Check if client is on the same subnet"""
    server_subnet = get_subnet()
    if not server_subnet:
        return False
    
    server_ip, server_netmask = server_subnet
    
    # Convert IP addresses to integers
    server_ip_int = int(''.join(['%02x' % int(x) for x in server_ip.split('.')]), 16)
    client_ip_int = int(''.join(['%02x' % int(x) for x in client_address.split('.')]), 16)
    netmask_int = int(''.join(['%02x' % int(x) for x in server_netmask.split('.')]), 16)
    
    # Compare network addresses
    return (server_ip_int & netmask_int) == (client_ip_int & netmask_int)

## COMPROBAR LAS CREDENCIALES
def check_credentials(username, password):
    """Verify username and password against stored credentials"""
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return username == ADMIN_USERNAME and password_hash == ADMIN_PASSWORD_HASH

## INICIAR EL SERVIDOR
def start_server(port=5000):
    schema = load_schema()
    if not schema:
        print("Failed to load schema. Server shutting down.")
        return

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(1)
    
    print(f"Server listening on port {port}")
    
    while True:
        client_socket, client_address = server_socket.accept()
        client_ip = client_address[0]
        
        if check_client_authorization(client_ip):
            credentials = client_socket.recv(1024).decode().split(':')
            if len(credentials) == 2 and check_credentials(*credentials):
                client_socket.send("Authorized".encode())
                
                # Wait for XML data
                xml_data = client_socket.recv(4096).decode()
                if validate_object(xml_data, schema):
                    client_socket.send("Object validated successfully".encode())
                    # Here you would process and store the valid object
                else:
                    client_socket.send("Invalid object format".encode())
            else:
                client_socket.send("Invalid credentials".encode())
        else:
            client_socket.send("Unauthorized network".encode())
        
        client_socket.close()

if __name__ == '__main__':
    start_server() 