import json
import PythonClientAPI.config.Constants as constants
import PythonClientAPI.comm.CommunicationConstants as comm_constants
from PythonClientAPI.game.Entities import *
from PythonClientAPI.game.Enums import TileType, Team, Direction
from PythonClientAPI.game.GameState import *
from PythonClientAPI.game.World import World
from enum import Enum


def parse_config(jsn, player_index):
    dct = json.loads(jsn)
    constants.MAP_NAME = dct["mapName"]
    comm_constants.PORT_NUMBER = int(dct["portNumber"])
    comm_constants.MAXIMUM_ALLOWED_RESPONSE_TIME = int(dct["maxResponseTime"])


def parse_game_state(jsn, tiles):
    dct = json.loads(jsn)
    return as_game_state(dct, tiles)


def as_game_state(dct, tiles):
    player_uuid_to_player_type_map = {}
    enemy_units_map = {}
    enemy_uuids = []

    for uuid in dct['playerUUIDToPlayerTypeMap'].keys():
        if uuid == constants.LOCAL_PLAYER_UUID:
            player_state = as_friendly_player_state(dct['playerUUIDToPlayerTypeMap'][uuid])
            friendly_unit = player_state.friendly_unit
        else:
            player_state = as_enemy_player_state(dct['playerUUIDToPlayerTypeMap'][uuid])
            enemy_units_map[player_state.friendly_unit.team] = player_state.friendly_unit
            enemy_uuids.append(uuid)
        player_uuid_to_player_type_map[uuid] = player_state

    player_index_to_uuid_map = {player_index: dct['playerIndexToUUIDMap'][player_index]
                                for player_index in dct['playerIndexToUUIDMap'].keys()}

    world = World(tiles, friendly_unit, enemy_units_map)

    return GameState(world, player_uuid_to_player_type_map, player_index_to_uuid_map, enemy_uuids)


def as_friendly_player_state(dct):
    return PlayerState(as_friendly_unit(dct))


def as_enemy_player_state(dct):
    return PlayerState(as_enemy_unit(dct))


def as_friendly_unit(dct):
    if 'playerStatus' not in dct:
        status = ''
    else:
        status = dct['playerStatus']
    return FriendlyUnit(dct['playerUnit']['team'], dct['playerUnit']['uuid'], dct['playerUnit']['position'], status,
                        dct['playerTrace'], dct['playerTerritory'], dct['playerUnit']['turnPenalty'])


def as_enemy_unit(dct):
    if 'playerStatus' not in dct:
        status = ''
    else:
        status = dct['playerStatus']
    return EnemyUnit(dct['playerUnit']['team'], dct['playerUnit']['uuid'], dct['playerUnit']['position'], status,
                     dct['playerTrace'], dct['playerTerritory'], dct['playerUnit']['turnPenalty'])


def parse_tile_data(game_starting_state):
    dct = json.loads(game_starting_state)
    return as_tiles(dct["tiles"])


def as_tiles(lst):
    return [[TileType[tile] for tile in column] for column in lst]

class SPPEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.name
        if isinstance(obj, MoveRequest):
            return {'uuidToUnitCoreMap': {uuid: obj.uuid_to_core_map[uuid] for uuid in obj.uuid_to_core_map.keys()}}
        if isinstance(obj, FriendlyUnit):
            return {'team': obj.team, 'uuid': obj.uuid, 'nextMovePoint': tuple_to_point(obj.next_move_target)}
        return json.JSONEncoder.default(self, obj)


def tuple_to_point(tupl):
    if tupl is None:
        return None
    return {'x': tupl[0], 'y': tupl[1]}


def as_point_from_dct(dct):
    return tuple([dct['x'], dct['y']])