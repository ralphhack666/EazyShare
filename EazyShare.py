# EazyShare | Secure File Transfer Tool
import tkinter as tk
from tkinter import filedialog
import socket
from cryptography.fernet import Fernet
import hashlib
import base64
import os
import struct

def derive_key(password):
    return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())

def send_file(sock, filename, password):
    key = derive_key(password)
    with open(filename, 'rb') as file:
        file_data = file.read()
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(file_data)

        filename_bytes = os.path.basename(filename).encode()
        sock.sendall(struct.pack('I', len(filename_bytes)) + filename_bytes)
        sock.sendall(encrypted_data)

def decrypt_data(key, data):
    fernet = Fernet(key)
    return fernet.decrypt(data)

def receive_file(key, port):
    host = '0.0.0.0'
    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receiver_socket.bind((host, port))
    receiver_socket.listen(1)
    print("Receiver is listening for incoming connections...")

    client_socket, client_address = receiver_socket.accept()
    print("Connection established with:", client_address)

    filename_len = struct.unpack('I', client_socket.recv(4))[0]
    filename = client_socket.recv(filename_len).decode()

    encrypted_data = b""
    while True:
        chunk = client_socket.recv(4096)
        if not chunk:
            break
        encrypted_data += chunk

    try:
        decrypted_data = decrypt_data(key, encrypted_data)
        with open(filename, 'wb') as file:
            file.write(decrypted_data)
            print(f"File received successfully: {filename}")
    except ValueError as e:
        print(f"Decryption failed: {e}")

    client_socket.close()
    receiver_socket.close()

def send_file_gui():
    password = password_entry.get()
    filename = file_path_label.cget("text")
    host = host_entry.get()
    port = int(port_entry.get())
    if password and filename and host and port:
        sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sender_socket.connect((host, port))
        send_file(sender_socket, filename, password)
        sender_socket.close()
        status_label.config(text="File sent successfully!")
    else:
        status_label.config(text="Please fill in all fields!")

def receive_file_gui():
    key = password_entry.get()
    port = int(port_entry.get())
    if key and port:
        receive_file(derive_key(key), port)
        status_label.config(text="File received successfully!")
    else:
        status_label.config(text="Please enter a valid key and port!")

def choose_file():
    filename = filedialog.askopenfilename()
    file_path_label.config(text=filename)

# UI Setup
root = tk.Tk()
root.title("EazyShare")
root.geometry('400x500')
root.configure(bg='black')

def configure_widget(widget, font=('Helvetica', 10, 'bold'), bg='black', fg='white'):
    widget.configure(bg=bg, fg=fg, font=font)
    if isinstance(widget, tk.Entry):
        widget.configure(insertbackground='white')

mode_label = tk.Label(root, text="EazyShare", font=('Helvetica', 16, 'bold'))
configure_widget(mode_label)
mode_label.pack(pady=10)

mode_var = tk.StringVar(value="send")
send_radio = tk.Radiobutton(root, text="Send", variable=mode_var, value="send", selectcolor='black')
configure_widget(send_radio)
send_radio.pack(pady=5)
receive_radio = tk.Radiobutton(root, text="Receive", variable=mode_var, value="receive", selectcolor='black')
configure_widget(receive_radio)
receive_radio.pack(pady=5)

host_label = tk.Label(root, text="Enter Host:")
configure_widget(host_label)
host_label.pack(pady=5)
host_entry = tk.Entry(root)
configure_widget(host_entry)
host_entry.pack(pady=5)

port_label = tk.Label(root, text="Enter Port:")
configure_widget(port_label)
port_label.pack(pady=5)
port_entry = tk.Entry(root)
configure_widget(port_entry)
port_entry.pack(pady=5)

password_label = tk.Label(root, text="Enter Password/Key:")
configure_widget(password_label)
password_label.pack(pady=5)
password_entry = tk.Entry(root, show="*")
configure_widget(password_entry)
password_entry.pack(pady=5)

file_path_label = tk.Label(root, text="No file chosen")
configure_widget(file_path_label)
file_path_label.pack(pady=5)

choose_file_button = tk.Button(root, text="Choose File", command=choose_file)
configure_widget(choose_file_button)
choose_file_button.pack(pady=5)

execute_button = tk.Button(root, text="Execute", command=lambda: send_file_gui() if mode_var.get() == "send" else receive_file_gui())
configure_widget(execute_button)
execute_button.pack(pady=5)

status_label = tk.Label(root, text="")
configure_widget(status_label)
status_label.pack(pady=10)

root.mainloop()