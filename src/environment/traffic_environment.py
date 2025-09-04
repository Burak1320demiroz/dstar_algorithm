import numpy as np
import random
import time
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from enum import Enum

class RoadType(Enum):
    """Yol tipleri"""
    HIGHWAY = 1         # Otoyol
    MAIN_STREET = 2     # Ana cadde  
    STREET = 3          # Normal sokak
    NARROW_STREET = 4   # Dar sokak
    PARKING_LOT = 5     # Otopark
    INTERSECTION = 6    # Kavşak
    ROUNDABOUT = 7      # Dönel kavşak

@dataclass
class TrafficLight:
    """Trafik ışığı"""
    x: int
    y: int
    state: str = "green"  # green, yellow, red
    cycle_time: float = 30.0  # saniye
    current_time: float = 0.0

@dataclass
class MovingVehicle:
    """Hareket eden araç"""
    x: float
    y: float
    vx: float  # x yönü hız
    vy: float  # y yönü hız
    size: Tuple[int, int] = (3, 2)  # boyut (length, width)
    vehicle_type: str = "car"  # car, truck, bus
    route: List[Tuple[int, int]] = None

class TrafficEnvironment:
    """Trafik ortamı simülatörü"""
    
    def __init__(self, width: int = 200, height: int = 150):
        self.width = width
        self.height = height
        
        # Grid layers
        self.road_grid = np.zeros((height, width), dtype=np.int8)
        self.building_grid = np.zeros((height, width), dtype=np.int8)
        self.traffic_grid = np.zeros((height, width), dtype=np.float32)
        self.speed_limit_grid = np.ones((height, width), dtype=np.float32) * 50  # km/h
        
        # Trafik elemanları
        self.traffic_lights: List[TrafficLight] = []
        self.moving_vehicles: List[MovingVehicle] = []
        self.parking_areas: List[Tuple[int, int, int, int]] = []
        
        # Dinamik durumlar
        self.current_time = 0.0
        self.traffic_density = 0.3  # 0-1 arası
        
        self._build_istanbul_like_city()
    
    def _build_istanbul_like_city(self):
        """İstanbul benzeri şehir haritası oluştur"""
        print("🏙️ İstanbul benzeri şehir haritası oluşturuluyor...")
        
        # 1. Ana caddeleri oluştur (Büyükdere Caddesi, Barbaros Bulvarı vb.)
        self._create_main_highways()
        
        # 2. Bina blokları (Levent, Maslak, Şişli vb.)
        self._create_building_blocks()
        
        # 3. Kavşaklar (Zincirlikuyu, Gayrettepe vb.)
        self._create_major_intersections()
        
        # 4. Dar sokaklar ve ara yollar
        self._create_side_streets()
        
        # 5. Otopark alanları
        self._create_parking_areas()
        
        # 6. Trafik ışıkları
        self._place_traffic_lights()
        
        # 7. Başlangıç trafiği
        self._spawn_initial_traffic()
    
    def _create_main_highways(self):
        """Ana otoyolları oluştur"""
        # Dikey ana cadde (Büyükdere Caddesi benzeri)
        main_vertical = self.width // 3
        for y in range(0, self.height):
            for lane in range(-4, 5):  # 8 şeritli yol
                x = main_vertical + lane
                if 0 <= x < self.width:
                    self.road_grid[y, x] = RoadType.HIGHWAY.value
                    self.speed_limit_grid[y, x] = 80  # 80 km/h
        
        # Yatay ana cadde (TEM Otoyolu benzeri)  
        main_horizontal = self.height // 2
        for x in range(0, self.width):
            for lane in range(-3, 4):  # 6 şeritli yol
                y = main_horizontal + lane
                if 0 <= y < self.height:
                    self.road_grid[y, x] = RoadType.HIGHWAY.value
                    self.speed_limit_grid[y, x] = 90  # 90 km/h
        
        # İkinci yatay ana cadde (D-100 benzeri)
        second_horizontal = self.height // 4 * 3
        for x in range(0, self.width):
            for lane in range(-2, 3):  # 4 şeritli yol
                y = second_horizontal + lane
                if 0 <= y < self.height:
                    self.road_grid[y, x] = RoadType.MAIN_STREET.value
                    self.speed_limit_grid[y, x] = 70  # 70 km/h
    
    def _create_building_blocks(self):
        """Bina bloklarını oluştur"""
        # Levent benzeri gökdelen bölgesi
        levent_area = [(50, 20, 80, 40), (85, 25, 110, 45)]
        for x1, y1, x2, y2 in levent_area:
            self._add_building_block(x1, y1, x2, y2, "skyscraper")
        
        # Şişli benzeri karma bölge
        sisli_area = [(20, 60, 45, 85), (55, 65, 75, 90)]
        for x1, y1, x2, y2 in sisli_area:
            self._add_building_block(x1, y1, x2, y2, "mixed")
        
        # Maslak benzeri iş merkezi
        maslak_area = [(120, 30, 150, 55), (155, 35, 180, 60)]
        for x1, y1, x2, y2 in maslak_area:
            self._add_building_block(x1, y1, x2, y2, "business")
        
        # Konut bölgeleri
        residential_areas = [
            (10, 100, 40, 130), (70, 105, 100, 135),
            (130, 85, 160, 115), (170, 90, 195, 120)
        ]
        for x1, y1, x2, y2 in residential_areas:
            self._add_building_block(x1, y1, x2, y2, "residential")
    
    def _add_building_block(self, x1: int, y1: int, x2: int, y2: int, block_type: str):
        """Bina bloğu ekle"""
        for y in range(y1, min(y2, self.height)):
            for x in range(x1, min(x2, self.width)):
                if self.road_grid[y, x] == 0:  # Yol değilse
                    self.building_grid[y, x] = 1
        
        # Blok etrafında sokaklar
        street_width = 2 if block_type == "residential" else 3
        
        # Üst ve alt sokaklar
        for x in range(max(0, x1-1), min(self.width, x2+1)):
            for offset in range(-street_width//2, street_width//2 + 1):
                # Üst sokak
                y_top = y1 - 2 + offset
                if 0 <= y_top < self.height and self.building_grid[y_top, x] == 0:
                    self.road_grid[y_top, x] = RoadType.STREET.value
                    self.speed_limit_grid[y_top, x] = 50
                
                # Alt sokak  
                y_bottom = y2 + 2 + offset
                if 0 <= y_bottom < self.height and self.building_grid[y_bottom, x] == 0:
                    self.road_grid[y_bottom, x] = RoadType.STREET.value
                    self.speed_limit_grid[y_bottom, x] = 50
        
        # Sol ve sağ sokaklar
        for y in range(max(0, y1-1), min(self.height, y2+1)):
            for offset in range(-street_width//2, street_width//2 + 1):
                # Sol sokak
                x_left = x1 - 2 + offset
                if 0 <= x_left < self.width and self.building_grid[y, x_left] == 0:
                    self.road_grid[y, x_left] = RoadType.STREET.value
                    self.speed_limit_grid[y, x_left] = 50
                
                # Sağ sokak
                x_right = x2 + 2 + offset
                if 0 <= x_right < self.width and self.building_grid[y, x_right] == 0:
                    self.road_grid[y, x_right] = RoadType.STREET.value
                    self.speed_limit_grid[y, x_right] = 50
    
    def _create_major_intersections(self):
        """Büyük kavşakları oluştur"""
        # Zincirlikuyu benzeri kavşak
        zincirlikuyu = (self.width // 3, self.height // 2)
        self._create_intersection(zincirlikuyu[0], zincirlikuyu[1], size=8)
        
        # Gayrettepe benzeri kavşak
        gayrettepe = (self.width // 3, self.height // 4)
        self._create_intersection(gayrettepe[0], gayrettepe[1], size=6)
        
        # Levent kavşağı
        levent = (self.width // 2, self.height // 3)
        self._create_intersection(levent[0], levent[1], size=7)
    
    def _create_intersection(self, center_x: int, center_y: int, size: int = 6):
        """Kavşak oluştur"""
        for dy in range(-size//2, size//2 + 1):
            for dx in range(-size//2, size//2 + 1):
                x, y = center_x + dx, center_y + dy
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.road_grid[y, x] = RoadType.INTERSECTION.value
                    self.speed_limit_grid[y, x] = 30  # Kavşakta yavaş
    
    def _create_side_streets(self):
        """Ara sokakları oluştur"""
        # Düzenli grid sokaklar
        for street_x in range(15, self.width - 15, 25):
            if abs(street_x - self.width // 3) > 10:  # Ana caddeden uzak
                for y in range(5, self.height - 5):
                    if (self.road_grid[y, street_x] == 0 and 
                        self.building_grid[y, street_x] == 0):
                        self.road_grid[y, street_x] = RoadType.NARROW_STREET.value
                        self.speed_limit_grid[y, street_x] = 30
        
        for street_y in range(15, self.height - 15, 20):
            if (abs(street_y - self.height // 2) > 10 and 
                abs(street_y - self.height // 4 * 3) > 10):
                for x in range(5, self.width - 5):
                    if (self.road_grid[street_y, x] == 0 and 
                        self.building_grid[street_y, x] == 0):
                        self.road_grid[street_y, x] = RoadType.NARROW_STREET.value
                        self.speed_limit_grid[street_y, x] = 30
    
    def _create_parking_areas(self):
        """Otopark alanları oluştur"""
        parking_locations = [
            (45, 85, 55, 95),    # AVM otoparkı
            (115, 45, 125, 55),  # İş merkezi otoparkı
            (25, 115, 35, 125),  # Konut otoparkı
            (165, 105, 175, 115) # Hastane otoparkı
        ]
        
        for x1, y1, x2, y2 in parking_locations:
            self.parking_areas.append((x1, y1, x2, y2))
            for y in range(y1, min(y2, self.height)):
                for x in range(x1, min(x2, self.width)):
                    if (self.road_grid[y, x] == 0 and 
                        self.building_grid[y, x] == 0):
                        self.road_grid[y, x] = RoadType.PARKING_LOT.value
                        self.speed_limit_grid[y, x] = 20
    
    def _place_traffic_lights(self):
        """Trafik ışıklarını yerleştir"""
        # Ana kavşaklarda trafik ışıkları
        major_intersections = [
            (self.width // 3, self.height // 2),
            (self.width // 3, self.height // 4),
            (self.width // 2, self.height // 3),
            (self.width // 4 * 3, self.height // 2)
        ]
        
        for x, y in major_intersections:
            # Her yönde trafik ışığı
            for dx, dy in [(0, -3), (3, 0), (0, 3), (-3, 0)]:
                light_x, light_y = x + dx, y + dy
                if 0 <= light_x < self.width and 0 <= light_y < self.height:
                    cycle_time = random.uniform(25, 35)
                    self.traffic_lights.append(
                        TrafficLight(light_x, light_y, "green", cycle_time)
                    )
    
    def _spawn_initial_traffic(self):
        """Başlangıç trafiğini oluştur"""
        # Trafik yoğunluğuna göre araç sayısı
        vehicle_count = int(self.width * self.height * 0.001 * self.traffic_density)
        
        for _ in range(vehicle_count):
            self._spawn_random_vehicle()
    
    def _spawn_random_vehicle(self):
        """Rastgele araç oluştur"""
        # Yol üzerinde rastgele konum bul
        attempts = 0
        while attempts < 100:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            
            if self.road_grid[y, x] > 0 and self._is_position_free(x, y):
                # Araç tipi seç
                vehicle_types = ["car", "truck", "bus", "motorcycle"]
                weights = [0.7, 0.15, 0.1, 0.05]
                vehicle_type = np.random.choice(vehicle_types, p=weights)
                
                # Hız seç (yol tipine göre)
                base_speed = self.speed_limit_grid[y, x] / 3.6  # m/s'ye çevir
                actual_speed = base_speed * random.uniform(0.8, 1.2)
                
                # Hareket yönü seç
                direction = random.uniform(0, 2 * np.pi)
                vx = actual_speed * np.cos(direction)
                vy = actual_speed * np.sin(direction)
                
                # Araç boyutu
                if vehicle_type == "truck":
                    size = (6, 3)
                elif vehicle_type == "bus":
                    size = (8, 3)
                elif vehicle_type == "motorcycle":
                    size = (2, 1)
                else:  # car
                    size = (4, 2)
                
                vehicle = MovingVehicle(x, y, vx, vy, size, vehicle_type)
                self.moving_vehicles.append(vehicle)
                break
            
            attempts += 1
    
    def _is_position_free(self, x: int, y: int, size: Tuple[int, int] = (4, 2)) -> bool:
        """Pozisyon boş mu kontrol et"""
        for vehicle in self.moving_vehicles:
            # Basit çakışma kontrolü
            if (abs(vehicle.x - x) < (size[0] + vehicle.size[0]) / 2 and
                abs(vehicle.y - y) < (size[1] + vehicle.size[1]) / 2):
                return False
        return True
    
    def update_traffic(self, dt: float = 0.1):
        """Trafiği güncelle"""
        self.current_time += dt
        
        # Trafik ışıklarını güncelle
        self._update_traffic_lights(dt)
        
        # Araçları hareket ettir
        self._update_moving_vehicles(dt)
        
        # Yeni araç spawn et
        if random.random() < 0.02 * self.traffic_density:  # %2 şans
            self._spawn_random_vehicle()
        
        # Trafik yoğunluğu matrisi güncelle
        self._update_traffic_density_grid()
    
    def _update_traffic_lights(self, dt: float):
        """Trafik ışıklarını güncelle"""
        for light in self.traffic_lights:
            light.current_time += dt
            
            if light.current_time >= light.cycle_time:
                light.current_time = 0
                # Döngüsel geçiş: green -> yellow -> red -> green
                if light.state == "green":
                    light.state = "yellow"
                    light.cycle_time = 3.0  # 3 saniye sarı
                elif light.state == "yellow":
                    light.state = "red"
                    light.cycle_time = 25.0  # 25 saniye kırmızı
                else:  # red
                    light.state = "green"
                    light.cycle_time = 30.0  # 30 saniye yeşil
    
    def _update_moving_vehicles(self, dt: float):
        """Hareket eden araçları güncelle"""
        vehicles_to_remove = []
        
        for i, vehicle in enumerate(self.moving_vehicles):
            # Basit hareket modeli
            new_x = vehicle.x + vehicle.vx * dt
            new_y = vehicle.y + vehicle.vy * dt
            
            # Sınırları kontrol et
            if (0 <= new_x < self.width - vehicle.size[0] and 
                0 <= new_y < self.height - vehicle.size[1]):
                
                # Yolda mı kontrol et
                if self.road_grid[int(new_y), int(new_x)] > 0:
                    vehicle.x = new_x
                    vehicle.y = new_y
                else:
                    # Yoldan çıktı, yön değiştir
                    vehicle.vx = -vehicle.vx * 0.5
                    vehicle.vy = -vehicle.vy * 0.5
            else:
                # Harita dışına çıktı, kaldır
                vehicles_to_remove.append(i)
        
        # Harita dışına çıkan araçları kaldır
        for i in reversed(vehicles_to_remove):
            self.moving_vehicles.pop(i)
    
    def _update_traffic_density_grid(self):
        """Trafik yoğunluğu matrisini güncelle"""
        self.traffic_grid.fill(0)
        
        for vehicle in self.moving_vehicles:
            x, y = int(vehicle.x), int(vehicle.y)
            if 0 <= x < self.width and 0 <= y < self.height:
                # Araç etrafında yoğunluk artışı
                for dy in range(-2, 3):
                    for dx in range(-2, 3):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            distance = np.sqrt(dx*dx + dy*dy)
                            if distance <= 2:
                                weight = 1.0 - distance / 2.0
                                self.traffic_grid[ny, nx] += weight
    
    def get_dynamic_cost(self, x: int, y: int) -> float:
        """Dinamik maliyet hesapla (trafik, ışık durumu vb.)"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return float('inf')
        
        # Bina kontrolü
        if self.building_grid[y, x] == 1:
            return float('inf')
        
        # Yol kontrolü
        if self.road_grid[y, x] == 0:
            return float('inf')
        
        # Temel maliyet (yol tipine göre)
        base_cost = {
            RoadType.HIGHWAY.value: 1.0,
            RoadType.MAIN_STREET.value: 1.2,
            RoadType.STREET.value: 1.5,
            RoadType.NARROW_STREET.value: 2.0,
            RoadType.PARKING_LOT.value: 3.0,
            RoadType.INTERSECTION.value: 2.5,
            RoadType.ROUNDABOUT.value: 2.0
        }.get(self.road_grid[y, x], 2.0)
        
        # Trafik yoğunluğu maliyeti
        traffic_cost = 1.0 + self.traffic_grid[y, x] * 2.0
        
        # Trafik ışığı maliyeti
        light_cost = self._get_traffic_light_cost(x, y)
        
        # Hız limiti maliyeti (düşük hız = yüksek maliyet)
        speed_factor = 50.0 / max(self.speed_limit_grid[y, x], 10.0)
        
        return base_cost * traffic_cost * light_cost * speed_factor
    
    def _get_traffic_light_cost(self, x: int, y: int) -> float:
        """Trafik ışığı maliyeti"""
        for light in self.traffic_lights:
            distance = abs(light.x - x) + abs(light.y - y)
            if distance <= 3:  # Işığa yakın
                if light.state == "red":
                    return 5.0  # Kırmızı ışık büyük maliyet
                elif light.state == "yellow":
                    return 2.0  # Sarı ışık orta maliyet
        return 1.0  # Normal
    
    def is_road(self, x: int, y: int) -> bool:
        """Yol mu kontrol et"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        return self.road_grid[y, x] > 0 and self.building_grid[y, x] == 0
    
    def get_road_info(self, x: int, y: int) -> Dict:
        """Yol bilgisi al"""
        if not self.is_road(x, y):
            return {}
        
        return {
            'type': RoadType(self.road_grid[y, x]).name,
            'speed_limit': self.speed_limit_grid[y, x],
            'traffic_density': self.traffic_grid[y, x],
            'cost': self.get_dynamic_cost(x, y)
        }
