from collections import deque
import random

def bfs(start, goal, map_data):

    queue = deque([start])

    visited = {start}

    parent = {}

    while queue:

        current = queue.popleft()

        if current == goal:
            break

        for neighbor in get_neighbors(current, map_data):

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

def get_neighbors(cell, map_data):

    x, y = cell
    rows = len(map_data)
    cols = len(map_data[0])

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

def random_neighbor(cell, last_cell, map_data):
    
    neighbors = get_neighbors(cell, map_data)

    filtered = [
        n for n in neighbors
        if n != last_cell
    ]

    if filtered:
        return random.choice(filtered)

    return random.choice(neighbors) if neighbors else cell
