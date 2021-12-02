from lux.game_objects import *
from lux.game_map import *
from lux.game import *

from .update_border import *

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

    if worker.pos.equals(nearest_border.pos):
        if worker.can_build(game_state.map):
            border_list = update_border(game_state, border_list, nearest_border)
            return worker.build_city()
        else:
            random_border = border_list[random.randint(0, len(border_list)-1)]
            return worker.move(worker.pos.direction_to(random_border.pos))
    """WARNING: 'direction_to()' need to be changed into A* based direction finder"""
    return worker.move(worker.pos.direction_to(nearest_border.pos))