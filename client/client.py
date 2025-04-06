import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, font, messagebox
from tkinter import ttk
import datetime
import sys

# Client configuration
HOST=input("Enter the HOST IP:")
PORT=int(input("Enter the Port number:"))

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((HOST, PORT))
except ConnectionRefusedError:
    print("Could not connect to server. Server might be offline.")
    sys.exit()

active_users = []
username = simpledialog.askstring("Username", "Enter your username:")
client.send(username.encode('utf-8'))

dark_theme = {
    "bg": "#0B141A",
    "chat_bg": "#0B141A",
    "input_bg": "#2A3942",
    "input_fg": "#FFFFFF",
    "users_bg": "#111B21",
    "users_fg": "#FFFFFF",
    "bubble_self": "#005C4B",
    "bubble_self_fg": "#FFFFFF",
    "bubble_other": "#202C33",
    "bubble_other_fg": "#FFFFFF",
    "timestamp": "#AEBAC1",
    "system_msg": "#8C9DA9",
    "sender_name": "#53BDEB",
    "send_button": "#00A884",
    "send_button_fg": "#FFFFFF"
}

light_theme = {
    "bg": "#F0F2F5",
    "chat_bg": "#E4DDD6",
    "input_bg": "#FFFFFF",
    "input_fg": "#000000",
    "users_bg": "#FFFFFF",
    "users_fg": "#000000",
    "bubble_self": "#D9FDD3",
    "bubble_self_fg": "#000000",
    "bubble_other": "#FFFFFF",
    "bubble_other_fg": "#000000",
    "timestamp": "#667781",
    "system_msg": "#65777F",
    "sender_name": "#3E7694",
    "send_button": "#00A884",
    "send_button_fg": "#FFFFFF"
}

current_theme = dark_theme

def receive_messages():
    global active_users
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            
            
            if message == "SERVER_SHUTDOWN":
                chat_box.config(state=tk.NORMAL)
                chat_box.insert(tk.END, "\nServer has been shut down. Application will close in 5 seconds.\n", "system")
                chat_box.config(state=tk.DISABLED)
                chat_box.yview(tk.END)
                root.after(5000, root.destroy)
                break
                
            
            if message.startswith("KICKED:"):
                kicked_user = message.split(":", 1)[1]
                if kicked_user == username:
                    chat_box.config(state=tk.NORMAL)
                    chat_box.insert(tk.END, "\nYou have been kicked from the chat. Application will close in 5 seconds.\n", "system")
                    chat_box.config(state=tk.DISABLED)
                    chat_box.yview(tk.END)
                    root.after(5000, root.destroy)
                    break
                continue
            
            if message.startswith("USERLIST:"):
                update_user_list(message[9:].split(","))
                continue
                
            chat_box.config(state=tk.NORMAL)
            
            if "has joined the chat" in message or "has left the chat" in message or "has been kicked from the chat" in message:
                chat_box.insert(tk.END, f"\n{message}\n", "system")
            elif ":" in message:
                if " [" in message and "]:" in message:
                    
                    parts = message.split("]:", 1)
                    if len(parts) == 2:
                        sender_and_time, content = parts
                        sender_and_time += "]"  
                        
                        if " [" in sender_and_time:
                            sender_parts = sender_and_time.split(" [")
                            sender = sender_parts[0]
                            timestamp = sender_parts[1][:-1]  
                            
                            if sender != username:
                                chat_box.insert(tk.END, f"\n", "bubble_spacer")
                                chat_box.insert(tk.END, f"{sender}", "sender_name")
                                chat_box.insert(tk.END, f"\n{content}", "bubble_other")
                                chat_box.insert(tk.END, f" {timestamp}", "timestamp_in_bubble")
                                chat_box.insert(tk.END, f"\n", "bubble_spacer")
                else:
                    sender, content = message.split(":", 1)
                    if sender != username:
                        chat_box.insert(tk.END, f"\n", "bubble_spacer")
                        chat_box.insert(tk.END, f"{sender}", "sender_name")
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
    for item in users_listbox.get_children():
        users_listbox.delete(item)
    
    for user in users:
        if user and user != username: 
            users_listbox.insert("", "end", text=user, values=(user,))
        if user==username:
            text = f"{user} (You)"
            users_listbox.insert("", "end", text=text, values=(user,), tags=("self",))

