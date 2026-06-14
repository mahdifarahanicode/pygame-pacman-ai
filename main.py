import pygame
import sys
import random
from collections import deque

pygame.init()

game_state = "playing"
current_level = 1
lives = 3
player_state = "alive"
respawn_timer = 0

# ----------------- تنظیمات -----------------
WIDTH, HEIGHT = 800, 600
tile = 40

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pacman Game")
clock = pygame.time.Clock()

levels = {
    1: {
        "ghost_count": 3,
        "ghost_ai": "random"
    },

    2: {
        "ghost_count": 2,
        "ghost_ai": "mixed"
    },

    3: {
        "ghost_count": 3,
        "ghost_ai": "bfs"
    }
}

# ----------------- map -----------------
map_data = [
"11111111111111111111",
"10000000000000000001",
"10111101111101111101",
"10000100010001000001",
"10110111010111011101",
"10000100010001000001",
"10111101111101111101",
"10000000000000000001",
"10111101111101111101",
"10000100010001000001",
"10110111010111011101",
"10000100010001000001",
"10111101111101111101",
"10000000000000000001",
"11111111111111111111",
]

rows = len(map_data)
cols = len(map_data[0])

# ----------------- walls -----------------
walls = []
for y, row in enumerate(map_data):
    for x, cell in enumerate(row):
        if cell == "1":
            walls.append(pygame.Rect(x * tile, y * tile, tile, tile))

# ----------------- player -----------------
player_size = 33
speed = 6

def is_valid_spawn(x, y):
    rect = pygame.Rect(x, y, player_size, player_size)
    return not any(rect.colliderect(w) for w in walls)

while True:
    player_x = random.randint(0, WIDTH - player_size)
    player_y = random.randint(0, HEIGHT - player_size)

    if is_valid_spawn(player_x, player_y):
        break

# ----------------- ghosts -----------------
ghost_size = player_size

def spawn_ghost():

    while True:

        cell_x = random.randint(1, cols - 2)
        cell_y = random.randint(1, rows - 2)

        if map_data[cell_y][cell_x] == "1":
            continue

        x = cell_x * tile + tile//2 - ghost_size//2
        y = cell_y * tile + tile//2 - ghost_size//2

        return {
        "cell_x": cell_x,
        "cell_y": cell_y,
        "x": x,
        "y": y,
        "path": [],
        "moving": False,
        "target_x": x,
        "target_y": y,
        "last_cell": None
    }

ghosts = []

# ----------------- movement -----------------

def handle_movement(x, y):
    keys = pygame.key.get_pressed()

    new_x, new_y = x, y

    if keys[pygame.K_LEFT]:
        new_x -= speed
    if keys[pygame.K_RIGHT]:
        new_x += speed
    if keys[pygame.K_UP]:
        new_y -= speed
    if keys[pygame.K_DOWN]:
        new_y += speed

    rect = pygame.Rect(new_x, new_y, player_size, player_size)

    if any(rect.colliderect(w) for w in walls):
        return x, y

    return new_x, new_y

