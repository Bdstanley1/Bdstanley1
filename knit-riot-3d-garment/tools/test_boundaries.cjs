// Fixture-level geometric invariants, not photographic or physical-fit validation.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert/strict');
const root=path.resolve(__dirname,'..');
const data=JSON.parse(fs.readFileSync(path.join(root,'fixtures/runtime/assets/body.json'),'utf8'));
let kept;
const context={data,body:{geometry:{setIndex(value){kept=value;},userData:{}}}};
vm.createContext(context);
vm.runInContext(fs.readFileSync(path.join(root,'patches/mask.js'),'utf8'),context);
context.maskCoveredBody();
assert(kept&&kept.length%3===0);
const present=new Set();for(let i=0;i<kept.length;i+=3)present.add(kept.slice(i,i+3).join(','));
let upperTriangles=0;
for(let i=0;i<data.mesh.indices.length;i+=3){
 const tri=data.mesh.indices.slice(i,i+3);
 if(tri.some(v=>data.mesh.positions[v*3+1]>=data.height*.553)){
  upperTriangles++;assert(present.has(tri.join(',')),'Upper-body face removed: open armholes can see through to background');
 }
}
assert(upperTriangles>5000);
vm.runInContext(fs.readFileSync(path.join(root,'patches/refine.js'),'utf8'),context);
const refined=context.refineTextileSurface(data.mesh);
let checked=0,minimum=Infinity;
for(let i=0;i<data.mesh.positions.length/3;i++){
 const [x,y,z]=data.mesh.positions.slice(i*3,i*3+3);
 if(z>.03&&Math.abs(x)<.215&&y>1.03&&y<1.38){
  const clearance=refined.positions[i*3+2]+.013*refined.normals[i*3+2]-z;
  assert(clearance>=-1e-7,'Garment front vertex projects behind intact body');
  checked++;minimum=Math.min(minimum,clearance);
 }
}
assert(checked>100);
console.log('BOUNDARY_GEOMETRY_RESULTS '+JSON.stringify({upper_body_triangles_retained:upperTriangles,front_vertex_projections_checked:checked,minimum_front_vertex_z_projection_clearance_metres:minimum,limitations:'Vertex projection is not triangle collision testing, pose clearance or physical garment-fit validation',physical_fit_validated:false}));

// Measurement-control boundary validation against actual transformed fixture geometry.
// This verifies geometric section circumferences only; it is not body-scan accuracy or physical garment fit.
function positionAttribute(values){
 const array=new Float32Array(values);
 return {array,count:array.length/3,getX(i){return array[i*3]},getY(i){return array[i*3+1]},getZ(i){return array[i*3+2]},setXYZ(i,x,y,z){array[i*3]=x;array[i*3+1]=y;array[i*3+2]=z}};
}
const measurementPosition=positionAttribute(data.mesh.positions),measurementScale={value:1,setScalar(v){this.value=v}};
const measurementMesh={name:'Anatomical female body',geometry:{attributes:{position:measurementPosition,skinIndex:{array:new Uint16Array(data.mesh.skinIndex)},skinWeight:{array:new Float32Array(data.mesh.skinWeight)}},computeVertexNormals(){},computeBoundingBox(){},computeBoundingSphere(){}}};
const measurementState={height:168,bust:92,waist:72,hips:98};
const measurementContext={data,meshRecords:[measurementMesh],state:measurementState,figure:{scale:measurementScale},console};
vm.createContext(measurementContext);
const measurementPatches=JSON.parse(fs.readFileSync(path.join(root,'patches/runtime.json'),'utf8')),measurementPatch=measurementPatches.find(p=>p.name==='measurement geometry implementation');
assert(measurementPatch);const measurementProgram=measurementPatch.after.slice(0,-'\nfunction change(k,val){'.length);vm.runInContext(measurementProgram,measurementContext);
measurementContext.initMeasurementGeometry();
function sectionPerimeter(y){
 const p=measurementPosition.array,segs=[];
 for(let k=0;k<data.mesh.indices.length;k+=3){
  const ids=data.mesh.indices.slice(k,k+3),hits=[];
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
  components.push({centroidAbsX:Math.abs(sumX/count),perimeter});
 }
 components.sort((a,b)=>a.centroidAbsX-b.centroidAbsX||b.perimeter-a.perimeter);assert(components.length,'No section contour found');return components[0].perimeter*100*measurementScale.value;
}
const measurementAxes={hips:[75,98,140],waist:[50,72,120],bust:[70,92,130],height:[145,168,195]},sectionY={hips:.86,waist:1.08,bust:1.24};
let measurementCases=0,worstMeasurementError=0,worstMeasurementCase=null;
for(const hips of measurementAxes.hips)for(const waist of measurementAxes.waist)for(const bust of measurementAxes.bust)for(const height of measurementAxes.height){
 Object.assign(measurementState,{hips,waist,bust,height});measurementContext.applyMeasurements();measurementCases++;
 const got={hips:sectionPerimeter(sectionY.hips),waist:sectionPerimeter(sectionY.waist),bust:sectionPerimeter(sectionY.bust)};
 for(const key of ['hips','waist','bust']){const error=Math.abs(got[key]-measurementState[key]);if(error>worstMeasurementError){worstMeasurementError=error;worstMeasurementCase={hips,waist,bust,height,axis:key,target_cm:measurementState[key],measured_cm:got[key]}}}
}
assert.equal(measurementCases,81);assert(worstMeasurementError<=.10,`Measurement geometry exceeds 0.10 cm boundary tolerance: ${JSON.stringify(worstMeasurementCase)}`);
console.log('MEASUREMENT_GEOMETRY_RESULTS '+JSON.stringify({cases:measurementCases,coverage:'exhaustive min/default/max Cartesian product for bust/waist/hips/height',worst_section_circumference_error_cm:worstMeasurementError,worst_case:worstMeasurementCase,limitations:'Fixture section matching only; not body reconstruction, garment grading/ease, pressure, comfort or physical fit',physical_fit_validated:false}));
