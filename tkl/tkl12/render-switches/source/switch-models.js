import * as THREE from 'three';
import {RoundedBoxGeometry} from 'three/addons/geometries/RoundedBoxGeometry.js';

// Drawing-based envelopes, not manufacturer CAD. Coordinates are board top view
// with Y towards the back (the native KiCad Y coordinate is inverted at export).
export function buildSwitches(group, family, data, materials, stems) {
  const oldGeometry=new Set();group.traverse(o=>{if(o.geometry)oldGeometry.add(o.geometry)});
  group.clear();oldGeometry.forEach(g=>g.dispose());stems.length=0;
  materials.switch.color.set(family.baseColor);materials.stem.color.set(family.stemColor);
  const T=data.board.thickness,tip=T+family.stemTip;
  const isChoc=family.mount==='choc',isGateron=family.plateTop===2.5;
  const geometries={
    lower:new RoundedBoxGeometry(family.lower,family.lower,family.plateTop,1,.2),
    flange:new RoundedBoxGeometry(family.body,family.body,.8,1,.25),
    cover:new RoundedBoxGeometry(family.body-.4,family.body-.4,isGateron?2.6:2.5,2,.65),
    contact:new THREE.BoxGeometry(.32,.7,3.4),
    post:new THREE.CylinderGeometry(family.postDiameter/2,family.postDiameter/2,2.5,24).rotateX(Math.PI/2)
  };
  const add=(parent,g,mat,x,y,z,name)=>{
    const mesh=new THREE.Mesh(g,mat);mesh.position.set(x,y,z);mesh.name=name;mesh.castShadow=mat!==materials.cover;mesh.receiveShadow=true;parent.add(mesh);return mesh;
  };
  const chocStem=()=>{
    const shape=new THREE.Shape();shape.moveTo(-3.8,-2.5);shape.lineTo(3.8,-2.5);shape.lineTo(3.8,2.5);shape.lineTo(-3.8,2.5);shape.closePath();
    for(const x of [-2.85,2.85]){
      const h=new THREE.Path();h.moveTo(x-.6,-1.4);h.lineTo(x-.6,1.4);h.lineTo(x+.6,1.4);h.lineTo(x+.6,-1.4);h.closePath();shape.holes.push(h);
    }
    return new THREE.ExtrudeGeometry(shape,{depth:2.2,bevelEnabled:false}).translate(0,0,-1.1);
  };
  const crossA=new THREE.BoxGeometry(4.1,1.17,3),crossB=new THREE.BoxGeometry(1.17,4.1,3);
  const twin=isChoc?chocStem():null;
  const collarShape=new THREE.Shape();collarShape.absarc(0,0,2.85,0,Math.PI*2);
  const hole=new THREE.Path();hole.absarc(0,0,2.2,0,Math.PI*2,true);collarShape.holes.push(hole);
  const collar=new THREE.ExtrudeGeometry(collarShape,{depth:2.5,bevelEnabled:false,curveSegments:16}).translate(0,0,-1.7);
  const pegCache=new Map();
  const stabGeometry=new RoundedBoxGeometry(4.6,6.8,3.4,1,.3);
  for(const key of data.switches){
    const [x,y]=key.xy;
    add(group,geometries.lower,materials.switch,x,y,T+family.plateTop/2,`${key.ref} lower housing`);
    add(group,geometries.flange,materials.switch,x,y,T+family.plateTop+.4,`${key.ref} flange`);
    add(group,geometries.cover,materials.cover,x,y,T+family.plateTop+.8+(isGateron?1.3:1.25),`${key.ref} translucent cover`);
    const stem=new THREE.Group();stem.position.set(x,y,tip-(isChoc?1.1:1.5));stem.userData.restZ=stem.position.z;stem.name=`${key.ref} ${isChoc?'two-slot Choc':'MX-cross'} moving stem`;
    if(isChoc)add(stem,twin,materials.stem,0,0,0,'Two rectangular Choc sockets');
    else{
      add(stem,crossA,materials.stem,0,0,0,'MX-cross horizontal');add(stem,crossB,materials.stem,0,0,0,'MX-cross vertical');
      if(!isGateron)add(stem,collar,materials.stem,0,0,0,'Choc V2 round dust collar');
    }
    group.add(stem);stems.push(stem);
    for(const [dx,dy] of family.contacts)add(group,geometries.contact,materials.metal,x+dx,y+dy,T-1.5,`${key.ref} contact at ${dx},${dy}`);
    add(group,geometries.post,materials.switch,x,y,T-1.25,`${key.ref} center locating post`);
    for(const [dx,dy,d] of family.locators){
      if(!pegCache.has(d))pegCache.set(d,new THREE.CylinderGeometry(d/2,d/2,2.4,12).rotateX(Math.PI/2));
      add(group,pegCache.get(d),materials.switch,x+dx,y+dy,T-1.2,`${key.ref} side locating post`);
    }
    if(key.units>=2)for(const sign of [-1,1])add(group,stabGeometry,materials.chip,x+sign*(key.units>=6?50:11.9),y,T+1.7,`${key.ref} stabilizer — illustrative, verify family`);
  }
  group.name=`86 ${family.name} switches — drawing-based appearance`;
  group.userData={assemblyLayer:'switches',family:family.family,mount:family.mount,plateTop:family.plateTop,stemTip:family.stemTip,physicalFitVerified:false};
}
