import numpy as np
import math
from typing import List, Tuple
from dataclasses import dataclass

@dataclass
class VehicleState:
    """Araç durumu"""
    x: float = 0.0          # X pozisyonu
    y: float = 0.0          # Y pozisyonu  
    theta: float = 0.0      # Yönelim (radyan)
    v: float = 0.0          # Hız (m/s)
    steering: float = 0.0   # Direksiyon açısı (radyan)

class AutonomousVehicle:
    """Otonom araç modeli"""
    
    def __init__(self, wheelbase: float = 2.5, max_speed: float = 10.0,
                 max_steering_angle: float = math.pi/4, max_acceleration: float = 3.0):
        self.wheelbase = wheelbase  # Dingil mesafesi
        self.max_speed = max_speed
        self.max_steering_angle = max_steering_angle
        self.max_acceleration = max_acceleration
        
        self.state = VehicleState()
        self.path_index = 0
        self.trajectory = []
        
        # Kontrol parametreleri
        self.kp_steering = 2.0  # Direksiyon P kontrolcüsü
        self.kp_speed = 1.0     # Hız P kontrolcüsü
        self.lookahead_distance = 5.0  # İleriye bakış mesafesi
    
    def bicycle_model(self, dt: float, acceleration: float, steering_angle: float):
        """Bisiklet modeli kinematik güncellemesi"""
        # Girdi sınırları
        steering_angle = np.clip(steering_angle, -self.max_steering_angle, self.max_steering_angle)
        
        # Hız güncellemesi
        new_velocity = self.state.v + acceleration * dt
        new_velocity = np.clip(new_velocity, 0, self.max_speed)
        
        # Pozisyon ve yönelim güncellemesi
        beta = math.atan(0.5 * math.tan(steering_angle))  # Kayma açısı
        
        new_x = self.state.x + new_velocity * math.cos(self.state.theta + beta) * dt
        new_y = self.state.y + new_velocity * math.sin(self.state.theta + beta) * dt
        new_theta = self.state.theta + (new_velocity / self.wheelbase) * math.sin(beta) * dt
        
        # Theta'yı [-π, π] aralığında tut
        new_theta = math.atan2(math.sin(new_theta), math.cos(new_theta))
        
        # Durumu güncelle
        self.state.x = new_x
        self.state.y = new_y
        self.state.theta = new_theta
        self.state.v = new_velocity
        self.state.steering = steering_angle
        
        # Trajektoriyi kaydet
        self.trajectory.append((new_x, new_y, new_theta, new_velocity))
    
    def pure_pursuit_control(self, path: List[Tuple[int, int]], target_speed: float = 5.0) -> Tuple[float, float]:
        """Pure Pursuit kontrol algoritması"""
        if not path or self.path_index >= len(path):
            return 0.0, 0.0
        
        # İleriye bakış noktasını bul
        lookahead_point = self.find_lookahead_point(path)
        if lookahead_point is None:
            return 0.0, 0.0
        
        # Direksiyon kontrolü
        dx = lookahead_point[0] - self.state.x
        dy = lookahead_point[1] - self.state.y
        target_angle = math.atan2(dy, dx)
        angle_error = target_angle - self.state.theta
        
        # Açı farkını [-π, π] aralığında normalize et
        angle_error = math.atan2(math.sin(angle_error), math.cos(angle_error))
        
        # Pure pursuit direksiyon açısı
        distance_to_target = math.sqrt(dx*dx + dy*dy)
        steering_angle = math.atan(2 * self.wheelbase * math.sin(angle_error) / distance_to_target)
        
        # Hız kontrolü
        speed_error = target_speed - self.state.v
        acceleration = self.kp_speed * speed_error
        acceleration = np.clip(acceleration, -self.max_acceleration, self.max_acceleration)
        
        return acceleration, steering_angle
    
    def find_lookahead_point(self, path: List[Tuple[int, int]]) -> Tuple[float, float]:
        """İleriye bakış noktasını bul"""
        min_distance = float('inf')
        closest_index = self.path_index
        
        # En yakın nokta indeksini bul
        for i in range(self.path_index, len(path)):
            point = path[i]
            distance = math.sqrt((point[0] - self.state.x)**2 + (point[1] - self.state.y)**2)
            if distance < min_distance:
                min_distance = distance
                closest_index = i
        
        self.path_index = closest_index
        
        # İleriye bakış mesafesindeki noktayı bul
        for i in range(self.path_index, len(path)):
            point = path[i]
            distance = math.sqrt((point[0] - self.state.x)**2 + (point[1] - self.state.y)**2)
            
            if distance >= self.lookahead_distance:
                return (float(point[0]), float(point[1]))
        
        # Son nokta
        if path:
            return (float(path[-1][0]), float(path[-1][1]))
        
        return None
    
    def follow_path(self, path: List[Tuple[int, int]], dt: float = 0.1, 
                   target_speed: float = 5.0) -> List[VehicleState]:
        """Yolu takip et"""
        trajectory = []
        self.path_index = 0
        
        while self.path_index < len(path) - 1:
            # Kontrol sinyallerini hesapla
            acceleration, steering = self.pure_pursuit_control(path, target_speed)
            
            # Araç modelini güncelle
            self.bicycle_model(dt, acceleration, steering)
            
            # Durumu kaydet
            trajectory.append(VehicleState(
                self.state.x, self.state.y, self.state.theta, 
                self.state.v, self.state.steering
            ))
            
            # Hedefe ulaştı mı kontrol et
            goal = path[-1]
            distance_to_goal = math.sqrt((goal[0] - self.state.x)**2 + (goal[1] - self.state.y)**2)
            if distance_to_goal < 1.0:  # 1 metre tolerans
                break
        
        return trajectory
    
    def set_position(self, x: float, y: float, theta: float = 0.0):
        """Araç pozisyonunu ayarla"""
        self.state.x = x
        self.state.y = y
        self.state.theta = theta
        self.state.v = 0.0
        self.state.steering = 0.0
    
    def get_vehicle_corners(self) -> List[Tuple[float, float]]:
        """Araç köşe noktalarını hesapla (görselleştirme için)"""
        # Araç boyutları (metre)
        length = 4.0
        width = 2.0
        
        # Araç merkezine göre köşe noktaları
        corners_local = [
            (-length/2, -width/2), (length/2, -width/2),
            (length/2, width/2), (-length/2, width/2)
        ]
        
        # Global koordinatlara dönüştür
        corners_global = []
        cos_theta = math.cos(self.state.theta)
        sin_theta = math.sin(self.state.theta)
        
        for x_local, y_local in corners_local:
            x_global = self.state.x + x_local * cos_theta - y_local * sin_theta
            y_global = self.state.y + x_local * sin_theta + y_local * cos_theta
            corners_global.append((x_global, y_global))
        
        return corners_global
