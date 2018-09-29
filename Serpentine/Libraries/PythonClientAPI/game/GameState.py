class GameState:
    def __init__(self, world, player_uuid_to_player_type_map, player_index_to_uuid_map, enemy_uuids):
        self.world = world
        self.player_uuid_to_player_type_map = player_uuid_to_player_type_map
        self.player_index_to_uuid_map = player_index_to_uuid_map
        self.enemy_uuids = enemy_uuids


class PlayerState:
    def __init__(self, friendly_unit):
        self.friendly_unit = friendly_unit
        self.friendly_territory = friendly_unit.territory
        self.friendly_body = friendly_unit.body
        self.friendly_status = friendly_unit.status


class MoveRequest:
    def __init__(self, uuid_to_core_map):
        self.uuid_to_core_map = uuid_to_core_map
