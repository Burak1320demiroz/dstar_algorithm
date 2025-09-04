import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.dstar.dstar_lite import DStarLite
from src.environment.grid_map import GridMap
from src.vehicle.vehicle_model import AutonomousVehicle
from src.visualization.plotter import PathPlotter
import numpy as np
import matplotlib.pyplot as plt

def vehicle_simulation_demo():
    """Araç simülasyonu demonstrasyonu"""
    print("Otonom Araç Simülasyonu ile D* Lite")
    print("=" * 40)
    
    # Grid harita oluştur (daha büyük, metre cinsinden)
    # 1 grid = 1 metre olarak kabul ediyoruz
    grid_map = GridMap(100, 80)
    
    # Şehir benzeri engel yapısı oluştur
    print("Şehir haritası oluşturuluyor...")
    
    # Binalar
    grid_map.add_obstacle(20, 20, 30, 40)   # Bina 1
    grid_map.add_obstacle(40, 15, 55, 25)   # Bina 2
    grid_map.add_obstacle(60, 35, 75, 50)   # Bina 3
    grid_map.add_obstacle(15, 55, 35, 70)   # Bina 4
    
    # Zor arazi alanları (park, inşaat vs.)
    grid_map.add_rough_terrain_area(45, 45, 58, 58, cost=2.5)  # Park alanı
    grid_map.add_rough_terrain_area(80, 10, 90, 30, cost=3.0)  # İnşaat alanı
    
    # Rastgele küçük engeller
    grid_map.add_random_obstacles(0.05)
    
    # Başlangıç ve hedef (metre cinsinden)
    start = (10, 10)
    goal = (85, 70)
    
    print(f"Başlangıç pozisyonu: {start} (metre)")
    print(f"Hedef pozisyonu: {goal} (metre)")
    
    # Yol planlaması
    print("\nYol planlaması yapılıyor...")
    planner = DStarLite(grid_map, heuristic_weight=1.0)
    path = planner.plan_path(start, goal)
    
    if not path:
        print("Yol bulunamadı")
        return
    
    print(f"Yol bulundu: {len(path)} nokta")
    print(f"Yaklaşık yol uzunluğu: {len(path):.1f} metre")
    
    # Araç modeli oluştur
    print("\nAraç modeli oluşturuluyor...")
    vehicle = AutonomousVehicle(
        wheelbase=2.8,           # metre (tipik sedan)
        max_speed=8.0,           # m/s (yaklaşık 29 km/h)
        max_steering_angle=np.pi/6,  # 30 derece
        max_acceleration=2.0      # m/s²
    )
    
    # Araç başlangıç pozisyonu
    vehicle.set_position(start[0], start[1], np.pi/4)  # 45 derece başlangıç açısı
    
    print(f"Araç özellikleri:")
    print(f"  - Dingil mesafesi: {vehicle.wheelbase} m")
    print(f"  - Maksimum hız: {vehicle.max_speed} m/s ({vehicle.max_speed*3.6:.1f} km/h)")
    print(f"  - Maksimum direksiyon açısı: {np.degrees(vehicle.max_steering_angle):.1f}°")
    print(f"  - Maksimum ivme: {vehicle.max_acceleration} m/s²")
    
    # Araç simülasyonu
    print(f"\nAraç simülasyonu başlatılıyor...")
    target_speed = 6.0  # m/s
    dt = 0.2  # saniye (5 Hz kontrol frekansı)
    
    trajectory = vehicle.follow_path(path, dt=dt, target_speed=target_speed)
    
    if trajectory:
        total_time = len(trajectory) * dt
        actual_distance = 0
        
        # Gerçek kat edilen mesafeyi hesapla
        for i in range(1, len(trajectory)):
            dx = trajectory[i].x - trajectory[i-1].x
            dy = trajectory[i].y - trajectory[i-1].y
            actual_distance += np.sqrt(dx*dx + dy*dy)
        
        avg_speed = actual_distance / total_time if total_time > 0 else 0
        
        print(f"Simülasyon tamamlandı")
        print(f"Toplam süre: {total_time:.1f} saniye")
        print(f"Kat edilen mesafe: {actual_distance:.1f} metre")
        print(f"Ortalama hız: {avg_speed:.1f} m/s ({avg_speed*3.6:.1f} km/h)")
        print(f"Simülasyon adım sayısı: {len(trajectory)}")
    else:
        print("❌ Simülasyon başarısız!")
        return
    
    # Dinamik engel senaryosu
    print(f"\n" + "="*40)
    print("Dinamik Engel Senaryosu")
    print("="*40)
    
    # Araç trajektorisinin ortasına yakın bir yerde engel oluştur
    if len(trajectory) > 20:
        mid_state = trajectory[len(trajectory)//3]  # Trajektorinin 1/3'ünde
        obstacle_x = int(mid_state.x)
        obstacle_y = int(mid_state.y)
        
        print(f"Engel ekleniyor: ({obstacle_x}, {obstacle_y}) civarında")
        
        # Engeli haritaya ekle
        grid_map.add_obstacle(obstacle_x-3, obstacle_y-3, obstacle_x+3, obstacle_y+3)
        
        # Planleyiciye bildir
        changed_cells = []
        for x in range(obstacle_x-3, obstacle_x+4):
            for y in range(obstacle_y-3, obstacle_y+4):
                if grid_map.is_valid_cell(x, y):
                    changed_cells.append((x, y, True))
        
        planner.update_obstacles(changed_cells)
        
        # Yeni başlangıç noktası (araç şu anki pozisyonundan)
        new_start = (int(mid_state.x), int(mid_state.y))
        
        # Yeniden planla
        print("Yeniden planlama yapılıyor...")
        new_path = planner.replan_path(new_start)
        
        if new_path:
            print(f"Yeni yol bulundu: {len(new_path)} nokta")
            
            # Yeni araç oluştur (şu anki durumdan devam etmek için)
            new_vehicle = AutonomousVehicle(
                wheelbase=vehicle.wheelbase,
                max_speed=vehicle.max_speed,
                max_steering_angle=vehicle.max_steering_angle,
                max_acceleration=vehicle.max_acceleration
            )
            
            new_vehicle.set_position(mid_state.x, mid_state.y, mid_state.theta)
            
            # Yeni yolu takip et
            new_trajectory = new_vehicle.follow_path(new_path, dt=dt, target_speed=target_speed)
            
            print(f"Yeni trajektori oluşturuldu: {len(new_trajectory)} adım")
        else:
            print("Yeni yol bulunamadı")
            new_path = []
            new_trajectory = []
    else:
        new_path = []
        new_trajectory = []
    
    # Görselleştirme
    print(f"\n" + "="*40)
    print("Görselleştirme")
    print("="*40)
    
    # Ana görselleştirme
    plotter = PathPlotter(figsize=(15, 12))
    
    if new_trajectory:
        # Dinamik engel sonrası karşılaştırma
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
        
        # 1. Orijinal plan
        plotter.fig, plotter.ax = fig, ax1
        plotter.ax.set_xlim(-0.5, grid_map.width - 0.5)
        plotter.ax.set_ylim(-0.5, grid_map.height - 0.5)
        plotter.ax.set_aspect('equal')
        plotter.ax.set_title('Orijinal Yol Planı', fontsize=14)
        
        # Orijinal grid (engel eklenmeden önce)
        original_grid = GridMap(grid_map.width, grid_map.height)
        original_grid.add_obstacle(20, 20, 30, 40)
        original_grid.add_obstacle(40, 15, 55, 25)
        original_grid.add_obstacle(60, 35, 75, 50)
        original_grid.add_obstacle(15, 55, 35, 70)
        original_grid.add_rough_terrain_area(45, 45, 58, 58, cost=2.5)
        original_grid.add_rough_terrain_area(80, 10, 90, 30, cost=3.0)
        
        plotter.plot_grid(original_grid)
        path_x = [p[0] for p in path]
        path_y = [p[1] for p in path]
        ax1.plot(path_x, path_y, 'b--', linewidth=2, alpha=0.7, label='Planlanan Yol')
        ax1.plot(start[0], start[1], 'go', markersize=10, label='Başlangıç')
        ax1.plot(goal[0], goal[1], 'ro', markersize=10, label='Hedef')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Orijinal araç trajektorisi
        plotter.fig, plotter.ax = fig, ax2
        plotter.ax.set_xlim(-0.5, grid_map.width - 0.5)
        plotter.ax.set_ylim(-0.5, grid_map.height - 0.5)
        plotter.ax.set_aspect('equal')
        plotter.ax.set_title('Orijinal Araç Trajektorisi', fontsize=14)
        plotter.plot_grid(original_grid)
        
        # Araç trajektorisi
        traj_x = [state.x for state in trajectory]
        traj_y = [state.y for state in trajectory]
        ax2.plot(path_x, path_y, 'b--', linewidth=1, alpha=0.5, label='Planlanan Yol')
        ax2.plot(traj_x, traj_y, 'r-', linewidth=2, label='Araç Trajektorisi')
        ax2.plot(start[0], start[1], 'go', markersize=10, label='Başlangıç')
        ax2.plot(goal[0], goal[1], 'ro', markersize=10, label='Hedef')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Dinamik engel sonrası yol
        plotter.fig, plotter.ax = fig, ax3
        plotter.ax.set_xlim(-0.5, grid_map.width - 0.5)
        plotter.ax.set_ylim(-0.5, grid_map.height - 0.5)
        plotter.ax.set_aspect('equal')
        plotter.ax.set_title('Dinamik Engel Sonrası Yeniden Planlama', fontsize=14)
        plotter.plot_grid(grid_map)  # Yeni engel ile
        
        new_path_x = [p[0] for p in new_path]
        new_path_y = [p[1] for p in new_path]
        ax3.plot(new_path_x, new_path_y, 'g-', linewidth=2, label='Yeni Yol')
        ax3.plot(new_start[0], new_start[1], 'yo', markersize=10, label='Yeni Başlangıç')
        ax3.plot(goal[0], goal[1], 'ro', markersize=10, label='Hedef')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Tam trajektori
        plotter.fig, plotter.ax = fig, ax4
        plotter.ax.set_xlim(-0.5, grid_map.width - 0.5)
        plotter.ax.set_ylim(-0.5, grid_map.height - 0.5)
        plotter.ax.set_aspect('equal')
        plotter.ax.set_title('Tam Araç Trajektorisi', fontsize=14)
        plotter.plot_grid(grid_map)
        
        # Her iki trajektoriyi de göster
        ax4.plot(traj_x, traj_y, 'r-', linewidth=2, label='İlk Trajektori')
        if new_trajectory:
            new_traj_x = [state.x for state in new_trajectory]
            new_traj_y = [state.y for state in new_trajectory]
            ax4.plot(new_traj_x, new_traj_y, 'g-', linewidth=2, label='Yeni Trajektori')
        
        ax4.plot(start[0], start[1], 'go', markersize=10, label='İlk Başlangıç')
        ax4.plot(new_start[0], new_start[1], 'yo', markersize=10, label='Yeniden Başlangıç')
        ax4.plot(goal[0], goal[1], 'ro', markersize=10, label='Hedef')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        import os
        plt.savefig(os.path.join(os.path.dirname(__file__), 'vehicle_simulation_complete.png'), dpi=300, bbox_inches='tight')
        print("Tam simülasyon görseli 'vehicle_simulation_complete.png' dosyasına kaydedildi.")
        
    else:
        # Basit görselleştirme
        fig = plotter.plot_vehicle_trajectory(grid_map, path, trajectory, 
                                            "Otonom Araç Simülasyonu")
        import os
        plotter.save(os.path.join(os.path.dirname(__file__), 'vehicle_simulation.png'))
        print("Simülasyon görseli 'vehicle_simulation.png' dosyasına kaydedildi.")
    
    # Hız profili
    if trajectory:
        plt.figure(figsize=(12, 8))
        
        time_points = [i * dt for i in range(len(trajectory))]
        speeds = [state.v for state in trajectory]
        steering_angles = [np.degrees(state.steering) for state in trajectory]
        
        plt.subplot(2, 1, 1)
        plt.plot(time_points, speeds, 'b-', linewidth=2)
        plt.axhline(y=target_speed, color='r', linestyle='--', label=f'Hedef Hız: {target_speed} m/s')
        plt.xlabel('Zaman (s)')
        plt.ylabel('Hız (m/s)')
        plt.title('Araç Hız Profili')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        plt.subplot(2, 1, 2)
        plt.plot(time_points, steering_angles, 'g-', linewidth=2)
        plt.axhline(y=np.degrees(vehicle.max_steering_angle), color='r', linestyle='--', alpha=0.7, label='Max Direksiyon')
        plt.axhline(y=-np.degrees(vehicle.max_steering_angle), color='r', linestyle='--', alpha=0.7)
        plt.xlabel('Zaman (s)')
        plt.ylabel('Direksiyon Açısı (derece)')
        plt.title('Araç Direksiyon Profili')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        plt.tight_layout()
        import os
        plt.savefig(os.path.join(os.path.dirname(__file__), 'vehicle_control_profile.png'), dpi=300, bbox_inches='tight')
        print("Kontrol profili 'vehicle_control_profile.png' dosyasına kaydedildi.")
    
    print("\nOtonom araç simülasyonu tamamlandı")

if __name__ == "__main__":
    vehicle_simulation_demo()