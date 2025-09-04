# D* Lite Tabanlı Dinamik Yol Planlama ve Trafik Simülasyonu

Bu proje, D* (D-star) ve D* Lite algoritmalarını kullanarak dinamik ortamda yol planlama yapar ve İstanbul benzeri bir trafik simülasyonu sunar. Araç kinematiği, dinamik engeller, trafik ışıkları ve yoğunluk gibi gerçekçi faktörler dikkate alınır. Tüm örnekler PNG formatında görseller üretir.

## İçindekiler
- Proje Özellikleri
- Kurulum
- Hızlı Başlangıç
- Örnek Senaryolar ve Üretilen PNG Dosyaları
- Gelişmiş Trafik Simülasyonu
- Performans Metrikleri ve Karşılaştırmalar
- Testler
- Katkıda Bulunma
- Lisans

## Proje Özellikleri
- D* ve D* Lite algoritmaları ile dinamik yol planlama
- Dinamik çevre: hareketli engeller, yol kapanmaları, trafik yoğunluğu
- Araç kinematik modeli ve temel araç takip simülasyonu
- Matplotlib ile gelişmiş görselleştirme ve otomatik PNG çıktıları
- Senaryo tabanlı test yapısı ve analiz araçları
- D* Lite ve referans bir “orijinal” D* Lite varyantı (`DStarLiteOriginal`)

## Kurulum
```bash
# Depoyu klonlayın
git clone https://github.com/yourusername/dstar-pathfinding.git
cd dstar-pathfinding

# Sanal ortam (önerilir)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Gereksinimleri yükleyin
pip install -r requirements.txt

# Geliştirici modu kurulum (opsiyonel)
pip install -e .
```
Yürütme sonunda PNG görseller proje kök dizinine kaydedilir.

## Mevcut Görseller (Önizleme ve Kısa Açıklamalar)

![Hızlı Demo - Yol Planlaması](examples/quick_demo.png)
Planlanan yolun engelleri dolaşarak başlangıçtan hedefe ulaşması.

![Hızlı Demo - Araç Simülasyonu](examples/quick_demo_vehicle.png)
Araç kinematik modeliyle planlanan yolun takibi ve gerçek trajektori.

![Hızlı Demo - Kontrol Profili](examples/quick_demo_control.png)
Zaman ekseninde hız ve direksiyon açısı profilleri.

![Temel Yol - İlk Yol](examples/original_path.png)
İlk planlanan yol ve başlangıç/hedef işaretleri.

![Temel Yol - Yeniden Planlanan Yol](examples/replanned_path.png)
Ortaya eklenen engel sonrası yeniden planlanan alternatif yol.

![Dinamik Engeller - Karşılaştırma](examples/dynamic_obstacles_comparison.png)
Hareketli engeller boyunca ilk ve son yolun yan yana karşılaştırması.

![Dinamik Engeller - Yeniden Planlama Performansı](examples/replanning_performance.png)
Her adımda yeniden planlama sürelerinin karşılaştırmalı grafiği.

![Araç Simülasyonu - Basit Görünüm](examples/vehicle_simulation.png)
Planlanan yol ve aracın izlediği gerçek trajektori (basit görünüm).

![Araç Simülasyonu - Kontrol Profili](examples/vehicle_control_profile.png)
Araç hız ve direksiyon açısı zaman serileri.

![Benchmark Sonuçları](examples/benchmark_results.png)
A* ve D* Lite arasında süre, düğüm sayısı ve ölçeklenme karşılaştırması.

Not: Tüm görseller `examples/` klasörüne kaydedilir.

## Lisans
Bu proje MIT Lisansı ile lisanslanmıştır. Ayrıntılar için `LICENSE` dosyasına bakınız.