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
    v[2]=z+weight(x,y,z)*(envelope-z);
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
