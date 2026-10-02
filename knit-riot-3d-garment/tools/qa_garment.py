"""Actual close-up garment-boundary render coverage; synthetic fixture, not physical fit."""
import base64
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageStat

POSES = ['neutral', 'fashion', 'hip', 'walk', 'three-quarter']
VIEWS = {'front': [0, .08, 1], 'side': [1, .08, 0], 'back': [0, .08, -1], 'oblique-front': [.72, .12, 1]}

def run_garment_boundary_closeups(page, root: Path, checks: dict) -> None:
    folder = root / 'garment-boundaries'
    folder.mkdir(exist_ok=True)
    page.evaluate("""()=>{
      window.__garmentRenderRestore={ratio:KR.renderer.getPixelRatio(),
        width:KR.renderer.domElement.width/KR.renderer.getPixelRatio(),
        height:KR.renderer.domElement.height/KR.renderer.getPixelRatio(),
        aspect:KR.camera.aspect,suppress:window.__suppressDraw};
      window.__suppressDraw=true;
    }""")
    records = []
    try:
        for pose in POSES:
            for view, direction in VIEWS.items():
                result = page.evaluate("""async (args)=>{
                  const T=await import('three');
                  KR.reset();KR.change('pose',args.pose);KR.figure.updateMatrixWorld(true);
                  const names=new Set(['Ribbed V-neck vest / skinned torso panels','Bound neckline, armholes and hem','Skinned front button band']);
                  const points=[],p=new T.Vector3(),counts={};
                  KR.figure.traverse(o=>{
                    if(!o.isMesh||!names.has(o.name))return;
                    if(o.skeleton)o.skeleton.update();
                    counts[o.name]=o.geometry.attributes.position.count;
                    for(let i=0;i<o.geometry.attributes.position.count;i++){
                      o.getVertexPosition(i,p);o.localToWorld(p);points.push(p.clone());
                    }
                  });
                  if(!counts['Ribbed V-neck vest / skinned torso panels']||points.length<500)throw Error('Missing skinned vest geometry for garment-boundary QA');
                  const full=new T.Box3().setFromPoints(points),box=full.clone();
                  const height=full.max.y-full.min.y;box.min.y=full.min.y+height*.34;
                  const center=box.getCenter(new T.Vector3()),size=box.getSize(new T.Vector3()),vfov=KR.camera.fov*Math.PI/180;
                  const distance=Math.max(size.y/(2*Math.tan(vfov/2)),size.x/(2*Math.tan(vfov/2)*1.333))*1.34;
                  KR.renderer.setPixelRatio(1);KR.renderer.setSize(720,540,false);
                  KR.camera.aspect=4/3;KR.camera.updateProjectionMatrix();
                  KR.camera.position.copy(center).add(new T.Vector3(...args.direction).normalize().multiplyScalar(distance));
                  KR.camera.lookAt(center);KR.camera.updateMatrixWorld(true);KR.renderer.render(KR.scene,KR.camera);
                  return {png:KR.renderer.domElement.toDataURL('image/png'),webglError:KR.renderer.getContext().getError(),
                    state:{pose:KR.state.pose,view:args.view},meshVertexCounts:counts,
                    focusedBounds:{min:box.min.toArray(),max:box.max.toArray()},fullVestBounds:{min:full.min.toArray(),max:full.max.toArray()}};
                }""", {'pose': pose, 'view': view, 'direction': direction})
                data = base64.b64decode(result.pop('png').split(',', 1)[1])
                name = f'{pose}-{view}.png'; path = folder / name; path.write_bytes(data)
                image = Image.open(path).convert('RGB')
                if image.size != (720, 540) or max(ImageStat.Stat(image).stddev) < 2:
                    checks['errors'].append('Invalid or uniform actual garment-boundary close-up: ' + name)
                if result['webglError'] or result['state'] != {'pose': pose, 'view': view}:
                    checks['errors'].append('Garment-boundary close-up state/WebGL failure: ' + name)
                digest = hashlib.sha256(data).hexdigest()
                records.append({'path': 'garment-boundaries/' + name, 'sha256': digest, 'pose': pose, 'view': view, **result})
        if len({r['sha256'] for r in records}) < 10:
            checks['errors'].append('Garment-boundary close-ups are insufficiently distinct across pose/view coverage')
        atlas = Image.new('RGB', (720 * 4, 568 * 5), 'white'); draw = ImageDraw.Draw(atlas)
        for i, record in enumerate(records):
            x, y = (i % 4) * 720, (i // 4) * 568
            atlas.paste(Image.open(root / record['path']).convert('RGB'), (x, y + 28))
            draw.text((x + 8, y + 6), record['pose'] + ' / ' + record['view'], fill='black')
        atlas.save(root / 'garment-boundaries-rendered.png')
        (root / 'garment-boundaries-manifest.json').write_text(json.dumps(records, indent=2))
        checks['garment_boundaries'] = {'executed_renders': len(records),
            'coverage': 'exhaustive 5 implemented poses x 4 close-up camera directions',
            'resolution': [720, 540], 'evidence': records, 'visual_approval': False,
            'physical_fit_validated': False,
            'limits': 'Actual Chromium/WebGL close-ups support boundary inspection; they are not physical collision, pressure, fit, or hardware-device validation.'}
    finally:
        page.evaluate("""()=>{
          const r=window.__garmentRenderRestore;
          KR.renderer.setPixelRatio(r.ratio);KR.renderer.setSize(r.width,r.height,false);
          KR.camera.aspect=r.aspect;KR.camera.updateProjectionMatrix();
          window.__suppressDraw=r.suppress;KR.reset();delete window.__garmentRenderRestore;
        }""")
