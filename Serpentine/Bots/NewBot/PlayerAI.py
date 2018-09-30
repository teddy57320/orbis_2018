from PythonClientAPI.game.PointUtils import *
from PythonClientAPI.game.Entities import FriendlyUnit, EnemyUnit, Tile
from PythonClientAPI.game.Enums import Team, Direction
from PythonClientAPI.game.World import World
from PythonClientAPI.game.TileUtils import TileUtils
from PythonClientAPI.game.PathFinder import PathFinder

import numpy as np 


class PlayerAI:

    def __init__(self):
        ''' Initialize! '''
        self.turn_count = 0             # game turn count
        self.target = None              # target to send unit to!
        self.outbound = True            # is the unit leaving, or returning?\
        self.move = None

        # map attributes 
        self.width = 30
        self.height = 30 
        self.distance_norm = np.power(self.width ** 2 + self.height ** 2 , 0.5)
        self.path_finder = PathFinder(None)

        # energy field 
        self.field = np.zeros((self.width, self.height))
        # field value heuristics 
        self.enemy_head_val = -100 
        self.enemy_head_buffer_val = -50
        self.enemy_body_val = 20
        self.enemy_body_buffer_val = 10
        self.enemy_head_discount = 0.9
        self.enemy_body_discount = 0.65

        self.friend_edge_val = 10
        self.friend_body_val = -200

        self.enemy_region_val = 30
        self.friend_region_val = 10
        self.neutral_region_val = 20

        with open("field.txt", 'w'):
            print('clear...')


    def get_valid_neighbor_coords(self, world, cur_coord):
        """ get valid neighbor point coordinates from current tile coordinate
        """
        neighbor_coords = list(world.get_neighbours(cur_coord).values())
        neighbor_coords = [coord for coord in neighbor_coords if not world.is_wall(coord)]
        return neighbor_coords


    def attractor_func(self, distance):
        """ function to scale friend-zone attraction based on current distance 
        """
        return np.power(distance / self.distance_norm, 4.0) + 1


    def replusor_func(self, distance):
        """ function to scale friend-zone rejection :( 
        """
        return 1.0 / (distance / float(self.distance_norm))


    def update_field(self, world, friendly_unit, enemy_units):
        """ use heuristic to evaluate energy field 
        """
        for coord, tile in world.position_to_tile_map.items():
            # update base energy (from tile type)
            if tile.is_neutral:
                self.field[coord] = self.neutral_region_val
            elif tile.is_friendly:
                self.field[coord] = self.friend_region_val
            else:
                self.field[coord] = self.enemy_region_val

            # thread from colliding to my own body 
            for friend_body_coord in friendly_unit.body:
                if friend_body_coord != coord:
                    distance = self.path_finder.get_taxi_cab_distance(coord, friend_body_coord)
                    self.field[coord] += -self.friend_body_val * self.replusor_func(distance)

            # threat from enemy heads 
            for enemy in enemy_units:
                # higher-level threat from enemy head 
                distance = self.path_finder.get_taxi_cab_distance(coord, enemy.position)
                self.field[coord] += self.enemy_head_val * np.power(self.enemy_head_discount, distance)
                # neighbor = self.get_valid_neighbor_coords(world, enemy.position)
                # for coord in neighbor:
                #     self.field[coord] += self.enemy_head_buffer_val

                # threat from enemy body 
                for enemy_body_coord in enemy.body:
                    distance = self.path_finder.get_taxi_cab_distance(coord, enemy_body_coord)
                    self.field[coord] += self.enemy_body_val * np.power(self.enemy_body_discount, distance)
                    # neighbor = self.get_valid_neighbor_coords(world, enemy_body_coord)
                    # for coord in neighbor:
                    #     self.field[coord] += self.enemy_body_buffer_val

            # attraction from friend territories 
            edge_coords = [tile.position for tile in world.util.get_friendly_territory_edges()]
            for edge_coord in edge_coords:
                distance = self.path_finder.get_taxi_cab_distance(coord, edge_coord)
                self.field[coord] += self.friend_edge_val * self.attractor_func(distance) 


    def log_field(self):
        """ print energy to text file 
        """
        f = open("field.txt", 'a')
        print('energy field ', file=f)
        for i in range(len(self.field)):
            for j in range(len(self.field[0])):
                print("%.2f " % self.field[i][j], file=f, end='')
            print('\n', file=f)
        print('\n\n', file=f)
        f.close()


    def sum_region_potential(self, coord1, coord2):
        """ summ up potential of a retecgula region specified by the diagonal coordinates 
        """
        return np.sum(self.field[coord1[0]:coord2[0]+1, coord1[1]:coord2[1]+1])


    def get_ascent_direction(self, world, friendly_unit):
        """ get move direction based on ascendig the energy field 
        """
        directions = []
        coord = friendly_unit.position
        neighbors = world.get_neighbours(coord)
        for direc, next_coord in neighbors.items():
            if world.is_wall(next_coord) or next_coord in friendly_unit.body:
                continue 
            # up 
            if direc == Direction.NORTH:
                energy_sum = self.sum_region_potential((1, 1), (coord[0]-1, self.width-2))
            # down 
            elif direc == Direction.SOUTH:
                energy_sum = self.sum_region_potential((coord[0]+1, 1), (self.width-2, self.height-2))
            # left 
            elif direc == Direction.WEST:
                energy_sum = self.sum_region_potential((1, 1), (self.height-2, coord[1]-1))
            # right 
            elif direc == Direction.EAST:
                energy_sum = self.sum_region_potential((1, coord[1]+1), (self.width-2, self.height-2))
            directions.append((direc, energy_sum, next_coord))
        # pick best direction       
        best_move = sorted(directions, key=lambda x: x[1], reverse=True)[0]
        return best_move[-1]


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

        # increment turn count
        self.turn_count += 1
        self.path_finder.world = world 
        self.update_field(world, friendly_unit, enemy_units)
        self.log_field()

        # if unit is dead, stop making moves.
        if friendly_unit.status == 'DISABLED':
            print("Turn {0}: Disabled - skipping move.".format(str(self.turn_count)))
            self.target = None
            self.outbound = True
            return

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
        next_move = world.path.get_shortest_path(friendly_unit.position, self.target.position, friendly_unit.snake)[0]
        # select move based on energy field 
        next_move = self.get_ascent_direction(world, friendly_unit)
        

        # move!
        friendly_unit.move(next_move)
        print("Turn {0}: currently at {1}, making {2} move to {3}.".format(
            str(self.turn_count),
            str(friendly_unit.position),
            'outbound' if self.outbound else 'inbound',
            str(self.target.position)
        ))
