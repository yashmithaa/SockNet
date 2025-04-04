import socket
import threading

# Server configuration
HOST = '127.0.0.1'  
PORT = 12345        
clients = {}        

# Function to broadcast messages to all clients except sender
def broadcast(message, sender_socket):
    disconnected_clients = []
    for client_socket in clients:
        if client_socket != sender_socket:  
            try:
                client_socket.send(message.encode('utf-8'))
            except:
                disconnected_clients.append(client_socket)
    
    for client_socket in disconnected_clients:
        if client_socket in clients:
            client_socket.close()
            del clients[client_socket]

# Function to handle individual client connections
def handle_client(client_socket):
    try:
        client_socket.send("Enter your username: ".encode('utf-8'))
        username = client_socket.recv(1024).decode('utf-8')
        clients[client_socket] = username
        broadcast(f"{username} has joined the chat!", client_socket)
        print(f"{username} has joined the chat!")
        
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"{username}: {message}")
            broadcast(f"{username}: {message}", client_socket)
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        if client_socket in clients:
            username = clients[client_socket]
            broadcast(f"{username} has left the chat.", client_socket)
            print(f"{username} has left the chat.")
            del clients[client_socket]
        client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    server.bind((HOST, PORT)) 
    server.listen(5)  
    print(f"Server started on {HOST}:{PORT}")

    try:
        while True:
            client_socket, client_address = server.accept()  
            print(f"New connection from {client_address}")
            threading.Thread(target=handle_client, args=(client_socket,)).start()
    except KeyboardInterrupt:
        print("Server shutting down...")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()