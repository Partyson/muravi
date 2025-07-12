import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np

# --- НАСТРОЙКИ ВИЗУАЛИЗАЦИИ ---

# Цвета для разных типов гексов (константы из API)
HEX_TYPE_COLORS = {
    1: '#FFD700',  # 1: Муравейник (золотой)
    2: '#FFFFFF',  # 2: Пустой (белый)
    3: '#A0522D',  # 3: Грязь (коричневый)
    4: '#90EE90',  # 4: Кислота (светло-зеленый)
    5: '#808080',  # 5: Камни (серый)
}

# Обозначения для типов юнитов (константы из API)
ANT_TYPE_SYMBOLS = {
    0: 'W',  # 0: Рабочий
    1: 'F',  # 1: Боец
    2: 'S',  # 2: Разведчик
}
ANT_TYPE_NAMES = {
    0: 'Рабочий',
    1: 'Боец',
    2: 'Разведчик',
}

# Цвета для ресурсов (константы из API)
FOOD_TYPE_COLORS = {
    1: 'red',      # 1: Яблоко
    2: 'orange',   # 2: Хлеб
    3: '#FFC0CB'   # 3: Нектар (хотя на карте он не появляется)
}
FOOD_TYPE_SYMBOLS = {
    1: '🍎',
    2: '🍞',
}


# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

def axial_to_pixel(q, r, size):
    """Конвертирует аксиальные координаты гекса в пиксельные (x, y) для отрисовки."""
    x = size * (3. / 2. * q)
    y = size * (np.sqrt(3) / 2. * q + np.sqrt(3) * r)
    return x, y

def draw_hexagon(ax, q, r, size, color, edgecolor='black', linewidth=1):
    """Рисует один гекс на холсте."""
    x, y = axial_to_pixel(q, r, size)
    corners = []
    for i in range(6):
        angle_deg = 60 * i - 30
        angle_rad = np.pi / 180 * angle_deg
        corners.append((x + size * np.cos(angle_rad), y + size * np.sin(angle_rad)))
    
    poly = Polygon(corners, facecolor=color, edgecolor=edgecolor, linewidth=linewidth)
    ax.add_patch(poly)


# --- ОСНОВНАЯ ФУНКЦИЯ ВИЗУАЛИЗАЦИИ ---

def visualize_map(api_data, save_to_file=None):
    """
    Главная функция, которая принимает данные из /api/arena и генерирует карту.
    
    :param api_data: Словарь с данными из ответа API /api/arena.
    :param save_to_file: Если указано имя файла (напр. 'map.png'), карта будет сохранена, а не показана.
    """
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_aspect('equal')
    hex_size = 1.0  # Базовый размер гекса

    # 1. Рисуем видимые гексы карты
    if 'map' in api_data and api_data['map']:
        for hex_data in api_data['map']:
            q, r = hex_data['q'], hex_data['r']
            hex_type = hex_data['type']
            color = HEX_TYPE_COLORS.get(hex_type, '#E0E0E0') # Серый для неизвестных типов
            draw_hexagon(ax, q, r, hex_size, color)
    
    # 2. Выделяем гексы своего муравейника
    if 'home' in api_data and api_data['home']:
        home_coords = {(h['q'], h['r']) for h in api_data['home']}
        spot_coord = (api_data['spot']['q'], api_data['spot']['r']) if 'spot' in api_data else None

        for q, r in home_coords:
            # Делаем рамку муравейника толще и другого цвета
            draw_hexagon(ax, q, r, hex_size, HEX_TYPE_COLORS[1], edgecolor='blue', linewidth=3)
            if (q, r) == spot_coord:
                # Особо выделяем главный гекс (точку спавна)
                x, y = axial_to_pixel(q, r, hex_size)
                ax.text(x, y, '★', ha='center', va='center', fontsize=20, color='blue', zorder=10)

    # 3. Рисуем ресурсы (еду)
    if 'food' in api_data and api_data['food']:
        for food_data in api_data['food']:
            q, r = food_data['q'], food_data['r']
            food_type = food_data['type']
            x, y = axial_to_pixel(q, r, hex_size)
            symbol = FOOD_TYPE_SYMBOLS.get(food_type, '?')
            ax.text(x, y, symbol, ha='center', va='center', fontsize=15, zorder=5)

    # 4. Рисуем врагов
    if 'enemies' in api_data and api_data['enemies']:
        for enemy in api_data['enemies']:
            q, r = enemy['q'], enemy['r']
            x, y = axial_to_pixel(q, r, hex_size)
            symbol = ANT_TYPE_SYMBOLS.get(enemy['type'], '?')
            ax.text(x, y + 0.3, f'E-{symbol}', ha='center', va='center', color='red', fontsize=10, weight='bold', zorder=8)
            ax.text(x, y - 0.3, f"{enemy['health']}", ha='center', va='center', color='red', fontsize=8, zorder=8)


    # 5. Рисуем своих юнитов и их маршруты
    if 'ants' in api_data and api_data['ants']:
        for ant in api_data['ants']:
            q, r = ant['q'], ant['r']
            symbol = ANT_TYPE_SYMBOLS.get(ant['type'], '?')
            health = ant['health']
            
            # Рисуем запланированный маршрут
            if ant.get('move'):
                path_coords = [(p['q'], p['r']) for p in ant['move']]
                path_pixels = [axial_to_pixel(pq, pr, hex_size) for pq, pr in path_coords]
                if path_pixels:
                    path_x, path_y = zip(*path_pixels)
                    ax.plot(path_x, path_y, 'b-', linewidth=2, alpha=0.7, zorder=7) # Синяя линия
            
            # Рисуем самого юнита
            x, y = axial_to_pixel(q, r, hex_size)
            ax.text(x, y + 0.3, symbol, ha='center', va='center', color='blue', fontsize=12, weight='bold', zorder=9)
            ax.text(x, y - 0.3, f"{health}", ha='center', va='center', color='blue', fontsize=8, zorder=9)
            # Отображаем, если юнит несет еду
            if ant.get('food') and ant['food']['amount'] > 0:
                food_symbol = FOOD_TYPE_SYMBOLS.get(ant['food']['type'], '?')
                ax.text(x, y, food_symbol, ha='center', va='center', fontsize=10, zorder=10, alpha=0.8)


    # Настройка отображения
    ax.autoscale_view()
    ax.set_title(f"Карта на ход: {api_data.get('turnNo', 'N/A')}. Ваш счет: {api_data.get('score', 0)}", fontsize=16)
    ax.set_xlabel("q-координата (примерно)")
    ax.set_ylabel("r-координата (примерно)")
    plt.grid(False)
    ax.invert_yaxis() # Часто удобнее, чтобы (0,0) был в левом верхнем углу

    if save_to_file:
        plt.savefig(save_to_file, bbox_inches='tight', dpi=150)
        print(f"Карта сохранена в файл: {save_to_file}")
        plt.close(fig) # Закрываем, чтобы не накапливать в памяти
    else:
        plt.show()

