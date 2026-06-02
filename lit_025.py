import pygame
import math
import random
import sys
import json
import os
 
# --- KONFIGURACE ---
WIDTH, HEIGHT = 1100, 700
FPS = 60

# Globální seznam pro hvězdy (musí být nadefinován hned na začátku)
stars = []

# Velikosti zón okolo stanic
# Barvy
# ... (rest of file unchanged)
# Save file
STATION_PERMIT_RADIUS = 220    # Vnější zóna (omezuje rychlost)
STATION_LANDING_RADIUS = 60    # Vnitřní zóna (hned otevírá obchod)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_FILE = os.path.join(SCRIPT_DIR, "savegame.json")
load_on_start = False
 
# Barvy
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 150)
RED = (255, 50, 50)
YELLOW = (255, 215, 0)
BLUE = (50, 150, 255)
 
# Obchodovatelné komodity a jejich základní ceny
GOODS = ["Meat", "Table", "Food", "Ore", "Spices"]
BASE_PRICES = {
    "Meat": 40,
    "Table": 70,
    "Food": 35,
    "Ore": 55,
    "Spices": 75
}
 
pygame.init()
clock = pygame.time.Clock()
font = pygame.font.SysFont("Consolas", 18)
 
RESOLUTION_OPTIONS = [
    ((800, 600), "800 x 600"),
    ((1000, 600), "1000 x 600"),
    ((1100, 700), "1100 x 700"),  # Bezpečnější výchozí rozlišení
    (None, "Fullscreen")
]
 
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Elite Python: WSAD Edition")
 
# --- TŘÍDA PRO HRÁČE ---
class Player:
    def __init__(self):
        self.x, self.y = 0, 0  # Globální pozice ve vesmíru
        self.angle = 90
        self.vel_x, self.vel_y = 0, 0
        self.thrust = 0.2
        self.friction = 0.98
        self.fuel = 100.0
        self.credits = 500
        self.cargo = {item: 0 for item in GOODS}
        self.max_cargo = 20
 
    def update(self):
        keys = pygame.key.get_pressed()
        
        # Rotace (A a D)
        if keys[pygame.K_a]: self.angle += 4
        if keys[pygame.K_d]: self.angle -= 4
        
        # Pohyb vpřed (W)
        if keys[pygame.K_w] and self.fuel > 0:
            rad = math.radians(self.angle)
            self.vel_x += math.cos(rad) * self.thrust
            self.vel_y -= math.sin(rad) * self.thrust
            self.fuel -= 0.03
        
        # Brzda (S)
        if keys[pygame.K_s]:
            self.vel_x *= 0.92
            self.vel_y *= 0.92
 
        # Aplikace pohybu a tření
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_x *= self.friction
        self.vel_y *= self.friction
 
    def cargo_total(self):
        return sum(self.cargo.values())

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "angle": self.angle,
            "vel_x": self.vel_x,
            "vel_y": self.vel_y,
            "fuel": self.fuel,
            "credits": self.credits,
            "cargo": self.cargo,
            "max_cargo": self.max_cargo
        }

    @classmethod
    def from_dict(cls, data):
        p = cls()
        p.x = data.get("x", 0)
        p.y = data.get("y", 0)
        p.angle = data.get("angle", 90)
        p.vel_x = data.get("vel_x", 0)
        p.vel_y = data.get("vel_y", 0)
        p.fuel = data.get("fuel", 100.0)
        p.credits = data.get("credits", 0)
        p.cargo = data.get("cargo", {item: 0 for item in GOODS})
        p.max_cargo = data.get("max_cargo", 20)
        return p
 
# --- GENEROVÁNÍ VESMÍRU ---
player = Player()
 
