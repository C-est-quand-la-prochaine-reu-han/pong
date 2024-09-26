import random
from dataclasses import dataclass

from utils import Rectangle

@dataclass
class Ball(Rectangle):
    speed_line:float = 0
    speed_column:float = 0

    def __init__(self):
        self.init_speed()

    def init_speed(self):
        self.line = 500
        self.column = 500
        self.speed_line = 10 * random.randint(-5, 5)
        self.speed_column = 10 * random.choice((1, -1)) * random.randint(8, 12)

    async def move(self):
        self.line += self.speed_line
        self.column += self.speed_column
