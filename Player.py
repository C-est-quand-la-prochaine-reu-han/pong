import asyncio

from websockets import ServerProtocol
from dataclasses import dataclass

from Game import Game
from utils import Rectangle

@dataclass
class Player(Rectangle):
    socket:ServerProtocol = None
    score:int = 0
    name:str = ""

    def __init__(self, connection=None, name:str="", size:int=100):
        self.line = 450
        self.name = name
        self.socket = connection
        self.height = size
        self.width = 10

    async def register(self, game:Game):
        game.players.append(self)
        if (len(game.players) == 1):
            self.column = 100
        else:
            self.column = 900
        if len(game.players) == 2:
            asyncio.create_task(game.run())
        self.game = game

