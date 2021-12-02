import math, sys
from lux.game import Game
from lux.game_map import Cell, RESOURCE_TYPES, Position
from lux.constants import Constants
from lux.game_constants import GAME_CONSTANTS
from lux import annotate
from lux.game_objects import CityTile
import random

from util.building import building
from util.farming import farming
from util.scan_initial_border import scan_initial_border
from util.update_border import update_border

DIRECTIONS = Constants.DIRECTIONS
game_state = None
action_state = "INITIALIZE"
border_list = []

def agent(observation, configuration):
    global game_state
    global action_state
    global border_list

    ### Do not edit ###
    if observation["step"] == 0:
        game_state = Game()
        game_state._initialize(observation["updates"])
        game_state._update(observation["updates"][2:])
        game_state.id = observation.player
    else:
        game_state._update(observation["updates"])
    
    actions = []

    ### AI Code goes down here! ### 
    player = game_state.players[observation.player]
    opponent = game_state.players[(observation.player + 1) % 2]
    width, height = game_state.map.width, game_state.map.height
    
    # lux-ai-2021 main.py main.py --out=replay.json
    
    resource_tiles: list[Cell] = []
    for y in range(height):
        for x in range(width):
            cell = game_state.map.get_cell(x, y)
            if cell.has_resource():
                resource_tiles.append(cell)
    
    annotate_actions = []
    while len(player.units) > 0 and len(actions) == 0:
        # Debug
        annotate_actions.append(annotate.sidetext(action_state))
        
        worker = player.units[0] # Assume is worker, ambil unit paling pertama
        if action_state == "INITIALIZE":
            border_list = scan_initial_border(game_state, worker, resource_tiles)
            # Debug border_list
            annotate_actions += [annotate.x(c.x, c.y) for c in border_list]
            annotate_actions.append(annotate.sidetext("Border length: " + str(len(border_list))))
            action_state = "FARM"
        
        elif action_state == "FARM":
            action = farming(game_state, player, worker, resource_tiles)
            if action == None:
                action_state = "BUILD"
            else:
                actions.append(action)
                
        elif action_state == "BUILD":
            action = building(game_state, worker, border_list)
            if action == None:
                # Update border
                border_list = update_border(game_state, border_list)
                action_state = "FARM"
            else:
                actions.append(action)
                
        else:
            raise ValueError("action_state invalid: {}".format(action_state))
            
    actions += annotate_actions
    
    # Do your bot
    return actions
