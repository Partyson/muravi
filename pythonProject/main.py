import tkinter as tk
from tkinter import Canvas
import math
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as patches
from dotenv import load_dotenv
import os

load_dotenv()


# Настройки
HEX_SIZE = 1
HEX_COLORS = {
    1: "lightblue",    # муравейник
    2: "lightgray",    # пустой
    3: "saddlebrown",  # грязь
    4: "green",        # кислота
    5: "black",        # камни
}
API_URL = "https://games-test.datsteam.dev"
AUTH_HEADER = {"X-Auth-Token": f"{os.getenv("TOKEN")}"}  # ← Замени на свой токен

# ---- Работа с координатами ----
def hex_to_pixel(q, r, size):
    x = size * 3 / 2 * q
    y = size * math.sqrt(3) * (r + 0.5 * (q % 2))
    return x, y

# ---- Рендер гекса ----
def draw_hex(ax, x, y, size, color):
    angles = [math.radians(60 * i) for i in range(6)]
    points = [(x + size * math.cos(a), y + size * math.sin(a)) for a in angles]
    hexagon = patches.Polygon(points, closed=True, edgecolor='gray', facecolor=color)
    ax.add_patch(hexagon)

def draw_unit(ax, x, y, icon, color='white'):
    circle = patches.Circle((x, y), 0.3, color=color, zorder=10)
    ax.add_patch(circle)
    ax.text(x, y, icon, ha='center', va='center', fontsize=8, zorder=11)

# ---- Основной рендер ----
def render_arena(arena):
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_aspect('equal')
    ax.axis('off')

    for tile in arena.get("map", []):
        q, r = tile["q"], tile["r"]
        x, y = hex_to_pixel(q, r, HEX_SIZE)
        tile_type = tile["type"]
        color = HEX_COLORS.get(tile_type, "white")
        draw_hex(ax, x, y, HEX_SIZE, color)

    for food in arena.get("food", []):
        x, y = hex_to_pixel(food["q"], food["r"], HEX_SIZE)
        draw_unit(ax, x, y, "🍗", color='orange')

    for ant in arena.get("ants", []):
        x, y = hex_to_pixel(ant["q"], ant["r"], HEX_SIZE)
        draw_unit(ax, x, y, "A", color='white')

    for enemy in arena.get("enemies", []):
        x, y = hex_to_pixel(enemy["q"], enemy["r"], HEX_SIZE)
        draw_unit(ax, x, y, "E", color='red')

    for home in arena.get("home", []):
        x, y = hex_to_pixel(home["q"], home["r"], HEX_SIZE)
        ax.add_patch(patches.Circle((x, y), 0.4, edgecolor='blue', facecolor='none', linewidth=2))

    spot = arena.get("spot", {"q": 0, "r": 0})
    x, y = hex_to_pixel(spot["q"], spot["r"], HEX_SIZE)
    ax.add_patch(patches.Circle((x, y), 0.5, edgecolor='cyan', linewidth=2, fill=False))

    ax.relim()
    ax.autoscale_view()
    return fig

# ---- Работа с API ----
def register():
    url = f"{API_URL}/api/register"
    response = requests.post(url, headers=AUTH_HEADER)
    response.raise_for_status()
    data = response.json()
    print("✅ Зарегистрирован:", data["name"], "| Realm:", data["realm"])
    return data

def fetch_arena():
    url = f"{API_URL}/api/arena"
    try:
        response = requests.get(url, headers=AUTH_HEADER)
        if response.status_code == 400:
            print("⚠️ Не зарегистрирован, пытаюсь зарегистрироваться...")
            register()
            response = requests.get(url, headers=AUTH_HEADER)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print("❌ Ошибка получения арены:", e)
        return {"map": [], "ants": [], "enemies": [], "food": [], "home": [], "spot": {"q": 0, "r": 0}}

def fetch_logs():
    url = f"{API_URL}/api/logs"
    try:
        response = requests.get(url, headers=AUTH_HEADER)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print("❌ Ошибка логов:", e)
        return []

# ---- Интерфейс ----
class ArenaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DatsPulse Arena Viewer")
        self.geometry("1000x800")

        self.canvas_frame = tk.Frame(self)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(self, height=8)
        self.log_text.pack(fill=tk.X)

        self.button = tk.Button(self, text="🔄 Обновить карту", command=self.refresh_map)
        self.button.pack(pady=5)

        self.refresh_map()

    def plot_arena(self, arena_data):
        fig = render_arena(arena_data)
        self.chart = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        self.chart.draw()
        self.chart.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def show_logs(self, logs):
        self.log_text.delete("1.0", tk.END)
        for entry in logs:
            self.log_text.insert(tk.END, f"{entry['time']} — {entry['message']}\n")

    def refresh_map(self):
        if hasattr(self, 'chart'):
            self.chart.get_tk_widget().destroy()
        arena = fetch_arena()
        logs = fetch_logs()
        self.plot_arena(arena)
        self.show_logs(logs)

if __name__ == "__main__":
    app = ArenaApp()
    app.mainloop()