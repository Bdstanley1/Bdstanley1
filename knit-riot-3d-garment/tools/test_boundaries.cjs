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
const H=data.height,fields=[(x,y,z)=>y-H*.553,(x,y,z)=>H*(.847-Math.max(0,Math.abs(x)-.06)*.23)-y,(x,y,z)=>{let h=y/H,t=Math.max(0,Math.min(1,(h-.64)/.207));const side=h<.64?.218:.218-.080*Math.pow(t,.72);return side-Math.abs(x)},(x,y,z)=>{const h=y/H,ax=Math.abs(x);return H*(z>0?.742+Math.min(1,ax/.095)*.115:.820+Math.min(1,ax/.105)*.045)-y}];
function maxCrossingEdge(mesh,field){let max=0,crossing=0;for(let t=0;t<mesh.indices.length;t+=3){const ids=mesh.indices.slice(t,t+3),q=ids.map(id=>field(...mesh.positions.slice(id*3,id*3+3)));if(Math.min(...q)<=0&&Math.max(...q)>=0){crossing++;for(let a=0;a<3;a++)for(let b=a+1;b<3;b++){const A=mesh.positions.slice(ids[a]*3,ids[a]*3+3),B=mesh.positions.slice(ids[b]*3,ids[b]*3+3);max=Math.max(max,Math.hypot(...A.map((v,k)=>v-B[k])));}}}return {max,crossing};}
const coarse=maxCrossingEdge(refined,fields[2]),subdivided=context.subdivideTextileClipBoundary(refined,fields,2,.022),fine=maxCrossingEdge(subdivided,fields[2]);
assert(subdivided.indices.length>refined.indices.length,'boundary tessellation did not add triangles');
assert.equal(subdivided.positions.length,subdivided.normals.length);assert.equal(subdivided.positions.length/3,subdivided.uv.length/2);assert.equal(subdivided.positions.length/3,subdivided.skinIndex.length/4);assert.equal(subdivided.skinIndex.length,subdivided.skinWeight.length);
assert(coarse.crossing>0&&fine.crossing>coarse.crossing,'armhole boundary crossing resolution did not increase');
assert(fine.max<coarse.max*.40,'armhole boundary segments were not sufficiently refined');
for(let i=0;i<subdivided.skinWeight.length;i+=4){const w=subdivided.skinWeight.slice(i,i+4);assert(w.every(Number.isFinite));assert(Math.abs(w.reduce((a,b)=>a+b,0)-1)<1e-6,'interpolated skin weights not normalized');}
let checked=0,minimum=Infinity,radialMinimum=Infinity,radialChecked=0;
for(let i=0;i<data.mesh.positions.length/3;i++){
 const [x,y,z]=data.mesh.positions.slice(i*3,i*3+3),rx=refined.positions[i*3],ry=refined.positions[i*3+1],rz=refined.positions[i*3+2],r=Math.hypot(rx,rz)||1;
 const ox=rx+.015*rx/r,oz=rz+.015*rz/r;
 if(z>.03&&Math.abs(x)<.215&&y>1.03&&y<1.38){
  const clearance=oz-z;
  assert(clearance>=-1e-7,'Radially offset garment front vertex projects behind intact body');
  checked++;minimum=Math.min(minimum,clearance);
 }
 const h=y/data.height,ax=Math.abs(x),t=Math.max(0,Math.min(1,(h-.64)/.207)),side=h<.64?.218:.218-.080*Math.pow(t,.72),neck=data.height*(z>0?.742+Math.min(1,ax/.095)*.115:.820+Math.min(1,ax/.105)*.045)-y,top=data.height*(.847-Math.max(0,ax-.06)*.23)-y;
 if(y-data.height*.553>=0&&top>=0&&side-ax>=0&&neck>=0){
  const clearance=Math.hypot(ox,oz)-Math.hypot(x,z);
  assert(clearance>=.005,'Radial vest clearance fell below 5 mm at a retained source vertex');
  radialChecked++;radialMinimum=Math.min(radialMinimum,clearance);
 }
}
assert(checked>100&&radialChecked>500);
console.log('BOUNDARY_GEOMETRY_RESULTS '+JSON.stringify({upper_body_triangles_retained:upperTriangles,front_vertex_projections_checked:checked,minimum_front_vertex_z_projection_clearance_metres:minimum,radial_vest_vertices_checked:radialChecked,minimum_radial_vest_clearance_metres:radialMinimum,armhole_boundary_max_edge_before_metres:coarse.max,armhole_boundary_max_edge_after_metres:fine.max,armhole_boundary_crossings_before:coarse.crossing,armhole_boundary_crossings_after:fine.crossing,limitations:'Source-vertex radial clearance and boundary tessellation are not triangle collision testing, pose clearance or physical garment-fit validation',physical_fit_validated:false}));
