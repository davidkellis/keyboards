"""Refresh CAD provenance after routing only, requiring identical extracted geometry."""
from pathlib import Path
import json,subprocess
R=Path(__file__).resolve().parents[1];path=R/'case/board-geometry.json'
before=json.loads(path.read_text())
subprocess.run(['/usr/bin/python3',str(R/'scripts/export_geometry.py'),str(R)],check=True)
after=json.loads(path.read_text())
oldhash=before.pop('source_sha256');newhash=after.pop('source_sha256')
assert before==after,'Placements, holes or fit configuration changed: rebuild CAD'
fitpath=R/'case/fit-report.json';fit=json.loads(fitpath.read_text())
assert fit['source_sha256']==oldhash
fit['source_sha256']=newhash
fitpath.write_text(json.dumps(fit,indent=2)+'\n')
(R/'validation/fit-provenance-refresh.json').write_text(json.dumps(dict(
 cad_source_pcb_sha256=oldhash,routed_source_pcb_sha256=newhash,
 all_extracted_geometry_identical=True,method='Exact JSON comparison excluding PCB file hash; copper is not part of these mechanical meshes.'),indent=2)+'\n')
print('All extracted geometry identical; CAD provenance refreshed after routing.')
