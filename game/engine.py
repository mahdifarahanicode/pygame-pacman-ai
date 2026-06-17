import random
import pygame
from assets.maps import maps
import game.state as state
from core.config import *
from core.levels import levels
from game.ghosts import spawn_ghost

def reset_game(level, full_reset=False):

    if full_reset:
        state.lives = 3
        state.score = 0

    state.map_data = maps[level - 1]
    state.rows = len(state.map_data)
    state.cols = len(state.map_data[0])

    # rebuild walls
    state.walls = []

    for y, row in enumerate(state.map_data):
        for x, cell in enumerate(row):
            if cell == "1":
                state.walls.append(pygame.Rect(x * tile, y * tile, tile, tile))

    # rebuild dots
    state.dots = []

    for y in range(state.rows):
        for x in range(state.cols):
            if state.map_data[y][x] == "0":
                state.dots.append(
                    pygame.Rect(
                        x * tile + tile // 2,
                        y * tile + tile // 2,
                        5, 5
                    )
                )
    
    

    # spawn player
    while True:
        x = random.randint(0, 800 - player_size)
        y = random.randint(0, 600 - player_size)

        rect = pygame.Rect(x, y, player_size, player_size)

        if not any(rect.colliderect(w) for w in state.walls):
            state.player_x = x
            state.player_y = y
            break

    # respawn ghosts
    state.ghosts = []

    for _ in range(levels[level]["ghost_count"]):
        g = spawn_ghost()

        if g:
            state.ghosts.append(g)