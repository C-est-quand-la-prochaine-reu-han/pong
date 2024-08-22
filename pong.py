import time
import random
import asyncio
from websockets.asyncio.server import serve
from websockets.asyncio.server import broadcast
from websockets.exceptions import ConnectionClosedOK

class Player:
    socket = None
    name = ""
    _height = 0

    def __init__(self, connection=None, name=""):
        self._height = 50
        self.name = name
        self.socket = connection

    async def up(self):
        self._height += 1
        await self.game.notify(self.name + " : up")

    async def down(self):
        self._height -= 1
        await self.game.notify(self.name + " : down")

    def register(self, game):
        print(self.name + " has joined the game")
        game.watchers.append(self)
        if len(game.watchers) == 2:
            asyncio.create_task(game.run())
        self.game = game


class Game:
    ball_pos = [500,500]
    ball_movement = [0,0]
    watchers = []

    def __init__(self):
        self.ball_movement = [random.randint(-10, 10), random.randint(-10, 10)]
        print("A new game is waiting for players")

    async def run(self):
        await self.broadcast("start")
        while True:
            self.ball_pos[0] += self.ball_movement[0]
            self.ball_pos[1] += self.ball_movement[1]
            pos = "pos:" + str(self.ball_pos[0]) + ":" + str(self.ball_pos[1])
            print(pos)
            await self.broadcast(pos)
            await asyncio.sleep(0.2)

    async def broadcast(self, message):
        for w in self.watchers:
            await w.socket.send(message)

game = Game()

async def pong(websocket):
    global game
    message = await websocket.recv()

    me = Player(connection=websocket, name=message)
    me.register(game)
    while True:
        message = await me.socket.recv()
        print(me.name + " : " + message)
        if message == "up":
            await game.broadcast(me.name + ":up")
        if message == "down":
            await game.broadcast(me.name + ":down")


async def main():
    async with serve(pong, "localhost", 8765) as websocket:
        await asyncio.get_running_loop().create_future()

asyncio.run(main())
