#!/bin/env python

import os
import sys
import time
import asyncio
import datetime
import requests
from websockets.asyncio.server import serve
from websockets.asyncio.server import broadcast
from websockets.exceptions import ConnectionClosedOK
from websockets import ServerProtocol
from dataclasses import dataclass
from utils import Rectangle
from Game import Game
from Player import Player


games = [Game(),]

def get_game(opponent, name, tournament_id):
    global games
    game = None

    print(name, file=sys.stderr)
    print(opponent, file=sys.stderr)
    print(tournament_id, file=sys.stderr)

    if name != 'bot':
        # Join a game if one is available
        for g in games:
            if len(g.players) != 1:
                continue
            if opponent != "*":
                for p in g.players:
                    if p.name == opponent:
                        game = g
            else:
                if (g.opponent == "*" or g.opponent == name) and g.players[0].name != "bot":
                    game = g

    # Or create one if nobody's already registered
    if game is None:
        print("Creating a game...")
        game = Game()
        game.players = []
        game.opponent = opponent
        game.tournament_id = tournament_id
        games.append(game)

    return game

async def pong(websocket:ServerProtocol):
    token = None
    tournament_id = -1

    opponent = await websocket.recv()
    temp = await websocket.recv()

    if temp.startswith("tournament"):
        tournament_id = int(temp.split(":")[1])
    else:
        token = temp
    if token is None:
        token = await websocket.recv()

    print("Tournament is : " + str(tournament_id), file=sys.stderr)

    player = requests.get(
        "http://ft-transcendence-api-1.transcendence:" + str(os.environ.get("API_PORT")) + "/appong/api/user/me/",
        headers={
            'Authorization': 'Token ' + token,
            'Accept': 'application/json'
        }
    )
    if (player.status_code != 200):
        await websocket.send("opponent:personne")
        await websocket.send("who are you ? get out")
        return
    player = player.json()
    me = Player(connection=websocket, name=player['user']['username'], token=token, id=player['pk'])

    game = get_game(opponent, me.name, tournament_id)
    await me.register(game)

    time = datetime.datetime.now()
    while True:
        try:
            message = await me.socket.recv()
        except:
            break
        delta = datetime.datetime.now() - time
        if delta.microseconds < 50000:
            continue
        time = datetime.datetime.now()
        try:
            if message == "up" or message == "up\n":
                me.line -= 10
                if me.line < 0:
                    me.line = 0
                else:
                    await game.broadcast(me.name + ":" + str(me.line) + ":" + str(me.column))
            if message == "down" or message == "down\n":
                me.line += 10
                if me.line > 900:
                    me.line = 900
                else:
                    await game.broadcast(me.name + ":" + str(me.line) + ":" + str(me.column))
        except:
            try:
                await game.players[0].socket.send("winner:aborted")
            except:
                pass
            try:
                await game.players[1].socket.send("winner:aborted")
            except:
                pass
            break


async def main():
    if os.environ["PORT"] is None:
        print("PORT environment variable must be defined.", file=sys.stderr)
        return
    async with serve(pong, "0.0.0.0", os.environ.get("PORT")) as websocket:
        await asyncio.get_running_loop().create_future()

asyncio.run(main())
