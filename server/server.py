import socket
import threading
import datetime
import time
import sys
import os

# Server configuration
HOST=input("Enter the HOST IP:")
PORT=int(input("Enter the Port number:"))

clients = {}
server_running = True

# Function to broadcast messages to all clients except sender
def broadcast(message, sender_socket=None):
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

def send_user_list(client_socket):
    users = list(clients.values())
    user_list_message = "USERLIST:" + ",".join(users)
    try:
        client_socket.send(user_list_message.encode('utf-8'))
    except:
        print(f"Error sending user list to {clients.get(client_socket, 'unknown')}")

def send_user_list_to_all():
    users = list(clients.values())
    user_list_message = "USERLIST:" + ",".join(users)
    for client_socket in clients:
        try:
            client_socket.send(user_list_message.encode('utf-8'))
        except:
            print(f"Error sending user list to {clients.get(client_socket, 'unknown')}")

def kick_user(username, sender_socket):
    # Find the socket of the user to kick
    user_socket = None
    for sock, name in clients.items():
        if name == username:
            user_socket = sock
            break
    
    if not user_socket:
        return False
    
    # Send kick notification to the kicked user
    try:
        user_socket.send(f"KICKED:{username}".encode('utf-8'))
    except:
        pass
    
    # Notify all other users about the kick
    current_time = datetime.datetime.now().strftime("%H:%M")
    kick_message = f"{username} has been kicked from the chat. [{current_time}]"
    broadcast(kick_message)
    print(kick_message)
    
    # Remove the kicked user from clients dictionary
    if user_socket in clients:
        del clients[user_socket]
        
    # Update the user list for all remaining clients
    send_user_list_to_all()
    
    # Close the socket connection
    try:
        user_socket.close()
    except:
        pass
    
    return True

# Function to handle individual client connections
def handle_client(client_socket):
    global server_running
    try:
        username = client_socket.recv(1024).decode('utf-8')
        clients[client_socket] = username
        current_time = datetime.datetime.now().strftime("%H:%M")
        join_message = f"{username} has joined the chat! [{current_time}]"
        broadcast(join_message, client_socket)
        print(join_message)
        
        # Send updated user list to all clients
        send_user_list_to_all()
        
        while server_running:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                    
                # Handle special command for requesting user list
                if message == "GET_USERS":
                    send_user_list(client_socket)
                    continue
                
                # Handle kick command
                if message.startswith("KICK:"):
                    user_to_kick = message.split(":", 1)[1]
                    if kick_user(user_to_kick, client_socket):
                        print(f"{clients[client_socket]} kicked {user_to_kick} from the chat")
                    continue
                
                # Add timestamp to the message - format changed to whatsapp style
                current_time = datetime.datetime.now().strftime("%H:%M")
                formatted_message = f"{username} [{current_time}]: {message}"
                print(formatted_message)
                broadcast(formatted_message, client_socket)
            except:
                if not server_running:
                    break
                raise  
                
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        if client_socket in clients and server_running:
            username = clients[client_socket]
            current_time = datetime.datetime.now().strftime("%H:%M")
            leave_message = f"{username} has left the chat. [{current_time}]"
            broadcast(leave_message, client_socket)
            print(leave_message)
            del clients[client_socket]
            # Update user list for all clients
            send_user_list_to_all()
        try:
            client_socket.close()
        except:
            pass

def shutdown_server():
    global server_running
    server_running = False
    print("Shutting down server...")
    
    broadcast("SERVER_SHUTDOWN")
    
    time.sleep(1)
    
    # Close all client connections
    for client_socket in list(clients.keys()):
        try:
            client_socket.close()
        except:
            pass
    
    print("All clients notified. Server is shutting down.")
    os._exit(0)  

def console_input():
    global server_running
    while server_running:
        cmd = input("Enter 'shutdown' to stop the server: ")
        if cmd.lower() == "shutdown":
            shutdown_server()
            break

def start_server():
    global server_running
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    server.bind((HOST, PORT)) 
    server.listen(5)
    print(f"Server started on {HOST}:{PORT}")
    print("Type 'shutdown' to stop the server.")
    
    # Start console input thread
    console_thread = threading.Thread(target=console_input, daemon=True)
    console_thread.start()

    try:
        while server_running:
            server.settimeout(1.0)
            try:
                client_socket, client_address = server.accept()  
                print(f"New connection from {client_address}")
                client_thread = threading.Thread(target=handle_client, args=(client_socket,))
                client_thread.daemon = True
                client_thread.start()
            except socket.timeout:
                continue
            except Exception as e:
                if server_running:
                    print(f"Error accepting connection: {e}")
    except KeyboardInterrupt:
        print("Keyboard interrupt detected.")
        shutdown_server()
    finally:
        server_running = False
        try:
            server.close()
        except:
            pass
        print("Server has been shut down.")

if __name__ == "__main__":
    start_server()