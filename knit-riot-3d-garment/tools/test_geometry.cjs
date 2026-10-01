const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const root=path.resolve(__dirname,'..');
const data=JSON.parse(fs.readFileSync(path.join(root,'fixtures/runtime/assets/body.json'),'utf8'));
const context={};vm.createContext(context);
vm.runInContext(fs.readFileSync(path.join(root,'patches/refine.js'),'utf8'),context);
const original=JSON.stringify(data.mesh),out=context.refineTextileSurface(data.mesh),groups=new Map();
let moved=0,maxShift=0,maxSeam=0,normalError=0;
assert.equal(JSON.stringify(data.mesh),original,'source body was mutated');
assert.equal(out.positions.length,data.mesh.positions.length);
assert.deepEqual(out.indices,data.mesh.indices);
assert.deepEqual(out.skinIndex,data.mesh.skinIndex);
assert.deepEqual(out.skinWeight,data.mesh.skinWeight);
for(let i=0;i<out.positions.length/3;i++){
  const xyz=out.positions.slice(i*3,i*3+3),n=out.normals.slice(i*3,i*3+3),old=data.mesh.positions.slice(i*3,i*3+3);
  assert(xyz.every(Number.isFinite)&&n.every(Number.isFinite));
  const distance=Math.hypot(...xyz.map((a,k)=>a-old[k]));
  if(distance>1e-9)moved++;
  maxShift=Math.max(maxShift,distance);
  assert(xyz[0]===old[0]&&xyz[1]===old[1]);
  if(old[1]<1.03||old[1]>1.37||Math.abs(old[0])>.21||old[2]<.015)assert(distance<1e-9,'outside garment refinement region changed');
  const key=data.mesh.sourceVertex[i];
  if(groups.has(key))maxSeam=Math.max(maxSeam,Math.hypot(...xyz.map((a,k)=>a-groups.get(key)[k])));
  groups.set(key,xyz);
  normalError=Math.max(normalError,Math.abs(Math.hypot(...n)-1));
}
assert(moved>100);assert(maxSeam<1e-10);assert(normalError<1e-10);
const result={source_body_unchanged:true,topology_preserved:true,skin_indices_preserved:true,skin_weights_preserved:true,finite_coordinates:true,maximum_welded_seam_gap_metres:maxSeam,maximum_normal_length_error:normalError,changed_render_vertices:moved,maximum_depth_change_metres:maxShift,physical_fit_validated:false};
console.log('GEOMETRY_UNIT_RESULTS '+JSON.stringify(result));
