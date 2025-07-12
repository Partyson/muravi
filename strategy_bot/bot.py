# bot.py
import requests
import time
import os
import datetime
# --- Импортируем наши модули ---
from strategy import decide_moves
from visualizer import visualize_map

# --- НАСТРОЙКИ ---
API_TOKEN = "1abe6497-6bcd-4e16-baa1-8de4c2e5f357" 
BASE_URL = "https://games-test.datsteam.dev"
HEADERS = {'X-Auth-Token': API_TOKEN, 'Content-Type': 'application/json'}

# Создаем папки, если их нет
if not os.path.exists('maps'):
    os.makedirs('maps')
if not os.path.exists('logs'):
    os.makedirs('logs')


def register_for_round():
    """Отправляет запрос на регистрацию и возвращает время до начала раунда."""
    print("[ДЕЙСТВИЕ] Попытка регистрации на текущий раунд...")
    url = f"{BASE_URL}/api/register"
    try:
        response = requests.post(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            wait_time = data.get('nextTurn', 5.0)
            print(f"[УСПЕХ] Регистрация прошла успешно!")
            return wait_time
        else:
            if response.status_code == 404:
                print("[ИНФО] Регистрация на раунд сейчас не открыта (ошибка 404).")
            else:
                message = response.text.strip()
                print(f"[ОШИБКА] Не удалось зарегистрироваться. Статус: {response.status_code}. Причина: '{message}'")
            return None
    except requests.RequestException as e:
        print(f"[КРИТИЧЕСКАЯ ОШИБКА] При попытке регистрации: {e}")
        return None

def fetch_and_write_logs(log_file_handle, last_logged_turn):
    """Запрашивает логи с сервера и дописывает новые в файл."""
    try:
        response = requests.get(f"{BASE_URL}/api/logs", headers=HEADERS)
        response.raise_for_status()
        logs = response.json()
        new_max_turn = last_logged_turn
        written_headers = set()
        for log_entry in sorted(logs, key=lambda x: x.get('tick', 0)):
            turn = log_entry.get('tick')
            if turn is None:
                continue
            if turn > last_logged_turn:
                if turn not in written_headers:
                    log_file_handle.write(f"\n--- Turn {turn} ---\n")
                    written_headers.add(turn)
                message = log_entry.get('message', 'No message content')
                log_file_handle.write(f"[LOG] {message}\n")
                new_max_turn = max(new_max_turn, turn)
        log_file_handle.flush()
        return new_max_turn
    except requests.RequestException as e:
        print(f"[ОШИБКА] Не удалось получить логи: {e}")
        return last_logged_turn
    except requests.exceptions.JSONDecodeError:
        print("[ОШИБКА] Ответ от /api/logs не является корректным JSON.")
        return last_logged_turn

def get_arena_state():
    """Получает текущее состояние арены."""
    try:
        response = requests.get(f"{BASE_URL}/api/arena", headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"[ОШИБКА] Не удалось получить состояние арены: {e}")
        return None

def send_moves(moves):
    """Отправляет ходы на сервер."""
    if not moves:
        print("[ИНФО] Нет ходов для отправки.")
        return
    try:
        data = {"moves": moves}
        response = requests.post(f"{BASE_URL}/api/move", headers=HEADERS, json=data)
        response.raise_for_status()
        print(f"[ИНФО] Ходы ({len(moves)}) успешно отправлены. Статус: {response.status_code}")
    except requests.RequestException as e:
        print(f"[ОШИБКА] При отправке ходов: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Тело ответа: {e.response.text}")

def main_loop():
    """Главный игровой цикл с логированием."""
    timestamp = datetime.datetime.now().strftime("%Y-m-%d_%H-%M-%S")
    log_filename = f"logs/round_{timestamp}.log"
    print(f"\n[ИНФО] Логи для этого раунда будут сохранены в: {log_filename}")
    last_logged_turn = -1
    with open(log_filename, 'w', encoding='utf-8') as log_file:
        print("[ИНФО] Запуск основного игрового цикла...")
        while True:
            game_state = get_arena_state()
            if not game_state:
                time.sleep(2)
                continue
            last_logged_turn = fetch_and_write_logs(log_file, last_logged_turn)
            turn = game_state.get('turnNo', 0)
            if turn == 0 and not game_state.get('ants'):
                 log_file.write("\n--- Раунд завершен ---\n")
                 print("[ИНФО] Раунд, похоже, завершен. Завершение работы игрового цикла.")
                 break
            score = game_state.get('score', 0)
            next_turn_in = game_state.get('nextTurnIn', 2.0)
            
            print(f"\n--- Ход: {turn} | Счет: {score} | Стратегия: Роевое Наступление | След. ход через: {next_turn_in:.2f}с ---")
            
            map_filename = f"maps/turn_{turn:03d}.png"
            visualize_map(game_state, save_to_file=map_filename)
            print("[ДЕЙСТВИЕ] Анализ ситуации и принятие решений...")
            moves_to_make = decide_moves(game_state)
            send_moves(moves_to_make)
            sleep_duration = max(0, next_turn_in - 0.2)
            time.sleep(sleep_duration)

if __name__ == "__main__":
    if "СУПЕР_СЕКРЕТНЫЙ" in API_TOKEN:
        print("!!! ВНИМАНИЕ: Пожалуйста, укажите ваш API_TOKEN в файле bot.py !!!")
    else:
        print("[ИНФО] Запуск бота в режиме ожидания регистрации...")
        attempt_count = 1
        wait_duration = None
        while True:
            print(f"\n--- Попытка регистрации №{attempt_count} ---")
            wait_duration = register_for_round()
            if wait_duration is not None:
                break
            else:
                print("[ИНФО] Следующая попытка через 60 секунд.")
                time.sleep(60)
                attempt_count += 1
        
        print(f"\n[ИНФО] Ожидание начала раунда ({wait_duration:.2f} сек)...")
        time.sleep(max(0, wait_duration + 0.2))
        main_loop()