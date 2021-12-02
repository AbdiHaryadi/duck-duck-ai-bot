from ..lux.game_objects import *
from ..lux.game_map import *
from ..lux.game import *

def update_border(game_state: Game, border_list: list[Cell], current_border: Cell):
    """
    Return border_list terbaru.
    Proses: untuk mencari hal yang baru, cek tile dari border_list
    apakah ada city tile di situ. Jika ada, expand ke luar dan
    anggap itu sebagai border_list baru. Return border_list baru.
    """

    border_list.remove(current_border)
    game_map = game_state.map
    neighbor_cells: list[Cell] = [
        game_map.get_cell_by_pos(Position(current_border.pos.x-1, current_border.pos.y-1)),
        game_map.get_cell_by_pos(Position(current_border.pos.x, current_border.pos.y-1)),
        game_map.get_cell_by_pos(Position(current_border.pos.x+1, current_border.pos.y-1)),
        game_map.get_cell_by_pos(Position(current_border.pos.x-1, current_border.pos.y)),
        game_map.get_cell_by_pos(Position(current_border.pos.x, current_border.pos.y)),
        game_map.get_cell_by_pos(Position(current_border.pos.x+1, current_border.pos.y)),
        game_map.get_cell_by_pos(Position(current_border.pos.x-1, current_border.pos.y+1)),
        game_map.get_cell_by_pos(Position(current_border.pos.x, current_border.pos.y+1)),
        game_map.get_cell_by_pos(Position(current_border.pos.x+1, current_border.pos.y+1))
    ]
    for neighbor in neighbor_cells:
        is_added = True
        for border in border_list:
            if border.pos.equals(neighbor.pos):
                is_added =  False
                break
        if is_added:
            border_list.append(neighbor)
            
    return border_list