from lux.constants import Constants
from lux.game_map import Position

def scan_initial_border(game_state, worker, resource_list):
    """
    Return border_list: border hutan terdekat yang terdiri dari position.
    Pilih yang terdekat.
    """
    
    """
    Idea:
    - Get all trees
    - Choose nearest tree, let's say with position (x1, y1)
    - From that tree, check another tree which has position (x2, y2)
      such that min(abs(dx), abs(dy)) <= 1
      and max(abs(dx), abs(dy)) <= 3
      (so it just like cross).
      Take that tree to some list, including the first one.
    - Determine top-left-pos: (max(max(xtree) - 1, 0), max(max(ytree) - 1, 0))
    - Determine bottom-right-pos: (min(min(xtree) - 1, game_state.map_width - 1), 
                                   min(min(ytree) - 1, game_state.map_height - 1))
    Old:
    - Create matrix such that contains tile from top-left-pos to bottom-right-pos.
      Then, set the value to True for
      a tile that has at least one tree to it's adjacent (include
      diagonal), or it is a tree. Otherwise, set to False.
    - Set to False for a tile which all of its adjacent tiles mark True
      - Watch out for edge and corner case!
    End of old
    New:
    - Just create the border with square
    End of new
    - Return list of position.
    """
    
    # Get all trees
    is_tree = lambda c: c.resource.type == Constants.RESOURCE_TYPES.WOOD
    tree_cells = list(filter(is_tree, resource_list))
    
    # Choose nearest tree
    tile_distance = lambda t: t.pos.distance_to(worker.pos)
    stc = min(tree_cells, key=tile_distance) # stc: selected_tree_cell
    
    # Gather the neighbor of tree
    is_neighbor = lambda c1, c2: (
        min(abs(c1.pos.x - c2.pos.x), abs(c1.pos.y - c2.pos.y)) <= 1
        and max(abs(c1.pos.x - c2.pos.x), abs(c1.pos.y - c2.pos.y)) <= 3
    )
    
    frontier = [stc]
    min_x = max_x = stc.pos.x
    min_y = max_y = stc.pos.y
    vtcs = [] # vtcs: visited_tree_cells
    while len(frontier) > 0:
        tc = frontier.pop(0)
        new_tree_cells = list(filter(lambda c: is_neighbor(tc, c), tree_cells))
        new_tree_cells = list(filter(lambda c: c not in vtcs, new_tree_cells))
        frontier += new_tree_cells
        min_x = min(min_x, tc.pos.x)
        min_y = min(min_y, tc.pos.y)
        max_x = max(max_x, tc.pos.x)
        max_y = max(max_y, tc.pos.y)
        vtcs.append(tc)
    # len(frontier) == 0
    
    # Create the border
    border_list = []
    min_border_x = max(min_x - 1, 0)
    min_border_y = max(min_y - 1, 0)
    max_border_x = min(max_x + 1, game_state.map_width - 1)
    max_border_y = min(max_y + 1, game_state.map_height - 1)
    
    if min_border_y > 0:
        # Create the top border
        border_list += [Position(x, min_border_y) for x in range(min_border_x,
                                                                 max_border_x + 1)]
    # else: do not
    
    if min_border_x > 0:
        # Create the left border
        if min_border_y > 0:
            border_list += [Position(min_border_x, y) for y in range(min_border_y + 1,
                                                                     max_border_y + 1)]
        else:
            border_list += [Position(min_border_x, y) for y in range(min_border_y,
                                                                     max_border_y + 1)]
    # else: do not
    
    if max_border_x < game_state.map_width - 1:
        # Create the right border
        if min_border_y > 0:
            border_list += [Position(max_border_x, y) for y in range(min_border_y + 1,
                                                                     max_border_y + 1)]
        else:
            border_list += [Position(max_border_x, y) for y in range(min_border_y,
                                                                     max_border_y + 1)]
        
    # else: do not
    
    if max_border_y < game_state.map_height - 1:
        # Create the bottom border
        border_list += [Position(x, max_border_y) for x in range(min_border_x + 1,
                                                                 max_border_x)]
    # else: do not
    
    return border_list