"""Render entry point: test a pinned repository build, then publish only that candidate."""
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from build_runtime import assemble_app,archive

expected=os.environ['KR_EXPECTED_APP_SHA']
project_commit=os.environ['KR_PROJECT_COMMIT']
actual_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
if actual_commit!=project_commit:
    raise RuntimeError('Project checkout is not the authorized pinned commit')
app,_,_=assemble_app()
if hashlib.sha256(app.encode()).hexdigest()!=expected:
    raise RuntimeError('App differs from the CI-validated candidate; publication blocked')
subprocess.run([sys.executable,'-m','pip','install','-r',str(ROOT/'requirements-test.txt')],check=True,timeout=180)
subprocess.run([sys.executable,'-m','playwright','install','chromium','--only-shell'],check=True,timeout=240)
result=subprocess.run([sys.executable,str(ROOT/'tools/render_test.py')],cwd=ROOT,timeout=780)
runtime=ROOT/'test-runtime'
qa=json.loads((runtime/'qa/results.json').read_text())
report=json.loads((runtime/'BUILD_REPORT.json').read_text())
summary={'execution_status':qa.get('execution_status'),'errors':qa.get('errors'),'capture_errors':qa.get('capture_errors'),'rendered_combinations':qa.get('extended',{}).get('rendered_combinations',0),'extended_passed':qa.get('extended',{}).get('passed',False),'glb_geometry_roundtrip':qa.get('glb_geometry_roundtrip'),'appearance_pairwise_cases':qa.get('appearance_pairwise',{}).get('case_count',0),'physical_hardware_tested':False,'physical_fit':'NOT_VALIDATED','visual_gate':'NOT_APPROVED'}
from PIL import Image
for name in ['desktop-detail.png','phone-neutral-front.png']:
    path=runtime/'qa'/name
    if path.exists():
        image=Image.open(path).convert('RGB')
        if name.startswith('desktop'):image=image.crop((330,95,1260,855))
        image.thumbnail((420,560))
        buffer=io.BytesIO();image.save(buffer,format='WEBP',quality=65,method=6)
        raw=buffer.getvalue()
        print('RENDER_THUMB '+name+' SHA256 '+hashlib.sha256(raw).hexdigest()+' '+base64.b64encode(raw).decode(),flush=True)
if result.returncode or qa.get('execution_status')!='completed' or qa.get('errors') or qa.get('capture_errors') or not qa.get('extended',{}).get('passed') or report['app_sha256']!=expected:
    print('CANDIDATE_NOT_PUBLISHED '+json.dumps(summary),flush=True)
    raise RuntimeError('Candidate browser regression failed; keep the previous live deployment')
checkpoint=json.loads(os.environ.get('PROJECT_HANDOFF','{}'))
checkpoint.update(report)
checkpoint.update(build_status='functional_candidate_verified',deployment_status='build ready; Render live status must be checked separately',actual_browser_results=summary,release_status='HOLD',visual_gate='NOT_APPROVED',physical_fit='NOT_VALIDATED')
(runtime/'PROJECT_STATUS.json').write_text(json.dumps(checkpoint,indent=2))
(runtime/'PROJECT_HANDOFF.json').write_text(json.dumps(checkpoint,indent=2))
for name in ['build_runtime.py','render_test.py','qa_extra.py','render_build.py']:
    (runtime/('source-'+name+'.txt')).write_bytes((ROOT/'tools'/name).read_bytes())
(runtime/'source-BUILD_PY.txt').write_text(os.environ['BUILD_PY'])
(runtime/'source-EFFECTIVE_BROWSER_QA.txt').write_bytes((runtime/'qa/effective-browser-qa.py').read_bytes())
(runtime/'source-runtime-patches.json.txt').write_bytes((ROOT/'patches/runtime.json').read_bytes())
(runtime/'SOURCE_README.txt').write_text('Active implementation is the pinned Bdstanley1/Bdstanley1 repository under knit-riot-3d-garment. Build using tools/build_runtime.py and tools/render_test.py. Baseline environment-variable source exports are retained for provenance, not executed by this build. app.js is the actual assembled application. The old NAVER asset commit remains separately identified.\n')
archive(runtime)
publish=Path(os.environ['KR_PUBLISH_DIR']).resolve()
if publish.name!='public' or publish==ROOT or ROOT in publish.parents:
    raise RuntimeError('Refusing an unexpected publication directory')
if publish.exists():
    legacy=publish/'app.js'
    managed=(publish/'.knit-riot-generated').exists() or (legacy.is_file() and "const defaults={skin:" in legacy.read_text())
    if not managed:
        raise RuntimeError('Existing publication directory is not a recognized generated Knit Riot runtime')
    shutil.rmtree(publish)
shutil.copytree(runtime,publish)
print('ACTUAL_BROWSER_RESULTS '+json.dumps(summary),flush=True)
print('PROJECT_CHECKPOINT '+json.dumps(checkpoint),flush=True)
