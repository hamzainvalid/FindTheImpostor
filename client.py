import tkinter as tk
import socketio

SERVER_URL = "http://127.0.0.1:10000"  # Replace with your server URL
sio = socketio.Client()
name = ''

# Connect to server
try:
    sio.connect(SERVER_URL, wait_timeout=5)
    print("Connected successfully!")
except Exception as e:
    print(f"Connection failed: {e}")


# Join game
def join_game():
    global name
    name = name_entry.get()
    print("name written " + name)
    sio.emit("join", {"username": name})
    root.destroy()
    start_game_ui()

@sio.on("timer")
def timer1(t):
    timer = t.get("timer")
    print(f'You have {timer} seconds to submit your input')

@sio.on("player_joined")
def player_joined(p):
    player_name = p.get("username")
    if player_name != 'Sajawal':
        question_label.config(text=f"{player_name} has joined")
    else:
        question_label.config(text=f"Unfortunately {player_name} has joined")

# Receive question
@sio.on("question")
def receive_question(q):
    question = q.get("question")
    question_label.config(text=f"Your Question: {question}")

@sio.on("reveal_question")
def reveal_question(data):
    rq = data.get("question")
    print("the question is: " + rq)


@sio.on("start_voting")
def start_voting():
    print('Write the name of the person you think is the Impostor')


# Create Game UI
def start_game_ui():
    global question_label
    game_window = tk.Tk()
    game_window.title("Game")

    question_label = tk.Label(game_window, text="Waiting for question...")
    question_label.pack()

    answer_entry = tk.Entry(game_window)
    answer_entry.pack()
    print(name)
    def submit_answer():
        sio.emit("submit_answer", {"answer": answer_entry.get(), "name": name})

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
