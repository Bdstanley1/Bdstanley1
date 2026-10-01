"""Rebuild the recovered runtime, apply reviewed repairs once, and test real renders.
This suite reports completed coverage separately from appearance/physical-fit approval.
"""
import base64
import hashlib
import http.server
import io
import json
import pathlib
import shutil
import subprocess
import threading
import time
import urllib.request
import zipfile
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = ROOT / 'recovered/2026-09-30'
RUNTIME = ROOT / 'test-runtime'
RUNTIME.mkdir(exist_ok=True)
q = RUNTIME / 'qa'
q.mkdir(exist_ok=True)
checks = {'visual_gate':'NOT_APPROVED','physical_fit':'NOT_VALIDATED','device_hardware_tested':False,'errors':[],'capture_errors':[],'cases':[]}
URL = 'https://knit-riot-studio-development.onrender.com/development-snapshot.zip'
for attempt in range(3):
    try:
        with urllib.request.urlopen(URL, timeout=90) as response:
            raw = response.read(96*1024*1024+1)
        assert hashlib.sha256(raw).hexdigest() == '141fe99b2fa7dfddd46469da2b00a50d7767be31741ad32dd9c3156c47f9b0bb', 'Review changed staging snapshot before using it'
        break
    except Exception:
        if attempt == 2:
            raise
        time.sleep(10)
libs = {'three.module.js','OrbitControls.js','GLTFExporter.js','BufferGeometryUtils.js','THREE-LICENSE.txt','TextureUtils.js','RGBELoader.js','GLTFLoader.js'}
assets = {'body.json','leye.json','reye.json','skin.png','hair.png','hair.json','studio_small_08_1k.hdr'}
manifest = json.loads((BASE/'asset-manifest.json').read_text())
with zipfile.ZipFile(io.BytesIO(raw)) as archive:
    for name in sorted(libs | {'assets/'+n for n in assets}):
        data = archive.read(name)
        if name.startswith('assets/'):
            assert hashlib.sha256(data).hexdigest() == manifest['files'][pathlib.Path(name).name]['sha256']
        destination = RUNTIME/name
        destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_bytes(data)
for name in ['index.html','ATTRIBUTION.txt','asset-manifest.json']:
    shutil.copyfile(BASE/name,RUNTIME/name)
app = (BASE/'app.js').read_text()
old_refine = (BASE/'source-REFINE_JS.txt').read_text()
new_refine = (ROOT/'patches/refine.js').read_text()+'\n'+old_refine[old_refine.index('function addSkinDetail'):]
old_clip = (BASE/'source-CLIP_JS.txt').read_text()
new_clip = old_clip[:old_clip.index('function maskCoveredBody')]+(ROOT/'patches/mask.js').read_text()
for old,new in [(old_refine,new_refine),(old_clip,new_clip)]:
    assert app.count(old) == 1, 'Repair context changed or patch already applied'
    app = app.replace(old,new)
(RUNTIME/'app.js').write_text(app)
(RUNTIME/'REFINE_JS.txt').write_text(new_refine)
(RUNTIME/'CLIP_JS.txt').write_text(new_clip)
subprocess.run(['node','--input-type=module','--check'],input=app,text=True,check=True)
checks['app_sha256'] = hashlib.sha256(app.encode()).hexdigest()
checks['baseline_sha256'] = hashlib.sha256((BASE/'app.js').read_bytes()).hexdigest()

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(RUNTIME),**kwargs)
    def log_message(self,*args):
        pass
