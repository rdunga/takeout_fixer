# test_imports.py
from pathlib import Path
import sys

project_root = Path(__file__).parent
src_path = project_root / 'src'
print(f"Project root: {project_root}")
print(f"Src path: {src_path}")
print(f"Src exists: {src_path.exists()}")

sys.path.insert(0, str(src_path))

print(f"\nPython will look for imports in:")
for path in sys.path[:5]:  # Show first 5
    print(f"  - {path}")

print("\nTrying to import...")
try:
    from parsers.takeout_parser import TakeoutParser
    print("✅ Import successful!")
except ImportError as e:
    print(f"❌ Import failed: {e}")