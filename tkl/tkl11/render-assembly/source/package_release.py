#!/usr/bin/env python3
"""Collect passed viewer checks and package the offline studio, not fabrication files."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[1];REPO=R.parents[2]
reports={s:json.loads((R/(s+'-validation.json')).read_text()) for s in ['validate','capture','stack','exports']}
assert all(r['passed'] and not r['errors'] and not r['network'] for r in reports.values())
manifest=json.loads((R/'provenance.json').read_text())
assert all(hashlib.sha256((REPO/name).read_bytes()).hexdigest()==sha for name,sha in manifest['source_sha256'].items())
result=dict(passed=True,offline=True,html_sha256=hashlib.sha256((R/'index.html').read_bytes()).hexdigest(),
 combinations_checked=len(reports['validate']['combinations']),keys=86,leds=10,
 source_files_verified_unchanged=len(manifest['source_sha256']),
 checks=[c for r in reports.values() for c in r['checks']],reports={s:s+'-validation.json' for s in reports},
 mechanical_fit_verified=False,photometric_simulation=False)
(R/'browser-validation.json').write_text(json.dumps(result,indent=2)+'\n')
files=['index.html','README.md','ATTRIBUTIONS.md','THREE-LICENSE.txt','provenance.json','browser-validation.json',
 'studio-preview.png','exploded-preview.png','v11-assembled.png','v11-exploded.png',
 'reference/ScottoCaps-LICENSE.md','reference/CPG1353S01D02-01-datasheet.pdf',
 *[s+'-validation.json' for s in reports]]
target=R/'tkl-v11-assembly-studio.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
 for name in files:z.write(R/name,name)
with zipfile.ZipFile(target) as z:
 assert z.testzip() is None
 for name in files:assert z.read(name)==(R/name).read_bytes(),name
print('Packaged',target.name,target.stat().st_size,'bytes;',result['combinations_checked'],'combinations;',len(result['checks']),'checks')
