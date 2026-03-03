"""pathfinding.py

Simple BFS pathfinding over the grid map.

- Builds a graph of walkable tiles.
- `get_path(start, goal)` returns the *next* step from `start` toward `goal`.

"""

from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from main import Game


Coord = Tuple[int, int]


class PathFinding:
    """Grid BFS navigation helper."""

    def __init__(self, game: Game) -> None:
        self.game = game
        self.map = game.map.mini_map

        # 8-way movement
        self.ways: List[Coord] = [
            (-1, 0),
            (0, -1),
            (1, 0),
            (0, 1),
            (-1, -1),
            (1, -1),
            (1, 1),
            (-1, 1),
        ]

        self.graph: Dict[Coord, List[Coord]] = {}
        self.get_graph()

    def get_path(self, start: Coord, goal: Coord) -> Coord:
        """Return the next coordinate to step to from start towards goal."""
        visited = self.bfs(start, goal, self.graph)

        if goal not in visited:
            return start

        path: List[Coord] = [goal]
        step = visited.get(goal, start)

        while step and step != start:
            path.append(step)
            step = visited[step]
        return path[-1]

    def bfs(
        self, start: Coord, goal: Coord, graph: Dict[Coord, List[Coord]]
    ) -> Dict[Coord, Optional[Coord]]:
        queue: deque[Coord] = deque([start])
        visited: Dict[Coord, Optional[Coord]] = {start: None}

        while queue:
            cur_node = queue.popleft()
            if cur_node == goal:
                break

            for next_node in graph.get(cur_node, []):
                if next_node in visited:
                    continue
                if next_node in self.game.object_handler.npc_positions:
                    continue
                queue.append(next_node)
                visited[next_node] = cur_node

        return visited

    def get_next_nodes(self, x: int, y: int) -> List[Coord]:
        nodes: List[Coord] = []
        for dx, dy in self.ways:
            nx, ny = x + dx, y + dy
            if (nx, ny) not in self.game.map.world_map:
                nodes.append((nx, ny))
        return nodes

    def get_graph(self) -> None:
        for y, row in enumerate(self.map):
            for x, col in enumerate(row):
                if not col:
                    self.graph[(x, y)] = self.get_next_nodes(x, y)
