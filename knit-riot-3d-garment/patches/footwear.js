// Artistic development slip-on derived from the licensed anatomical foot surface.
{
  const shoe=clipSubset(m,[(x,y)=>H*.052-y],.006),p=shoe.attributes.position;
  const b=[{},{ }];for(const q of b){q.x0=Infinity;q.x1=-Infinity;q.y0=Infinity;q.z0=Infinity;q.z1=-Infinity;}
  for(let i=0;i<p.count;i++){const x=p.getX(i),y=p.getY(i),z=p.getZ(i),q=b[x<0?0:1];q.x0=Math.min(q.x0,x);q.x1=Math.max(q.x1,x);q.y0=Math.min(q.y0,y);q.z0=Math.min(q.z0,z);q.z1=Math.max(q.z1,z);}
  const ease=(a,c,x)=>{const t=Math.max(0,Math.min(1,(x-a)/(c-a)));return t*t*(3-2*t);};
  for(let i=0;i<p.count;i++){
    let x=p.getX(i),y=p.getY(i),z=p.getZ(i);const q=b[x<0?0:1],span=q.z1-q.z0,cx=(q.x0+q.x1)/2,rx=(q.x1-q.x0)/2;
    const front=ease(q.z0+span*.66,q.z1,z),u=Math.min(1,Math.abs(x-cx)/(rx||1));
    if(front>0){const target=q.z1-span*(.045+.10*u*u);z=z*(1-front*.68)+target*(front*.68);x=cx+(x-cx)*(1-front*.10);if(y>q.y0+H*.012){const top=q.y0+H*(.025+.007*(1-u*u));y=Math.max(y,top*front+y*(1-front));}}
    p.setXYZ(i,x,y,z);
  }
  p.needsUpdate=true;shoe.computeVertexNormals();
  const colors=[],upper=new T.Color('#f1eee8'),sole=new T.Color('#cbc8c2');
  for(let i=0;i<p.count;i++){const t=ease(H*.010,H*.023,p.getY(i)),c=sole.clone().lerp(upper,t);colors.push(c.r,c.g,c.b);}
  shoe.setAttribute('color',new T.Float32BufferAttribute(colors,3));
  boots=skinned('White slip-on shoes / smoothed shell',shoe,new T.MeshPhysicalMaterial({vertexColors:true,roughness:.56,metalness:0,clearcoat:.06,clearcoatRoughness:.45,side:T.DoubleSide}));
}
