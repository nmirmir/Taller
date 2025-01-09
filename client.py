import socket
import xml.etree.ElementTree as ET

def create_sample_object():
    """Create a sample object following the schema"""
    object_xml = """
    <object>
        <id>1</id>
        <name>Sample Object</name>
        <description>This is a test object</description>
        <price>99.99</price>
        <quantity>10</quantity>
        <category>Test</category>
        <zone>Zone1</zone>
        <creation_date>2024-03-20</creation_date>
        <modification_date>2024-03-20</modification_date>
        <deletion_date>2024-03-20</deletion_date>
        <status>Active</status>
        <creation_user>admin</creation_user>
        <modification_user>admin</modification_user>
        <deletion_user></deletion_user>
    </object>
    """
    return object_xml

def connect_to_server(username, password, xml_data, host='localhost', port=5000):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host, port))
        
        # Send credentials
        credentials = f"{username}:{password}"
        client_socket.send(credentials.encode())
        response = client_socket.recv(1024).decode()
        print(f"Authentication response: {response}")
        
        if response == "Authorized":
            # Send XML data
            client_socket.send(xml_data.encode())
            validation_response = client_socket.recv(1024).decode()
            print(f"Validation response: {validation_response}")
            
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        client_socket.close()

if __name__ == '__main__':
    sample_object = create_sample_object()
    connect_to_server("admin", "your_secure_password", sample_object) 