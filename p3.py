import math
from itertools import combinations, permutations
from copy import deepcopy
import numpy as np
from utils import Map, Player_P3, cost_of_resource_collecting
EMPTY = 0
STONE = 1
APPLE = 2
GRASS = 3

def algo_brute_p3(missions, matrix, start_point, initial_h):
    pass

def algo_p3(missions, matrix, start_point, initial_h):
    game_map = Map(matrix)
    player = Player_P3(start_point, initial_h, matrix)
    
    # Helper: Extract current resource points from the player's map.
    def extract_resource_list(mat):
        resources = []
        n = mat.shape[0]
        for i in range(n):
            for j in range(n):
                if mat[i, j] == STONE:
                    resources.append((i, j, STONE))
                elif mat[i, j] == GRASS:
                    resources.append((i, j, GRASS))
        return resources
    
    # Manhattan distance function.
    def manhattan_distance(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)
    def compute_total_cost_single(order, startX, startY):
        curx, cury = startX, startY
        movement_cost = 0
        for (rx, ry, rtype) in order:
            movement_cost += manhattan_distance(curx, cury, rx, ry)
            curx, cury = rx, ry
        collection_cost = 3 * 10  
        return movement_cost + collection_cost
    
    def build_plan_single(order, startX, startY):
        actions = []
        curx, cury = startX, startY
        for (rx, ry, rtype) in order:
            actions.append(("move", (rx, ry)))
            actions.append(("collect", (rx, ry), rtype))
            curx, cury = rx, ry
        return actions
    
    def meets_requirement(combo, req_stones, req_grass):
        stone_count = sum(1 for (x, y, rtype) in combo if rtype == STONE)
        grass_count = sum(1 for (x, y, rtype) in combo if rtype == GRASS)
        return stone_count == req_stones and grass_count == req_grass
    
    def simulate_route(order, player_obj):
        sim_player = deepcopy(player_obj)
        total_cost = 0
        actions = []
        for (rx, ry, rtype) in order:
            move_cost = manhattan_distance(sim_player.x, sim_player.y, rx, ry)
            collect_cost = cost_of_resource_collecting(rtype)
            if move_cost + collect_cost > sim_player.h:
                return (None, None)
            total_cost += (move_cost + collect_cost)
            sim_player.h -= (move_cost + collect_cost)
            sim_player.x, sim_player.y = rx, ry
            actions.append(("move", (rx, ry)))
            actions.append(("collect", (rx, ry), rtype))
        return (total_cost, actions)
    
    # Plan a single mission: find the optimal route (order of collecting 3 resources) that meets the requirement.
    def plan_single_mission(startX, startY, health, req_stones, req_grass, resource_list):
        if req_stones + req_grass != 3:
            # For this problem, mission must require exactly 3 resources.
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
    
    # Sequential mission planning:
    action_sequence = []
    max_reward = 0
    
    # For each mission (in fixed order), update the player's state after mission completion.
    for (req_stones, req_grass) in missions:
        # Re-extract current resource points from player's matrix (since matrix changes after collection).
        current_resource_list = extract_resource_list(player.matrix)
        plan_actions, plan_cost = plan_single_mission(player.x, player.y, player.h, req_stones, req_grass, current_resource_list)
        if plan_actions is None or plan_cost > player.h:
            break  # Cannot complete the current mission.
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
                ccost = cost_of_resource_collecting(rtype)
                if ccost > player.h:
                    break
                player.h -= ccost
                if player.matrix[tx][ty] != EMPTY:
                    player.matrix[tx][ty] = EMPTY
                action_sequence.append(("collect", (tx, ty), rtype))
        max_reward += 1
        player.num_stones = 0
        player.num_grass = 0

    return (max_reward, action_sequence)

if __name__ == "__main__":
    missions = [(2, 1), (1, 2), (2, 1), (3,0)]
    size = 15
    matrix = np.zeros((size, size), dtype=int)
    all_indices = [(i, j) for i in range(size) for j in range(size)]
    np.random.shuffle(all_indices)
    stone_positions = all_indices[:20]
    remaining = all_indices[20:]
    np.random.shuffle(remaining)
    grass_positions = remaining[:20]
    for (i, j) in stone_positions:
        matrix[i, j] = STONE
    for (i, j) in grass_positions:
        matrix[i, j] = GRASS

    start_point = (size // 2, size // 2)
    initial_h = 100

    max_reward, action_sequence = algo_p3(missions, matrix, start_point, initial_h)
    
    print("Max Reward (Missions Completed):", max_reward)
    print("Action Sequence:")
    for act in action_sequence:
        print(act)