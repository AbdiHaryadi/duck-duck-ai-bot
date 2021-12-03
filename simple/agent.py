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
action_queue = []

# For multiagent
action_queues = {}
action_states = {}

def agent(observation, configuration):
    global game_state
    global action_state
    global border_list
    global action_queue
    global action_queues
    global action_states

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
    if action_state == "INITIALIZE":
        border_list = scan_initial_border(game_state, resource_tiles)
        # Debug border_list
        annotate_actions += [annotate.x(c.pos.x, c.pos.y) for c in border_list]
        annotate_actions.append(annotate.sidetext("Border length: " + str(len(border_list))))
        action_state = "NOT INITIALIZE"
        
    for worker in player.units:
        # Assume no cart
        if worker.id not in action_queues:
            action_queues[worker.id] = []
            
        if worker.id not in action_states:
            # Tentukan role pertama dari worker baru
            action_states[worker.id] = "FARM"
        
        while len(action_queues[worker.id]) == 0 and worker.can_act():
            # Debug
            annotate_actions.append(annotate.sidetext("{}: {}".format(worker.id, action_states[worker.id])))
            
            if action_states[worker.id] == "FARM":
                action = farming(game_state, player, worker, resource_tiles)
                if action == None:
                    action_states[worker.id] = "BUILD"
                else:
                    action_queues[worker.id] += action
                    
            elif action_states[worker.id] == "BUILD":
                action = building(game_state, worker, border_list)
                if action == None or action == "GO_FARMING":
                    # Debug border_list
                    # TODO: Jangan panggil terus kalau sudah banyak worker
                    annotate_actions += [annotate.x(c.pos.x, c.pos.y) for c in border_list]
                    annotate_actions.append(annotate.sidetext("Border length: " + str(len(border_list))))
                    
                    action_states[worker.id] = "FARM"
                else:
                    action_queues[worker.id] += action
                    
            else:
                raise ValueError("action_state invalid: {}".format(action_states[worker.id]))
    
        if len(action_queues[worker.id]) > 0 and worker.can_act():
            new_action = action_queues[worker.id].pop(0)
            actions.append(new_action)
            annotate_actions.append(annotate.sidetext(new_action))
            annotate_actions.append(annotate.sidetext("{}: Queue length: {}".format(worker.id, len(action_queues[worker.id]))))
    
    actions += annotate_actions
    
    # Do your bot
    return actions
