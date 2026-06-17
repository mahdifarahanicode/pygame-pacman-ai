import random
import game.state as state
from core.config import tile, ghost_size
from core.levels import levels
from game.pathfinding import bfs, get_neighbors, random_neighbor


def spawn_ghost():

    map_data = state.map_data

    if map_data is None:
        return None
    
    while True:
        cell_x = random.randint(1, len(map_data[0]) - 2)
        cell_y = random.randint(1, len(map_data) - 2)

        if map_data[cell_y][cell_x] == "1":
            continue

        x = cell_x * tile + tile // 2 - ghost_size // 2
        y = cell_y * tile + tile // 2 - ghost_size // 2

        return {
            "cell_x": cell_x,
            "cell_y": cell_y,
            "x": x,
            "y": y,
            "moving": False,
            "target_x": x,
            "target_y": y,
            "last_cell": None
        }


def is_cell_occupied(cell, current_ghost):

    for g in state.ghosts:
        if g is current_ghost:
            continue

        if (g["cell_x"], g["cell_y"]) == cell:
            return True

    return False


def move_ghosts():

    ghost_speed = 2
    map_data = state.map_data

    for g in state.ghosts:

        # ---------------- حرکت در حال اجرا ----------------
        if g["moving"]:

            dx = g["target_x"] - g["x"]
            dy = g["target_y"] - g["y"]

            g["x"] += ghost_speed if dx > 0 else -ghost_speed if dx != 0 else 0
            g["y"] += ghost_speed if dy > 0 else -ghost_speed if dy != 0 else 0

            if g["x"] == g["target_x"] and g["y"] == g["target_y"]:
                g["moving"] = False

            continue

        # ---------------- تصمیم‌گیری ----------------
        player_cell = (state.player_x // tile, state.player_y // tile)

        start = (g["cell_x"], g["cell_y"])

        ai = levels[state.current_level]["ghost_ai"]

        if ai == "random":
            next_cell = random_neighbor(start, g["last_cell"], map_data)

        elif ai == "mixed":
            if random.random() < 0.25:
                path = bfs(start, player_cell, map_data)
                next_cell = path[0] if path else start
            else:
                next_cell = random_neighbor(start, g["last_cell"], map_data)

        elif ai == "bfs":
            path = bfs(start, player_cell, map_data)
            next_cell = path[0] if path else start

        else:
            next_cell = start

        # ---------------- جلوگیری از برخورد ----------------
        if is_cell_occupied(next_cell, g):
            alternatives = [
                n for n in get_neighbors(start, map_data)
                if not is_cell_occupied(n, g)
            ]

            if alternatives:
                next_cell = random.choice(alternatives)
            else:
                continue

        # ---------------- آپدیت ----------------
        g["last_cell"] = (g["cell_x"], g["cell_y"])
        g["cell_x"], g["cell_y"] = next_cell

        g["target_x"] = g["cell_x"] * tile + tile // 2 - ghost_size // 2
        g["target_y"] = g["cell_y"] * tile + tile // 2 - ghost_size // 2

        g["moving"] = True