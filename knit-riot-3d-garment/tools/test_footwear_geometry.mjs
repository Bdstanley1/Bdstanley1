// Numerical topology checks of actual procedural footwear; not physical-fit evidence.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import * as T from '../fixtures/runtime/three.module.js';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const data=JSON.parse(fs.readFileSync(path.join(root,'fixtures/runtime/assets/body.json'),'utf8'));
const m=data.mesh,H=data.height,source=JSON.stringify(m),figure=new T.Group();
const r=data.rig,bones=r.names.map((name,i)=>{
  const b=new T.Bone();b.name=name;b.position.fromArray(r.heads[i]);
  if(r.parents[i]>=0)b.position.sub(new T.Vector3(...r.heads[r.parents[i]]));return b;
});
bones.forEach((b,i)=>{if(r.parents[i]>=0)bones[r.parents[i]].add(b);else figure.add(b);});
figure.updateMatrixWorld(true);
const skeleton=new T.Skeleton(bones,bones.map(b=>b.matrixWorld.clone().invert())),meshRecords=[];
const program=fs.readFileSync(path.join(root,'patches/footwear.js'),'utf8');
new Function('T','m','H','figure','skeleton','meshRecords','let boots;\n'+program)(T,m,H,figure,skeleton,meshRecords);
assert.equal(JSON.stringify(m),source,'Footwear construction mutated the source body');
assert.equal(meshRecords.length,4,'Expected two separate uppers and soles');
const evidence=[];
for(const mesh of meshRecords){
  const g=mesh.geometry,p=g.attributes.position,n=g.attributes.normal,sw=g.attributes.skinWeight,si=g.attributes.skinIndex;
  assert.equal(mesh.skeleton,skeleton);assert.equal(sw.count,p.count);assert.equal(si.count,p.count);
  let maxWeightError=0,maxNormalError=0;
  for(let i=0;i<p.count;i++){
    assert([p.getX(i),p.getY(i),p.getZ(i),n.getX(i),n.getY(i),n.getZ(i)].every(Number.isFinite));
    maxNormalError=Math.max(maxNormalError,Math.abs(Math.hypot(n.getX(i),n.getY(i),n.getZ(i))-1));
    let sum=0;
    for(let j=0;j<4;j++){const w=sw.array[i*4+j],index=si.array[i*4+j];assert(w>=0&&w<=1&&index>=0&&index<bones.length);sum+=w;}
    maxWeightError=Math.max(maxWeightError,Math.abs(sum-1));
  }
  assert(maxWeightError<1e-5);assert(maxNormalError<1e-5);
  const topology={};
  if(mesh.name.endsWith('upper')){
    assert(g.index,'Upper must retain its indexed lining topology');
    const edges=new Map();let signedVolume=0;
    const a=new T.Vector3(),b=new T.Vector3(),c=new T.Vector3(),cross=new T.Vector3();
    for(let i=0;i<g.index.count;i+=3){
      const ids=[g.index.getX(i),g.index.getX(i+1),g.index.getX(i+2)];
      a.fromBufferAttribute(p,ids[0]);b.fromBufferAttribute(p,ids[1]);c.fromBufferAttribute(p,ids[2]);
      signedVolume+=a.dot(cross.crossVectors(b,c))/6;
      for(let j=0;j<3;j++){
        const u=ids[j],v=ids[(j+1)%3],key=Math.min(u,v)+','+Math.max(u,v);
        const old=edges.get(key)||{count:0,direction:0};old.count++;old.direction+=u<v?1:-1;edges.set(key,old);
      }
    }
    assert([...edges.values()].every(e=>e.count===2&&e.direction===0),'Open or inconsistently oriented lining/collar edge');
    assert(signedVolume>1e-7,'Upper lining must have outward orientation and positive volume');
    topology.closed_oriented_edges=edges.size;topology.signed_volume_m3=signedVolume;
  }
  g.computeBoundingBox();assert(g.boundingBox.max.y-g.boundingBox.min.y<.15);
  evidence.push({name:mesh.name,vertices:p.count,maximum_weight_sum_error:maxWeightError,maximum_normal_length_error:maxNormalError,...topology});
}
console.log('FOOTWEAR_GEOMETRY_RESULTS '+JSON.stringify({source_body_unchanged:true,meshes:evidence,physical_fit_validated:false}));
