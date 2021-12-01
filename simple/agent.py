import math, sys
from lux.game import Game
from lux.game_map import Cell, RESOURCE_TYPES, Position
from lux.constants import Constants
from lux.game_constants import GAME_CONSTANTS
from lux import annotate
from lux.game_objects import CityTile
import random

from Pathfinder import Pathfinder

DIRECTIONS = Constants.DIRECTIONS
game_state = None
pathfinder = Pathfinder()
next_actions = []
target = None
current_subtarget = None

clusters = []

wood_pos = []
annotate_actions = []
initialized = False

def agent(observation, configuration):
    global game_state
    global pathfinder
    global next_actions
    global target
    global current_subtarget
    global initialized
    # global annotate_actions
    global wood_pos
    global clusters

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
    if not initialized:
        wood_pos = [[False for _ in range(height)] for _ in range(width)]
        for y in range(height):
            for x in range(width):
                cell = game_state.map.get_cell(x, y)
                if cell.has_resource():
                    if cell.resource.type == Constants.RESOURCE_TYPES.WOOD:
                        for i in range(-1, 2):
                            for j in range(-1, 2):
                                wood_pos[min(max(0, i + x), width - 1)][min(max(0, j + y), height - 1)] = True
        # Remove the inner
        inner_wood_pos = [[False for _ in range(height)] for _ in range(width)]
        for y in range(height):
            for x in range(width):
                unmark = True
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        unmark = wood_pos[min(max(0, i + x), width - 1)][min(max(0, j + y), height - 1)]
                        if not unmark:
                            break
                        
                    if not unmark:
                        break
                        
                inner_wood_pos[x][y] = unmark
                
        for y in range(height):
            for x in range(width):
                if inner_wood_pos[x][y]:
                    wood_pos[x][y] = False
        
        # Get clusters 
        for y in range(height):
            for x in range(width):
                if wood_pos[x][y]:
                    cluster = []
                    x1 = x
                    y1 = y
                    
                    # Check whether this is a loop or not
                    while wood_pos[x1][y1]:
                        cluster.append(Position(x1, y1))
                        wood_pos[x1][y1] = False
                        
                        # Next element
                        next_element_detected = False
                        if x1 > 0:
                            if wood_pos[x1 - 1][y1]:
                                x1 -= 1
                                next_element_detected = True
                        
                        if not next_element_detected and x1 < width - 1:
                            if wood_pos[x1 + 1][y1]:
                                x1 += 1
                                next_element_detected = True
                                
                        if not next_element_detected and y1 > 0:
                            if wood_pos[x1][y1 - 1]:
                                y1 -= 1
                                next_element_detected = True
                                
                        if not next_element_detected and y1 < height - 1:
                            if wood_pos[x1][y1 + 1]:
                                y1 += 1
                                next_element_detected = True
                                
                        if not next_element_detected and x > 0:
                            if wood_pos[x - 1][y]:
                                x1 = x - 1
                                y1 = y
                                next_element_detected = True
                        
                        if not next_element_detected and x < width - 1:
                            if wood_pos[x + 1][y]:
                                x1 = x + 1
                                y1 = y
                                next_element_detected = True
                                
                        if not next_element_detected and y > 0:
                            if wood_pos[x][y - 1]:
                                x1 = x
                                y1 = y - 1
                                next_element_detected = True
                                
                        if not next_element_detected and y < height - 1:
                            if wood_pos[x][y + 1]:
                                x1 = x
                                y1 = y + 1
                                next_element_detected = True
                                
                    clusters.append(cluster)

    
    random_cluster = random.choice(clusters)
    annotate_actions = []
    for y in range(height):
        for x in range(width):
            if Position(x, y) in random_cluster:
                annotate_actions.append(annotate.circle(x, y))
    
    initialized = True

    
    resource_tiles: list[Cell] = []
    for y in range(height):
        for x in range(width):
            cell = game_state.map.get_cell(x, y)
            if cell.has_resource():
                resource_tiles.append(cell)
    
    """
    # we iterate over all our units and do something with them
    for unit in player.units:
        if unit.is_worker() and unit.can_act():
            closest_dist = math.inf
            closest_resource_tile = None
            if unit.get_cargo_space_left() > 0:
                # if the unit is a worker and we have space in cargo, lets find the nearest resource tile and try to mine it
                for resource_tile in resource_tiles:
                    if resource_tile.resource.type == Constants.RESOURCE_TYPES.COAL and not player.researched_coal(): continue
                    if resource_tile.resource.type == Constants.RESOURCE_TYPES.URANIUM and not player.researched_uranium(): continue
                    dist = resource_tile.pos.distance_to(unit.pos)
                    if dist < closest_dist:
                        closest_dist = dist
                        closest_resource_tile = resource_tile
                if closest_resource_tile is not None:
                    actions.append(unit.move(unit.pos.direction_to(closest_resource_tile.pos)))
            else:
                # if unit is a worker and there is no cargo space left, and we have cities, lets return to them
                if len(player.cities) > 0:
                    closest_dist = math.inf
                    closest_city_tile = None
                    for k, city in player.cities.items():
                        for city_tile in city.citytiles:
                            dist = city_tile.pos.distance_to(unit.pos)
                            if dist < closest_dist:
                                closest_dist = dist
                                closest_city_tile = city_tile
                    if closest_city_tile is not None:
                        move_dir = unit.pos.direction_to(closest_city_tile.pos)
                        actions.append(unit.move(move_dir))
    """
    
    if len(player.units) > 0:
        unit = player.units[0]
        if unit.is_worker() and unit.can_act():
            if len(next_actions) == 0:
                if not isinstance(target, Position):
                    target = Position(random.randint(0, width - 1), random.randint(0, height - 1))
                while unit.pos == target or isinstance(game_state.map.get_cell_by_pos(target).citytile, CityTile):
                    target = Position(random.randint(0, width - 1), random.randint(0, height - 1))
            
                #next_actions = pathfinder.find_path(game_state, unit, target)
            
                def resource_needed(target):
                    # Count feasible of path
                    distance_to_target = unit.pos.distance_to(target)
                    """
                    resource_needed = 0
                    turn = game_state.turn
                    while distance_to_target > 0:
                        if turn % 40 < 30:
                            delta = (30 - turn) % 40
                            turn += delta
                            distance_to_target -= delta / 2
                        else:
                            delta = min((40 - turn) % 40, distance_to_target)
                            turn += delta
                            distance_to_target -= delta / 4
                            resource_needed += 4 * delta
                    """
                    
                    turn = game_state.turn
                    if turn % 40 < 30:
                        day_turn = min((30 - turn) % 40, distance_to_target)
                        return (distance_to_target - day_turn) * 16
                    else:
                        night_turn = min((40 - turn) % 40, distance_to_target)
                        distance_to_target -= night_turn
                        day_turn = min(30, distance_to_target)
                        distance_to_target -= day_turn
                        return (night_turn + distance_to_target) * 16
                
                """
                target_resource = resource_needed(target)
                if target_resource < unit.cargo.wood:
                    current_subtarget = None
                    next_actions = pathfinder.find_path(game_state, unit, target)
                else:
                    subtarget_candidates = list(map(
                        lambda r: r.pos,
                        filter(
                            lambda r: r.resource.type == Constants.RESOURCE_TYPES.WOOD,
                            resource_tiles
                        )
                    ))
                    random.shuffle(subtarget_candidates)
                    
                    current_subtarget = min(
                        subtarget_candidates,
                        key=lambda p: (p.distance_to(unit.pos) + p.distance_to(target) + 1) * (1 if resource_needed(p) < unit.cargo.wood else 9999)
                    )
                    
                    next_actions = pathfinder.find_path(game_state, unit, current_subtarget)
                """
                next_actions = pathfinder.find_path(game_state, unit, target)
                
            
            if len(next_actions) > 0:
                actions.append(next_actions.pop(0))
                
        actions.append(annotate.circle(target.x, target.y))
        if isinstance(current_subtarget, Position):
            actions.append(annotate.x(current_subtarget.x, current_subtarget.y))
            actions.append(annotate.line(unit.pos.x, unit.pos.y, current_subtarget.x, current_subtarget.y))
        else:
            actions.append(annotate.line(unit.pos.x, unit.pos.y, target.x, target.y))
        
    # you can add debug annotations using the functions in the annotate object
    # actions.append(annotate.circle(0, 0))
    
    return actions # + annotate_actions
