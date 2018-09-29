from enum import Enum
from PythonClientAPI.game.PointUtils import *


class Direction(Enum):
    """
    Represents cardinal directions that units can move in.
    Their value is a coordinate offset represented by a single move of 1 tile in that direction.
    """
    NOWHERE = (0, 0)
    NORTH = (0, -1)
    EAST = (1, 0)
    SOUTH = (0, 1)
    WEST = (-1, 0)

    def move_point(self, point):
        """
        Returns a new point who's values are that of the given point moved 1 tile in this direction.

        :param (int,int) point: (x,y) point
        :rtype: (int,int)
        """
        return add_points(point, self.value)


Direction._delta_to_direction = {
    direction.value: direction for direction in Direction
}

Direction.ORDERED_DIRECTIONS = [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]
Direction.INDEX_TO_DIRECTION = {0: Direction.NOWHERE, 1: Direction.NORTH, 2: Direction.EAST, 3: Direction.SOUTH, 4: Direction.WEST}
Direction.DIRECTION_TO_INDEX = {Direction.INDEX_TO_DIRECTION[idx]: idx for idx in Direction.INDEX_TO_DIRECTION.keys()}


class TileType(Enum):
    WALL = 0
    TILE = 1

class Team(Enum):
    RED = 0
    BLUE = 1
    GREEN = 2
    PURPLE = 3

    @classmethod
    def get_players(cls):
        return [element.name for element in cls]


class Status(Enum):
    VALID_MOVE = 0
    INVALID_MOVE = 1
    DISABLED = 2
    RESPAWNED = 3
    BLOCKED_BY_WALL = 4
