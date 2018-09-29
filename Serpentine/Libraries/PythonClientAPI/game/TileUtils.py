from PythonClientAPI.structures.Collections import PriorityQueue, Queue
from PythonClientAPI.game.Enums import TileType, Direction, Team
from PythonClientAPI.game.PointUtils import *
from PythonClientAPI.game.Entities import Tile


class TileUtils:
    def __init__(self, world, friendly_unit, enemy_units_map):
        self.world = world
        self.friendly_unit = friendly_unit
        self.enemy_units_map = enemy_units_map

    def get_closest_point_from(self, source, condition):
        """
        Returns the closest point from a given point given a predicate.

        :param source: point of interest.
        :param condition: specified predicate.
        :return: closest point from source that satisfies condition.
        :rtype: tuple
        """
        queue = Queue()
        visited = set()
        queue.add(source)
        visited.add(source)

        while not (queue.is_empty()):
            cursor = queue.poll()
            neighbours = self.world.get_neighbours(cursor)

            for direction in Direction.ORDERED_DIRECTIONS:
                neighbour = neighbours[direction]
                if not ((neighbour in visited) or self.world.is_wall(neighbour)):
                    queue.add(neighbour)
                    visited.add(neighbour)

            if condition(cursor):
                return cursor

        return None

    def get_closest_neutral_territory_from(self, point, excluding_points):
        """
        Returns the closest tile that isn't owned by any team from a given point.

        :param point: point of interest
        :param excluding_points: collection of points to exclude in search.
        :return: closest neutral tile from point.
        :rtype: Tile
        """
        if not self.world.is_within_bounds(point):
            return None
        target = self.get_closest_point_from(point, lambda p: self.world.position_to_tile_map[p].is_neutral and ((not excluding_points) or (p not in excluding_points)))
        if target is not None:
            return self.world.position_to_tile_map[target]
        return None

    def get_closest_capturable_territory_from(self, point, excluding_points):
        """
        Returns the closest tile that is capturable (neutral or enemy).

        :param point: point of interest
        :param excluding_points: collection of points to exclude in search.
        :return: closest capturable tile from point.
        :rtype: Tile
        """
        if not self.world.is_within_bounds(point):
            return None
        target = self.get_closest_point_from(point, lambda p: (self.world.position_to_tile_map[p].is_neutral or self.world.position_to_tile_map[p].is_enemy) and ((not excluding_points) or (p not in excluding_points)))
        if target is not None:
            return self.world.position_to_tile_map[target]
        return None

    def get_closest_friendly_territory_from(self, point, excluding_points):
        """
        Returns the closest tile that is a part of friendly territory.

        :param point: point of interest
        :param excluding_points: collection of points to exclude in search.
        :return: closest friendly tile from point.
        :rtype: Tile
        """
        if not self.world.is_within_bounds(point):
            return None
        target = self.get_closest_point_from(point, lambda p: self.world.position_to_tile_map[p].is_friendly and ((not excluding_points) or (p not in excluding_points)))
        if target is not None:
            return self.world.position_to_tile_map[target]
        return None

    def get_closest_enemy_territory_from(self, point, excluding_points):
        """
        Returns the closest tile that is a part of enemy territory (any enemy team).

        :param point: point of interest
        :param excluding_points: collection of points to exclude in search.
        :return: closest enemy tile from point.
        :rtype: Tile
        """
        if not self.world.is_within_bounds(point):
            return None
        target = self.get_closest_point_from(point, lambda p: self.world.position_to_tile_map[p].is_enemy and ((not excluding_points) or (p not in excluding_points)))
        if target is not None:
            return self.world.position_to_tile_map[target]
        return None

    def get_closest_territory_by_team(self, point, team, excluding_points):
        """
        Returns the closest tile that is a part of the given team's territory.

        :param point: point of interest
        :param team: team of interest
        :param excluding_points: collection of points to exclude in search.
        :return: closest tile from point that belongs to the team of interest.
        :rtype: Tile
        """
        if not self.world.is_within_bounds(point):
            return None
        target = self.get_closest_point_from(point, lambda p: self.world.position_to_tile_map[p].owner == team and ((not excluding_points) or (p not in excluding_points)))
        if target is not None:
            return self.world.position_to_tile_map[target]
        return None

    def get_closest_friendly_body_from(self, point, excluding_points):
        """
        Returns the closest tile that has a friendly body on it.

        :param point: point of interest
        :param excluding_points: collection of points to exclude in search.
        :return: closest tile from point that has a friendly body on it.
        :rtype: Tile
        """
        if not self.world.is_within_bounds(point):
            return None
        target = self.get_closest_point_from(point, lambda p: self.world.position_to_tile_map[p].body == self.friendly_unit.team and ((not excluding_points) or (p not in excluding_points)))
        if target is not None:
            return self.world.position_to_tile_map[target]
        return None

    def get_closest_enemy_body_from(self, point, excluding_points):
        """
        Returns the closest tile that has an enemy body on it (any enemy team).

        :param point: point of interest
        :param excluding_points: collection of points to exclude in search.
        :return: closest tile from point that has an enemy body on it.
        :rtype: Tile
        """
        if not self.world.is_within_bounds(point):
            return None
        target = self.get_closest_point_from(point, lambda p: self.world.position_to_tile_map[p].body in self.enemy_units_map.keys() and ((not excluding_points) or (p not in excluding_points)))
        if target is not None:
            return self.world.position_to_tile_map[target]
        return None

    def get_closest_body_by_team(self, point, team, excluding_points):
        """
        Returns the closest tile that has a body of the given team.

        :param point: point of interest
        :param excluding_points: collection of points to exclude in search.
        :return: closest tile from point that has a body of a given point on it.
        :rtype: Tile
        """
        if not self.world.is_within_bounds(point):
            return None
        target = self.get_closest_point_from(point, lambda p: self.world.position_to_tile_map[p].body == team and ((not excluding_points) or (p not in excluding_points)))
        if target is not None:
            return self.world.position_to_tile_map[target]
        return None

    def get_closest_enemy_head_from(self, point, excluding_points):
        """
        Returns the closest tile that has an enemy head on it (any enemy team).

        :param point: point of interest
        :param excluding_points: collection of points to exclude in search.
        :return: closest tile from point that has an enemy head on it.
        :rtype: Tile
        """
        if not self.world.is_within_bounds(point):
            return None
        target = self.get_closest_point_from(point, lambda p: self.world.position_to_tile_map[p].head in self.enemy_units_map.keys() and ((not excluding_points) or (p not in excluding_points)))
        if target is not None:
            return self.world.position_to_tile_map[target]
        return None

    def get_closest_head_by_team(self, point, team, excluding_points):
        """
        Returns the closest tile that has a head of the given team.

        :param point: point of interest
        :param excluding_points: collection of points to exclude in search.
        :return: closest tile from point that has the head of a given team on it.
        :rtype: Tile
        """
        if not self.world.is_within_bounds(point):
            return None
        target = self.get_closest_point_from(point, lambda p: self.world.position_to_tile_map[p].head == team and ((not excluding_points) or (p not in excluding_points)))
        if target is not None:
            return self.world.position_to_tile_map[target]
        return None

    def get_friendly_territory_edges(self):
        """
        Returns the edges of friendly territory.

        :return: set of tiles at the edges of friendly territory.
        :rtype: set
        """
        edges = set()
        for point in self.friendly_unit.territory:
            for adjacent in self.world.get_neighbours(point).values():
                adjacent_tile = self.world.position_to_tile_map[adjacent]
                if adjacent_tile.is_neutral or adjacent_tile.is_enemy:
                    edges.add(self.world.position_to_tile_map[point])
        return edges

    def get_friendly_territory_corners(self):
        """
        Returns the corners of friendly territory.

        :return: set of tiles at the corners of friendly territory.
        :rtype: set
        """
        corners = set()
        edges = self.get_friendly_territory_edges()
        for t in edges:
            friendly_adjacent_tiles = set()
            for adjacent in self.world.get_neighbours(t.position).values():
                adjacent_tile = self.world.position_to_tile_map[adjacent]
                if adjacent_tile.is_friendly:
                    friendly_adjacent_tiles.add(adjacent_tile)

            distinct_x = set()
            distinct_y = set()

            for tile in friendly_adjacent_tiles:
                distinct_x.add(t.position[0])
                distinct_y.add(t.position[1])

            if len(distinct_x) == len(distinct_y) == len(friendly_adjacent_tiles):
                corners.add(t)

        return corners
