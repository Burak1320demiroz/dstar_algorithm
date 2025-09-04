import heapq
import math
from typing import List, Tuple, Optional
from src.utils.data_structures import PriorityQueue
from .dstar_lite import Node  # Aynı düğüm yapısını kullanıyoruz


class DStarLiteOriginal:
    """Orijinal D* Lite yaklaşımıyla uyumlu referans implementasyon.

    Notlar:
    - 8-komşuluk ve köşe kesmeyi engelleme kullanır.
    - Arayüz, projedeki `DStarLite` sınıfıyla uyumludur (plan_path, update_obstacles, replan_path).
    """

    def __init__(self, grid_map, heuristic_weight: float = 1.0):
        self.grid_map = grid_map
        self.width = grid_map.width
        self.height = grid_map.height
        self.heuristic_weight = heuristic_weight

        self.nodes = {}
        self._initialize_nodes()

        self.open_list = PriorityQueue()

        self.start: Optional[Node] = None
        self.goal: Optional[Node] = None
        self.last_start: Optional[Node] = None

        self.stats = {
            'nodes_expanded': 0,
            'replanning_count': 0,
            'total_planning_time': 0.0
        }

    def _initialize_nodes(self):
        for y in range(self.height):
            for x in range(self.width):
                self.nodes[(x, y)] = Node(x, y)

    def _get_node(self, x: int, y: int) -> Node:
        if (x, y) not in self.nodes:
            self.nodes[(x, y)] = Node(x, y)
        return self.nodes[(x, y)]

    def _heuristic(self, node1: Node, node2: Node) -> float:
        dx = abs(node1.x - node2.x)
        dy = abs(node1.y - node2.y)
        return self.heuristic_weight * math.sqrt(dx * dx + dy * dy)

    def _get_neighbors(self, node: Node) -> List[Node]:
        neighbors: List[Node] = []
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1),
                      (0, 1), (1, -1), (1, 0), (1, 1)]
        for dx, dy in directions:
            nx, ny = node.x + dx, node.y + dy
            if not (0 <= nx < self.width and 0 <= ny < self.height):
                continue
            if self.grid_map.is_obstacle(nx, ny):
                continue
            # Diyagonal köşe kesmeyi engelle
            if dx != 0 and dy != 0:
                if (self.grid_map.is_obstacle(node.x + dx, node.y) or
                        self.grid_map.is_obstacle(node.x, node.y + dy)):
                    continue
            neighbors.append(self._get_node(nx, ny))
        return neighbors

    def _move_cost(self, a: Node, b: Node) -> float:
        if self.grid_map.is_obstacle(b.x, b.y):
            return float('inf')
        dx = abs(a.x - b.x)
        dy = abs(a.y - b.y)
        base = math.sqrt(2) if (dx == 1 and dy == 1) else 1.0
        return base + self.grid_map.get_terrain_cost(b.x, b.y)

    def _key(self, node: Node) -> Tuple[float, float]:
        k1 = min(node.g, node.rhs) + self._heuristic(node, self.start)
        k2 = min(node.g, node.rhs)
        return k1, k2

    def _initialize_search(self, start: Tuple[int, int], goal: Tuple[int, int]):
        self.start = self._get_node(start[0], start[1])
        self.goal = self._get_node(goal[0], goal[1])
        self.last_start = self.start

        for node in self.nodes.values():
            node.g = float('inf')
            node.rhs = float('inf')

        self.open_list.clear()

        self.goal.rhs = 0
        self.goal.h = self._heuristic(self.goal, self.start)
        self.open_list.insert(self.goal, self._key(self.goal))

    def _update_vertex(self, node: Node):
        if node != self.goal:
            min_rhs = float('inf')
            for neighbor in self._get_neighbors(node):
                cost = self._move_cost(node, neighbor) + neighbor.g
                if cost < min_rhs:
                    min_rhs = cost
            node.rhs = min_rhs

        if self.open_list.contains(node):
            self.open_list.remove(node)

        if node.g != node.rhs:
            node.h = self._heuristic(node, self.start)
            self.open_list.insert(node, self._key(node))

    def _compute_shortest_path(self):
        while (not self.open_list.empty() and
               (self.open_list.top_key() < self._key(self.start) or
                self.start.rhs != self.start.g)):
            current = self.open_list.pop()
            self.stats['nodes_expanded'] += 1

            if current.g > current.rhs:
                current.g = current.rhs
                for neighbor in self._get_neighbors(current):
                    if neighbor != self.goal:
                        neighbor.rhs = min(neighbor.rhs,
                                           self._move_cost(neighbor, current) + current.g)
                    self._update_vertex(neighbor)
            else:
                current.g = float('inf')
                neighbors = self._get_neighbors(current) + [current]
                for neighbor in neighbors:
                    self._update_vertex(neighbor)

    def _extract_path(self) -> List[Tuple[int, int]]:
        if self.start.g == float('inf'):
            return []
        path: List[Tuple[int, int]] = []
        current = self.start
        while current != self.goal:
            path.append((current.x, current.y))
            best_neighbor = None
            best_cost = float('inf')
            for neighbor in self._get_neighbors(current):
                cost = self._move_cost(current, neighbor) + neighbor.g
                if cost < best_cost:
                    best_cost = cost
                    best_neighbor = neighbor
            if best_neighbor is None:
                break
            current = best_neighbor
        path.append((self.goal.x, self.goal.y))
        return path

    def plan_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        import time
        t0 = time.time()
        self._initialize_search(start, goal)
        self._compute_shortest_path()
        path = self._extract_path()
        self.stats['total_planning_time'] += (time.time() - t0)
        return path

    def update_obstacles(self, changed_cells: List[Tuple[int, int, bool]]):
        self.stats['replanning_count'] += 1
        for x, y, _ in changed_cells:
            node = self._get_node(x, y)
            for neighbor in self._get_neighbors(node):
                self._update_vertex(neighbor)
            self._update_vertex(node)
        if self.last_start != self.start:
            for node in self.nodes.values():
                node.h = self._heuristic(node, self.start)
            self.last_start = self.start
        self._compute_shortest_path()

    def replan_path(self, new_start: Optional[Tuple[int, int]] = None) -> List[Tuple[int, int]]:
        if new_start:
            self.start = self._get_node(new_start[0], new_start[1])
        self._compute_shortest_path()
        return self._extract_path()


