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
    page.evaluate('KR.view("side");KR.renderer.render(KR.scene,KR.camera)')
    slip_side=base64.b64decode(page.evaluate('KR.renderer.domElement.toDataURL("image/png")').split(',',1)[1])
    (root/'footwear-slip-ons-side.png').write_bytes(slip_side)
    page.evaluate('KR.view("front");KR.change("shoes","barefoot");KR.renderer.render(KR.scene,KR.camera)')
    bare=base64.b64decode(page.evaluate('KR.renderer.domElement.toDataURL("image/png")').split(',',1)[1])
    (root/'footwear-barefoot.png').write_bytes(bare)
    page.evaluate('KR.view("side");KR.renderer.render(KR.scene,KR.camera)')
    bare_side=base64.b64decode(page.evaluate('KR.renderer.domElement.toDataURL("image/png")').split(',',1)[1])
    (root/'footwear-barefoot-side.png').write_bytes(bare_side)
    checks['footwear_visual_effect']={'different_render':slip!=bare and slip_side!=bare_side,'slip_sha256':hashlib.sha256(slip).hexdigest(),'barefoot_sha256':hashlib.sha256(bare).hexdigest(),'slip_side_sha256':hashlib.sha256(slip_side).hexdigest(),'barefoot_side_sha256':hashlib.sha256(bare_side).hexdigest(),'coverage':'direct actual-render comparison of both footwear values in front and side views'}
    if slip==bare or slip_side==bare_side:checks['errors'].append('Footwear control did not produce a rendered visual effect in both front and side views')
    page.evaluate('KR.change("shoes","slip-ons");KR.view("front")')
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

    mobile=browser.new_page(viewport={'width':390,'height':844},device_scale_factor=1)
    mobile.add_init_script('window.__qaPause=true')
    mobile.on('pageerror',lambda e:checks['errors'].append(str(e)))
    mobile.goto('http://127.0.0.1:8719/',wait_until='networkidle',timeout=60000)
    mobile.wait_for_function('window.KR && KR.ready',timeout=30000)
    mobile.evaluate("KR.setSheet('collapsed');KR.reset();KR.view('front');KR.renderer.render(KR.scene,KR.camera)")
    zoom_hidden=not mobile.locator('#zoomIn').is_visible() and not mobile.locator('#zoomOut').is_visible()
    projected=mobile.evaluate("""async()=>{
      const T=await import('three'),p=new T.Vector3();let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity,n=0;
      KR.figure.updateMatrixWorld(true);
      KR.figure.traverse(o=>{if(!o.isMesh||!o.visible)return;if(o.skeleton)o.skeleton.update();const count=o.geometry.attributes.position?.count||0;for(let i=0;i<count;i++){o.getVertexPosition(i,p);o.localToWorld(p);p.project(KR.camera);if(!Number.isFinite(p.x)||!Number.isFinite(p.y))continue;minX=Math.min(minX,p.x);maxX=Math.max(maxX,p.x);minY=Math.min(minY,p.y);maxY=Math.max(maxY,p.y);n++;}});
      return {vertices:n,minX,maxX,minY,maxY,topFraction:(1-maxY)/2,bottomFraction:(1-minY)/2,heightFraction:(maxY-minY)/2};
    }""")
    raw=base64.b64decode(mobile.evaluate('KR.renderer.domElement.toDataURL("image/png")').split(',',1)[1])
    (root/'mobile-collapsed-rendered.png').write_bytes(raw)
    cd=mobile.context.new_cdp_session(mobile)
    cd.send('Emulation.setTouchEmulationEnabled',{'enabled':True,'maxTouchPoints':2})
    box=mobile.locator('#canvas').bounding_box();cx=box['x']+box['width']/2;cy=box['y']+box['height']/2
    one=lambda x,y:[{'x':x,'y':y,'id':0,'radiusX':2,'radiusY':2,'force':1}]
    cd.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':one(cx,cy)})
    cd.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
    mobile.wait_for_timeout(120)
    tap_view=mobile.evaluate('KR.state.view')
    before_pinch=mobile.evaluate('()=>({p:KR.camera.position.toArray(),q:KR.camera.quaternion.toArray()})')
    two=lambda d:[{'x':cx-d,'y':cy,'id':0,'radiusX':2,'radiusY':2,'force':1},{'x':cx+d,'y':cy,'id':1,'radiusX':2,'radiusY':2,'force':1}]
    cd.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':two(24)})
    for d in [30,36,42,48,54]:
        cd.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':two(d)});mobile.wait_for_timeout(25)
    cd.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});mobile.wait_for_timeout(150)
    after_pinch=mobile.evaluate('()=>({p:KR.camera.position.toArray(),q:KR.camera.quaternion.toArray(),view:KR.state.view})')
    mobile.evaluate("KR.reset();KR.view('front')")
    before_drag=mobile.evaluate('KR.camera.quaternion.toArray()')
    cd.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':one(cx,cy)})
    for dx in [15,30,45,60,75]:
        cd.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':one(cx+dx,cy+8)});mobile.wait_for_timeout(25)
    cd.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});mobile.wait_for_timeout(150)
    drag_view=mobile.evaluate('KR.state.view');after_drag=mobile.evaluate('KR.camera.quaternion.toArray()')
    cd.detach()
    mobile_state={'zoom_buttons_hidden':zoom_hidden,'tap_preserved_preset':tap_view=='front','pinch_changed_camera':before_pinch['p']!=after_pinch['p'],'pinch_preserved_preset':after_pinch['view']=='front','drag_entered_free':drag_view=='free','drag_changed_orientation':before_drag!=after_drag,'collapsed_projection':projected,'physical_hardware':False,'evidence':'software-rendered Chromium with CDP touch emulation; owner physical-iPhone screenshots remain separate evidence'}
    checks['mobile_interaction']=mobile_state
    if not zoom_hidden:checks['errors'].append('Mobile +/- zoom buttons remain visible')
    if tap_view!='front':checks['errors'].append('Canvas tap changed a selected camera preset')
    if before_pinch['p']==after_pinch['p'] or after_pinch['view']!='front':checks['errors'].append('Pinch zoom did not preserve camera preset')
    if drag_view!='free' or before_drag==after_drag:checks['errors'].append('Touch drag did not enter free orbit')
    if projected['vertices']<10000 or projected['topFraction']>.28 or projected['heightFraction']<.60 or projected['maxY']>1.08 or projected['minY']<-1.08:checks['errors'].append('Collapsed phone model framing is outside the tested visibility envelope')
    mobile.close()
