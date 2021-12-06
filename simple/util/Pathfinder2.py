import copy
from lux.game_map import Position, Resource
from lux.constants import Constants
from lux.game_objects import CityTile
from lux import annotate

import random
import time

DIRECTIONS = Constants.DIRECTIONS
RESOURCE_TYPES = Constants.RESOURCE_TYPES

class Pathfinder2:
    def __init__(self):
        pass
        
    def find_path(self, game_state, worker, target, max_turns=10, hit_player_ct=False, time_limit=999):
        """
        Find a path for worker to target which is goes nearer than before.
        Returns minimum-turn path if any path exists.
        Returns empty list if not.
        
        Precondition:
        - worker is instance of Unit and worker.is_worker()
        - game_state is instance of Game
        - target is instance of Position
        """
        
        """
        function GRAPH-SEARCH(problem) returns a solution, or failure
            initialize the frontier using the initial state of problem
            initialize the explored set to be empty
            loop do
                if the frontier is empty then return failure
                choose a leaf node and remove it from the frontier
                if the node contains a goal state then return the corresponding solution
                add the node to the explored set
                expand the chosen node, adding the resulting nodes to the frontier
                    only if not in the frontier or explored set
        """
        
        deadline = time.time() + time_limit
        
        other_units = []
        for p in game_state.players:
            other_units += p.units
        other_units.remove(worker)
        
        frontier = [(
            Position(worker.pos.x, worker.pos.y), # current position
            0,                                    # score so far
            worker.pos.distance_to(target),       # heuristic score
            [],                                   # actions
            game_state.turn,                      # turn
            worker.cargo.wood,                    # fuel
            worker.cooldown,                      # cooldown
        )]
        
        explored = []
        stop_search = False
        solution = None
        city_tile_pos = []
        player_city_tile_pos = []
        resource_pos = []
        for y in range(game_state.map_height):
            for x in range(game_state.map_width):
                cell = game_state.map.get_cell(x, y)
                if isinstance(cell.citytile, CityTile):
                    city_tile_pos.append(cell.pos)
                    if cell.citytile.team == worker.team:
                        player_city_tile_pos.append(cell.pos)
                """
                elif isinstance(cell.resource, Resource):
                    if cell.resource.type == RESOURCE_TYPES.COAL:
                        city_tile_pos.append(cell.pos)
                    elif cell.resource.type == RESOURCE_TYPES.URANIUM:
                        city_tile_pos.append(cell.pos)

                    else:
                        resource_pos.append(cell.pos)
                        resource_pos.append(cell.pos.translate(DIRECTIONS.NORTH, 1))
                        resource_pos.append(cell.pos.translate(DIRECTIONS.WEST, 1))
                        resource_pos.append(cell.pos.translate(DIRECTIONS.SOUTH, 1))
                        resource_pos.append(cell.pos.translate(DIRECTIONS.EAST, 1))
                """
        
        bad_solutions = []
        while not stop_search:
            if len(frontier) == 0:
                stop_search = True
            else:
                current_pos, current_g, current_h, actions, current_turn, current_fuel, cooldown = frontier.pop(0)
                # if (current_pos.equals(target) or current_g >= max_turns):
                if current_pos.equals(target) or current_g >= max_turns or time.time() > deadline:
                    if current_fuel > current_h:
                        solution = actions
                        stop_search = True
                    else:
                        bad_solutions.append((-current_fuel, actions))
                else:
                    explored.append(current_pos)
                    directions = []
                    if cooldown < 1:
                        if current_pos.y > 0: # North condition
                            directions.append(DIRECTIONS.NORTH)
                            
                        if current_pos.x > 0: # West condition
                            directions.append(DIRECTIONS.WEST)
                            
                        if current_pos.y < game_state.map_height - 1: # South condition
                            directions.append(DIRECTIONS.SOUTH)
                            
                        if current_pos.x < game_state.map_width - 1: # East condition
                            directions.append(DIRECTIONS.EAST)
                        
                        random.shuffle(directions)
                        
                        for d in directions:
                            new_pos = current_pos.translate(d, 1)
                            cell = game_state.map.get_cell_by_pos(new_pos)
                            if isinstance(cell.resource, Resource):
                                if cell.resource.type == RESOURCE_TYPES.WOOD:
                                    # Make it simple
                                    new_fuel = min(current_fuel + 20, 100)
                                else:
                                    new_fuel = current_fuel
                            else:
                                new_fuel = current_fuel
                                
                            if current_turn % 40 >= 30:
                                new_fuel = new_fuel - 4
                                new_cooldown = cooldown + 3
                            else:
                                new_cooldown = cooldown + 1
                            new_turn = current_turn + 1
                                
                            if (new_pos == target or ((new_pos not in explored) and ((new_pos not in city_tile_pos) or (hit_player_ct and new_pos in player_city_tile_pos)))) and new_fuel >= 0 and (min(list(map(lambda u: u.pos.distance_to(new_pos), other_units))) > (current_g / 2 + 1) or random.random() > 0.2 ** (current_g / 2 + 1)):
                                new_g = current_g + 1 # Asumsikan 1 cost untuk setiap aksi
                                new_h = new_pos.distance_to(target)
                                new_actions = actions + [worker.move(d)]
                                
                                # Find where to put in frontier
                                if len(frontier) > 0:
                                    i = len(frontier) - 1
                                    while i > 0 and frontier[i][1] + frontier[i][2] > new_g + new_h:
                                        i -= 1
                                    # i == 0 or frontier[i][1] + frontier[i][2] <= new_g + new_h
                                    
                                    if frontier[i][1] + frontier[i][2] <= new_g + new_h:
                                        frontier.insert(
                                            i + 1,
                                            (new_pos, new_g, new_h, new_actions, new_turn, new_fuel, new_cooldown)
                                        )
                                        
                                    else:
                                        frontier.insert(
                                            0,
                                            (new_pos, new_g, new_h, new_actions, new_turn, new_fuel, new_cooldown)
                                        )
                                else:
                                    frontier.append(
                                        (new_pos, new_g, new_h, new_actions, new_turn, new_fuel, new_cooldown)
                                    )
                    else:
                        new_pos = current_pos
                        cell = game_state.map.get_cell_by_pos(new_pos)
                        if isinstance(cell.resource, Resource):
                            if cell.resource.type == RESOURCE_TYPES.WOOD:
                                # Make it simple
                                new_fuel = min(current_fuel + 20, 100)
                            else:
                                new_fuel = current_fuel
                        else:
                            new_fuel = current_fuel
                        
                        if current_turn % 40 >= 30:
                            new_fuel = new_fuel - 4
                        
                        new_turn = current_turn + 1
                        new_cooldown = cooldown - 1
                            
                        if new_fuel >= 0:
                            new_g = current_g + 1 # Asumsikan 1 cost untuk setiap aksi
                            new_h = new_pos.distance_to(target)
                            new_actions = actions
                            
                            # Find where to put in frontier
                            if len(frontier) > 0:
                                i = len(frontier) - 1
                                while i > 0 and frontier[i][1] + frontier[i][2] > new_g + new_h:
                                    i -= 1
                                # i == 0 or frontier[i][1] + frontier[i][2] <= new_g + new_h
                                
                                if frontier[i][1] + frontier[i][2] <= new_g + new_h:
                                    frontier.insert(
                                        i + 1,
                                        (new_pos, new_g, new_h, new_actions, new_turn, new_fuel, new_cooldown)
                                    )
                                    
                                else:
                                    frontier.insert(
                                        0,
                                        (new_pos, new_g, new_h, new_actions, new_turn, new_fuel, new_cooldown)
                                    )
                            else:
                                frontier.append(
                                    (new_pos, new_g, new_h, new_actions, new_turn, new_fuel, new_cooldown)
                                )
                        
        
        if solution != None:
            return solution
            
        elif len(bad_solutions) > 0:
            return min(bad_solutions, key=lambda s: s[0])[1]
            
        else:
            return []
                            
                        
        
        