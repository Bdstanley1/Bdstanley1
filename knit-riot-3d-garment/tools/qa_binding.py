"""Capture durable actual-render evidence for vest bindings across every implemented pose and camera preset."""
import base64
import hashlib
import pathlib
from PIL import Image, ImageStat

POSES=('neutral','fashion','hip','walk','three-quarter')
VIEWS=('front','side','back')

def run_binding_closeups(page, qa_dir, checks):
    target=pathlib.Path(qa_dir)/'binding-closeups'
    target.mkdir(exist_ok=True)
    evidence=[]
    for pose in POSES:
        for view in VIEWS:
            page.evaluate('([p,v])=>{KR.change("pose",p);KR.view(v)}',[pose,view])
            page.locator('#detail').click()
            page.evaluate('KR.renderer.render(KR.scene,KR.camera)')
            data=page.evaluate('KR.renderer.domElement.toDataURL("image/png")')
            raw=base64.b64decode(data.split(',',1)[1])
            name=f'{pose}-{view}.png'
            path=target/name
            path.write_bytes(raw)
            image=Image.open(path).convert('RGB')
            deviation=ImageStat.Stat(image).stddev
            evidence.append({
                'path':'binding-closeups/'+name,
                'sha256':hashlib.sha256(raw).hexdigest(),
                'rgb_standard_deviation':deviation,
                'nonuniform':max(deviation)>=1
            })
    checks['binding_closeups']={
        'coverage':'exhaustive 5 implemented poses x 3 front/side/back camera presets',
        'executed_renders':len(evidence),
        'hardware':'software-rendered Chromium only',
        'evidence':evidence
    }
    if len(evidence)!=15:
        checks['errors'].append('15-frame exhaustive binding close-up coverage incomplete')
    if any(not item['nonuniform'] for item in evidence):
        checks['errors'].append('Uniform binding close-up renders detected')
