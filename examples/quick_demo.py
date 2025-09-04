import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.dstar.dstar_lite import DStarLite
from src.environment.grid_map import GridMap
from src.visualization.plotter import PathPlotter
from src.vehicle.vehicle_model import AutonomousVehicle
import numpy as np
import matplotlib.pyplot as plt

def quick_demo():
    """Hızlı demo"""
    print("D* Lite Hızlı Demo")
    print("=" * 25)
    
    # Basit harita
    grid_map = GridMap(30, 25)
    grid_map.add_obstacle(10, 8, 15, 12)     # Ana bina
    grid_map.add_obstacle(5, 15, 8, 20)      # Küçük bina
    grid_map.add_circular_obstacle(20, 18, 3) # Dairesel engel (park/meydan)
    
    # Zor arazi ekle (inşaat alanı gibi)
    grid_map.add_rough_terrain_area(22, 8, 28, 13, cost=2.0)
    
    start = (2, 2)
    goal = (27, 22)
    
    print(f"Başlangıç: {start}")
    print(f"Hedef: {goal}")
    print(f"Grid boyutu: {grid_map.width} x {grid_map.height}")
    
    # Yol planla
    print(f"\nD* Lite ile yol planlaması...")
    import time
    start_time = time.time()
    
    planner = DStarLite(grid_map, heuristic_weight=1.0)
    path = planner.plan_path(start, goal)
    
    planning_time = time.time() - start_time
    
    if path:
        print(f"Yol bulundu")
        print(f"Yol uzunluğu: {len(path)} adım")
        print(f"Planlama süresi: {planning_time:.4f} saniye")
        print(f"Genişletilen düğüm: {planner.stats['nodes_expanded']}")
        
        # Ana görselleştirme
        plotter = PathPlotter(figsize=(12, 10))
        fig = plotter.plot_path(grid_map, path, start, goal, 
                               "D* Lite Hızlı Demo - Yol Planlaması")
        plotter.save(os.path.join(os.path.dirname(__file__), 'quick_demo.png'), dpi=300)
        
        print(f"Ana görsel 'quick_demo.png' dosyasına kaydedildi")
        
        # Araç simülasyonu
        print(f"\nOtonom araç simülasyonu başlatılıyor...")
        vehicle = AutonomousVehicle(
            wheelbase=2.5,
            max_speed=5.0,
            max_steering_angle=np.pi/6,  # 30 derece
            max_acceleration=2.0
        )
        
        # Araç başlangıç pozisyonu (küçük offset ile gerçekçi başlangıç)
        vehicle.set_position(start[0] + 0.5, start[1] + 0.5, np.pi/4)
        
        # Simülasyon parametreleri
        dt = 0.2  # 5 Hz kontrol frekansı
        target_speed = 3.0  # m/s (yaklaşık 11 km/h - şehir içi hız)
        
        start_time = time.time()
        trajectory = vehicle.follow_path(path, dt=dt, target_speed=target_speed)
        simulation_time = time.time() - start_time
        
        if trajectory and len(trajectory) > 0:
            total_sim_time = len(trajectory) * dt
            
            # Gerçek mesafe hesaplama
            actual_distance = 0
            for i in range(1, len(trajectory)):
                dx = trajectory[i].x - trajectory[i-1].x
                dy = trajectory[i].y - trajectory[i-1].y
                actual_distance += np.sqrt(dx*dx + dy*dy)
            
            avg_speed = actual_distance / total_sim_time if total_sim_time > 0 else 0
            
            print(f"Araç simülasyonu tamamlandı")
            print(f"Simülasyon hesaplama süresi: {simulation_time:.3f} saniye")
            print(f"Toplam simüle edilen zaman: {total_sim_time:.1f} saniye")
            print(f"Kat edilen mesafe: {actual_distance:.1f} metre")
            print(f"Ortalama hız: {avg_speed:.1f} m/s ({avg_speed*3.6:.1f} km/h)")
            print(f"Simülasyon adım sayısı: {len(trajectory)}")
            
            # Araç trajektorisi görselleştirme
            plotter_vehicle = PathPlotter(figsize=(14, 10))
            fig_vehicle = plotter_vehicle.plot_vehicle_trajectory(
                grid_map, path, trajectory, 
                "Otonom Araç Simülasyonu - Hızlı Demo"
            )
            
            # Ek bilgiler ekle
            ax = plotter_vehicle.ax
            
            # Performans bilgilerini grafiğe ekle
            info_text = f"""Performans Metrikleri:
• Planlama: {planning_time:.3f}s
• Yol: {len(path)} adım
• Simülasyon: {total_sim_time:.1f}s
• Hız: {avg_speed:.1f} m/s
• Mesafe: {actual_distance:.1f}m"""
            
            ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
                   fontsize=10, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            
            plotter_vehicle.save(os.path.join(os.path.dirname(__file__), 'quick_demo_vehicle.png'), dpi=300)
            print(f"Araç simülasyonu 'quick_demo_vehicle.png' dosyasına kaydedildi")
            
            # Basit kontrol profili
            speeds = [state.v for state in trajectory]
            steering_angles = [np.degrees(state.steering) for state in trajectory]
            time_points = [i * dt for i in range(len(trajectory))]
            
            plt.figure(figsize=(12, 8))
            
            plt.subplot(2, 1, 1)
            plt.plot(time_points, speeds, 'b-', linewidth=2, label='Gerçek Hız')
            plt.axhline(y=target_speed, color='r', linestyle='--', alpha=0.7, label=f'Hedef Hız: {target_speed} m/s')
            plt.xlabel('Zaman (saniye)')
            plt.ylabel('Hız (m/s)')
            plt.title('Araç Hız Profili - Hızlı Demo')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            plt.subplot(2, 1, 2)
            plt.plot(time_points, steering_angles, 'g-', linewidth=2, label='Direksiyon Açısı')
            max_steer_deg = np.degrees(vehicle.max_steering_angle)
            plt.axhline(y=max_steer_deg, color='r', linestyle='--', alpha=0.5, label=f'Max: ±{max_steer_deg:.0f}°')
            plt.axhline(y=-max_steer_deg, color='r', linestyle='--', alpha=0.5)
            plt.xlabel('Zaman (saniye)')
            plt.ylabel('Direksiyon Açısı (derece)')
            plt.title('Araç Direksiyon Profili - Hızlı Demo')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(os.path.join(os.path.dirname(__file__), 'quick_demo_control.png'), dpi=300, bbox_inches='tight')
            print(f"Kontrol profili 'quick_demo_control.png' dosyasına kaydedildi")
            
        else:
            print("Araç simülasyonu başarısız")
            return
        
        # Özet bilgiler
        print(f"\n" + "="*50)
        print(f"HIZLI DEMO ÖZETİ")
        print(f"="*50)
        print(f"Algoritma: D* Lite")
        print(f"Rota: {start} -> {goal}")
        print(f"Planlama Performansı: {planning_time:.4f} saniye")
        print(f"Yol Kalitesi: {len(path)} adım")
        print(f"Araç Performansı: {avg_speed:.1f} m/s ortalama")
        print(f"Oluşturulan Dosyalar:")
        print(f"   • quick_demo.png (yol planlaması)")
        print(f"   • quick_demo_vehicle.png (araç simülasyonu)")
        print(f"   • quick_demo_control.png (kontrol profili)")
        
        print(f"\nHızlı demo başarıyla tamamlandı")
        print(f"Daha detaylı örnekler için:")
        print(f"   • python examples/basic_pathfinding.py")
        print(f"   • python examples/dynamic_obstacles.py")
        print(f"   • python examples/vehicle_simulation.py")
        print(f"   • python examples/benchmark_comparison.py")
        
        # README için örnek performans metrikleri
        print(f"\n" + "="*50)
        print(f"README İÇİN PERFORMANS METRİKLERİ")
        print(f"="*50)
        print(f"| Metrik | Değer |")
        print(f"|--------|--------|")
        print(f"| **Planlama Süresi** | ~{planning_time:.3f}s |")
        print(f"| **Yol Uzunluğu** | {len(path)} adım |")
        print(f"| **Araç Simülasyon Süresi** | ~{total_sim_time:.1f}s |")
        print(f"| **Ortalama Hız** | {avg_speed:.1f} m/s |")
        print(f"| **Maksimum Direksiyon Açısı** | ±{max_steer_deg:.0f}° |")
        
    else:
        print("Yol bulunamadı. Harita konfigürasyonunu kontrol edin.")

if __name__ == "__main__":
    quick_demo()