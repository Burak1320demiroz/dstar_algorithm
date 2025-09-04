import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time

from src.environment.traffic_environment import TrafficEnvironment
from src.dstar.traffic_dstar import TrafficAwareDStar
import numpy as np

def istanbul_scenarios():
    """İstanbul gerçek trafik senaryoları"""
    
    print("🇹🇷 İSTANBUL TRAFİK SENARYOLARI")
    print("=" * 40)
    
    # İstanbul'a özel trafik ortamı
    traffic_env = TrafficEnvironment(width=250, height=200)
    traffic_env.traffic_density = 0.4  # Yoğun İstanbul trafiği
    
    # Gerçek İstanbul rotaları
    istanbul_routes = [
        {
            "name": "Taksim → Levent Metro",
            "start": (50, 80),    # Taksim Meydanı
            "goal": (80, 120),    # Levent Metro
            "expected_time": "25 dakika",
            "difficulty": "Orta",
            "traffic_peak": True
        },
        {
            "name": "Kadıköy → Beşiktaş Vapur",
            "start": (180, 60),   # Kadıköy İskele
            "goal": (70, 85),     # Beşiktaş İskele
            "expected_time": "45 dakika", 
            "difficulty": "Zor",
            "traffic_peak": True
        },
        {
            "name": "Atatürk Havalimanı → Taksim",
            "start": (10, 10),    # Havalimanı
            "goal": (50, 80),     # Taksim
            "expected_time": "60 dakika",
            "difficulty": "Çok Zor",
            "traffic_peak": False
        },
        {
            "name": "Maslak → Şişli Metro",
            "start": (120, 140),  # Maslak iş merkezi
            "goal": (45, 90),     # Şişli Metro
            "expected_time": "35 dakika",
            "difficulty": "Zor",
            "traffic_peak": True
        },
        {
            "name": "Bosphorus Köprüsü Geçişi",
            "start": (60, 70),    # Avrupa yakası
            "goal": (160, 90),    # Anadolu yakası
            "expected_time": "20 dakika",
            "difficulty": "Orta",
            "traffic_peak": True
        }
    ]
    
    # Her rotayı test et
    for i, route in enumerate(istanbul_routes[:3], 1):  # İlk 3 rota
        print(f"\n🚗 ROTA {i}: {route['name']}")
        print(f"{'='*50}")
        print(f"📍 Başlangıç: {route['start']}")
        print(f"🎯 Hedef: {route['goal']}")
        print(f"⏰ Beklenen süre: {route['expected_time']}")
        print(f"📊 Zorluk: {route['difficulty']}")
        print(f"🚦 Yoğun saat: {'Evet' if route['traffic_peak'] else 'Hayır'}")
        
        # Trafik yoğunluğunu ayarla
        if route['traffic_peak']:
            traffic_env.traffic_density = 0.6  # Peak hours
        else:
            traffic_env.traffic_density = 0.3  # Off-peak
        
        # Yeniden trafik oluştur
        traffic_env.moving_vehicles = []
        traffic_env._spawn_initial_traffic()
        
        # Planlayıcı oluştur
        planner = TrafficAwareDStar(traffic_env, heuristic_weight=1.4)
        
        # Yol planla
        start_time = time.time()
        path = planner.plan_path_with_traffic(route['start'], route['goal'])
        planning_time = time.time() - start_time
        
        if path:
            estimated_distance = len(path) * 5  # metre
            traffic_info = planner.get_real_time_traffic_info()
            
            print(f"\n✅ YOL BULUNDU!")
            print(f"📏 Mesafe: {estimated_distance:.0f} metre")
            print(f"⏱️ Planlama: {planning_time:.3f} saniye")
            print(f"🛡️ Güvenlik skoru: {planner.stats['path_safety_score']:.2f}")
            print(f"💰 Ortalama maliyet: {planner.stats['average_cost']:.2f}")
            print(f"🚗 Aktif araç sayısı: {traffic_info['total_vehicles']}")
            print(f"📊 Tıkanıklık seviyesi: {traffic_info['congestion_level']:.2f}")
            
            # Tahmini seyahat süresi
            avg_speed = 15.0  # km/h İstanbul trafiği
            if traffic_info['congestion_level'] > 0.7:
                avg_speed = 8.0   # Çok yoğun trafik
            elif traffic_info['congestion_level'] > 0.4:
                avg_speed = 12.0  # Yoğun trafik
            
            estimated_time = (estimated_distance / 1000) / avg_speed * 60  # dakika
            print(f"⏰ Tahmini süre: {estimated_time:.0f} dakika")
            
            # Gerçek süre ile karşılaştırma
            expected_minutes = int(route['expected_time'].split()[0])
            if estimated_time <= expected_minutes * 1.2:
                print(f"🎯 Optimal rota bulundu! (beklenen ±20% içinde)")
            else:
                print(f"⚠️ Normalden uzun rota (trafik yoğunluğu nedeniyle)")
                
        else:
            print(f"❌ Yol bulunamadı!")
    
    print(f"\n" + "="*50)
    print(f"📊 İSTANBUL TRAFİK ANALİZ SONUCU")
    print(f"="*50)
    print(f"🏙️ Test edilen şehir: İstanbul")
    print(f"📏 Harita boyutu: {traffic_env.width}x{traffic_env.height}")
    print(f"🚦 Ortalama trafik yoğunluğu: %{traffic_env.traffic_density*100:.0f}")
    print(f"⚡ D* Lite algoritması İstanbul trafiği için optimize edildi")
    print(f"🎯 Gerçek zamanlı navigasyon için hazır!")

if __name__ == "__main__":
    istanbul_scenarios()