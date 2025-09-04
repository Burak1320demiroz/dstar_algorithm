from src.dstar.dstar_lite import DStarLite, Node
from src.environment.traffic_environment import TrafficEnvironment
import time
import numpy as np
from typing import List, Tuple, Dict, Optional

class TrafficAwareDStar(DStarLite):
    """Trafik farkındalıklı D* Lite"""
    
    def __init__(self, traffic_env: TrafficEnvironment, heuristic_weight: float = 1.2):
        self.traffic_env = traffic_env
        self.width = traffic_env.width
        self.height = traffic_env.height
        self.heuristic_weight = heuristic_weight
        
        # Node haritası
        self.nodes = {}
        self.initialize_nodes()
        
        # Priority queue
        from src.utils.data_structures import PriorityQueue
        self.open_list = PriorityQueue()
        
        # Planlama parametreleri
        self.start = None
        self.goal = None
        self.last_start = None
        
        # Trafik güncellemesi
        self.last_traffic_update = 0.0
        self.traffic_update_interval = 1.0  # saniye
        
        # Gelişmiş istatistikler
        self.stats = {
            'nodes_expanded': 0,
            'replanning_count': 0,
            'total_planning_time': 0.0,
            'traffic_updates': 0,
            'average_cost': 0.0,
            'path_safety_score': 0.0
        }
    
    def get_neighbors(self, node: Node) -> List[Node]:
        """Trafik farkındalıklı komşu bulma"""
        neighbors = []
        # 8 yönlü hareket + köşegen öncelik
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),    # Düz yönler
            (-1, -1), (-1, 1), (1, -1), (1, 1)   # Köşegen yönler
        ]
        
        for dx, dy in directions:
            nx, ny = node.x + dx, node.y + dy
            
            if self.traffic_env.is_road(nx, ny):
                neighbors.append(self.get_node(nx, ny))
        
        return neighbors
    
    def get_cost(self, node1: Node, node2: Node) -> float:
        """Trafik farkındalıklı maliyet hesaplama"""
        # Dinamik maliyet al
        dynamic_cost = self.traffic_env.get_dynamic_cost(node2.x, node2.y)
        
        if dynamic_cost == float('inf'):
            return float('inf')
        
        # Mesafe maliyeti
        dx = abs(node1.x - node2.x)
        dy = abs(node1.y - node2.y)
        
        if dx == 1 and dy == 1:  # Diagonal
            distance_cost = np.sqrt(2)
        else:  # Düz hareket
            distance_cost = 1.0
        
        return distance_cost * dynamic_cost
    
    def heuristic(self, node1: Node, node2: Node) -> float:
        """Gelişmiş heuristik - Manhattan + Euclidean hibrit"""
        dx = abs(node1.x - node2.x)
        dy = abs(node1.y - node2.y)
        
        # Hibrit heuristik: Manhattan + Euclidean
        manhattan = dx + dy
        euclidean = np.sqrt(dx*dx + dy*dy)
        
        # Trafik yoğunluğuna göre heuristik ağırlık ayarlama
        traffic_factor = 1.0 + self.traffic_env.traffic_grid[node1.y, node1.x] * 0.5
        
        return self.heuristic_weight * (0.7 * manhattan + 0.3 * euclidean) * traffic_factor
    
    def plan_path_with_traffic(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Trafik farkındalıklı yol planlama"""
        start_time = time.time()
        
        # Trafik güncelle
        self.traffic_env.update_traffic(0.1)
        self.stats['traffic_updates'] += 1
        
        # Normal D* planlaması
        path = self.plan_path(start, goal)
        
        if path:
            # Path kalitesi analizi
            self._analyze_path_quality(path)
        
        planning_time = time.time() - start_time
        self.stats['total_planning_time'] += planning_time
        
        return path
    
    def replan_with_traffic_update(self, dt: float = 0.1) -> List[Tuple[int, int]]:
        """Trafik güncellemesi ile yeniden planlama"""
        current_time = time.time()
        
        # Periyodik trafik güncellemesi
        if current_time - self.last_traffic_update >= self.traffic_update_interval:
            self.traffic_env.update_traffic(dt)
            self.last_traffic_update = current_time
            self.stats['traffic_updates'] += 1
            
            # Değişen maliyetleri güncelle
            self._update_dynamic_costs()
        
        return self.replan_path()
    
    def _update_dynamic_costs(self):
        """Dinamik maliyetlerde değişiklik varsa güncelle"""
        changed_cells = []
        
        # Tüm yol hücrelerini kontrol et (optimizasyon için sadece değişenler)
        for y in range(self.height):
            for x in range(self.width):
                if self.traffic_env.is_road(x, y):
                    # Eski maliyet ile yeni maliyeti karşılaştır
                    current_cost = self.traffic_env.get_dynamic_cost(x, y)
                    node = self.get_node(x, y)
                    
                    # Önemli maliyet değişikliği varsa güncelle
                    if hasattr(node, 'last_cost'):
                        cost_change = abs(current_cost - node.last_cost)
                        if cost_change > 0.5:  # %50'den fazla değişim
                            changed_cells.append((x, y, False))  # False = cost change
                    
                    node.last_cost = current_cost
        
        if changed_cells:
            self.update_obstacles(changed_cells)
    
    def _analyze_path_quality(self, path: List[Tuple[int, int]]):
        """Yol kalitesi analizi"""
        if not path:
            return
        
        total_cost = 0.0
        safety_scores = []
        
        for i, (x, y) in enumerate(path):
            # Maliyet analizi
            cost = self.traffic_env.get_dynamic_cost(x, y)
            total_cost += cost
            
            # Güvenlik skoru (düşük trafik + yüksek hız limiti = güvenli)
            traffic_density = self.traffic_env.traffic_grid[y, x]
            speed_limit = self.traffic_env.speed_limit_grid[y, x]
            safety_score = (speed_limit / 90.0) * (1.0 - min(traffic_density, 1.0))
            safety_scores.append(safety_score)
        
        self.stats['average_cost'] = total_cost / len(path)
        self.stats['path_safety_score'] = sum(safety_scores) / len(safety_scores)
    
    def get_real_time_traffic_info(self) -> Dict:
        """Gerçek zamanlı trafik bilgisi"""
        return {
            'total_vehicles': len(self.traffic_env.moving_vehicles),
            'traffic_density': self.traffic_env.traffic_density,
            'active_traffic_lights': len([l for l in self.traffic_env.traffic_lights if l.state != "green"]),
            'average_speed': np.mean([v.vx**2 + v.vy**2 for v in self.traffic_env.moving_vehicles])**0.5 if self.traffic_env.moving_vehicles else 0,
            'congestion_level': min(1.0, np.mean(self.traffic_env.traffic_grid))
        }