# Náhodné stanice v obrovském prostoru s rovnoměrným rozmístěním
stations = []
station_names = [
    "Alpha", "Bravo", "Gamma", "Delta", "Echo", "Omega",
    "Nova", "Sierra", "Vega", "Orion", "Atlas", "Titan",
    "Helix", "Cosmo", "Luna", "Pulsar", "Aurora", "Zenith"
]
station_range = 12000
min_station_distance = 1400
for name in station_names:
    placed = False
    for _ in range(40):
        x = random.randint(-station_range, station_range)
        y = random.randint(-station_range, station_range)
        if all(math.hypot(x - s["x"], y - s["y"]) >= min_station_distance for s in stations):
            prices = {}
            for good in GOODS:
                base = BASE_PRICES[good]
                buy_price = max(5, base + random.randint(-15, 20))
                sell_price = max(1, buy_price - random.randint(10, 25))
                prices[good] = {"buy": buy_price, "sell": sell_price}
            stations.append({
                "name": f"Station {name}",
                "x": x,
                "y": y,
                "prices": prices,
                "fuel_price": 8
            })
            placed = True
            break
    if not placed:
        prices = {}
        for good in GOODS:
            base = BASE_PRICES[good]
            buy_price = max(5, base + random.randint(-15, 20))
            sell_price = max(1, buy_price - random.randint(10, 25))
            prices[good] = {"buy": buy_price, "sell": sell_price}
        stations.append({
            "name": f"Station {name}",
            "x": random.randint(-station_range, station_range),
            "y": random.randint(-station_range, station_range),
            "prices": prices,
            "fuel_price": 8
        })


def save_game(player_obj, stations_obj):
    try:
        data = {
            "player": player_obj.to_dict(),
            "stations": stations_obj
        }
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Failed to save game:", e)


def load_game():
    if not os.path.exists(SAVE_FILE):
        return None
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        player_data = data.get("player")
        stations_data = data.get("stations")
        if player_data is None or stations_data is None:
            return None
        p = Player.from_dict(player_data)
        return p, stations_data
    except Exception as e:
        print("Failed to load save:", e)
        return None


def delete_save():
    try:
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)
    except Exception as e:
        print("Failed to delete save:", e)
 
def create_screen(resolution):
    global WIDTH, HEIGHT, screen
    if resolution is None:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        WIDTH, HEIGHT = screen.get_size()
    else:
        WIDTH, HEIGHT = resolution
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Elite Python: WSAD Edition")
    return screen
 
