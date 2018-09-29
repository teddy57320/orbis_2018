import os
import sys
import json
import importlib
import imp

from PythonClientAPI.comm.ClientHandlerProtocol import *
import PythonClientAPI.config.Constants as constants
import PythonClientAPI.comm.CommunicationConstants as cc
from PythonClientAPI.game.JSON import parse_config


class Unbuffered(object):
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)


if __name__ == '__main__':
    sys.stdout = Unbuffered(sys.stdout)
    sys.stderr = Unbuffered(sys.stderr)
    UUIDForAi = ""

    sys.argv.pop(0)

    cwd = os.getcwd() + "/"
    config_name = ''
    player_index = -1

    for i in range(int(len(sys.argv) / 2)):
        if sys.argv[i * 2] == "-c":
            config_name = sys.argv[i * 2 + 1]
        elif sys.argv[i * 2] == "-d":
            player_index = int(sys.argv[i * 2 + 1])
        elif sys.argv[i * 2] == "-u":
            constants.LOCAL_PLAYER_UUID = sys.argv[i * 2 + 1]
        elif sys.argv[i * 2] == "-cp":
            constants.PLAYER_AI_PATH = sys.argv[i * 2 + 1]

    if player_index == -1:
        if constants.LOCAL_PLAYER_UUID == "Red":
            player_index = 0
        elif constants.LOCAL_PLAYER_UUID == "Blue":
            player_index = 1
        elif constants.LOCAL_PLAYER_UUID == "Green":
            player_index = 2
        elif constants.LOCAL_PLAYER_UUID == "Purple":
            player_index = 3
        else:
            print(
                "Player UUID (-u parameter) was neither Red, Blue, Green nor Purple, and the player index (-d parameter) was not specified.")
            sys.exit(0)

    file = open(cwd + 'MatchPresets/' + config_name + ".json", 'r')

    parse_config(file.read(), player_index)

    try:
        sys.path.append(constants.PLAYER_AI_PATH)
        tempString = constants.PLAYER_AI_PATH
        while ('\\' in tempString):
            sys.path.append(tempString[:tempString.rindex('\\')])
            tempString = tempString[:tempString.rindex('\\')]
    except:
        pass

    UUIDForAi = constants.LOCAL_PLAYER_UUID
    print("Welcome " + UUIDForAi)


    fp, pathname, description = imp.find_module('PlayerAI', [constants.PLAYER_AI_PATH])
    player_ai_module = imp.load_module('PlayerAI', fp, pathname, description)
    client_ai = player_ai_module.PlayerAI()
    client_handler_protocol = ClientHandlerProtocol(client_ai, cc.PORT_NUMBER, cc.MAXIMUM_ALLOWED_RESPONSE_TIME,
                                                    UUIDForAi)

    client_handler_protocol.start_communications()
