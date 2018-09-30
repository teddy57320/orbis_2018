from PythonClientAPI.game.PointUtils import *
from PythonClientAPI.game.Entities import FriendlyUnit, EnemyUnit, Tile
from PythonClientAPI.game.Enums import Team
from PythonClientAPI.game.World import World
from PythonClientAPI.game.TileUtils import TileUtils
from PythonClientAPI.game.PathFinder import PathFinder

class PlayerAI:

    def __init__(self):
        ''' Initialize! '''
        self.turn_count = 0             # game turn count
        self.target = None              # target to send unit to!
        self.outbound = True            # is the unit leaving, or returning?\
        self.move = None
        self.max_num_exposed_turns = 10

        self.world = None
        self.friendly_unit = None
        self.enemy_units = None

        self.attack_range = 5
        self.start_range = 9
        self.start_path = [(2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (2, 10), (2, 11), (2, 12), (2, 13), (3, 13), (4, 13), (4, 12), (4, 11), (4, 10), (4, 9), (4, 8), (4, 7), (4, 6), (4, 5), (4, 4)]
        self.first_round = True
        self.death_buffer = 3
        self.first_round_turn_limit = 20
        self.lock_target = False

    def do_move(self, world, friendly_unit, enemy_units):
        '''
        This method is called every turn by the game engine.
        Make sure you call friendly_unit.move(target) somewhere here!

        Below, you'll find a very rudimentary strategy to get you started.
        Feel free to use, or delete any part of the provided code - Good luck!

        :param world: world object (more information on the documentation)
            - world: contains information about the game map.
            - world.path: contains various pathfinding helper methods.
            - world.util: contains various tile-finding helper methods.
            - world.fill: contains various flood-filling helper methods.

        :param friendly_unit: FriendlyUnit object
        :param enemy_units: list of EnemyUnit objects
        '''
        self.update_members(world, friendly_unit, enemy_units)

        # strategy for beginning of game
        if self.first_round:
            self.first_round_strat()
        else:

            # if enemy body is near us, kill them!
            self.kill_enemy()

            # if unit reaches the target point, reverse outbound boolean and set target back to None
            if self.target is not None and friendly_unit.position == self.target.position:
                self.outbound = not self.outbound
                self.target = None

            # if outbound and no target set, set target as the closest capturable tile at least 1 tile away from your territory's edge.
            if self.outbound and self.target is None:
                edges = [tile for tile in world.util.get_friendly_territory_edges()]
                avoid = []
                for edge in edges:
                    avoid += [pos for pos in world.get_neighbours(edge.position).values()]
                self.target = world.util.get_closest_capturable_territory_from(friendly_unit.position, avoid)

            # else if inbound and no target set, set target as the closest friendly tile
            elif not self.outbound and self.target is None:
                self.target = world.util.get_closest_friendly_territory_from(friendly_unit.position, None)

        # set next move as the next point in the path to target
        if self.target.position in self.friendly_unit.snake:
            print("Recalculating target...")
            self.target = world.util.get_closest_capturable_territory_from(friendly_unit.position, None)
        next_move = world.path.get_shortest_path(friendly_unit.position, self.target.position, friendly_unit.snake)[0]
        friendly_unit.move(next_move)

        self.print_log()
        self.turn_count += 1
        self.lock_target = False

    def update_members(self, world, friendly_unit, enemy_units):
        self.world = world
        self.friendly_unit = friendly_unit
        self.enemy_units = enemy_units


    def first_round_strat(self):
        if self.is_enabled():
            closest_friendly_territory = self.world.util.get_closest_friendly_territory_from(self.friendly_unit.position, None)
            min_turns_until_killed = 100
            for unit in self.enemy_units:
                closest_friendly_body = self.world.util.get_closest_friendly_body_from(unit.position, None)
                if closest_friendly_body:
                    min_turns_until_killed = min(min_turns_until_killed, self.world.path.get_taxi_cab_distance(closest_friendly_body.position, unit.position))
            min_turns_to_friendly_territory = self.world.path.get_taxi_cab_distance(closest_friendly_territory.position, self.friendly_unit.position)

            # check if we need to retreat to not get killed, or if stayed out for too long
            if min_turns_until_killed < self.death_buffer + min_turns_to_friendly_territory or \
               self.turn_count > self.first_round_turn_limit:
                if closest_friendly_territory.position in self.world.get_neighbours(self.friendly_unit.position).values():
                    self.first_round = False
                self.target = closest_friendly_territory
                self.outbound = False

            # otherwise freely gather territory!
            else:
                self.outbound = True
                inc = (0,1) if self.turn_count % 2 else (1, 0)
                self.target = self.world.position_to_tile_map[add_points(self.friendly_unit.position, inc)]
                # self.target = self.world.util.get_closest_capturable_territory_from(self.friendly_unit.position, None)

    def kill_enemy(self):
        if self.is_enabled():
            closest_enemy_body = self.world.util.get_closest_enemy_body_from(self.friendly_unit.position, None)
            if closest_enemy_body and self.world.path.get_taxi_cab_distance(closest_enemy_body.position, self.friendly_unit.position) <= self.attack_range:
                print ("Spotted enemy body!")
                self.target = closest_enemy_body
                self.lock_target = True


    def print_log(self):
       print("Turn {0}: currently at {1}, making {2} move to {3}.".format(
            str(self.turn_count),
            str(self.friendly_unit.position),
            'outbound' if self.outbound else 'inbound',
            str(self.target)
        ))

    def is_enabled(self):
        return (self.friendly_unit.status != 'DISABLED') and not (self.lock_target)
