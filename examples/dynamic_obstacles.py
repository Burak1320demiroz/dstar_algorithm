import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.dstar.dstar_lite import DStarLite
from src.environment.grid_map import GridMap
from src.visualization.plotter import PathPlotter
import time
import matplotlib.pyplot as plt

def simulate_moving_obstacle():
    """Hareketli engel simülasyonu"""
    print("Dinamik Engeller ile D* Lite Örneği")
    print("=" * 45)
    
    # Büyük grid oluştur
    grid_map = GridMap(80, 60)
    
    # Statik engeller ekle
    grid_map.add_obstacle(20, 20, 25, 40)  # Dikey duvar
    grid_map.add_obstacle(40, 10, 60, 15)  # Yatay duvar
    grid_map.add_obstacle(15, 45, 35, 50)  # Blok
    grid_map.add_random_obstacles(0.05)     # %5 rastgele engel (daha ulaşılabilir)
    
    start = (5, 5)
    goal = (70, 50)

    # Başlangıç ve hedefe açık koridor oluştur (L-şekilli güvenli şerit)
    x1, y1 = start
    x2, y2 = goal
    x_min, x_max = min(x1, x2), max(x1, x2)
    y_min, y_max = min(y1, y2), max(y1, y2)
    # Yatay şerit
    grid_map.clear_area(x_min - 1, y1 - 2, x_max + 1, y1 + 2)
    # Dikey şerit
    grid_map.clear_area(x2 - 2, min(y1, y2) - 1, x2 + 2, max(y1, y2) + 1)
    
    print(f"Başlangıç: {start}, Hedef: {goal}")
    print(f"Grid boyutu: {grid_map.width}x{grid_map.height}")
    
    # D* Lite planlayıcısı
    planner = DStarLite(grid_map, heuristic_weight=1.1)
    
    # İlk yol planlaması
    print("\n1. İlk yol planlanıyor...")
    path = planner.plan_path(start, goal)
    
    if not path:
        print("İlk yol bulunamadı")
        return
    
    print(f"İlk yol bulundu: {len(path)} adım")
    
    # Hareketli engel simülasyonu
    obstacle_positions = [
        (30, 25, 35, 30),  # Engel pozisyon 1
        (35, 30, 40, 35),  # Engel pozisyon 2
        (40, 35, 45, 40),  # Engel pozisyon 3
        (45, 25, 50, 30),  # Engel pozisyon 4
        (50, 20, 55, 25),  # Engel pozisyon 5
    ]
    
    paths_history = [path.copy()]
    planning_times = []
    
    for i, (x1, y1, x2, y2) in enumerate(obstacle_positions, 1):
        print(f"\n{i+1}. Hareketli engel pozisyonu: ({x1},{y1}) - ({x2},{y2})")
        
        # Önceki engeli temizle (ilk iterasyon hariç)
        if i > 1:
            prev_x1, prev_y1, prev_x2, prev_y2 = obstacle_positions[i-2]
            grid_map.clear_area(prev_x1, prev_y1, prev_x2, prev_y2)
            
            # Temizlenen alanı planleyiciye bildir
            cleared_cells = []
            for x in range(prev_x1, prev_x2 + 1):
                for y in range(prev_y1, prev_y2 + 1):
                    if grid_map.is_valid_cell(x, y):
                        cleared_cells.append((x, y, False))
            planner.update_obstacles(cleared_cells)
        
        # Yeni engeli ekle
        grid_map.add_obstacle(x1, y1, x2, y2)
        
        # Yeni engeli planleyiciye bildir
        new_obstacle_cells = []
        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                if grid_map.is_valid_cell(x, y):
                    new_obstacle_cells.append((x, y, True))
        
        # Yeniden planla
        start_time = time.time()
        planner.update_obstacles(new_obstacle_cells)
        new_path = planner.replan_path()
        planning_time = time.time() - start_time
        
        planning_times.append(planning_time)
        
        if new_path:
            print(f"Yeni yol bulundu: {len(new_path)} adım")
            print(f"Yeniden planlama süresi: {planning_time:.4f} saniye")
            paths_history.append(new_path.copy())
        else:
            print("Yeni yol bulunamadı")
            break
    
    # İstatistikler
    print(f"\n" + "="*45)
    print("İSTATİSTİKLER")
    print("="*45)
    print(f"Toplam yeniden planlama: {len(planning_times)}")
    print(f"Ortalama yeniden planlama süresi: {sum(planning_times)/len(planning_times):.4f}s")
    print(f"En hızlı yeniden planlama: {min(planning_times):.4f}s")
    print(f"En yavaş yeniden planlama: {max(planning_times):.4f}s")
    print(f"Toplam genişletilen düğüm: {planner.stats['nodes_expanded']}")
    print(f"Yeniden planlama sayısı: {planner.stats['replanning_count']}")
    
    # Görselleştirme
    print(f"\nGörselleştirme oluşturuluyor...")
    
    # İlk ve son yolu karşılaştır
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
    
    # İlk yol
    plotter1 = PathPlotter()
    plotter1.fig, plotter1.ax = fig, ax1
    plotter1.ax.set_xlim(-0.5, grid_map.width - 0.5)
    plotter1.ax.set_ylim(-0.5, grid_map.height - 0.5)
    plotter1.ax.set_aspect('equal')
    plotter1.ax.set_title('İlk Planlanan Yol', fontsize=14)
    
    # Grid'i çiz (engelsiz)
    temp_grid = GridMap(grid_map.width, grid_map.height)
    temp_grid.add_obstacle(20, 20, 25, 40)
    temp_grid.add_obstacle(40, 10, 60, 15)
    temp_grid.add_obstacle(15, 45, 35, 50)
    plotter1.plot_grid(temp_grid)
    
    # İlk yolu çiz
    first_path = paths_history[0]
    path_x = [p[0] for p in first_path]
    path_y = [p[1] for p in first_path]
    ax1.plot(path_x, path_y, 'b-', linewidth=3, label=f'İlk Yol ({len(first_path)} adım)')
    ax1.plot(start[0], start[1], 'go', markersize=12, label='Başlangıç')
    ax1.plot(goal[0], goal[1], 'ro', markersize=12, label='Hedef')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Son yol
    plotter2 = PathPlotter()
    plotter2.fig, plotter2.ax = fig, ax2
    plotter2.ax.set_xlim(-0.5, grid_map.width - 0.5)
    plotter2.ax.set_ylim(-0.5, grid_map.height - 0.5)
    plotter2.ax.set_aspect('equal')
    plotter2.ax.set_title('Son Planlanan Yol (Hareketli Engel Sonrası)', fontsize=14)
    plotter2.plot_grid(grid_map)
    
    # Son yolu çiz
    if paths_history:
        last_path = paths_history[-1]
        path_x = [p[0] for p in last_path]
        path_y = [p[1] for p in last_path]
        ax2.plot(path_x, path_y, 'r-', linewidth=3, label=f'Son Yol ({len(last_path)} adım)')
        ax2.plot(start[0], start[1], 'go', markersize=12, label='Başlangıç')
        ax2.plot(goal[0], goal[1], 'ro', markersize=12, label='Hedef')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    import os
    plt.savefig(os.path.join(os.path.dirname(__file__), 'dynamic_obstacles_comparison.png'), dpi=300, bbox_inches='tight')
    print("Karşılaştırma görseli 'dynamic_obstacles_comparison.png' dosyasına kaydedildi.")
    
    # Performance grafiği
    if planning_times:
        plt.figure(figsize=(10, 6))
        plt.plot(range(1, len(planning_times)+1), planning_times, 'bo-', linewidth=2, markersize=8)
        plt.xlabel('Yeniden Planlama Numarası')
        plt.ylabel('Süre (saniye)')
        plt.title('D* Lite Yeniden Planlama Performance')
        plt.grid(True, alpha=0.3)
        plt.xticks(range(1, len(planning_times)+1))
        
        # Ortalama çizgisi
        avg_time = sum(planning_times) / len(planning_times)
        plt.axhline(y=avg_time, color='r', linestyle='--', label=f'Ortalama: {avg_time:.4f}s')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig(os.path.join(os.path.dirname(__file__), 'replanning_performance.png'), dpi=300, bbox_inches='tight')
        print("Performance grafiği 'replanning_performance.png' dosyasına kaydedildi.")
    
    print("\nDinamik engeller örneği tamamlandı")

if __name__ == "__main__":
    simulate_moving_obstacle()