def send_message():
    message = message_entry.get()
    message_entry.delete(0, tk.END)
    if message:
        
        current_time = datetime.datetime.now().strftime("%H:%M")
        
        chat_box.config(state=tk.NORMAL)
        
        chat_box.insert(tk.END, f"\n", "bubble_spacer")
        chat_box.insert(tk.END, f"{message}", "bubble_self")
        chat_box.insert(tk.END, f" {current_time}", "timestamp_in_bubble_self")
        chat_box.insert(tk.END, f"\n", "bubble_spacer")
        
        chat_box.config(state=tk.DISABLED)
        chat_box.yview(tk.END)
        
        client.send(message.encode('utf-8'))

def toggle_theme():
    global current_theme
    if current_theme == dark_theme:
        current_theme = light_theme
        theme_button.config(text="Dark Mode")
    else:
        current_theme = dark_theme
        theme_button.config(text="Light Mode")
    
    apply_theme()

def kick_user():
    selected_items = users_listbox.selection()
    if not selected_items:
        messagebox.showinfo("Kick User", "Please select a user to kick")
        return
    
    selected_item = selected_items[0]
    user_to_kick = users_listbox.item(selected_item)['values'][0]
    
    if user_to_kick == username:
        messagebox.showinfo("Kick User", "You cannot kick yourself")
        return
    
    confirmation = messagebox.askyesno("Kick User", f"Are you sure you want to kick {user_to_kick}?")
    if confirmation:
        client.send(f"KICK:{user_to_kick}".encode('utf-8'))

def apply_theme():
   
    root.configure(bg=current_theme["bg"])
    
    
    chat_panel.configure(bg=current_theme["bg"])
    chat_frame.configure(bg=current_theme["chat_bg"])
    chat_box.configure(bg=current_theme["chat_bg"], fg=current_theme["bubble_other_fg"])
    
    
    message_frame.configure(bg=current_theme["users_bg"])
    message_entry.configure(bg=current_theme["input_bg"], fg=current_theme["input_fg"])
    send_button.configure(bg=current_theme["send_button"], fg=current_theme["send_button_fg"])
    
    
    users_panel.configure(bg=current_theme["users_bg"])
    users_header.configure(bg=current_theme["users_bg"], fg=current_theme["users_fg"])
    help_frame.configure(bg=current_theme["users_bg"], fg=current_theme["users_fg"])
    help_label.configure(bg=current_theme["users_bg"], fg=current_theme["system_msg"])
    
    
    theme_button.configure(bg=current_theme["send_button"], fg=current_theme["send_button_fg"])
    kick_button.configure(bg="#F15C6D", fg="#FFFFFF")
    
    
    chat_box.tag_configure("bubble_self", background=current_theme["bubble_self"], foreground=current_theme["bubble_self_fg"], 
                       lmargin1=100, lmargin2=100, rmargin=20, spacing1=10, spacing3=10, justify="right")
    chat_box.tag_configure("timestamp_in_bubble_self", foreground=current_theme["timestamp"], 
                        font=timestamp_font, justify="right")
    
    chat_box.tag_configure("bubble_other", foreground=current_theme["bubble_other_fg"], 
                       lmargin1=20, lmargin2=20, rmargin=100, spacing1=6, spacing3=6, justify="left")
    chat_box.tag_configure("timestamp_in_bubble", foreground=current_theme["timestamp"], 
                        font=timestamp_font, justify="right")
    
    chat_box.tag_configure("bubble_spacer", spacing1=4)
    chat_box.tag_configure("system", justify="center", foreground=current_theme["system_msg"], font=("Segoe UI", 11, "italic"))
    chat_box.tag_configure("sender_name", foreground=current_theme["sender_name"], font=name_font, justify="left")
    
    
    style.configure("Users.Treeview", background=current_theme["users_bg"], foreground=current_theme["users_fg"], fieldbackground=current_theme["users_bg"])
    style.configure("Users.Treeview.Heading", background=current_theme["users_bg"], foreground=current_theme["users_fg"])

root = tk.Tk()
root.title("Chat App")
root.configure(bg=current_theme["bg"])  

root.attributes('-fullscreen', True)
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

main_paned = tk.PanedWindow(root, orient=tk.HORIZONTAL, bg=current_theme["bg"], sashwidth=4)
main_paned.pack(fill=tk.BOTH, expand=True)

chat_panel = tk.Frame(main_paned, bg=current_theme["bg"])
main_paned.add(chat_panel, width=int(screen_width * 0.7))

users_panel = tk.Frame(main_paned, bg=current_theme["users_bg"])
main_paned.add(users_panel, width=int(screen_width * 0.3))


