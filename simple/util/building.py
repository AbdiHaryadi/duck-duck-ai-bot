from lux.game_objects import *
from lux.game_map import *
from lux.game import *

from .update_border import *

from .Pathfinder2 import Pathfinder2

import random

def building(game_state: Game, worker: Unit, border_list: list[Cell]):
    """
    Go to nearest border_list tile if not there.
    Build if there.
    Precondition: worker_id has 100 wood
    
    Return action if not build a city_tile yet in border_list
    Return None if yes
    """
    if worker.get_cargo_space_left() > 0:
        return "GO_FARMING"
    
    nearest_border: Cell = None
    for border in border_list:
        if nearest_border is None:
            nearest_border = border
        else:
            if worker.pos.distance_to(border.pos) < worker.pos.distance_to(nearest_border.pos):
                nearest_border = border
    # Problem: bisa saja nearest_border sudah memiliki city
    """
    Jika mau ubah urutannya (misalkan corner dulu), ubah bagian di atas.
    """
    
    if nearest_border is None:
        """
        random_border = border_list[random.randint(0, len(border_list)-1)]
        pathfinder = Pathfinder2()
        # return [worker.move(worker.pos.direction_to(random_border.pos))]
        return pathfinder.find_path(game_state, worker, random_border.pos)
        """
        random_border = border_list[random.randint(0, len(border_list)-1)]
        return [worker.move(worker.pos.direction_to(random_border.pos))]
    elif worker.pos.equals(nearest_border.pos):
        if worker.can_build(game_state.map):
            new_border_list = update_border(game_state, border_list, nearest_border)
            for idx, cell in enumerate(new_border_list):
                border_list[idx] = cell
            return [worker.build_city()]
        else:
            random_border = border_list[random.randint(0, len(border_list)-1)]
            return [worker.move(worker.pos.direction_to(random_border.pos))]
    """WARNING: 'direction_to()' need to be changed into A* based direction finder"""
    pathfinder = Pathfinder2()
    return pathfinder.find_path(game_state, worker, nearest_border.pos)
    # return [worker.move(worker.pos.direction_to(nearest_border.pos))]