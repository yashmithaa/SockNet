# server.py
import socket
import threading

# Server configuration
HOST = '127.0.0.1'  
PORT = 12345        
clients = {}        
# Function to broadcast messages to all clients except sender
def broadcast(message, sender_socket):
    for client in clients:
        if client != sender_socket:  
            try:
                client.send(message.encode('utf-8'))
            except:
                client.close()
                del clients[client]

# Function to handle individual client connections
def handle_client(client_socket):
    try:
        client_socket.send("Enter your username: ".encode('utf-8'))
        username = client_socket.recv(1024).decode('utf-8')
        clients[client_socket] = username
        broadcast(f"{username} has joined the chat!", client_socket)
        
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            broadcast(f"{username}: {message}", client_socket)
    except:
        pass
    finally:
        broadcast(f"{clients[client_socket]} has left the chat.", client_socket)
        del clients[client_socket]
        client_socket.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    server.bind((HOST, PORT)) 
    server.listen(5)  
    print(f"Server started on {HOST}:{PORT}")

    while True:
        client_socket, client_address = server.accept()  
        print(f"New connection from {client_address}")
        threading.Thread(target=handle_client, args=(client_socket,)).start()


if __name__ == "__main__":
    start_server()
