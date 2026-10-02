// Artistic garment envelope; not a measured cloth or pressure solver.
function refineTextileSurface(m) {
  const count = m.positions.length / 3;
  const keyOf = m.sourceVertex || Array.from({length: count}, (_, i) => i);
  const copies = new Map();
  for (let i = 0; i < count; i++) {
    const key = keyOf[i];
    if (!copies.has(key)) copies.set(key, []);
    copies.get(key).push(i);
  }
  const ids = [...copies.keys()];
  const pos = new Map(ids.map(k => [k, m.positions.slice(copies.get(k)[0]*3, copies.get(k)[0]*3+3)]));
  const adjacent = new Map(ids.map(k => [k, new Set()]));
  for (let t = 0; t < m.indices.length; t += 3) {
    const tri = m.indices.slice(t, t+3).map(i => keyOf[i]);
    for (const a of tri) for (const b of tri) if (a !== b) adjacent.get(a).add(b);
  }
  const ease = (a,b,x) => {const t = Math.max(0,Math.min(1,(x-a)/(b-a))); return t*t*(3-2*t);};
  const weight = (x,y,z) => ease(1.03,1.10,y)*(1-ease(1.30,1.37,y))*(1-ease(.16,.21,Math.abs(x)))*ease(.015,.060,z);
  // Use shared source vertices rather than smoothing UV-split islands separately.
  for (let iter=0; iter<36; iter++) {
    const next = new Map();
    for (const k of ids) {
      const [x,y,z] = pos.get(k), ns = adjacent.get(k);
      let sum=0; for (const j of ns) sum += pos.get(j)[2];
      const mean = ns.size ? sum/ns.size : z;
      next.set(k, [x,y,z+.6*weight(x,y,z)*(mean-z)]);
    }
    for (const [k,v] of next) pos.set(k,v);
  }
  // Bridge the two breast contours with a smooth shared front envelope.
  const rows=[];
  for (let r=0;r<=44;r++) {
    const y=1.02+r*.008;
    let peak=0;
    for (const k of ids) {
      const [x,yy,z]=pos.get(k);
      if (Math.abs(x)<.14 && Math.abs(yy-y)<.024) peak=Math.max(peak,z);
    }
    rows.push(peak);
  }
  const blurred=rows.map((_,r)=>{let total=0,n=0;for(let d=-2;d<=2;d++){const j=Math.max(0,Math.min(rows.length-1,r+d)),w=3-Math.abs(d);total+=rows[j]*w;n+=w;}return total/n;});
  const out={...m,positions:[...m.positions],normals:new Array(m.normals.length).fill(0)};
  for (const k of ids) {
    const v=pos.get(k), [x,y,z]=v, r=Math.max(0,Math.min(43.999,(y-1.02)/.008));
    const peak=blurred[Math.floor(r)]*(1-r%1)+blurred[Math.floor(r)+1]*(r%1);
    const envelope=peak*Math.sqrt(Math.max(0,1-Math.pow(Math.abs(x)/.215,4)));
    // Broad artistic clearance, not nipple-shaped point corrections or body deletion.
    v[2]=z+weight(x,y,z)*(envelope-z+.003);
    for(const i of copies.get(k)) for(let a=0;a<3;a++) out.positions[3*i+a]=v[a];
  }
  const normals=new Map(ids.map(k=>[k,[0,0,0]])), p=out.positions;
  for(let t=0;t<m.indices.length;t+=3) {
    const tri=m.indices.slice(t,t+3), [a,b,c]=tri.map(i=>i*3);
    const u=[p[b]-p[a],p[b+1]-p[a+1],p[b+2]-p[a+2]], v=[p[c]-p[a],p[c+1]-p[a+1],p[c+2]-p[a+2]];
    const n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
    for(const i of tri) for(let k=0;k<3;k++) normals.get(keyOf[i])[k]+=n[k];
  }
  for(let i=0;i<count;i++) {
    let n=normals.get(keyOf[i]), l=Math.hypot(...n);
    if(l<1e-10){n=m.normals.slice(i*3,i*3+3);l=Math.hypot(...n)||1;}
    for(let k=0;k<3;k++) out.normals[i*3+k]=n[k]/l;
  }
  return out;
}

