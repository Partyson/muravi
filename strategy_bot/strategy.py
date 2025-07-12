# strategy.py
from pathfinding import find_path, _get_hex_distance
import random
import numpy as np

# --- КОНСТАНТЫ СТРАТЕГИИ «АДАПТИВНЫЙ ЛЕГИОН» ---
ANT_SPEED = {0: 5, 1: 4, 2: 7}
HOME_ZONE_RADIUS = 12
MIN_HOME_DEFENDERS = 1
CROWDED_RADIUS = 1
CROWDED_LIMIT = 3

STRATEGY_MEMORY = {
    'legions': {}
}

class GameState:
    """Удобный класс для хранения и доступа к состоянию игры."""
    def __init__(self, api_data):
        self.turn = api_data.get('turnNo', 0) 
        self.my_ants = api_data.get('ants', [])
        self.enemies = api_data.get('enemies', [])
        self.food = api_data.get('food', [])
        self.home_hexes = {(h['q'], h['r']) for h in api_data.get('home', [])}
        self.home_center = list(self.home_hexes)[1] if len(self.home_hexes) > 1 else (0,0)
        self.spot_hex = (api_data['spot']['q'], api_data['spot']['r']) if 'spot' in api_data else None
        self.game_map = {(h['q'], h['r']): h for h in api_data.get('map', [])}
        self.my_ant_positions = { (a['q'], a['r']): a for a in self.my_ants }

def decide_moves(game_state_data):
    gs = GameState(game_state_data)
    moves = []
    
    occupied_hexes = {(a['q'], a['r']) for a in gs.my_ants} | {(e['q'], e['r']) for e in gs.enemies}
    assigned_ants = set()

    all_ant_pos = list(gs.my_ant_positions.keys())
    for ant in gs.my_ants:
        neighbor_count = sum(1 for pos in all_ant_pos if pos != (ant['q'],ant['r']) and _get_hex_distance(ant['q'],ant['r'],pos[0],pos[1]) <= CROWDED_RADIUS)
        if neighbor_count >= CROWDED_LIMIT:
            for _ in range(10):
                direction = random.choice([(1,0), (-1,0), (0,1), (0,-1), (1,-1), (-1,1)])
                target_pos = (ant['q'] + direction[0] * 2, ant['r'] + direction[1] * 2)
                if target_pos in gs.game_map and target_pos not in occupied_hexes:
                    path = find_path((ant['q'], ant['r']), target_pos, gs.game_map, occupied_hexes)
                    if path:
                        moves.append(format_move(ant, path, occupied_hexes)); assigned_ants.add(ant['id']); break

    update_legions(gs)
    
    ant_ids_in_legions = {ant_id for legion in STRATEGY_MEMORY['legions'].values() for ant_id in legion['members']}
    unassigned_ants = [ant for ant in gs.my_ants if ant['id'] not in assigned_ants and ant['id'] not in ant_ids_in_legions]

    home_defenders_count = len([ant for ant in unassigned_ants if _get_hex_distance(ant['q'], ant['r'], gs.home_center[0], gs.home_center[1]) <= HOME_ZONE_RADIUS])
    if home_defenders_count >= MIN_HOME_DEFENDERS and len(unassigned_ants) > MIN_HOME_DEFENDERS:
        create_new_mission(gs, unassigned_ants)

    for legion_id, legion in STRATEGY_MEMORY['legions'].items():
        leader = next((ant for ant in gs.my_ants if ant['id'] in legion['members']), None)
        if not leader: continue
        for member_id in legion['members']:
            member = next((ant for ant in gs.my_ants if ant['id'] == member_id), None)
            if not member: continue
            
            if legion['mission'] == 'EXPAND_AND_HARVEST' and member['type'] != 1:
                 path = find_food_near_point(member, (leader['q'], leader['r']), 6, gs, occupied_hexes)
            else:
                target_pos = legion['target'] if member_id == leader['id'] else (leader['q'], leader['r'])
                path = find_path((member['q'], member['r']), target_pos, gs.game_map, occupied_hexes)
            if path: moves.append(format_move(member, path, occupied_hexes))

    for ant in unassigned_ants:
        path = handle_home_zone_duty(ant, gs, occupied_hexes)
        if path: moves.append(format_move(ant, path, occupied_hexes))
            
    return moves

def update_legions(gs):
    legions_to_disband, ant_ids_in_game = [], {ant['id'] for ant in gs.my_ants}
    for legion_id, legion in STRATEGY_MEMORY['legions'].items():
        legion['members'] = {ant_id for ant_id in legion['members'] if ant_id in ant_ids_in_game}
        if not legion['members']: legions_to_disband.append(legion_id); continue
        target_q, target_r = legion['target']
        if legion['mission'] == 'ATTACK_ENEMY_GROUP':
            if not any(_get_hex_distance(e['q'], e['r'], target_q, target_r) < 5 for e in gs.enemies):
                legions_to_disband.append(legion_id)
    for legion_id in legions_to_disband:
        if legion_id in STRATEGY_MEMORY['legions']:
            del STRATEGY_MEMORY['legions'][legion_id]
            print(f"[ГЕНШТАБ] Легион {legion_id} расформирован.")

