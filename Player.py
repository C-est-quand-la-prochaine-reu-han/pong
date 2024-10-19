import asyncio

from websockets import ServerProtocol
from dataclasses import dataclass

from Game import Game
from utils import Rectangle

@dataclass
class Player(Rectangle):
    def __init__(self, connection=None, name:str="", token="", id=-1, size:int=100):
        self.line = 450
        self.score = 0
        self.name = name
        self.socket = connection
        self.height = size
        self.width = 10
        self.token = token
        self.id = id

    async def register(self, game:Game):
        game.players.append(self)
        if (len(game.players) == 1):
            self.column = 100
        else:
            self.column = 900
        if len(game.players) == 2:
            asyncio.create_task(game.run())
        self.game = game

