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
let checked=0,minimum=Infinity,radialMinimum=Infinity,radialChecked=0;
for(let i=0;i<data.mesh.positions.length/3;i++){
 const [x,y,z]=data.mesh.positions.slice(i*3,i*3+3),rx=refined.positions[i*3],ry=refined.positions[i*3+1],rz=refined.positions[i*3+2],r=Math.hypot(rx,rz)||1;
 const ox=rx+.015*rx/r,oz=rz+.015*rz/r;
 if(z>.03&&Math.abs(x)<.215&&y>1.03&&y<1.38){
  const clearance=oz-z;
  assert(clearance>=-1e-7,'Radially offset garment front vertex projects behind intact body');
  checked++;minimum=Math.min(minimum,clearance);
 }
 const h=y/data.height,ax=Math.abs(x),t=Math.max(0,Math.min(1,(h-.64)/.207)),side=h<.64?.218:.218-.080*Math.pow(t,.72),neck=data.height*(z>0?.742+Math.min(1,ax/.095)*.115:.820+Math.min(1,ax/.105)*.045)-y,shoulderT=Math.max(0,Math.min(1,(ax-.045)/.115)),shoulderS=shoulderT*shoulderT*(3-2*shoulderT),top=data.height*(.847-.023*shoulderS)-y;
 if(y-data.height*.553>=0&&top>=0&&side-ax>=0&&neck>=0){
  const clearance=Math.hypot(ox,oz)-Math.hypot(x,z);
  assert(clearance>=.005,'Radial vest clearance fell below 5 mm at a retained source vertex');
  radialChecked++;radialMinimum=Math.min(radialMinimum,clearance);
 }
}
assert(checked>100&&radialChecked>500);

// The shoulder cap must be C1-smooth at both transition points.  This guards
// against the visible angular shoulder step that a piecewise flat/linear cap
// produced in actual detail renders.  It is a rendering boundary invariant,
// not a physical garment-fit claim.
const shoulderCap=ax=>{const t=Math.max(0,Math.min(1,(Math.abs(ax)-.045)/.115)),s=t*t*(3-2*t);return .847-.023*s;};
const capSamples=Array.from({length:117},(_,i)=>shoulderCap(.044+i*.001));
for(let i=1;i<capSamples.length;i++)assert(capSamples[i]<=capSamples[i-1]+1e-12,'Shoulder cap must descend monotonically toward the armhole');
assert(Math.abs(shoulderCap(.045)-.847)<1e-12);
assert(Math.abs(shoulderCap(.160)-.824)<1e-12);
const d=.0001,innerSlope=Math.abs((shoulderCap(.045+d)-shoulderCap(.045-d))/(2*d)),outerSlope=Math.abs((shoulderCap(.160+d)-shoulderCap(.160-d))/(2*d));
assert(innerSlope<.002&&outerSlope<.002,'Shoulder cap transition slope is not visually smooth');
const runtimePatches=fs.readFileSync(path.join(root,'patches/runtime.json'),'utf8');
assert.equal((runtimePatches.match(/\.847-\.023\*s/g)||[]).length,2,'Vest clip and binding shoulder caps must stay synchronized');
assert.equal((runtimePatches.match(/\(ax-\.045\)\/\.115/g)||[]).length,2,'Vest clip and binding shoulder transition ranges must stay synchronized');
const finishPatches=JSON.parse(fs.readFileSync(path.join(root,'patches/finish.json'),'utf8'));
assert.equal(finishPatches.length,1,'Expected one bounded final finishing patch');
assert.match(finishPatches[0].after,/innerTop/,'Inner shoulder join suppression must remain explicit');
assert(runtimePatches.includes(finishPatches[0].before),'Finishing patch must target the assembled binding boundary context');
const builder=fs.readFileSync(path.join(root,'tools/build_runtime.py'),'utf8');
assert(builder.includes("ROOT/'patches/finish.json'"),'Final finishing patch must be registered by build_runtime.py');

console.log('BOUNDARY_GEOMETRY_RESULTS '+JSON.stringify({upper_body_triangles_retained:upperTriangles,front_vertex_projections_checked:checked,minimum_front_vertex_z_projection_clearance_metres:minimum,radial_vest_vertices_checked:radialChecked,minimum_radial_vest_clearance_metres:radialMinimum,limitations:'Source-vertex radial clearance is not triangle collision testing, pose clearance or physical garment-fit validation',physical_fit_validated:false}));
