import tkinter as tk
from tkinter import messagebox, scrolledtext
import socketio
import threading
import time

SERVER_URL = "https://findtheimpostor.onrender.com"  # Replace with your server URL
sio = socketio.Client()
name = ''
player_names = []
question = ''
game_started = False
is_first_player = False
discussion_active = False
voting_active = False
answers_revealed = {}
impostor_name = ""
timer_value = 0

# These variables will hold references to UI elements
question_label = None
player_label = None
status_label = None
timer_label = None
game_window = None
answer_entry = None
vote_entry = None
answers_display = None
start_button = None


# Function to safely update tkinter UI from other threads
def update_ui(widget, property_name, value):
    if widget is not None and game_window is not None:
        try:
            game_window.after(0, lambda: widget.config(**{property_name: value}))
        except Exception as e:
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


# Start the game (only first player can do this)
def start_game_request():
    sio.emit("start_game")
    update_ui(start_button, "state", tk.DISABLED)
    update_ui(status_label, "text", "Starting game...")


@sio.on("is_first_player")
def set_first_player(data):
    global is_first_player
    is_first_player = data.get("is_first", False)
    if is_first_player and start_button:
        update_ui(start_button, "state", tk.NORMAL)
        update_ui(status_label, "text", "You are the host. Click Start when everyone has joined.")


@sio.on("game_started")
def handle_game_started():
    global game_started
    game_started = True
    if start_button:
        update_ui(start_button, "state", tk.DISABLED)
    update_ui(status_label, "text", "Game has started! Waiting for question...")


@sio.on("timer")
def timer_update(t):
    global timer_value
    timer_value = t.get("timer")
    phase = t.get("phase", "answer")

    if timer_label:
        if phase == "answer":
            update_ui(timer_label, "text", f"Time to answer: {timer_value} seconds")
        elif phase == "discussion":
            update_ui(timer_label, "text", f"Discussion time: {timer_value} seconds")
        elif phase == "voting":
            update_ui(timer_label, "text", f"Time to vote: {timer_value} seconds")

    # Enable/disable appropriate inputs based on phase
    if phase == "answer" and answer_entry:
        update_ui(answer_entry, "state", tk.NORMAL)
        if vote_entry:
            update_ui(vote_entry, "state", tk.DISABLED)
    elif phase == "voting" and vote_entry:
        update_ui(vote_entry, "state", tk.NORMAL)
        if answer_entry:
            update_ui(answer_entry, "state", tk.DISABLED)


@sio.on("player_joined")
def player_joined(p):
    player_name = p.get("username")
    if player_name not in player_names:  # Avoid duplicates
        player_names.append(player_name)

    # Update the player label with the current list of players
    if player_label:
        player_list_text = "Players: " + ", ".join(player_names)
        update_ui(player_label, "text", player_list_text)


@sio.on("player_left")
def player_left(username):
    if username in player_names:
        player_names.remove(username)

    # Update the player label
    if player_label:
        player_list_text = "Players: " + ", ".join(player_names)
        update_ui(player_label, "text", player_list_text)


# Receive question
@sio.on("question")
def receive_question(q):
    global question
    question = q.get("question")
    if question_label:
        update_ui(question_label, "text", "Your Question: " + question)
    update_ui(status_label, "text", "Answer the question above!")


@sio.on("reveal_answers")
def reveal_answers(data):
    global answers_revealed
    answers_revealed = data.get("answers", {})
    correct_question = data.get("question", "")

    if answers_display:
        text = f"The question was: {correct_question}\n\nAnswers:\n"
        for player, answer in answers_revealed.items():
            text += f"{player}: {answer}\n"
        answers_display.delete(1.0, tk.END)
        answers_display.insert(tk.END, text)

    update_ui(status_label, "text", "Discuss who you think is the impostor!")


@sio.on("start_discussion")
def start_discussion():
    global discussion_active
    discussion_active = True
    update_ui(status_label, "text", "Discussion time! Who do you think is the impostor?")


@sio.on("start_voting")
def start_voting():
    global voting_active, discussion_active
    voting_active = True
    discussion_active = False
    update_ui(status_label, "text", "Vote for who you think is the impostor!")
    if vote_entry:
        update_ui(vote_entry, "state", tk.NORMAL)


