// Development measurement morph: target geometric section circumferences only.
// This is not a body scan/reconstruction, pressure model, comfort prediction, or physical-fit validation.
const measurementBases=new Map();
let measurementBoneIds=new Set();
const measurementControls={
  hips:{y:.86,baseCm:98.56065185405565,z:.019140276675794318,core:.205},
  waist:{y:1.08,baseCm:68.15833098578725,z:.041643452403700966,core:.160},
  bust:{y:1.24,baseCm:88.4680902095765,z:.07254166648861177,core:.180}
};
const measurementSmooth=t=>{t=Math.max(0,Math.min(1,t));return t*t*(3-2*t)};
function measurementBlend(y,values,edgeLow=values[0],edgeHigh=values[2]){
  if(y<=.68)return edgeLow;
  if(y<.82){const t=measurementSmooth((y-.68)/.14);return edgeLow+(values[0]-edgeLow)*t;}
  if(y<=.90)return values[0];
  if(y<1.04){const t=measurementSmooth((y-.90)/.14);return values[0]+(values[1]-values[0])*t;}
  if(y<=1.12)return values[1];
  if(y<1.20){const t=measurementSmooth((y-1.12)/.08);return values[1]+(values[2]-values[1])*t;}
  if(y<=1.28)return values[2];
  if(y<1.34){const t=measurementSmooth((y-1.28)/.06);return values[2]+(edgeHigh-values[2])*t;}
  return edgeHigh;
}
function measurementCenterZ(y){
  const h=measurementControls.hips,w=measurementControls.waist,b=measurementControls.bust;
  if(y<=h.y)return h.z;
  if(y<w.y){const t=measurementSmooth((y-h.y)/(w.y-h.y));return h.z+(w.z-h.z)*t;}
  if(y<b.y){const t=measurementSmooth((y-w.y)/(b.y-w.y));return w.z+(b.z-w.z)*t;}
  return b.z;
}
function measurementInfluence(mesh,i,x,y){
  if(y<=.68||y>=1.34)return 0;
  const si=mesh.geometry.attributes.skinIndex,sw=mesh.geometry.attributes.skinWeight;
  let boneWeight=0;
  if(si&&sw)for(let k=0;k<4;k++){const at=i*4+k;if(measurementBoneIds.has(si.array[at]))boneWeight+=sw.array[at];}
  const core=measurementBlend(y,[measurementControls.hips.core,measurementControls.waist.core,measurementControls.bust.core],measurementControls.hips.core,measurementControls.bust.core);
  const outer=core+.008,ax=Math.abs(x);
  const positional=ax<=core?1:ax>=outer?0:1-measurementSmooth((ax-core)/(outer-core));
  return Math.max(0,Math.min(1,Math.max(boneWeight,positional)));
}
function initMeasurementGeometry(){
  const names=new Set(['root','pelvis.L','pelvis.R','upperleg01.L','upperleg02.L','upperleg01.R','upperleg02.R','spine05','spine04','spine03','spine02','spine01','breast.L','breast.R','clavicle.L','clavicle.R']);
  measurementBoneIds=new Set(data.rig.names.map((name,i)=>names.has(name)?i:-1).filter(i=>i>=0));
  measurementBases.clear();
  const eligible=name=>typeof name==='string'&&(name==='Anatomical female body'||name==='Ribbed V-neck vest / skinned torso panels'||name==='Neutral underlayer'||name==='Taupe leggings'||name.startsWith('Vest button ')||name==='Bound neckline, armholes and hem'||name==='Skinned front button band');
  for(const mesh of meshRecords){
    const p=mesh.geometry?.attributes?.position;
    if(!eligible(mesh.name)||!p||!mesh.geometry.attributes.skinIndex||!mesh.geometry.attributes.skinWeight)continue;
    measurementBases.set(mesh,new Float32Array(p.array));
  }
  applyMeasurements();
}
function applyMeasurements(){
  if(!measurementBases.size)return;
  const heightScale=state.height/168;
  const scales=[state.hips/(measurementControls.hips.baseCm*heightScale),state.waist/(measurementControls.waist.baseCm*heightScale),state.bust/(measurementControls.bust.baseCm*heightScale)];
  for(const [mesh,base] of measurementBases){
    const p=mesh.geometry.attributes.position;
    for(let i=0;i<p.count;i++){
      const x=base[i*3],y=base[i*3+1],z=base[i*3+2];
      const influence=measurementInfluence(mesh,i,x,y);
      if(!influence){p.setXYZ(i,x,y,z);continue;}
      const radial=measurementBlend(y,scales,1,1),factor=1+influence*(radial-1),zc=measurementCenterZ(y);
      p.setXYZ(i,x*factor,y,zc+(z-zc)*factor);
    }
    p.needsUpdate=true;
    mesh.geometry.computeVertexNormals();
    mesh.geometry.computeBoundingBox();mesh.geometry.computeBoundingSphere();
  }
  figure.scale.setScalar(heightScale);
}
function measurementSectionPerimeterCm(control){
  const p=body.geometry.attributes.position.array,indices=data.mesh.indices,y=control.y,segs=[];
  for(let k=0;k<indices.length;k+=3){
    const ids=indices.slice(k,k+3),hits=[];
    for(let e=0;e<3;e++){
      const ia=ids[e],ib=ids[(e+1)%3],ay=p[ia*3+1],by=p[ib*3+1],da=ay-y,db=by-y;
      if(!((da<0&&db>=0)||(da>0&&db<=0)))continue;
      const den=by-ay;if(Math.abs(den)<1e-12)continue;const t=(y-ay)/den;
      const q=[p[ia*3]+t*(p[ib*3]-p[ia*3]),p[ia*3+2]+t*(p[ib*3+2]-p[ia*3+2])];
      if(!hits.some(r=>Math.hypot(q[0]-r[0],q[1]-r[1])<1e-9))hits.push(q);
    }
    if(hits.length>=2)segs.push([hits[0],hits[1]]);
  }
  const key=q=>`${Math.round(q[0]*1e6)},${Math.round(q[1]*1e6)}`,node=new Map();
  for(let i=0;i<segs.length;i++)for(const q of segs[i]){const k=key(q),list=node.get(k)||[];list.push(i);node.set(k,list)}
  const seen=new Set(),components=[];
  for(let i=0;i<segs.length;i++){
    if(seen.has(i))continue;const stack=[i],members=[];
    while(stack.length){const e=stack.pop();if(seen.has(e))continue;seen.add(e);members.push(e);for(const q of segs[e])for(const n of node.get(key(q))||[])if(!seen.has(n))stack.push(n)}
    let perimeter=0,sumX=0,count=0;for(const e of members){const [a,b]=segs[e];perimeter+=Math.hypot(b[0]-a[0],b[1]-a[1]);sumX+=a[0]+b[0];count+=2}
    if(count)components.push({centroidAbsX:Math.abs(sumX/count),perimeter});
  }
  components.sort((a,b)=>a.centroidAbsX-b.centroidAbsX||b.perimeter-a.perimeter);
  return components.length?components[0].perimeter*100*figure.scale.x:NaN;
}
function measurementReport(){
  const measured={};for(const key of ['bust','waist','hips'])measured[key]=measurementSectionPerimeterCm(measurementControls[key]);
  return {targets_cm:{bust:state.bust,waist:state.waist,hips:state.hips,height:state.height},measured_sections_cm:measured,section_planes_m:Object.fromEntries(Object.entries(measurementControls).map(([k,v])=>[k,v.y])),fixture_height_cm:data.height*100*figure.scale.y,method:'Development fixture horizontal triangle-plane section circumference after geometric morph',limitations:'Not a body scan/reconstruction, garment grading/ease, pressure, comfort or physical-fit validation'};
}
