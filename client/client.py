import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, font
from tkinter import ttk
import datetime
import sys

# Client configuration
HOST = '127.0.0.1'
PORT = 12345

# Client socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((HOST, PORT))
except ConnectionRefusedError:
    print("Could not connect to server. Server might be offline.")
    sys.exit()

# Active users list
active_users = []

# Get username
username = simpledialog.askstring("Username", "Enter your username:")
client.send(username.encode('utf-8'))

def receive_messages():
    global active_users
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            
            # Check for server shutdown message
            if message == "SERVER_SHUTDOWN":
                chat_box.config(state=tk.NORMAL)
                chat_box.insert(tk.END, "\nServer has been shut down. Application will close in 5 seconds.\n", "system")
                chat_box.config(state=tk.DISABLED)
                chat_box.yview(tk.END)
                root.after(5000, root.destroy)
                break
            
            # Handle user list updates
            if message.startswith("USERLIST:"):
                update_user_list(message[9:].split(","))
                continue
                
            chat_box.config(state=tk.NORMAL)
            
            if "has joined the chat" in message or "has left the chat" in message:
                chat_box.insert(tk.END, f"\n{message}\n", "system")
                # Request updated user list
                client.send("GET_USERS".encode('utf-8'))
            elif ":" in message:
                # Check if message has timestamp
                if " [" in message and "]:" in message:
                    # Message with timestamp from server
                    parts = message.split("]:", 1)
                    if len(parts) == 2:
                        sender_and_time, content = parts
                        sender_and_time += "]"  # Add back the closing bracket
                        
                        if " [" in sender_and_time:
                            sender_parts = sender_and_time.split(" [")
                            sender = sender_parts[0]
                            timestamp = sender_parts[1][:-1]  # Remove the closing bracket
                            
                            if sender != username:
                                # Create WhatsApp style bubble for received message
                                chat_box.insert(tk.END, f"\n", "bubble_spacer")
                                # Add sender name above bubble for group chat clarity
                                chat_box.insert(tk.END, f"{sender}", "sender_name")
                                # Add message in green bubble with timestamp
                                chat_box.insert(tk.END, f"\n{content}", "bubble_other")
                                chat_box.insert(tk.END, f" {timestamp}", "timestamp_in_bubble")
                                chat_box.insert(tk.END, f"\n", "bubble_spacer")
                else:
                    # Legacy message format without timestamp
                    sender, content = message.split(":", 1)
                    if sender != username:
                        chat_box.insert(tk.END, f"\n", "bubble_spacer")
                        chat_box.insert(tk.END, f"{sender}", "sender_name")
                        # Add current time as timestamp
                        current_time = datetime.datetime.now().strftime("%H:%M")
                        chat_box.insert(tk.END, f"\n{content}", "bubble_other")
                        chat_box.insert(tk.END, f" {current_time}", "timestamp_in_bubble")
                        chat_box.insert(tk.END, f"\n", "bubble_spacer")
            
            chat_box.config(state=tk.DISABLED)
            chat_box.yview(tk.END)
        except Exception as e:
            print(f"Error receiving message: {e}")
            chat_box.config(state=tk.NORMAL)
            chat_box.insert(tk.END, "\nLost connection to server. Application will close in 5 seconds.\n", "system")
            chat_box.config(state=tk.DISABLED)
            root.after(5000, root.destroy)
            break

def update_user_list(users):
    # Clear current list
    for item in users_listbox.get_children():
        users_listbox.delete(item)
    
    # Add users to treeview
    for user in users:
        if user and user != username:  # Don't show current user in the list
            users_listbox.insert("", "end", text=user, values=(user,))

def send_message():
    message = message_entry.get()
    message_entry.delete(0, tk.END)
    if message:
        if message == "GET_USERS":  # Special command to request user list
            client.send(message.encode('utf-8'))
            return
            
        # Get current time
        current_time = datetime.datetime.now().strftime("%H:%M")
        
        chat_box.config(state=tk.NORMAL)
        
        # Create WhatsApp style bubble for sent message with timestamp inside bubble - right aligned
        chat_box.insert(tk.END, f"\n", "bubble_spacer")
        chat_box.insert(tk.END, f"{message}", "bubble_self")
        chat_box.insert(tk.END, f" {current_time}", "timestamp_in_bubble_self")
        chat_box.insert(tk.END, f"\n", "bubble_spacer")
        
        chat_box.config(state=tk.DISABLED)
        chat_box.yview(tk.END)
        
        client.send(message.encode('utf-8'))

# Create main window
root = tk.Tk()
root.title("Chat App")
root.configure(bg="#0B141A")  # WhatsApp dark mode background

# Make window fullscreen
root.attributes('-fullscreen', True)
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Create a PanedWindow to hold chat and users sections
main_paned = tk.PanedWindow(root, orient=tk.HORIZONTAL, bg="#0B141A", sashwidth=4)
main_paned.pack(fill=tk.BOTH, expand=True)

