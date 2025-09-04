import numpy as np
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
from dataclasses import dataclass

@dataclass
class TrafficMetrics:
    """Trafik metrikleri"""
    average_speed: float
    congestion_level: float
    vehicle_density: float
    intersection_delays: float
    route_efficiency: float
    safety_index: float

class TrafficAnalyzer:
    """Trafik analizi sınıfı"""
    
    def __init__(self):
        self.metrics_history = []
        self.route_comparisons = []
    
    def analyze_route_performance(self, path: List[Tuple[int, int]], 
                                 traffic_env, planning_time: float) -> Dict:
        """Rota performans analizi"""
        if not path:
            return {}
        
        # Temel metrikler
        route_length = len(path)
        estimated_distance = route_length * 5  # metre
        
        # Yol tipi analizi
        highway_ratio = 0
        main_street_ratio = 0
        narrow_street_ratio = 0
        
        for x, y in path:
            road_type = traffic_env.road_grid[y, x]
            if road_type == 1:  # Highway
                highway_ratio += 1
            elif road_type == 2:  # Main street
                main_street_ratio += 1
            elif road_type == 4:  # Narrow street
                narrow_street_ratio += 1
        
        total_points = len(path)
        highway_ratio /= total_points
        main_street_ratio /= total_points
        narrow_street_ratio /= total_points
        
        # Trafik yoğunluğu analizi
        traffic_densities = []
        speed_limits = []
        
        for x, y in path:
            traffic_densities.append(traffic_env.traffic_grid[y, x])
            speed_limits.append(traffic_env.speed_limit_grid[y, x])
        
        avg_traffic_density = np.mean(traffic_densities)
        avg_speed_limit = np.mean(speed_limits)
        
        # Güvenlik indeksi hesaplama
        safety_index = self._calculate_safety_index(path, traffic_env)
        
        # Verimlilik skoru
        efficiency_score = self._calculate_efficiency_score(
            route_length, planning_time, avg_traffic_density
        )
        
        return {
            'route_length_km': estimated_distance / 1000,
            'planning_time_ms': planning_time * 1000,
            'highway_ratio': highway_ratio,
            'main_street_ratio': main_street_ratio,
            'narrow_street_ratio': narrow_street_ratio,
            'avg_traffic_density': avg_traffic_density,
            'avg_speed_limit_kmh': avg_speed_limit,
            'safety_index': safety_index,
            'efficiency_score': efficiency_score,
            'route_type': self._classify_route_type(highway_ratio, main_street_ratio)
        }
    
    def _calculate_safety_index(self, path: List[Tuple[int, int]], traffic_env) -> float:
        """Güvenlik indeksi hesaplama"""
        safety_scores = []
        
        for x, y in path:
            # Trafik yoğunluğu faktörü (düşük yoğunluk = güvenli)
            traffic_factor = 1.0 - min(traffic_env.traffic_grid[y, x], 1.0)
            
            # Hız limiti faktörü (orta hız = güvenli)
            speed_limit = traffic_env.speed_limit_grid[y, x]
            speed_factor = 1.0 - abs(speed_limit - 50) / 50.0
            speed_factor = max(0.0, speed_factor)
            
            # Yol tipi faktörü
            road_type = traffic_env.road_grid[y, x]
            road_safety = {1: 0.9, 2: 0.8, 3: 0.7, 4: 0.5, 5: 0.4, 6: 0.3}.get(road_type, 0.5)
            
            # Kombinasyon
            safety_score = (traffic_factor * 0.4 + speed_factor * 0.3 + road_safety * 0.3)
            safety_scores.append(safety_score)
        
        return np.mean(safety_scores)
    
    def _calculate_efficiency_score(self, route_length: int, planning_time: float, 
                                   traffic_density: float) -> float:
        """Verimlilik skoru hesaplama"""
        # Planlama hızı skoru (hızlı planlama = verimli)
        planning_score = max(0, 1.0 - planning_time / 0.1)  # 0.1s baseline
        
        # Rota kompaktlığı (kısa rota = verimli)
        length_score = max(0, 1.0 - route_length / 200)  # 200 adım baseline
        
        # Trafik kaçınma skoru (az trafik = verimli)
        traffic_avoidance = max(0, 1.0 - traffic_density)
        
        return (planning_score * 0.3 + length_score * 0.4 + traffic_avoidance * 0.3)
    
    def _classify_route_type(self, highway_ratio: float, main_street_ratio: float) -> str:
        """Rota tipi sınıflandırma"""
        if highway_ratio > 0.6:
            return "Otoyol Ağırlıklı"
        elif main_street_ratio > 0.4:
            return "Ana Cadde Ağırlıklı"
        elif highway_ratio + main_street_ratio > 0.5:
            return "Karma (Hızlı)"
        else:
            return "Şehir İçi (Yavaş)"
    
    def compare_algorithms(self, routes_data: Dict) -> Dict:
        """Algoritma karşılaştırması"""
        comparison = {
            'algorithm_comparison': {},
            'best_performer': {},
            'recommendations': []
        }
        
        for algo_name, data in routes_data.items():
            avg_planning_time = np.mean([r['planning_time_ms'] for r in data])
            avg_route_length = np.mean([r['route_length_km'] for r in data])
            avg_safety = np.mean([r['safety_index'] for r in data])
            avg_efficiency = np.mean([r['efficiency_score'] for r in data])
            
            comparison['algorithm_comparison'][algo_name] = {
                'avg_planning_time_ms': avg_planning_time,
                'avg_route_length_km': avg_route_length,
                'avg_safety_index': avg_safety,
                'avg_efficiency_score': avg_efficiency,
                'total_routes': len(data)
            }
        
        # En iyi performer belirleme
        best_overall = max(routes_data.keys(), 
                          key=lambda x: comparison['algorithm_comparison'][x]['avg_efficiency_score'])
        
        comparison['best_performer'] = {
            'algorithm': best_overall,
            'score': comparison['algorithm_comparison'][best_overall]['avg_efficiency_score']
        }
        
        # Öneriler
        comparison['recommendations'] = self._generate_recommendations(comparison)
        
        return comparison
    
    def _generate_recommendations(self, comparison: Dict) -> List[str]:
        """Algoritma önerileri üret"""
        recommendations = []
        
        best_algo = comparison['best_performer']['algorithm']
        best_score = comparison['best_performer']['score']
        
        if best_score > 0.8:
            recommendations.append(f"{best_algo} mükemmel performans gösteriyor")
        elif best_score > 0.6:
            recommendations.append(f"{best_algo} iyi performans, küçük optimizasyonlar yapılabilir")
        else:
            recommendations.append(f"Tüm algoritmalar için optimizasyon gerekli")
        
        # Trafik yoğunluğuna göre öneriler
        for algo, data in comparison['algorithm_comparison'].items():
            if data['avg_planning_time_ms'] < 10:
                recommendations.append(f"{algo} gerçek zamanlı uygulamalar için uygun")
            
            if data['avg_safety_index'] > 0.7:
                recommendations.append(f"{algo} güvenli rotalar için tercih edilebilir")
        
        return recommendations

