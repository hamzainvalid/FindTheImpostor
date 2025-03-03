import tkinter as tk
from tkinter import messagebox
import socketio
import threading

SERVER_URL = "https://findtheimpostor.onrender.com"  # Replace with your server URL
sio = socketio.Client()
name = ''
player_names = []
question = ''

# These variables will hold references to UI elements
question_label = None
player_label = None
empty_label = None
game_window = None


# Function to safely update tkinter UI from other threads
def update_ui(widget, property_name, value):
    if widget is not None:
        try:
            widget.config(**{property_name: value})
        except tk.TclError as e:
            print(f"UI update error: {e}")


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
    if not name:
        messagebox.showerror("Error", "Please enter a name")
        return

    print("name written " + name)
    sio.emit("join", {"username": name})
    root.destroy()
    start_game_ui()


@sio.on("timer")
def timer1(t):
    timer = t.get("timer")
    print(f'You have {timer} seconds to submit your input')
    # Also update UI if available
    if empty_label:
        update_ui(empty_label, "text", f"Time remaining: {timer} seconds")


@sio.on("player_joined")
def player_joined(p):
    global player_label
    player_name = p.get("username")
    if player_name not in player_names:  # Avoid duplicates
        player_names.append(player_name)

    # Update the player label with the current list of players
    if player_label:
        player_list_text = "Players: " + ", ".join(player_names)
        update_ui(player_label, "text", player_list_text)


# Receive question
@sio.on("question")
def receive_question(q):
    global question, question_label
    question = q.get("question")
    if question_label:
        update_ui(question_label, "text", "Your Question: " + question)


@sio.on("reveal_question")
def reveal_question(data):
    global empty_label
    rq = data.get("question")
    if empty_label:
        update_ui(empty_label, "text", "The question is: " + rq)


@sio.on("start_voting")
def start_voting():
    print('Write the name of the person you think is the Impostor')
    if empty_label:
        update_ui(empty_label, "text", "Write the name of the person you think is the Impostor")


# Create Game UI
def start_game_ui():
    global empty_label, question_label, player_label, game_window

    game_window = tk.Tk()
    game_window.title("Find The Impostor")
    game_window.geometry("500x400")

    # Create a frame with some padding
    frame = tk.Frame(game_window, padx=20, pady=20)
    frame.pack(fill=tk.BOTH, expand=True)

    # Question section
    question_label = tk.Label(frame, text="Waiting for question...", font=("Arial", 12, "bold"), wraplength=460)
    question_label.pack(pady=10)

    # Answer section
    answer_frame = tk.Frame(frame)
    answer_frame.pack(pady=10)

    tk.Label(answer_frame, text="Your Answer:").pack(side=tk.LEFT)
    answer_entry = tk.Entry(answer_frame, width=30)
    answer_entry.pack(side=tk.LEFT, padx=5)

    def submit_answer():
        answer = answer_entry.get()
        if not answer:
            messagebox.showerror("Error", "Please enter an answer")
            return

        sio.emit("submit_answer", {"answer": answer, "name": name})
        answer_entry.delete(0, tk.END)
        update_ui(empty_label, "text", "Answer submitted, waiting for others...")

    submit_btn = tk.Button(answer_frame, text="Submit", command=submit_answer)
    submit_btn.pack(side=tk.LEFT, padx=5)

    # Status section
    empty_label = tk.Label(frame, text="", font=("Arial", 10, "italic"), wraplength=460)
    empty_label.pack(pady=10)

    # Player list section
    player_list_text = "Players: " + ", ".join(player_names)
    player_label = tk.Label(frame, text=player_list_text, font=("Arial", 10))
    player_label.pack(pady=10)

    # Start a thread to check for updates
    def update_loop():
        while True:
            try:
                # Check if the UI should be updated with the current question
                if question and question_label:
                    game_window.after(100, lambda: update_ui(question_label, "text", "Your Question: " + question))

                # Update player list
                if player_names and player_label:
                    player_list_text = "Players: " + ", ".join(player_names)
                    game_window.after(100, lambda: update_ui(player_label, "text", player_list_text))

                # Sleep to avoid hogging CPU
                game_window.update()
                import time
                time.sleep(0.1)

            except tk.TclError:
                # Window was closed
                break
            except Exception as e:
                print(f"Error in update loop: {e}")
                break

    # Start the update thread
    threading.Thread(target=update_loop, daemon=True).start()

    game_window.mainloop()


# Main Tkinter Window
root = tk.Tk()
root.title("Find The Impostor - Login")
root.geometry("300x150")

frame = tk.Frame(root, padx=20, pady=20)
frame.pack(fill=tk.BOTH, expand=True)

tk.Label(frame, text="Enter Your Name:").pack(pady=5)
name_entry = tk.Entry(frame, width=25)
name_entry.pack(pady=5)

tk.Button(frame, text="Join Game", command=join_game).pack(pady=10)

root.mainloop()