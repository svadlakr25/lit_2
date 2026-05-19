import pygame
import sys
import math
import random
import os

pygame.init()

SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 800

COLOR_BG = (0, 0, 0)
COLOR_PANEL = (18, 25, 40)
COLOR_ACCENT = (120, 200, 255)
COLOR_TEXT = (220, 230, 240)
COLOR_HIGHLIGHT = (120, 200, 255)
COLOR_SHIP = (200, 230, 255)
COLOR_STATION = (180, 170, 120)

SHIP_ACCEL = 220
SHIP_ROT_SPEED = 3.2
SHIP_FRICTION = 0.995
SHIP_MAX_SPEED = 420
STATION_PERMIT_RADIUS = 150
STATION_LANDING_RADIUS = 70
DOCK_SPEED_MAX = 80
INITIAL_CREDITS = 500
MIN_STATION_DISTANCE = 700
CARGO_CAPACITY = 25
FUEL_CAPACITY = 100
FUEL_CONSUMPTION = 2
MAP_WIDTH = 320
MAP_HEIGHT = 170
MAP_RANGE = 5200
TRADE_ITEMS = {
    "Fuel": {"buy": 5, "sell": 3},
    "Cargo": {"buy": 20, "sell": 14},
    "Ammo": {"buy": 12, "sell": 8},
}


def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))


def generate_stations(count):
    stations = []
    attempts = 0
    while len(stations) < count and attempts < count * 20:
        x = random.randint(-2500, 2500)
        y = random.randint(-1800, 1800)
        too_close = False
        for station in stations:
            if math.hypot(station["x"] - x, station["y"] - y) < MIN_STATION_DISTANCE:
                too_close = True
                break
        if not too_close:
            market = {}
            for item, price in TRADE_ITEMS.items():
                modifier = random.uniform(-0.25, 0.25)
                market[item] = {
                    "buy": max(1, int(price["buy"] * (1 + modifier))),
                    "sell": max(1, int(price["sell"] * (1 + modifier * 0.8)))
                }
            stations.append({
                "x": x,
                "y": y,
                "name": f"Station {len(stations) + 1}",
                "market": market,
            })
        attempts += 1
    return stations


def generate_stars(count):
    stars = []
    for _ in range(count):
        x = random.randint(-4000, 4000)
        y = random.randint(-3200, 3200)
        size = random.choice([1, 1, 2])
        stars.append((x, y, size))
    return stars


def draw_ship(screen, ship_center, angle):
    base_points = [
        (0, -20),
        (-12, 14),
        (0, 8),
        (12, 14),
    ]
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    rotated = [
        (ship_center[0] + x * cos_a - y * sin_a, ship_center[1] + x * sin_a + y * cos_a)
        for x, y in base_points
    ]
    pygame.draw.polygon(screen, COLOR_SHIP, rotated)
    pygame.draw.circle(screen, COLOR_ACCENT, ship_center, 5, 1)


def draw_space(screen, ship_pos, stars, stations, ship_angle, closest_station=None):
    screen.fill(COLOR_BG)

    # Stars in background
    for x, y, size in stars:
        dx = x - ship_pos[0] + SCREEN_WIDTH // 2
        dy = y - ship_pos[1] + SCREEN_HEIGHT // 2
        if -20 < dx < SCREEN_WIDTH + 20 and -20 < dy < SCREEN_HEIGHT + 20:
            color = (255, 255, 255) if random.random() < 0.25 else (180, 200, 255)
            pygame.draw.circle(screen, color, (int(dx), int(dy)), size)

    # Station markers only
    for station in stations:
        dx = station["x"] - ship_pos[0] + SCREEN_WIDTH // 2
        dy = station["y"] - ship_pos[1] + SCREEN_HEIGHT // 2
        if -80 < dx < SCREEN_WIDTH + 80 and -80 < dy < SCREEN_HEIGHT + 80:
            pygame.draw.rect(screen, COLOR_STATION, (dx - 12, dy - 12, 24, 24), border_radius=4)
            pygame.draw.circle(screen, COLOR_ACCENT, (int(dx), int(dy)), 6, 1)
            if closest_station is station:
                label_font = pygame.font.SysFont(None, 22)
                label = label_font.render(station["name"], True, COLOR_ACCENT)
                screen.blit(label, (dx + 16, dy - 10))

    ship_center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    draw_ship(screen, ship_center, ship_angle)


