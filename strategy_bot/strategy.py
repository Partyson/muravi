from pathfinding import find_path, _get_hex_distance
import numpy as np
import random
import os # Нужен для проверки файла-флага

# --- КОНСТАНТЫ ДОКТРИНЫ «ИНСТИНКТ РОЯ 2.0» ---
ANT_SPEED = {0: 5, 1: 4, 2: 7}
CROWDED_RADIUS = 1
CROWDED_LIMIT = 2
EXPLORATION_DISTANCE = 70

class GameState:
    def __init__(self, api_data):
        self.my_ants = api_data.get('ants', [])
        self.enemies = api_data.get('enemies', [])
        self.food = api_data.get('food', [])
        self.home_hexes = {(h['q'], h['r']) for h in api_data.get('home', [])}
        self.home_center = list(self.home_hexes)[1] if len(self.home_hexes) > 1 else (0,0)
        self.spot_hex = (api_data['spot']['q'], api_data['spot']['r']) if 'spot' in api_data else None
        self.game_map = {(h['q'], h['r']): h for h in api_data.get('map', [])}

def decide_moves(game_state_data):
    """
    Реализация «Инстинкта Роя» с динамическим планированием.
    """
    gs = GameState(game_state_data)
    moves = []
    
    # VVV КЛЮЧЕВОЕ ИЗМЕНЕНИЕ VVV
    # Этот словарь будет хранить клетки, которые БУДУТ заняты в этом ходу
    future_occupied_hexes = {(e['q'], e['r']) for e in gs.enemies}

    # Сначала обрабатываем тех, кто ближе к центру, чтобы они ушли первыми
    sorted_ants = sorted(gs.my_ants, key=lambda a: _get_hex_distance(a['q'], a['r'], gs.home_center[0], gs.home_center[1]))

    for ant in sorted_ants:
        # Каждый раз передаем обновленный список будущих занятых клеток
        path = get_best_action_for_ant(ant, gs, future_occupied_hexes)
        if path:
            move_command = format_move(ant, path)
            moves.append(move_command)
            # Если ход запланирован, добавляем конечную точку в 'будущие' занятые клетки
            if move_command['path']:
                final_hex = (move_command['path'][-1]['q'], move_command['path'][-1]['r'])
                future_occupied_hexes.add(final_hex)
            
    return moves

def get_best_action_for_ant(ant, gs, occupied_hexes):
    """Определяет лучший ход для одного муравья на основе иерархии инстинктов."""
    ant_pos = (ant['q'], ant['r'])

    # --- ИНСТИНКТ №1: ВЫЖИВАНИЕ ---
    if ant_pos == gs.spot_hex:
        for h in gs.home_hexes:
            if h != gs.spot_hex and h not in occupied_hexes: return [gs.spot_hex, h]
    
    neighbor_count = sum(1 for a in gs.my_ants if a['id'] != ant['id'] and _get_hex_distance(ant_pos[0], ant_pos[1], a['q'], a['r']) <= CROWDED_RADIUS)
    if neighbor_count >= CROWDED_LIMIT:
        for _ in range(10):
            direction = random.choice([(1,0), (-1,0), (0,1), (0,-1), (1,-1), (1,1)])
            target_pos = (ant_pos[0] + direction[0] * 3, ant_pos[1] + direction[1] * 3)
            if target_pos in gs.game_map and target_pos not in occupied_hexes:
                path = find_path(ant_pos, target_pos, gs.game_map, occupied_hexes)
                if path: return path

    # --- ИНСТИНКТ №2: ОБЕСПЕЧЕНИЕ ---
    if ant.get('food') and ant['food']['amount'] > 0:
        path = find_path(ant_pos, gs.home_center, gs.game_map, occupied_hexes)
        if path: return path

    # --- ИНСТИНКТ №3 и №4: АГРЕССИЯ и СБОР/РАЗВЕДКА ---
    best_target_path, highest_score = None, -1

    # АТАКА
    for enemy in gs.enemies:
        score, dist = 0, _get_hex_distance(ant_pos[0], ant_pos[1], enemy['q'], enemy['r'])
        if dist == 0: dist = 0.5
        if enemy.get('food') and enemy['food']['amount'] > 0: score = 1000 / dist
        elif enemy['type'] == 0: score = 500 / dist
        else: score = 100 / dist
        if ant['type'] == 1: score *= 3.0
        elif ant['type'] == 2: score *= 1.5
        else: score *= 0.1
        if score > highest_score:
            path = find_path(ant_pos, (enemy['q'], enemy['r']), gs.game_map, occupied_hexes)
            if path and len(path) > 1: path.pop()
            if path: highest_score, best_target_path = score, path

    # СБОР
    for food in gs.food:
        dist = _get_hex_distance(ant_pos[0], ant_pos[1], food['q'], food['r'])
        if dist == 0: dist = 0.5
        score = (food['amount'] * 20) / dist
        if ant['type'] == 0: score *= 3.0
        elif ant['type'] == 2: score *= 1.5
        else: score *= 0.1
        if score > highest_score:
            path = find_path(ant_pos, (food['q'], food['r']), gs.game_map, occupied_hexes)
            if path: highest_score, best_target_path = score, path

    if best_target_path: return best_target_path

    # РАЗВЕДКА
    ant_numeric_id = int(ant['id'].replace('-', '')[:8], 16)
    sector_angle = (ant_numeric_id % 12) * 30
    target_q = gs.home_center[0] + int(EXPLORATION_DISTANCE * np.cos(np.deg2rad(sector_angle)))
    target_r = gs.home_center[1] + int(EXPLORATION_DISTANCE * np.sin(np.deg2rad(sector_angle)))
    return find_path(ant_pos, (target_q, target_r), gs.game_map, occupied_hexes)

def format_move(ant, path):
    speed = ANT_SPEED.get(ant['type'], 1)
    final_path_coords = path[1:speed+1] if path and len(path) > 1 else []
    return {'ant': ant['id'], 'path': [{'q': p[0], 'r': p[1]} for p in final_path_coords]}