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
from util.TaskManager import TaskManager

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
    task_manager = TaskManager()

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
                    # Assume single agent need to handle city that nearest than all worker
                    need_fuel_cities = list(filter(lambda c: c.fuel <= (c.get_light_upkeep() + 23) * 10, player.cities.values()))
                    """
                    need_fuel_cities = list(filter(
                        lambda c: min(player.units, key=lambda u: min(
                            list(map(
                                lambda ct: u.pos.distance_to(ct.pos),
                                c.citytiles
                            ))
                        )).id == worker.id,
                        need_fuel_cities
                    ))
                    """
                    # Just take cities that near to worker
                    need_fuel_cities = list(filter(
                        lambda c: min(
                            list(map(
                                lambda ct: worker.pos.distance_to(ct.pos),
                                c.citytiles
                            ))
                        ) <= 2,
                        need_fuel_cities
                    ))
                    if len(need_fuel_cities) > 0:
                        # city_prio_func = lambda c: c.fuel / c.get_light_upkeep()
                        city_prio_func = lambda c: min(list(map(lambda ct: ct.pos.distance_to(worker.pos), c.citytiles)))
                        action_data[worker.id]["cityid"] = min(need_fuel_cities, key=city_prio_func).cityid
                        action_states[worker.id] = "REFUEL"
                    else:
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
                    
            elif action_states[worker.id] == "REFUEL":
                if action_data[worker.id]["cityid"] in player.cities:
                    city = player.cities[action_data[worker.id]["cityid"]]
                    refuel_actions = go_to_city(game_state, worker, city)
                    if len(refuel_actions) > 0:
                        action_queues[worker.id] += refuel_actions
                    elif game_state.turn % 40 >= 30: # night
                        action_states[worker.id] = "FARM"
                    else:
                        action_states[worker.id] = "FARM"
                        
                else:
                    action_states[worker.id] = "FARM"
            else:
                raise ValueError("action_state invalid: {}".format(action_states[worker.id]))
    
        if len(action_queues[worker.id]) > 0 and worker.can_act():
            new_action = action_queues[worker.id].pop(0)
            
            # USING TASK MANAGER
            # actions.append(new_action)
            task_manager.submit_action_unit(new_action)

            annotate_actions.append(annotate.sidetext(new_action))
            annotate_actions.append(annotate.sidetext("{}: Queue length: {}".format(worker.id, len(action_queues[worker.id]))))
    
    actions = task_manager.get_action_list()

    # Greedy build worker for test, two units only
    # Not good above 2 because it will be overwhelmed to maintain the city
    k = min(player.city_tile_count, 4) - len(player.units)
    for _, city in player.cities.items():
        for ct in city.citytiles:
            if ct.can_act():
                if k > 0:
                    actions.append(ct.build_worker())
                    k -= 1
                elif not player.researched_uranium():
                    actions.append(ct.research())
    
    actions += annotate_actions
    
    # Do your bot
    return actions