chat_frame = tk.Frame(chat_panel, bg=current_theme["chat_bg"])
chat_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)


message_font = font.Font(family="Segoe UI", size=13)
name_font = font.Font(family="Segoe UI", size=12)
timestamp_font = font.Font(family="Segoe UI", size=8)


chat_box = scrolledtext.ScrolledText(chat_frame, state=tk.DISABLED, bg=current_theme["chat_bg"], fg=current_theme["bubble_other_fg"], font=message_font, wrap=tk.WORD)
chat_box.pack(fill=tk.BOTH, expand=True)

message_frame = tk.Frame(chat_panel, bg=current_theme["users_bg"])
message_frame.pack(fill=tk.X, padx=0, pady=0)

message_entry = tk.Entry(message_frame, width=40, font=("Segoe UI", 14), borderwidth=0, relief="flat", 
                         bg=current_theme["input_bg"], fg=current_theme["input_fg"])
message_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
message_frame.columnconfigure(0, weight=1)

send_button = tk.Button(message_frame, text="Send", font=("Segoe UI", 13), 
                        bg=current_theme["send_button"], fg=current_theme["send_button_fg"], 
                        command=send_message, relief="flat", borderwidth=0)
send_button.grid(row=0, column=1, padx=10, pady=10)

message_entry.bind('<Return>', lambda event: send_message())


users_header = tk.Label(users_panel, text="Active Users", font=("Segoe UI", 16, "bold"), 
                        bg=current_theme["users_bg"], fg=current_theme["users_fg"], pady=10)
users_header.pack(fill=tk.X)

style = ttk.Style()
style.configure("Users.Treeview", font=('Segoe UI', 14), rowheight=35, 
               background=current_theme["users_bg"], foreground=current_theme["users_fg"], 
               fieldbackground=current_theme["users_bg"])
style.configure("Users.Treeview.Heading", font=('Segoe UI', 14, 'bold'), 
               background=current_theme["users_bg"], foreground=current_theme["users_fg"])
style.map('Users.Treeview', background=[('selected', current_theme["send_button"])])

users_listbox = ttk.Treeview(users_panel, style="Users.Treeview", columns=("username",), show="headings", height=5)
users_listbox.heading("username", text="Username")
users_listbox.column("username", width=200, anchor="center")
users_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


kick_button = tk.Button(users_panel, text="Kick Selected User", font=("Segoe UI", 14), 
                       bg="#F15C6D", fg="#FFFFFF", command=kick_user, pady=5)
kick_button.pack(pady=10, padx=10, fill=tk.X)


help_frame = tk.LabelFrame(users_panel, text="Instructions", font=("Segoe UI", 14, "bold"), 
                          bg=current_theme["users_bg"], fg=current_theme["users_fg"], padx=10, pady=10)
help_frame.pack(fill=tk.X, padx=10, pady=10)

help_text = """• Type your message and press Enter or click Send
• Select a user and click 'Kick' to remove them
• Application will close if server shuts down
• Messages show timestamps (HH:MM)
• Toggle between light and dark mode using the button below"""

help_label = tk.Label(help_frame, text=help_text, justify="left", 
                     bg=current_theme["users_bg"], fg=current_theme["system_msg"], font=("Segoe UI", 12))
help_label.pack(anchor="w")


theme_button = tk.Button(users_panel, text="☀️ Light Mode", font=("Segoe UI", 14),
# Theme toggle button in right panel (moved above exit button)
theme_button = tk.Button(users_panel, text="Light Mode", font=("Segoe UI", 14),
                        bg=current_theme["send_button"], fg=current_theme["send_button_fg"],
                        command=toggle_theme, pady=5)
theme_button.pack(pady=10, padx=10, fill=tk.X)

exit_button = tk.Button(users_panel, text="Exit Chat", font=("Segoe UI", 14), bg="#F15C6D", fg="#FFFFFF", 
                       command=root.destroy, pady=5)
exit_button.pack(pady=10, padx=10, fill=tk.X)

chat_box.config(state=tk.NORMAL)
chat_box.insert(tk.END, "\nWelcome to the chat! Connected to server.\n", "system")
chat_box.config(state=tk.DISABLED)


apply_theme()

threading.Thread(target=receive_messages, daemon=True).start()

message_entry.focus_set()


root.after(1000, lambda: client.send("GET_USERS".encode('utf-8')))

root.mainloop()