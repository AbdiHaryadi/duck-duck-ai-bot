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
from util.go_to_city import go_to_city

DIRECTIONS = Constants.DIRECTIONS
game_state = None
action_state = "INITIALIZE"
border_list = []
action_queue = []

# For multiagent
action_queues = {}
action_states = {}
action_data = {} # Dictionary of dictionary

def agent(observation, configuration):
    global game_state
    global action_state
    global border_list
    global action_queue
    global action_queues
    global action_states
    global action_data

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
    # No replay: lux-ai-2021 main.py main.py --out=replay.json --storeLogs=false --storeReplay=false
    
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
            
        if worker.id not in action_data:
            action_data[worker.id] = {}
        
        while len(action_queues[worker.id]) == 0 and worker.can_act():
            # Debug
            annotate_actions.append(annotate.sidetext("{}: {}".format(worker.id, action_states[worker.id])))
            
            if action_states[worker.id] == "FARM":
                action = farming(game_state, player, worker, resource_tiles)
                if action == None:
                    need_fuel_cities = list(player.cities.values())
                    if len(need_fuel_cities) > 0:
                        action_data[worker.id]["cityid"] = need_fuel_cities[0].cityid
                        action_states[worker.id] = "REFUEL"
                    else:
                        action_queues[worker.id].append(annotate.sidetext("Do nothing"))
                else:
                    action_queues[worker.id] += action
                    
            elif action_states[worker.id] == "REFUEL":
                if action_data[worker.id]["cityid"] in player.cities:
                    city = player.cities[action_data[worker.id]["cityid"]]
                    refuel_actions = go_to_city(game_state, worker, city)
                    if len(refuel_actions) > 0:
                        action_queues[worker.id] += refuel_actions
                    else:
                        action_states[worker.id] = "FARM"
                        
                else:
                    action_states[worker.id] = "FARM"
            else:
                raise ValueError("action_state invalid: {}".format(action_states[worker.id]))
    
        if len(action_queues[worker.id]) > 0 and worker.can_act():
            new_action = action_queues[worker.id].pop(0)
            actions.append(new_action)
            annotate_actions.append(annotate.sidetext(new_action))
    
    actions += annotate_actions
    
    # Do your bot
    return actions
