import time
import random
import asyncio
import datetime
from websockets.asyncio.server import serve
from websockets.asyncio.server import broadcast
from websockets.exceptions import ConnectionClosedOK


class Point2D:
    line = 0
    column = 0


class Rectangle(Point2D):
    height = 0
    width = 0

    def collidesWith(self, rectangle):
        if self.line > rectangle.line and self.line < rectangle.line + rectangle.height:
            if self.column > rectangle.column and self.column < rectangle.column + rectangle.width:
                return True
        if self.line > rectangle.line and self.line < rectangle.line + rectangle.height:
            if self.column + self.width > rectangle.column and self.column + self.width < rectangle.column + rectangle.width:
                return True
        return False


class Ball(Rectangle):
    speed_line = 0
    speed_column = 0

    def __init__(self):
        self.init_speed()

    def init_speed(self):
        self.line = 500
        self.column = 500
        self.speed_line = random.randint(-5, 5)
        self.speed_column = random.choice((1, -1)) * random.randint(5, 10)

    async def move(self):
        self.line += self.speed_line
        self.column += self.speed_column


class Player(Rectangle):
    socket = None
    score = 0
    name = ""

    def __init__(self, connection=None, name="", size=100):
        self.line = 450
        self.name = name
        self.socket = connection
        self.height = size
        self.width = 10

    async def register(self, game):
        game.players.append(self)
        if (len(game.players) == 1):
            self.column = 100
        else:
            self.column = 900
        if len(game.players) == 2:
            asyncio.create_task(game.run())
            game = Game()
        self.game = game


class Game:
    ball = Ball()
    players = []
    score_max = 0

    def __init__(self, score_max=10):
        self.score_max = score_max
        print("A new game is waiting for players")

    async def broadcast(self, message):
        for w in self.players:
            await w.socket.send(message)

    async def handle_collision(self):
        movement = ""
        if self.ball.line <= 0:
            self.ball.speed_line = +(abs(self.ball.speed_line) + 0.2)
            movement = "mov:" + str(self.ball.speed_line) + ":" + str(self.ball.speed_column)
        if self.ball.line >= 1000:
            self.ball.speed_line = -(abs(self.ball.speed_line) + 0.2)
            movement = "mov:" + str(self.ball.speed_line) + ":" + str(self.ball.speed_column)
        if self.ball.collidesWith(self.players[0]):
            self.ball.speed_column = abs(self.ball.speed_column) + 1
            self.ball.column = self.players[0].column + self.players[0].width + 1
            movement = "mov:" + str(self.ball.speed_line) + ":" + str(self.ball.speed_column)
        if self.ball.collidesWith(self.players[1]):
            self.ball.speed_column = -abs(self.ball.speed_column + 1)
            self.ball.column = self.players[1].column - self.players[1].width + 1
            movement = "mov:" + str(self.ball.speed_line) + ":" + str(self.ball.speed_column)
        if movement != "":
            await self.broadcast(movement)

    async def check_score(self):
        score_msg = ""
        if self.ball.column > 1000:
            self.ball.init_speed()
            self.players[0].score += 1
            score_msg = "score:" + self.players[0].name + ":" + str(self.players[0].score)
        if self.ball.column < 0:
            self.ball.init_speed()
            self.players[1].score += 1
            score_msg = "score:" + self.players[1].name + ":" + str(self.players[1].score)
        if score_msg != "":
            await self.broadcast(score_msg)
            movement = "mov:" + str(self.ball.speed_line) + ":" + str(self.ball.speed_column)
            await self.broadcast(movement)

    async def start_game(self):
        await self.broadcast("start")
        await self.players[0].socket.send("youare:1")
        await self.players[0].socket.send("opponent:" + self.players[1].name)
        await self.players[1].socket.send("youare:2")
        await self.players[1].socket.send("opponent:" + self.players[0].name)
        movement = "mov:" + str(self.ball.speed_line) + ":" + str(self.ball.speed_column)
        await self.broadcast(movement)

    async def run(self):
        await self.start_game()
        pos = "pos:" + str(self.ball.line) + ":" + str(self.ball.column)
        await self.broadcast(pos)
        
        while True:
            # TODO DDA to check for collision between current ball position and next ball position.
            # It currently checks the collision on the current position, but if the step is too large (when the ball goes fast).
            # It goes through the paddel and looks like the ball goes through the paddel instead of bouncing.
            await self.ball.move()
            await self.handle_collision()
            await self.check_score()
            # TODO Sleep until you reached x 0, x 1000, y 100 or y 900
            await asyncio.sleep(0.1)
            pos = "pos:" + str(self.ball.line) + ":" + str(self.ball.column)
            await self.broadcast(pos)


game = Game()

async def pong(websocket):
    global game
    message = await websocket.recv()

    me = Player(connection=websocket, name=message)
    await me.register(game)
    while True:
        message = await me.socket.recv()
        if message == "up":
            me.line -= 10
            if me.line < 0:
                me.line = 0
            else:
                await game.broadcast(me.name + ":up") # TODO Send the player position instead of its movement
        if message == "down":
            me.line += 10
            if me.line > 900:
                me.line = 900
            else:
                await game.broadcast(me.name + ":down") # TODO Send the player position instead of its movement


async def main():
    async with serve(pong, "0.0.0.0", 8765) as websocket:
        await asyncio.get_running_loop().create_future()

asyncio.run(main())
