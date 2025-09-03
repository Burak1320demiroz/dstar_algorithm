import numpy as np
import random
from typing import List, Tuple, Optional

class GridMap:
    """Grid tabanlı harita sınıfı"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid = np.zeros((height, width), dtype=np.int8)
        self.terrain_costs = np.ones((height, width), dtype=np.float32)
        
        # 0: Serbest alan, 1: Engel, 2: Zor arazi
        self.FREE = 0
        self.OBSTACLE = 1
        self.ROUGH_TERRAIN = 2
    
    def is_valid_cell(self, x: int, y: int) -> bool:
        """Hücre geçerli mi kontrolü"""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def is_obstacle(self, x: int, y: int) -> bool:
        """Engel kontrolü"""
        if not self.is_valid_cell(x, y):
            return True
        return self.grid[y, x] == self.OBSTACLE
    
    def set_obstacle(self, x: int, y: int, is_obstacle: bool = True):
        """Engel ayarla"""
        if self.is_valid_cell(x, y):
            self.grid[y, x] = self.OBSTACLE if is_obstacle else self.FREE
    
    def add_obstacle(self, x1: int, y1: int, x2: int, y2: int):
        """Dikdörtgen engel ekle"""
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        
        for y in range(max(0, y1), min(self.height, y2 + 1)):
            for x in range(max(0, x1), min(self.width, x2 + 1)):
                self.grid[y, x] = self.OBSTACLE
    
    def add_circular_obstacle(self, center_x: int, center_y: int, radius: int):
        """Dairesel engel ekle"""
        for y in range(max(0, center_y - radius), 
                      min(self.height, center_y + radius + 1)):
            for x in range(max(0, center_x - radius), 
                          min(self.width, center_x + radius + 1)):
                if ((x - center_x) ** 2 + (y - center_y) ** 2) <= radius ** 2:
                    self.grid[y, x] = self.OBSTACLE
    
    def add_random_obstacles(self, obstacle_ratio: float = 0.2):
        """Rastgele engeller ekle"""
        total_cells = self.width * self.height
        obstacle_count = int(total_cells * obstacle_ratio)
        
        for _ in range(obstacle_count):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.grid[y, x] = self.OBSTACLE
    
    def set_terrain_cost(self, x: int, y: int, cost: float):
        """Arazi maliyeti ayarla"""
        if self.is_valid_cell(x, y):
            self.terrain_costs[y, x] = cost
            if cost > 1.0:
                self.grid[y, x] = self.ROUGH_TERRAIN
    
    def get_terrain_cost(self, x: int, y: int) -> float:
        """Arazi maliyetini getir"""
        if not self.is_valid_cell(x, y):
            return float('inf')
        return self.terrain_costs[y, x]
    
    def add_rough_terrain_area(self, x1: int, y1: int, x2: int, y2: int, cost: float = 3.0):
        """Zor arazi alanı ekle"""
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        
        for y in range(max(0, y1), min(self.height, y2 + 1)):
            for x in range(max(0, x1), min(self.width, x2 + 1)):
                if self.grid[y, x] != self.OBSTACLE:
                    self.grid[y, x] = self.ROUGH_TERRAIN
                    self.terrain_costs[y, x] = cost
    
    def clear_area(self, x1: int, y1: int, x2: int, y2: int):
        """Alanı temizle"""
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        
        for y in range(max(0, y1), min(self.height, y2 + 1)):
            for x in range(max(0, x1), min(self.width, x2 + 1)):
                self.grid[y, x] = self.FREE
                self.terrain_costs[y, x] = 1.0
    
    def get_neighbors_8(self, x: int, y: int) -> List[Tuple[int, int]]:
        """8-bağlantılı komşuları getir"""
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if self.is_valid_cell(nx, ny) and not self.is_obstacle(nx, ny):
                    neighbors.append((nx, ny))
        return neighbors
    
    def get_neighbors_4(self, x: int, y: int) -> List[Tuple[int, int]]:
        """4-bağlantılı komşuları getir"""
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if self.is_valid_cell(nx, ny) and not self.is_obstacle(nx, ny):
                neighbors.append((nx, ny))
        return neighbors