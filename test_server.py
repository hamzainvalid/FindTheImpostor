from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import random

# Server Configuration
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
print("Server is running... Waiting for connections")
clients = {}  # {username: sid}
questions = [
    "Who's most likely to forget someone's birthday?",
    "Who's most likely to win a Nobel Prize?",
    "Who's most likely to become famous?",
    "Who's most likely to survive a zombie apocalypse?",
    "Who's most likely to go on a solo trip around the world?",
    "Who's most likely to cry while watching a movie?",
    "Who's most likely to start a successful business?",
    "Who's most likely to spend all their money on something stupid?",
    "Who's most likely to adopt a stray animal?",
    "Who's most likely to get lost in their own city?",
    "Who's most likely to laugh at the wrong moment?",
    "Who's most likely to go skydiving?",
    "Who's most likely to binge-watch an entire series in one night?",
    "Who's most likely to stay up all night talking?",
    "Who's most likely to move to another country?",
    "Who's most likely to write a bestselling book?",
    "Who's most likely to be late to their own wedding?",
    "Who's most likely to sleep through their alarm?",
    "Who's most likely to win a cooking competition?",
    "Who's most likely to become a politician?",
    "Who's most likely to live in a tiny house?",
    "Who's most likely to become a social media influencer?",
    "Who's most likely to accidentally text the wrong person?",
    "Who's most likely to always have snacks with them?",
    "Who's most likely to become a stand-up comedian?",
    "Who's most likely to fall asleep in class or at work?",
    "Who's most likely to trip over nothing?",
    "Who's most likely to talk their way out of trouble?",
    "Who's most likely to go viral on the internet?",
    "Who's most likely to spend the most money on shopping?",
    "Who's most likely to forget where they parked their car?",
    "Who's most likely to adopt an unusual pet?",
    "Who's most likely to be the first one on the dance floor?",
    "Who's most likely to break their phone screen?",
    "Who's most likely to get a weird tattoo?",
    "Who's most likely to win a reality TV show?",
    "Who's most likely to stay calm in a crisis?",
    "Who's most likely to make a dramatic exit?",
    "Who's most likely to prank their friends?",
    "Who's most likely to take the longest to get ready?",
    "Who's most likely to own the most pets?",
    "Who's most likely to become a millionaire?",
    "Who's most likely to forget to respond to messages?",
    "Who's most likely to befriend a stranger?",
    "Who's most likely to laugh until they cry?",
    "Who's most likely to fall in love at first sight?",
    "Who's most likely to start a trend?",
    "Who's most likely to go to space?",
    "Who's most likely to win an eating contest?",
    "Who's most likely to say something embarrassing in public?"
]



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
    print(f"{username} joined the game.")
    if not username:
        print('username not found')
        return  # Ignore if username is missing
    clients[username] = request.sid  # ✅ Now it's a valid key
    print(f"{username} joined the game.")
    broadcast("player_joined", username)



def start_game():
    """Start the game loop"""
    '''if len(clients) < 3:
        return'''

    print("Starting game...")
    odd_player = random.choice(list(clients.keys()))
    question = random.choice(questions)
    fake_question = random.choice(questions)
    while fake_question == question:
        fake_question = random.choice(questions)

    for username, sid in clients.items():
        q_to_send = fake_question if username == odd_player else question
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
