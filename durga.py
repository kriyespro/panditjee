"""
durga.py — Clear cache and start Django dev server
Usage: python durga.py
       python durga.py --no-cache   (skip cache clearing)
"""
import os
import sys
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def clear_cache():
    patterns = ['__pycache__', '*.pyc', '.pytest_cache']
    removed = 0
    for root, dirs, files in os.walk(BASE_DIR):
        # Skip venv
        if 'venv' in root:
            continue
        for d in dirs:
            if d == '__pycache__' or d == '.pytest_cache':
                path = os.path.join(root, d)
                shutil.rmtree(path, ignore_errors=True)
                removed += 1
        for f in files:
            if f.endswith('.pyc'):
                os.remove(os.path.join(root, f))
                removed += 1
    print(f"🧹 Cache cleared ({removed} items removed)")

if __name__ == '__main__':
    skip_cache = '--no-cache' in sys.argv
    if not skip_cache:
        clear_cache()
    print("🚀 Starting Django dev server...")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    os.execv(
        os.path.join(BASE_DIR, 'venv', 'bin', 'python'),
        [os.path.join(BASE_DIR, 'venv', 'bin', 'python'),
         'manage.py', 'runserver']
    )
