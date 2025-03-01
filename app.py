import tkinter as tk
import socket
import threading

SERVER_IP = "127.0.0.1"
PORT = 12345

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, PORT))

# Ask for username
username = input("Enter your username: ")
client_socket.send(username.encode("utf-8"))

def send_message():
    """Send input to server"""
    message = entry.get()
    client_socket.send(message.encode("utf-8"))
    entry.delete(0, tk.END)

def receive_messages():
    """Receive and display messages"""
    while True:
        try:
            message = client_socket.recv(1024).decode("utf-8")
            if message.startswith("QUESTION:"):
                question_label.config(text=message.replace("QUESTION:", ""))
            elif message.startswith("REVEAL:"):
                reveal_label.config(text=message.replace("REVEAL:", ""))
            else:
                chat_area.insert(tk.END, message + "\n")
        except:
            break

# Tkinter UI
root = tk.Tk()
root.title("Hidden Question Game")
root.geometry("500x400")

question_label = tk.Label(root, text="Waiting for question...", font=("Arial", 14))
question_label.pack(pady=10)

reveal_label = tk.Label(root, text="", font=("Arial", 12))
reveal_label.pack(pady=5)

chat_area = tk.Text(root, height=10, state=tk.DISABLED)
chat_area.pack(pady=10)

entry = tk.Entry(root, width=40)
entry.pack(pady=5)
entry.bind("<Return>", lambda event: send_message())

send_button = tk.Button(root, text="Send", command=send_message)
send_button.pack(pady=5)

# Start receiving messages
threading.Thread(target=receive_messages, daemon=True).start()

root.mainloop()
