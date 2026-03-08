#!/usr/bin/env python3
"""初回セットアップを一括実行"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
scripts = [
    "seed_chains.py",
    "seed_restaurants.py",
    "migrate_nutrition.py",
    "update_menu_nutrition.py",
]
for s in scripts:
    p = ROOT / "scripts" / s
    if p.exists():
        print(f"Running {s}...")
        r = subprocess.run([sys.executable, str(p)], cwd=str(ROOT))
        if r.returncode != 0:
            sys.exit(r.returncode)
print("Setup complete.")
