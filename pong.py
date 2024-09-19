#!/bin/env python

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


game = Game()

async def pong(websocket:ServerProtocol):
    global game
    token = await websocket.recv()

    # TODO Query user matching token to know who's playing
    me = Player(connection=websocket, name=token)
    await me.register(game)
    time = datetime.datetime.now()
    while True:
        message = await me.socket.recv()
        delta = datetime.datetime.now() - time
        if delta.microseconds < 100000:
            continue
        time = datetime.datetime.now()
        if message == "up" or message == "up\n":
            me.line -= 10
            if me.line < 0:
                me.line = 0
            else:
                await game.broadcast(me.name + ":" + str(me.column) + ":" + str(me.line))
        if message == "down" or message == "down\n":
            me.line += 10
            if me.line > 900:
                me.line = 900
            else:
                await game.broadcast(me.name + ":" + str(me.column) + ":" + str(me.line))


async def main():
    async with serve(pong, "0.0.0.0", 8765) as websocket:
        await asyncio.get_running_loop().create_future()

asyncio.run(main())
