"""Optional dataset regeneration: requires basemap-data, pyshp, pyproj, shapely, pandas, plotnine, pycountry.
Run `python tools/regenerate_expansion.py` then `python tools/build.py`.
Research-only: original-day questions stay untouched.
"""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parent
for name in ['expand_sources.py','switch_unesco_year.py','write_release_report.py','build.py']:
    subprocess.run([sys.executable,str(root/name)],check=True)
