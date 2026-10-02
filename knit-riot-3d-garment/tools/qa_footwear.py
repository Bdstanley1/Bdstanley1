"""Actual close-up footwear render coverage; synthetic fixture, not physical fit."""
import base64
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageStat, ImageChops

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
    probe_records = []
    probe_folder = root / 'footwear-occlusion'
    probe_folder.mkdir(exist_ok=True)
    try:
        probe_setup = page.evaluate('''async()=>{
          const T=await import('three'),response=await fetch('./assets/body.json');
          if(!response.ok)throw Error('Missing synthetic anatomy for occlusion QA');
          const fixture=await response.json(),body=KR.figure.getObjectByName('Anatomical female body');
          const contours=['left','right'].map(side=>KR.figure.getObjectByName('White slip-on '+side+' upper')?.userData.developmentContour);
          if(!body||contours.some(c=>!c))throw Error('Missing actual shoe contour metadata');
          const positions=fixture.mesh.positions,indices=[];
          for(let i=0;i<fixture.mesh.indices.length;i+=3){
            const tri=fixture.mesh.indices.slice(i,i+3);
            if(tri.every(id=>{const [x,y,z]=positions.slice(id*3,id*3+3),c=contours[x<0?0:1];return y<c.collarY-.003&&z>c.forefootInspectionStartZ;}))indices.push(...tri);
          }
          if(indices.length<300)throw Error('Insufficient visible-foot negative-control geometry');
          const probe=body.clone(false);probe.geometry=body.geometry.clone();probe.geometry.setIndex(indices);
          probe.material=new T.MeshBasicMaterial({color:0xff00ff,side:T.DoubleSide,toneMapped:false});
          probe.name='QA-only forefoot occlusion probe';probe.visible=false;probe.castShadow=false;probe.receiveShadow=false;probe.frustumCulled=false;
          KR.figure.add(probe);probe.bind(body.skeleton,body.bindMatrix);
          window.__krToeProbe={probe,body};
          return {triangles:indices.length/3,contours};
        }''')
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
                    probe_data = page.evaluate('''()=>{
                      const {probe,body}=window.__krToeProbe,wasVisible=body.visible;
                      try{body.visible=false;probe.visible=true;KR.figure.updateMatrixWorld(true);
                        probe.skeleton.update();KR.renderer.render(KR.scene,KR.camera);
                        return {png:KR.renderer.domElement.toDataURL('image/png'),webglError:KR.renderer.getContext().getError()};
                      }finally{body.visible=wasVisible;probe.visible=false;}
                    }''')
                    probe_raw = base64.b64decode(probe_data['png'].split(',', 1)[1])
                    (probe_folder / name).write_bytes(probe_raw)
                    red, green, blue = Image.open(probe_folder / name).convert('RGB').split()
                    mask = ImageChops.multiply(ImageChops.multiply(
                        red.point(lambda v: 255 if v > 160 else 0),
                        blue.point(lambda v: 255 if v > 160 else 0)),
                        green.point(lambda v: 255 if v < 80 else 0))
                    exposed = mask.histogram()[255]
                    if probe_data['webglError']:
                        checks['errors'].append('Toe occlusion probe WebGL failure: ' + name)
                    if shoe == 'slip-ons' and exposed:
                        checks['errors'].append(f'Closed slip-on exposes {exposed} diagnostic forefoot pixels: {name}')
                    if shoe == 'barefoot' and exposed < 20:
                        checks['errors'].append('Toe exposure negative control was not visible: ' + name)
                    probe_records.append({'path': 'footwear-occlusion/' + name,
                        'sha256': hashlib.sha256(probe_raw).hexdigest(), 'shoe': shoe,
                        'pose': pose, 'view': view, 'exposed_probe_pixels': exposed})
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
        probe_atlas = Image.new('RGB', (720 * 4, 508 * 10), 'white')
        probe_draw = ImageDraw.Draw(probe_atlas)
        for i, record in enumerate(probe_records):
            x, y = (i % 4) * 720, (i // 4) * 508
            probe_atlas.paste(Image.open(root / record['path']).convert('RGB'), (x, y + 28))
            probe_draw.text((x + 8, y + 6), f"{record['shoe']} / {record['pose']} / {record['view']} / pixels={record['exposed_probe_pixels']}", fill='black')
        probe_atlas.save(root / 'footwear-occlusion-rendered.png')
        (root / 'footwear-occlusion-manifest.json').write_text(json.dumps(probe_records, indent=2))
        checks['footwear_occlusion'] = {'executed_renders': len(probe_records),
            'coverage': 'exhaustive 2 footwear choices x 5 poses x 4 camera directions; 20 closed-shoe checks plus 20 barefoot negative controls',
            'probe_region': probe_setup, 'evidence': probe_records,
            'closed_shoe_exposed_probe_pixels': sum(r['exposed_probe_pixels'] for r in probe_records if r['shoe'] == 'slip-ons'),
            'pixel_threshold_rgb': 'R>160, B>160, G<80 for unlit magenta diagnostic mesh',
            'limits': 'Actual depth-tested forefoot visibility only, not every shoe boundary, physical fit or real-device validation',
            'physical_fit_validated': False}
        (root / 'footwear-closeups-manifest.json').write_text(json.dumps(records, indent=2))
        checks['footwear_closeups'] = {'executed_renders': len(records),
            'coverage': 'exhaustive 2 footwear choices x 5 existing poses x 4 close-up camera directions',
            'resolution': [720, 480], 'evidence': records,
            'visual_approval': False, 'physical_fit_validated': False,
            'limits': 'Image/state checks detect missing effects; actual visual inspection remains required.'}
    finally:
        page.evaluate('''()=>{
          if(window.__krToeProbe){const {probe}=window.__krToeProbe;KR.figure.remove(probe);probe.geometry.dispose();probe.material.dispose();delete window.__krToeProbe;}
          const r=window.__footwearRenderRestore;
          KR.renderer.setPixelRatio(r.ratio);KR.renderer.setSize(r.width,r.height,false);
          KR.camera.aspect=r.aspect;KR.camera.updateProjectionMatrix();
          window.__suppressDraw=r.suppress;KR.reset();
          delete window.__footwearRenderRestore;
        }''')
