from lux.constants import Constants
from lux.game_constants import GAME_CONSTANTS


def farming(game_state, player, worker, resource_list):
    """
    Go to nearest resource_list tile if not there.
    Do nothing if there. (return move center action, not None)
    Precondition: worker has space left in its cargo
    
    Return action if no exists resource type that full in cargo
    Return None if yes
    """
    # Note that resource_list is cells
    if worker.get_cargo_space_left() == 0:
        return None
    else:
        tile_distance = lambda t: t.pos.distance_to(worker.pos)
        gatherable_list = list(filter(
            lambda r: gatherable(player, r.resource.type),
            resource_list
        ))
        selected_resource = min(gatherable_list, key=tile_distance)
        selected_direction = worker.pos.direction_to(selected_resource.pos)
        
        return [worker.move(selected_direction)]
    
def gatherable(player, resource_type):
    if resource_type == Constants.RESOURCE_TYPES.WOOD:
        return True
    elif resource_type == Constants.RESOURCE_TYPES.COAL:
        return player.researched_coal()
    elif resource_type == Constants.RESOURCE_TYPES.URANIUM:
        return player.researched_uranium()
    else:
        # Unknown resource
        print("Warning: unknown resource: {}".format(resource_type))
        return False