def get_cell(x, y):
    return (
        int(x // tile),
        int(y // tile)
    )

def get_neighbors(cell):

    x, y = cell

    neighbors = []

    directions = [
        (1, 0),
        (-1, 0),
        (0, 1),
        (0, -1)
    ]

    for dx, dy in directions:

        nx = x + dx
        ny = y + dy

        if (
            0 <= nx < cols and
            0 <= ny < rows and
            map_data[ny][nx] == "0"
        ):
            neighbors.append((nx, ny))

    return neighbors

def random_neighbor(cell, last_cell):

    neighbors = get_neighbors(cell)

    filtered = [
        n for n in neighbors
        if n != last_cell
    ]

    if filtered:
        return random.choice(filtered)

    return random.choice(neighbors) if neighbors else cell

def is_cell_occupied(cell, current_ghost):
    
    for g in ghosts:

        if g is current_ghost:
            continue

        if (
            g["cell_x"],
            g["cell_y"]
        ) == cell:
            return True

    return False

def bfs(start, goal):

    queue = deque([start])

    visited = {start}

    parent = {}

    while queue:

        current = queue.popleft()

        if current == goal:
            break

        for neighbor in get_neighbors(current):

            if neighbor not in visited:

                visited.add(neighbor)

                parent[neighbor] = current

                queue.append(neighbor)

    if goal not in visited:
        return []

    path = []

    current = goal

    while current != start:

        path.append(current)

        current = parent[current]

    path.reverse()

    return path


def move_ghosts():

    ghost_speed = 2

    for g in ghosts:

        # هنوز در حال حرکت است
        if g["moving"]:

            dx = g["target_x"] - g["x"]
            dy = g["target_y"] - g["y"]

            if abs(dx) <= ghost_speed:
                g["x"] = g["target_x"]
            else:
                g["x"] += ghost_speed if dx > 0 else -ghost_speed

            if abs(dy) <= ghost_speed:
                g["y"] = g["target_y"]
            else:
                g["y"] += ghost_speed if dy > 0 else -ghost_speed

            if (
                g["x"] == g["target_x"]
                and
                g["y"] == g["target_y"]
            ):
                g["moving"] = False

            continue

        player_cell = get_cell(player_x, player_y)

        start = (
            g["cell_x"],
            g["cell_y"]
        )

        ai = levels[current_level]["ghost_ai"]

        if ai == "random":

            next_cell = random_neighbor(
                start,
                g["last_cell"]
            )

        elif ai == "mixed":

            if random.random() < 0.25:

                path = bfs(start, player_cell)

                if not path:
                    g["moving"] = False
                    continue

                next_cell = path[0]

            else:
                next_cell = random_neighbor(
                    start,
                    g["last_cell"]
                )

        elif ai == "bfs":

            path = bfs(start, player_cell)

            if not path:
                g["moving"] = False
                continue

            next_cell = path[0]

        if is_cell_occupied(
            next_cell,
            g
        ):

            alternatives = [
                n
                for n in get_neighbors(start)
                if not is_cell_occupied(n, g)
            ]

            if alternatives:
                next_cell = random.choice(alternatives)
            else:
                continue

        g["last_cell"] = (
            g["cell_x"],
            g["cell_y"]
        )
        
        g["cell_x"] = next_cell[0]
        g["cell_y"] = next_cell[1]

        g["target_x"] = (
            g["cell_x"] * tile
            + tile//2
            - ghost_size//2
        )

        g["target_y"] = (
            g["cell_y"] * tile
            + tile//2
            - ghost_size//2
        )

        g["moving"] = True

# ----------------- dots -----------------
dots = []
for y in range(rows):
    for x in range(cols):
        if map_data[y][x] == "0":
            dots.append(
                pygame.Rect(
                    x * tile + tile//2,
                    y * tile + tile//2,
                    5, 5
                )
            )

# ----------------- score -----------------
score = 0
font = pygame.font.SysFont(None, 36)

def reset_game(full_reset=False):
    global player_x, player_y, dots, ghosts
    global lives, current_level, game_state
    global player_state, respawn_timer, score

    if full_reset:
        lives = 3
        current_level = 1
        score = 0

    game_state = "playing"
    player_state = "alive"
    respawn_timer = 0

    while True:
        player_x = random.randint(0, WIDTH - player_size)
        player_y = random.randint(0, HEIGHT - player_size)
        if is_valid_spawn(player_x, player_y):
            break

    ghosts = [
        spawn_ghost()
        for _ in range(levels[current_level]["ghost_count"])
    ]

    dots = [
        pygame.Rect(
            x * tile + tile//2,
            y * tile + tile//2,
            5, 5
        )
        for y in range(rows)
        for x in range(cols)
        if map_data[y][x] == "0"
    ]

# ----------------- game loop -----------------
running = True
reset_game()

while running:

    if player_state == "respawning":
        respawn_timer -= 1

        if respawn_timer <= 0:
            reset_game()
            player_state = "alive"

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_r:
                reset_game(full_reset=True)

    if game_state != "playing":
        screen.fill((0, 0, 0))

        text = font.render(
            "YOU WIN" if game_state == "win" else "YOU DIED",
            True,
            (0, 255, 0) if game_state == "win" else (255, 0, 0)
        )

        screen.blit(
            text,
            (WIDTH // 2 - 60, HEIGHT // 3)
        )

        restart_text = font.render(
            "Press R to Restart",
            True,
            (255, 255, 255)
        )

        screen.blit(
            restart_text,
            (WIDTH // 2 - 100, HEIGHT // 2 + 30)
        )

        pygame.display.flip()
        clock.tick(60)
        continue

    player_x, player_y = handle_movement(player_x, player_y)

    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)

    # eat dots
    for d in dots[:]:
        if player_rect.colliderect(d):
            dots.remove(d)
            score += 1

    
    move_ghosts()

    # render
    screen.fill((0, 0, 0))

    for w in walls:
        pygame.draw.rect(screen, (0, 0, 255), w)

    for d in dots:
        pygame.draw.rect(screen, (255, 255, 255), d)

    for g in ghosts:
        pygame.draw.rect(screen, (255, 0, 0), (g["x"], g["y"], ghost_size, ghost_size))

    pygame.draw.rect(screen, (255, 255, 0), (player_x, player_y, player_size, player_size))

    # collision
    if player_state == "alive":
        for g in ghosts:
            if player_rect.colliderect(pygame.Rect(g["x"], g["y"], ghost_size, ghost_size)):
                lives -= 1

                if lives <= 0:
                    game_state = "lose"
                    player_state = "dead"
                else:
                    player_state = "respawning"
                    respawn_timer = 60

                break

    if len(dots) == 0:

        if current_level < 3:

            current_level += 1

            reset_game()

        else:

            game_state = "win"

    text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(text, (10, 10))

    level_text = font.render(
        f"Level: {current_level}",
        True,
        (255, 255, 255)
    )

    screen.blit(
        level_text,
        (
            WIDTH // 2 - level_text.get_width() // 2,
            10
        )
    )

    lives_text = font.render(
        f"Lives: {lives}",
        True,
        (255, 255, 255)
    )

    screen.blit(
        lives_text,
        (
            WIDTH - lives_text.get_width() - 10,
            10
        )
    )

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()