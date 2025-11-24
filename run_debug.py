import sys
from pathlib import Path
backend_dir = Path(__file__).resolve().parent / 'backend'
print('Adding to sys.path:', backend_dir)
sys.path.insert(0, str(backend_dir))
from backend.scripts.debug_category import *
