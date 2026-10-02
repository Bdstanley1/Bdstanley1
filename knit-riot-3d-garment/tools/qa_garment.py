"""Actual close-up garment-boundary render coverage; artistic fixture, not physical fit."""
import base64
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageStat

POSES = ['neutral', 'fashion', 'hip', 'walk', 'three-quarter']
VIEWS = {
    'front': [0, .06, 1],
    'left-oblique': [-.62, .08, .78],
    'right-oblique': [.62, .08, .78],
    'side': [1, .06, 0],
}

def run_garment_closeups(page, root: Path, checks: dict) -> None:
    """Render every existing pose from four close-up directions around upper garment."""
    folder = root / 'garment-closeups'
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
                  KR.reset();KR.change('pose',args.pose);KR.view('front');
                  KR.figure.updateMatrixWorld(true);
                  const garment=KR.figure.getObjectByName('Ribbed V-neck vest / skinned torso panels');
                  const trim=KR.figure.getObjectByName('Bound neckline, armholes and hem');
                  if(!garment||!trim)throw Error('Missing implemented vest or binding for garment QA');
                  garment.skeleton?.update();trim.skeleton?.update();
                  const box=new T.Box3(),p=new T.Vector3();let vertices=0;
                  for(const mesh of [garment,trim]){
                    for(let i=0;i<mesh.geometry.attributes.position.count;i++){
                      mesh.getVertexPosition(i,p);mesh.localToWorld(p);box.expandByPoint(p);vertices++;
                    }
                  }
                  if(!vertices||box.isEmpty())throw Error('No garment geometry for actual boundary QA');
                  const center=box.getCenter(new T.Vector3()),size=box.getSize(new T.Vector3());
                  center.y += size.y*.08;
                  const distance=Math.max(size.x,size.y)*1.40/Math.sin(KR.camera.fov*Math.PI/360);
                  KR.renderer.setPixelRatio(1);KR.renderer.setSize(720,620,false);
                  KR.camera.aspect=720/620;KR.camera.updateProjectionMatrix();
                  KR.camera.position.copy(center).add(new T.Vector3(...args.direction).normalize().multiplyScalar(distance));
                  KR.camera.lookAt(center);KR.camera.updateMatrixWorld(true);
                  KR.renderer.render(KR.scene,KR.camera);
                  return {png:KR.renderer.domElement.toDataURL('image/png'),
                    webglError:KR.renderer.getContext().getError(),vertices,
                    state:{pose:KR.state.pose},bounds:{min:box.min.toArray(),max:box.max.toArray()},
                    meshes:{garmentVertices:garment.geometry.attributes.position.count,
                      bindingVertices:trim.geometry.attributes.position.count}};
                }""", {'pose': pose, 'direction': direction})
                raw = base64.b64decode(result.pop('png').split(',', 1)[1])
                name = f'{pose}-{view}.png'
                path = folder / name
                path.write_bytes(raw)
                image = Image.open(path).convert('RGB')
                if image.size != (720, 620) or max(ImageStat.Stat(image).stddev) < 2:
                    checks['errors'].append('Invalid or uniform actual garment close-up: ' + name)
                if result['webglError'] or result['state'] != {'pose': pose}:
                    checks['errors'].append('Garment close-up state/WebGL failure: ' + name)
                records.append({'path': 'garment-closeups/' + name,
                    'sha256': hashlib.sha256(raw).hexdigest(), 'pose': pose,
                    'view': view, **result})
        atlas = Image.new('RGB', (720 * 4, 650 * 5), 'white')
        draw = ImageDraw.Draw(atlas)
        for i, record in enumerate(records):
            x, y = (i % 4) * 720, (i // 4) * 650
            atlas.paste(Image.open(root / record['path']).convert('RGB'), (x, y + 30))
            draw.text((x + 8, y + 7), record['pose'] + ' / ' + record['view'], fill='black')
        atlas.save(root / 'garment-closeups-rendered.png')
        (root / 'garment-closeups-manifest.json').write_text(json.dumps(records, indent=2))
        page.set_viewport_size({'width': 844, 'height': 390})
        page.evaluate("KR.reset();KR.view('front');KR.renderer.setPixelRatio(1);KR.renderer.setSize(844,390,false);KR.camera.aspect=844/390;KR.camera.updateProjectionMatrix();KR.reframe();KR.renderer.render(KR.scene,KR.camera)")
        landscape = page.screenshot(animations='disabled')
        (root / 'phone-landscape-neutral-front.png').write_bytes(landscape)
        landscape_image = Image.open(root / 'phone-landscape-neutral-front.png').convert('RGB')
        landscape_ok = landscape_image.size == (844, 390) and max(ImageStat.Stat(landscape_image).stddev) >= 2
        if not landscape_ok:
            checks['errors'].append('Invalid or uniform representative phone landscape render')
        checks['garment_closeups'] = {
            'executed_renders': len(records),
            'coverage': 'exhaustive 5 implemented pose choices x 4 defined upper-garment close-up camera directions',
            'resolution': [720, 620],
            'evidence': records,
            'inspection_scope': 'neckline, both armholes/shoulders, vest attachment and hem visible in pose-specific close-ups',
            'limits': 'Not exhaustive over continuous orbit angles, measurements, grading, physical garment fit, or real-device hardware',
            'visual_approval': False,
            'physical_fit_validated': False,
            'phone_landscape_representative': {'resolution': [844, 390], 'path': 'phone-landscape-neutral-front.png', 'nonuniform_pixels': landscape_ok, 'coverage': 'representative neutral/front software viewport only; not physical-device validation'},
        }
    finally:
        page.evaluate("""()=>{
          const r=window.__garmentRenderRestore;
          if(!r)return;
          KR.renderer.setPixelRatio(r.ratio);KR.renderer.setSize(r.width,r.height,false);
          KR.camera.aspect=r.aspect;KR.camera.updateProjectionMatrix();window.__suppressDraw=r.suppress;
          KR.reset();delete window.__garmentRenderRestore;
        }""")