@sio.on("reveal_impostor")
def reveal_impostor(data):
    global impostor_name
    impostor_name = data.get("impostor", "")
    votes = data.get("votes", {})

    result_text = f"The impostor was: {impostor_name}!\n\nVotes:\n"
    for voter, vote in votes.items():
        result_text += f"{voter} voted for {vote}\n"

    if answers_display:
        answers_display.delete(1.0, tk.END)
        answers_display.insert(tk.END, result_text)

    update_ui(status_label, "text", f"Game over! {impostor_name} was the impostor.")


# Create Game UI
def start_game_ui():
    global status_label, question_label, player_label, game_window, timer_label
    global answer_entry, vote_entry, answers_display, start_button

    game_window = tk.Tk()
    game_window.title("Find The Impostor")
    game_window.geometry("600x600")

    # Create a frame with some padding
    frame = tk.Frame(game_window, padx=20, pady=20)
    frame.pack(fill=tk.BOTH, expand=True)

    # Game controls (only for first player)
    control_frame = tk.Frame(frame)
    control_frame.pack(fill=tk.X, pady=5)

    start_button = tk.Button(control_frame, text="Start Game", command=start_game_request, state=tk.DISABLED)
    start_button.pack(side=tk.LEFT, padx=5)

    timer_label = tk.Label(control_frame, text="Waiting to start...", font=("Arial", 10, "bold"))
    timer_label.pack(side=tk.RIGHT, padx=5)

    # Status section
    status_label = tk.Label(frame, text="Waiting for players to join...", font=("Arial", 10, "italic"), wraplength=560)
    status_label.pack(pady=5, fill=tk.X)

    # Question section
    question_label = tk.Label(frame, text="Waiting for question...", font=("Arial", 12, "bold"), wraplength=560)
    question_label.pack(pady=10, fill=tk.X)

    # Answer section
    answer_frame = tk.Frame(frame)
    answer_frame.pack(pady=10, fill=tk.X)

    tk.Label(answer_frame, text="Your Answer:").pack(side=tk.LEFT)
    answer_entry = tk.Entry(answer_frame, width=40, state=tk.DISABLED)
    answer_entry.pack(side=tk.LEFT, padx=5)

    def submit_answer():
        answer = answer_entry.get()
        if not answer:
            messagebox.showerror("Error", "Please enter an answer")
            return

        sio.emit("submit_answer", {"answer": answer, "name": name})
        answer_entry.delete(0, tk.END)
        answer_entry.config(state=tk.DISABLED)
        update_ui(status_label, "text", "Answer submitted, waiting for others...")

    submit_btn = tk.Button(answer_frame, text="Submit", command=submit_answer)
    submit_btn.pack(side=tk.LEFT, padx=5)

    # Voting section
    vote_frame = tk.Frame(frame)
    vote_frame.pack(pady=10, fill=tk.X)

    tk.Label(vote_frame, text="Vote Impostor:").pack(side=tk.LEFT)
    vote_entry = tk.Entry(vote_frame, width=40, state=tk.DISABLED)
    vote_entry.pack(side=tk.LEFT, padx=5)

    def submit_vote():
        vote = vote_entry.get()
        if not vote:
            messagebox.showerror("Error", "Please enter a name to vote")
            return

        sio.emit("submit_vote", {"vote": vote, "voter": name})
        vote_entry.delete(0, tk.END)
        vote_entry.config(state=tk.DISABLED)
        update_ui(status_label, "text", "Vote submitted, waiting for results...")

    vote_btn = tk.Button(vote_frame, text="Vote", command=submit_vote)
    vote_btn.pack(side=tk.LEFT, padx=5)

    # Answers display area
    tk.Label(frame, text="Game Information:", font=("Arial", 11, "bold")).pack(anchor=tk.W, pady=(10, 5))
    answers_display = scrolledtext.ScrolledText(frame, height=10, width=70, wrap=tk.WORD)
    answers_display.pack(fill=tk.BOTH, expand=True, pady=5)
    answers_display.insert(tk.END, "Game information will appear here...")
    answers_display.config(state=tk.DISABLED)  # Start as read-only

    # Player list section
    player_list_text = "Players: " + ", ".join(player_names)
    player_label = tk.Label(frame, text=player_list_text, font=("Arial", 10))
    player_label.pack(pady=10, fill=tk.X)

    # Check if we're the first player
    sio.emit("check_first_player", {"name": name})

    # Start the update loop for UI
    def update_loop():
        while True:
            try:
                if answers_display:
                    game_window.after(0, lambda: answers_display.config(state=tk.NORMAL))
                    game_window.after(100, lambda: answers_display.config(state=tk.DISABLED))

                # Sleep to avoid hogging CPU
                time.sleep(0.1)

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