from PythonClientAPI.game.PointUtils import *
from PythonClientAPI.game.Entities import FriendlyUnit, EnemyUnit, Tile
from PythonClientAPI.game.Enums import Team, Direction
from PythonClientAPI.game.World import World
from PythonClientAPI.game.TileUtils import TileUtils
from PythonClientAPI.game.PathFinder import PathFinder
from PythonClientAPI.structures.Collections import PriorityQueue, Queue

import numpy as np 

class PlayerAI:

    def __init__(self):

        self.turn_count = 0
        self.target = None
        self.outbound = True
        self.idle = False
        self.move = None

        # store the inputs every cycle
        self.world = None
        self.friendly_unit = None
        self.enemy_units = None

        # To be initialized on turn 0 only
        self.early_game_incs = None
        self.direction_preference = None
        self.map_edges = None

        # constants used in decision making
        self.expansion_depth = 5
        self.attack_range = 2
        self.early_game = True
        self.death_buffer = 3
        self.early_game_turn_limit = 17
        self.lock_target = False
        self.width = 30
        self.height = 30 

    def initialize_params(self):

        ''' Initialize time-invariant properties based on the given world object
        '''

        ''' Initialize properties based on starting location '''

        # top left
        if self.friendly_unit.position == (3, 3):
            self.early_game_incs = ((0,1), (1,0))
            self.direction_preference = [Direction.WEST, Direction.SOUTH, Direction.NORTH, Direction.EAST]

        # bottom left
        elif self.friendly_unit.position == (3, self.height-4):
            self.early_game_incs = ((0,-1), (1,0))
            self.direction_preference = [Direction.WEST, Direction.NORTH, Direction.SOUTH, Direction.EAST]

        # top right
        elif self.friendly_unit.position == (self.width-4, 3):
            self.early_game_incs = ((0,1), (-1,0))
            self.direction_preference = [Direction.EAST, Direction.SOUTH, Direction.NORTH, Direction.WEST]

        # bottom right
        elif self.friendly_unit.position == (self.width-4, self.height-4):
            self.early_game_incs = ((0,-1), (-1,0))
            self.direction_preference = [Direction.EAST, Direction.NORTH, Direction.SOUTH, Direction.WEST]

        # Get the edges of the map
        self.map_edges = [(x, y) for x in range(1, self.width-1) for y in range(1, self.height-1) \
                                  if self.world.is_edge((x,y))]


    def my_get_shortest_path(self, start, end, avoid):
        """ Refactoring of provided get_shortest_path function to prioritize going in a certain direction
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
            for direction in self.direction_preference:
                neighbour = neighbours[direction]
                if self.world.is_wall(neighbour) or (avoid and (neighbour in avoid)):
                    continue
                cost = movement_costs[current] + 1
                if (neighbour not in movement_costs) or (cost < movement_costs[neighbour]):
                    movement_costs[neighbour] = cost
                    queue.add(neighbour,
                              cost + self.world.path.get_taxi_cab_distance(neighbour, end))
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

    def get_valid_neighbor_coords(self, cur_coord):
        """ get valid neighbor point coordinates from current tile coordinate
        """
        neighbor_coords = list(self.world.get_neighbours(cur_coord).values())
        neighbor_coords = [coord for coord in neighbor_coords if not self.world.is_wall(coord)]
        return neighbor_coords

    def update_members(self, world, friendly_unit, enemy_units):
        """ called on every turn - updates the class members in an FSM style
        """
        self.world = world
        self.friendly_unit = friendly_unit
        self.enemy_units = enemy_units

        # previously locked on target is already gone
        if self.lock_target and self.world.position_to_tile_map[self.target.position].body is None:
            self.lock_target = False


        # reset if disabled
        if self.friendly_unit.status == 'DISABLED':
            self.outbound = False
            self.idle = True
            self.lock_target = False
        else:

            # finished first expansion
            if (not self.outbound) and self.world.position_to_tile_map[friendly_unit.position].is_friendly:
                self.early_game = False

            # finished an expansion, waiting for next task
            if not self.outbound and self.world.position_to_tile_map[self.friendly_unit.position].is_friendly:
                self.outbound = False
                self.idle = True

            # finished killing locked on target
            if self.target and self.friendly_unit.position == self.target.position and self.lock_target:
                self.lock_target = False

    def get_territory_edge_ranking(self):
        ''' returns a list of friendly territory positions, from closest to farthest
        '''
        return sorted(self.world.util.get_friendly_territory_edges(), 
                      key = lambda x : self.world.path.get_taxi_cab_distance(x.position, self.friendly_unit.position))

    def get_min_turns_until_killed(self):
        ''' calculates the number of turns that it will take for an enemy to kill friendly snake
        '''
        min_turns_until_killed = 100
        for unit in self.enemy_units:
            closest_friendly_body = self.world.util.get_closest_friendly_body_from(unit.position, None)
            if closest_friendly_body:
                min_turns_until_killed = min(min_turns_until_killed, self.world.path.get_taxi_cab_distance(closest_friendly_body.position, unit.position))
        return min_turns_until_killed

    def general_expansion(self):
        ''' This is generally what the friendly snake will be doing if no special circumstance arises
        '''
        if self.is_enabled() and not self.escaping:

            # Finished expanding, time to head back to friendly territory
            if self.friendly_unit.position == self.target.position and self.outbound:
                self.outbound = False
                edge_ranking = self.get_territory_edge_ranking()
                self.target = edge_ranking[3]
                self.idle = False

            # Just returned to friendly territory, should find more space to explore
            elif not self.outbound and self.idle:
                edges = self.world.util.get_friendly_territory_edges()
                temp = [edge.position for edge in edges]
                for i in range(self.expansion_depth):
                    avoid = []
                    for pos in temp:
                        avoid += [p for p in self.get_valid_neighbor_coords(pos) \
                                  if not self.world.position_to_tile_map[p].is_friendly] + [pos]
                    temp = avoid
                self.outbound = True
                self.target = self.world.util.get_closest_capturable_territory_from(self.friendly_unit.position, avoid + self.map_edges)
                self.idle = False

    def defend_body(self):
        ''' Detects if enemy snake comes too close to a friendly body, in which case retreat to friendly territory
        '''
        if not self.lock_target:
            closest_friendly_territory = self.world.util.get_closest_friendly_territory_from(self.friendly_unit.position, None)
            min_turns_until_killed = self.get_min_turns_until_killed()
            min_turns_to_friendly_territory = self.world.path.get_taxi_cab_distance(closest_friendly_territory.position, self.friendly_unit.position)
            if min_turns_until_killed < self.death_buffer + min_turns_to_friendly_territory:
                print('Escaping enemy...')
                if self.outbound:
                    self.target = closest_friendly_territory
                self.escaping = True
                self.outbound = False
            else:
                self.escaping = False

    def early_game_strat(self):
        ''' Strategy for the first few turns - aggressively gathers territory and run if necessary
        '''
        if self.is_enabled():
            closest_friendly_territory = self.world.util.get_closest_friendly_territory_from(self.friendly_unit.position, None)
            min_turns_until_killed = self.get_min_turns_until_killed()
            min_turns_to_friendly_territory = self.world.path.get_taxi_cab_distance(closest_friendly_territory.position, self.friendly_unit.position)

            # check if we need to retreat to not get killed, or if stayed out for too long
            if min_turns_until_killed < self.death_buffer + min_turns_to_friendly_territory:
                print('Escaping enemy...')
                if self.outbound:
                    self.target = closest_friendly_territory
                self.escaping = True
                self.outbound = False

            elif self.turn_count > self.early_game_turn_limit:
                print('Inbounding...')
                if self.outbound or self.escaping:
                    edge_ranking = self.get_territory_edge_ranking()
                    furthest_x = max([tile.position[0] for tile in edge_ranking], key=lambda x: abs(self.friendly_unit.position[0] - x))
                    self.target = next(tile for tile in edge_ranking if tile.position[0] == furthest_x)
                    self.escaping = False
                self.outbound = False

            # otherwise freely gather territory!
            else:
                print('Expanding....')
                self.outbound = True
                inc = self.early_game_incs[0] if int(self.turn_count / 2) % 2 else self.early_game_incs[1]
                self.target = self.world.position_to_tile_map[add_points(self.friendly_unit.position, inc)]

    def kill_enemy(self):
        ''' Check if a kill is possible/safe, and initiate them appropriately
        '''
        if self.is_enabled():

            # check for enemy head
            closest_enemy_head = self.world.util.get_closest_enemy_head_from(self.friendly_unit.position, None)
            dist_from_enemy = self.world.path.get_taxi_cab_distance(closest_enemy_head.position, self.friendly_unit.position)

            # must fight
            if dist_from_enemy == 1:
                print ("Spotted enemy head!")
                self.target = closest_enemy_head
                self.lock_target = True
                return

            # check for enemy body
            closest_enemy_body = self.world.util.get_closest_enemy_body_from(self.friendly_unit.position, None)
            if closest_enemy_body:
                dist_from_enemy = self.world.path.get_taxi_cab_distance(closest_enemy_body.position, self.friendly_unit.position)
                closest_safety = self.world.util.get_closest_territory_by_team(closest_enemy_body.position, closest_enemy_body.body, None)
                enemy_dist_from_safety = self.world.path.get_taxi_cab_distance(closest_enemy_head.position, closest_safety.position)
                if (dist_from_enemy <= self.attack_range and enemy_dist_from_safety > self.attack_range) or dist_from_enemy < 2:
                    print ("Hunting enemy body!")
                    self.target = closest_enemy_body
                    self.lock_target = True

            # return to idle state after killing
            if dist_from_enemy == 1:
                self.outbound = False

    def print_log(self):
       print("Turn {0}: currently at {1}, making {2} move to {3}.".format(
            str(self.turn_count),
            str(self.friendly_unit.position),
            'outbound' if self.outbound else 'inbound',
            str(self.target)))

    def is_enabled(self):
        ''' Don't want any more computation to happen if we are locking in on an enemy
            or if we are disabled
        '''
        return (self.friendly_unit.status != 'DISABLED') and not (self.lock_target)

    def do_move(self, world, friendly_unit, enemy_units):

        self.update_members(world, friendly_unit, enemy_units)

        if (self.turn_count == 0):
            self.initialize_params()

        ''' Separate strategy into early game and mid/late game '''
        if self.early_game:
            self.early_game_strat()
            next_move = self.my_get_shortest_path(self.friendly_unit.position, self.target.position, self.friendly_unit.snake)
            if not next_move:
                print('Path finding failed, resorting to default move...')
                next_move = self.my_get_shortest_path(self.friendly_unit.position, self.early_game_incs[2], self.friendly_unit.snake)

        else:
            # if enemy body is near us, abort current task and kill!
            self.kill_enemy()

            # defend and retreat if necessary
            self.defend_body()

            # if nothing special is happening, just casually expand
            self.general_expansion()

            # print (self.friendly_unit.position, self.target.position, self.outbound, self.idle)
            next_move = self.world.path.get_shortest_path(self.friendly_unit.position, self.target.position, self.friendly_unit.snake)

            # somtimes an empty list is given from shortest path finder...
            if not next_move:
                print('Path finding failed, resorting to default move...')
                next_move = self.world.path.get_shortest_path(self.friendly_unit.position,
                                                                self.world.util.get_closest_friendly_territory_from(self.friendly_unit.position),
                                                                self.friendly_unit.snake)
        self.friendly_unit.move(next_move[0])

        self.print_log()
        self.turn_count += 1