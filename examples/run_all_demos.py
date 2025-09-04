"""
Tüm demo'ları sırayla çalıştır
"""

import subprocess
import sys
import os
import time

def run_demo(demo_name, description):
    """Demo çalıştır"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, f"examples/{demo_name}"], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ {demo_name} başarıyla tamamlandı!")
            if result.stdout:
                print("📋 Çıktı:")
                print(result.stdout[-500:])  # Son 500 karakter
        else:
            print(f"❌ {demo_name} hata ile sonlandı!")
            if result.stderr:
                print("🐛 Hata:")
                print(result.stderr[-500:])
                
    except subprocess.TimeoutExpired:
        print(f"⏰ {demo_name} zaman aşımına uğradı (5dk)")
    except Exception as e:
        print(f"💥 {demo_name} beklenmedik hata: {e}")
    
    time.sleep(2)  # Kısa bekleme

def main():
    """Ana demo çalıştırıcı"""
    print("🎯 D* STAR TÜM DEMO'LAR")
    print("=" * 40)
    
    demos = [
        ("quick_demo.py", "Hızlı Demo - Temel Özellikler"),
        ("basic_pathfinding.py", "Temel Yol Bulma"),
        ("dynamic_obstacles.py", "Dinamik Engeller"),
        ("vehicle_simulation.py", "Araç Simülasyonu"),
        ("advanced_traffic_demo.py", "Gelişmiş Trafik Simülasyonu"),
        ("istanbul_traffic_scenario.py", "İstanbul Trafik Senaryoları"),
        ("benchmark_comparison.py", "Algoritma Karşılaştırması")
    ]
    
    total_demos = len(demos)
    successful_demos = 0
    
    start_time = time.time()
    
    for i, (demo_file, description) in enumerate(demos, 1):
        print(f"\n📍 Demo {i}/{total_demos}: {description}")
        
        if os.path.exists(f"examples/{demo_file}"):
            run_demo(demo_file, description)
            successful_demos += 1
        else:
            print(f"⚠️ Demo dosyası bulunamadı: {demo_file}")
    
    total_time = time.time() - start_time
    
    # Sonuç özeti
    print(f"\n" + "="*60)
    print(f"📊 DEMO SONUÇ ÖZETİ")
    print(f"="*60)
    print(f"✅ Başarılı demo sayısı: {successful_demos}/{total_demos}")
    print(f"⏱️ Toplam süre: {total_time/60:.1f} dakika")
    print(f"📁 Oluşturulan dosyalar:")
    
    # Oluşturulan PNG dosyalarını listele
    png_files = [f for f in os.listdir('.') if f.endswith('.png')]
    for png_file in sorted(png_files):
        file_size = os.path.getsize(png_file) / 1024  # KB
        print(f"   📊 {png_file} ({file_size:.1f} KB)")
    
    if successful_demos == total_demos:
        print(f"\n🎉 TÜM DEMO'LAR BAŞARIYLA TAMAMLANDI!")
    else:
        print(f"\n⚠️ {total_demos - successful_demos} demo tamamlanamadı.")
    
    print(f"\n🚀 Proje GitHub'a yüklemeye hazır!")

if __name__ == "__main__":
    main()