def draw_centered(text, y, color=WHITE):
    img = font.render(text, True, color)
    screen.blit(img, ((WIDTH - img.get_width()) // 2, y))
 
def draw_ship_icon(surface, x, y, scale=1.0, angle=0.0, color=GREEN):
    rad = math.radians(angle)
    nose = (x + math.cos(rad) * 38 * scale, y - math.sin(rad) * 38 * scale)
    left_wing = (x + math.cos(rad + 2.4) * 22 * scale, y - math.sin(rad + 2.4) * 22 * scale)
    right_wing = (x + math.cos(rad - 2.4) * 22 * scale, y - math.sin(rad - 2.4) * 22 * scale)
    back_left = (x + math.cos(rad + 3.4) * 18 * scale, y - math.sin(rad + 3.4) * 18 * scale)
    back_right = (x + math.cos(rad - 3.4) * 18 * scale, y - math.sin(rad - 3.4) * 18 * scale)
    body = [nose, left_wing, back_left, back_right, right_wing]
    pygame.draw.polygon(surface, color, body)
    thruster = [
        (x + math.cos(rad + math.pi) * 12 * scale, y - math.sin(rad + math.pi) * 12 * scale),
        (x + math.cos(rad + 2.8) * 18 * scale, y - math.sin(rad + 2.8) * 18 * scale),
        (x + math.cos(rad - 2.8) * 18 * scale, y - math.sin(rad - 2.8) * 18 * scale)
    ]
    pygame.draw.polygon(surface, RED, thruster)
    pygame.draw.circle(surface, (230, 230, 255), (int(x + math.cos(rad) * 6 * scale), int(y - math.sin(rad) * 6 * scale)), int(4 * scale))
 
selected_resolution = 2  # Nastaveno na index 2 (1100x700) jako bezpečný střed
resolution_options = RESOLUTION_OPTIONS
 
def show_menu(selected_resolution):
    menu_mode = "main"
    menu_index = 0
    menu_stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(0.2, 0.8)] for _ in range(90)]
    while True:
        screen.fill(BLACK)
        menu_buttons = []
        current_time = pygame.time.get_ticks()
        ship_angle = (current_time * 0.02) % 360
 
        # Background grid and stars
        for x in range(0, WIDTH, 120):
            pygame.draw.line(screen, (10, 10, 20), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, 120):
            pygame.draw.line(screen, (10, 10, 20), (0, y), (WIDTH, y))
 
        for star in menu_stars:
            star[0] += star[2]
            if star[0] > WIDTH:
                star[0] = 0
                star[1] = random.randint(0, HEIGHT)
            pygame.draw.circle(screen, (180, 220, 255), (int(star[0]), int(star[1])), 2)
 
        glow = int(10 + 6 * math.sin(current_time * 0.004))
        pygame.draw.circle(screen, (20, 40, 80), (WIDTH // 2, 170), 170, 1)
        pygame.draw.circle(screen, (30, 60, 110), (WIDTH // 2, 170), 140, 1)
 
        draw_ship_icon(screen, WIDTH // 2, 170, scale=1.5, angle=ship_angle, color=(120, 220, 255))
        draw_centered("ELITE PYTHON", 64, YELLOW)
        draw_centered("Pilot your ship through space and dock at stations", 100, WHITE)
 
        save_exists = os.path.exists(SAVE_FILE)
        if menu_mode == "main":
            if save_exists:
                button_labels = ["Continue", "New Game", "Settings", "Quit"]
            else:
                button_labels = ["Start Game", "Settings", "Quit"]
            for idx, label in enumerate(button_labels):
                rect = pygame.Rect((WIDTH // 2 - 175, 260 + idx * 80, 350, 60))
                menu_buttons.append(("main", idx, rect))
                color = (55, 140, 210) if idx != menu_index else (100, 220, 170)
                pygame.draw.rect(screen, color, rect, border_radius=18)
                pygame.draw.rect(screen, (220, 220, 220), rect, 2, border_radius=18)
                screen.blit(font.render(label, True, BLACK), (rect.x + 120, rect.y + 18))
        else:
            draw_centered("Settings", 140, YELLOW)
            draw_centered("Choose resolution", 168, WHITE)
            for idx, (_, label) in enumerate(resolution_options):
                rect = pygame.Rect((WIDTH // 2 - 210, 240 + idx * 70, 420, 55))
                menu_buttons.append(("resolution", idx, rect))
                color = (55, 140, 210) if idx != selected_resolution else (100, 220, 170)
                pygame.draw.rect(screen, color, rect, border_radius=16)
                pygame.draw.rect(screen, (220, 220, 220), rect, 2, border_radius=16)
                screen.blit(font.render(label, True, BLACK), (rect.x + 20, rect.y + 16))
            back_rect = pygame.Rect((WIDTH // 2 - 90, 240 + len(resolution_options) * 70, 180, 55))
            menu_buttons.append(("back", None, back_rect))
            pygame.draw.rect(screen, RED, back_rect, border_radius=16)
            pygame.draw.rect(screen, (220, 220, 220), back_rect, 2, border_radius=16)
            screen.blit(font.render("Back", True, BLACK), (back_rect.x + 60, back_rect.y + 16))
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if menu_mode == "settings":
                        menu_mode = "main"
                        menu_index = 0
                    else:
                        pygame.quit()
                        sys.exit()
                elif event.key == pygame.K_DOWN:
                    max_index = len(menu_buttons) - 1
                    menu_index = min(menu_index + 1, max_index)
                elif event.key == pygame.K_UP:
                    menu_index = max(menu_index - 1, 0)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    kind, idx, _ = menu_buttons[menu_index]
                    if kind == "main":
                        label = button_labels[idx]
                        if label == "Continue":
                            global load_on_start
                            load_on_start = True
                            return selected_resolution
                        elif label == "New Game":
                            delete_save()
                            load_on_start = False
                            return selected_resolution
                        elif label == "Start Game":
                            load_on_start = False
                            return selected_resolution
                        elif label == "Settings":
                            menu_mode = "settings"
                            menu_index = selected_resolution
                        else:
                            pygame.quit()
                            sys.exit()
                    elif kind == "resolution":
                        selected_resolution = idx
                    elif kind == "back":
                        menu_mode = "main"
                        menu_index = 0
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for kind, idx, rect in menu_buttons:
                    if rect.collidepoint(mx, my):
                        if kind == "main":
                            label = button_labels[idx]
                            if label == "Continue":
                                load_on_start = True
                                return selected_resolution
                            elif label == "New Game":
                                delete_save()
                                load_on_start = False
                                return selected_resolution
                            elif label == "Start Game":
                                load_on_start = False
                                return selected_resolution
                            elif label == "Settings":
                                menu_mode = "settings"
                                menu_index = selected_resolution
                            else:
                                pygame.quit()
                                sys.exit()
                        elif kind == "resolution":
                            selected_resolution = idx
                        elif kind == "back":
                            menu_mode = "main"
                            menu_index = 0
                        break
 
        pygame.display.flip()
        clock.tick(FPS)
 
def run_game():
    global selected_good, trade_message, stars
    selected_good = 0
    trade_message = ""
    while True:
        screen.fill(BLACK)
 
        market_station = None
        market_buttons = []
        market_line_rects = []
        fuel_button = None
        
        # Šířka celého panelu zvětšena na 700 px, aby se tam vše pohodlně vešlo
        panel_w = 700
        panel_x = WIDTH // 2 - panel_w // 2
        panel_y = HEIGHT // 2 - 180

        in_permit_zone = False
        in_landing_zone = False

        for s in stations:
            dist = math.hypot(player.x - s["x"], player.y - s["y"])
            if dist < STATION_PERMIT_RADIUS:
                in_permit_zone = True
            if dist < STATION_LANDING_RADIUS:
                in_landing_zone = True
                market_station = s  

        # Omezovač rychlosti
        if in_permit_zone and not in_landing_zone:
            speed = math.hypot(player.vel_x, player.vel_y)
            max_zone_speed = 2.8
            if speed > max_zone_speed:
                scale = max_zone_speed / speed
                player.vel_x *= scale
                player.vel_y *= scale
 
        if market_station:
            for idx, good in enumerate(GOODS):
                y = panel_y + 70 + idx * 45
                market_line_rects.append(pygame.Rect(panel_x + 20, y, 660, 36))
                # Tlačítka posunuta doprava a přesně zarovnána
                market_buttons.append(("buy", idx, good, pygame.Rect(panel_x + 440, y + 4, 100, 28)))
                market_buttons.append(("sell", idx, good, pygame.Rect(panel_x + 560, y + 4, 100, 28)))
            fuel_button = pygame.Rect(panel_x + 440, panel_y + 70 + len(GOODS) * 45 + 5, 220, 34)
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game(player, stations)
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                save_game(player, stations)
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and market_station:
                trade_message = ""
                mx, my = event.pos
                for idx, rect in enumerate(market_line_rects):
                    if rect.collidepoint(mx, my):
                        selected_good = idx
                        break
                for action, idx, good, rect in market_buttons:
                    if rect.collidepoint(mx, my):
                        price = market_station["prices"][good]
                        if action == "buy":
                            if player.credits >= price["buy"] and player.cargo_total() < player.max_cargo:
                                player.credits -= price["buy"]
                                player.cargo[good] += 1
                                trade_message = f"Bought 1 {good} for {price['buy']}cr"
                            else:
                                trade_message = "Not enough credits or cargo space"
                        elif action == "sell":
                            if player.cargo[good] > 0:
                                player.credits += price["sell"]
                                player.cargo[good] -= 1
                                trade_message = f"Sold 1 {good} for {price['sell']}cr"
                            else:
                                trade_message = "No cargo to sell"
                        selected_good = idx
                        break
                if fuel_button and fuel_button.collidepoint(mx, my):
                    if player.credits >= market_station["fuel_price"] and player.fuel < 100:
                        player.credits -= market_station["fuel_price"]
                        player.fuel = min(100, player.fuel + 10)
                        trade_message = f"Refueled 10% for {market_station['fuel_price']}cr"
                    else:
                        trade_message = "Cannot refuel"
 
        player.update()
 
        # 1. VYKRESLENÍ HVĚZD
        for s in stars:
            sx = (s[0] - player.x * 0.1) % WIDTH
            sy = (s[1] - player.y * 0.1) % HEIGHT
            pygame.draw.circle(screen, WHITE, (int(sx), int(sy)), 1)
 
        # 2. VYKRESLENÍ STANIC
        for s in stations:
            screen_x = s["x"] - player.x + WIDTH // 2
            screen_y = s["y"] - player.y + HEIGHT // 2
            if -300 < screen_x < WIDTH + 300 and -300 < screen_y < HEIGHT + 300:
                center_x = int(screen_x + 15)
                center_y = int(screen_y + 15)
                
                pygame.draw.circle(screen, (70, 70, 140), (center_x, center_y), STATION_PERMIT_RADIUS, 1)
                pygame.draw.circle(screen, (120, 120, 220), (center_x, center_y), STATION_LANDING_RADIUS, 1)
                
                pygame.draw.rect(screen, YELLOW, (screen_x, screen_y, 30, 30), 2)
                pygame.draw.circle(screen, YELLOW, (center_x, center_y), 5)
                lbl = font.render(f"{s['name']}", True, YELLOW)
                screen.blit(lbl, (screen_x - 40, screen_y - 25))
 
        # 3. VYKRESLENÍ HRÁČE
        p_rad = math.radians(player.angle)
        p_pts = [
            (WIDTH//2 + math.cos(p_rad)*18, HEIGHT//2 - math.sin(p_rad)*18),
            (WIDTH//2 + math.cos(p_rad+2.6)*14, HEIGHT//2 - math.sin(p_rad+2.6)*14),
            (WIDTH//2 + math.cos(p_rad-2.6)*14, HEIGHT//2 - math.sin(p_rad-2.6)*14)
        ]
        pygame.draw.polygon(screen, GREEN, p_pts, 2)
        if pygame.key.get_pressed()[pygame.K_w] and player.fuel > 0:
            flame_pts = [
                (WIDTH//2 + math.cos(p_rad+3.14)*10, HEIGHT//2 - math.sin(p_rad+3.14)*10),
                (WIDTH//2 + math.cos(p_rad+2.8)*15, HEIGHT//2 - math.sin(p_rad+2.8)*15),
                (WIDTH//2 + math.cos(p_rad-2.8)*15, HEIGHT//2 - math.sin(p_rad-2.8)*15)
            ]
            pygame.draw.polygon(screen, RED, flame_pts)
 
        # 4. MINIMAPA
        map_size = 160
        map_x, map_y = WIDTH - map_size - 20, 20
        pygame.draw.rect(screen, (30, 30, 30), (map_x, map_y, map_size, map_size))
        pygame.draw.rect(screen, BLUE, (map_x, map_y, map_size, map_size), 1)
        pygame.draw.circle(screen, GREEN, (map_x + map_size//2, map_y + map_size//2), 2)
        for s in stations:
            rx = (s['x'] - player.x) * 0.01 + map_x + map_size//2
            ry = (s['y'] - player.y) * 0.01 + map_y + map_size//2
            if map_x < rx < map_x + map_size and map_y < ry < map_y + map_size:
                pygame.draw.circle(screen, YELLOW, (int(rx), int(ry)), 2)
 
        # HUD Texty
        ui_y = 20
        cargo_text = ", ".join(f"{name} x{count}" for name, count in player.cargo.items() if count) or "Empty"
        
        if in_landing_zone: zone_status = ("ZONE: Market Open", GREEN)
        elif in_permit_zone: zone_status = ("ZONE: Speed Limit Active", (180, 180, 0))
        else: zone_status = ("ZONE: Open Space", RED)

        info = [
            (f"CREDITS: {player.credits}", WHITE),
            (f"FUEL: {int(player.fuel)}%", RED if player.fuel < 20 else GREEN),
            (f"CARGO: {cargo_text}", WHITE),
            (f"POS: {int(player.x)}, {int(player.y)}", BLUE),
            zone_status
        ]
        for text, color in info:
            screen.blit(font.render(text, True, color), (20, ui_y))
            ui_y += 25
 
        # 5. NOVÝ OBCHODNÍ PANEL (PODLE PŘEDLOHY)
        if market_station:
            panel_h = 80 + len(GOODS) * 45 + 85
            # Tmavé pozadí panelu
            pygame.draw.rect(screen, (10, 10, 18), (panel_x, panel_y, panel_w, panel_h))
            pygame.draw.rect(screen, BLUE, (panel_x, panel_y, panel_w, panel_h), 1)
            
            # Hlavní nadpisy navrchu
            title = font.render(f"{market_station['name']} Market", True, YELLOW)
            screen.blit(title, (panel_x + 20, panel_y + 15))
            
            fuel_text = font.render(f"Fuel refill: 10% for {market_station['fuel_price']}cr", True, WHITE)
            screen.blit(fuel_text, (panel_x + 20, panel_y + 40))
 
            # Tabulkový výpis komodit
            for idx, good in enumerate(GOODS):
                price = market_station['prices'][good]
                y = panel_y + 70 + idx * 45
                
                # Výběr pozadí řádku (aktivní komodita má lehce světlejší nádech)
                item_bg = (30, 30, 50) if idx == selected_good else (15, 15, 25)
                pygame.draw.rect(screen, item_bg, (panel_x + 20, y, 660, 36))
                pygame.draw.rect(screen, WHITE, (panel_x + 20, y, 660, 36), 1) # Bílé ohraničení řádku
                
                # Formátování textu přesně do jedné linie a sloupců (včetně počtu kusů v nákladním prostoru)
                good_label = f"{idx+1}. {good:<6}"
                buy_label = f"BUY {price['buy']:<3}"
                sell_label = f"SELL {price['sell']:<3}"
                inv_label = f"Hold: {player.cargo[good]}"
                
                # Vykreslení textů s přesnými rozestupy
                color = GREEN if idx == selected_good else WHITE
                screen.blit(font.render(good_label, True, color), (panel_x + 35, y + 9))
                screen.blit(font.render(buy_label, True, GREEN), (panel_x + 160, y + 9))
                screen.blit(font.render(sell_label, True, RED), (panel_x + 280, y + 9))
                screen.blit(font.render(inv_label, True, BLUE), (panel_x + 380, y + 9))
 
                # Pozice tlačítek BUY a SELL
                buy_rect = pygame.Rect(panel_x + 460, y + 5, 90, 26)
                sell_rect = pygame.Rect(panel_x + 570, y + 5, 90, 26)
                
                pygame.draw.rect(screen, GREEN, buy_rect)
                pygame.draw.rect(screen, RED, sell_rect)
                
                screen.blit(font.render("BUY", True, BLACK), (buy_rect.x + 32, buy_rect.y + 4))
                screen.blit(font.render("SELL", True, BLACK), (sell_rect.x + 27, sell_rect.y + 4))
 
            # Tlačítko pro palivo na spodku tabulky
            fuel_button = pygame.Rect(panel_x + 460, panel_y + 70 + len(GOODS) * 45 + 6, 200, 30)
            pygame.draw.rect(screen, BLUE, fuel_button)
            screen.blit(font.render("REFUEL", True, WHITE), (fuel_button.x + 72, fuel_button.y + 6))
 
            # Výpis hlášek o nákupu/prodeji
            if trade_message:
                screen.blit(font.render(trade_message, True, YELLOW), (panel_x + 20, panel_y + panel_h - 35))
 
        screen.blit(font.render("W-S: Thrust/Brake | A-D: Turn | Click buttons in market panel to trade", True, WHITE), (20, HEIGHT - 35))
 
        pygame.display.flip()
        clock.tick(FPS)
 
# --- START PROGRAMU ---
while True:
    selected_resolution = show_menu(selected_resolution)
    create_screen(RESOLUTION_OPTIONS[selected_resolution][0])
    # If user chose Continue, load the save
    if load_on_start:
        loaded = load_game()
        if loaded:
            p_loaded, stations_loaded = loaded
            player.x = p_loaded.x
            player.y = p_loaded.y
            player.angle = p_loaded.angle
            player.vel_x = p_loaded.vel_x
            player.vel_y = p_loaded.vel_y
            player.fuel = p_loaded.fuel
            player.credits = p_loaded.credits
            player.cargo = p_loaded.cargo
            stations = stations_loaded
    # Generování hvězd až PO nastavení rozlišení obrazovky
    stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(150)]
    run_game()
 
pygame.quit()