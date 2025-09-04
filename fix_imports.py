import os
import re

def fix_python_file(filepath):
    """Python dosyasındaki import'ları düzelt"""
    
    if not os.path.exists(filepath):
        return False
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Yaygın import sorunlarını düzelt
    fixes = [
        # Missing imports
        (r'^from src\.dstar', 'from src.dstar.dstar_lite'),
        (r'^from src\.environment', 'from src.environment.grid_map'), 
        (r'^from src\.vehicle', 'from src.vehicle.vehicle_model'),
        (r'^from src\.visualization', 'from src.visualization.plotter'),
        
        # Path ayarlamaları
        (r"sys\.path\.append.*", """sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))""")
    ]
    
    modified = False
    for pattern, replacement in fixes:
        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        if new_content != content:
            content = new_content
            modified = True
    
    # Eksik import'ları ekle
    if 'import numpy as np' not in content and 'np.' in content:
        content = 'import numpy as np\n' + content
        modified = True
    
    if 'import matplotlib.pyplot as plt' not in content and 'plt.' in content:
        content = 'import matplotlib.pyplot as plt\n' + content  
        modified = True
        
    if 'import time' not in content and 'time.' in content:
        content = 'import time\n' + content
        modified = True
    
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def main():
    """Import düzeltmelerini çalıştır"""
    print("🔧 Import Sorunları Düzeltiliyor...")
    
    # Python dosyalarını bul ve düzelt
    python_files = []
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    fixed_files = 0
    for filepath in python_files:
        if fix_python_file(filepath):
            print(f"✅ Düzeltildi: {filepath}")
            fixed_files += 1
        else:
            print(f"ℹ️ Değişiklik gerekmedi: {filepath}")
    
    print(f"\n📊 Özet: {fixed_files}/{len(python_files)} dosya düzeltildi")
    
    if fixed_files > 0:
        print("🎉 Import sorunları düzeltildi!")
    else:
        print("✅ Tüm import'lar zaten doğru!")

if __name__ == "__main__":
    main()