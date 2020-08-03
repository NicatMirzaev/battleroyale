import pygame
import os
import math
import time
from client import Client

pygame.init()
pygame.font.init()
# CONSTANTS
width = 1152
height = 700
lastHealthReductionAt = 0
map_data = [
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]
tile1 = pygame.image.load(os.path.join("imgs", "1.png"))
tile2 = pygame.image.load(os.path.join("imgs", "0.png"))
player_img = pygame.image.load(os.path.join("imgs", "player.png"))
coin_img = pygame.image.load(os.path.join("imgs", "coin.png"))
NAME_FONT = pygame.font.SysFont("Comic Sans MS", 15)
Waiting = pygame.font.SysFont("Segoe UI", 40)
Coin_Text = pygame.font.SysFont("Comic Sans MS", 25)

clock = pygame.time.Clock()
# Dynamic Variables
players = {}

def redraw_window(win, id, game, game_time, area_radius, players, coins):
    global player_coins
    k = 0
    for row_nb, row in enumerate(map_data):
        for col_nb, tile in enumerate(row):
            if tile == 1:
                image = tile1
            else:
                image = tile2

            tileX = 64 * k
            tileY = row_nb * 64
            k += 1
            if k >= width / 64:
                k = 0
            win.blit(image, (tileX, tileY))

    for player in players:
        p = players[player]
        if p["isdead"] == 0:
            win.blit(player_img, (p["x"], p["y"]))
            text = NAME_FONT.render(p["name"], 1, (0, 0, 0))
            win.blit(text, (p["x"] + 18, p["y"] - 2))

    if players[id]["isdead"] == 0:
        text = Coin_Text.render(f'Coins: {players[id]["coins"]}', 1, (255, 255, 255))
        win.blit(text, (width - 120, height - 50))
        pygame.draw.rect(win, (255, 255, 255), (players[id]["x"] + 7, players[id]["y"] + 45, 50, 10))  # NEW
        pygame.draw.rect(win, (255, 0, 0), (players[id]["x"] + 7, players[id]["y"] + 45, players[id]["health"] * 5, 10))  # NEW
    if game == 0:
        text = Waiting.render(f"Waiting for players... ({len(players)}/2)", 1, (255, 255, 255))
        win.blit(text, (350, height - 80))
    elif game == 1:
        text = Waiting.render(f"Game is starting... ({game_time}s)", 1, (255, 255, 255))
        win.blit(text, (350, height - 80))
    elif game == 2:
        if area_radius >= 2:
            pygame.draw.circle(win, (0, 0, 0), (round(width / 2), round(height / 2)), area_radius, 2)

        for coin in coins:
            win.blit(coin_img, (coin[0], coin[1]))

    elif game == 3:
        for player in players:
            if players[player]["isdead"] == 0:
                winner = players[player]["name"]

        text = Waiting.render(f"Winner is {winner}, game restarting...", 1, (255, 255, 255))
        win.blit(text, (350, height - 80))


def isSolidTile(x, y):
     tileX = round(x / 64)
     tileY = round(y / 64)
     return map_data[tileY][tileX]


def isInCircle(x, y, radius):
    newpos1 = y - round(height / 2)
    newpos2 = x - round(width / 2)

    distance = math.sqrt(newpos1**2 + newpos2**2)
    if x < round(width / 2):
        if distance - 32 <= radius:
            return True
    else:
        if distance + 32 <= radius:
            return True
    return False

def IsPlayerCollidedWithCoin(x, y, coins):
    rect1 = pygame.Rect(x, y, 32, 32)
    for i in range(len(coins)):
        rect2 = pygame.Rect(coins[i][0], coins[i][1], 32, 32)
        if rect1.colliderect(rect2):
            return i
    return -1
def main(name):
    global players, lastHealthReductionAt
    client = Client()
    player_id = int(client.connect(name))
    players, game, game_time, area_radius, coins = client.send("get")
    print("[LOG] You are connected to the server with id", player_id)
    print("[LOG] Joining the game...")

    run = True
    while run:
        clock.tick(60)
        player = players[player_id]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        if player["isdead"] == 0:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                if isSolidTile(player["x"] - 10, player["y"]) == 0:
                    player["x"] = player["x"] - 10
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                if isSolidTile(player["x"] + 10, player["y"]) == 0:
                    player["x"] = player["x"] + 10
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                if isSolidTile(player["x"], player["y"] - 10) == 0:
                    player["y"] = player["y"] - 10
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                if isSolidTile(player["x"], player["y"] + 10) == 0:
                    player["y"] = player["y"] + 10
            if keys[pygame.K_f]:
                if player["coins"] >= 20:
                    player["coins"] -= 20
                    player["health"] += 3
                    data = "buy " + str(player["coins"]) + " " + str(player["health"])
                    players, game, game_time, area_radius, coins = client.send(data)

        data = "move " + str(player["x"]) + " " + str(player["y"]) + " "
        players, game, game_time, area_radius, coins = client.send(data)
        if game == 2 and player["isdead"] == 0:
            if isInCircle(player["x"], player["y"], area_radius) == False and time.time() >= lastHealthReductionAt:
                player["health"] -= 1
                lastHealthReductionAt = time.time() + 3
                if player["health"] <= 0: player["isdead"] = 1
                data = "health " + str(player["health"])
                players, game, game_time, area_radius, coins = client.send(data)

            check = IsPlayerCollidedWithCoin(player["x"], player["y"], coins)
            if check != -1:
                data = "collide " + str(check)
                print(str(check))
                players, game, game_time, area_radius, coins = client.send(data)

        win.fill((255, 255, 255))
        redraw_window(win, player_id, game, game_time, area_radius, players, coins)
        pygame.display.update()

    client.disconnect()
    pygame.quit()
    quit()




while True:
    name = input("Please enter your nickname: ")
    if 0 < len(name) < 20:
        break
    else:
        print("[ERROR] Name must be between 1 and 20 characters")


win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Battle Royale (By Zoxy)")

main(name)

