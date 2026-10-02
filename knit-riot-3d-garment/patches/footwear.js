// Anatomical-fixture-derived, closed procedural slip-ons with a real vamp and counter.
// Artistic development geometry only: not a scanned product, last, or fit validation.
{
  const hullOf=points=>{
    const sorted=[...new Map(points.map(p=>[p.map(v=>Math.round(v*1e7)).join(','),p])).values()].sort((a,b)=>a[0]-b[0]||a[1]-b[1]);
    if(sorted.length<3)throw Error('Insufficient anatomical footwear contour');
    const cross=(a,b,c)=>(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);
    const lower=[],upper=[];
    for(const p of sorted){while(lower.length>1&&cross(lower.at(-2),lower.at(-1),p)<=0)lower.pop();lower.push(p);}
    for(const p of [...sorted].reverse()){while(upper.length>1&&cross(upper.at(-2),upper.at(-1),p)<=0)upper.pop();upper.push(p);}
    return lower.slice(0,-1).concat(upper.slice(0,-1));
  };
  const radiusAt=(hull,cx,cz,angle)=>{
    const dx=Math.cos(angle),dz=Math.sin(angle);let radius=0;
    for(let i=0;i<hull.length;i++){
      const a=hull[i],b=hull[(i+1)%hull.length],ax=a[0]-cx,az=a[1]-cz,ex=b[0]-a[0],ez=b[1]-a[1];
      const den=dx*ez-dz*ex;if(Math.abs(den)<1e-12)continue;
      const r=(ax*ez-az*ex)/den,s=(ax*dz-az*dx)/den;
      if(r>0&&s>=-1e-7&&s<=1+1e-7)radius=Math.max(radius,r);
    }
    if(!(radius>0))throw Error('Anatomical shoe contour does not surround ankle');
    return radius;
  };
  boots=new T.Group();boots.name='White slip-on shoes';figure.add(boots);
  const upperMat=new T.MeshPhysicalMaterial({color:'#f3f0e9',roughness:.62,metalness:0,clearcoat:.035,clearcoatRoughness:.65,side:T.DoubleSide});
  const soleMat=new T.MeshPhysicalMaterial({color:'#c9c5bd',roughness:.78,metalness:0,side:T.DoubleSide});
  const N=96,ROWS=18;
  for(let side=0;side<2;side++){
    const matches=x=>side?x>=0:x<0;
    const foot=[];let bottom=Infinity;
    for(let i=0;i<m.positions.length;i+=3){
      const x=m.positions[i],y=m.positions[i+1],z=m.positions[i+2];
      if(matches(x)&&y<H*.080){foot.push({id:i/3,x,y,z});bottom=Math.min(bottom,y);}
    }
    const collarY=bottom+H*.044,soleH=H*.0032,soleBottom=bottom-H*.0014,upperBase=soleBottom+soleH*.80;
    const triangles=[],cut=[];
    for(let i=0;i<m.indices.length;i+=3){
      const ids=m.indices.slice(i,i+3),v=ids.map(id=>m.positions.slice(id*3,id*3+3));
      if(!v.every(p=>matches(p[0]))||Math.min(...v.map(p=>p[1]))>collarY+H*.012)continue;
      triangles.push(v);
      for(let k=0;k<3;k++){
        const a=v[k],b=v[(k+1)%3];
        if((a[1]<=collarY&&b[1]>collarY)||(b[1]<=collarY&&a[1]>collarY)){
          const t=(collarY-a[1])/(b[1]-a[1]);cut.push([a[0]+t*(b[0]-a[0]),a[2]+t*(b[2]-a[2])]);
        }
      }
    }
    const innerHull=hullOf(cut),outerHull=hullOf(foot.filter(p=>p.y<=collarY).map(p=>[p.x,p.z]));
    const cx=(Math.min(...cut.map(p=>p[0]))+Math.max(...cut.map(p=>p[0])))/2;
    const cz=(Math.min(...cut.map(p=>p[1]))+Math.max(...cut.map(p=>p[1])))/2;
    const outer=[],inner=[];
    for(let i=0;i<N;i++){
      const a=i*2*Math.PI/N;
      inner.push(radiusAt(innerHull,cx,cz,a)+H*.0012);
      outer.push(Math.max(radiusAt(outerHull,cx,cz,a)+H*.0032,inner[i]+H*.004));
    }
    const footSurface=(x,z)=>{
      let top=bottom;
      for(const v of triangles){
        const [a,b,c]=v;
        if(x<Math.min(a[0],b[0],c[0])-1e-8||x>Math.max(a[0],b[0],c[0])+1e-8||z<Math.min(a[2],b[2],c[2])-1e-8||z>Math.max(a[2],b[2],c[2])+1e-8)continue;
        const den=(b[2]-c[2])*(a[0]-c[0])+(c[0]-b[0])*(a[2]-c[2]);if(Math.abs(den)<1e-12)continue;
        const u=((b[2]-c[2])*(x-c[0])+(c[0]-b[0])*(z-c[2]))/den;
        const v0=((c[2]-a[2])*(x-c[0])+(a[0]-c[0])*(z-c[2]))/den,w=1-u-v0;
        if(Math.min(u,v0,w)<-1e-7)continue;
        const y=u*a[1]+v0*b[1]+w*c[1];if(y<=collarY+H*.001)top=Math.max(top,y);
      }
      return top;
    };
    const attach=g=>{
      const p=g.attributes.position,si=[],sw=[];
      for(let i=0;i<p.count;i++){
        let best=foot[0],distance=Infinity;
        for(const v of foot){const d=(p.getX(i)-v.x)**2+(p.getY(i)-v.y)**2+(p.getZ(i)-v.z)**2;if(d<distance){distance=d;best=v;}}
        for(let k=0;k<4;k++){si.push(m.skinIndex[best.id*4+k]);sw.push(m.skinWeight[best.id*4+k]);}
      }
      g.setAttribute('skinIndex',new T.Uint16BufferAttribute(si,4));g.setAttribute('skinWeight',new T.Float32BufferAttribute(sw,4));
    };
    const add=(part,g,material)=>{
      attach(g);const shoe=new T.SkinnedMesh(g,material);shoe.name='White slip-on '+(side?'right':'left')+' '+part;
      shoe.castShadow=true;shoe.receiveShadow=true;shoe.frustumCulled=false;boots.add(shoe);shoe.bind(skeleton,new T.Matrix4());meshRecords.push(shoe);
      shoe.userData.developmentGeometry='Synthetic anatomical contour; artistic clearance, not physical product validation';
    };
    const outline=new T.Shape();
    for(let i=0;i<N;i++){
      const a=i*2*Math.PI/N,x=cx+outer[i]*Math.cos(a),z=cz+outer[i]*Math.sin(a);
      if(i===0)outline.moveTo(x,-z);else outline.lineTo(x,-z);
    }
    outline.closePath();
    const sole=new T.ExtrudeGeometry(outline,{depth:soleH,steps:1,bevelEnabled:true,bevelSegments:3,bevelThickness:H*.0005,bevelSize:H*.0007});
    sole.rotateX(-Math.PI/2);sole.translate(0,soleBottom,0);sole.computeVertexNormals();add('sole',sole,soleMat);
    const positions=[],uv=[],indices=[];
    for(let row=0;row<=ROWS;row++)for(let i=0;i<N;i++){
      const t=row/ROWS,a=i*2*Math.PI/N,front=(Math.sin(a)+1)/2;
      const r=outer[i]*(1-t)+inner[i]*t,x=cx+r*Math.cos(a),z=cz+r*Math.sin(a);
      const exponent=.30+.34*front;
      let y=upperBase+(collarY-upperBase)*Math.pow(Math.sin(t*Math.PI/2),exponent);
      if(row>0&&row<ROWS)y=Math.max(y,footSurface(x,z)+H*.0020);
      positions.push(x,y,z);uv.push(i/N,t);
    }
    for(let row=0;row<ROWS;row++)for(let i=0;i<N;i++){
      const j=(i+1)%N,a=row*N+i,b=row*N+j,c=(row+1)*N+i,d=(row+1)*N+j;
      indices.push(a,c,b,b,c,d);
    }
    // A thin interior lining and closed collar avoid a single paper-thin surface.
    const count=positions.length/3,outerIndices=indices.slice();
    for(let i=0;i<count;i++){positions.push(positions[i*3],positions[i*3+1]-H*.0011,positions[i*3+2]);uv.push(uv[i*2],uv[i*2+1]);}
    for(let i=0;i<outerIndices.length;i+=3)indices.push(outerIndices[i]+count,outerIndices[i+2]+count,outerIndices[i+1]+count);
    for(const row of [0,ROWS])for(let i=0;i<N;i++){
      const j=(i+1)%N,a=row*N+i,b=row*N+j;
      if(row===ROWS)indices.push(a,a+count,b,b,a+count,b+count);
      else indices.push(a,b,a+count,b,b+count,a+count);
    }
    const upper=new T.BufferGeometry();upper.setAttribute('position',new T.Float32BufferAttribute(positions,3));upper.setAttribute('uv',new T.Float32BufferAttribute(uv,2));upper.setIndex(indices);upper.computeVertexNormals();
    add('upper',upper,upperMat);
  }
}
