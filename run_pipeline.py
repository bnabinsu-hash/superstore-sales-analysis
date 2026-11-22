"""Run the whole project end to end: clean -> load -> analyze."""
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent / "src"

for step in ["clean_data.py", "load_to_sqlite.py", "analysis.py"]:
    print(f"\n=== {step} ===")
    subprocess.run([sys.executable, str(SRC / step)], check=True)

print("\nDone. Charts are in images/, database is data/superstore.db")
