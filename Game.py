import asyncio
from dataclasses import dataclass

from Ball import Ball
from utils import Rectangle

class Game:
    ball:Ball = Ball()
    players = []
    score_max:int = 0

    def __init__(self, score_max:int=10):
        self.score_max = score_max
        print("A new game is waiting for players")

    async def start_game(self):
        await self.broadcast("start")
        await self.players[0].socket.send("youare:1")
        await self.players[0].socket.send("opponent:" + self.players[1].name)
        await self.players[1].socket.send("youare:2")
        await self.players[1].socket.send("opponent:" + self.players[0].name)
        movement = "mov:" + str(self.ball.speed_line) + ":" + str(self.ball.speed_column)
        await self.broadcast(movement)

    async def broadcast(self, message:str):
        for w in self.players:
            await w.socket.send(message)

    def get_time_before_collision(self):
        time = 999999999999999999999999
        if self.ball.speed_column < 0:
            to_be_travelled = self.ball.column - 100
            temp_time = abs(to_be_travelled / self.ball.speed_column)
            if temp_time < time:
                time = temp_time

        if self.ball.speed_column > 0:
            to_be_travelled = 900 - self.ball.column - self.ball.width
            temp_time = abs(to_be_travelled / self.ball.speed_column)
            if temp_time < time:
                time = temp_time

        if self.ball.speed_line < 0:
            to_be_travelled = self.ball.line
            temp_time = abs(to_be_travelled / self.ball.speed_line)
            if temp_time < time:
                time = temp_time

        if self.ball.speed_line > 0:
            to_be_travelled = 1000 - self.ball.line - self.ball.height
            temp_time = abs(to_be_travelled / self.ball.speed_line)
            if temp_time < time:
                time = temp_time

        return time

    async def run(self):
        await self.start_game()
        pos = "pos:" + str(self.ball.line) + ":" + str(self.ball.column)
        await self.broadcast(pos)
        
        while True:
            # Broadcast the next movement and position
            mov = "mov:" + str(self.ball.speed_line) + ":" + str(self.ball.speed_column)
            pos = "pos:" + str(int(self.ball.line)) + ":" + str(int(self.ball.column))
            await self.broadcast(pos)
            await self.broadcast(mov)

            # Wait for the next collision
            delay_until_collision = self.get_time_before_collision()
            await asyncio.sleep(delay_until_collision)

            # Compute the new position and check for collision
            self.ball.line, self.ball.column = (self.ball.line + self.ball.speed_line * delay_until_collision, self.ball.column + self.ball.speed_column * delay_until_collision)

            # TODO Check for a collision
            if self.ball.line == 0:
                self.ball.speed_line = -self.ball.speed_line
            if self.ball.line == 1000:
                self.ball.speed_line = -self.ball.speed_line
            if self.ball.column == 100:
                self.ball.speed_column = -self.ball.speed_column
            if self.ball.column == 900:
                self.ball.speed_column = -self.ball.speed_column

            # TODO Invert the direction according to the collision

