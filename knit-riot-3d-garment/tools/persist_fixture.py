"""Persist only the already verified, allow-listed synthetic fixture and dependencies."""
import hashlib
import json
from pathlib import Path

root = Path('recovery')
project = Path('knit-riot-3d-garment')
destination = project / 'fixtures/runtime'
report = json.loads((root/'RECOVERY_MANIFEST.json').read_text())
records = {entry['path']:entry for entry in report['files']}
assets = {'body.json','leye.json','reye.json','skin.png','hair.png','hair.json','studio_small_08_1k.hdr'}
libraries = {'three.module.js','OrbitControls.js','GLTFExporter.js','BufferGeometryUtils.js','THREE-LICENSE.txt','TextureUtils.js','RGBELoader.js','GLTFLoader.js'}
allowed = libraries | {'assets/'+name for name in assets} | {'asset-manifest.json','ATTRIBUTION.txt'}
manifest = {'snapshot_sha256':report['snapshot_sha256'],'kind':'synthetic adult female fixture, not customer data','files':[]}
for name in sorted(allowed):
    data = (root/name).read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    assert digest == records[name]['sha256'], 'Recovery checksum changed'
    target = destination/name
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():
        assert target.read_bytes() == data, 'Refusing to overwrite immutable fixture'
    else:
        target.write_bytes(data)
    manifest['files'].append({'path':name,'bytes':len(data),'sha256':digest})
(destination/'FIXTURE_MANIFEST.json').write_text(json.dumps(manifest,indent=2))
print('Verified and persisted',len(manifest['files']),'licensed fixture/dependency files')
