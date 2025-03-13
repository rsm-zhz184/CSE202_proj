
import math
from itertools import combinations, permutations
from copy import deepcopy
from utils import Map, Player_P3, STONE, ，GRASS，EMPTY  
EMPTY = 0
STONE = 1
APPLE = 2
GRASS = 3

def algo_brute_p2(matrix, start_point, initial_h):
    
    pass
def algo_p3(matrix, start_point, initial_h):
    game_map = Map(matrix)
    
    resource_list = []
    for s in game_map.stones:
        resource_list.append((s[0], s[1], STONE))
    for g in game_map.grass:
        resource_list.append((g[0], g[1], GRASS))
    def manhattan_distance(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)
    
    # Compute total cost for a given order of 3 resources.
    def compute_total_cost_single(order, startX, startY):
        current_x, current_y = startX, startY
        movement_cost = 0
        for (tx, ty, rtype) in order:
            movement_cost += manhattan_distance(current_x, current_y, tx, ty)
            current_x, current_y = tx, ty
        collection_cost = 3 * 10  # Each collection costs 10
        return movement_cost + collection_cost
    
    # Build an action plan given an order of resources.
    def build_plan_single(order, startX, startY):
        actions = []
        curx, cury = startX, startY
        for (tx, ty, rtype) in order:
            actions.append(("move", (tx, ty)))
            actions.append(("collect", (tx, ty), rtype))
            curx, cury = tx, ty
        return actions
    
    # Check if a 3-resource combination meets the requirement.
    def meets_requirement(combo, req_stones, req_grass):
        stone_count = sum(1 for (x, y, rtype) in combo if rtype == STONE)
        grass_count = sum(1 for (x, y, rtype) in combo if rtype == GRASS)
        return stone_count == req_stones and grass_count == req_grass
    
    # Simulate executing a route on a copy of the player to compute cost and check feasibility.
    def simulate_route(order, player_obj):
        sim_player = deepcopy(player_obj)
        total_cost = 0
        actions = []
        for (rx, ry, rtype) in order:
            move_cost = manhattan_distance(sim_player.x, sim_player.y, rx, ry)
            collect_cost = 10 if (rtype == STONE or rtype == GRASS) else 0
            if move_cost + collect_cost > sim_player.h:
                return (None, None)
            total_cost += move_cost + collect_cost
            # Update simulated player: move and then collect resource.
            sim_player.h -= (move_cost + collect_cost)
            sim_player.x = rx
            sim_player.y = ry
            actions.append(("move", (rx, ry)))
            actions.append(("collect", (rx, ry), rtype))
        return (total_cost, actions)
    
    # Plan a single mission: choose an optimal order to collect exactly 3 resources that meet the requirement.
    def plan_single_mission(startX, startY, health, req_stones=2, req_grass=1, resource_list):
        needed_total = req_stones + req_grass
        if needed_total != 3:
            return (None, math.inf)
        best_cost = math.inf
        best_plan = None
        for combo in combinations(resource_list, 3):
            if not meets_requirement(combo, req_stones, req_grass):
                continue
            for order in permutations(combo):
                cost, actions = simulate_route(order, player)
                if cost is not None and cost < best_cost and cost <= health:
                    best_cost = cost
                    best_plan = actions
        return (best_plan, best_cost)
    
    # Sequential mission planning: iterate over missions in fixed order.
    action_sequence = []  # Global action list
    max_reward = 0
    current_state = (start_point[0], start_point[1], initial_h)
    
    # Initialize the player (real player) with initial state.
    player = Player_P3(start_point, initial_h, matrix)
    
    missions=[]
    for (req_stones, req_grass) in missions:
        plan_actions, plan_cost = plan_single_mission(player.x, player.y, player.h, req_stones, req_grass, resource_list)
        if plan_actions is None or plan_cost > player.h:
            break  # Cannot complete this mission
        # Execute the plan on the real player step-by-step:
        for act in plan_actions:
            if act[0] == "move":
                (tx, ty) = act[1]
                move_cost = manhattan_distance(player.x, player.y, tx, ty)
                if move_cost > player.h:
                    break
                player.h -= move_cost
                player.x, player.y = tx, ty
                action_sequence.append(("move", (tx, ty)))
            elif act[0] == "collect":
                (tx, ty, rtype) = (act[1][0], act[1][1], act[2])
                ccost = 10 if (rtype == STONE or rtype == GRASS) else 0
                if ccost > player.h:
                    break
                player.h -= ccost
                # Update the player's matrix: mark as EMPTY
                if player.matrix[tx][ty] != EMPTY:
                    player.matrix[tx][ty] = EMPTY
                action_sequence.append(("collect", (tx, ty), rtype))
        # After collecting 3 resources, we assume the mission is completed.
        max_reward += 1
        # In your Player_P3, the reward and bag reset would be handled;
        # Here, we simulate it:
        player.num_stones = 0
        player.num_grass = 0

    return (max_reward, action_sequence)