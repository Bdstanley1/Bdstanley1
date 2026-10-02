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
 const h=y/data.height,ax=Math.abs(x),t=Math.max(0,Math.min(1,(h-.64)/.207)),side=h<.64?.218:.218-.080*Math.pow(t,.72),neck=data.height*(z>0?.742+Math.min(1,ax/.095)*.115:.820+Math.min(1,ax/.105)*.045)-y,top=data.height*(.847-Math.max(0,ax-.06)*.23)-y;
 if(y-data.height*.553>=0&&top>=0&&side-ax>=0&&neck>=0){
  const clearance=Math.hypot(ox,oz)-Math.hypot(x,z);
  assert(clearance>=.005,'Radial vest clearance fell below 5 mm at a retained source vertex');
  radialChecked++;radialMinimum=Math.min(radialMinimum,clearance);
 }
}
assert(checked>100&&radialChecked>500);
console.log('BOUNDARY_GEOMETRY_RESULTS '+JSON.stringify({upper_body_triangles_retained:upperTriangles,front_vertex_projections_checked:checked,minimum_front_vertex_z_projection_clearance_metres:minimum,radial_vest_vertices_checked:radialChecked,minimum_radial_vest_clearance_metres:radialMinimum,limitations:'Source-vertex radial clearance is not triangle collision testing, pose clearance or physical garment-fit validation',physical_fit_validated:false}));
