import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.dstar.dstar_lite import DStarLite
from src.environment.grid_map import GridMap
from src.visualization.plotter import PathPlotter
import time

def main():
    print("D* Lite Temel Yol Bulma Örneği")
    print("=" * 40)
    
    # Grid haritası oluştur
    print("Grid haritası oluşturuluyor...")
    grid_map = GridMap(50, 50)
    
    # Engeller ekle
    grid_map.add_obstacle(10, 10, 15, 15)  # Kare engel
    grid_map.add_obstacle(20, 5, 25, 25)   # Büyük engel
    grid_map.add_circular_obstacle(35, 35, 5)  # Dairesel engel
    grid_map.add_random_obstacles(0.1)      # %10 rastgele engel
    
    # Başlangıç ve hedef noktalar
    start = (5, 5)
    goal = (45, 45)
    
    print(f"Başlangıç: {start}")
    print(f"Hedef: {goal}")
    
    # D* Lite planlayıcısı oluştur
    print("\nD* Lite planlayıcısı oluşturuluyor...")
    planner = DStarLite(grid_map, heuristic_weight=1.2)
    
    # Yol planla
    print("Yol planlanıyor...")
    start_time = time.time()
    path = planner.plan_path(start, goal)
    planning_time = time.time() - start_time
    
    if path:
        print(f"\n✅ Yol bulundu!")
        print(f"Yol uzunluğu: {len(path)} adım")
        print(f"Planlama süresi: {planning_time:.3f} saniye")
        print(f"Genişletilen düğüm sayısı: {planner.stats['nodes_expanded']}")
        
        # İlk birkaç ve son birkaç noktayı göster
        print(f"\nYolun başlangıcı: {path[:3]}")
        print(f"Yolun sonu: {path[-3:]}")
    else:
        print("\n❌ Yol bulunamadı!")
        return
    
    # Dinamik engel testi
    print(f"\n" + "="*40)
    print("Dinamik Engel Testi")
    print("="*40)
    
    # Yolun ortasına engel ekle
    mid_point = path[len(path)//2]
    print(f"Yolun ortasına engel ekleniyor: {mid_point}")
    
    grid_map.add_obstacle(mid_point[0]-2, mid_point[1]-2, 
                         mid_point[0]+2, mid_point[1]+2)
    
    # Değişiklikleri planleyiciye bildir
    changed_cells = []
    for x in range(mid_point[0]-2, mid_point[0]+3):
        for y in range(mid_point[1]-2, mid_point[1]+3):
            changed_cells.append((x, y, True))
    
    planner.update_obstacles(changed_cells)
    
    # Yeniden planla
    print("Yeniden planlama...")
    start_time = time.time()
    new_path = planner.replan_path()
    replanning_time = time.time() - start_time
    
    if new_path:
        print(f"✅ Yeni yol bulundu!")
        print(f"Yeni yol uzunluğu: {len(new_path)} adım")
        print(f"Yeniden planlama süresi: {replanning_time:.3f} saniye")
        print(f"Toplam genişletilen düğüm: {planner.stats['nodes_expanded']}")
        
        # Performance karşılaştırması
        print(f"\nPerformans Karşılaştırması:")
        print(f"İlk planlama: {planning_time:.3f}s")
        print(f"Yeniden planlama: {replanning_time:.3f}s")
        print(f"Hızlanma oranı: {planning_time/replanning_time:.1f}x")
    else:
        print("❌ Yeni yol bulunamadı!")
        new_path = path
    
    # Görselleştirme
    print(f"\n" + "="*40)
    print("Görselleştirme")
    print("="*40)
    
    plotter = PathPlotter()
    
    # Orijinal yol
    fig1 = plotter.plot_path(grid_map, path, start, goal, 
                            "D* Lite - İlk Yol")
    plotter.save("original_path.png")
    
    # Yeni yol
    plotter = PathPlotter()  # Yeni plotter
    fig2 = plotter.plot_path(grid_map, new_path, start, goal, 
                            "D* Lite - Yeniden Planlanmış Yol")
    plotter.save("replanned_path.png")
    
    print("Görselleştirmeler 'original_path.png' ve 'replanned_path.png' dosyalarına kaydedildi.")
    print("\nÖrnek tamamlandı! 🎉")

if __name__ == "__main__":
    main()