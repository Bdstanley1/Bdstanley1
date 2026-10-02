"""Actual close-up footwear render coverage; synthetic fixture, not physical fit."""
import base64
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageStat

POSES = ['neutral', 'fashion', 'hip', 'walk', 'three-quarter']
VIEWS = {'front': [0, .22, 1], 'side': [1, .16, 0],
         'back': [0, .22, -1], 'above-front': [.35, .95, 1]}


def run_footwear_closeups(page, root: Path, checks: dict) -> None:
    folder = root / 'footwear-closeups'
    folder.mkdir(exist_ok=True)
    page.evaluate('''()=>{
      window.__footwearRenderRestore={ratio:KR.renderer.getPixelRatio(),
        width:KR.renderer.domElement.width/KR.renderer.getPixelRatio(),
        height:KR.renderer.domElement.height/KR.renderer.getPixelRatio(),
        aspect:KR.camera.aspect,suppress:window.__suppressDraw};
      window.__suppressDraw=true;
    }''')
    records = []
    digests = {}
    try:
        for shoe in ['slip-ons', 'barefoot']:
            for pose in POSES:
                for view, direction in VIEWS.items():
                    result = page.evaluate('''async (args)=>{
                      const T=await import('three');
                      KR.reset();KR.change('shoes',args.shoe);KR.change('pose',args.pose);
                      KR.figure.updateMatrixWorld(true);
                      const box=new T.Box3(),p=new T.Vector3();let vertices=0;
                      // Include hidden shoe geometry to keep both choices identically framed.
                      KR.figure.traverse(o=>{
                        if(!o.isMesh||!o.name.startsWith('White slip-on '))return;
                        if(o.skeleton)o.skeleton.update();
                        for(let i=0;i<o.geometry.attributes.position.count;i++){
                          o.getVertexPosition(i,p);o.localToWorld(p);box.expandByPoint(p);vertices++;
                        }
                      });
                      if(!vertices||box.isEmpty())throw Error('No footwear geometry for actual close-up QA');
                      const center=box.getCenter(new T.Vector3()),size=box.getSize(new T.Vector3());
                      const distance=size.length()*.58/Math.sin(KR.camera.fov*Math.PI/360);
                      KR.renderer.setPixelRatio(1);KR.renderer.setSize(720,480,false);
                      KR.camera.aspect=1.5;KR.camera.updateProjectionMatrix();
                      KR.camera.position.copy(center).add(new T.Vector3(...args.direction).normalize().multiplyScalar(distance));
                      KR.camera.lookAt(center);KR.camera.updateMatrixWorld(true);
                      KR.renderer.render(KR.scene,KR.camera);
                      return {png:KR.renderer.domElement.toDataURL('image/png'),
                        webglError:KR.renderer.getContext().getError(),vertices,
                        state:{shoes:KR.state.shoes,pose:KR.state.pose},
                        bounds:{min:box.min.toArray(),max:box.max.toArray()}};
                    }''', {'shoe': shoe, 'pose': pose, 'direction': direction})
                    data = base64.b64decode(result.pop('png').split(',', 1)[1])
                    name = f'{shoe}-{pose}-{view}.png'
                    (folder / name).write_bytes(data)
                    image = Image.open(folder / name).convert('RGB')
                    if image.size != (720, 480) or max(ImageStat.Stat(image).stddev) < 2:
                        checks['errors'].append('Invalid or uniform actual footwear close-up: ' + name)
                    if result['webglError'] or result['state'] != {'shoes': shoe, 'pose': pose}:
                        checks['errors'].append('Footwear close-up state/WebGL failure: ' + name)
                    digest = hashlib.sha256(data).hexdigest()
                    digests[(shoe, pose, view)] = digest
                    records.append({'path': 'footwear-closeups/' + name, 'sha256': digest,
                                    'shoe': shoe, 'pose': pose, 'view': view, **result})
        for pose in POSES:
            for view in VIEWS:
                if digests[('slip-ons', pose, view)] == digests[('barefoot', pose, view)]:
                    checks['errors'].append('Footwear choices rendered identically: ' + pose + '/' + view)
        atlas = Image.new('RGB', (720 * 4, 508 * 10), 'white')
        draw = ImageDraw.Draw(atlas)
        for i, record in enumerate(records):
            x, y = (i % 4) * 720, (i // 4) * 508
            atlas.paste(Image.open(root / record['path']).convert('RGB'), (x, y + 28))
            draw.text((x + 8, y + 6), record['shoe'] + ' / ' + record['pose'] + ' / ' + record['view'], fill='black')
        atlas.save(root / 'footwear-closeups-rendered.png')
        (root / 'footwear-closeups-manifest.json').write_text(json.dumps(records, indent=2))
        checks['footwear_closeups'] = {'executed_renders': len(records),
            'coverage': 'exhaustive 2 footwear choices x 5 existing poses x 4 close-up camera directions',
            'resolution': [720, 480], 'evidence': records,
            'visual_approval': False, 'physical_fit_validated': False,
            'limits': 'Image/state checks detect missing effects; actual visual inspection remains required.'}
    finally:
        page.evaluate('''()=>{
          const r=window.__footwearRenderRestore;
          KR.renderer.setPixelRatio(r.ratio);KR.renderer.setSize(r.width,r.height,false);
          KR.camera.aspect=r.aspect;KR.camera.updateProjectionMatrix();
          window.__suppressDraw=r.suppress;KR.reset();
          delete window.__footwearRenderRestore;
        }''')