def draw_ui(screen, speed, closest_name, closest_dist, near_station, can_dock, credits, inventory):
    font = pygame.font.SysFont(None, 28)
    cargo_label = f"{inventory['CargoAmount']}/{CARGO_CAPACITY}"
    if inventory['CargoType']:
        cargo_label = f"{inventory['CargoType']} {inventory['CargoAmount']}/{CARGO_CAPACITY}"

    status = (
        f"WASD pohyb · Speed: {int(speed)} m/s · Credits: {credits} "
        f"· Cargo: {cargo_label}"
    )
    text = font.render(status, True, COLOR_TEXT)
    surface = pygame.Surface((text.get_width() + 16, text.get_height() + 10), pygame.SRCALPHA)
    surface.fill((5, 10, 30, 200))
    surface.blit(text, (8, 5))
    screen.blit(surface, (20, 20))

    fuel_text = font.render(f"Fuel: {int(inventory['Fuel'])}/{FUEL_CAPACITY}", True, COLOR_TEXT)
    fuel_surface = pygame.Surface((fuel_text.get_width() + 16, fuel_text.get_height() + 10), pygame.SRCALPHA)
    fuel_surface.fill((5, 10, 30, 200))
    fuel_surface.blit(fuel_text, (8, 5))
    screen.blit(fuel_surface, (20, SCREEN_HEIGHT - fuel_text.get_height() - 34))

    action_text = ""
    if near_station:
        action_text = "In docking zone. Press E to dock." if can_dock else "Slow down to dock (Speed below 80 m/s)."
    else:
        action_text = f"Nearest: {closest_name} ({int(closest_dist)} m)"
    info = font.render(action_text, True, COLOR_ACCENT if near_station else COLOR_TEXT)
    info_surface = pygame.Surface((info.get_width() + 16, info.get_height() + 10), pygame.SRCALPHA)
    info_surface.fill((5, 10, 30, 180))
    info_surface.blit(info, (8, 5))
    screen.blit(info_surface, (20, 56))


def draw_trade_menu(screen, station, credits, inventory):
    menu_w = 420
    menu_h = 320
    menu_x = SCREEN_WIDTH - menu_w - 40
    menu_y = 120
    pygame.draw.rect(screen, (8, 12, 28), (menu_x, menu_y, menu_w, menu_h), border_radius=14)
    pygame.draw.rect(screen, COLOR_ACCENT, (menu_x, menu_y, menu_w, menu_h), 2, border_radius=14)

    menu_font = pygame.font.SysFont(None, 32)
    title = menu_font.render(f"{station['name']} Market", True, COLOR_TEXT)
    screen.blit(title, (menu_x + 18, menu_y + 18))

    small_font = pygame.font.SysFont(None, 24)
    cargo_label = f"{inventory['CargoAmount']}/{CARGO_CAPACITY}"
    if inventory['CargoType']:
        cargo_label = f"{inventory['CargoType']} {inventory['CargoAmount']}/{CARGO_CAPACITY}"
    sell_label = "4: Cargo → empty"
    if inventory['CargoType']:
        sell_price = station['market'][inventory['CargoType']]['sell']
        sell_label = f"4: Cargo → {sell_price} cr"
    lines = [
        f"Credits: {credits}",
        f"Cargo: {cargo_label}",
        f"Fuel: {int(inventory['Fuel'])}/{FUEL_CAPACITY}",
        "",
        "Buy:",
        f"1: Fuel → {station['market']['Fuel']['buy']} cr",
        f"2: Cargo → {station['market']['Cargo']['buy']} cr",
        f"3: Ammo → {station['market']['Ammo']['buy']} cr",
        "",
        "Sell:",
        sell_label,
        "",
        "Q: Leave station",
    ]
    for i, line in enumerate(lines):
        screen.blit(small_font.render(line, True, COLOR_TEXT), (menu_x + 20, menu_y + 70 + i * 28))


def draw_map(screen, ship_pos, stations, ship_angle):
    map_x = SCREEN_WIDTH - MAP_WIDTH - 10
    map_y = 10
    pygame.draw.rect(screen, (12, 18, 28), (map_x, map_y, MAP_WIDTH, MAP_HEIGHT), border_radius=8)
    pygame.draw.rect(screen, COLOR_ACCENT, (map_x, map_y, MAP_WIDTH, MAP_HEIGHT), 1, border_radius=8)

    inner_x = map_x + 8
    inner_y = map_y + 8
    inner_w = MAP_WIDTH - 16
    inner_h = MAP_HEIGHT - 16
    pygame.draw.rect(screen, (8, 12, 20), (inner_x, inner_y, inner_w, inner_h), border_radius=6)

    scale = MAP_RANGE / 2
    for station in stations:
        rel_x = (station["x"] - ship_pos[0]) / scale
        rel_y = (station["y"] - ship_pos[1]) / scale
        map_px = inner_x + inner_w / 2 + rel_x * inner_w / 2
        map_py = inner_y + inner_h / 2 + rel_y * inner_h / 2
        if -0.2 <= rel_x <= 0.2 and -0.2 <= rel_y <= 0.2:
            pygame.draw.circle(screen, COLOR_STATION, (int(map_px), int(map_py)), 4)
        elif abs(rel_x) <= 1.5 and abs(rel_y) <= 1.5:
            clamped_x = clamp(map_px, inner_x + 4, inner_x + inner_w - 4)
            clamped_y = clamp(map_py, inner_y + 4, inner_y + inner_h - 4)
            pygame.draw.circle(screen, COLOR_ACCENT, (int(clamped_x), int(clamped_y)), 2)

    ship_x = inner_x + inner_w / 2
    ship_y = inner_y + inner_h / 2
    ship_points = [
        (0, -6),
        (-4, 5),
        (4, 5),
    ]
    cos_a = math.cos(ship_angle)
    sin_a = math.sin(ship_angle)
    rotated = [
        (ship_x + x * cos_a - y * sin_a, ship_y + x * sin_a + y * cos_a)
        for x, y in ship_points
    ]
    pygame.draw.polygon(screen, COLOR_SHIP, rotated)
    pygame.draw.circle(screen, COLOR_SHIP, (int(ship_x), int(ship_y)), 2)