# --- ПРИМЕР ИСПОЛЬЗОВАНИЯ ---

if __name__ == '__main__':
    # ЭТО МОК-ДАННЫЕ. ЗАМЕНИТЕ ИХ РЕАЛЬНЫМ ОТВЕТОМ ОТ /api/arena
    mock_api_data = {
      "ants": [
        {"id": "uuid-worker-1", "type": 0, "q": 1, "r": 0, "health": 130, "food": {"amount": 5, "type": 1}, "move": [{"q": 1, "r":-1}, {"q": 0, "r": 0}]},
        {"id": "uuid-fighter-1", "type": 1, "q": 2, "r": -1, "health": 180, "food": None, "move": []},
        {"id": "uuid-scout-1", "type": 2, "q": 3, "r": 0, "health": 80, "food": None, "move": []}
      ],
      "enemies": [
        {"type": 1, "q": 4, "r": 0, "health": 150, "food": None}
      ],
      "food": [
        {"q": 5, "r": 0, "type": 1, "amount": 10},
        {"q": 2, "r": 2, "type": 2, "amount": 20}
      ],
      "home": [
        {"q": 0, "r": 0},
        {"q": 0, "r": -1},
        {"q": 1, "r": -1}
      ],
      "map": [
        {"q": 0, "r": 0, "type": 1, "cost": 1}, {"q": 0, "r": -1, "type": 1, "cost": 1}, {"q": 1, "r": -1, "type": 1, "cost": 1},
        {"q": 1, "r": 0, "type": 2, "cost": 1}, {"q": 2, "r": -1, "type": 2, "cost": 1}, {"q": 2, "r": 0, "type": 3, "cost": 2},
        {"q": 3, "r": 0, "type": 2, "cost": 1}, {"q": 4, "r": 0, "type": 4, "cost": 1}, {"q": 5, "r": 0, "type": 2, "cost": 1},
        {"q": 3, "r": 1, "type": 5, "cost": 999}, {"q": 2, "r": 2, "type": 2, "cost": 1}
      ],
      "nextTurnIn": 1.5,
      "score": 60,
      "spot": {"q": 0, "r": 0},
      "turnNo": 77
    }

    print("Генерация карты на основе тестовых данных...")
    # Чтобы показать карту в окне:
    visualize_map(mock_api_data)
    
    # Чтобы сохранить карту в файл (полезно для бота, чтобы следить за историей):
    # filename = f"turn_{mock_api_data['turnNo']}.png"
    # visualize_map(mock_api_data, save_to_file=filename)