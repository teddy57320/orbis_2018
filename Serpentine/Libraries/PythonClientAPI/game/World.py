from PythonClientAPI.game.Enums import TileType, Direction
from PythonClientAPI.game.Entities import Tile
from PythonClientAPI.game.TileUtils import TileUtils
from PythonClientAPI.game.FloodFiller import FloodFiller
from PythonClientAPI.game.PathFinder import PathFinder


class World:
    """
    Represents a colour-changing tile on the board.

    :ivar position_to_tile_map: dictionary of tuple positions to corresponding Tile objects.
    :ivar PathFinder path: instance of PathFinder class - access methods by calling world.path...
    :ivar TileUtils util: instance of TileUtils class - access methods by calling world.util...
    :ivar FloodFiller fill: instance of FloodFiller class - access methods by calling world.fill...
    """
    def __init__(self, tiles, friendly_unit, enemy_units_map):
        self.position_to_tile_map = {}
        self.tiles = tiles
        self.width = len(tiles)
        self.height = len(tiles[0])
        self.friendly_unit = friendly_unit
        self.enemy_units_map = enemy_units_map
        self._set_position_to_tile_map(tiles, friendly_unit, enemy_units_map)
        self.neutral_points = self._deduce_neutral_territory(tiles, friendly_unit, enemy_units_map)
        self.path = PathFinder(self)
        self.util = TileUtils(self, friendly_unit, enemy_units_map)
        self.fill = FloodFiller(self)

    def _deduce_neutral_territory(self, tiles, friendly_unit, enemy_units_map):
        neutral_points = set()

        for x in range(len(tiles)):
            for y in range(len(tiles[0])):
                neutral = True
                if tiles[x][y] == TileType.WALL or (x, y) in friendly_unit.territory:
                    neutral = False
                for key in enemy_units_map:
                    if (x, y) in enemy_units_map[key].territory:
                        neutral = False
                        break
                if neutral:
                    neutral_points.add((x, y))
                    if (x, y) in self.position_to_tile_map.keys():
                        self.position_to_tile_map[(x, y)].is_neutral = True
                    else:
                        self.position_to_tile_map[(x, y)] = Tile(self, True, False, False, self.is_edge((x, y)), False, None, None, None, (x, y))
        return neutral_points

    def _set_position_to_tile_map(self, tiles, friendly_unit, enemy_units_map):
        for x in range(len(tiles)):
            for y in range(len(tiles[0])):
                pos = (x, y)
                tile = Tile(self, False, False, False, False, False, None, None, None, (x, y))

                if self.is_wall(pos):
                    tile.is_wall = True

                if self.is_edge(pos):
                    tile.is_edge = True

                if pos == friendly_unit.position:
                    tile.head = friendly_unit.team

                if pos in friendly_unit.body:
                    tile.body = friendly_unit.team

                if pos in friendly_unit.territory:
                    tile.owner = friendly_unit.team
                    tile.is_friendly = True

                for key in enemy_units_map:
                    enemy_unit = enemy_units_map[key]
                    if pos == enemy_unit.position:
                        tile.head = enemy_unit.team

                    if pos in enemy_unit.body:
                        tile.body = enemy_unit.team

                    if pos in enemy_unit.territory:
                        tile.owner = enemy_unit.team
                        tile.is_enemy = True

                self.position_to_tile_map[pos] = tile

    def get_width(self):
        """
        Returns the integer width of the current map.
        The width includes walls.

        :return: the width of the map.
        :rtype: int
        """
        return self.width

    def get_height(self):
        """
        Returns the integer height of the current map.
        The height includes walls.

        :return: the height of the map.
        :rtype: int
        """
        return self.height

    def is_within_bounds(self, point):
        """
        Returns a boolean indicating whether the point is in bounds.
        Note that walls count as being in bounds.

        :param point: point of interest.
        :return: true if point is within bounds.
        :rtype: bool
        """
        return (0 <= point[0] < self.width) and (0 <= point[1] < self.height)

    def is_wall(self, point):
        """
        Returns a boolean indicating whether the point is a wall.

        :param point: point of interest.
        :return: true if point is wall.
        :rtype: bool
        """
        return self.tiles[point[0]][point[1]] == TileType.WALL

    def is_edge(self, point):
        """
        Returns a boolean indicating whether the point is at the edge of the map.
        Edge points are points directly adjacent to the wall.

        :param point: point of interest.
        :return: true if point is wall.
        :rtype: bool
        """
        return self.is_within_bounds(point) and \
               (point[0] == 1 or point[1] == 1 or point[0] == self.width - 2 or point[1] == self.height - 2)

    def get_neutral_points(self):
        """
        Returns a set of neutral points on the map.
        Points are neutral if the point is not a part of any team's territory, and not a wall.
        Note that units and bodies can be on neutral points.

        :return: set of all neutral points.
        :rtype: set
        """
        return self.neutral_points

    def get_neighbours(self, point):
        """
        Returns a dictionary of direction to neighbouring points.

        :param point: point of interest.
        :return: dictionary of direction to neighbours.
        :rtype: dictionary
        """
        neighbours = {}
        for direction in Direction.ORDERED_DIRECTIONS:
            neighbours[direction] = direction.move_point(point)
        return neighbours

    def get_unit_by_team(self, team):
        """
        Returns units corresponding to a given team.

        :param team: team of interest.
        :return: the unit of that team.
        :rtype: Unit
        """
        if team == self.friendly_unit.team:
            return self.friendly_unit
        else:
            return self.enemy_units_map[team]
