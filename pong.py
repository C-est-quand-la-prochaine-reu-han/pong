import time
import random
import asyncio
import datetime
from websockets.asyncio.server import serve
from websockets.asyncio.server import broadcast
from websockets.exceptions import ConnectionClosedOK


def collides(player, ball_position, index):
    if index == 1 and ball_position[0] > player.y + 10:
        return False
    if index == 2 and ball_position[0] < player.y - 10:
        return False
    if ball_position[1] < player.height - 100 or ball_position[1] > player.height + 100:
        return False
    return True


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


class Game:
    ball_pos = [500,500]
    ball_movement = [0,0]
    watchers = []
    timer = 0

    def __init__(self):
        self.ball_movement = [random.randint(-10, 10), random.randint(-2, 2)]
        print("A new game is waiting for players")

    async def broadcast(self, message):
        for w in self.watchers:
            await w.socket.send(message)

    async def handle_collision(self):
        if self.ball_pos[1] < 0 or self.ball_pos[1] > 1000:
            self.ball_movement[1] = -self.ball_movement[1]
            movement = "mov:" + str(self.ball_movement[0]) + ":" + str(self.ball_movement[1])
            await self.broadcast(movement)
        if collides(self.watchers[0], self.ball_pos, 1):
            self.ball_movement[1] += 3 * (0.01 * (self.ball_movement[1] - self.watchers[1].height) - 0.5)
            self.ball_movement[0] = abs(self.ball_movement[0]) + 0.01
            movement = "mov:" + str(self.ball_movement[0]) + ":" + str(self.ball_movement[1])
            await self.broadcast(movement)
        if collides(self.watchers[1], self.ball_pos, 2):
            self.ball_movement[1] += 3 * (0.01 * (self.ball_pos[1] - self.watchers[1].height) - 0.5)
            self.ball_movement[0] = -abs(self.ball_movement[0]) - 0.01
            movement = "mov:" + str(self.ball_movement[0]) + ":" + str(self.ball_movement[1])
            await self.broadcast(movement)

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
            movement = "mov:" + str(self.ball_movement[0]) + ":" + str(self.ball_movement[1])
            await self.broadcast(movement)

    async def handle_game_start(self):
        timer = int(datetime.datetime.now().timestamp())
        await self.broadcast("start")
        await self.watchers[0].socket.send("youare:1")
        await self.watchers[0].socket.send("opponent:" + self.watchers[1].name)
        await self.watchers[1].socket.send("youare:2")
        await self.watchers[1].socket.send("opponent:" + self.watchers[0].name)
        movement = "mov:" + str(self.ball_movement[0]) + ":" + str(self.ball_movement[1])
        await self.broadcast(movement)

    async def run(self):
        await self.handle_game_start()
        pos = "pos:" + str(self.ball_pos[0]) + ":" + str(self.ball_pos[1])
        await self.broadcast(pos)
        
        i = 0
        while True:
            time = int(datetime.datetime.now().timestamp())
            delay = (time - self.timer)
            self.timer = time
            self.ball_pos[0] += self.ball_movement[0] * delay
            self.ball_pos[1] += self.ball_movement[1] * delay
            await self.handle_collision()
            await self.handle_score()
            await asyncio.sleep(0.1)
            i += 1
            if i == 10:
                print(pos)
                pos = "pos:" + str(self.ball_pos[0]) + ":" + str(self.ball_pos[1])
                await self.broadcast(pos)
                i = 0



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
    async with serve(pong, "0.0.0.0", 8765) as websocket:
        await asyncio.get_running_loop().create_future()

asyncio.run(main())
