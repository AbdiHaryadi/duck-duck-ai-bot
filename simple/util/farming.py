def farming(game_state, worker, resource_list):
    """
    Go to nearest resource_list tile if not there.
    Do nothing if there. (use action.move center, not None)
    Precondition: worker_id has 100 wood
    
    Return action if wood < 100 (resource full)
    Return None if wood == 100
    """
    return None