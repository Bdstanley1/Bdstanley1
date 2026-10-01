"""Additional actual-render checks: GLB deformed geometry and appearance pairwise coverage."""
import base64
import hashlib
import random
from pathlib import Path


def pairwise_cases(factors):
    keys=list(factors)
    pairs={(i,a,j,b) for i in range(len(keys)) for j in range(i+1,len(keys)) for a in factors[keys[i]] for b in factors[keys[j]]}
    total=len(pairs)
    rng=random.Random(9030)
    cases=[]
    while pairs:
        forced=min(pairs,key=repr)
        candidates=[]
        for _ in range(160):
            c=[rng.choice(factors[k]) for k in keys]
            c[forced[0]]=forced[1];c[forced[2]]=forced[3]
            covered={(i,c[i],j,c[j]) for i in range(len(keys)) for j in range(i+1,len(keys))}
            candidates.append((len(pairs & covered),c,covered))
        _,case,covered=max(candidates,key=lambda item:item[0])
        pairs-=covered
        cases.append(dict(zip(keys,case)))
    return cases,total


def run_additional(browser, root: Path, checks: dict):
    page=browser.new_page(viewport={'width':1100,'height':900},device_scale_factor=1)
    page.add_init_script('window.__qaPause=true')
    page.on('pageerror',lambda e:checks['errors'].append(str(e)))
    page.goto('http://127.0.0.1:8719/',wait_until='networkidle',timeout=60000)
    page.wait_for_function('window.KR && KR.ready',timeout=30000)
    page.evaluate('KR.reset();KR.view("front");KR.renderer.render(KR.scene,KR.camera)')
    before=page.evaluate('KR.renderer.domElement.toDataURL("image/png")')
    (root/'glb-original.png').write_bytes(base64.b64decode(before.split(',',1)[1]))
    comparison=page.evaluate("""async()=>{
      const T=await import('three');const {GLTFLoader}=await import('./GLTFLoader.js');
      const loaded=await new GLTFLoader().loadAsync('./qa/female-dressed-test.glb');
      const original=new Map();
      KR.figure.updateMatrixWorld(true);loaded.scene.updateMatrixWorld(true);
      let expectedMeshes=0;KR.figure.traverse(o=>{if(o.isMesh&&o.visible){expectedMeshes++;if(o.skeleton)o.skeleton.update();original.set(T.PropertyBinding.sanitizeNodeName(o.name),o);}});
      let checked=0,maxDeviation=0,meshes=0,missing=[],bad=[];
      const a=new T.Vector3(),b=new T.Vector3();
      loaded.scene.traverse(o=>{
        if(!o.isMesh)return;meshes++;if(o.skeleton)o.skeleton.update();
        const old=original.get(o.name);if(!old){missing.push(o.name);return;}
        if(old.geometry.attributes.position.count!==o.geometry.attributes.position.count){bad.push(o.name+' vertex count');return;}
        for(let i=0;i<o.geometry.attributes.position.count;i++){
          old.getVertexPosition(i,a);old.localToWorld(a);o.getVertexPosition(i,b);o.localToWorld(b);
          const d=a.distanceTo(b);if(!Number.isFinite(d)){bad.push(o.name+' nonfinite');break;}
          maxDeviation=Math.max(maxDeviation,d);checked++;
        }
        o.castShadow=true;o.receiveShadow=true;
      });
      KR.figure.visible=false;KR.scene.add(loaded.scene);window.__reloadFigure=loaded.scene;
      KR.renderer.render(KR.scene,KR.camera);
      return {meshes,expectedMeshes,checkedSkinnedVertices:checked,maxWorldDeviationMetres:maxDeviation,missing,bad};
    }""")
    comparison['passed']=comparison['meshes']==comparison['expectedMeshes'] and comparison['expectedMeshes']>=18 and comparison['checkedSkinnedVertices']>10000 and comparison['maxWorldDeviationMetres']<1e-4 and not comparison['missing'] and not comparison['bad']
    comparison['appearance']='Actual front/side/back/detail reload renders archived; visual approval remains separate.'
    checks['glb_geometry_roundtrip']=comparison
    if not comparison['passed']:
        checks['errors'].append('GLB skinned world-geometry comparison failed')
    for view in ['front','side','back']:
        page.evaluate('(v)=>{KR.view(v);KR.renderer.render(KR.scene,KR.camera)}',view)
        png=page.evaluate('KR.renderer.domElement.toDataURL("image/png")')
        (root/('glb-reloaded-'+view+'.png')).write_bytes(base64.b64decode(png.split(',',1)[1]))
    page.evaluate('KR.view("front")');page.locator('#detail').click()
    page.evaluate('KR.renderer.render(KR.scene,KR.camera)')
    png=page.evaluate('KR.renderer.domElement.toDataURL("image/png")')
    (root/'glb-reloaded-detail.png').write_bytes(base64.b64decode(png.split(',',1)[1]))
    page.evaluate('KR.scene.remove(window.__reloadFigure);KR.figure.visible=true;KR.reset()')
    page.evaluate('KR.reset();KR.view("front");KR.change("shoes","slip-ons");KR.renderer.render(KR.scene,KR.camera)')
    slip=base64.b64decode(page.evaluate('KR.renderer.domElement.toDataURL("image/png")').split(',',1)[1])
    (root/'footwear-slip-ons.png').write_bytes(slip)
    page.evaluate('KR.change("shoes","barefoot");KR.renderer.render(KR.scene,KR.camera)')
    bare=base64.b64decode(page.evaluate('KR.renderer.domElement.toDataURL("image/png")').split(',',1)[1])
    (root/'footwear-barefoot.png').write_bytes(bare)
    checks['footwear_visual_effect']={'different_render':slip!=bare,'slip_sha256':hashlib.sha256(slip).hexdigest(),'barefoot_sha256':hashlib.sha256(bare).hexdigest(),'coverage':'direct actual-render comparison of both footwear values'}
    if slip==bare:checks['errors'].append('Footwear control did not produce a rendered visual effect')
    page.evaluate('KR.change("shoes","slip-ons")')
    factors={'skin':['#ffffff','#d6ac8d','#a97959'],'hair':['#836c57','#ffffff','#493025','#201a16','#ac7946','#854629'],'hairStyle':['wavy','straight','curly'],'length':[.75,1,1.35],'shoes':['slip-ons','barefoot'],'pose':['neutral','fashion','hip','walk','three-quarter'],'view':['front','side','back','free']}
    cases,pairs=pairwise_cases(factors)
    folder=root/'appearance-pairwise';folder.mkdir(exist_ok=True)
    page.evaluate('KR.renderer.setPixelRatio(1);KR.renderer.setSize(240,360,false);KR.renderer.shadowMap.enabled=false;KR.camera.aspect=2/3;KR.camera.updateProjectionMatrix();window.__suppressDraw=true')
    evidence=[]
    for i,case in enumerate(cases):
        result=page.evaluate("""(values)=>{
          for(const [k,v] of Object.entries(values)){if(k==='view')KR.view(v);else KR.change(k,v);}
          KR.renderer.render(KR.scene,KR.camera);
          return {png:KR.renderer.domElement.toDataURL('image/png'),webglError:KR.renderer.getContext().getError(),state:{...KR.state}};
        }""",case)
        raw=base64.b64decode(result.pop('png').split(',',1)[1])
        name=f'{i:03d}.png';(folder/name).write_bytes(raw)
        if result['webglError'] or any(result['state'][k]!=v for k,v in case.items()):
            checks['errors'].append('Pairwise appearance control/render failure '+str(i))
        evidence.append({'case':case,'path':'appearance-pairwise/'+name,'sha256':hashlib.sha256(raw).hexdigest(),'webglError':result['webglError']})
    checks['appearance_pairwise']={'coverage':'all value pairs across the seven listed factors, not the full Cartesian product','factors':factors,'pair_count':pairs,'case_count':len(cases),'evidence':evidence,'render_resolution':[240,360],'shadows':False,'physical_hardware':False,'visual_approval':False}
    page.close()
