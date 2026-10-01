function maskCoveredBody(){
 const m=data.mesh,H=data.height,kept=[];
 const covered=(x,y,z)=>{
   const lower=y>H*.067+.005 && y<H*.553 && Math.abs(x)<.228;
   const h=y/H,ax=Math.abs(x),width=h<.724?.218:.218-(h-.724)*.54;
   const neck=H*(z>0?.742+Math.min(1,ax/.095)*.115:.820+Math.min(1,ax/.105)*.045);
   const upper=y>H*.553+.004 && y<H*.847-.004 && ax<width-.004 && y<neck-.004;
   return lower||upper;
 };
 for(let i=0;i<m.indices.length;i+=3){const tri=m.indices.slice(i,i+3);if(!tri.every(id=>covered(...m.positions.slice(id*3,id*3+3))))kept.push(...tri);}
 body.geometry.setIndex(kept);
 body.geometry.userData.coverageMask='matching garment cut fields with 4mm boundary reserve';
}
