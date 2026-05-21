import pygame
import math
import random
import sys
 
# --- KONFIGURACE ---
WIDTH, HEIGHT = 1100, 700
FPS = 60

# Globální seznam pro hvězdy (musí být nadefinován hned na začátku)
stars = []

# Velikosti zón okolo stanic
STATION_PERMIT_RADIUS = 220    # Vnější zóna (omezuje rychlost)
STATION_LANDING_RADIUS = 60    # Vnitřní zóna (hned otevírá obchod)
 
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
 
# --- GENEROVÁNÍ VESMÍRU ---
player = Player()
 
# Náhodné stanice v obrovském prostoru
stations = []
names = ["Alpha", "Bravo", "Gamma", "Delta", "Echo", "Omega"]
for name in names:
    prices = {}
    for good in GOODS:
        base = BASE_PRICES[good]
        buy_price = max(5, base + random.randint(-15, 20))
        sell_price = max(1, buy_price - random.randint(10, 25))
        prices[good] = {"buy": buy_price, "sell": sell_price}
    stations.append({
        "name": f"Station {name}",
        "x": random.randint(-5000, 5000),
        "y": random.randint(-5000, 5000),
        "prices": prices,
        "fuel_price": 8
    })
 
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
 
selected_resolution = 2  # Nastaveno na index 2 (1100x700) jako bezpečný střed
resolution_options = RESOLUTION_OPTIONS
 
def show_menu(selected_resolution):
    menu_mode = "main"
    menu_index = 0
    while True:
        screen.fill(BLACK)
        menu_buttons = []
 
        if menu_mode == "main":
            draw_centered("Elite Python: WSAD Edition", 120, YELLOW)
            draw_centered("Start and choose settings before play", 160, WHITE)
            for idx, label in enumerate(["Start Game", "Settings", "Quit"]):
                rect = pygame.Rect((WIDTH // 2 - 150, 240 + idx * 70, 300, 50))
                menu_buttons.append(("main", idx, rect))
                color = GREEN if idx == menu_index else BLUE
                pygame.draw.rect(screen, color, rect)
                screen.blit(font.render(label, True, BLACK), (rect.x + 80, rect.y + 14))
        else:
            draw_centered("Settings", 120, YELLOW)
            draw_centered("Choose resolution or fullscreen", 160, WHITE)
            for idx, (_, label) in enumerate(resolution_options):
                rect = pygame.Rect((WIDTH // 2 - 220, 240 + idx * 60, 440, 45))
                menu_buttons.append(("resolution", idx, rect))
                color = GREEN if idx == selected_resolution else BLUE
                pygame.draw.rect(screen, color, rect)
                screen.blit(font.render(label, True, BLACK), (rect.x + 20, rect.y + 12))
            back_rect = pygame.Rect((WIDTH // 2 - 90, 240 + len(resolution_options) * 60, 180, 45))
            menu_buttons.append(("back", None, back_rect))
            pygame.draw.rect(screen, RED, back_rect)
            screen.blit(font.render("Back", True, BLACK), (back_rect.x + 65, back_rect.y + 12))
 
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
                    menu_index = min(menu_index + 1, 2 if menu_mode == "main" else len(resolution_options))
                elif event.key == pygame.K_UP:
                    menu_index = max(menu_index - 1, 0)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if menu_mode == "main":
                        if menu_index == 0:
                            return selected_resolution
                        elif menu_index == 1:
                            menu_mode = "settings"
                            menu_index = selected_resolution
                        else:
                            pygame.quit()
                            sys.exit()
                    else:
                        if menu_index < len(resolution_options):
                            selected_resolution = menu_index
                        else:
                            menu_mode = "main"
                            menu_index = 0
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for kind, idx, rect in menu_buttons:
                    if rect.collidepoint(mx, my):
                        if kind == "main":
                            if idx == 0:
                                return selected_resolution
                            elif idx == 1:
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
    # Generování hvězd až PO nastavení rozlišení obrazovky
    stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(150)]
    run_game()
 
pygame.quit()