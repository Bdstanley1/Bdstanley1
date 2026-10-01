// Procedural development slip-ons derived from licensed anatomical foot bounds.
// Artistic footwear geometry only; not a scan, product last, or fit/comfort validation.
{
  const bounds=[{},{}];
  for(const b of bounds){b.x0=Infinity;b.x1=-Infinity;b.y0=Infinity;b.y1=-Infinity;b.z0=Infinity;b.z1=-Infinity;}
  for(let i=0;i<m.positions.length;i+=3){
    const x=m.positions[i],y=m.positions[i+1],z=m.positions[i+2];
    if(y>H*.075)continue;
    const b=bounds[x<0?0:1];
    b.x0=Math.min(b.x0,x);b.x1=Math.max(b.x1,x);b.y0=Math.min(b.y0,y);b.y1=Math.max(b.y1,y);b.z0=Math.min(b.z0,z);b.z1=Math.max(b.z1,z);
  }
  if(bounds.some(b=>!Number.isFinite(b.x0)||b.z1-b.z0<.12))throw Error('Foot bounds unavailable for slip-on construction');
  boots=new T.Group();boots.name='White slip-on shoes';figure.add(boots);
  const upper=new T.Color('#f2efe9'),sole=new T.Color('#cbc8c1');
  const material=new T.MeshPhysicalMaterial({vertexColors:true,roughness:.56,metalness:0,clearcoat:.08,clearcoatRoughness:.42});
  for(const [side,b] of bounds.entries()){
    const cx=(b.x0+b.x1)/2,cz=(b.z0+b.z1)/2,rx=(b.x1-b.x0)*.61,rz=(b.z1-b.z0)*.57;
    const bottom=Math.max(0,b.y0+H*.001),ry=H*.029,cy=bottom+ry;
    const g=new T.SphereGeometry(1,36,22),p=g.attributes.position;
    for(let i=0;i<p.count;i++){
      const ux=p.getX(i),uy=p.getY(i),uz=p.getZ(i);
      const longitudinal=(uz+1)/2;
      const width=.76+.27*Math.sin(Math.PI*Math.min(1,longitudinal*.92));
      let x=cx+ux*rx*width,y=cy+uy*ry,z=cz+uz*rz;
      if(longitudinal>.70){const t=(longitudinal-.70)/.30;x=cx+(x-cx)*(1-.08*t);y+=H*.004*t*(1-uy*uy);}
      if(longitudinal<.23){const t=(.23-longitudinal)/.23;x=cx+(x-cx)*(1-.14*t);}
      if(y<bottom+H*.005)y=bottom+H*.005;
      p.setXYZ(i,x,y,z);
    }
    p.needsUpdate=true;g.computeVertexNormals();
    const colors=[];
    for(let i=0;i<p.count;i++){
      const t=Math.max(0,Math.min(1,(p.getY(i)-(bottom+H*.008))/(H*.012))),c=sole.clone().lerp(upper,t);
      colors.push(c.r,c.g,c.b);
    }
    g.setAttribute('color',new T.Float32BufferAttribute(colors,3));
    let best=0,bestD=Infinity;
    for(let i=0;i<m.positions.length;i+=3){
      const dx=m.positions[i]-cx,dy=m.positions[i+1]-(bottom+H*.025),dz=m.positions[i+2]-cz,d=dx*dx+dy*dy+dz*dz;
      if(d<bestD){bestD=d;best=i/3;}
    }
    const si=[],sw=[];
    for(let i=0;i<p.count;i++)for(let a=0;a<4;a++){si.push(m.skinIndex[best*4+a]);sw.push(m.skinWeight[best*4+a]);}
    g.setAttribute('skinIndex',new T.Uint16BufferAttribute(si,4));g.setAttribute('skinWeight',new T.Float32BufferAttribute(sw,4));
    const shoe=new T.SkinnedMesh(g,material);shoe.name='White slip-on '+(side?'right':'left');shoe.castShadow=true;shoe.receiveShadow=true;shoe.frustumCulled=false;boots.add(shoe);shoe.bind(skeleton,new T.Matrix4());meshRecords.push(shoe);
  }
}
