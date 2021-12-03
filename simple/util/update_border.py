from lux.game_objects import *
from lux.game_map import *
from lux.game import *

def update_border(game_state: Game, border_list: list[Cell], current_border: Cell):
    """
    Return border_list terbaru.
    Proses: untuk mencari hal yang baru, cek tile dari border_list
    apakah ada city tile di situ. Jika ada, expand ke luar dan
    anggap itu sebagai border_list baru. Return border_list baru.
    """

    border_list.remove(current_border)
    game_map = game_state.map
    nearest_pos = lambda x, y: Position(
        min(max(x, 0), game_state.map_width - 1),
        min(max(y, 0), game_state.map_height - 1),
    )
    neighbor_cells: list[Cell] = []
    for x in range(max(current_border.pos.x-1, 0), min(current_border.pos.x+1, game_state.map_width - 1) + 1):
        for y in range(max(current_border.pos.y-1, 0), min(current_border.pos.y+1, game_state.map_height - 1) + 1):
            new_pos = Position(x, y)
            if not new_pos.equals(current_border.pos):
                neighbor_cells.append(game_map.get_cell_by_pos(new_pos))
    """
    neighbor_cells: list[Cell] = [
        game_map.get_cell_by_pos(nearest_pos(current_border.pos.x-1, current_border.pos.y-1)),
        game_map.get_cell_by_pos(nearest_pos(current_border.pos.x, current_border.pos.y-1)),
        game_map.get_cell_by_pos(nearest_pos(current_border.pos.x+1, current_border.pos.y-1)),
        game_map.get_cell_by_pos(nearest_pos(current_border.pos.x-1, current_border.pos.y)),
        game_map.get_cell_by_pos(nearest_pos(current_border.pos.x+1, current_border.pos.y)),
        game_map.get_cell_by_pos(nearest_pos(current_border.pos.x-1, current_border.pos.y+1)),
        game_map.get_cell_by_pos(nearest_pos(current_border.pos.x, current_border.pos.y+1)),
        game_map.get_cell_by_pos(nearest_pos(current_border.pos.x+1, current_border.pos.y+1))
    ]
    """
    
    
    for neighbor in neighbor_cells:
        is_added = True
        if game_state.map.get_cell_by_pos(neighbor.pos).has_resource():
            is_added = False
        elif game_state.map.get_cell_by_pos(neighbor.pos).citytile is not None:
            is_added = False
        else:
            for border in border_list:
                if border.pos.equals(neighbor.pos):
                    is_added =  False
                    break
        if is_added:
            border_list.append(neighbor)
            
    return border_list