server = http.server.ThreadingHTTPServer(('127.0.0.1',8719),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()

def safe_screenshot(page,path):
    """A capture failure remains a failure but cannot erase later test coverage."""
    try:
        page.evaluate('KR.renderer.render(KR.scene,KR.camera)')
        page.screenshot(path=path,timeout=30000,animations='disabled')
    except Exception as error:
        checks['capture_errors'].append({'path':str(pathlib.Path(path).name),'error':str(error)})
        try:
            image = page.evaluate('KR.renderer.domElement.toDataURL("image/png")')
            pathlib.Path(path).with_suffix('.canvas.png').write_bytes(base64.b64decode(image.split(',',1)[1]))
        except Exception as fallback_error:
            checks['errors'].append(str(fallback_error))

def store_sweep(summary):
    target=q/'sweep'
    target.mkdir(exist_ok=True)
    for i,frame in enumerate(summary.pop('frames',[])):
        data=base64.b64decode(frame.pop('png').split(',',1)[1])
        name=f'{i:03d}.png'
        (target/name).write_bytes(data)
        frame.update(path='sweep/'+name,sha256=hashlib.sha256(data).hexdigest())
        summary.setdefault('rendered_frames',[]).append(frame)

try:
    code=(BASE/'source-EFFECTIVE_BROWSER_QA.txt').read_text()
    code=code.replace('page.set_default_timeout(6000)','page.set_default_timeout(30000)')
    code=code.replace('page.screenshot(path=','safe_screenshot(page,path=')
    code=code.replace('const result={count:0,errors:[],resolution:[160,240]}','const result={count:0,errors:[],frames:[],resolution:[160,240]}')
    code=code.replace('result.count++;',"result.frames.push({size:s,color:c,pose:p,view:v,png:KR.renderer.domElement.toDataURL('image/png')});result.count++;")
    code=code.replace("extended['render_sweep']=summary", "extended['render_sweep']=summary;store_sweep(summary)")
    compiled=compile(code,'extended_browser_qa.py','exec')
    (q/'effective-browser-qa.py').write_text(code)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
        checks['browser_version']=browser.version
        for label,width,height in [('desktop',1280,900),('phone',390,844)]:
            page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
            page.add_init_script('window.__qaPause=true')
            page.on('pageerror',lambda error:checks['errors'].append(str(error)))
            page.goto('http://127.0.0.1:8719/',wait_until='networkidle',timeout=60000)
            page.wait_for_function('window.KR && KR.ready',timeout=40000)
            for pose in ['neutral','fashion','hip','walk','three-quarter']:
                for view in ['front','side','back']:
                    page.evaluate('([p,v])=>{KR.change("pose",p);KR.view(v)}',[pose,view])
                    safe_screenshot(page,str(q/f'{label}-{pose}-{view}.png'))
                result=page.evaluate('KR.runQA()')
                result.update(label=label,requested_pose=pose)
                checks['cases'].append(result)
            page.evaluate('KR.reset();KR.view("front")')
            page.locator('#detail').click()
            safe_screenshot(page,str(q/f'{label}-detail.png'))
            page.close()
        exec(compiled,globals())
        checks['coverage']={'discrete_controls':'all present values in each implemented button group','ranges':'minimum, maximum, default; state checks','cross_product':'7 size labels x 3 colors x 5 poses x 4 views, all 420 rendered frames archived','appearance_cross_product':'not exhaustive','hardware':'software-rendered Chromium only','missing_implementation':['measurement-matched bust/waist/hip geometry','garment size grading geometry','validated cloth mechanics','photo reconstruction','Shopify integration']}
        from PIL import Image, ImageStat
        frames=checks['extended'].get('render_sweep',{}).get('rendered_frames',[])
        blank=[]
        for frame in frames:
            image=Image.open(q/frame['path']).convert('RGB')
            deviation=ImageStat.Stat(image).stddev
            frame['rgb_standard_deviation']=deviation
            if max(deviation)<1:
                blank.append(frame['path'])
        checks['pixel_validation']={'frames_checked':len(frames),'near_uniform_frames':blank,'note':'Nonuniform pixels are not visual approval; see archived actual screenshots'}
        if blank:
            checks['errors'].append('Uniform rendered frames detected')
        if len(frames)!=420:
            checks['errors'].append('420-frame sweep not completed')
        page=browser.new_page(viewport={'width':390,'height':844})
        page.route('**/assets/body.json',lambda route:route.abort())
        page.goto('http://127.0.0.1:8719/',wait_until='networkidle',timeout=60000)
        page.wait_for_timeout(1200)
        checks['load_failure']={'core_mesh_blocked':True,'visible_error':page.locator('#error').is_visible(),'model_ready':page.evaluate('!!(window.KR && KR.ready)')}
        if not checks['load_failure']['visible_error'] or checks['load_failure']['model_ready']:
            checks['errors'].append('Essential mesh failure was not surfaced correctly')
        page.close()
        browser.close()
    checks['execution_status']='completed'
except Exception as error:
    checks['execution_status']='incomplete'
    checks['errors'].append(str(error))
finally:
    server.shutdown()
    checks['release_status']='HOLD'
    (q/'results.json').write_text(json.dumps(checks,indent=2))
    inventory=[]
    for path in sorted(q.rglob('*')):
        if path.is_file():
            inventory.append({'path':str(path.relative_to(q)),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    (q/'evidence-manifest.json').write_text(json.dumps(inventory,indent=2))
    print('ACTUAL_BROWSER_RESULTS '+json.dumps({k:v for k,v in checks.items() if k!='extended'}),flush=True)
if checks['execution_status']!='completed' or checks['errors'] or checks['capture_errors'] or not checks.get('extended',{}).get('passed',False):
    raise SystemExit(1)
