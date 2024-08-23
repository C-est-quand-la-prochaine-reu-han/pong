import time
import random
import asyncio
from websockets.asyncio.server import serve
from websockets.asyncio.server import broadcast
from websockets.exceptions import ConnectionClosedOK

class Player:
    socket = None
    name = ""
    height = 0
    y = 0
    score = 0

    def __init__(self, connection=None, name=""):
        self.height = 500
        self.name = name
        self.socket = connection

    async def register(self, game):
        game.watchers.append(self)
        if (len(game.watchers) == 1):
            self.y = 100
        else:
            self.y = 900
        if len(game.watchers) == 2:
            asyncio.create_task(game.run())
            game = Game()
        self.game = game


def collides(player, ball_position):
    if ball_position[0] < player.y - 20 or ball_position[0] > player.y + 20:
        return False
    if ball_position[1] < player.height - 20 or ball_position[1] > player.height + 20:
        return False
    return True


class Game:
    ball_pos = [500,500]
    ball_movement = [0,0]
    watchers = []

    def __init__(self):
        self.ball_movement = [random.randint(-10, 10), random.randint(-4, 4)]
        print("A new game is waiting for players")

    def handle_collision(self):
      if self.ball_pos[1] < 0 or self.ball_pos[1] > 1000:
          self.ball_movement[1] = -self.ball_movement[1]
      if collides(self.watchers[0], self.ball_pos):
          self.ball_movement[1] += 3 * (0.01 * (self.ball_movement[1] - self.watchers[1].height) - 0.5)
          self.ball_movement[0] = abs(self.ball_movement[0]) + 0.01
      if collides(self.watchers[1], self.ball_pos):
          self.ball_movement[1] += 3 * (0.01 * (self.ball_pos[1] - self.watchers[1].height) - 0.5)
          self.ball_movement[0] = -abs(self.ball_movement[0]) - 0.01

    async def handle_score(self):
        score_msg = ""
        if self.ball_pos[0] > 1000:
            self.ball_pos = [500, 500]
            self.ball_movement = [random.randint(-10, 10), random.randint(-4, 4)]
            self.watchers[0].score += 1
            score_msg = "score:" + self.watchers[0].name + ":" + str(self.watchers[0].score)
        if self.ball_pos[0] < 0:
            self.ball_pos = [500, 500]
            self.ball_movement = [random.randint(-10, 10), random.randint(-4, 4)]
            self.watchers[1].score += 1
            score_msg = "score:" + self.watchers[1].name + ":" + str(self.watchers[1].score)
        if score_msg != "":
            await self.broadcast(score_msg)

    async def run(self):
        await self.broadcast("start")
        await self.watchers[0].socket.send("youare:1")
        await self.watchers[0].socket.send("opponent:" + self.watchers[1].name)
        await self.watchers[1].socket.send("youare:2")
        await self.watchers[1].socket.send("opponent:" + self.watchers[0].name)

        while True:
            self.ball_pos[0] += self.ball_movement[0]
            self.ball_pos[1] += self.ball_movement[1]
            self.handle_collision()
            await self.handle_score()
            pos = "pos:" + str(self.ball_pos[0]) + ":" + str(self.ball_pos[1])
            await self.broadcast(pos)
            await asyncio.sleep(0.1)

    async def broadcast(self, message):
        for w in self.watchers:
            await w.socket.send(message)

game = Game()

async def pong(websocket):
    global game
    message = await websocket.recv()

    me = Player(connection=websocket, name=message)
    await me.register(game)
    while True:
        message = await me.socket.recv()
        if message == "up":
            me.height -= 10
            await game.broadcast(me.name + ":up")
        if message == "down":
            me.height += 10
            await game.broadcast(me.name + ":down")


async def main():
    async with serve(pong, "localhost", 8765) as websocket:
        await asyncio.get_running_loop().create_future()

asyncio.run(main())
