"""Build and test actual rendered outcomes; never equate a test pass with realism or fit approval."""
import base64
import hashlib
import html
import http.server
import importlib.metadata
import json
import pathlib
import shutil
import threading
from playwright.sync_api import sync_playwright
from build_runtime import ROOT, BASE, build, archive
from qa_extra import run_additional
from qa_footwear import run_footwear_closeups
from qa_garment import run_garment_closeups
from qa_hair import run_hair_closeups

RUNTIME=ROOT/'test-runtime'
q=RUNTIME/'qa'
if q.exists():
    if not (RUNTIME/'.knit-riot-generated').exists():
        raise RuntimeError('Refusing to erase an unmarked QA directory')
    shutil.rmtree(q)
report=build(RUNTIME)
q.mkdir(exist_ok=True)
checks={'visual_gate':'NOT_APPROVED','physical_fit':'NOT_VALIDATED','device_hardware_tested':False,'errors':[],'capture_errors':[],'cases':[],'app_sha256':report['app_sha256'],'build_report':report,'dependencies':{k:importlib.metadata.version(k) for k in ['playwright','Pillow']}}

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(RUNTIME),**kwargs)
    def log_message(self,*args):
        pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',8719),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()

def safe_screenshot(page,path):
    page.evaluate('KR.renderer.render(KR.scene,KR.camera)')
    try:
        page.screenshot(path=path,timeout=30000,animations='disabled')
        return
    except Exception as first_error:
        # Render's build host has occasionally stalled while Playwright waits on a
        # full-page screenshot even though WebGL remains responsive. Retry once
        # after a short settle; a successful retry is recorded, not hidden.
        page.wait_for_timeout(750)
        try:
            page.evaluate('KR.renderer.render(KR.scene,KR.camera)')
            page.screenshot(path=path,timeout=30000,animations='disabled')
            checks.setdefault('capture_retries',[]).append({'path':str(pathlib.Path(path).name),'first_error':str(first_error),'recovered':True})
            return
        except Exception as retry_error:
            checks['capture_errors'].append({'path':str(pathlib.Path(path).name),'first_error':str(first_error),'retry_error':str(retry_error)})
            try:
                image=page.evaluate('KR.renderer.domElement.toDataURL("image/png")')
                pathlib.Path(path).with_suffix('.canvas.png').write_bytes(base64.b64decode(image.split(',',1)[1]))
            except Exception as fallback_error:
                checks['errors'].append(str(fallback_error))

