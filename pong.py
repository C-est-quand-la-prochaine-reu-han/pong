import time
import random
import asyncio
from websockets.asyncio.server import serve
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

    def is_ready(self):
        if self.socket is None: return False
        if self.name == "":
            return False
        return True

    def up(self):
        self._height += 1

    def down(self):
        self._height -= 1


class Game:
    players = None
    ball_pos = [50,50]
    ball_movement = [0,0]
    _status = "WAITING"

    def __init__(self):
        self.players = []
        self.ball_movement = [random.randint(-10, 10), random.randint(-10, 10)]
        print("A new game is waiting for players")

    @property
    def status(self):
        return self._status

    async def run_game(self, player):
        print("A new player has appeared")
        if len(self.players) > 2:
            raise exception("Too many players.")
        while True:
            msg = await player.socket.recv()
            if msg == "up":
                print(player.name + " : up")
                player.up()
                await player.socket.send(str(player.height))
            if msg == "down":
                print(player.name + " : down")
                player.down()
                await player.socket.send(str(player.height))

game = Game()

async def pong(websocket):
    global connections
    global game
    message = await websocket.recv()

    newplayer = Player(connection=websocket, name=message)
    await game.run_game(newplayer)

async def main():
    async with serve(pong, "localhost", 8765):
        await asyncio.get_running_loop().create_future()

asyncio.run(main())

