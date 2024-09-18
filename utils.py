from dataclasses import dataclass


@dataclass
class Point2D:
    line:int = 0
    column:int = 0


@dataclass
class Rectangle(Point2D):
    height:int = 0
    width:int = 0

    def collidesWith(self, rectangle):
        if self.line > rectangle.line and self.line < rectangle.line + rectangle.height:
            if self.column > rectangle.column and self.column < rectangle.column + rectangle.width:
                return True
        if self.line > rectangle.line and self.line < rectangle.line + rectangle.height:
            if self.column + self.width > rectangle.column and self.column + self.width < rectangle.column + rectangle.width:
                return True
        return False

