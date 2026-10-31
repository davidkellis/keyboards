#!/usr/bin/env python3
"""Build this revision using the shared CadQuery generator."""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parents[1]
shared=root.parent/'mechanical'
subprocess.run(['/usr/bin/python3',str(root/'scripts/export_geometry.py'),str(root)],check=True)
subprocess.run([sys.executable,str(shared/'build_fit.py'),str(root)],check=True)
subprocess.run([sys.executable,str(shared/'build_stabilizer_coupon.py'),str(root)],check=True)
