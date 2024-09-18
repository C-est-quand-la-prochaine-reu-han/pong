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

    async def handle_collision(self):
        movement = ""
        if self.ball.line <= 0:
            self.ball.speed_line = +(abs(self.ball.speed_line) + 0.2)
            movement = "mov:" + str(self.ball.speed_line) + ":" + str(self.ball.speed_column)
        if self.ball.line >= 1000:
            self.ball.speed_line = -(abs(self.ball.speed_line) + 0.2)
            movement = "mov:" + str(self.ball.speed_line) + ":" + str(self.ball.speed_column)
        if self.ball.collidesWith(self.players[0]):
            angle = ((self.ball.line - self.players[0].line) - 50) / 100
            self.ball.speed_column = abs(self.ball.speed_column) + abs(angle)
            self.ball.speed_line += angle
            self.ball.column = self.players[0].column + self.players[0].width + 1
            movement = "mov:" + str(self.ball.speed_line) + ":" + str(self.ball.speed_column)
        if self.ball.collidesWith(self.players[1]):
            angle = ((self.ball.line - self.players[1].line) - 50) / 100
            self.ball.speed_column = - abs(self.ball.speed_column + 1) - abs(angle)
            self.ball.speed_line += angle
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

    def get_time_before_collision(self):
        time = 999999999999999999999999
        if self.ball.speed_column < 0:
            to_be_travelled = self.ball.column - 100
            temp_time = abs(to_be_travelled / self.ball.speed_column)
            if temp_time < time:
                time = temp_time

        if self.ball.speed_column > 0:
            to_be_travelled = 900 - self.ball.column
            temp_time = abs(to_be_travelled / self.ball.speed_column)
            if temp_time < time:
                time = temp_time

        if self.ball.speed_line < 0:
            to_be_travelled = self.ball.line
            temp_time = abs(to_be_travelled / self.ball.speed_line)
            if temp_time < time:
                time = temp_time

        if self.ball.speed_line > 0:
            to_be_travelled = 1000 - self.ball.line
            temp_time = abs(to_be_travelled / self.ball.speed_line)
            if temp_time < time:
                time = temp_time

        return time

    async def run(self):
        await self.start_game()
        pos = "pos:" + str(self.ball.line) + ":" + str(self.ball.column)
        await self.broadcast(pos)
        
        while True:
            await self.handle_collision()
            await self.check_score()

            mov = "mov:" + str(self.ball.speed_line) + ":" + str(self.ball.speed_column)
            pos = "pos:" + str(int(self.ball.line)) + ":" + str(int(self.ball.column))
            print(mov)
            print(pos)
            await self.broadcast(pos)
            await self.broadcast(mov)

            delay_until_collision = self.get_time_before_collision()
            print(delay_until_collision)
            await asyncio.sleep(delay_until_collision)

            self.ball.line, self.ball.column = (self.ball.line + self.ball.speed_line * delay_until_collision, self.ball.column + self.ball.speed_column * delay_until_collision)
            if self.ball.column == 900:
                self.ball.column = 899
            if self.ball.column == 100:
                self.ball.column = 101
            if self.ball.line == 1000:
                self.ball.line = 999
            if self.ball.line == 0:
                self.ball.line = 1

