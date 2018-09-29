from PythonClientAPI.game.Enums import Team

class Entity:
    def __init__(self, position):
        self.position = position

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.position == other.position

    def __ne__(self, other):
        return not self.__eq__(other)


class Tile(Entity):
    """
    Represents a colour-changing tile on the board.

    :ivar boolean is_neutral: true if tile is neutral.
    :ivar boolean is_enemy: true if tile is enemy territory.
    :ivar boolean is_friendly: true if tile is friendly territory.
    :ivar boolean is_edge: true if tile is at the edge.
    :ivar boolean is_wall: true if tile is at wall.
    :ivar Team owner: team that owns this tile.
    :ivar Team body: team that has a body on this tile.
    :ivar Team head: team that has a head on this tile.
    :ivar tuple position: point corresponding to this tile.
    """
    def __init__(self, world, is_neutral, is_friendly, is_enemy, is_edge, is_wall, owner, body, head, position):
        super().__init__(position)
        self.is_neutral = is_neutral
        self.world = world
        self.is_friendly = is_friendly
        self.is_enemy = is_enemy
        self.is_edge = is_edge
        self.is_wall = is_wall
        self.owner = owner
        self.body = body
        self.head = head
        self.position = position

    def get_neighbours(self):
        modifiers = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        adjacent = [self.world.position_to_tile_map[(self.position[0] + m[0], self.position[1] + m[1])] for m in modifiers if m in self.world.position_to_tile_map]
        adjacent = [t for t in adjacent if t]
        result = set(t for t in adjacent)
        return result

    def __hash__(self):
        return 31 + self.position[0] * 31 + self.position[1]

    def __repr__(self):
        return "{} TILE: {}".format(self.owner, self.position)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.position == other.position

    def __ne__(self, other):
        return not (self == other)

class Unit(Entity):
    def __init__(self, team, uuid, position, status, body, territory, turn_penalty):
        super().__init__(position)
        self.uuid = uuid
        self.position = tuple((position['x'], position['y']))
        self.team = team
        self.status = status
        self.body = set([tuple((point['x'], point['y'])) for point in body])
        self.territory = set([tuple((point['x'], point['y'])) for point in territory])
        self.turn_penalty = turn_penalty

    def __hash__(self):
        return hash(self.team) * 31 + hash(self.uuid)

    def __repr__(self):
        return str(self.uuid)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.uuid == other.uuid

    def __ne__(self, other):
        return not (self == other)


class FriendlyUnit(Unit):
    """
    Represents a friendly unit.

    :ivar str uuid: unique uuid for this unit
    :ivar position: unit position
    :ivar status: status of the unit.
    :ivar body: set of points corresponding to unit's body.
    :ivar snake: union of position and body.
    :ivar territory: set of points corresponding to unit's territory.
    :ivar turn_penalty: remaining turns on unit's turn penalty.
    """
    def __init__(self, team, uuid, position, status, body, territory, turn_penalty):
        super().__init__(team, uuid, position, status, body, territory, turn_penalty)
        self.next_move_target = None
        self.team = team
        self.status = status
        self.position = tuple((position['x'], position['y']))
        self.body = set([tuple((point['x'], point['y'])) for point in body])
        self.snake = set([self.position]) | self.body
        self.territory = set([tuple((point['x'], point['y'])) for point in territory])
        self.turn_penalty = turn_penalty

    def move(self, point):
        """
        :param FriendlyUnit friendly_unit: friendly unit to move
        :param point: target point to move the unit to
        :return: void
        """
        self.next_move_target = point

class EnemyUnit(Unit):
    """
    Represents a friendly unit.

    :ivar str uuid: unique uuid for this unit
    :ivar position: unit position
    :ivar status: status of the unit.
    :ivar body: set of points corresponding to unit's body.
    :ivar snake: union of position and body.
    :ivar territory: set of points corresponding to unit's territory.
    :ivar turn_penalty: remaining turns on unit's turn penalty.
    """

    def __init__(self, team, uuid, position, status, body, territory, turn_penalty):
        super().__init__(team, uuid, position, status, body, territory, turn_penalty)
        self.team = team
        self.position = tuple((position['x'], position['y']))
        self.status = status
        self.body = set([tuple((point['x'], point['y'])) for point in body])
        self.snake = set([self.position]) | self.body
        self.territory = set([tuple((point['x'], point['y'])) for point in territory])
        self.turn_penalty = turn_penalty
