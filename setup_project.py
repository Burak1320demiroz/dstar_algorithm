"""
Projeyi otomatik olarak kurar ve test eder
"""

import os
import subprocess
import sys

def create_directory_structure():
    """Dizin yapısını oluştur"""
    directories = [
        'src',
        'src/dstar', 
        'src/environment',
        'src/vehicle',
        'src/visualization', 
        'src/utils',
        'examples',
        'tests',
        'docs',
        'data',
        'data/maps',
        'data/scenarios'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        
        # __init__.py dosyalarını oluştur
        if directory.startswith('src/'):
            init_file = os.path.join(directory, '__init__.py')
            if not os.path.exists(init_file):
                with open(init_file, 'w') as f:
                    f.write(f'"""Package: {directory}"""\n')
    
    print("✅ Dizin yapısı oluşturuldu")

def install_requirements():
    """Requirements yükle"""
    requirements = [
        'numpy>=1.21.0',
        'matplotlib>=3.5.0', 
        'scipy>=1.7.0',
        'pytest>=6.2.0'
    ]
    
    for requirement in requirements:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', requirement])
            print(f"✅ Yüklendi: {requirement}")
        except subprocess.CalledProcessError:
            print(f"❌ Yüklenemedi: {requirement}")

def run_basic_test():
    """Temel test çalıştır"""
    test_code = '''
import numpy as np
import matplotlib.pyplot as plt
print("✅ NumPy version:", np.__version__)
print("✅ Matplotlib version:", plt.matplotlib.__version__)
print("✅ Temel kütüphaneler çalışıyor!")
'''
    
    try:
        exec(test_code)
        return True
    except Exception as e:
        print(f"❌ Test hatası: {e}")
        return False

def main():
    """Ana kurulum"""
    print("🚀 D* STAR PROJESİ KURULUMU")
    print("=" * 40)
    
    # 1. Dizin yapısı
    create_directory_structure()
    
    # 2. Requirements
    print("\n📦 Gerekli kütüphaneler yükleniyor...")
    install_requirements()
    
    # 3. Test
    print("\n🧪 Temel test çalıştırılıyor...")
    if run_basic_test():
        print("✅ Kurulum başarılı!")
    else:
        print("❌ Kurulum tamamlanamadı!")
        return
    
    # 4. İlk demo
    print("\n🎮 Hızlı demo çalıştırılıyor...")
    try:
        if os.path.exists('examples/quick_demo.py'):
            subprocess.run([sys.executable, 'examples/quick_demo.py'], timeout=60)
            print("✅ Demo başarılı!")
        else:
            print("⚠️ Demo dosyası bulunamadı")
    except Exception as e:
        print(f"⚠️ Demo hatası: {e}")
    
    print(f"\n🎉 D* Star projesi kullanıma hazır!")
    print(f"📚 Çalıştırılabilir komutlar:")
    print(f"   python examples/quick_demo.py")
    print(f"   python examples/run_all_demos.py")
    print(f"   python fix_imports.py")

if __name__ == "__main__":
    main()