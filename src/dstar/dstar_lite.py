import heapq
import math
import numpy as np
from typing import List, Tuple, Dict, Set, Optional
from dataclasses import dataclass
from src.utils.data_structures import PriorityQueue

@dataclass
class Node:
    """D* Lite düğüm sınıfı"""
    x: int
    y: int
    g: float = float('inf')  # Başlangıçtan gerçek maliyet
    rhs: float = float('inf')  # Tek adım lookahead maliyet
    h: float = 0.0  # Heuristik maliyet
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

class DStarLite:
    """D* Lite algoritması implementasyonu"""
    
    def __init__(self, grid_map, heuristic_weight=1.0):
        self.grid_map = grid_map
        self.width = grid_map.width
        self.height = grid_map.height
        self.heuristic_weight = heuristic_weight
        
        # Düğüm haritası
        self.nodes = {}
        self.initialize_nodes()
        
        # Priority queue
        self.open_list = PriorityQueue()
        
        # Başlangıç ve hedef noktalar
        self.start = None
        self.goal = None
        self.last_start = None
        
        # İstatistikler
        self.stats = {
            'nodes_expanded': 0,
            'replanning_count': 0,
            'total_planning_time': 0.0
        }
    
    def initialize_nodes(self):
        """Tüm düğümleri başlat"""
        for y in range(self.height):
            for x in range(self.width):
                self.nodes[(x, y)] = Node(x, y)
    
    def get_node(self, x: int, y: int) -> Node:
        """Koordinatlara göre düğüm getir"""
        if (x, y) not in self.nodes:
            self.nodes[(x, y)] = Node(x, y)
        return self.nodes[(x, y)]
    
    def heuristic(self, node1: Node, node2: Node) -> float:
        """Heuristik fonksiyon (Euclidean distance)"""
        dx = abs(node1.x - node2.x)
        dy = abs(node1.y - node2.y)
        return self.heuristic_weight * math.sqrt(dx*dx + dy*dy)
    
    def get_neighbors(self, node: Node) -> List[Node]:
        """Bir düğümün komşularını getir"""
        neighbors = []
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), 
                     (0, 1), (1, -1), (1, 0), (1, 1)]
        
        for dx, dy in directions:
            nx, ny = node.x + dx, node.y + dy
            if (0 <= nx < self.width and 0 <= ny < self.height and
                not self.grid_map.is_obstacle(nx, ny)):
                neighbors.append(self.get_node(nx, ny))
        
        return neighbors
    
    def get_cost(self, node1: Node, node2: Node) -> float:
        """İki düğüm arasındaki maliyet"""
        if self.grid_map.is_obstacle(node2.x, node2.y):
            return float('inf')
        
        # Diagonal ve düz hareket maliyetleri
        dx = abs(node1.x - node2.x)
        dy = abs(node1.y - node2.y)
        
        if dx == 1 and dy == 1:  # Diagonal
            return math.sqrt(2) + self.grid_map.get_terrain_cost(node2.x, node2.y)
        else:  # Düz hareket
            return 1.0 + self.grid_map.get_terrain_cost(node2.x, node2.y)
    
    def calculate_key(self, node: Node) -> Tuple[float, float]:
        """Düğümün priority key'ini hesapla"""
        k1 = min(node.g, node.rhs) + self.heuristic(node, self.start)
        k2 = min(node.g, node.rhs)
        return (k1, k2)
    
    def initialize_search(self, start: Tuple[int, int], goal: Tuple[int, int]):
        """Arama sürecini başlat"""
        self.start = self.get_node(start[0], start[1])
        self.goal = self.get_node(goal[0], goal[1])
        self.last_start = self.start
        
        # Tüm düğümleri sıfırla
        for node in self.nodes.values():
            node.g = float('inf')
            node.rhs = float('inf')
        
        # Priority queue'yu temizle
        self.open_list.clear()
        
        # Hedef düğümü başlat
        self.goal.rhs = 0
        self.goal.h = self.heuristic(self.goal, self.start)
        self.open_list.insert(self.goal, self.calculate_key(self.goal))
    
    def update_vertex(self, node: Node):
        """Düğümü güncelle"""
        if node != self.goal:
            min_rhs = float('inf')
            for neighbor in self.get_neighbors(node):
                cost = self.get_cost(node, neighbor) + neighbor.g
                if cost < min_rhs:
                    min_rhs = cost
            node.rhs = min_rhs
        
        # Priority queue'dan kaldır
        if self.open_list.contains(node):
            self.open_list.remove(node)
        
        # Tutarsızsa tekrar ekle
        if node.g != node.rhs:
            node.h = self.heuristic(node, self.start)
            self.open_list.insert(node, self.calculate_key(node))
    
    def compute_shortest_path(self):
        """En kısa yolu hesapla"""
        while (not self.open_list.empty() and 
               (self.open_list.top_key() < self.calculate_key(self.start) or
                self.start.rhs != self.start.g)):
            
            current = self.open_list.pop()
            self.stats['nodes_expanded'] += 1
            
            if current.g > current.rhs:
                current.g = current.rhs
                for neighbor in self.get_neighbors(current):
                    if neighbor != self.goal:
                        neighbor.rhs = min(neighbor.rhs, 
                                         self.get_cost(neighbor, current) + current.g)
                    self.update_vertex(neighbor)
            else:
                current.g = float('inf')
                neighbors = self.get_neighbors(current) + [current]
                for neighbor in neighbors:
                    self.update_vertex(neighbor)
    
    def extract_path(self) -> List[Tuple[int, int]]:
        """Hesaplanan yolu çıkar"""
        if self.start.g == float('inf'):
            return []  # Yol bulunamadı
        
        path = []
        current = self.start
        
        while current != self.goal:
            path.append((current.x, current.y))
            
            # En iyi komşuyu bul
            best_neighbor = None
            best_cost = float('inf')
            
            for neighbor in self.get_neighbors(current):
                cost = self.get_cost(current, neighbor) + neighbor.g
                if cost < best_cost:
                    best_cost = cost
                    best_neighbor = neighbor
            
            if best_neighbor is None:
                break  # Takılı kaldı
                
            current = best_neighbor
        
        path.append((self.goal.x, self.goal.y))
        return path
    
    def plan_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Yol planla"""
        import time
        start_time = time.time()
        
        self.initialize_search(start, goal)
        self.compute_shortest_path()
        path = self.extract_path()
        
        planning_time = time.time() - start_time
        self.stats['total_planning_time'] += planning_time
        
        return path
    
    def update_obstacles(self, changed_cells: List[Tuple[int, int, bool]]):
        """Engelleri güncelle ve yeniden planla"""
        self.stats['replanning_count'] += 1
        
        # Değişen hücreler için düğümleri güncelle
        for x, y, is_obstacle in changed_cells:
            node = self.get_node(x, y)
            
            # Bu düğümün komşularını güncelle
            neighbors = self.get_neighbors(node)
            for neighbor in neighbors:
                self.update_vertex(neighbor)
            
            # Kendi düğümünü de güncelle
            self.update_vertex(node)
        
        # Başlangıç değiştiyse heuristiği güncelle
        if self.last_start != self.start:
            for node in self.nodes.values():
                node.h = self.heuristic(node, self.start)
            self.last_start = self.start
        
        self.compute_shortest_path()
    
    def replan_path(self, new_start: Optional[Tuple[int, int]] = None) -> List[Tuple[int, int]]:
        """Yeniden planla"""
        if new_start:
            self.start = self.get_node(new_start[0], new_start[1])
        
        self.compute_shortest_path()
        return self.extract_path()