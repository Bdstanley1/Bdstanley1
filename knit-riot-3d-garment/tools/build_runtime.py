"""Build the real fitting-room runtime from immutable, checksum-verified sources.
No downloads, credentials, customer data, or production-store access are needed.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import zipfile
from catalog_contract import load_and_validate_catalog

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'recovered/2026-09-30'
FIXTURE = ROOT / 'fixtures/runtime'
CATALOG = ROOT / 'research/contracts/development-catalog.json'


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def assemble_app() -> tuple[str, str, str]:
    app = (BASE/'app.js').read_text()
    old_refine = (BASE/'source-REFINE_JS.txt').read_text()
    refine = (ROOT/'patches/refine.js').read_text()+'\n'+old_refine[old_refine.index('function addSkinDetail'):]
    old_clip = (BASE/'source-CLIP_JS.txt').read_text()
    clip = old_clip[:old_clip.index('function maskCoveredBody')]+(ROOT/'patches/mask.js').read_text()
    for before, after in [(old_refine, refine), (old_clip, clip)]:
        if app.count(before) != 1:
            raise ValueError('Expected exactly one pristine repair context')
        app = app.replace(before, after)
    footwear_before="boots=skinned('White slip-on shoes',clipSubset(m,[(x,y)=>H*.067-y],.006),new T.MeshStandardMaterial({color:'#eae7df',roughness:.72,side:T.DoubleSide}));"
    footwear=(ROOT/'patches/footwear.js').read_text().strip()
    if app.count(footwear_before) != 1:
        raise ValueError('Expected exactly one pristine footwear context')
    app=app.replace(footwear_before,footwear)
    for extra in [ROOT/'patches/runtime.json', ROOT/'patches/interaction.json', ROOT/'patches/framing.json']:
        if extra.exists():
            for patch in json.loads(extra.read_text()):
                before, after = patch['before'], patch['after']
                if app.count(before) != patch.get('count', 1):
                    raise ValueError('Runtime patch context mismatch: '+patch.get('name', before[:60]))
                app = app.replace(before, after)
    return app, refine, clip


def build(destination: Path) -> dict:
    destination = destination.resolve()
    manifest = json.loads((FIXTURE/'FIXTURE_MANIFEST.json').read_text())
    verified = []
    # Validate all inputs before writing any runtime file.
    for record in manifest['files']:
        path = PurePosixPath(record['path'])
        if path.is_absolute() or '..' in path.parts:
            raise ValueError('Unsafe fixture path')
        data = (FIXTURE/path).read_bytes()
        if len(data) != record['bytes'] or sha(data) != record['sha256']:
            raise ValueError('Fixture checksum mismatch: '+str(path))
        verified.append((path, data))
    catalog = load_and_validate_catalog(CATALOG)
    app, refine, clip = assemble_app()
    subprocess.run(['node','--input-type=module','--check'],input=app,text=True,check=True)
    destination.mkdir(parents=True, exist_ok=True)
    for path, data in verified:
        target = destination/path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    index = (BASE/'index.html').read_text()
    zoom_before = '<button id="zoomIn" aria-label="Zoom in">＋</button><button id="zoomOut" aria-label="Zoom out">−</button>'
    zoom_after = '<button id="zoomIn" aria-label="Zoom in">+</button><button id="zoomOut" aria-label="Zoom out">-</button>'
    if index.count(zoom_before) != 1:
        raise ValueError('Expected exactly one pristine zoom-control label context')
    index = index.replace(zoom_before, zoom_after)
    style_anchor = '</style><script type="importmap">'
    mobile_css = '@media(max-width:800px){#zoomIn,#zoomOut{display:none}}'
    if index.count(style_anchor) != 1:
        raise ValueError('Expected exactly one style/importmap context')
    index = index.replace(style_anchor, mobile_css+style_anchor)
    (destination/'index.html').write_text(index)
    (destination/'app.js').write_text(app)
    (destination/'REFINE_JS.txt').write_text(refine)
    (destination/'CLIP_JS.txt').write_text(clip)
    (destination/'app-source.html').write_text('<pre>'+html.escape(app)+'</pre>')
    (destination/'robots.txt').write_text('User-agent: *\nDisallow: /\n')
    (destination/'catalog').mkdir(exist_ok=True)
    (destination/'catalog/development-catalog.json').write_text(json.dumps(catalog,indent=2)+'\n')
    project_commit = os.environ.get('KR_PROJECT_COMMIT')
    if not project_commit:
        project_commit = subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,text=True,capture_output=True).stdout.strip() or 'local-uncommitted'
    report = {
        'project_commit':project_commit,
        'upstream_asset_commit':'d6fc027ced5c17b6b0775dee944096ade7a9ef80',
        'baseline_app_sha256':sha((BASE/'app.js').read_bytes()),
        'app_sha256':sha(app.encode()),
        'verified_fixture_files':len(verified),
        'fixture_manifest_sha256':sha((FIXTURE/'FIXTURE_MANIFEST.json').read_bytes()),
        'catalog_contract_sha256':sha(CATALOG.read_bytes()),
        'catalog_items':len(catalog['items']),
        'catalog_release_status':catalog.get('release_status','HOLD'),
        'release_status':'HOLD',
        'visual_gate':'NOT_APPROVED',
        'physical_fit':'NOT_VALIDATED',
    }
    (destination/'BUILD_REPORT.json').write_text(json.dumps(report,indent=2))
    (destination/'PROJECT_STATUS.json').write_text(json.dumps(report,indent=2))
    for path in BASE.glob('source-*.txt'):
        (destination/path.name).write_bytes(path.read_bytes())
    (destination/'source-REFINE_JS.txt').write_text(refine)
    (destination/'source-CLIP_JS.txt').write_text(clip)
    (destination/'source-FOOTWEAR_JS.txt').write_bytes((ROOT/'patches/footwear.js').read_bytes())
    for patch_name in ['runtime.json','interaction.json','framing.json']:
        patch_path=ROOT/'patches'/patch_name
        if patch_path.exists():
            (destination/('source-'+patch_name)).write_bytes(patch_path.read_bytes())
    (destination/'source-build_runtime.py.txt').write_bytes(Path(__file__).read_bytes())
    (destination/'.knit-riot-generated').write_text('Build output only; never store customer data here.\n')
    return report


def archive(destination: Path) -> None:
    with zipfile.ZipFile(destination/'development-snapshot.zip','w',zipfile.ZIP_DEFLATED) as out:
        for path in sorted(destination.rglob('*')):
            if path.is_file() and path.name != 'development-snapshot.zip':
                out.write(path,path.relative_to(destination))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=ROOT/'test-runtime')
    args = parser.parse_args()
    result = build(args.output)
    archive(args.output)
    print('BUILD_RUNTIME '+json.dumps(result),flush=True)