def create_comprehensive_report(analyzer: TrafficAnalyzer, results: Dict):
    """Kapsamlı rapor oluştur"""
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('D* Lite İstanbul Trafik Analiz Raporu', fontsize=16, fontweight='bold')
    
    # 1. Planlama süreleri
    algorithms = list(results.keys())
    planning_times = [results[algo]['avg_planning_time_ms'] for algo in algorithms]
    
    axes[0, 0].bar(algorithms, planning_times, color=['blue', 'red', 'green'][:len(algorithms)])
    axes[0, 0].set_title('Ortalama Planlama Süreleri')
    axes[0, 0].set_ylabel('Süre (milisaniye)')
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # 2. Rota uzunlukları
    route_lengths = [results[algo]['avg_route_length_km'] for algo in algorithms]
    axes[0, 1].bar(algorithms, route_lengths, color=['skyblue', 'lightcoral', 'lightgreen'][:len(algorithms)])
    axes[0, 1].set_title('Ortalama Rota Uzunlukları')
    axes[0, 1].set_ylabel('Uzunluk (km)')
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    # 3. Güvenlik indeksleri
    safety_indices = [results[algo]['avg_safety_index'] for algo in algorithms]
    axes[0, 2].bar(algorithms, safety_indices, color=['navy', 'darkred', 'darkgreen'][:len(algorithms)])
    axes[0, 2].set_title('Ortalama Güvenlik İndeksleri')
    axes[0, 2].set_ylabel('Güvenlik Skoru (0-1)')
    axes[0, 2].set_ylim(0, 1)
    axes[0, 2].tick_params(axis='x', rotation=45)
    
    # 4. Verimlilik skorları
    efficiency_scores = [results[algo]['avg_efficiency_score'] for algo in algorithms]
    axes[1, 0].bar(algorithms, efficiency_scores, color=['purple', 'orange', 'brown'][:len(algorithms)])
    axes[1, 0].set_title('Ortalama Verimlilik Skorları')
    axes[1, 0].set_ylabel('Verimlilik Skoru (0-1)')
    axes[1, 0].set_ylim(0, 1)
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    # 5. Radar chart (çok boyutlu karşılaştırma)
    from math import pi
    
    categories = ['Hız', 'Güvenlik', 'Verimlilik', 'Rota Kalitesi']
    
    # Normalize edilmiş veriler
    max_planning = max(planning_times)
    max_length = max(route_lengths)
    
    for i, algo in enumerate(algorithms):
        values = [
            1 - results[algo]['avg_planning_time_ms'] / max_planning,  # Hız (ters)
            results[algo]['avg_safety_index'],                        # Güvenlik
            results[algo]['avg_efficiency_score'],                    # Verimlilik
            1 - results[algo]['avg_route_length_km'] / max_length     # Rota kalitesi (ters)
        ]
        
        # Radar chart çizimi
        angles = [n / len(categories) * 2 * pi for n in range(len(categories))]
        values += values[:1]  # Döngüyü kapatmak için
        angles += angles[:1]
        
        axes[1, 1].plot(angles, values, 'o-', linewidth=2, label=algo)
        axes[1, 1].fill(angles, values, alpha=0.25)
    
    axes[1, 1].set_xticks(angles[:-1])
    axes[1, 1].set_xticklabels(categories)
    axes[1, 1].set_title('Çok Boyutlu Performans Karşılaştırması')
    axes[1, 1].legend()
    axes[1, 1].set_ylim(0, 1)
    
    # 6. Sonuç özeti (metin)
    axes[1, 2].axis('off')
    
    best_algo = max(algorithms, key=lambda x: results[x]['avg_efficiency_score'])
    best_score = results[best_algo]['avg_efficiency_score']
    
    summary_text = f"""
📊 SONUÇ ÖZETİ

🥇 En İyi Algoritma: {best_algo}
⭐ Genel Skor: {best_score:.3f}

📈 Öne Çıkan Özellikler:
• En hızlı planlama: {min(planning_times):.1f}ms
• En güvenli rota: {max(safety_indices):.3f}
• En kısa mesafe: {min(route_lengths):.2f}km

🎯 Öneriler:
• İstanbul trafiği için optimize
• Gerçek zamanlı navigasyon uygun
• Dinamik rota güncellemesi aktif
    """
    
    axes[1, 2].text(0.1, 0.9, summary_text, transform=axes[1, 2].transAxes,
                   fontsize=11, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('istanbul_traffic_comprehensive_report.png', dpi=300, bbox_inches='tight')
    
    print("📋 Kapsamlı rapor oluşturuldu: 'istanbul_traffic_comprehensive_report.png'")

if __name__ == "__main__":
    # TrafficAnalyzer örnek kullanımı
    print("📊 Traffic Analyzer Test Modu")
    print("=" * 40)
    
    # Örnek test verisi oluştur
    sample_results = {
        'D* Lite': {
            'avg_planning_time_ms': 4.2,
            'avg_route_length_km': 12.5,
            'avg_safety_index': 0.84,
            'avg_efficiency_score': 0.78,
            'total_routes': 25
        },
        'A*': {
            'avg_planning_time_ms': 8.1,
            'avg_route_length_km': 11.8,
            'avg_safety_index': 0.71,
            'avg_efficiency_score': 0.65,
            'total_routes': 25
        },
        'Dijkstra': {
            'avg_planning_time_ms': 45.3,
            'avg_route_length_km': 11.2,
            'avg_safety_index': 0.69,
            'avg_efficiency_score': 0.42,
            'total_routes': 25
        }
    }
    
    # Analyzer oluştur ve test et
    analyzer = TrafficAnalyzer()
    
    print("🔍 Algoritma karşılaştırması yapılıyor...")
    comparison = analyzer.compare_algorithms(sample_results)
    
    print(f"🥇 En iyi algoritma: {comparison['best_performer']['algorithm']}")
    print(f"⭐ Skor: {comparison['best_performer']['score']:.3f}")
    
    print(f"\n📋 Öneriler:")
    for rec in comparison['recommendations']:
        print(f"   • {rec}")
    
    # Rapor oluştur
    create_comprehensive_report(analyzer, sample_results['algorithm_comparison'])
    
    print(f"\n✅ Traffic Analyzer test tamamlandı!")
    print(f"📁 Test raporu: 'istanbul_traffic_comprehensive_report.png'")
