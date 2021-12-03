from .farming import farming
from .Pathfinder2 import Pathfinder2

class RefuelAgent:
    def __init__(self, worker_id, city_id):
        self.worker_id = worker_id
        self.city_id = city_id
        self.state = "FARM"
        
    def get_action(self, game_state, player):
        workers = list(filter(lambda u: u.id == self.worker_id, player.units))
        cities = list(filter(lambda c: c.cityid == self.city_id, player.cities))
        if len(workers) == 0 or len(cities) == 0:
            return []
        else:
            worker = workers[0]
            city = cities[0]
            actions = None
            while actions is None:
                if self.state == "FARM":
                    resource_tiles: list[Cell] = []
                    for y in range(height):
                        for x in range(width):
                            cell = game_state.map.get_cell(x, y)
                            if cell.has_resource():
                                resource_tiles.append(cell)
                                
                    farm_actions = farming(game_state, player, worker, resource_list)
                    
                    if farm_actions == None:
                        self.state = "REFUEL"
                    else:
                        actions = farm_actions
                        
                elif self.state == "REFUEL":
                    # Should we check whether agent has resource to bring?
                    pathfinder = Pathfinder2()
                    target_citytile = min(city.citytiles, key=(
                        lambda ct: ct.pos.distance_to(worker.pos)
                    ))
                    refuel_actions = pathfinder.find_path(
                        game_state,
                        worker,
                        target_citytile.pos
                    )
                    
                    if refuel_actions == []:
                        self.state = "FARM"
                    else:
                        actions = refuel_actions
                        
                else:
                    raise ValueError("Unknown state: {}".format(self.state))
                        
            return actions