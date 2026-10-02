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

  const outline=(w,l)=>{
    const s=new T.Shape();
    s.moveTo(0,-l*.55);
    s.bezierCurveTo(-w*.72,-l*.54,-w*1.01,-l*.34,-w*1.02,-l*.10);
    s.bezierCurveTo(-w*.99,l*.17,-w*.73,l*.45,-w*.58,l*.50);
    s.quadraticCurveTo(0,l*.54,w*.58,l*.50);
    s.bezierCurveTo(w*.73,l*.45,w*.99,l*.17,w*1.02,-l*.10);
    s.bezierCurveTo(w*1.01,-l*.34,w*.72,-l*.54,0,-l*.55);
    return s;
  };
  const attachToFoot=(g,side,cx,cz)=>{
    let best=0,bestD=Infinity;
    for(let i=0;i<m.positions.length;i+=3){
      const x=m.positions[i],y=m.positions[i+1],z=m.positions[i+2];
      if((side===0&&x>=0)||(side===1&&x<0)||y>H*.065)continue;
      const dx=x-cx,dy=y-H*.022,dz=z-(cz+H*.010),d=dx*dx+dy*dy+dz*dz;
      if(d<bestD){bestD=d;best=i/3;}
    }
    const p=g.attributes.position,si=[],sw=[];
    for(let i=0;i<p.count;i++)for(let a=0;a<4;a++){si.push(m.skinIndex[best*4+a]);sw.push(m.skinWeight[best*4+a]);}
    g.setAttribute('skinIndex',new T.Uint16BufferAttribute(si,4));
    g.setAttribute('skinWeight',new T.Float32BufferAttribute(sw,4));
  };
  const addShoe=(name,g,material)=>{
    const shoe=new T.SkinnedMesh(g,material);
    shoe.name=name;shoe.castShadow=true;shoe.receiveShadow=true;shoe.frustumCulled=false;
    boots.add(shoe);shoe.bind(skeleton,new T.Matrix4());meshRecords.push(shoe);
  };

  boots=new T.Group();boots.name='White slip-on shoes';figure.add(boots);
  const upperMat=new T.MeshPhysicalMaterial({color:'#f3f0e9',roughness:.48,metalness:0,clearcoat:.10,clearcoatRoughness:.40,side:T.DoubleSide});
  const soleMat=new T.MeshPhysicalMaterial({color:'#c9c5bd',roughness:.70,metalness:0,clearcoat:.025,clearcoatRoughness:.72,side:T.DoubleSide});

  for(const [side,b] of bounds.entries()){
    const anatomyW=(b.x1-b.x0)/2,anatomyL=b.z1-b.z0;
    const cx=(b.x0+b.x1)/2,cz=(b.z0+b.z1)/2;
    const w=anatomyW+H*.0038,l=anatomyL+H*.018;
    const bottom=b.y0-H*.0015,soleH=H*.0044;

    const sole= new T.ExtrudeGeometry(outline(w,l),{depth:soleH,steps:1,curveSegments:16,bevelEnabled:true,bevelSegments:3,bevelThickness:H*.0005,bevelSize:H*.0008});
    sole.rotateX(-Math.PI/2);sole.translate(cx,bottom,cz);sole.computeVertexNormals();
    attachToFoot(sole,side,cx,cz);
    addShoe('White slip-on '+(side?'right':'left')+' sole',sole,soleMat);

    const upperShape=outline(w*.955,l*.945);
    const opening=new T.Path();
    opening.absellipse(0,-l*.13,w*.62,l*.24,0,Math.PI*2,false,0);
    upperShape.holes.push(opening);
    const upperH=H*.046,upperBase=bottom+soleH*.64;
    const upper=new T.ExtrudeGeometry(upperShape,{depth:upperH,steps:1,curveSegments:18,bevelEnabled:true,bevelSegments:4,bevelThickness:H*.0013,bevelSize:H*.0015});
    upper.rotateX(-Math.PI/2);upper.translate(cx,upperBase,cz);
    const p=upper.attributes.position;
    for(let i=0;i<p.count;i++){
      let x=p.getX(i),y=p.getY(i),z=p.getZ(i);
      const t=Math.max(0,Math.min(1,(z-(cz-l*.52))/l));
      const fy=Math.max(0,Math.min(1,(y-upperBase)/upperH));
      const vamp=Math.exp(-Math.pow((t-.66)/.22,2));
      const heel=Math.max(0,1-t/.32);
      const top=H*(.013+.034*vamp+.004*heel);
      x=cx+(x-cx)*(1-.055*fy);
      y=upperBase+fy*top+H*.002*Math.pow(Math.max(0,(t-.78)/.22),2)*fy;
      p.setXYZ(i,x,y,z);
    }
    p.needsUpdate=true;upper.computeVertexNormals();
    attachToFoot(upper,side,cx,cz);
    addShoe('White slip-on '+(side?'right':'left')+' upper',upper,upperMat);
  }
}
