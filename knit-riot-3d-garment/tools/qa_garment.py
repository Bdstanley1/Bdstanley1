"""Targeted actual-render QA for vest neckline/armhole/attachment boundaries.

This is rendering evidence for synthetic development geometry. It does not validate
physical fit, cloth mechanics, comfort, or hardware-specific rendering.
"""
import base64
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageStat

POSES = ['neutral', 'fashion', 'hip', 'walk', 'three-quarter']
VIEWS = {
    'front': [0, .12, 1],
    'front-left': [-.42, .16, 1],
    'front-right': [.42, .16, 1],
    'side': [1, .12, .08],
}
REQUIRED_OVERLAYS = [
    'Smooth front armhole binding left',
    'Smooth front armhole binding right',
    'Smooth front neckline binding left',
    'Smooth front neckline binding right',
]


def run_garment_closeups(page, root: Path, checks: dict) -> None:
    folder = root / 'garment-closeups'
    folder.mkdir(exist_ok=True)
    records = []
    setup = page.evaluate("""async()=>{
      const names=%s;
      const overlays=names.map(name=>KR.figure.getObjectByName(name));
      const missing=names.filter((name,i)=>!overlays[i]);
      const vertices=overlays.map(o=>o?.geometry?.attributes?.position?.count||0);
      const nonfinite=[];
      overlays.forEach((o,oi)=>{if(!o)return;const p=o.geometry.attributes.position;
        for(let i=0;i<p.count;i++)for(let k=0;k<3;k++)if(!Number.isFinite(p.getComponent(i,k)))nonfinite.push([oi,i,k]);});
      return {missing,vertices,nonfinite};
    }""" % json.dumps(REQUIRED_OVERLAYS))
    if setup['missing']:
        checks['errors'].append('Missing smooth garment boundary overlays: ' + ', '.join(setup['missing']))
    if any(v < 60 for v in setup['vertices']):
        checks['errors'].append('Smooth garment boundary overlay has insufficient geometry')
    if setup['nonfinite']:
        checks['errors'].append('Smooth garment boundary overlay contains non-finite coordinates')

    restore = page.evaluate("""()=>({ratio:KR.renderer.getPixelRatio(),
      width:KR.renderer.domElement.width/KR.renderer.getPixelRatio(),
      height:KR.renderer.domElement.height/KR.renderer.getPixelRatio(),aspect:KR.camera.aspect,
      suppress:window.__suppressDraw})""")
    page.evaluate('window.__suppressDraw=true')
    try:
        for pose in POSES:
            for view, direction in VIEWS.items():
                result = page.evaluate("""async(args)=>{
                  const T=await import('three');
                  KR.reset();KR.change('pose',args.pose);KR.figure.updateMatrixWorld(true);
                  const vest=KR.figure.getObjectByName('Ribbed V-neck vest / skinned torso panels');
                  if(!vest)throw Error('Missing vest for garment close-up QA');
                  if(vest.skeleton)vest.skeleton.update();
                  const box=new T.Box3(),p=new T.Vector3();
                  const names=['Ribbed V-neck vest / skinned torso panels','Bound neckline, armholes and hem',
                    'Smooth front armhole binding left','Smooth front armhole binding right',
                    'Smooth front neckline binding left','Smooth front neckline binding right','Skinned front button band'];
                  let vertices=0;
                  for(const name of names){const o=KR.figure.getObjectByName(name);if(!o||!o.isMesh)continue;
                    if(o.skeleton)o.skeleton.update();for(let i=0;i<o.geometry.attributes.position.count;i++){
                      o.getVertexPosition(i,p);o.localToWorld(p);box.expandByPoint(p);vertices++;}}
                  if(vertices<1000||box.isEmpty())throw Error('Insufficient garment geometry for close-up QA');
                  const center=box.getCenter(new T.Vector3()),size=box.getSize(new T.Vector3());
                  center.y += size.y*.02;
                  const dir=new T.Vector3(...args.direction).normalize();
                  const distance=Math.max(size.y/(2*Math.tan(KR.camera.fov*Math.PI/360)),
                    size.x/(2*Math.tan(KR.camera.fov*Math.PI/360)*1.25))*1.23;
                  KR.renderer.setPixelRatio(1);KR.renderer.setSize(800,640,false);
                  KR.camera.aspect=1.25;KR.camera.updateProjectionMatrix();
                  KR.camera.position.copy(center).addScaledVector(dir,distance);KR.camera.lookAt(center);KR.camera.updateMatrixWorld(true);
                  KR.renderer.render(KR.scene,KR.camera);
                  return {png:KR.renderer.domElement.toDataURL('image/png'),webglError:KR.renderer.getContext().getError(),
                    vertices,state:{pose:KR.state.pose},bounds:{min:box.min.toArray(),max:box.max.toArray()}};
                }""", {'pose': pose, 'direction': direction})
                raw = base64.b64decode(result.pop('png').split(',', 1)[1])
                name = f'{pose}-{view}.png'
                (folder / name).write_bytes(raw)
                image = Image.open(folder / name).convert('RGB')
                if image.size != (800, 640) or max(ImageStat.Stat(image).stddev) < 2:
                    checks['errors'].append('Invalid or uniform garment close-up: ' + name)
                if result['webglError'] or result['state'] != {'pose': pose}:
                    checks['errors'].append('Garment close-up state/WebGL failure: ' + name)
                records.append({'path': 'garment-closeups/' + name,
                    'sha256': hashlib.sha256(raw).hexdigest(), 'pose': pose, 'view': view, **result})
    finally:
        page.evaluate("""r=>{KR.renderer.setPixelRatio(r.ratio);KR.renderer.setSize(r.width,r.height,false);
          KR.camera.aspect=r.aspect;KR.camera.updateProjectionMatrix();window.__suppressDraw=r.suppress;KR.reset();}""", restore)

    atlas = Image.new('RGB', (800 * 4, 670 * 5), 'white')
    draw = ImageDraw.Draw(atlas)
    for i, record in enumerate(records):
        x, y = (i % 4) * 800, (i // 4) * 670
        atlas.paste(Image.open(root / record['path']).convert('RGB'), (x, y + 30))
        draw.text((x + 8, y + 7), record['pose'] + ' / ' + record['view'], fill='black')
    atlas.save(root / 'garment-closeups-rendered.png')
    (root / 'garment-closeups-manifest.json').write_text(json.dumps(records, indent=2))
    checks['garment_closeups'] = {
        'executed_renders': len(records),
        'coverage': 'exhaustive 5 implemented poses x 4 targeted upper-garment camera directions',
        'resolution': [800, 640],
        'required_overlay_geometry': setup,
        'evidence': records,
        'visual_approval': False,
        'physical_fit_validated': False,
        'physical_hardware': False,
        'limits': 'Targeted Chromium boundary renders and overlay-presence checks; actual image inspection is still required and this does not validate physical fit.'
    }
