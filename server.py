import socket
from _thread import *
import _pickle as pickle
import time
import math
import random

# Setup sockets
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Set constants
server = '192.168.100.2'
port = 5555
MAX_PLAYERS = 30

# Dynamic Variables
players = {}
coins = []
connections = 0
id = 0
game = 0
game_time = 0
area_radius = 550
coinSpawnTime = 10

# Try connect to server
try:
    s.bind((server, port))
except Exception as e:
    print("[EXCEPTION] ", e)

s.listen(MAX_PLAYERS)
print("[SERVER] Server started, waiting for connections...")

def client_communication(conn, id):
    global players, connections, game, game_time, coins
    current_id = id
    data = conn.recv(20)
    name = data.decode("utf-8")
    print("[SERVER]", name, "connected to the server.")
    conn.send(str.encode(str(current_id)))
    x = random.randrange(100, 800)
    y = random.randrange(100, 500)
    players[current_id] = {"x": x, "y": y, "name": name, "health": 10, "coins": 0, "isdead": 0}

    while True:
        data = conn.recv(1024)
        if not data:
            connections -= 1
            del players[current_id]
            print(f"[DISCONNECT] {addr} has been disconnected.")

        data = data.decode("utf-8")
        if data.split(" ")[0] == "get":
            send_data = pickle.dumps((players, game, game_time, area_radius, coins))
        elif data.split(" ")[0] == "move":
            split_data = data.split(" ")
            x = int(split_data[1])
            y = int(split_data[2])
            players[current_id]["x"] = x
            players[current_id]["y"] = y

            send_data = pickle.dumps((players, game, game_time, area_radius, coins))
        elif data.split(" ")[0] == "health":
            split_data = data.split(" ")
            health = int(split_data[1])
            if health <= 0:
                players[current_id]["isdead"] = 1
                if AliveCount(players) <= 1 and game == 2:
                    game = 3
                    game_time = 5

            players[current_id]["health"] = health
            send_data = pickle.dumps((players, game, game_time, area_radius, coins))
        elif data.split(" ")[0] == "collide":
            split_data = data.split(" ")
            coin_id = int(split_data[1])
            del coins[coin_id]
            players[current_id]["coins"] += 10
            send_data = pickle.dumps((players, game, game_time, area_radius, coins))
        elif data.split(" ")[0] == "buy":
            split_data = data.split(" ")
            coin_count = int(split_data[1])
            health = int(split_data[2])
            players[current_id]["coins"] = coin_count
            players[current_id]["health"] = health
            send_data = pickle.dumps((players, game, game_time, area_radius, coins))

        conn.send(send_data)
        time.sleep(0.001)

def AliveCount(players):
    count = 0
    for player in players:
        if players[player]["isdead"] == 0:
            count += 1
    return count

def RestartGame():
    global game, game_time, players, coins, area_radius, coinSpawnTime
    game = 1
    game_time = 20
    coins = []
    area_radius = 550
    coinSpawnTime = 10
    for player in players:
        x = random.randrange(100, 800)
        y = random.randrange(100, 500)
        players[player]["x"] = x
        players[player]["y"] = y
        players[player]["health"] = 10
        players[player]["coins"] = 0
        players[player]["isdead"] = 0
def game_counter():
    global game, game_time, connections, area_radius, coinSpawnTime, coins, players
    while True:
        time.sleep(1)
        if game == 1 and game_time > 0:
            if connections <= 1:
                game = 0
                game_time = 0
                break
            game_time -= 1
            if game_time <= 0:
                area_radius = 550
                game = 2

        elif game == 2:
            if connections <= 1:
                RestartGame()
                game = 0
                game_time = 0
            area_radius -= 3
            coinSpawnTime -= 1
            if coinSpawnTime <= 0:
                x = random.randrange(100, 800)
                y = random.randrange(100, 500)
                coinSpawnTime = 10
                coins.append([x, y])
        elif game == 3:
            game_time -= 1
            if game_time <= 0:
                if connections > 1:
                    RestartGame()
                else:
                    game = 0



while True:
    conn, addr = s.accept() # Accept new connections
    print("[SERVER] Connected to: ", addr)
    connections += 1
    if connections > 1 and game == 0:
        game = 1
        game_time = 20
        start_new_thread(game_counter, ())

    start_new_thread(client_communication, (conn, id))
    id += 1



print("[SERVER] Server offline")


