import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.dstar.dstar_lite import DStarLite
from src.environment.grid_map import GridMap
from src.visualization.plotter import PathPlotter
from src.vehicle.vehicle_model import AutonomousVehicle
import numpy as np

def quick_demo():
    """Hızlı demo"""
    print("🚀 D* Lite Hızlı Demo")
    print("=" * 25)
    
    # Basit harita
    grid_map = GridMap(30, 25)
    grid_map.add_obstacle(10, 8, 15, 12)
    grid_map.add_obstacle(5, 15, 8, 20)
    grid_map.add_circular_obstacle(20, 18, 3)
    
    start = (2, 2)
    goal = (27, 22)
    
    print(f"Başlangıç: {start}")
    print(f"Hedef: {goal}")
    
    # Yol planla
    planner = DStarLite(grid_map)
    path = planner.plan_path(start, goal)
    
    if path:
        print(f"✅ Yol bulundu: {len(path)} adım")
        
        # Görselleştir
        plotter = PathPlotter()
        fig = plotter.plot_path(grid_map, path, start, goal, "D* Lite Hızlı Demo")
        plotter.save('quick_demo.png')
        
        print("📊 Görsel 'quick_demo.png' dosyasına kaydedildi")
        
        # Basit araç simülasyonu
        print("\n🚗 Basit araç simülasyonu...")
        vehicle = AutonomousVehicle(max_speed=5.0)
        vehicle.set_position(start[0], start[1])
        
        trajectory = vehicle.follow_path(path, dt=0.2, target_speed=3.0)
        
        if trajectory:
            print(f"✅ Araç simülasyonu tamamlandı: {len(trajectory)} adım")
            
            # Araç trajektorisi görselleştirme
            plotter = PathPlotter()
            fig = plotter.plot_vehicle_trajectory(grid_map, path, trajectory, 
                                                "Araç Trajektorisi - Hızlı Demo")
            plotter.save('quick_demo_vehicle.png')
            print("🚗 Araç simülasyonu 'quick_demo_vehicle.png' dosyasına kaydedildi")
        
        print("\n🎉 Hızlı demo tamamlandı!")
        print("Detaylı örnekler için examples/ klasöründeki diğer dosyalara bakın.")
        
    else:
        print("❌ Yol bulunamadı!")

if __name__ == "__main__":
    quick_demo()