def store_sweep(summary):
    target=q/'sweep';target.mkdir(exist_ok=True)
    for i,frame in enumerate(summary.pop('frames',[])):
        data=base64.b64decode(frame.pop('png').split(',',1)[1])
        name=f'{i:03d}.png';(target/name).write_bytes(data)
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
        browser=pw.chromium.launch(headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
        checks['browser_version']=browser.version
        for label,width,height in [('desktop',1280,900),('phone',390,844)]:
            page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
            page.add_init_script('window.__qaPause=true')
            page.on('pageerror',lambda error:checks['errors'].append(str(error)))
            page.goto('http://127.0.0.1:8719/',wait_until='networkidle',timeout=60000)
            page.wait_for_function('window.KR && KR.ready',timeout=40000)
            if label=='desktop':
                labels=page.evaluate("()=>({zin:document.getElementById('zoomIn').textContent,zout:document.getElementById('zoomOut').textContent})")
                if labels!={'zin':'+','zout':'-'}:checks['errors'].append('Zoom controls are not using font-independent ASCII labels')
                distance0=page.evaluate('KR.camera.position.length()')
                page.locator('#zoomIn').click();distance1=page.evaluate('KR.camera.position.length()')
                page.locator('#zoomOut').click();distance2=page.evaluate('KR.camera.position.length()')
                checks['zoom_controls']={'labels':labels,'initial_distance':distance0,'after_zoom_in':distance1,'after_zoom_out':distance2,'rendered_label_check':True}
                if not (distance1 < distance0 and distance2 > distance1):checks['errors'].append('Zoom controls did not change camera distance in the required directions')
                page.evaluate('KR.reset();KR.view("front")')
            for pose in ['neutral','fashion','hip','walk','three-quarter']:
                for view in ['front','side','back']:
                    page.evaluate('([p,v])=>{KR.change("pose",p);KR.view(v)}',[pose,view])
                    safe_screenshot(page,str(q/f'{label}-{pose}-{view}.png'))
                result=page.evaluate('KR.runQA()');result.update(label=label,requested_pose=pose)
                checks['cases'].append(result)
            page.evaluate('KR.reset();KR.view("front")');page.locator('#detail').click()
            safe_screenshot(page,str(q/f'{label}-detail.png'));page.close()
        exec(compiled,globals())
        checks['coverage']={'discrete_controls':'all present values in each implemented button group','ranges':'minimum, maximum, default; state checks','cross_product':'7 size labels x 3 colors x 5 poses x 4 views; completed count recorded below','appearance_cross_product':'pairwise, not exhaustive','hardware':'software-rendered Chromium only','missing_implementation':['measurement-matched bust/waist/hip geometry','garment size grading geometry','validated cloth mechanics','photo reconstruction','Shopify integration']}
        from PIL import Image,ImageStat
        frames=checks['extended'].get('render_sweep',{}).get('rendered_frames',[])
        blank=[]
        for frame in frames:
            image=Image.open(q/frame['path']).convert('RGB')
            deviation=ImageStat.Stat(image).stddev;frame['rgb_standard_deviation']=deviation
            if max(deviation)<1:blank.append(frame['path'])
        checks['pixel_validation']={'frames_checked':len(frames),'near_uniform_frames':blank,'note':'Nonuniform pixels are not visual approval; inspect actual screenshots.'}
        if blank:checks['errors'].append('Uniform rendered frames detected')
        if len(frames)!=420:checks['errors'].append('420-frame sweep not completed')
        run_additional(browser,q,checks)
        footwear_page=browser.new_page(viewport={'width':1100,'height':900},device_scale_factor=1)
        footwear_page.add_init_script('window.__qaPause=true')
        footwear_page.on('pageerror',lambda error:checks['errors'].append(str(error)))
        footwear_page.goto('http://127.0.0.1:8719/',wait_until='networkidle',timeout=60000)
        footwear_page.wait_for_function('window.KR && KR.ready',timeout=40000)
        run_footwear_closeups(footwear_page,q,checks)
        footwear_page.close()
        garment_page=browser.new_page(viewport={'width':1100,'height':900},device_scale_factor=1)
        garment_page.add_init_script('window.__qaPause=true')
        garment_page.on('pageerror',lambda error:checks['errors'].append(str(error)))
        garment_page.goto('http://127.0.0.1:8719/',wait_until='networkidle',timeout=60000)
        garment_page.wait_for_function('window.KR && KR.ready',timeout=40000)
        run_garment_closeups(garment_page,q,checks)
        garment_page.close()
        hair_page=browser.new_page(viewport={'width':1100,'height':900},device_scale_factor=1)
        hair_page.add_init_script('window.__qaPause=true')
        hair_page.on('pageerror',lambda error:checks['errors'].append(str(error)))
        hair_page.goto('http://127.0.0.1:8719/',wait_until='networkidle',timeout=60000)
        hair_page.wait_for_function('window.KR && KR.ready',timeout=40000)
        run_hair_closeups(hair_page,q,checks)
        hair_page.close()
        if checks.get('footwear_closeups',{}).get('executed_renders')!=40:
            checks['errors'].append('40-frame exhaustive footwear close-up coverage incomplete')
        for case in checks.get('appearance_pairwise',{}).get('evidence',[]):
            image=Image.open(q/case['path']).convert('RGB')
            if max(ImageStat.Stat(image).stddev)<1:checks['errors'].append('Uniform pairwise render '+case['path'])
        page=browser.new_page(viewport={'width':390,'height':844})
        page.route('**/assets/body.json',lambda route:route.abort())
        page.goto('http://127.0.0.1:8719/',wait_until='networkidle',timeout=60000);page.wait_for_timeout(1200)
        checks['load_failure']={'core_mesh_blocked':True,'visible_error':page.locator('#error').is_visible(),'model_ready':page.evaluate('!!(window.KR && KR.ready)')}
        if not checks['load_failure']['visible_error'] or checks['load_failure']['model_ready']:checks['errors'].append('Essential mesh failure not surfaced correctly')
        page.close()
        page=browser.new_page(viewport={'width':390,'height':844})
        page.route('**/GLTFExporter.js',lambda route:route.abort())
        page.goto('http://127.0.0.1:8719/',wait_until='networkidle',timeout=60000)
        page.wait_for_function('window.KR && KR.ready',timeout=30000)
        page.evaluate("KR.setSheet('half')")
        page.locator('[data-tab="qa"]').click();page.locator('#export').click()
        page.wait_for_function("document.getElementById('qaResult').textContent.includes('Export could not finish:')",timeout=10000)
        checks['export_load_failure']={'visible_error':page.locator('#qaResult').is_visible(),'button_restored':page.locator('#export').is_enabled(),'model_still_ready':page.evaluate('KR.ready')}
        if not all(checks['export_load_failure'].values()):checks['errors'].append('Export failure recovery failed')
        page.close();browser.close()
    checks['execution_status']='completed'
except Exception as error:
    checks['execution_status']='incomplete';checks['errors'].append(str(error))
finally:
    server.shutdown()
    checks['release_status']='HOLD'
    (q/'results.json').write_text(json.dumps(checks,indent=2))
    inventory=[]
    for path in sorted(q.rglob('*')):
        if path.is_file():inventory.append({'path':str(path.relative_to(q)),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    (q/'evidence-manifest.json').write_text(json.dumps(inventory,indent=2))
    page_html='<h1>Actual rendered QA</h1><p>Development only. Appearance and physical fit are not approved. Software-rendered Chromium is not hardware validation.</p><pre>'+html.escape(json.dumps({k:v for k,v in checks.items() if k not in ['extended','appearance_pairwise']},indent=2))+'</pre>'
    for path in sorted(q.glob('*.png')):page_html+='<h2>'+html.escape(path.name)+'</h2><img style="max-width:100%" src="'+path.name+'">'
    (q/'index.html').write_text(page_html)
    archive(RUNTIME)
    print('ACTUAL_BROWSER_RESULTS '+json.dumps({k:v for k,v in checks.items() if k not in ['extended','appearance_pairwise']}),flush=True)
if checks['execution_status']!='completed' or checks['errors'] or checks['capture_errors'] or not checks.get('extended',{}).get('passed',False):
    raise SystemExit(1)
