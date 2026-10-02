// Fixture-level vest binding geometry invariants; not visual or physical-fit approval.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert/strict');
const root=path.resolve(__dirname,'..');
const data=JSON.parse(fs.readFileSync(path.join(root,'fixtures/runtime/assets/body.json'),'utf8'));
const context={};vm.createContext(context);vm.runInContext(fs.readFileSync(path.join(root,'patches/refine.js'),'utf8'),context);
const m=context.refineTextileSurface(data.mesh),H=data.height;
const fields=[
 (x,y,z)=>y-H*.553,
 (x,y,z)=>H*.847-y,
 (x,y,z)=>{let h=y/H,t=Math.max(0,Math.min(1,(h-.64)/.207));const side=h<.64?.218:.218-.080*Math.pow(t,.72);return side-Math.abs(x)},
 (x,y,z)=>{const h=y/H,ax=Math.abs(x);return H*(z>0?.742+Math.min(1,ax/.095)*.115:.820+Math.min(1,ax/.105)*.045)-y}
];
function at(id){return {p:m.positions.slice(id*3,id*3+3),n:m.normals.slice(id*3,id*3+3),u:m.uv.slice(id*2,id*2+2),i:m.skinIndex.slice(id*4,id*4+4),w:m.skinWeight.slice(id*4,id*4+4)}}
function mix(a,b,t){const ag=new Map();for(let k=0;k<4;k++){ag.set(a.i[k],(ag.get(a.i[k])||0)+(1-t)*a.w[k]);ag.set(b.i[k],(ag.get(b.i[k])||0)+t*b.w[k]);}const top=[...ag].filter(q=>q[1]>0).sort((a,b)=>b[1]-a[1]).slice(0,4),sum=top.reduce((s,q)=>s+q[1],0)||1;while(top.length<4)top.push([0,0]);return {p:a.p.map((v,k)=>v+(b.p[k]-v)*t),n:a.n.map((v,k)=>v+(b.n[k]-v)*t),u:a.u.map((v,k)=>v+(b.u[k]-v)*t),i:top.map(q=>q[0]),w:top.map(q=>q[1]/sum)}}
const verts=[],indices=[];
for(let j=0;j<m.indices.length;j+=3){let polygon=m.indices.slice(j,j+3).map(at);for(const field of fields){if(!polygon.length)break;let next=[],prev=polygon.at(-1),a=field(...prev.p);for(const v of polygon){const b=field(...v.p);if((a>=0)!=(b>=0)){let t=a/(a-b);next.push(mix(prev,v,Math.min(1,Math.max(0,t))));}if(b>=0)next.push(v);prev=v;a=b;}polygon=next;}if(polygon.length<3)continue;for(let k=1;k<polygon.length-1;k++)for(const v of [polygon[0],polygon[k],polygon[k+1]]){const l=Math.hypot(...v.n)||1,n=v.n.map(q=>q/l);const p=v.p.map((q,a)=>q+n[a]*.013);verts.push({...v,p,n});indices.push(verts.length-1);}}
assert(indices.length>1000,'Vest clip did not produce enough geometry');
const key=i=>verts[i].p.map(x=>Math.round(x*1e5)).join(','),edges=new Map();
for(let t=0;t<indices.length;t+=3){const ids=indices.slice(t,t+3);for(let k=0;k<3;k++){const a=ids[k],b=ids[(k+1)%3],ka=key(a),kb=key(b),s=ka<kb?ka+'|'+kb:kb+'|'+ka,old=edges.get(s);if(old)old.count++;else edges.set(s,{a,b,c:ids[(k+2)%3],count:1});}}
const sub=(a,b)=>a.map((v,k)=>v-b[k]),add=(a,b)=>a.map((v,k)=>v+b[k]),scale=(a,s)=>a.map(v=>v*s),dot=(a,b)=>a.reduce((s,v,k)=>s+v*b[k],0),len=a=>Math.hypot(...a),unit=a=>{const l=len(a);assert(l>1e-10);return scale(a,1/l)},lerp=(a,b,t)=>a.map((v,k)=>v+(b[k]-v)*t),cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
function blendedWeights(a,c,f){const ag=new Map();for(let k=0;k<4;k++){let j=a.i[k],w=a.w[k]*(1-f);ag.set(j,(ag.get(j)||0)+w);j=c.i[k];w=c.w[k]*f;ag.set(j,(ag.get(j)||0)+w);}let top=[...ag].filter(q=>q[1]>1e-8).sort((x,y)=>y[1]-x[1]).slice(0,4),sum=top.reduce((s,q)=>s+q[1],0)||1;while(top.length<4)top.push([0,0]);return top.map(q=>q[1]/sum)}
let boundary=0,maxInset=0,minInset=Infinity,maxPlane=0,maxNormalError=0,maxWeightError=0,minF=Infinity,maxF=0;
for(const edge of edges.values()){
 if(edge.count!==1)continue;boundary++;
 const A=verts[edge.a].p,B=verts[edge.b].p,C=verts[edge.c].p,nA=unit(verts[edge.a].n),nB=unit(verts[edge.b].n),nC=unit(verts[edge.c].n),along=unit(sub(B,A));
 const ca=sub(C,A),inward=add(ca,scale(along,-dot(ca,along))),altitude=len(inward);assert(altitude>1e-8,'Degenerate binding boundary triangle');
 const f=Math.min(.28,.005/Math.max(altitude,1e-6)),D=lerp(A,C,f),E=lerp(B,C,f),nD=unit(lerp(nA,nC,f)),nE=unit(lerp(nB,nC,f));
 const inset=f*altitude;maxInset=Math.max(maxInset,inset);minInset=Math.min(minInset,inset);minF=Math.min(minF,f);maxF=Math.max(maxF,f);
 assert(f>0&&f<=.2800000001);assert(inset<=.005000001,'Binding inset exceeds five millimetres');
 const plane=unit(cross(sub(B,A),sub(C,A)));maxPlane=Math.max(maxPlane,Math.abs(dot(sub(D,A),plane)),Math.abs(dot(sub(E,A),plane)));
 for(const n of [nA,nB,nD,nE])maxNormalError=Math.max(maxNormalError,Math.abs(len(n)-1));
 for(const weights of [blendedWeights(verts[edge.a],verts[edge.c],f),blendedWeights(verts[edge.b],verts[edge.c],f)])maxWeightError=Math.max(maxWeightError,Math.abs(weights.reduce((a,b)=>a+b,0)-1));
}
assert(boundary>100,'Too few vest boundary edges for binding validation');
assert(maxPlane<1e-9,'Binding left the underlying vest triangle plane');assert(maxNormalError<1e-12);assert(maxWeightError<1e-12);
console.log('BINDING_GEOMETRY_RESULTS '+JSON.stringify({boundary_edges_checked:boundary,maximum_binding_inset_metres:maxInset,minimum_binding_inset_metres:minInset,minimum_interpolation_fraction:minF,maximum_interpolation_fraction:maxF,maximum_triangle_plane_error_metres:maxPlane,maximum_normal_length_error:maxNormalError,maximum_skin_weight_sum_error:maxWeightError,limitations:'Fixture-level geometry only; actual rendered pose inspection and physical garment validation remain separate',physical_fit_validated:false}));
