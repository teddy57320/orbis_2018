class FloodFiller:
    def __init__(self, world):
        self.world = world

    def flood_fill(self, body, territory, unit, next_move):
        """
        Returns the tiles that will be filled given unit, body, territory locations, and the next move.

        :param body: set of points of the body of the snake.
        :param territory: set of points of the territory of the snake.
        :param unit: point that the unit is on.
        :param next_move: next move that will be made by the unit.
        :return: set of points that will be filled, if any.
        """
        if next_move not in territory:
            return []
        if len(body) == 0:
            return []

        body.add(unit)
        points_to_be_filled = set()
        minX, maxX, minY, maxY = 300, -300, 300, -300

        for point in territory:
            if point[0] < minX:
                minX = point[0]
            if point[1] < minY:
                minY = point[1]
            if point[0] > maxX:
                maxX = point[0]
            if point[1] > maxY:
                maxY = point[1]

        for point in body:
            if point[0] < minX:
                minX = point[0]
            if point[1] < minY:
                minY = point[1]
            if point[0] > maxX:
                maxX = point[0]
            if point[1] > maxY:
                maxY = point[1]

        start = (maxX + 1, maxY + 1)
        visited = set()

        print(minX, maxX, minY, maxY)

        self.recursively_fill(minX, minY, maxX, maxY, start, visited, territory, body)

        for i in range(minX - 1, maxX + 2):
            for j in range(minY - 1, maxY + 2):
                if (i, j) not in visited and not self.world.is_wall((i, j)):
                    points_to_be_filled.add((i, j))

        return points_to_be_filled

    def recursively_fill(self, minX, minY, maxX, maxY, point, visited, territory, body):
        if point[0] < minX - 1 or point[0] > maxX + 1:
            return
        if point[1] < minY - 1 or point[1] > maxY + 1:
            return
        if point in territory:
            return
        if point in body:
            return
        visited.add(point)

        if not (point[0] - 1, point[1]) in visited:
            self.recursively_fill(minX, minY, maxX, maxY, (point[0] - 1, point[1]), visited, territory, body)
        if not (point[0] + 1, point[1]) in visited:
            self.recursively_fill(minX, minY, maxX, maxY, (point[0] + 1, point[1]), visited, territory, body)
        if not (point[0], point[1] - 1) in visited:
            self.recursively_fill(minX, minY, maxX, maxY, (point[0], point[1] - 1), visited, territory, body)
        if not (point[0], point[1] + 1) in visited:
            self.recursively_fill(minX, minY, maxX, maxY, (point[0], point[1] + 1), visited, territory, body)