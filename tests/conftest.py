import sys
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "loop-craft" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
