from PythonClientAPI.structures.Collections import PriorityQueue, Queue
from PythonClientAPI.game.Enums import TileType, Direction, Team
from PythonClientAPI.game.PointUtils import *
from PythonClientAPI.navigation.NavigationCache import navigation_cache


class PathFinder:
    def __init__(self, world):
        self.world = world

    def get_taxi_cab_distance(self, start, end):
        """
        Returns the taxi-cab distance between two points.

        :param start: start point.
        :param end: end point.
        :return: taxi-cab distance.
        :rtype: int
        """
        return abs(start[0] - end[0]) + abs(start[1] - end[1])

    def get_shortest_path(self, start, end, avoid):
        """
        Returns a list of points (in order) showing the shortest path between 2 points.

        :param start: start point.
        :param end: end point.
        :param avoid: collection of points to avoid.
        :return: list of points in shortest path.
        :rtype: list
        """
        if start == end: return [end]
        if self.world.is_wall(start) or self.world.is_wall(end): return None

        queue = PriorityQueue()

        queue.add(start, 0)

        inverted_tree = {}
        movement_costs = {}

        inverted_tree[start] = None
        movement_costs[start] = 0

        while not queue.is_empty():
            current = queue.poll()

            neighbours = self.world.get_neighbours(current)
            for direction in Direction.ORDERED_DIRECTIONS:
                neighbour = neighbours[direction]
                if self.world.is_wall(neighbour) or (avoid and (neighbour in avoid)):
                    continue
                cost = movement_costs[current] + 1
                if (neighbour not in movement_costs) or (cost < movement_costs[neighbour]):
                    movement_costs[neighbour] = cost
                    queue.add(neighbour,
                              cost + self.get_taxi_cab_distance(neighbour, end))
                    inverted_tree[neighbour] = current

            if current == end:
                path = []
                cursor = end
                peek_cursor = inverted_tree[cursor]
                while peek_cursor:
                    path.append(cursor)
                    cursor = peek_cursor
                    peek_cursor = inverted_tree[cursor]
                path.reverse()
                return path

        return None

    def get_shortest_path_distance(self, start, end):
        """
        Returns the shortest distance between 2 points.

        :param start: start point.
        :param end: end point.
        :return: distance between the 2 points.
        :rtype: int
        """
        if not navigation_cache.loaded:
            path = self.get_shortest_path(start, end, None)
            if path: return len(path)
            return 0
        return navigation_cache.get_distance(start, end)


    def get_next_point_in_shortest_path(self, start, end):
        """
        Returns the next point in the shortest path between 2 points.

        :param start: start point.
        :param end: end point.
        :return: next point in shortest path.
        :rtype: tuple
        """
        if not navigation_cache.loaded:
            path = self.get_shortest_path(start, end, None)
            if path:
                return path[0]
            return start
        direction = navigation_cache.get_next_direction_in_path(start, end)
        return direction.move_point(start)