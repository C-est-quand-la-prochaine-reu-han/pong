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

    @property
    def height(self):
        return self._height

    async def up(self):
        self._height += 1
        await self.game.notify(self.name + " : up")

    async def down(self):
        self._height -= 1
        await self.game.notify(self.name + " : down")

    def register(self, game):
        print(self.name + " has joined the game")
        game.watchers.append(self)
        self.game = game


class Game:
    ball_pos = [50,50]
    ball_movement = [0,0]
    _status = "WAITING"
    watchers = []
    player_count = 0

    def __init__(self):
        self.ball_movement = [random.randint(-10, 10), random.randint(-10, 10)]
        print("A new game is waiting for players")

    async def notify(self, message):
        broadcast(map(lambda x: x.socket, self.watchers), message)

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
            broadcast(map(lambda x: x.socket, game.watchers), me.name + ":up")
        if message == "down":
            broadcast(map(lambda x: x.socket, game.watchers), me.name + ":down")


async def main():
    async with serve(pong, "localhost", 8765):
        await asyncio.get_running_loop().create_future()

asyncio.run(main())

