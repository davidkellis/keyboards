import * as THREE from 'three';

// Geometry uses case Z-up coordinates. Each inspection layer translates only
// along Z; at zero separation all original assembly transforms are exact.
export function setupAssembly({cad,board,keys,legends,partMeshes,acrylicGroups,data,materials,camera,stage,onUpdate,onMode}) {
  const $=s=>document.querySelector(s);
  const levels={bottom:0,battery:42,pcb:105,plate:165,top:225,switches:275,caps:320};
  const names={bottom:'Lower case',battery:'5000 mAh battery',pcb:'V11 PCB + electronics',plate:'Acrylic switch plate',top:'Top case frame',switches:'Switches + stabilizers',caps:'Keycaps'};
  const colors={bottom:'#7f9287',battery:'#b18d43',pcb:'#508964',plate:'#6d9dba',top:'#738780',switches:'#647eac',caps:'#9c9e89'};
  const layers=Object.fromEntries(Object.keys(levels).map(id=>{
    const group=new THREE.Group();group.name=names[id];group.userData.assemblyLayer=id;cad.add(group);return [id,group];
  }));
  layers.pcb.add(board);
  const localFrame=()=>{
    const f=new THREE.Group();f.position.set(2.4,2.4,data.originZ);f.rotation.x=data.tilt*Math.PI/180;return f;
  };
  const capFrame=localFrame(),switchFrame=localFrame();layers.caps.add(capFrame);layers.switches.add(switchFrame);
  capFrame.add(keys,legends);
  for(const mesh of [...board.children])if(/Whale|stabilizer/.test(mesh.name))switchFrame.add(mesh);
  const hardware=[];
  for(const mesh of partMeshes) {
    if(mesh.name==='bottom')layers.bottom.add(mesh);
    else if(mesh.name==='board')layers.pcb.add(mesh);
    else if(mesh.name==='bezel')layers.top.add(mesh);
    else if(mesh.name.endsWith('-screw')){layers.bottom.add(mesh);hardware.push(mesh);}
    else if(/-(carrier|nut)$/.test(mesh.name)){layers.top.add(mesh);hardware.push(mesh);}
  }
  const battery=cad.getObjectByName('5044147 nominal battery appearance');layers.battery.add(battery);
  const tape=new THREE.MeshStandardMaterial({color:'#d5ae45',roughness:.6});
  for(const [x,y,w,d] of [[87,83.5,147,1.5],[87,126,147,1.5],[87,85,1.5,41],[232.5,85,1.5,41]]) {
    const strip=new THREE.Mesh(new THREE.BoxGeometry(w,d,5.06),tape);strip.position.set(x+w/2,y+d/2,4.2);strip.name='Pouch edge tape — illustrative';layers.battery.add(strip);
  }
  const labelCanvas=document.createElement('canvas');labelCanvas.width=768;labelCanvas.height=160;
  const ctx=labelCanvas.getContext('2d');ctx.fillStyle='#434c43';ctx.font='500 42px system-ui';ctx.textAlign='center';ctx.fillText('5000 mAh  ·  1S LiPo',384,64);ctx.font='24px system-ui';ctx.fillText('147 × 44 × 5 mm nominal',384,108);
  const texture=new THREE.CanvasTexture(labelCanvas);texture.colorSpace=THREE.SRGBColorSpace;
  const label=new THREE.Mesh(new THREE.PlaneGeometry(105,22),new THREE.MeshBasicMaterial({map:texture,transparent:true,depthWrite:false}));
  label.position.set(160.5,105.5,6.74);label.name='Battery nominal specification label';layers.battery.add(label);
  for(const result of Object.values(acrylicGroups)) {
    layers.plate.add(result.group);layers.top.add(result.frame);
  }
  let amount=0,animation=null;
  const labels=$('#layer-labels'),svg=$('#assembly-leaders');
  const entries=Object.keys(levels).reverse().map(id=>{
    const el=document.createElement('div');el.className='layer-tag';el.textContent=names[id];el.style.setProperty('--layer-color',colors[id]);labels.append(el);
    const line=document.createElementNS('http://www.w3.org/2000/svg','path');line.setAttribute('fill','none');line.setAttribute('stroke',colors[id]);line.setAttribute('stroke-width','1');line.setAttribute('stroke-dasharray','3 4');svg.append(line);
    return {id,el,line};
  });
  function visibility() {
    for(const [id,layer] of Object.entries(layers))layer.visible=$(id==='caps'?'#caps-visible':`#visible-${id}`).checked;
    hardware.forEach(p=>p.visible=$('#visible-hardware').checked);
    const ghost=$('#xray-case').checked;
    for(const material of [materials.shell,materials.base]){material.transparent=ghost;material.opacity=ghost?.19:1;material.depthWrite=!ghost;material.needsUpdate=true;}
    onUpdate(false);
  }
  function apply(v,fit=true) {
    amount=THREE.MathUtils.clamp(v,0,1);
    for(const [id,layer] of Object.entries(layers))layer.position.z=levels[id]*amount;
    for(const p of hardware)if(p.name.endsWith('-screw'))p.position.z=-16*amount;
    $('#separation').value=String(Math.round(amount*100));$('#separation-value').textContent=Math.round(amount*100)+'%';
    $('#assemble').setAttribute('aria-pressed',String(amount<.001));$('#explode').setAttribute('aria-pressed',String(amount>.999));
    $('#assembly-state').textContent=amount<.001?'Assembled':'Exploded · '+Math.round(amount*100)+'%';
    $('#transfer-note').hidden=amount<.001;
    cad.userData.explodedAmount=amount;cad.userData.assemblyNote=data.assemblyNote;
    onUpdate(fit);
  }
  function set(v,animate=false) {
    if(amount<.001&&v>0)onMode('stack');
    else if(animate&&v===0)onMode('hero');
    if(animate&&!matchMedia('(prefers-reduced-motion: reduce)').matches)animation={from:amount,to:v,start:performance.now()};
    else {animation=null;apply(v);}
  }
  function tick(now) {
    if(!animation)return false;
    const t=Math.min(1,(now-animation.start)/450),e=t*t*(3-2*t);apply(animation.from+(animation.to-animation.from)*e);
    if(t===1)animation=null;return true;
  }
  function drawLabels() {
    const visible=amount>.015&&$('#assembly-labels').checked;
    labels.hidden=!visible;svg.style.display=visible?'block':'none';if(!visible)return;
    svg.setAttribute('viewBox',`0 0 ${stage.clientWidth} ${stage.clientHeight}`);
    const list=entries.filter(e=>layers[e.id].visible);
    for(const e of entries){e.el.hidden=!layers[e.id].visible;e.line.style.display=layers[e.id].visible?'':'none';}
    const top=98,bottom=stage.clientHeight-155;
    const labelX=Math.max(8,stage.clientWidth-172);
    const projected=list.map(e=>{
      const base=e.id==='battery'?5:e.id==='bottom'?3:e.id==='caps'?25:e.id==='switches'?20:14;
      const anchor=new THREE.Vector3(e.id==='battery'?226:343,e.id==='battery'?104:64,base+levels[e.id]*amount);
      cad.localToWorld(anchor);anchor.project(camera);
      const x=(anchor.x*.5+.5)*stage.clientWidth,ay=(-anchor.y*.5+.5)*stage.clientHeight;
      return {e,x,ay,y:THREE.MathUtils.clamp(ay-13,top,bottom)};
    }).sort((a,b)=>a.y-b.y);
    let previous=top-34;
    for(const p of projected){p.y=Math.max(p.y,previous+34);previous=p.y;}
    const overflow=Math.max(0,(projected.at(-1)?.y||0)-bottom);
    projected.forEach(({e,x,ay,y:unshifted})=>{
      const y=unshifted-overflow;e.el.style.transform=`translate(${labelX}px,${y}px)`;
      e.line.setAttribute('d',`M ${x} ${ay} L ${labelX-12} ${y+13} L ${labelX} ${y+13}`);
    });
  }
  function drawAnnotations(ctx,sx,sy) {
    if(labels.hidden||getComputedStyle(labels).display==='none')return;
    const bounds=stage.getBoundingClientRect(),dim=$('#room').value==='dim';
    ctx.save();ctx.scale(sx,sy);ctx.lineWidth=1;
    for(const e of entries)if(!e.el.hidden){ctx.strokeStyle=colors[e.id];ctx.setLineDash([3,4]);ctx.stroke(new Path2D(e.line.getAttribute('d')));}
    ctx.setLineDash([]);ctx.font='10px system-ui';ctx.textBaseline='middle';
    for(const e of entries)if(!e.el.hidden){
      const r=e.el.getBoundingClientRect(),x=r.x-bounds.x,y=r.y-bounds.y;
      ctx.fillStyle=dim?'#27332f':'#fafcf7';ctx.strokeStyle=dim?'#4f5e53':'#d2dcd0';
      ctx.beginPath();ctx.roundRect(x,y,r.width,r.height,5);ctx.fill();ctx.stroke();
      ctx.fillStyle=colors[e.id];ctx.fillRect(x,y,3,r.height);ctx.fillStyle=dim?'#e3ebe1':'#41503f';ctx.fillText(names[e.id],x+11,y+r.height/2);
    }
    ctx.restore();
  }
  $('#assemble').addEventListener('click',()=>set(0,true));$('#explode').addEventListener('click',()=>set(1,true));
  $('#separation').addEventListener('input',e=>set(Number(e.target.value)/100));
  for(const id of Object.keys(levels))$(id==='caps'?'#caps-visible':`#visible-${id}`).addEventListener('change',visibility);
  for(const id of ['visible-hardware','xray-case'])$('#'+id).addEventListener('change',visibility);
  $('#assembly-labels').addEventListener('change',()=>onUpdate(false));
  return {layers,levels,names,hardware,set,tick,drawLabels,drawAnnotations,visibility,get amount(){return amount},get animating(){return !!animation}};
}
