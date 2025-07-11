import tkinter as tk
import math
import requests
from dotenv import load_dotenv
import os

load_dotenv()

# === Конфиг ===
API_URL = "https://games-test.datsteam.dev"
TOKEN = f"{os.getenv("TOKEN")}"
AUTH_HEADER = {"X-Auth-Token": TOKEN}

# === Цвета ===
TILE_COLORS = {
    1: "#cccccc",  # земля
    2: "#999999",  # камень
    3: "#666666",  # гора
    4: "#88cc88",  # лес
    5: "#ffcc00",  # болото / песок
}
ANT_COLORS = {
    0: "blue",     # Scout
    1: "red",      # Soldier
    2: "green",    # Worker
}
FOOD_COLOR = "orange"
HOME_COLOR = "cyan"

# === Размеры ===
HEX_SIZE = 20
HEX_HEIGHT = HEX_SIZE * 2
HEX_WIDTH = math.sqrt(3) / 2 * HEX_HEIGHT

def hex_to_pixel(q, r):
    x = HEX_WIDTH * (q + r / 2)
    y = HEX_HEIGHT * (3/4) * r
    return x, y

def draw_hex(canvas, x, y, size, fill):
    points = []
    for i in range(6):
        angle = math.radians(60 * i)
        px = x + size * math.cos(angle)
        py = y + size * math.sin(angle)
        points.extend((px, py))
    return canvas.create_polygon(points, outline="black", fill=fill)

def register():
    try:
        r = requests.post(f"{API_URL}/api/register", headers=AUTH_HEADER)
        r.raise_for_status()
        print("✅ Зарегистрирован:", r.json())
    except requests.RequestException as e:
        print("❌ Ошибка регистрации:", e)

def fetch_arena():
    try:
        r = requests.get(f"{API_URL}/api/arena", headers=AUTH_HEADER)
        if r.status_code == 400:
            print("ℹ️ Получен 400 — пробуем зарегистрироваться...")
            register()
            r = requests.get(f"{API_URL}/api/arena", headers=AUTH_HEADER)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        print("❌ Ошибка получения арены:", e)
        return {}

class ArenaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ant Arena Viewer")
        self.canvas = tk.Canvas(self, width=1000, height=800, bg="white")
        self.canvas.pack()
        self.after(1000, self.update_arena)  # запуск автообновления через 1с

    def update_arena(self):
        self.canvas.delete("all")  # очищаем перед перерисовкой
        self.draw_arena()
        self.after(2000, self.update_arena)  # повторно запускаем через 2 секунды

    def draw_arena(self):
        data = fetch_arena()
        tiles = data.get("map", [])
        ants = data.get("ants", [])
        food = data.get("food", [])
        homes = data.get("home", [])

        OFFSET_X, OFFSET_Y = 100, 100

        for tile in tiles:
            q, r = tile["q"], tile["r"]
            x, y = hex_to_pixel(q, r)
            x += OFFSET_X
            y += OFFSET_Y
            color = TILE_COLORS.get(tile["type"], "gray")
            draw_hex(self.canvas, x, y, HEX_SIZE, fill=color)

        for cell in homes:
            q, r = cell["q"], cell["r"]
            x, y = hex_to_pixel(q, r)
            x += OFFSET_X
            y += OFFSET_Y
            self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill=HOME_COLOR, outline="black")

        for f in food:
            q, r = f["q"], f["r"]
            x, y = hex_to_pixel(q, r)
            x += OFFSET_X
            y += OFFSET_Y
            self.canvas.create_rectangle(x - 5, y - 5, x + 5, y + 5, fill=FOOD_COLOR, outline="black")

        for ant in ants:
            q, r = ant["q"], ant["r"]
            x, y = hex_to_pixel(q, r)
            x += OFFSET_X
            y += OFFSET_Y
            color = ANT_COLORS.get(ant["type"], "black")
            self.canvas.create_oval(x - 6, y - 6, x + 6, y + 6, fill=color, outline="black")

if __name__ == "__main__":
    app = ArenaApp()
    app.mainloop()
