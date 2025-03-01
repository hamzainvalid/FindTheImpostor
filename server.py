import socket
import threading
import json
import random

# Server Configuration
HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 12345
clients = {}  # {username: socket}
questions = [
    "What is the capital of France?",
    "What is 2 + 2?",
    "Who wrote 'To Kill a Mockingbird'?",
    "What is the largest planet in the Solar System?"
]


def broadcast(message):
    """Send message to all players"""
    for client in clients.values():
        client.send(message.encode('utf-8'))


def handle_client(client_socket, username):
    """Handle communication with a player"""
    try:
        while True:
            data = client_socket.recv(1024).decode("utf-8")
            if data:
                broadcast(f"{username}: {data}")  # Share message with all players
    except:
        print(f"{username} disconnected")
        del clients[username]
        client_socket.close()


def start_game():
    """Start the game loop"""
    while True:
        if len(clients) >= 3:  # Minimum players to start
            print("Starting game...")

            # Select one random player to get a different question
            odd_player = random.choice(list(clients.keys()))
            question = random.choice(questions)
            fake_question = "What is the speed of light?"  # Random fake question

            # Send the same question to all except the odd one
            for username, client in clients.items():
                q_to_send = fake_question if username == odd_player else question
                client.send(f"QUESTION:{q_to_send}".encode('utf-8'))

            # Wait for answers
            answers = {}
            for username, client in clients.items():
                data = client.recv(1024).decode("utf-8")
                answers[username] = data

            # Reveal the common question
            broadcast(f"REVEAL: The common question was: {question}")

            # Voting phase
            broadcast("VOTE: Who had the fake question? Type the username to vote.")
            votes = {}
            for username, client in clients.items():
                vote = client.recv(1024).decode("utf-8")
                votes[vote] = votes.get(vote, 0) + 1

            # Determine who gets voted out
            voted_out = max(votes, key=votes.get)
            broadcast(f"{voted_out} has been voted out!")

        else:
            print("Waiting for more players...")


def accept_connections():
    """Accept new players"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print("Server is running... Waiting for players.")

    while True:
        client_socket, addr = server_socket.accept()
        username = client_socket.recv(1024).decode("utf-8")
        clients[username] = client_socket
        print(f"{username} joined the game.")
        threading.Thread(target=handle_client, args=(client_socket, username), daemon=True).start()


# Start server
threading.Thread(target=start_game, daemon=True).start()
accept_connections()
