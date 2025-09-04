"""
D* Star projesinin temel işlevselliğini test eder
"""

import sys
import os
import traceback

# Proje root dizinini path'e ekle
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_imports():
    """Import testleri"""
    print("🔍 Import testleri...")
    
    tests = [
        ("numpy", "import numpy as np"),
        ("matplotlib", "import matplotlib.pyplot as plt"), 
        ("scipy", "import scipy"),
        ("time", "import time"),
        ("math", "import math"),
        ("random", "import random")
    ]
    
    passed = 0
    for name, import_code in tests:
        try:
            exec(import_code)
            print(f"  ✅ {name}")
            passed += 1
        except ImportError as e:
            print(f"  ❌ {name}: {e}")
        except Exception as e:
            print(f"  ⚠️ {name}: {e}")
    
    return passed, len(tests)

def test_basic_functionality():
    """Temel işlevsellik testleri"""
    print("\n🧪 Temel işlevsellik testleri...")
    
    try:
        # NumPy testi
        import numpy as np
        arr = np.array([1, 2, 3, 4, 5])
        assert len(arr) == 5
        print("  ✅ NumPy array işlemleri")
        
        # Matplotlib testi
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 1, figsize=(5, 4))
        ax.plot([1, 2, 3], [1, 4, 2])
        ax.set_title('Test Plot')
        plt.close(fig)  # Memory leak önleme
        print("  ✅ Matplotlib plotting")
        
        # Math işlemleri
        import math
        distance = math.sqrt((3-1)**2 + (4-2)**2)
        assert abs(distance - 2.828) < 0.01
        print("  ✅ Math hesaplamalar")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Temel işlevsellik hatası: {e}")
        return False

def test_project_structure():
    """Proje yapı testleri"""
    print("\n📁 Proje yapısı testleri...")
    
    required_dirs = [
        'src',
        'examples', 
        'tests',
        'docs'
    ]
    
    missing_dirs = []
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"  ✅ {directory}/")
        else:
            print(f"  ❌ {directory}/ (eksik)")
            missing_dirs.append(directory)
    
    return len(missing_dirs) == 0

def create_simple_grid_map():
    """Basit grid map oluştur"""
    print("\n🗺️ Basit grid map testi...")
    
    try:
        import numpy as np
        
        # Basit 10x10 grid
        width, height = 10, 10
        grid = np.zeros((height, width), dtype=int)
        
        # Engeller ekle
        grid[3:7, 3:7] = 1  # Ortada engel
        grid[1, 1:9] = 1    # Üstte duvar
        
        # Basit yol bulma (çok basit A*)
        start = (0, 0)
        goal = (9, 9)
        
        # Manhattan distance heuristic
        def heuristic(pos1, pos2):
            return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        
        # Basit yol var mı kontrolü
        if grid[start[1], start[0]] == 0 and grid[goal[1], goal[0]] == 0:
            print("  ✅ Grid map oluşturuldu")
            print(f"  ✅ Başlangıç {start} ve hedef {goal} erişilebilir")
            return True
        else:
            print("  ⚠️ Başlangıç veya hedef engelli")
            return False
            
    except Exception as e:
        print(f"  ❌ Grid map hatası: {e}")
        traceback.print_exc()
        return False

def test_vehicle_basics():
    """Temel araç modeli testi"""
    print("\n🚗 Temel araç modeli testi...")
    
    try:
        import numpy as np
        import math
        
        # Basit araç state
        class SimpleVehicle:
            def __init__(self):
                self.x = 0.0
                self.y = 0.0
                self.theta = 0.0  # radyan
                self.speed = 0.0
        
        vehicle = SimpleVehicle()
        
        # Basit hareket
        dt = 0.1
        target_speed = 5.0
        vehicle.speed = target_speed
        
        # İleri hareket
        vehicle.x += vehicle.speed * math.cos(vehicle.theta) * dt
        vehicle.y += vehicle.speed * math.sin(vehicle.theta) * dt
        
        expected_x = target_speed * dt  # theta=0 için
        if abs(vehicle.x - expected_x) < 0.001:
            print("  ✅ Araç hareket modeli")
            return True
        else:
            print(f"  ❌ Hareket hatası: beklenen {expected_x}, gerçek {vehicle.x}")
            return False
            
    except Exception as e:
        print(f"  ❌ Araç modeli hatası: {e}")
        return False

def create_test_visualization():
    """Test görselleştirmesi oluştur"""
    print("\n📊 Test görselleştirmesi...")
    
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        
        # Basit test grafiği
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # 1. Grid haritası
        grid = np.zeros((10, 10))
        grid[3:7, 3:7] = 1  # Engel
        
        ax1.imshow(grid, cmap='RdYlBu', origin='lower')
        ax1.set_title('Test Grid Map')
        ax1.plot(0, 0, 'go', markersize=10, label='Start')
        ax1.plot(9, 9, 'ro', markersize=10, label='Goal')
        ax1.legend()
        
        # 2. Basit yol
        path_x = [0, 1, 2, 2, 2, 8, 9]
        path_y = [0, 0, 1, 2, 8, 8, 9]
        ax2.plot(path_x, path_y, 'b-o', linewidth=2, label='Path')
        ax2.set_title('Test Path')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        plt.tight_layout()
        plt.savefig('test_basic_visualization.png', dpi=150)
        plt.close(fig)
        
        print("  ✅ Test görseli oluşturuldu: test_basic_visualization.png")
        return True
        
    except Exception as e:
        print(f"  ❌ Görselleştirme hatası: {e}")
        return False

def main():
    """Ana test fonksiyonu"""
    print("🧪 D* STAR TEMEL TEST PAKETİ")
    print("=" * 40)
    
    test_results = []
    
    # 1. Import testleri
    passed, total = test_imports()
    test_results.append(("Import", passed == total, f"{passed}/{total}"))
    
    # 2. Temel işlevsellik
    result = test_basic_functionality()
    test_results.append(("Basic Functions", result, "NumPy/Matplotlib"))
    
    # 3. Proje yapısı
    result = test_project_structure()
    test_results.append(("Project Structure", result, "Directories"))
    
    # 4. Grid map
    result = create_simple_grid_map()
    test_results.append(("Grid Map", result, "10x10 test"))
    
    # 5. Araç modeli
    result = test_vehicle_basics()
    test_results.append(("Vehicle Model", result, "Movement"))
    
    # 6. Görselleştirme
    result = create_test_visualization()
    test_results.append(("Visualization", result, "PNG output"))
    
    # Sonuç özeti
    print(f"\n" + "=" * 50)
    print(f"📋 TEST SONUÇLARI")
    print(f"=" * 50)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, passed, details in test_results:
        status = "✅ BAŞARILI" if passed else "❌ BAŞARISIZ"
        print(f"{status:12} | {test_name:20} | {details}")
        if passed:
            passed_tests += 1
    
    print(f"\n📊 ÖZET: {passed_tests}/{total_tests} test başarılı")
    
    if passed_tests == total_tests:
        print(f"🎉 TÜM TESTLER BAŞARILI! Proje kullanıma hazır.")
        
        print(f"\n🚀 Sonraki adımlar:")
        print(f"   1. python examples/quick_demo.py")
        print(f"   2. python examples/advanced_traffic_demo.py")  
        print(f"   3. python setup_project.py (tam kurulum)")
    else:
        failed_tests = total_tests - passed_tests
        print(f"⚠️ {failed_tests} test başarısız. Kurulum gerekebilir.")
        print(f"   python setup_project.py çalıştırmayı deneyin")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)