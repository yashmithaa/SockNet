import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog

# Client configuration
HOST = '127.0.0.1'
PORT = 12345

# Client socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

username = simpledialog.askstring("Username", "Enter your username:")
client.send(username.encode('utf-8'))

def receive_messages():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            chat_box.config(state=tk.NORMAL)
            
            if ":" not in message or "has joined the chat" in message or "has left the chat" in message:
                chat_box.insert(tk.END, f"\n{message}\n", "system")
            else:
                chat_box.insert(tk.END, f"\n{message}\n", "receiver")
                
            chat_box.config(state=tk.DISABLED)
            chat_box.yview(tk.END)
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

def send_message():
    message = message_entry.get()
    message_entry.delete(0, tk.END)
    if message:
        
        chat_box.config(state=tk.NORMAL)
        chat_box.insert(tk.END, f"\nYou: {message}\n", "sender")
        chat_box.config(state=tk.DISABLED)
        chat_box.yview(tk.END)
        
        client.send(message.encode('utf-8'))

root = tk.Tk()
root.title("Chat Room")
root.geometry("400x500")
root.configure(bg="#ECE5DD")

chat_frame = tk.Frame(root, bg="#ECE5DD")
chat_frame.pack(pady=10, fill=tk.BOTH, expand=True)

chat_box = scrolledtext.ScrolledText(chat_frame, state=tk.DISABLED, width=50, height=20, bg="#FFFFFF", fg="#000000")
chat_box.pack(fill=tk.BOTH, expand=True)

chat_box.tag_configure("sender", justify="right", background="#DCF8C6")
chat_box.tag_configure("receiver", justify="left", background="#FFFFFF")
chat_box.tag_configure("system", justify="center", foreground="#888888", font=("Arial", 10, "italic"))

message_frame = tk.Frame(root, bg="#ECE5DD")
message_frame.pack(fill=tk.X)

message_entry = tk.Entry(message_frame, width=40, font=("Arial", 12))
message_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
message_frame.columnconfigure(0, weight=1)

send_button = tk.Button(message_frame, text="Send", font=("Arial", 12), bg="#25D366", fg="#FFFFFF", command=send_message)
send_button.grid(row=0, column=1, padx=10, pady=10)

message_entry.bind('<Return>', lambda event: send_message())

threading.Thread(target=receive_messages, daemon=True).start()

message_entry.focus_set()

root.mainloop()