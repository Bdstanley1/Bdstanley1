"""Actual torso-detail render coverage for garment boundaries and attachments."""
import base64
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageStat

POSES=['neutral','fashion','hip','walk','three-quarter']
VIEWS=['front','side','back']

def run_garment_closeups(page, root: Path, checks: dict) -> None:
    folder=root/'garment-closeups'
    folder.mkdir(exist_ok=True)
    page.evaluate("KR.reset();KR.view('front')")
    page.locator('#detail').click()
    records=[]
    for pose in POSES:
        for view in VIEWS:
            page.evaluate("(args)=>{KR.change('pose',args.pose);KR.view(args.view);KR.renderer.render(KR.scene,KR.camera)}", {'pose':pose,'view':view})
            state=page.evaluate("()=>({pose:KR.state.pose,view:KR.state.view,error:KR.renderer.getContext().getError()})")
            binding=page.evaluate("()=>{let found=false;KR.figure.traverse(o=>{if(o.isMesh&&o.visible&&o.name==='Bound neckline, armholes and hem')found=true});return found}")
            raw=base64.b64decode(page.evaluate("KR.renderer.domElement.toDataURL('image/png')").split(',',1)[1])
            name=f'{pose}-{view}.png'
            path=folder/name
            path.write_bytes(raw)
            image=Image.open(path).convert('RGB')
            if max(ImageStat.Stat(image).stddev)<2:
                checks['errors'].append('Uniform actual garment close-up: '+name)
            if state!={'pose':pose,'view':view,'error':0}:
                checks['errors'].append('Garment close-up state/WebGL failure: '+name)
            if not binding:
                checks['errors'].append('Garment binding mesh missing in actual close-up: '+name)
            records.append({'path':'garment-closeups/'+name,'sha256':hashlib.sha256(raw).hexdigest(),'pose':pose,'view':view,'pixel_size':list(image.size),'binding_mesh_visible':binding})
    sample=Image.open(root/records[0]['path']).convert('RGB')
    thumb_w=360
    thumb_h=round(sample.height*thumb_w/sample.width)
    cell_h=thumb_h+28
    atlas=Image.new('RGB',(thumb_w*3,cell_h*5),'white')
    draw=ImageDraw.Draw(atlas)
    for i,record in enumerate(records):
        x,y=(i%3)*thumb_w,(i//3)*cell_h
        frame=Image.open(root/record['path']).convert('RGB')
        frame.thumbnail((thumb_w,thumb_h))
        atlas.paste(frame,(x,y+28))
        draw.text((x+5,y+5),f"{record['pose']} {record['view']}",fill='black')
    atlas.save(root/'garment-closeups-rendered.png')
    (root/'garment-closeups-manifest.json').write_text(json.dumps(records,indent=2))
    checks['garment_closeups']={'executed_renders':len(records),'coverage':'exhaustive 5 implemented poses x 3 representative preset views at torso-detail framing','poses':POSES,'views':VIEWS,'evidence':records,'visual_approval':False,'physical_fit_validated':False,'physical_hardware':False,'limits':'Actual Chromium renders for human visual inspection; not collision-complete, physical-fit, cloth-mechanics, or physical-device validation.'}
    page.evaluate("KR.reset();KR.view('front')")