def find_closest_station(ship_pos, stations):
    best = None
    best_dist = float('inf')
    for station in stations:
        dist = math.hypot(station["x"] - ship_pos[0], station["y"] - ship_pos[1])
        if dist < best_dist:
            best_dist = dist
            best = station
    return best, best_dist


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Elite Dangerous Top-Down Ship")
    clock = pygame.time.Clock()
    running = True

    ship_pos = [0.0, 0.0]
    ship_vel = [0.0, 0.0]
    ship_angle = 0.0
    credits = INITIAL_CREDITS
    inventory = {"Fuel": FUEL_CAPACITY, "CargoType": None, "CargoAmount": 0}
    trade_mode = False
    stations = generate_stations(7)
    stars = generate_stars(180)

    while running:
        dt = clock.tick(60) / 1000.0

        closest_station, closest_dist = find_closest_station(ship_pos, stations)
        near_station = closest_dist < STATION_PERMIT_RADIUS
        speed = math.hypot(ship_vel[0], ship_vel[1])
        can_dock = near_station and speed < DOCK_SPEED_MAX

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif trade_mode:
                    market = closest_station["market"]
                    if event.key == pygame.K_1 and credits >= market["Fuel"]["buy"] and inventory["Fuel"] < FUEL_CAPACITY:
                        credits -= market["Fuel"]["buy"]
                        inventory["Fuel"] = min(FUEL_CAPACITY, inventory["Fuel"] + 1)
                    elif event.key == pygame.K_2 and credits >= market["Cargo"]["buy"] and inventory["CargoAmount"] < CARGO_CAPACITY and (inventory["CargoType"] is None or inventory["CargoType"] == "Cargo"):
                        credits -= market["Cargo"]["buy"]
                        inventory["CargoType"] = "Cargo"
                        inventory["CargoAmount"] += 1
                    elif event.key == pygame.K_3 and credits >= market["Ammo"]["buy"] and inventory["CargoAmount"] < CARGO_CAPACITY and (inventory["CargoType"] is None or inventory["CargoType"] == "Ammo"):
                        credits -= market["Ammo"]["buy"]
                        inventory["CargoType"] = "Ammo"
                        inventory["CargoAmount"] += 1
                    elif event.key == pygame.K_4 and inventory["CargoAmount"] > 0:
                        sell_price = market[inventory["CargoType"]]["sell"]
                        credits += sell_price * inventory["CargoAmount"]
                        inventory["CargoType"] = None
                        inventory["CargoAmount"] = 0
                    elif event.key == pygame.K_q:
                        trade_mode = False
                else:
                    if event.key == pygame.K_e and can_dock:
                        trade_mode = True

        if trade_mode:
            ship_vel[0] = 0.0
            ship_vel[1] = 0.0
        else:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                ship_angle -= SHIP_ROT_SPEED * dt
            if keys[pygame.K_d]:
                ship_angle += SHIP_ROT_SPEED * dt

            thrust = 0.0
            if keys[pygame.K_w] and inventory["Fuel"] > 0:
                thrust += SHIP_ACCEL
                inventory["Fuel"] = max(0, inventory["Fuel"] - FUEL_CONSUMPTION * dt)
            if keys[pygame.K_s]:
                thrust -= SHIP_ACCEL * 0.55

            thrust_x = math.sin(ship_angle) * thrust
            thrust_y = -math.cos(ship_angle) * thrust

            ship_vel[0] += thrust_x * dt
            ship_vel[1] += thrust_y * dt
            ship_vel[0] *= SHIP_FRICTION
            ship_vel[1] *= SHIP_FRICTION

        speed = math.hypot(ship_vel[0], ship_vel[1])
        if near_station and speed > DOCK_SPEED_MAX:
            scale = DOCK_SPEED_MAX / speed
            ship_vel[0] *= scale
            ship_vel[1] *= scale
            speed = DOCK_SPEED_MAX

        ship_pos[0] += ship_vel[0] * dt
        ship_pos[1] += ship_vel[1] * dt

        draw_space(screen, ship_pos, stars, stations, ship_angle, closest_station)
        draw_ui(screen, speed, closest_station["name"], closest_dist, near_station, can_dock, credits, inventory)
        draw_map(screen, ship_pos, stations, ship_angle)
        if trade_mode:
            draw_trade_menu(screen, closest_station, credits, inventory)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()


