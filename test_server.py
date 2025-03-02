from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import random
import openai

# Server Configuration
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
clients = {}  # {username: sid}
openai.api_key = "YOUR_OPENAI_API_KEY"



def generate_question():
    prompt = "Generate a unique trivia question with four answer choices."

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["choices"][0]["message"]["content"]

def broadcast(event, data):
    """Send message to all players"""
    socketio.emit(event, data)


@socketio.on("connect")
def handle_connect():
    print("A player has connected.")


@socketio.on("disconnect")
def handle_disconnect():
    username = None
    for user, sid in clients.items():
        if sid == request.sid:
            username = user
            break
    if username:
        del clients[username]
        print(f"{username} disconnected")
        broadcast("player_left", username)


@socketio.on("join")
def handle_join(data):
    username = data.get("username")  # ✅ Extract 'username' from the dictionary
    if not username:
        return  # Ignore if username is missing
    clients[username] = request.sid  # ✅ Now it's a valid key
    print(f"{username} joined the game.")
    broadcast("player_joined", username)


questions = generate_question()

def start_game():
    """Start the game loop"""


    print("Starting game...")

    question = random.choice(questions)


    for username, sid in clients.items():
        q_to_send = question
        socketio.emit("question", {"question": q_to_send}, room=sid)

    socketio.sleep(10)  # Wait for answers

    # Reveal question and start voting
    broadcast("reveal_question", {"question": question})
    broadcast("start_voting", "Vote who had the fake question!")

    votes = {}
    for _ in range(len(clients)):
        vote = socketio.wait_event("vote")
        votes[vote] = votes.get(vote, 0) + 1

    voted_out = max(votes, key=votes.get)
    broadcast("player_voted_out", voted_out)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)
