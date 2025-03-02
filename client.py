import tkinter as tk
import socketio

SERVER_URL = "https://findtheimpostor-3tjo.onrender.com/"  # Replace with your server URL
sio = socketio.Client()

# Connect to server
sio.connect(SERVER_URL)


# Join game
def join_game():
    name = name_entry.get()
    sio.emit("join", {"name": name})
    root.destroy()
    start_game_ui()


# Receive question
@sio.on("question")
def receive_question(q):
    question_label.config(text=f"Your Question: {q}")


# Create Game UI
def start_game_ui():
    global question_label
    game_window = tk.Tk()
    game_window.title("Game")

    question_label = tk.Label(game_window, text="Waiting for question...")
    question_label.pack()

    answer_entry = tk.Entry(game_window)
    answer_entry.pack()

    def submit_answer():
        sio.emit("submit_answer", {"answer": answer_entry.get()})

    submit_btn = tk.Button(game_window, text="Submit", command=submit_answer)
    submit_btn.pack()

    game_window.mainloop()


# Main Tkinter Window
root = tk.Tk()
root.title("Multiplayer Game")

tk.Label(root, text="Enter Name:").pack()
name_entry = tk.Entry(root)
name_entry.pack()

tk.Button(root, text="Join", command=join_game).pack()

root.mainloop()
