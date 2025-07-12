# pathfinding.py
import heapq

def _get_hex_distance(q1, r1, q2, r2):
    """Рассчитывает эвристическое расстояние между двумя гексами."""
    return (abs(q1 - q2) + abs(q1 + r1 - q2 - r2) + abs(r1 - r2)) / 2

def find_path(start_pos, goal_pos, game_map, occupied_hexes):
    """
    Улучшенная реализация A*, учитывающая стоимость и опасность гексов.
    :param start_pos: Кортеж (q, r) начала.
    :param goal_pos: Кортеж (q, r) цели.
    :param game_map: Словарь {(q, r): hex_data} со всей видимой картой.
    :param occupied_hexes: Множество {(q, r)} с занятыми гексами.
    :return: Список координат [(q, r), ...] или None.
    """
    open_list = [(0, start_pos)]
    came_from = {start_pos: None}
    g_cost = {start_pos: 0}

    while open_list:
        _, current_node = heapq.heappop(open_list)

        if current_node == goal_pos:
            path = []
            while current_node is not None:
                path.append(current_node)
                current_node = came_from[current_node]
            return path[::-1]

        q, r = current_node
        neighbors = [(q+1, r), (q-1, r), (q, r+1), (q, r-1), (q+1, r-1), (q-1, r+1)]

        for neighbor in neighbors:
            if neighbor not in game_map:
                continue

            hex_info = game_map[neighbor]
            if hex_info['type'] == 5 or (neighbor in occupied_hexes and neighbor != goal_pos):
                continue
            
            # Базовая стоимость передвижения из API
            move_cost = hex_info.get('cost', 1)
            # Добавляем большой штраф за кислоту, чтобы избегать её
            if hex_info['type'] == 4:
                move_cost += 15 # Штраф, чтобы предпочесть более длинный, но безопасный путь

            new_g_cost = g_cost[current_node] + move_cost

            if neighbor not in g_cost or new_g_cost < g_cost[neighbor]:
                g_cost[neighbor] = new_g_cost
                h_cost = _get_hex_distance(neighbor[0], neighbor[1], goal_pos[0], goal_pos[1])
                f_cost = new_g_cost + h_cost
                heapq.heappush(open_list, (f_cost, neighbor))
                came_from[neighbor] = current_node
    
    return None