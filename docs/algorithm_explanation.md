# D* ve D* Lite Algoritmaları - Detaylı Açıklama

## Giriş

D* (Dynamic A*) algoritmaları, dinamik ortamlarda en kısa yol bulma problemini çözen algoritmalar ailesidir. Bu algoritmalar, çevre değişikliklerini etkili bir şekilde handle ederek yeniden planlamayı optimize eder.

## D* Lite Algoritması

### Temel Kavramlar

#### 1. g ve rhs Değerleri
- **g(s)**: s düğümünün başlangıçtan gerçek en kısa mesafesi
- **rhs(s)**: s düğümünün "right-hand side" değeri (tek adımlık lookahead)

```
rhs(s) = 0                           if s = s_goal
rhs(s) = min_{s' ∈ Succ(s)}(c(s,s') + g(s'))  otherwise
```

#### 2. Tutarlılık (Consistency)
Bir düğüm s tutarlıdır eğer g(s) = rhs(s) ise. Tutarsız düğümler yeniden işlenmelidir.

#### 3. Priority Queue
Düğümler iki anahtarla önceliklendirilir:
```
k₁(s) = min(g(s), rhs(s)) + h(s, s_start)
k₂(s) = min(g(s), rhs(s))
```

### Algoritma Adımları

#### Başlatma Fazı
```python
def initialize():
    U = ∅  # Priority queue
    for all s ∈ S:
        g(s) = rhs(s) = ∞
    rhs(s_goal) = 0
    U.insert(s_goal, calculateKey(s_goal))
```

#### Ana Döngü
```python
def computeShortestPath():
    while U.topKey() < calculateKey(s_start) or rhs(s_start) ≠ g(s_start):
        u = U.pop()
        if g(u) > rhs(u):
            g(u) = rhs(u)
            for each s ∈ Pred(u):
                updateVertex(s)
        else:
            g(u) = ∞
            for each s ∈ Pred(u) ∪ {u}:
                updateVertex(s)
```

#### Düğüm Güncelleme
```python
def updateVertex(u):
    if u ≠ s_goal:
        rhs(u) = min_{s' ∈ Succ(u)}(c(u,s') + g(s'))
    if u ∈ U:
        U.remove(u)
    if g(u) ≠ rhs(u):
        U.insert(u, calculateKey(u))
```

### Dinamik Değişiklikler

Çevre değiştiğinde (engel ekleme/çıkarma):

1. Değişen kenarların maliyetlerini güncelle
2. Etkilenen düğümleri `updateVertex()` ile güncelle  
3. `computeShortestPath()` ile yeniden planla

### Karmaşıklık Analizi

- **Zaman Karmaşıklığı**: O(V log V) amortized
- **Alan Karmaşıklığı**: O(V)
- **Yeniden Planlama**: Sadece etkilenen bölgeler işlenir

### A* ile Karşılaştırma

| Özellik | A* | D* Lite |
|---------|----|---------| 
| Arama Yönü | İleri (goal'e doğru) | Geri (goal'den) |
| Dinamik Çevre | ❌ Sıfırdan yeniden planla | ✅ İnkremental güncelleme |
| İlk Planlama | Genellikle daha hızlı | Biraz daha yavaş |
| Yeniden Planlama | Çok yavaş | Çok hızlı |
| Bellek Kullanımı | Daha az | Biraz daha fazla |

### Optimizasyonlar

1. **Heuristic Weighting**: h(s) * w (w > 1) suboptimal ama hızlı çözüm
2. **Tie Breaking**: Eşit f değerlerinde tutarlı seçim
3. **Path Extraction**: Greedy yol çıkarma
4. **Lazy Deletion**: Priority queue'dan fiziksel silme yerine işaretleme

## Otonom Araçlarda Kullanım

### Avantajları
- **Gerçek Zamanlı**: Dinamik engelleri anında handle eder
- **Etkili**: Sadece değişen kısımları yeniden hesaplar  
- **Robust**: Sensor noise ve belirsizliğe dayanıklı

### Uygulama Alanları
- Otonom araç navigasyonu
- Robot yol planlaması
- Video oyunlarında AI
- Network routing

### Pratik Considerations

#### Parametre Ayarlama
- **Heuristic Weight**: 1.0 (optimal) - 2.0 (hızlı)
- **Grid Resolution**: Hassasiyet vs performans trade-off
- **Update Frequency**: Sensor data ile senkronizasyon

#### Sensor Integration
```python
def update_from_sensors(sensor_data):
    changed_cells = process_sensor_data(sensor_data)
    planner.update_obstacles(changed_cells)
    new_path = planner.replan_path()
    return new_path
```

## Kod Implementasyonu İncelemesi

Projemizdeki D* Lite implementasyonu aşağıdaki özellikleri içerir:

### Ana Sınıflar
1. **DStarLite**: Ana algoritma sınıfı
2. **Node**: Düğüm veri yapısı (g, rhs, h değerleri)
3. **PriorityQueue**: Özel priority queue implementasyonu
4. **GridMap**: 2D grid ortam modeli

### Temel Metodlar
```python
# Yol planlama
path = planner.plan_path(start, goal)

# Dinamik güncelleme  
planner.update_obstacles(changed_cells)
new_path = planner.replan_path()

# İstatistik toplama
stats = planner.stats
```

### Performance Metrikleri
- Planlama süresi
- Genişletilen düğüm sayısı  
- Yol uzunluğu ve kalitesi
- Bellek kullanımı

## Gelişmiş Konular

### Multi-Resolution Planning
Hiyerarşik planlama ile büyük ortamları handle etme:
1. Kaba çözünürlükte global plan
2. İnce çözünürlükte lokal refinement

### Anytime Variants
Zaman kısıtı altında suboptimal ama kullanışlı çözümler:
- Anytime D*
- ARA* benzeri yaklaşımlar

### 3D Extensions
3 boyutlu ortamlar için genişletmeler:
- Drone navigasyonu
- Underwater robotics
- Multi-level planning

## Sonuç

D* Lite, dinamik ortamlarda optimal yol planlaması için güçlü bir algoritmadır. Otonom araçlar gibi gerçek zamanlı uygulamalarda büyük avantaj sağlar. Doğru parametre seçimi ve sensor entegrasyonu ile mükemmel sonuçlar verir.

## Referanslar

1. Koenig, S., & Likhachev, M. (2002). D* lite. AAAI.
2. Stentz, A. (1994). Optimal and efficient path planning for partially-known environments. ICRA.
3. Hart, P. E., Nilsson, N. J., & Raphael, B. (1968). A formal basis for the heuristic determination of minimum cost paths. IEEE transactions on Systems Science and Cybernetics.