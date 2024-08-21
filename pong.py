import time
import random
import asyncio
from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosedOK

class Player:
    socket = None
    name = ""
    _height = 0
    listeners = set()

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
        game.players.append(self)
        self.game = game


class Game:
    players = []
    ball_pos = [50,50]
    ball_movement = [0,0]
    _status = "WAITING"

    def __init__(self):
        self.ball_movement = [random.randint(-10, 10), random.randint(-10, 10)]
        print("A new game is waiting for players")

    async def notify(self, message):
        for p in self.players:
            await p.socket.send(message)

    async def run(self):
        while True:
            time.sleep(0.2)
            self.ball_pos[0] += self.ball_movement[0]
            self.ball_pos[1] += self.ball_movement[1]
            encoded_position = "pos:" + str(self.ball_pos[0]) + ":" + str(self.ball_pos[1])
            self.notify(encoded_position)

game = Game()

async def pong(websocket):
    global game
    message = await websocket.recv()

    me = Player(connection=websocket, name=message)
    me.register(game)
    if (len(game.players) == 2):
        asyncio.create_task(game.run())
        game = Game()

    try:
        while True:
            message = await me.socket.recv()
            if message == "up":
                await me.up()
            if message == "down":
                await me.down()
    except Exception as e:
        print(e)
        for p in game.players:
            p.socket.send("error")
        game.players.clear()

async def main():
    async with serve(pong, "localhost", 8765):
        await asyncio.get_running_loop().create_future()

asyncio.run(main())