def create_new_mission(gs, available_ants):
    enemy_clusters = find_clusters(gs.enemies, 7)
    if enemy_clusters:
        target_cluster = max(enemy_clusters, key=len)
        target_pos = (target_cluster[0]['q'], target_cluster[0]['r'])
        form_legion(gs, available_ants, target_pos, 'ATTACK_ENEMY_GROUP')
        return

    best_food_spot, max_dist = None, HOME_ZONE_RADIUS
    for food in gs.food:
        dist_from_home = _get_hex_distance(food['q'], food['r'], gs.home_center[0], gs.home_center[1])
        if dist_from_home > max_dist:
            max_dist, best_food_spot = dist_from_home, food
    if best_food_spot:
        form_legion(gs, available_ants, (best_food_spot['q'], best_food_spot['r']), 'EXPAND_AND_HARVEST')

def form_legion(gs, available_ants, target_pos, mission_type):
    needed = {'FIGHTER': 1, 'SCOUT': 1}
    recruited = {}
    sorted_ants = sorted(available_ants, key=lambda a: _get_hex_distance(a['q'], a['r'], target_pos[0], target_pos[1]))
    for ant in sorted_ants:
        if ant['type'] == 1 and needed['FIGHTER'] > 0:
            recruited[ant['id']] = 'FIGHTER'; needed['FIGHTER'] -= 1
        elif ant['type'] == 2 and needed['SCOUT'] > 0:
            recruited[ant['id']] = 'SCOUT'; needed['SCOUT'] -= 1
    if len(recruited) >= 2:
        legion_id = f"{mission_type}_{gs.turn}"
        if legion_id not in STRATEGY_MEMORY['legions']:
            STRATEGY_MEMORY['legions'][legion_id] = {'mission': mission_type, 'target': target_pos, 'members': recruited}
            print(f"[ГЕНШТАБ] Сформирован легион {legion_id} для миссии {mission_type} к цели {target_pos}.")

def handle_home_zone_duty(ant, gs, occupied_hexes):
    if (ant['q'], ant['r']) == gs.spot_hex:
        for h in gs.home_hexes:
            if h != gs.spot_hex and h not in occupied_hexes: return [gs.spot_hex, h]
    if ant['type'] == 1:
        for enemy in gs.enemies:
            if _get_hex_distance(enemy['q'], enemy['r'], gs.home_center[0], gs.home_center[1]) <= HOME_ZONE_RADIUS:
                path = find_path((ant['q'], ant['r']), (enemy['q'], enemy['r']), gs.game_map, occupied_hexes)
                if path and len(path) > 1: path.pop(); return path
        return find_path((ant['q'], ant['r']), (gs.home_center[0] + random.randint(-5,5), gs.home_center[1] + random.randint(-5,5)), gs.game_map, occupied_hexes)
    else: return find_food_near_point(ant, gs.home_center, HOME_ZONE_RADIUS, gs, occupied_hexes)

def find_food_near_point(ant, point, radius, gs, occupied_hexes):
    if ant.get('food') and ant['food']['amount'] > 0:
        return find_path((ant['q'], ant['r']), gs.home_center, gs.game_map, occupied_hexes)
    best_food, min_dist = None, 999
    for food in gs.food:
        if _get_hex_distance(food['q'], food['r'], point[0], point[1]) <= radius:
            dist = _get_hex_distance(ant['q'], ant['r'], food['q'], food['r'])
            if dist < min_dist: min_dist, best_food = dist, food
    if best_food: return find_path((ant['q'], ant['r']), (best_food['q'], best_food['r']), gs.game_map, occupied_hexes)
    return None

def find_clusters(entities, radius):
    clusters, visited = [], set()
    for i, e1 in enumerate(entities):
        if i in visited: continue
        new_cluster = [e1]
        visited.add(i)
        for j, e2 in enumerate(entities):
            if j in visited: continue
            if _get_hex_distance(e1['q'], e1['r'], e2['q'], e2['r']) < radius:
                new_cluster.append(e2); visited.add(j)
        if len(new_cluster) > 1: clusters.append(new_cluster)
    return clusters

def format_move(ant, path, occupied_hexes):
    ant_pos, speed = (ant['q'], ant['r']), ANT_SPEED.get(ant['type'], 1)
    final_path_coords = path[1:speed+1] if path and len(path) > 1 else []
    if final_path_coords:
        destination = final_path_coords[-1]
        if destination not in occupied_hexes:
            occupied_hexes.add(destination)
            if ant_pos in occupied_hexes: occupied_hexes.remove(ant_pos)
    return {'ant': ant['id'], 'path': [{'q': p[0], 'r': p[1]} for p in final_path_coords]}