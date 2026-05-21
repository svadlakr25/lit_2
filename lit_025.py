import pygame
import math
import random
import sys
 
# --- KONFIGURACE ---
WIDTH, HEIGHT = 1100, 700
FPS = 60
STATION_PERMIT_RADIUS = 220
STATION_LANDING_RADIUS = 90
 
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
    ((1920, 1080), "1920 x 1080"),
    (None, "Fullscreen")
]
LANGUAGE_OPTIONS = ["English", "Česky"]
FPS_OPTIONS = [30, 60, 120]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Elite Dangerous")
 
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
            self.fuel -= 0.03  # pomalejší spotřeba paliva
       
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
 
# --- GENEROVÁNÍ VESMÍRU ---
player = Player()
 
# Náhodné stanice v obrovském prostoru
stations = []
names = ["Alpha", "Bravo", "Gamma", "Delta", "Echo", "Omega", "Nova", "Sierra", "Vega", "Orion", "Atlas", "Titan"]
station_range = 9000
min_station_distance = 1400
attempts = 0
for name in names:
    placed = False
    while not placed and attempts < len(names) * 30:
        x = random.randint(-station_range, station_range)
        y = random.randint(-station_range, station_range)
        too_close = False
        for station in stations:
            if math.hypot(station["x"] - x, station["y"] - y) < min_station_distance:
                too_close = True
                break
        if not too_close:
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
                "fuel_price": 8,
                "permit_radius": STATION_PERMIT_RADIUS,
                "landing_radius": STATION_LANDING_RADIUS
            })
            placed = True
        attempts += 1
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
            "fuel_price": 8,
            "permit_radius": STATION_PERMIT_RADIUS,
            "landing_radius": STATION_LANDING_RADIUS
        })
 
# Statické hvězdy na pozadí (pro pocit pohybu)
 
def create_screen(resolution):
    global WIDTH, HEIGHT, screen
    if resolution is None:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        WIDTH, HEIGHT = screen.get_size()
    else:
        WIDTH, HEIGHT = resolution
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Elite Dangerous")
    return screen
 
 
