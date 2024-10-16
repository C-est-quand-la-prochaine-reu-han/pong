#!/bin/env python

import os
import sys
import time
import asyncio
import datetime
from websockets.asyncio.server import serve
from websockets.asyncio.server import broadcast
from websockets.exceptions import ConnectionClosedOK
from websockets import ServerProtocol
from dataclasses import dataclass
from utils import Rectangle
from Game import Game
from Player import Player


games = [Game(),]

def get_game(opponent, name):
    global games
    game = None

    for g in games:
        if len(g.players) == 2:
            continue
        if opponent != "*":
            for p in g.players:
                if p.name == opponent:
                    game = g
        else:
            if g.opponent == "*" or g.opponent == name:
                game = g

    # Or create one if nobody's already registered
    if game is None:
        print("Creating a game...")
        game = Game()
        game.players = []
        game.opponent = opponent
        games.append(game)

    return game

async def pong(websocket:ServerProtocol):
    opponent = await websocket.recv()
    token = await websocket.recv()

    # TODO Query user matching token to know who's playing
    me = Player(connection=websocket, name=token)

    game = get_game(opponent, me.name)
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


async def main():
    if os.environ["PORT"] is None:
        print("PORT environment variable must be defined.", file=sys.stderr)
        return
    async with serve(pong, "0.0.0.0", os.environ.get("PORT")) as websocket:
        await asyncio.get_running_loop().create_future()

asyncio.run(main())
