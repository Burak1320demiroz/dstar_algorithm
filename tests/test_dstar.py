import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.dstar.dstar_lite import DStarLite, Node
from src.environment.grid_map import GridMap
import numpy as np

class TestDStarLite(unittest.TestCase):
    """D* Lite algoritması test sınıfı"""
    
    def setUp(self):
        """Her test öncesi kurulum"""
        self.grid_map = GridMap(20, 20)
        self.planner = DStarLite(self.grid_map)
    
    def test_node_creation(self):
        """Node oluşturma testi"""
        node = Node(5, 10)
        self.assertEqual(node.x, 5)
        self.assertEqual(node.y, 10)
        self.assertEqual(node.g, float('inf'))
        self.assertEqual(node.rhs, float('inf'))
    
    def test_node_equality(self):
        """Node eşitlik testi"""
        node1 = Node(5, 5)
        node2 = Node(5, 5)
        node3 = Node(5, 6)
        
        self.assertEqual(node1, node2)
        self.assertNotEqual(node1, node3)
    
    def test_heuristic_calculation(self):
        """Heuristik hesaplama testi"""
        node1 = Node(0, 0)
        node2 = Node(3, 4)
        
        # Euclidean distance: sqrt(3^2 + 4^2) = 5
        expected_distance = 5.0
        calculated_distance = self.planner.heuristic(node1, node2)
        
        self.assertAlmostEqual(calculated_distance, expected_distance, places=2)
    
    def test_neighbors_empty_grid(self):
        """Boş grid'de komşu bulma testi"""
        node = self.planner.get_node(10, 10)
        neighbors = self.planner.get_neighbors(node)
        
        # 8 komşu olmalı (grid ortasında)
        self.assertEqual(len(neighbors), 8)
        
        # Köşede daha az komşu olmalı
        corner_node = self.planner.get_node(0, 0)
        corner_neighbors = self.planner.get_neighbors(corner_node)
        self.assertEqual(len(corner_neighbors), 3)
    
    def test_neighbors_with_obstacles(self):
        """Engelli grid'de komşu bulma testi"""
        # Merkeze engel ekle
        self.grid_map.set_obstacle(10, 10, True)
        
        node = self.planner.get_node(9, 9)
        neighbors = self.planner.get_neighbors(node)
        
        # (10,10) komşu olmamalı
        obstacle_node = self.planner.get_node(10, 10)
        self.assertNotIn(obstacle_node, neighbors)
    
    def test_simple_path_finding(self):
        """Basit yol bulma testi"""
        start = (1, 1)
        goal = (5, 5)
        
        path = self.planner.plan_path(start, goal)
        
        self.assertIsNotNone(path)
        self.assertGreater(len(path), 0)
        self.assertEqual(path[0], start)
        self.assertEqual(path[-1], goal)
    
    def test_path_finding_with_obstacles(self):
        """Engelli grid'de yol bulma testi"""
        # Duvar oluştur
        for y in range(5, 15):
            self.grid_map.set_obstacle(10, y, True)
        
        start = (5, 10)
        goal = (15, 10)
        
        path = self.planner.plan_path(start, goal)
        
        self.assertIsNotNone(path)
        self.assertGreater(len(path), 0)
        
        # Yolun duvardan geçmediğini kontrol et
        for x, y in path:
            self.assertFalse(self.grid_map.is_obstacle(x, y))
    
    def test_no_path_exists(self):
        """Yol bulunamayan durum testi"""
        # Başlangıcı çevreleyen duvarlar
        for x in range(4, 7):
            for y in range(4, 7):
                if not (x == 5 and y == 5):  # Başlangıç hariç
                    self.grid_map.set_obstacle(x, y, True)
        
        start = (5, 5)
        goal = (15, 15)
        
        path = self.planner.plan_path(start, goal)
        
        self.assertEqual(len(path), 0)
    
    def test_dynamic_obstacle_update(self):
        """Dinamik engel güncelleme testi"""
        start = (1, 1)
        goal = (10, 10)
        
        # İlk yol
        path1 = self.planner.plan_path(start, goal)
        self.assertIsNotNone(path1)
        
        # Yolun ortasına engel ekle
        if len(path1) > 2:
            mid_point = path1[len(path1)//2]
            self.grid_map.set_obstacle(mid_point[0], mid_point[1], True)
            
            # Güncellemeyi bildir
            self.planner.update_obstacles([(mid_point[0], mid_point[1], True)])
            
            # Yeniden planla
            path2 = self.planner.replan_path()
            
            self.assertIsNotNone(path2)
            # Yeni yol engelden geçmemeli
            self.assertNotIn(mid_point, path2)
    
    def test_cost_calculation(self):
        """Maliyet hesaplama testi"""
        node1 = Node(0, 0)
        node2 = Node(1, 0)  # Yatay komşu
        node3 = Node(1, 1)  # Diagonal komşu
        
        # Yatay/dikey maliyet = 1.0
        horizontal_cost = self.planner.get_cost(node1, node2)
        self.assertAlmostEqual(horizontal_cost, 2.0, places=1)  # 1.0 + terrain_cost(1.0)
        
        # Diagonal maliyet = sqrt(2)
        diagonal_cost = self.planner.get_cost(node1, node3)
        expected_diagonal = np.sqrt(2) + 1.0  # sqrt(2) + terrain_cost(1.0)
        self.assertAlmostEqual(diagonal_cost, expected_diagonal, places=1)
    
    def test_priority_queue_operations(self):
        """Priority queue işlemlerini test et"""
        from src.utils.data_structures import PriorityQueue
        
        pq = PriorityQueue()
        
        # Boş queue testi
        self.assertTrue(pq.empty())
        
        # Eleman ekleme
        node1 = Node(1, 1)
        node2 = Node(2, 2)
        
        pq.insert(node1, (5.0, 3.0))
        pq.insert(node2, (3.0, 2.0))
        
        self.assertFalse(pq.empty())
        self.assertTrue(pq.contains(node1))
        self.assertTrue(pq.contains(node2))
        
        # En yüksek öncelikli elementi çıkar (en düşük key)
        popped = pq.pop()
        self.assertEqual(popped, node2)  # (3.0, 2.0) < (5.0, 3.0)
        
        # Top key testi
        top_key = pq.top_key()
        self.assertEqual(top_key, (5.0, 3.0))

class TestGridMap(unittest.TestCase):
    """GridMap test sınıfı"""
    
    def setUp(self):
        """Her test öncesi kurulum"""
        self.grid_map = GridMap(10, 8)
    
    def test_grid_initialization(self):
        """Grid başlatma testi"""
        self.assertEqual(self.grid_map.width, 10)
        self.assertEqual(self.grid_map.height, 8)
        self.assertEqual(self.grid_map.grid.shape, (8, 10))
    
    def test_valid_cell_check(self):
        """Geçerli hücre kontrolü testi"""
        self.assertTrue(self.grid_map.is_valid_cell(5, 5))
        self.assertTrue(self.grid_map.is_valid_cell(0, 0))
        self.assertTrue(self.grid_map.is_valid_cell(9, 7))
        
        self.assertFalse(self.grid_map.is_valid_cell(-1, 5))
        self.assertFalse(self.grid_map.is_valid_cell(5, -1))
        self.assertFalse(self.grid_map.is_valid_cell(10, 5))
        self.assertFalse(self.grid_map.is_valid_cell(5, 8))
    
    def test_obstacle_operations(self):
        """Engel işlemleri testi"""
        # Başlangıçta engel yok
        self.assertFalse(self.grid_map.is_obstacle(5, 5))
        
        # Engel ekle
        self.grid_map.set_obstacle(5, 5, True)
        self.assertTrue(self.grid_map.is_obstacle(5, 5))
        
        # Engeli kaldır
        self.grid_map.set_obstacle(5, 5, False)
        self.assertFalse(self.grid_map.is_obstacle(5, 5))
    
    def test_rectangular_obstacle(self):
        """Dikdörtgen engel testi"""
        self.grid_map.add_obstacle(2, 2, 5, 4)
        
        # Engel alanı içindeki tüm hücreler engel olmalı
        for y in range(2, 5):
            for x in range(2, 6):
                self.assertTrue(self.grid_map.is_obstacle(x, y))
        
        # Dış alanlar engel olmamalı
        self.assertFalse(self.grid_map.is_obstacle(1, 2))
        self.assertFalse(self.grid_map.is_obstacle(6, 2))
        self.assertFalse(self.grid_map.is_obstacle(2, 1))
        self.assertFalse(self.grid_map.is_obstacle(2, 5))
    
    def test_circular_obstacle(self):
        """Dairesel engel testi"""
        center_x, center_y, radius = 5, 4, 2
        self.grid_map.add_circular_obstacle(center_x, center_y, radius)
        
        # Merkez engel olmalı
        self.assertTrue(self.grid_map.is_obstacle(center_x, center_y))
        
        # Yarıçap içindeki noktalar engel olmalı
        self.assertTrue(self.grid_map.is_obstacle(center_x + 1, center_y))
        self.assertTrue(self.grid_map.is_obstacle(center_x, center_y + 1))
        
        # Yarıçap dışındaki noktalar engel olmamalı
        self.assertFalse(self.grid_map.is_obstacle(center_x + 3, center_y))
        self.assertFalse(self.grid_map.is_obstacle(center_x, center_y + 3))
    
    def test_terrain_cost(self):
        """Arazi maliyeti testi"""
        # Varsayılan maliyet 1.0 olmalı
        self.assertEqual(self.grid_map.get_terrain_cost(5, 5), 1.0)
        
        # Maliyet ayarlama
        self.grid_map.set_terrain_cost(5, 5, 2.5)
        self.assertEqual(self.grid_map.get_terrain_cost(5, 5), 2.5)
        
        # Geçersiz koordinat için sonsuz maliyet
        self.assertEqual(self.grid_map.get_terrain_cost(-1, 5), float('inf'))
        self.assertEqual(self.grid_map.get_terrain_cost(15, 5), float('inf'))
    
    def test_neighbors(self):
        """Komşu bulma testi"""
        # 8-bağlantılı komşular
        neighbors_8 = self.grid_map.get_neighbors_8(5, 4)
        self.assertEqual(len(neighbors_8), 8)
        
        # 4-bağlantılı komşular  
        neighbors_4 = self.grid_map.get_neighbors_4(5, 4)
        self.assertEqual(len(neighbors_4), 4)
        
        # Köşede daha az komşu
        corner_neighbors_8 = self.grid_map.get_neighbors_8(0, 0)
        self.assertEqual(len(corner_neighbors_8), 3)
        
        corner_neighbors_4 = self.grid_map.get_neighbors_4(0, 0)
        self.assertEqual(len(corner_neighbors_4), 2)

class TestVehicleModel(unittest.TestCase):
    """Vehicle model test sınıfı"""
    
    def setUp(self):
        """Her test öncesi kurulum"""
        from src.vehicle.vehicle_model import AutonomousVehicle
        self.vehicle = AutonomousVehicle(
            wheelbase=2.5,
            max_speed=10.0,
            max_steering_angle=np.pi/4,
            max_acceleration=3.0
        )
    
    def test_vehicle_initialization(self):
        """Araç başlatma testi"""
        self.assertEqual(self.vehicle.wheelbase, 2.5)
        self.assertEqual(self.vehicle.max_speed, 10.0)
        self.assertEqual(self.vehicle.max_steering_angle, np.pi/4)
        self.assertEqual(self.vehicle.state.x, 0.0)
        self.assertEqual(self.vehicle.state.y, 0.0)
    
    def test_vehicle_position_setting(self):
        """Araç pozisyon ayarlama testi"""
        self.vehicle.set_position(10.0, 5.0, np.pi/2)
        
        self.assertEqual(self.vehicle.state.x, 10.0)
        self.assertEqual(self.vehicle.state.y, 5.0)
        self.assertEqual(self.vehicle.state.theta, np.pi/2)
    
    def test_bicycle_model_straight(self):
        """Düz hareket bicycle model testi"""
        initial_x = self.vehicle.state.x
        initial_y = self.vehicle.state.y
        
        # Düz hareket (direksiyon 0, pozitif ivme)
        self.vehicle.bicycle_model(dt=1.0, acceleration=2.0, steering_angle=0.0)
        
        # X yönünde hareket etmeli
        self.assertGreater(self.vehicle.state.x, initial_x)
        self.assertEqual(self.vehicle.state.y, initial_y)  # Y değişmemeli
        self.assertEqual(self.vehicle.state.v, 2.0)  # Hız = ivme * zaman
    
    def test_bicycle_model_turning(self):
        """Dönüşlü hareket bicycle model testi"""
        self.vehicle.state.v = 5.0  # Başlangıç hızı
        initial_theta = self.vehicle.state.theta
        
        # Sola dönüş
        self.vehicle.bicycle_model(dt=0.1, acceleration=0.0, steering_angle=0.1)
        
        # Yönelim değişmeli
        self.assertNotEqual(self.vehicle.state.theta, initial_theta)
    
    def test_speed_limits(self):
        """Hız limiti testi"""
        # Maksimum hızı aş
        very_high_acceleration = 50.0
        dt = 1.0
        
        for _ in range(10):  # Birkaç adım
            self.vehicle.bicycle_model(dt, very_high_acceleration, 0.0)
        
        # Hız maksimum hızı geçmemeli
        self.assertLessEqual(self.vehicle.state.v, self.vehicle.max_speed)
    
    def test_steering_limits(self):
        """Direksiyon limiti testi"""
        # Aşırı direksiyon açısı
        extreme_steering = np.pi  # 180 derece
        
        self.vehicle.bicycle_model(dt=0.1, acceleration=1.0, steering_angle=extreme_steering)
        
        # Gerçek direksiyon açısı limit içinde olmalı
        self.assertLessEqual(abs(self.vehicle.state.steering), self.vehicle.max_steering_angle)

if __name__ == '__main__':
    # Test suite oluştur
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Test sınıflarını ekle
    suite.addTests(loader.loadTestsFromTestCase(TestDStarLite))
    suite.addTests(loader.loadTestsFromTestCase(TestGridMap))
    suite.addTests(loader.loadTestsFromTestCase(TestVehicleModel))
    
    # Testleri çalıştır
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Sonuç özeti
    if result.wasSuccessful():
        print(f"\n🎉 Tüm testler başarılı! ({result.testsRun} test)")
    else:
        print(f"\n❌ {len(result.failures)} test başarısız, {len(result.errors)} hata")
        print(f"Toplam {result.testsRun} test çalıştırıldı.")