def draw_centered(text, y, color=WHITE):
    img = font.render(text, True, color)
    screen.blit(img, ((WIDTH - img.get_width()) // 2, y))
 
selected_resolution = 1
selected_language = 1
selected_fps = 60
 
resolution_options = RESOLUTION_OPTIONS
language_options = LANGUAGE_OPTIONS
fps_options = FPS_OPTIONS
 
 
def show_menu(selected_resolution):
    global selected_language, selected_fps, FPS
    menu_mode = "main"
    menu_index = 0
    while True:
        screen.fill(BLACK)
        menu_buttons = []

        lang = language_options[selected_language]
        if menu_mode == "main":
            title = "Elite Dangerous" if selected_language == 0 else "Elite Dangerous"
            subtitle = "Start and choose settings before play" if selected_language == 0 else "Start a zvol nastavení před hrou"
            draw_centered(title, 120, YELLOW)
            draw_centered(subtitle, 160, WHITE)
            for idx, label in enumerate(["Start Game" if selected_language == 0 else "Spustit hru",
                                         "Settings" if selected_language == 0 else "Nastavení",
                                         "Quit" if selected_language == 0 else "Konec"]):
                rect = pygame.Rect((WIDTH // 2 - 150, 240 + idx * 70, 300, 50))
                menu_buttons.append(("main", idx, rect))
                color = GREEN if idx == menu_index else BLUE
                pygame.draw.rect(screen, color, rect)
                screen.blit(font.render(label, True, BLACK), (rect.x + 80, rect.y + 14))
        elif menu_mode == "settings":
            draw_centered("Settings" if selected_language == 0 else "Nastavení", 120, YELLOW)
            draw_centered("Choose language, FPS, resolution", 160, WHITE) if selected_language == 0 else draw_centered("Vyber jazyk, FPS, rozlišení", 160, WHITE)
            settings_items = [
                ("language", f"Language: {language_options[selected_language]}") if selected_language == 0 else ("language", f"Jazyk: {language_options[selected_language]}"),
                ("fps", f"FPS: {selected_fps}"),
                ("resolution", f"Resolution: {resolution_options[selected_resolution][1]}" if selected_language == 0 else f"Rozlišení: {resolution_options[selected_resolution][1]}"),
                ("back", "Back" if selected_language == 0 else "Zpět")
            ]
            for idx, (_, label) in enumerate(settings_items):
                rect = pygame.Rect((WIDTH // 2 - 220, 240 + idx * 60, 440, 45))
                menu_buttons.append((settings_items[idx][0], idx, rect))
                color = GREEN if idx == menu_index else BLUE
                pygame.draw.rect(screen, color, rect)
                screen.blit(font.render(label, True, BLACK), (rect.x + 20, rect.y + 12))
        elif menu_mode == "language":
            draw_centered("Choose Language" if selected_language == 0 else "Vyber jazyk", 120, YELLOW)
            for idx, label in enumerate(language_options):
                rect = pygame.Rect((WIDTH // 2 - 150, 240 + idx * 70, 300, 50))
                menu_buttons.append(("language", idx, rect))
                color = GREEN if idx == menu_index else BLUE
                pygame.draw.rect(screen, color, rect)
                screen.blit(font.render(label, True, BLACK), (rect.x + 80, rect.y + 14))
        elif menu_mode == "fps":
            draw_centered("Choose FPS" if selected_language == 0 else "Vyber FPS", 120, YELLOW)
            for idx, value in enumerate(fps_options):
                label = f"{value} FPS"
                rect = pygame.Rect((WIDTH // 2 - 150, 240 + idx * 70, 300, 50))
                menu_buttons.append(("fps", idx, rect))
                color = GREEN if idx == menu_index else BLUE
                pygame.draw.rect(screen, color, rect)
                screen.blit(font.render(label, True, BLACK), (rect.x + 80, rect.y + 14))
        elif menu_mode == "resolution":
            draw_centered("Choose Resolution" if selected_language == 0 else "Vyber rozlišení", 120, YELLOW)
            for idx, (_, label) in enumerate(resolution_options):
                rect = pygame.Rect((WIDTH // 2 - 220, 240 + idx * 60, 440, 45))
                menu_buttons.append(("resolution", idx, rect))
                color = GREEN if idx == selected_resolution else BLUE
                pygame.draw.rect(screen, color, rect)
                screen.blit(font.render(label, True, BLACK), (rect.x + 20, rect.y + 12))
            back_rect = pygame.Rect((WIDTH // 2 - 90, 240 + len(resolution_options) * 60, 180, 45))
            menu_buttons.append(("back", None, back_rect))
            pygame.draw.rect(screen, RED, back_rect)
            screen.blit(font.render("Back" if selected_language == 0 else "Zpět", True, BLACK), (back_rect.x + 65, back_rect.y + 12))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if menu_mode in ("settings", "language", "fps", "resolution"):
                        menu_mode = "main" if menu_mode == "settings" else "settings"
                        menu_index = 0
                    else:
                        pygame.quit()
                        sys.exit()
                elif event.key == pygame.K_DOWN:
                    if menu_mode == "settings":
                        menu_index = min(menu_index + 1, 3)
                    elif menu_mode == "main":
                        menu_index = min(menu_index + 1, 2)
                    elif menu_mode == "language":
                        menu_index = min(menu_index + 1, len(language_options) - 1)
                    elif menu_mode == "fps":
                        menu_index = min(menu_index + 1, len(fps_options) - 1)
                    elif menu_mode == "resolution":
                        menu_index = min(menu_index + 1, len(resolution_options) - 1)
                elif event.key == pygame.K_UP:
                    menu_index = max(menu_index - 1, 0)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if menu_mode == "main":
                        if menu_index == 0:
                            return selected_resolution
                        elif menu_index == 1:
                            menu_mode = "settings"
                            menu_index = 0
                        else:
                            pygame.quit()
                            sys.exit()
                    elif menu_mode == "settings":
                        if menu_index == 0:
                            menu_mode = "language"
                            menu_index = selected_language
                        elif menu_index == 1:
                            menu_mode = "fps"
                            menu_index = fps_options.index(selected_fps)
                        elif menu_index == 2:
                            menu_mode = "resolution"
                            menu_index = selected_resolution
                        else:
                            menu_mode = "main"
                            menu_index = 1
                    elif menu_mode == "language":
                        selected_language = menu_index
                        menu_mode = "settings"
                        menu_index = 0
                    elif menu_mode == "fps":
                        selected_fps = fps_options[menu_index]
                        FPS = selected_fps
                        menu_mode = "settings"
                        menu_index = 1
                    elif menu_mode == "resolution":
                        selected_resolution = menu_index
                        menu_mode = "settings"
                        menu_index = 2
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for kind, idx, rect in menu_buttons:
                    if rect.collidepoint(mx, my):
                        if kind == "main":
                            if idx == 0:
                                return selected_resolution
                            elif idx == 1:
                                menu_mode = "settings"
                                menu_index = 0
                            else:
                                pygame.quit()
                                sys.exit()
                        elif kind == "language":
                            if menu_mode == "settings":
                                menu_mode = "language"
                                menu_index = selected_language
                            else:
                                selected_language = idx
                                menu_mode = "settings"
                                menu_index = 0
                        elif kind == "fps":
                            if menu_mode == "settings":
                                menu_mode = "fps"
                                menu_index = fps_options.index(selected_fps)
                            else:
                                selected_fps = fps_options[idx]
                                FPS = selected_fps
                                menu_mode = "settings"
                                menu_index = 1
                        elif kind == "resolution":
                            if menu_mode == "settings":
                                menu_mode = "resolution"
                                menu_index = selected_resolution
                            else:
                                selected_resolution = idx
                                menu_mode = "settings"
                                menu_index = 2
                        elif kind == "back":
                            menu_mode = "settings" if menu_mode == "resolution" else "main"
                            menu_index = 0
                        break

        pygame.display.flip()
        clock.tick(FPS)
 
 
def run_game():
    global selected_good, trade_message
    selected_good = 0
    trade_message = ""
    while True:
        screen.fill(BLACK)
 
        market_station = None
        market_buttons = []
        market_line_rects = []
        fuel_button = None
        panel_x = WIDTH // 2 - 300
        panel_y = HEIGHT // 2 - 145
 
        in_permit_zone = False
        in_landing_zone = False
        nearest_station = None
        nearest_dist = float("inf")
        for s in stations:
            dist = math.hypot(player.x - s["x"], player.y - s["y"])
            if dist < nearest_dist:
                nearest_dist = dist
                nearest_station = s
            if dist < s["permit_radius"]:
                in_permit_zone = True
            if dist < s["landing_radius"]:
                in_landing_zone = True
                market_station = s
                break
        if market_station:
            for idx, good in enumerate(GOODS):
                y = panel_y + 60 + idx * 40
                market_line_rects.append(pygame.Rect(panel_x + 20, y, 520, 32))
                market_buttons.append(("buy", idx, good, pygame.Rect(panel_x + 380, y + 4, 90, 24)))
                market_buttons.append(("sell", idx, good, pygame.Rect(panel_x + 490, y + 4, 90, 24)))
            fuel_button = pygame.Rect(panel_x + 380, panel_y + 60 + len(GOODS) * 40, 200, 30)
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
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
 
        # 1. VYKRESLENÍ HVĚZD (Parallax efekt)
        for s in stars:
            sx = (s[0] - player.x * 0.1) % WIDTH
            sy = (s[1] - player.y * 0.1) % HEIGHT
            pygame.draw.circle(screen, WHITE, (int(sx), int(sy)), 1)
 
        # 2. VYKRESLENÍ STANIC (Relativně k hráči)
        for s in stations:
            screen_x = s["x"] - player.x + WIDTH // 2
            screen_y = s["y"] - player.y + HEIGHT // 2
            if -100 < screen_x < WIDTH + 100 and -100 < screen_y < HEIGHT + 100:
                center_x = int(screen_x + 15)
                center_y = int(screen_y + 15)
                pygame.draw.circle(screen, (70, 70, 140), (center_x, center_y), s["permit_radius"], 1)
                pygame.draw.circle(screen, (120, 120, 220), (center_x, center_y), s["landing_radius"], 1)
                pygame.draw.rect(screen, YELLOW, (screen_x, screen_y, 30, 30), 2)
                pygame.draw.circle(screen, YELLOW, (center_x, center_y), 5)
                lbl = font.render(f"{s['name']} (Click items and buttons to trade)", True, YELLOW)
                screen.blit(lbl, (screen_x - 40, screen_y - 25))
 
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
 
        if in_permit_zone and not in_landing_zone:
            speed = math.hypot(player.vel_x, player.vel_y)
            max_zone_speed = 2.8
            if speed > max_zone_speed:
                scale = max_zone_speed / speed
                player.vel_x *= scale
                player.vel_y *= scale
 
 
        ui_y = 20
        cargo_text = ", ".join(f"{name} x{count}" for name, count in player.cargo.items() if count) or "Empty"
        info = [
            (f"CREDITS: {player.credits}", WHITE),
            (f"FUEL: {int(player.fuel)}%", RED if player.fuel < 20 else GREEN),
            (f"CARGO: {cargo_text}", WHITE),
            (f"POS: {int(player.x)}, {int(player.y)}", BLUE)
        ]
        if in_landing_zone:
            info.append(("ZONE: Docking zone active", GREEN))
        elif in_permit_zone:
            info.append(("ZONE: Permit approach zone", (180, 180, 0)))
        else:
            info.append(("ZONE: Outside station zones", RED))
        for text, color in info:
            screen.blit(font.render(text, True, color), (20, ui_y))
            ui_y += 25
 
 
        if market_station and not docking:
            panel_w = 600
            panel_h = 70 + len(GOODS) * 40 + 70
            pygame.draw.rect(screen, (15, 15, 25), (panel_x, panel_y, panel_w, panel_h))
            pygame.draw.rect(screen, BLUE, (panel_x, panel_y, panel_w, panel_h), 2)
            title = font.render(f"{market_station['name']} Market", True, YELLOW)
            screen.blit(title, (panel_x + 20, panel_y + 10))
            fuel_text = font.render(f"Fuel refill: 10% for {market_station['fuel_price']}cr", True, WHITE)
            screen.blit(fuel_text, (panel_x + 20, panel_y + 35))
 
            for idx, good in enumerate(GOODS):
                price = market_station['prices'][good]
                y = panel_y + 60 + idx * 40
                item_bg = (40, 40, 60) if idx == selected_good else (30, 30, 45)
                pygame.draw.rect(screen, item_bg, (panel_x + 20, y, 560, 32))
                pygame.draw.rect(screen, WHITE, (panel_x + 20, y, 560, 32), 1)
                line = f"{idx+1}. {good}: BUY {price['buy']}   SELL {price['sell']}"
                screen.blit(font.render(line, True, GREEN if idx == selected_good else WHITE), (panel_x + 30, y + 6))
 
                buy_rect = pygame.Rect(panel_x + 380, y + 4, 90, 24)
                sell_rect = pygame.Rect(panel_x + 490, y + 4, 90, 24)
                pygame.draw.rect(screen, GREEN, buy_rect)
                pygame.draw.rect(screen, RED, sell_rect)
                screen.blit(font.render("BUY", True, BLACK), (buy_rect.x + 28, buy_rect.y + 4))
                screen.blit(font.render("SELL", True, BLACK), (sell_rect.x + 24, sell_rect.y + 4))
 
            fuel_button = pygame.Rect(panel_x + 380, panel_y + 60 + len(GOODS) * 40, 200, 30)
            pygame.draw.rect(screen, BLUE, fuel_button)
            screen.blit(font.render("REFUEL", True, WHITE), (fuel_button.x + 64, fuel_button.y + 4))
 
            if trade_message:
                screen.blit(font.render(trade_message, True, BLUE), (panel_x + 20, panel_y + panel_h - 30))
 
        screen.blit(font.render("W-S: Thrust/Brake | A-D: Turn | Click buttons in market panel to trade", True, WHITE), (20, HEIGHT - 35))
 
        pygame.display.flip()
        clock.tick(FPS)
 
while True:
    selected_resolution = show_menu(selected_resolution)
    create_screen(RESOLUTION_OPTIONS[selected_resolution][0])
    stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(150)]
    run_game()
 
pygame.quit()