// Increase tessellation only around analytic garment cut fields before clipping.
// This reduces visible polygon faceting at armholes/neckline without changing the body mesh.
// Interpolated skin weights remain normalized; this is rendering geometry, not physical-fit validation.
function subdivideTextileClipBoundary(m, fields, passes=2, band=.022) {
  let current=m;
  const vertex=(mesh,id)=>({
    p:mesh.positions.slice(id*3,id*3+3),
    n:mesh.normals.slice(id*3,id*3+3),
    u:mesh.uv.slice(id*2,id*2+2),
    i:mesh.skinIndex.slice(id*4,id*4+4),
    w:mesh.skinWeight.slice(id*4,id*4+4)
  });
  const mix=(a,b)=>{
    const weights=new Map();
    for(let k=0;k<4;k++){
      weights.set(a.i[k],(weights.get(a.i[k])||0)+.5*a.w[k]);
      weights.set(b.i[k],(weights.get(b.i[k])||0)+.5*b.w[k]);
    }
    const top=[...weights].filter(q=>q[1]>0).sort((a,b)=>b[1]-a[1]).slice(0,4);
    const total=top.reduce((sum,q)=>sum+q[1],0)||1;
    while(top.length<4)top.push([0,0]);
    const n=a.n.map((v,k)=>(v+b.n[k])*.5), nl=Math.hypot(...n)||1;
    return {p:a.p.map((v,k)=>(v+b.p[k])*.5),n:n.map(v=>v/nl),u:a.u.map((v,k)=>(v+b.u[k])*.5),i:top.map(q=>q[0]),w:top.map(q=>q[1]/total)};
  };
  for(let pass=0;pass<passes;pass++){
    const positions=[],normals=[],uv=[],skinIndex=[],skinWeight=[],indices=[];
    const emit=v=>{const total=v.w.reduce((sum,x)=>sum+x,0)||1;positions.push(...v.p);normals.push(...v.n);uv.push(...v.u);skinIndex.push(...v.i);skinWeight.push(...v.w.map(x=>x/total));indices.push(indices.length);};
    for(let t=0;t<current.indices.length;t+=3){
      const tri=current.indices.slice(t,t+3).map(id=>vertex(current,id));
      const near=fields.some(field=>{
        const q=tri.map(v=>field(...v.p)), lo=Math.min(...q), hi=Math.max(...q);
        return (lo<=0&&hi>=0)||Math.min(...q.map(Math.abs))<band;
      });
      if(!near){tri.forEach(emit);continue;}
      const [a,b,c]=tri,ab=mix(a,b),bc=mix(b,c),ca=mix(c,a);
      for(const face of [[a,ab,ca],[ab,b,bc],[ca,bc,c],[ab,bc,ca]])face.forEach(emit);
    }
    current={positions,normals,uv,skinIndex,skinWeight,indices};
    band*=.55;
  }
  return current;
}

// Apply uniform artistic torso clearance in the horizontal radial plane.
// This avoids turning local triangulation-normal variation into a scalloped garment cut edge.
// It remains a visual envelope, not a cloth-pressure or physical-fit solver.
function offsetTextileRadially(g, distance) {
  const p = g.attributes.position;
  for (let i = 0; i < p.count; i++) {
    const x = p.getX(i), y = p.getY(i), z = p.getZ(i), r = Math.hypot(x, z) || 1;
    p.setXYZ(i, x + distance*x/r, y, z + distance*z/r);
  }
  p.needsUpdate = true;
  g.computeBoundingBox();
  g.computeBoundingSphere();
  return g;
}
