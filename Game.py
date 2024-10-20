import os
import sys
import json
import math
import asyncio
import requests
import datetime

from Ball import Ball
from utils import Rectangle

from dateutil import tz
from datetime import timezone

from websockets.exceptions import WebSocketException

class Game:
    def __init__(self, score_max:int=10):
        self.score_max = score_max
        self.opponent = "*"
        self.players = []
        self.ball = Ball()
        self.score_max = 0
        self.start_time = None
        self.ball_max_speed = 0
        self.tournament_id = None

    async def start_game(self):
        # await self.broadcast("time")
        # asyncio.sleep(3)
        await self.broadcast("start")
        await self.players[0].socket.send("opponent:" + self.players[1].name)
        await self.players[0].socket.send("youare:1")
        await self.players[1].socket.send("opponent:" + self.players[0].name)
        await self.players[1].socket.send("youare:2")
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

    async def handle_victory(self):
        if self.players[0].score == 1:
            await self.broadcast("winner:" + self.players[0].name)
            return True
        if self.players[1].score == 1:
            await self.broadcast("winner:" + self.players[1].name)
            return True
        return False

    async def handle_collision(self):
        if self.ball.line <= 0 or self.ball.line >= 1000:
            self.ball.speed_line = -self.ball.speed_line
        if self.ball.column <= 100 and self.ball.line >= self.players[0].line and self.ball.line <= self.players[0].line + self.players[1].height:
            self.ball.speed_column = -self.ball.speed_column + 5
            self.ball.speed_line += (self.ball.line - self.players[0].line) / self.players[0].height * 100 - 50
            self.players[0].ball_hit += 1
        elif self.ball.column <= 100:
            self.players[1].score += 1
            await self.broadcast("score:" + self.players[1].name + ":" + str(self.players[1].score))
            self.ball.init_speed()
            return
        if self.ball.column >= 900 and self.ball.line >= self.players[1].line and self.ball.line <= self.players[1].line + self.players[1].height:
            self.ball.speed_column = -self.ball.speed_column - 5
            self.ball.speed_line += (self.ball.line - self.players[1].line) / self.players[1].height * 100 - 50
            self.players[1].ball_hit += 1
        elif self.ball.column >= 900:
            self.players[0].score += 1
            await self.broadcast("score:" + self.players[0].name + ":" + str(self.players[0].score))
            self.ball.init_speed()
            return

    def save_match(self):
        tzone = tz.gettz('Europe/Paris')
        match_data = {
            "player1": self.players[0].id,
            "player2": self.players[1].id,
            "match_start_time": self.start_time,
            "match_end_time": datetime.datetime.now(tz=tzone),
            "player1_hit_nb": self.players[0].ball_hit,
            "player2_hit_nb": self.players[1].ball_hit,
            "player1_perfect_hit_nb": 0,
            "player2_perfect_hit_nb": 0,
            "player1_score": self.players[0].score,
            "player2_score": self.players[1].score,
            "ball_max_speed": int(self.ball_max_speed),
            "match_status": 1
        }
        print(self.tournament_id, file=sys.stderr)
        if self.tournament_id is not None:
            match_data["tournament"] = self.tournament_id
        r = requests.post(
                "http://ft-transcendence-api-1:" + str(os.environ.get("API_PORT")) + "/appong/api/match/",
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': 'Token ThisIsASuperStrongAndSolidToken:3'
            },

            data=json.dumps(match_data, default=str)
        )
        print("=========== REQUEST ===========", file=sys.stderr)
        print(r.status_code, file=sys.stderr)
        print(r.text, file=sys.stderr)

    async def run(self):
        self.start_time = datetime.datetime.now(tz=tz.gettz('Europe/Paris'))
        try:
            await self.start_game()
            pos = "pos:" + str(self.ball.line) + ":" + str(self.ball.column)
            await self.broadcast(pos)
        
            while True:
                # Broadcast the next movement and position
                mov = "mov:" + str(self.ball.speed_line) + ":" + str(self.ball.speed_column)
                pos = "pos:" + str(self.ball.line) + ":" + str(self.ball.column)
                await self.broadcast(pos)
                await self.broadcast(mov)

                # Calculate the speed of the ball and update max_speed if required
                speed = math.sqrt(pow(self.ball.speed_line, 2) + pow(self.ball.speed_column, 2))
                if speed > self.ball_max_speed:
                    self.ball_max_speed = speed

                # Wait for the next collision
                delay_until_collision = self.get_time_before_collision()
                print("let's sleep for %s" % delay_until_collision)
                await asyncio.sleep(delay_until_collision)

                # Compute the new position and check for collision
                self.ball.line = int(self.ball.line + self.ball.speed_line * delay_until_collision)
                self.ball.column = int(self.ball.column + self.ball.speed_column * delay_until_collision)
                await self.handle_collision()

                if await self.handle_victory():
                    self.save_match()
                    break
        except WebSocketException:
            for w in self.players:
                try:
                    await w.socket.send("winner:aborted")
                except:
                    pass
            return

