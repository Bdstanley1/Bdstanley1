function maskCoveredBody(){
 const m=data.mesh,H=data.height,kept=[];
 // Preserve the complete upper body: hidden torso triangles otherwise leave
 // background-visible holes through an open armhole in side/posed views.
 // The smooth vest envelope provides artistic clearance instead of deleting skin.
 const covered=(x,y)=>y>H*.067+.005 && y<H*.553 && Math.abs(x)<.228;
 for(let i=0;i<m.indices.length;i+=3){
   const tri=m.indices.slice(i,i+3);
   if(!tri.every(id=>covered(...m.positions.slice(id*3,id*3+3))))kept.push(...tri);
 }
 body.geometry.setIndex(kept);
 body.geometry.userData.coverageMask='Lower fully wrapped leggings only; complete upper-body skin retained at every armhole and neckline';
}
