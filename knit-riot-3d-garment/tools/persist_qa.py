"""Preserve only synthetic app-test evidence; never consume customer import folders."""
import hashlib
import json
import os
from pathlib import Path
import shutil
from PIL import Image,ImageDraw

root=Path(__file__).resolve().parents[1]
source=root/'test-runtime/qa'
result=json.loads((source/'results.json').read_text())
assert result['execution_status']=='completed' and not result['errors'] and not result['capture_errors']
assert result['extended']['passed'] and result['extended']['rendered_combinations']==420
out=root/'validation/latest'
out.mkdir(parents=True,exist_ok=True)
for name in ['results.json','evidence-manifest.json','desktop-detail.png','desktop-neutral-front.png','desktop-neutral-side.png','desktop-neutral-back.png','desktop-hip-front.png','phone-neutral-front.png','glb-original.png','glb-reloaded-front.png','glb-reloaded-detail.png','footwear-slip-ons.png','footwear-slip-ons-side.png','footwear-barefoot.png','footwear-barefoot-side.png']:
    shutil.copyfile(source/name,out/name)

def atlas(records,name,columns,width,height):
    rows=(len(records)+columns-1)//columns
    image=Image.new('RGB',(columns*width,rows*(height+24)),'white')
    draw=ImageDraw.Draw(image)
    for i,record in enumerate(records):
        path=source/record['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==record['sha256']
        tile=Image.open(path).convert('RGB')
        assert tile.size==(width,height), 'Unexpected render size: '+record['path']
        x=(i%columns)*width;y=(i//columns)*(height+24)
        image.paste(tile,(x,y+24));draw.text((x+3,y+3),str(i)+' '+record['path'],fill='black')
    image.save(out/name)

atlas(result['extended']['render_sweep']['rendered_frames'],'all-420-rendered-cases.png',20,160,240)
atlas(result['appearance_pairwise']['evidence'],'appearance-pairwise-rendered.png',8,240,360)
metadata={'tested_commit':os.environ['GITHUB_SHA'],'workflow_run_id':os.environ['GITHUB_RUN_ID'],'app_sha256':result['app_sha256'],'release_status':'HOLD','visual_approval':False,'physical_fit_validated':False,'hardware_tested':False,'files':[]}
for path in sorted(out.iterdir()):
    if path.is_file() and path.name!='PROVENANCE.json':metadata['files'].append({'path':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size})
(out/'PROVENANCE.json').write_text(json.dumps(metadata,indent=2))
print('Persisted verified actual-render evidence for',metadata['tested_commit'])
