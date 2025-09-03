import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.dstar.dstar_lite import DStarLite
from src.environment.grid_map import GridMap
from src.visualization.plotter import PathPlotter
import time
import heapq
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Tuple, Dict

class AStar:
    """A* algoritması karşılaştırma için"""
    
    def __init__(self, grid_map):
        self.grid_map = grid_map
        self.stats = {'nodes_expanded': 0}
    
    def heuristic(self, pos1, pos2):
        """Manhattan distance heuristic"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def get_neighbors(self, pos):
        """8-yönlü komşular"""
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                x, y = pos[0] + dx, pos[1] + dy
                if (0 <= x < self.grid_map.width and 0 <= y < self.grid_map.height 
                    and not self.grid_map.is_obstacle(x, y)):
                    neighbors.append((x, y))
        return neighbors
    
    def get_cost(self, pos1, pos2):
        """İki pozisyon arası maliyet"""
        dx = abs(pos1[0] - pos2[0])
        dy = abs(pos1[1] - pos2[1])
        if dx == 1 and dy == 1:  # Diagonal
            return np.sqrt(2)
        return 1.0
    
    def plan_path(self, start, goal):
        """A* ile yol planla"""
        self.stats['nodes_expanded'] = 0
        
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}
        
        while open_set:
            current = heapq.heappop(open_set)[1]
            self.stats['nodes_expanded'] += 1
            
            if current == goal:
                # Yolu reconstruct et
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1]
            
            for neighbor in self.get_neighbors(current):
                tentative_g_score = g_score[current] + self.get_cost(current, neighbor)
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + self.heuristic(neighbor, goal)
                    
                    if neighbor not in [item[1] for item in open_set]:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        return []

def run_benchmark():
    """Benchmark testlerini çalıştır"""
    print("D* Lite vs A* Benchmark Karşılaştırması")
    print("=" * 50)
    
    # Test senaryoları
    scenarios = [
        {"name": "Küçük Grid (20x20)", "size": (20, 20), "obstacles": 0.1},
        {"name": "Orta Grid (50x50)", "size": (50, 50), "obstacles": 0.15},
        {"name": "Büyük Grid (100x100)", "size": (100, 100), "obstacles": 0.2},
        {"name": "Çok Engelli (50x50)", "size": (50, 50), "obstacles": 0.3},
    ]
    
    results = []
    
    for scenario in scenarios:
        print(f"\n📋 Test Senaryosu: {scenario['name']}")
        print("-" * 40)
        
        width, height = scenario['size']
        grid_map = GridMap(width, height)
        
        # Rastgele engeller
        grid_map.add_random_obstacles(scenario['obstacles'])
        
        # Test noktaları
        start = (2, 2)
        goal = (width-3, height-3)
        
        # Engellerin başlangıç ve hedefe çok yakın olmamasını sağla
        grid_map.clear_area(0, 0, 5, 5)
        grid_map.clear_area(width-6, height-6, width-1, height-1)
        
        print(f"Grid boyutu: {width}x{height}")
        print(f"Engel oranı: {scenario['obstacles']*100:.0f}%")
        print(f"Başlangıç: {start}, Hedef: {goal}")
        
        # A* testi
        print("\n🔍 A* Algoritması test ediliyor...")
        astar = AStar(grid_map)
        
        start_time = time.time()
        astar_path = astar.plan_path(start, goal)
        astar_time = time.time() - start_time
        
        if astar_path:
            print(f"✅ A* - Yol bulundu: {len(astar_path)} adım")
            print(f"⏱️ A* - Süre: {astar_time:.4f} saniye")
            print(f"🔍 A* - Genişletilen düğüm: {astar.stats['nodes_expanded']}")
        else:
            print("❌ A* - Yol bulunamadı")
            continue
        
        # D* Lite testi
        print("\n🌟 D* Lite Algoritması test ediliyor...")
        dstar = DStarLite(grid_map, heuristic_weight=1.0)
        
        start_time = time.time()
        dstar_path = dstar.plan_path(start, goal)
        dstar_time = time.time() - start_time
        
        if dstar_path:
            print(f"✅ D* Lite - Yol bulundu: {len(dstar_path)} adım")
            print(f"⏱️ D* Lite - Süre: {dstar_time:.4f} saniye")
            print(f"🔍 D* Lite - Genişletilen düğüm: {dstar.stats['nodes_expanded']}")
        else:
            print("❌ D* Lite - Yol bulunamadı")
            continue
        
        # Dinamik değişiklik testi (sadece D* Lite için)
        print("\n🔄 Dinamik değişiklik testi...")
        
        # Yolun ortasına engel ekle
        if len(dstar_path) > 4:
            mid_idx = len(dstar_path) // 2
            obstacle_x, obstacle_y = dstar_path[mid_idx]
            
            # Engeli ekle
            grid_map.add_obstacle(obstacle_x-1, obstacle_y-1, obstacle_x+1, obstacle_y+1)
            
            # D* Lite yeniden planlama
            start_time = time.time()
            changed_cells = []
            for x in range(obstacle_x-1, obstacle_x+2):
                for y in range(obstacle_y-1, obstacle_y+2):
                    if grid_map.is_valid_cell(x, y):
                        changed_cells.append((x, y, True))
            
            dstar.update_obstacles(changed_cells)
            dstar_replan_path = dstar.replan_path()
            dstar_replan_time = time.time() - start_time
            
            # A* yeniden planlama (sıfırdan)
            start_time = time.time()
            astar_replan = AStar(grid_map)
            astar_replan_path = astar_replan.plan_path(start, goal)
            astar_replan_time = time.time() - start_time
            
            print(f"🌟 D* Lite Yeniden Planlama: {dstar_replan_time:.4f} saniye")
            print(f"🔍 A* Yeniden Planlama: {astar_replan_time:.4f} saniye")
            
            if dstar_replan_time > 0:
                speedup = astar_replan_time / dstar_replan_time
                print(f"🚀 D* Lite Hızlanma Oranı: {speedup:.1f}x")
        else:
            dstar_replan_time = 0
            astar_replan_time = 0
            speedup = 0
        
        # Sonuçları kaydet
        results.append({
            'scenario': scenario['name'],
            'grid_size': width * height,
            'obstacle_ratio': scenario['obstacles'],
            'astar_time': astar_time,
            'dstar_time': dstar_time,
            'astar_nodes': astar.stats['nodes_expanded'],
            'dstar_nodes': dstar.stats['nodes_expanded'],
            'astar_path_length': len(astar_path) if astar_path else 0,
            'dstar_path_length': len(dstar_path) if dstar_path else 0,
            'astar_replan_time': astar_replan_time,
            'dstar_replan_time': dstar_replan_time,
            'replan_speedup': speedup
        })
        
        print(f"\n📊 Bu senaryo için özet:")
        print(f"  • İlk Planlama Hız Karşılaştırması: A* {astar_time:.4f}s vs D* {dstar_time:.4f}s")
        print(f"  • Yol Kalitesi: A* {len(astar_path)} vs D* {len(dstar_path)} adım")
        print(f"  • Genişletilen Düğüm: A* {astar.stats['nodes_expanded']} vs D* {dstar.stats['nodes_expanded']}")
        if speedup > 0:
            print(f"  • Yeniden Planlama Avantajı: {speedup:.1f}x daha hızlı")
    
    # Sonuç analizi
    print(f"\n" + "=" * 50)
    print("📊 GENEL SONUÇLAR VE ANALİZ")
    print("=" * 50)
    
    if results:
        # Ortalama performans
        avg_astar_time = sum(r['astar_time'] for r in results) / len(results)
        avg_dstar_time = sum(r['dstar_time'] for r in results) / len(results)
        avg_speedup = sum(r['replan_speedup'] for r in results if r['replan_speedup'] > 0)
        replan_tests = len([r for r in results if r['replan_speedup'] > 0])
        
        if replan_tests > 0:
            avg_speedup = avg_speedup / replan_tests
        
        print(f"\n🏆 İlk Planlama Performansı:")
        print(f"  • A* Ortalama: {avg_astar_time:.4f} saniye")
        print(f"  • D* Lite Ortalama: {avg_dstar_time:.4f} saniye")
        
        if avg_dstar_time > 0:
            initial_ratio = avg_astar_time / avg_dstar_time
            if initial_ratio > 1:
                print(f"  • A* {initial_ratio:.1f}x daha hızlı (ilk planlama)")
            else:
                print(f"  • D* Lite {1/initial_ratio:.1f}x daha hızlı (ilk planlama)")
        
        if replan_tests > 0:
            print(f"\n🔄 Yeniden Planlama Performansı:")
            print(f"  • Ortalama D* Lite hızlanma oranı: {avg_speedup:.1f}x")
            print(f"  • D* Lite'ın ana avantajı dinamik ortamlarda!")
    
    # Görselleştirme
    create_benchmark_plots(results)
    
    print(f"\n🎯 SONUÇ: D* Lite, dinamik ortamlarda ve yeniden planlama")
    print(f"gerektiren uygulamalarda büyük avantaj sağlar!")
    print(f"\nDetaylı grafikler 'benchmark_results.png' dosyasında.")

def create_benchmark_plots(results):
    """Benchmark sonuçlarını görselleştir"""
    if not results:
        return
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    scenarios = [r['scenario'] for r in results]
    astar_times = [r['astar_time'] for r in results]
    dstar_times = [r['dstar_time'] for r in results]
    astar_nodes = [r['astar_nodes'] for r in results]
    dstar_nodes = [r['dstar_nodes'] for r in results]
    
    # 1. Planlama süreleri karşılaştırması
    x = np.arange(len(scenarios))
    width = 0.35
    
    ax1.bar(x - width/2, astar_times, width, label='A*', alpha=0.8, color='blue')
    ax1.bar(x + width/2, dstar_times, width, label='D* Lite', alpha=0.8, color='red')
    ax1.set_xlabel('Test Senaryoları')
    ax1.set_ylabel('Planlama Süresi (saniye)')
    ax1.set_title('İlk Planlama Süresi Karşılaştırması')
    ax1.set_xticks(x)
    ax1.set_xticklabels(scenarios, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Genişletilen düğüm sayısı
    ax2.bar(x - width/2, astar_nodes, width, label='A*', alpha=0.8, color='blue')
    ax2.bar(x + width/2, dstar_nodes, width, label='D* Lite', alpha=0.8, color='red')
    ax2.set_xlabel('Test Senaryoları')
    ax2.set_ylabel('Genişletilen Düğüm Sayısı')
    ax2.set_title('Genişletilen Düğüm Karşılaştırması')
    ax2.set_xticks(x)
    ax2.set_xticklabels(scenarios, rotation=45, ha='right')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Yeniden planlama hızlanma oranı
    replan_speedups = [r['replan_speedup'] for r in results if r['replan_speedup'] > 0]
    replan_scenarios = [r['scenario'] for r in results if r['replan_speedup'] > 0]
    
    if replan_speedups:
        ax3.bar(range(len(replan_scenarios)), replan_speedups, color='green', alpha=0.7)
        ax3.set_xlabel('Test Senaryoları')
        ax3.set_ylabel('Hızlanma Oranı (kat)')
        ax3.set_title('D* Lite Yeniden Planlama Hızlanma Oranı')
        ax3.set_xticks(range(len(replan_scenarios)))
        ax3.set_xticklabels(replan_scenarios, rotation=45, ha='right')
        ax3.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='Eşit Performans')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
    
    # 4. Grid büyüklüğü vs performans
    grid_sizes = [r['grid_size'] for r in results]
    ax4.scatter(grid_sizes, astar_times, label='A*', color='blue', s=60, alpha=0.7)
    ax4.scatter(grid_sizes, dstar_times, label='D* Lite', color='red', s=60, alpha=0.7)
    ax4.set_xlabel('Grid Büyüklüğü (hücre sayısı)')
    ax4.set_ylabel('Planlama Süresi (saniye)')
    ax4.set_title('Grid Büyüklüğü vs Performans')
    ax4.set_xscale('log')
    ax4.set_yscale('log')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('benchmark_results.png', dpi=300, bbox_inches='tight')
    print("Benchmark grafikleri 'benchmark_results.png' dosyasına kaydedildi.")

if __name__ == "__main__":
    run_benchmark()