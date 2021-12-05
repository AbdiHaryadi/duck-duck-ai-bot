from .Pathfinder2 import Pathfinder2

def go_to_city(game_state, worker, city):
    """
    Get action for go to city
    """
    
    pathfinder = Pathfinder2()
    target_citytile = min(city.citytiles, key=(
        lambda ct: ct.pos.distance_to(worker.pos)
    ))
    actions = pathfinder.find_path(
        game_state,
        worker,
        target_citytile.pos
    )
    
    return actions