# Left panel - Chat section
chat_panel = tk.Frame(main_paned, bg="#0B141A")
main_paned.add(chat_panel, width=int(screen_width * 0.7))

# Right panel - Users section
users_panel = tk.Frame(main_paned, bg="#111B21")
main_paned.add(users_panel, width=int(screen_width * 0.3))

# Chat section setup
chat_frame = tk.Frame(chat_panel, bg="#0B141A")
chat_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

# Custom font for messages - WhatsApp-like
message_font = font.Font(family="Segoe UI", size=13)
name_font = font.Font(family="Segoe UI", size=12)
timestamp_font = font.Font(family="Segoe UI", size=10)

# Chat box with WhatsApp-style background
chat_box = scrolledtext.ScrolledText(chat_frame, state=tk.DISABLED, bg="#0B141A", fg="#FFFFFF", font=message_font, wrap=tk.WORD)
chat_box.pack(fill=tk.BOTH, expand=True)

# Configure tags for WhatsApp-style message bubbles
chat_box.tag_configure("bubble_self", background="#005C4B", foreground="#FFFFFF", 
                       lmargin1=100, lmargin2=100, rmargin=20, spacing1=6, spacing3=6, justify="right")
chat_box.tag_configure("timestamp_in_bubble_self", background="#005C4B", foreground="#AEBAC1", 
                        font=timestamp_font, justify="right")
chat_box.tag_configure("bubble_other", background="#222E35", foreground="#FFFFFF", 
                       lmargin1=20, lmargin2=20, rmargin=100, spacing1=6, spacing3=6, justify="left")
chat_box.tag_configure("timestamp_in_bubble", background="#222E35", foreground="#AEBAC1", 
                        font=timestamp_font, justify="left")
chat_box.tag_configure("bubble_spacer", background="#0B141A", spacing1=4)
chat_box.tag_configure("system", justify="center", foreground="#8C9DA9", font=("Segoe UI", 11, "italic"))
chat_box.tag_configure("sender_name", foreground="#53BDEB", font=name_font, justify="left")

# Message input frame - WhatsApp style
message_frame = tk.Frame(chat_panel, bg="#1F2C33")
message_frame.pack(fill=tk.X, padx=0, pady=0)

# Message entry
message_entry = tk.Entry(message_frame, width=40, font=("Segoe UI", 14), borderwidth=0, relief="flat", bg="#2A3942", fg="#FFFFFF")
message_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
message_frame.columnconfigure(0, weight=1)

# Send button
send_button = tk.Button(message_frame, text="Send", font=("Segoe UI", 13), bg="#00A884", fg="#FFFFFF", 
                        command=send_message, relief="flat", borderwidth=0)
send_button.grid(row=0, column=1, padx=10, pady=10)

# Bind Enter key to send
message_entry.bind('<Return>', lambda event: send_message())

# Users section setup
users_header = tk.Label(users_panel, text="Active Users", font=("Segoe UI", 16, "bold"), bg="#111B21", fg="#FFFFFF", pady=10)
users_header.pack(fill=tk.X)

# Treeview for users list with custom style - WhatsApp look
style = ttk.Style()
style.configure("Users.Treeview", font=('Segoe UI', 14), rowheight=35, background="#111B21", foreground="#FFFFFF", fieldbackground="#111B21")
style.configure("Users.Treeview.Heading", font=('Segoe UI', 14, 'bold'), background="#111B21", foreground="#FFFFFF")
style.map('Users.Treeview', background=[('selected', '#00A884')])

users_listbox = ttk.Treeview(users_panel, style="Users.Treeview", columns=("username",), show="headings", height=20)
users_listbox.heading("username", text="Username")
users_listbox.column("username", width=200, anchor="center")
users_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Instructions/Help section
help_frame = tk.LabelFrame(users_panel, text="Instructions", font=("Segoe UI", 14, "bold"), bg="#111B21", fg="#FFFFFF", padx=10, pady=10)
help_frame.pack(fill=tk.X, padx=10, pady=10)

help_text = """• Type your message and press Enter or click Send
• Type GET_USERS to refresh user list
• Application will close if server shuts down
• Messages show timestamps (HH:MM)"""

help_label = tk.Label(help_frame, text=help_text, justify="left", bg="#111B21", fg="#8C9DA9", font=("Segoe UI", 12))
help_label.pack(anchor="w")

# Add exit button
exit_button = tk.Button(users_panel, text="Exit Chat", font=("Segoe UI", 14), bg="#F15C6D", fg="#FFFFFF", 
                       command=root.destroy, pady=5)
exit_button.pack(pady=20, padx=10, fill=tk.X)

# Show a welcome message
chat_box.config(state=tk.NORMAL)
chat_box.insert(tk.END, "\nWelcome to the chat! Connected to server.\n", "system")
chat_box.config(state=tk.DISABLED)

# Start receiving thread
threading.Thread(target=receive_messages, daemon=True).start()

# Set focus to entry
message_entry.focus_set()

# Request user list on startup
root.after(1000, lambda: client.send("GET_USERS".encode('utf-8')))

# Start main loop
root.mainloop()