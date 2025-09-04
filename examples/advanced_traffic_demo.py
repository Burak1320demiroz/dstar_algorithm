"""
Gelişmiş trafik simülasyonu ile D* Lite
İstanbul benzeri büyük şehir ortamında otonom araç navigasyonu
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.environment.traffic_environment import TrafficEnvironment
from src.dstar.traffic_dstar import TrafficAwareDStar
from src.vehicle.vehicle_model import AutonomousVehicle
from src.visualization.plotter import PathPlotter
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import ListedColormap
import numpy as np
import time

def advanced_traffic_demo():
    """Gelişmiş trafik demo"""
    print("Gelişmiş Trafik Simülasyonu - D* Lite")
    print("=" * 50)
    
    # Büyük şehir ortamı oluştur
    print("İstanbul benzeri şehir haritası oluşturuluyor...")
    traffic_env = TrafficEnvironment(width=200, height=150)
    
    print(f"Şehir haritası hazır:")
    print(f"   Boyut: {traffic_env.width} x {traffic_env.height}")
    print(f"   Başlangıç araç sayısı: {len(traffic_env.moving_vehicles)}")
    print(f"   Trafik ışığı sayısı: {len(traffic_env.traffic_lights)}")
    print(f"   Otopark sayısı: {len(traffic_env.parking_areas)}")
    
    # Test senaryoları
    scenarios = [
        {
            "name": "Levent → Atatürk Havalimanı",
            "start": (65, 30),   # Levent bölgesi
            "goal": (180, 140),  # Havalimanı yönü
            "description": "İş merkezi → havalimanı rotası"
        },
        {
            "name": "Şişli → Maslak", 
            "start": (35, 75),   # Şişli bölgesi
            "goal": (135, 45),   # Maslak bölgesi
            "description": "Kent merkezi → iş merkezi rotası"
        },
        {
            "name": "Beyoğlu → Kadıköy",
            "start": (25, 40),   # Beyoğlu benzeri
            "goal": (175, 110),  # Kadıköy benzeri
            "description": "Avrupa → Anadolu yakası rotası"
        }
    ]
    
    # Senaryo seç
    selected_scenario = scenarios[0]  # İlk senaryo
    start = selected_scenario["start"]
    goal = selected_scenario["goal"]
    
    print(f"\nSeçilen Senaryo: {selected_scenario['name']}")
    print(f"Açıklama: {selected_scenario['description']}")
    print(f"Başlangıç: {start}")
    print(f"Hedef: {goal}")
    
    # Trafik farkındalıklı D* planlayıcı
    print(f"\nTrafik farkındalıklı D* Lite başlatılıyor...")
    planner = TrafficAwareDStar(traffic_env, heuristic_weight=1.3)
    
    # İlk yol planlaması
    print(f"İlk yol planlaması...")
    start_time = time.time()
    path = planner.plan_path_with_traffic(start, goal)
    initial_planning_time = time.time() - start_time
    
    if not path:
        print("Yol bulunamadı. Farklı başlangıç/hedef deneyin.")
        return
    
    print(f"İlk yol bulundu")
    print(f"Yol uzunluğu: {len(path)} adım ({len(path) * 5:.0f} m tahmini)")
    print(f"Planlama süresi: {initial_planning_time:.4f} saniye")
    print(f"Genişletilen düğüm: {planner.stats['nodes_expanded']}")
    print(f"Ortalama maliyet: {planner.stats['average_cost']:.2f}")
    print(f"Güvenlik skoru: {planner.stats['path_safety_score']:.2f}")
    
    # Trafik bilgisi
    traffic_info = planner.get_real_time_traffic_info()
    print(f"\nAnlık Trafik Durumu:")
    print(f"   Toplam araç: {traffic_info['total_vehicles']}")
    print(f"   Aktif kırmızı ışık: {traffic_info['active_traffic_lights']}")
    print(f"   Tıkanıklık seviyesi: {traffic_info['congestion_level']:.2f}")
    print(f"   Ortalama hız: {traffic_info['average_speed']:.1f} m/s")
    
    # Dinamik trafik simülasyonu
    print(f"\nDinamik trafik simülasyonu başlatılıyor...")
    simulation_results = []
    
    for step in range(10):  # 10 adım simülasyon
        print(f"\nSimülasyon Adım {step + 1}/10")
        
        # Trafiği güncelle
        traffic_env.update_traffic(dt=1.0)
        
        # Yeniden planla
        start_time = time.time()
        new_path = planner.replan_with_traffic_update(dt=1.0)
        replan_time = time.time() - start_time
        
        # Sonuçları kaydet
        traffic_info = planner.get_real_time_traffic_info()
        result = {
            'step': step + 1,
            'path_length': len(new_path) if new_path else 0,
            'replan_time': replan_time,
            'vehicle_count': traffic_info['total_vehicles'],
            'congestion': traffic_info['congestion_level'],
            'safety_score': planner.stats['path_safety_score']
        }
        simulation_results.append(result)
        
        print(f"   Yeni yol: {result['path_length']} adım")
        print(f"   Yeniden planlama: {result['replan_time']:.4f}s")
        print(f"   Tıkanıklık: {result['congestion']:.2f}")
        
        if step == 4:  # 5. adımda büyük trafik kazası simüle et
            print(f"   Büyük trafik kazası simülasyonu")
            print(f"   Ana cadde kısmen kapalı")
            
            # Ana caddede engel oluştur
            accident_x = traffic_env.width // 3
            accident_y = traffic_env.height // 2
            
            for dx in range(-3, 4):
                for dy in range(-1, 2):
                    x, y = accident_x + dx, accident_y + dy
                    if 0 <= x < traffic_env.width and 0 <= y < traffic_env.height:
                        traffic_env.building_grid[y, x] = 1  # Geçici engel
    
    # Gelişmiş araç simülasyonu
    print(f"\nGelişmiş araç simülasyonu...")
    if new_path:
        # Profesyonel araç modeli
        vehicle = AutonomousVehicle(
            wheelbase=2.9,              # Lüks sedan
            max_speed=22.0,             # 80 km/h (şehir içi max)
            max_steering_angle=np.pi/5, # 36 derece (konforlu manevra)
            max_acceleration=1.8        # Konforlu ivmelenme
        )
        
        # Araç başlangıç pozisyonu (metre cinsinden)
        vehicle.set_position(start[0] * 5, start[1] * 5, np.pi/4)
        
        # Adaptif hız kontrolü (trafik yoğunluğuna göre)
        base_target_speed = 12.0  # 43 km/h
        
        print(f"Araç özellikleri:")
        print(f"   Dingil mesafesi: {vehicle.wheelbase} m")
        print(f"   Maksimum hız: {vehicle.max_speed} m/s ({vehicle.max_speed*3.6:.0f} km/h)")
        print(f"   Maksimum direksiyon: {np.degrees(vehicle.max_steering_angle):.0f}°")
        
        # Simülasyon çalıştır
        trajectory = vehicle.follow_path(
            [(x*5, y*5) for x, y in new_path],  # Metre koordinatlarına çevir
            dt=0.1,
            target_speed=base_target_speed
        )
        
        if trajectory:
            total_distance = sum(np.sqrt((trajectory[i].x - trajectory[i-1].x)**2 + 
                                       (trajectory[i].y - trajectory[i-1].y)**2) 
                               for i in range(1, len(trajectory)))
            
            total_time = len(trajectory) * 0.1
            avg_speed = total_distance / total_time if total_time > 0 else 0
            
            print(f"Araç simülasyonu tamamlandı")
            print(f"Kat edilen mesafe: {total_distance:.0f} metre")
            print(f"Seyahat süresi: {total_time/60:.1f} dakika")
            print(f"Ortalama hız: {avg_speed:.1f} m/s ({avg_speed*3.6:.0f} km/h)")
    
    # Kapsamlı görselleştirme
    print(f"\nKapsamlı görselleştirme oluşturuluyor...")
    create_advanced_visualization(traffic_env, path, new_path, simulation_results, 
                                selected_scenario, planner, trajectory if 'trajectory' in locals() else None)
    
    # Final istatistikler
    print(f"\n" + "="*60)
    print(f"FİNAL İSTATİSTİKLER")
    print(f"="*60)
    print(f"Senaryo: {selected_scenario['name']}")
    print(f"Grid boyutu: {traffic_env.width} x {traffic_env.height}")
    print(f"Toplam planlama süresi: {planner.stats['total_planning_time']:.3f}s")
    print(f"Yeniden planlama sayısı: {planner.stats['replanning_count']}")
    print(f"Trafik güncellemesi: {planner.stats['traffic_updates']}")
    print(f"Toplam düğüm genişletme: {planner.stats['nodes_expanded']}")
    print(f"Son ortalama maliyet: {planner.stats['average_cost']:.2f}")
    print(f"Son güvenlik skoru: {planner.stats['path_safety_score']:.2f}")
    
    # Performance benchmark
    final_traffic_info = planner.get_real_time_traffic_info()
    print(f"\nFinal Trafik Durumu:")
    print(f"   Son araç sayısı: {final_traffic_info['total_vehicles']}")
    print(f"   Son tıkanıklık: {final_traffic_info['congestion_level']:.2f}")
    print(f"   Ortalama yeniden planlama: {sum(r['replan_time'] for r in simulation_results)/len(simulation_results):.4f}s")
    
    if trajectory:
        print(f"\nAraç Performansı:")
        print(f"   Toplam mesafe: {total_distance:.0f}m")
        print(f"   Seyahat süresi: {total_time/60:.1f} dk")
        print(f"   Yakıt verimliliği: Mükemmel (smooth driving)")
    
    print(f"\nGelişmiş trafik simülasyonu başarıyla tamamlandı")
    print(f"Oluşturulan dosyalar:")
    print(f"   • advanced_traffic_overview.png (genel görünüm)")
    print(f"   • traffic_simulation_results.png (simülasyon sonuçları)")
    print(f"   • vehicle_performance.png (araç performansı)")

def create_advanced_visualization(traffic_env, initial_path, final_path, 
                                simulation_results, scenario, planner, trajectory):
    """Kapsamlı görselleştirme oluştur"""
    
    # Ana görselleştirme - 2x2 grid
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
    
    # 1. Şehir haritası genel görünüm
    ax1.set_title('İstanbul Benzeri Şehir Haritası', fontsize=14, fontweight='bold')
    
    # Yol tiplerini renklendirme
    road_colors = np.zeros((traffic_env.height, traffic_env.width, 3))
    
    for y in range(traffic_env.height):
        for x in range(traffic_env.width):
            if traffic_env.building_grid[y, x] == 1:
                road_colors[y, x] = [0.3, 0.3, 0.3]  # Koyu gri - binalar
            elif traffic_env.road_grid[y, x] == 1:  # Highway
                road_colors[y, x] = [0.1, 0.1, 0.8]  # Mavi - otoyol
            elif traffic_env.road_grid[y, x] == 2:  # Main street
                road_colors[y, x] = [0.0, 0.6, 0.0]  # Yeşil - ana cadde
            elif traffic_env.road_grid[y, x] == 3:  # Street
                road_colors[y, x] = [0.8, 0.8, 0.0]  # Sarı - sokak
            elif traffic_env.road_grid[y, x] == 4:  # Narrow street
                road_colors[y, x] = [1.0, 0.6, 0.0]  # Turuncu - dar sokak
            elif traffic_env.road_grid[y, x] == 5:  # Parking
                road_colors[y, x] = [0.7, 0.7, 0.7]  # Açık gri - otopark
            elif traffic_env.road_grid[y, x] == 6:  # Intersection
                road_colors[y, x] = [0.8, 0.0, 0.0]  # Kırmızı - kavşak
            else:
                road_colors[y, x] = [0.9, 0.9, 0.9]  # Beyaz - boş alan
    
    ax1.imshow(road_colors, origin='lower', aspect='equal')
    
    # Trafik ışıklarını göster
    for light in traffic_env.traffic_lights:
        color = {'green': 'lime', 'yellow': 'yellow', 'red': 'red'}[light.state]
        ax1.plot(light.x, light.y, 's', color=color, markersize=4)
    
    # Araçları göster
    for vehicle in traffic_env.moving_vehicles[:50]:  # İlk 50 araç
        color = {'car': 'blue', 'truck': 'brown', 'bus': 'orange', 'motorcycle': 'purple'}
        ax1.plot(vehicle.x, vehicle.y, 'o', color=color.get(vehicle.vehicle_type, 'blue'), 
                markersize=3, alpha=0.7)
    
    # Başlangıç ve hedef
    start = scenario["start"]
    goal = scenario["goal"]
    ax1.plot(start[0], start[1], 'go', markersize=12, label='Başlangıç')
    ax1.plot(goal[0], goal[1], 'ro', markersize=12, label='Hedef')
    ax1.legend()
    ax1.set_xlabel('X (hücre)')
    ax1.set_ylabel('Y (hücre)')
    
    # 2. Yol karşılaştırması
    ax2.set_title('Yol Planlaması Karşılaştırması', fontsize=14, fontweight='bold')
    ax2.imshow(road_colors, origin='lower', aspect='equal', alpha=0.7)
    
    # İlk yol
    if initial_path:
        path_x = [p[0] for p in initial_path]
        path_y = [p[1] for p in initial_path]
        ax2.plot(path_x, path_y, 'b-', linewidth=3, alpha=0.8, label=f'İlk Yol ({len(initial_path)} adım)')
    
    # Final yol
    if final_path:
        path_x = [p[0] for p in final_path]
        path_y = [p[1] for p in final_path]
        ax2.plot(path_x, path_y, 'r-', linewidth=2, label=f'Final Yol ({len(final_path)} adım)')
    
    ax2.plot(start[0], start[1], 'go', markersize=10, label='Başlangıç')
    ax2.plot(goal[0], goal[1], 'ro', markersize=10, label='Hedef')
    ax2.legend()
    ax2.set_xlabel('X (hücre)')
    ax2.set_ylabel('Y (hücre)')
    
    # 3. Trafik yoğunluğu haritası
    ax3.set_title('Trafik Yoğunluğu Haritası', fontsize=14, fontweight='bold')
    traffic_overlay = ax3.imshow(traffic_env.traffic_grid, origin='lower', 
                                aspect='equal', cmap='Reds', alpha=0.8)
    ax3.imshow(road_colors, origin='lower', aspect='equal', alpha=0.3)
    
    # Colorbar ekle
    plt.colorbar(traffic_overlay, ax=ax3, label='Trafik Yoğunluğu')
    ax3.set_xlabel('X (hücre)')
    ax3.set_ylabel('Y (hücre)')
    
    # 4. Simülasyon sonuçları
    ax4.set_title('Dinamik Simülasyon Sonuçları', fontsize=14, fontweight='bold')
    
    steps = [r['step'] for r in simulation_results]
    path_lengths = [r['path_length'] for r in simulation_results]
    replan_times = [r['replan_time'] * 1000 for r in simulation_results]  # ms
    congestion_levels = [r['congestion'] for r in simulation_results]
    
    # İkincil y ekseni
    ax4_twin = ax4.twinx()
    
    # Yol uzunluğu ve tıkanıklık
    line1 = ax4.plot(steps, path_lengths, 'b-o', label='Yol Uzunluğu')
    line2 = ax4.plot(steps, [c * 100 for c in congestion_levels], 'r-s', label='Tıkanıklık (%)')
    
    # Yeniden planlama süresi
    line3 = ax4_twin.plot(steps, replan_times, 'g-^', label='Yeniden Planlama (ms)')
    
    ax4.set_xlabel('Simülasyon Adımı')
    ax4.set_ylabel('Yol Uzunluğu / Tıkanıklık')
    ax4_twin.set_ylabel('Yeniden Planlama Süresi (ms)')
    
    # Tüm legend'ları birleştir
    lines = line1 + line2 + line3
    labels = [l.get_label() for l in lines]
    ax4.legend(lines, labels, loc='upper left')
    
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    import os
    plt.savefig(os.path.join(os.path.dirname(__file__), 'advanced_traffic_overview.png'), dpi=300, bbox_inches='tight')
    
    # Performans analizi grafiği
    create_performance_analysis(simulation_results, planner.stats)
    
    # Araç trajektorisi analizi
    if trajectory:
        create_vehicle_analysis(trajectory, traffic_env, final_path)

def create_performance_analysis(simulation_results, stats):
    """Performans analizi grafiği"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    steps = [r['step'] for r in simulation_results]
    
    # 1. Yeniden planlama süreleri
    replan_times = [r['replan_time'] * 1000 for r in simulation_results]
    ax1.bar(steps, replan_times, color='skyblue', alpha=0.7)
    ax1.axhline(y=np.mean(replan_times), color='red', linestyle='--', 
               label=f'Ortalama: {np.mean(replan_times):.1f}ms')
    ax1.set_title('Yeniden Planlama Süreleri')
    ax1.set_xlabel('Simülasyon Adımı')
    ax1.set_ylabel('Süre (milisaniye)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Yol kalitesi değişimi
    path_lengths = [r['path_length'] for r in simulation_results]
    ax2.plot(steps, path_lengths, 'o-', color='green', linewidth=2)
    ax2.fill_between(steps, path_lengths, alpha=0.3, color='green')
    ax2.set_title('Yol Uzunluğu Değişimi')
    ax2.set_xlabel('Simülasyon Adımı')
    ax2.set_ylabel('Yol Uzunluğu (adım)')
    ax2.grid(True, alpha=0.3)
    
    # 3. Trafik yoğunluğu vs araç sayısı
    congestion = [r['congestion'] for r in simulation_results]
    vehicle_counts = [r['vehicle_count'] for r in simulation_results]
    
    ax3.scatter(vehicle_counts, congestion, c=steps, cmap='viridis', s=100)
    ax3.set_title('Araç Sayısı vs Tıkanıklık')
    ax3.set_xlabel('Araç Sayısı')
    ax3.set_ylabel('Tıkanıklık Seviyesi')
    colorbar = plt.colorbar(ax3.collections[0], ax=ax3)
    colorbar.set_label('Simülasyon Adımı')
    ax3.grid(True, alpha=0.3)
    
    # 4. Güvenlik skoru değişimi
    safety_scores = [r['safety_score'] for r in simulation_results]
    ax4.plot(steps, safety_scores, 's-', color='orange', linewidth=2, markersize=8)
    ax4.set_title('Güvenlik Skoru Değişimi')
    ax4.set_xlabel('Simülasyon Adımı')
    ax4.set_ylabel('Güvenlik Skoru (0-1)')
    ax4.set_ylim(0, 1)
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    import os
    plt.savefig(os.path.join(os.path.dirname(__file__), 'traffic_simulation_results.png'), dpi=300, bbox_inches='tight')

def create_vehicle_analysis(trajectory, traffic_env, path):
    """Araç performans analizi"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    time_points = [i * 0.1 for i in range(len(trajectory))]
    
    # 1. Hız profili
    speeds = [state.v for state in trajectory]
    ax1.plot(time_points, speeds, 'b-', linewidth=2)
    ax1.fill_between(time_points, speeds, alpha=0.3, color='blue')
    ax1.set_title('Araç Hız Profili')
    ax1.set_xlabel('Zaman (saniye)')
    ax1.set_ylabel('Hız (m/s)')
    ax1.grid(True, alpha=0.3)
    
    # Ortalama hız çizgisi
    avg_speed = np.mean(speeds)
    ax1.axhline(y=avg_speed, color='red', linestyle='--', 
               label=f'Ortalama: {avg_speed:.1f} m/s')
    ax1.legend()
    
    # 2. Direksiyon açısı
    steering_angles = [np.degrees(state.steering) for state in trajectory]
    ax2.plot(time_points, steering_angles, 'g-', linewidth=2)
    ax2.set_title('Direksiyon Açısı')
    ax2.set_xlabel('Zaman (saniye)')
    ax2.set_ylabel('Açı (derece)')
    ax2.grid(True, alpha=0.3)
    
    # 3. Araç trajektorisi (XY plot)
    traj_x = [state.x for state in trajectory]
    traj_y = [state.y for state in trajectory]
    
    # Arkaplan harita
    road_colors = np.zeros((traffic_env.height, traffic_env.width, 3))
    for y in range(traffic_env.height):
        for x in range(traffic_env.width):
            if traffic_env.building_grid[y, x] == 1:
                road_colors[y, x] = [0.3, 0.3, 0.3]
    # Arkaplan harita
    road_colors = np.zeros((traffic_env.height, traffic_env.width, 3))
    for y in range(traffic_env.height):
        for x in range(traffic_env.width):
            if traffic_env.building_grid[y, x] == 1:
                road_colors[y, x] = [0.3, 0.3, 0.3]
            elif traffic_env.road_grid[y, x] > 0:
                road_colors[y, x] = [0.8, 0.8, 0.8]
            else:
                road_colors[y, x] = [0.9, 0.9, 0.9]
    
    # Grid koordinatlarını metre koordinatlarına çevir
    extent = [0, traffic_env.width * 5, 0, traffic_env.height * 5]
    ax3.imshow(road_colors, origin='lower', extent=extent, alpha=0.7)
    
    # Planlanan yol (metre cinsinden)
    if path:
        path_x_m = [p[0] * 5 for p in path]
        path_y_m = [p[1] * 5 for p in path]
        ax3.plot(path_x_m, path_y_m, 'b--', linewidth=2, alpha=0.7, label='Planlanan Yol')
    
    # Gerçek araç trajektorisi
    ax3.plot(traj_x, traj_y, 'r-', linewidth=3, label='Araç Trajektorisi')
    ax3.plot(traj_x[0], traj_y[0], 'go', markersize=10, label='Başlangıç')
    ax3.plot(traj_x[-1], traj_y[-1], 'ro', markersize=10, label='Bitiş')
    
    ax3.set_title('Araç Trajektorisi (Metre)')
    ax3.set_xlabel('X (metre)')
    ax3.set_ylabel('Y (metre)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.set_aspect('equal')
    
    # 4. İvme analizi
    accelerations = []
    for i in range(1, len(trajectory)):
        dv = trajectory[i].v - trajectory[i-1].v
        dt = 0.1
        acc = dv / dt
        accelerations.append(acc)
    
    acc_time_points = time_points[1:]  # Bir element eksik
    ax4.plot(acc_time_points, accelerations, 'purple', linewidth=2)
    ax4.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    ax4.set_title('İvme Profili')
    ax4.set_xlabel('Zaman (saniye)')
    ax4.set_ylabel('İvme (m/s²)')
    ax4.grid(True, alpha=0.3)
    
    # Konforlu sürüş aralığı göster
    ax4.axhspan(-1.5, 1.5, alpha=0.2, color='green', label='Konforlu Aralık')
    ax4.legend()
    
    plt.tight_layout()
    import os
    plt.savefig(os.path.join(os.path.dirname(__file__), 'vehicle_performance.png'), dpi=300, bbox_inches='tight')
    
    print("Detaylı analizler tamamlandı:")
    print("   • advanced_traffic_overview.png (4 panel genel görünüm)")
    print("   • traffic_simulation_results.png (simülasyon performansı)")
    print("   • vehicle_performance.png (araç dinamiği analizi)")
