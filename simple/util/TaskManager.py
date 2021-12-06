from os import stat
from lux import constants
from lux.game_objects import *
from lux.game_map import *
from lux.game import *
from lux.constants import *

class TaskManager:
    def __init__(self):
        self.action_list = []
        self.occupied_locations = []

    def get_default_action(self, unit: Unit) -> list[str]:
        return [unit.move(Constants.DIRECTIONS.CENTER)]
    
    def get_target_location(self, game_state: Game, current_location:Position, direction: Constants.DIRECTIONS) -> Position:
        if direction == Constants.DIRECTIONS.NORTH:
            return Position(
                    min(max(current_location.x, 0), game_state.map_width - 1),
                    min(max(current_location.y-1, 0), game_state.map_height - 1))
        elif direction == Constants.DIRECTIONS.EAST:
            return Position(
                    min(max(current_location.x+1, 0), game_state.map_width - 1),
                    min(max(current_location.y, 0), game_state.map_height - 1))
        elif direction == Constants.DIRECTIONS.SOUTH:
            return Position(
                    min(max(current_location.x, 0), game_state.map_width - 1),
                    min(max(current_location.y+1, 0), game_state.map_height - 1))
        elif direction == Constants.DIRECTIONS.WEST:
            return Position(
                    min(max(current_location.x-1, 0), game_state.map_width - 1),
                    min(max(current_location.y, 0), game_state.map_height - 1))
        return current_location

    def submit_action_unit(self, game_state: Game, unit: Unit, action) -> bool:
        if not isinstance(action, list):
            action = [action]
            
        status = False
        current_location = unit.pos
        splitted_action = action[0].split(" ")
        if splitted_action[0] == "m":
            target_location = self.get_target_location(game_state, current_location, splitted_action[2])
            location_valid = True
            for loc in self.occupied_locations:
                if loc.equals(target_location):
                    location_valid = False
                    break
            if location_valid:
                self.occupied_locations.append(target_location)
                status = True
            else:
                clocation_valid = True
                for loc in self.occupied_locations:
                    if loc.equals(current_location):
                        clocation_valid = False
                        break
                if clocation_valid:
                    self.occupied_locations.append(current_location)
        else:
            self.occupied_locations.append(current_location)
            status = True



        if status == True:
            self.action_list.append(action[0])
        else:
            self.action_list.append(self.get_default_action(unit)[0])

        return status
    
    def get_action_list(self):
        action_list = self.action_list.copy()
        self.occupied_locations = []
        self.action_list = []
        return action_list