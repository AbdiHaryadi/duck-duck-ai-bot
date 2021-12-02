from lux.constants import Constants
from lux.game_map import Position

def scan_initial_border(game_state, resource_list):
    """
    Return border_list: border hutan terdekat yang terdiri dari cell.
    Pilih yang terdekat.
    """
    
    """
    Idea:
    - Get all trees
    - Pick sell such that it is adjacent to some tree (include diagonally) and it is empty tile.
    - Return list of cell.
    """
    
    # Get all trees
    is_tree = lambda c: c.resource.type == Constants.RESOURCE_TYPES.WOOD
    tree_cells = list(filter(is_tree, resource_list))
    
    border_list = []
    for tc in tree_cells:
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    new_pos = Position(
                        min(max(tc.pos.x + dx, 0), game_state.map_width - 1),
                        min(max(tc.pos.y + dy, 0), game_state.map_height - 1),
                    )
                    cell = game_state.map.get_cell_by_pos(new_pos)
                    
                    if cell.has_resource():
                        pass
                    elif cell.citytile != None:
                        pass
                    elif cell in border_list: # Warning: O(n^2) complexity!
                        pass
                    else:
                        border_list.append(cell)
    
    return border_list