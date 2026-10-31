import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { toCreasedNormals } from 'three/addons/utils/BufferGeometryUtils.js';
import { GLTFExporter } from 'three/addons/exporters/GLTFExporter.js';

const $ = (s) => document.querySelector(s);
const data = JSON.parse($('#model-data').textContent);
const canvas = $('#viewport');
const stage = $('.studio');
const [width, depth] = data.config.fixed_footprint_mm;
const radians = Math.PI / 180;
let renderer;

try {
  renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false, preserveDrawingBuffer: true });
  init();
} catch (error) {
  console.error(error);
  const loading = $('#loading');
  loading.hidden = false;
  loading.classList.add('failed');
  loading.textContent = '3D could not start. Open this file in Brave or Chrome with hardware acceleration enabled, or use the earlier view gallery.';
}

function init() {
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.12;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.shadowMap.autoUpdate = false;
  renderer.shadowMap.needsUpdate = true;
  let dirty = true;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#eeefea');
  const camera = new THREE.OrthographicCamera(-260, 260, 180, -180, 0.1, 3000);
  const controls = new OrbitControls(camera, canvas);
  controls.enableDamping = true;
  controls.dampingFactor = 0.09;
  controls.rotateSpeed = 0.65;
  controls.zoomSpeed = 0.8;
  controls.minZoom = 0.25;
  controls.maxZoom = 14;
  controls.minPolarAngle = 0.001;
  controls.maxPolarAngle = Math.PI - 0.001;
  controls.autoRotateSpeed = 0.8;
  const pmrem = new THREE.PMREMGenerator(renderer);
  const room = new RoomEnvironment();
  const environment = pmrem.fromScene(room, 0.04);
  scene.environment = environment.texture;
  scene.environmentIntensity = 0.6;
  room.dispose();
  pmrem.dispose();
  const ambient = new THREE.HemisphereLight('#ffffff', '#697166', 1.0);
  scene.add(ambient);
  const light = new THREE.DirectionalLight('#fff9ee', 2.4);
  light.position.set(-170, 320, 180);
  light.castShadow = true;
  light.shadow.mapSize.set(4096, 4096);
  Object.assign(light.shadow.camera, { left: -265, right: 265, top: 200, bottom: -200, near: 1, far: 1100 });
  light.shadow.normalBias = 0.28;
  light.shadow.bias = -0.00035;
  light.shadow.radius = 3;
  scene.add(light);
  const fill = new THREE.DirectionalLight('#e2ecf3', 1.2);
  fill.position.set(220, 150, -180);
  scene.add(fill);
  const lowFill = new THREE.DirectionalLight('#ffffff', 0.45);
  lowFill.position.set(20, -220, 140);
  scene.add(lowFill);
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(3000, 3000), new THREE.ShadowMaterial({ opacity: 0.13 }));
  floor.rotation.x = -Math.PI / 2;
  floor.position.y = -0.35;
  floor.receiveShadow = true;
  scene.add(floor);

  const materials = {
    shell: new THREE.MeshStandardMaterial({ color: '#343c40', roughness: 0.62, metalness: 0.02 }),
    base: new THREE.MeshStandardMaterial({ color: '#343c40', roughness: 0.62, metalness: 0.02 }),
    pcb: new THREE.MeshStandardMaterial({ color: '#234c37', roughness: 0.8 }),
    carrier: new THREE.MeshStandardMaterial({ color: '#363b35', roughness: 0.8 }),
    metal: new THREE.MeshStandardMaterial({ color: '#aeb3b3', roughness: 0.36, metalness: 0.8 }),
    switch: new THREE.MeshStandardMaterial({ color: '#456ba2', roughness: 0.65 }),
    cover: new THREE.MeshStandardMaterial({ color: '#e0e8ee', roughness: 0.26, transparent: true, opacity: 0.48, depthWrite: false }),
    stem: new THREE.MeshStandardMaterial({ color: '#82604d', roughness: 0.65 }),
    lightWindow: new THREE.MeshStandardMaterial({ color: '#e2e4d8', roughness: 0.48, emissive: '#fff6e4', emissiveIntensity: 0 }),
    frostedDeck: new THREE.MeshStandardMaterial({ color: '#c8cec7', roughness: 0.78, emissive: '#ffffff', emissiveIntensity: 0 }),
    halo: new THREE.MeshStandardMaterial({ color: '#d5d9cb', roughness: 0.55, emissive: '#fff6e4', emissiveIntensity: 0 }),
    chip: new THREE.MeshStandardMaterial({ color: '#202626', roughness: 0.8 }),
    alpha: new THREE.MeshStandardMaterial({ color: '#dddcd4', roughness: 0.5 }),
    modifier: new THREE.MeshStandardMaterial({ color: '#7b8583', roughness: 0.54 }),
    accent: new THREE.MeshStandardMaterial({ color: '#859e8b', roughness: 0.54 }),
    legendLight: new THREE.MeshBasicMaterial({ color: '#454c48', transparent: true, depthWrite: false }),
    legendDark: new THREE.MeshBasicMaterial({ color: '#f1f0e7', transparent: true, depthWrite: false }),
    diffuser: new THREE.MeshStandardMaterial({ color: '#c6cec4', roughness: 0.35, emissive: '#b6dfba', emissiveIntensity: 0 }),
    acrylicClear: new THREE.MeshPhysicalMaterial({color:'#f5f7f5',roughness:.09,transmission:.94,thickness:1.5,ior:1.49,metalness:0,emissive:'#fff8ed',emissiveIntensity:0,clearcoat:.2,clearcoatRoughness:.1}),
    acrylicFrosted: new THREE.MeshPhysicalMaterial({color:'#e9eeeb',roughness:.7,transmission:.28,thickness:1.5,ior:1.49,metalness:0,emissive:'#fff8ed',emissiveIntensity:0}),
    acrylicEtched: new THREE.MeshPhysicalMaterial({color:'#f3f6f3',roughness:.9,transmission:.86,thickness:1.5,ior:1.49,metalness:0,emissive:'#fff8ed',emissiveIntensity:0,clearcoat:.12,clearcoatRoughness:.2}),
    reflector: new THREE.MeshStandardMaterial({color:'#f2f3e9',roughness:.88,metalness:0}),
  };
  const cad = new THREE.Group();
  cad.name = 'V10 complete keyboard';
  // A proper rotation maps the existing CAD's Z-up frame to Three.js's Y-up.
  cad.rotation.x = -Math.PI / 2;
  cad.position.set(-width / 2, 0, depth / 2);
  scene.add(cad);
  const partMeshes = [];
  const variantGroups = {};
  const raisedGroups = {};
  const acrylicGroups = {};
  function decode(text, Type) {
    const binary = atob(text);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    return new Type(bytes.buffer);
  }
  for (const part of data.parts) {
    let geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(decode(part.positions, Float32Array), 3));
    geometry.setIndex(new THREE.BufferAttribute(decode(part.indices, Uint32Array), 1));
    const smooth = toCreasedNormals(geometry, Math.PI / 6);
    geometry.dispose();
    geometry = smooth;
    const mesh = new THREE.Mesh(geometry, materials[part.material]);
    mesh.name = part.name;
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    cad.add(mesh);
    partMeshes.push(mesh);
  }
  const board = new THREE.Group();
  board.name = 'Illustrative components at existing fit coordinates';
  board.rotation.x = data.tilt * radians;
  board.position.set(2.4, 2.4, data.originZ);
  cad.add(board);
  const keys = new THREE.Group();
  keys.name = '86 illustrative 5mm low-profile keycaps';
  board.add(keys);
  const legends = new THREE.Group();
  legends.name = 'Illustrative ANSI legends';
  board.add(legends);
  const capMeshes = [];
  const legendMeshes = [];
  const stemMeshes = [];
  const capCache = new Map();
  const profiles = {
    'xvx-bow': { name: 'XVX Skyline R2 BOW', height: 5, depth: 17, dish: .65, seat: 3, shine: true, legends: true, note: 'Approximate 5 mm uniform profile, gently scooped top and north-positioned legends. BOW uses white keys; black accent caps are optional in the supplied set.' },
    'xvx-wob': { name: 'XVX Skyline R2 WOB', height: 5, depth: 17, dish: .65, seat: 3, shine: true, legends: true, note: 'Same approximate Skyline shape in black with translucent legends. This six-source plate study does not assume evenly illuminated letters.' },
    flat: { name: 'ScottoCaps Flat MX', height: 6.7, depth: 18.05, dish: 0, seat: 3, source: 'flat', legends: false, note: 'Joe Scotto’s actual FDM blank meshes. 6.7 mm overall, including the stem. This is not automatically lower than a 5 mm XVX cap; socket engagement and Whale collar clearance govern the installed height.' },
    glass: { name: 'ScottoCaps Glass MX', height: 5.7, depth: 18.2, dish: 0, seat: 3, source: 'glass', legends: false, note: 'Joe Scotto’s actual resin-print MX blank meshes: 5.7 mm from the central socket opening to the top. Wide-key stabilizer bosses extend another 0.9 mm. Use the designer’s specified resin process and verify the Whale collar and stabilizers.' },
    slim: { name: 'Extra-flat MX concept', height: 3.5, depth: 17, dish: .12, seat: 2.3, legends: false, note: 'Experimental 3.5 mm overall cap with 2.3 mm socket engagement. A possible lower silhouette, not a finished printable keycap or verified Whale fit. Stem strength, dust-collar clearance and full travel need a coupon.' },
  };
  let currentProfile = 'xvx-bow';
  let currentDesign = 'etched';
  let currentEdition = 'raised';
  const sourceLenses = [];
  function assetGeometry(asset) {
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(decode(asset.positions, Float32Array), 3));
    g.setIndex(new THREE.BufferAttribute(decode(asset.indices, Uint32Array), 1));
    const smooth = toCreasedNormals(g, Math.PI / 6);
    g.dispose();
    return smooth;
  }
  for (const [name, parts] of Object.entries(data.study.variants)) {
    const group = new THREE.Group();
    group.name = name + ' — lighting case visual concept';
    group.visible = false;
    for (const part of parts) {
      const mesh = new THREE.Mesh(assetGeometry(part), materials[part.material]);
      mesh.name = part.name;
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      group.add(mesh);
    }
    cad.add(group);
    variantGroups[name] = group;
  }
  for (const [name, parts] of Object.entries(data.raisedEdition.variants)) {
    const group = new THREE.Group();
    group.name = `Edition 2 ${name} raised enclosure`;
    group.visible = false;
    for (const part of parts) {
      const mesh = new THREE.Mesh(assetGeometry(part), materials[part.material]);
      mesh.name = part.name; mesh.castShadow = true; mesh.receiveShadow = true;
      group.add(mesh);
    }
    cad.add(group);raisedGroups[name] = group;
  }
  function plateUV(geometry) {
    const p=geometry.attributes.position,uv=[];
    const c=Math.cos(data.tilt*radians),s=Math.sin(data.tilt*radians);
    for(let i=0;i<p.count;i++) {
      const x=p.getX(i)-2.4,y=(p.getY(i)-2.4)*c+(p.getZ(i)-data.originZ)*s;
      uv.push(x/data.board.width,y/data.board.depth);
    }
    geometry.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));return geometry;
  }
  for(const [edition,parts] of Object.entries(data.acrylicStudy.editions)) {
    const group=new THREE.Group();group.name=`${edition} acrylic plate appearance assembly`;group.visible=false;
    const result={group,collectors:[]};
    for(const [kind,part,material] of [['frame',parts.frame,materials.shell],['plate',parts.plate,materials.acrylicClear],['reflector',parts.reflector,materials.reflector],...parts.collectors.map(p=>['collector',p,materials.acrylicClear])]) {
      const geometry=assetGeometry(part);if(kind==='plate'||kind==='collector')plateUV(geometry);
      const mesh=new THREE.Mesh(geometry,material);mesh.name=part.name;
      mesh.castShadow=kind==='frame';mesh.receiveShadow=kind!=='collector';
      group.add(mesh);if(kind==='collector')result.collectors.push(mesh);else result[kind]=mesh;
    }
    cad.add(group);acrylicGroups[edition]=result;
  }
  // The Whale's flange and stem heights follow the manufacturer drawing.
  // Cover and base colours are illustrative, using the MINI product photographs.
  function housing(w,d,h) {
    const outline=roundedShape(w,d,.35);
    const hole=new THREE.Path();hole.moveTo(-1,-5.68);hole.lineTo(1,-5.68);hole.lineTo(1,-4.18);hole.lineTo(-1,-4.18);hole.closePath();outline.holes.push(hole);
    const g=new THREE.ExtrudeGeometry(outline,{depth:h,bevelEnabled:false,curveSegments:6});g.translate(0,0,-h/2);return g;
  }
  const lowerBody = housing(13.95,13.95,2.2);
  const flange = housing(15,15,.8);
  const coverBody = new RoundedBoxGeometry(14.6, 14.6, 2.5, 2, .75);
  const stemGeometry = new THREE.CylinderGeometry(2.85, 2.85, 3.1, 24);
  const pinGeometry = new THREE.CylinderGeometry(.45, .45, 1.7, 8);
  for (const key of data.switches) {
    const [x, y] = key.xy;
    for (const [g, z, material, label] of [[lowerBody, 2.7, materials.switch, 'lower housing'], [flange, 4.2, materials.switch, 'flange'], [coverBody, 5.85, materials.cover, 'clear PC cover']]) {
      const mesh = new THREE.Mesh(g, material); mesh.position.set(x, y, z); mesh.name = `${key.ref} Whale ${label} — appearance model`; mesh.castShadow = label !== 'clear PC cover'; mesh.receiveShadow = true; board.add(mesh);
    }
    const stem = new THREE.Mesh(stemGeometry, materials.stem);
    stem.rotation.x = Math.PI / 2; stem.position.set(x, y, 8.65); stem.name = `${key.ref} Whale round MX stem — appearance model`; board.add(stem);stemMeshes.push(stem);
    if (key.units >= 2) {
      const offset = key.units >= 6 ? 50 : 11.9;
      for (const sign of [-1, 1]) {
        const stabilizer = new THREE.Mesh(new RoundedBoxGeometry(4.6, 6.8, 3.4, 1, .3), materials.chip);
        stabilizer.position.set(x + sign * offset, y, 3.3); stabilizer.name = `${key.ref} stabilizer — illustrative`; stabilizer.castShadow = true; board.add(stabilizer);
      }
    }
  }
  function rebuildCaps(profileName, resetSeat = true) {
    currentProfile = profileName;
    const profile = profiles[profileName];
    keys.name = `86 ${profile.name} keycaps`;
    keys.userData = profile.source ? { author:'Joe Scotto', source:'https://github.com/joe-scotto/scottokeebs/tree/main/Extras/ScottoCaps', license:'CC BY-NC-SA 4.0', changes:'Reoriented and simplified with 0.025 mm surface tolerance' } : { status:'Approximate appearance geometry; physical fit unverified' };
    if (resetSeat) { $('#seat-depth').value = profile.seat; $('#legends').checked = profile.legends; }
    const seat = Number($('#seat-depth').value);
    const travel = Number($('#key-travel').value);
    $('#seat-value').textContent = seat.toFixed(1) + ' mm';
    $('#profile-note').textContent = profile.note;
    keys.clear();
    for (const label of legendMeshes) { label.material.map.dispose(); label.material.dispose(); label.geometry.dispose(); }
    legends.clear(); capMeshes.length = 0; legendMeshes.length = 0;
    for (const key of data.switches) {
      const [x, y] = key.xy;
      const w = key.units * 19.05 - 1.05;
      const cache = profileName + ':' + key.units;
      if (!capCache.has(cache)) capCache.set(cache, profile.source ? assetGeometry(data.study.caps[profile.source][String(key.units)] || data.study.caps[profile.source][key.units.toFixed(1)]) : makeCap(w, profile.depth, profile.height, profile.dish));
      const keyType = key.label === 'Esc' ? 'accent' : key.modifier ? 'modifier' : 'alpha';
      const cap = new THREE.Mesh(capCache.get(cache), materials[keyType]);
      cap.position.set(x, y, 10.2-seat-travel);
      cap.userData.restZ=10.2-seat;
      cap.name = `${key.ref} ${profile.name} ${key.label || 'Space'} keycap`;
      cap.castShadow = true; cap.receiveShadow = true; cap.userData.keyType = keyType;
      keys.add(cap); capMeshes.push(cap);
      const labelText = key.label || (profile.shine ? '—' : '');
      if (labelText) {
        const texture = makeLegend(labelText, w, profile.shine);
        const material = new THREE.MeshStandardMaterial({ map: texture, color: '#454c48', transparent: true, depthWrite: false, alphaTest: .015, roughness: .7, emissive: '#fff6de', emissiveMap: texture, emissiveIntensity: 0 });
        const geometry = legendSurface(cap.geometry,w-3.6,profile.depth-3.6,profile.height-profile.dish-.06);
        const label = new THREE.Mesh(geometry, material);
        label.name = `${key.label || 'Space'} illustrative legend`;
        label.position.copy(cap.position); label.userData.keyType = keyType;label.userData.restZ=10.2-seat;
        legends.add(label); legendMeshes.push(label);
      }
    }
    keys.visible=$('#caps-visible').checked;
    legends.visible = $('#legends').checked&&keys.visible;
    cad.userData.keycapProfile = profileName;
    recolorKeys(); updateLighting();
    renderer.shadowMap.needsUpdate = true; dirty = true;
  }
  const dark = materials.chip;
  function box(group, name, x, y, z, w, d, h, material = dark) {
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(w, d, h), material);
    mesh.position.set(x + w / 2, y + d / 2, z + h / 2);
    mesh.name = name;
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    group.add(mesh);
    return mesh;
  }
  for (const part of data.components) {
    if (part.ref === 'USB_PLUG_EXTERNAL' || part.ref === 'USB_SOCKET') continue;
    const [x, y, xx, yy] = part.bounds;
    if (part.ref.startsWith('LED')) {
      const lens = new THREE.Mesh(new THREE.CylinderGeometry(1.05, 1.05, 1.5, 20), materials.diffuser);
      lens.rotation.x = Math.PI / 2;
      lens.position.set((x + xx) / 2, (y + yy) / 2, 3.05);
      lens.name = `${part.ref} flush diffuser`;
      board.add(lens); sourceLenses.push(lens);
    } else {
      const material = part.ref === 'J1' ? new THREE.MeshStandardMaterial({ color: '#dddccf', roughness: 0.65 }) : dark;
      box(board, `${part.ref} appearance envelope`, x, y, (part.z_top || 0) - part.height, xx - x, yy - y, part.height, material);
    }
  }
  // Render the purchased battery's nominal body, contained within its reserve.
  box(cad, '5044147 nominal battery appearance', 87, 83.5, 1.7, 147, 44, 5,
    new THREE.MeshStandardMaterial({ color: '#b4b3a5', roughness: 0.45, metalness: 0.3 }));
  addUSB(board, box, materials);
  const switchPart = data.components.find(p => p.ref === 'SW87');
  box(board, 'Power switch actuator — illustrative', 299.3, switchPart.bounds[3] - 1, -1.65, 2.1, 1.6, 1.3);

  const ledParts = data.components.filter(p => p.ref.startsWith('LED'));
  // These are deliberately simple appearance fields, not optical material data.
  // Each source kernel has unit integrated weight before clipping to the board.
  // A wider distribution therefore lowers the peak rather than adding power.
  const fieldSettings={clear:[[5,.8],[18,.2]],frosted:[[9,.3],[25,.7]],etched:[[9,.15],[36,.85]]};
  const fieldRecords={};
  const textureWidth=1404,textureHeight=516;
  const ledXY=ledParts.map(p=>[(p.bounds[0]+p.bounds[2])/2,(p.bounds[1]+p.bounds[3])/2]);
  function bakeField(style) {
    const values=new Float32Array(textureWidth*textureHeight),pattern=new Float32Array(values.length);
    let plainSum=0,patternedSum=0;
    for(let j=0;j<textureHeight;j++)for(let i=0;i<textureWidth;i++) {
      const x=(i+.5)/textureWidth*data.board.width,y=(1-(j+.5)/textureHeight)*data.board.depth;
      let field=0,nearest=Infinity;
      for(const [sx,sy] of ledXY){const r2=(x-sx)**2+(y-sy)**2;nearest=Math.min(nearest,r2);for(const [radius,weight] of fieldSettings[style])field+=weight/(radius*radius)*Math.exp(-r2/(radius*radius));}
      const cell=.95,dx=x/cell-Math.floor(x/cell)-.5,dy=y/cell-Math.floor(y/cell)-.5;
      const dotRadius=.13+.10*Math.min(1,Math.sqrt(nearest)/50);
      const dots=Math.hypot(dx,dy)<dotRadius?1:0;
      const extraction=style==='etched'?.46+1.4*dots:1;
      const index=j*textureWidth+i;values[index]=field;pattern[index]=extraction;plainSum+=field;patternedSum+=field*extraction;
    }
    const normalization=plainSum/patternedSum;let peak=0;
    for(let i=0;i<values.length;i++){values[i]*=pattern[i]*normalization;peak=Math.max(peak,values[i]);}
    const c=document.createElement('canvas');c.width=textureWidth;c.height=textureHeight;
    const ctx=c.getContext('2d'),pixels=ctx.createImageData(textureWidth,textureHeight);
    const rough=document.createElement('canvas');rough.width=textureWidth;rough.height=textureHeight;
    const rc=rough.getContext('2d'),rp=rc.createImageData(textureWidth,textureHeight);
    for(let i=0;i<values.length;i++) {
      const linear=values[i]/peak;
      const v=Math.round(255*(linear<=.0031308?linear*12.92:1.055*linear**(1/2.4)-.055));
      pixels.data.set([v,v,v,255],i*4);
      const r=pattern[i]>1?225:26;rp.data.set([r,r,r,255],i*4);
    }
    ctx.putImageData(pixels,0,0);rc.putImageData(rp,0,0);
    const texture=new THREE.CanvasTexture(c);texture.colorSpace=THREE.SRGBColorSpace;texture.anisotropy=4;
    const roughnessMap=new THREE.CanvasTexture(rough);roughnessMap.anisotropy=4;
    fieldRecords[style]={peak,integratedKernelWeight:6*Math.PI,clippedFieldSum:plainSum,extractionNormalization:normalization};
    return {texture,roughnessMap,peak};
  }
  for(const [style,material] of [['clear',materials.acrylicClear],['frosted',materials.acrylicFrosted],['etched',materials.acrylicEtched]]) {
    const field=bakeField(style);material.emissiveMap=field.texture;material.userData.fieldPeak=field.peak;
    if(style==='etched')material.roughnessMap=field.roughnessMap;
    material.needsUpdate=true;
  }
  const glowTexture = (() => {
    const c = document.createElement('canvas'); c.width = c.height = 128;
    const context = c.getContext('2d');
    const g = context.createRadialGradient(64,64,0,64,64,64);
    g.addColorStop(0,'rgba(255,250,225,.65)'); g.addColorStop(.2,'rgba(255,250,225,.23)'); g.addColorStop(1,'rgba(255,250,225,0)');
    context.fillStyle=g;context.fillRect(0,0,128,128);
    return new THREE.CanvasTexture(c);
  })();
  const glowMaterial = new THREE.MeshBasicMaterial({ map: glowTexture, transparent:true, depthWrite:false, blending:THREE.AdditiveBlending, opacity:.4 });
  const spots = [];
  const pointLights = [];
  for (const led of ledParts) {
    const [x,y,xx,yy] = led.bounds;
    const spot = new THREE.Mesh(new THREE.PlaneGeometry(17,17), glowMaterial);
    spot.position.set((x+xx)/2,(y+yy)/2,3.825); spot.name=led.ref+' illustrative light spill';board.add(spot);spots.push(spot);
    const point = new THREE.PointLight('#fff3d8', 0, 28, 2);
    point.position.copy(spot.position);point.position.z=4.05;board.add(point);pointLights.push(point);
  }
  const concepts = {
    original:{badge:'Opaque plate · current six LED windows',note:'Baseline V10 lighting. The switch plate is opaque and the six small windows sit below the keycap skirts.'},
    clear:{badge:'Clear acrylic + six existing LED inputs',note:'Glossy acrylic shows concentrated light pools and brighter cut edges. The six upward sources remain in place; a clear sheet alone does not make an evenly lit panel.'},
    frosted:{badge:'Lightly frosted acrylic · broader, softer pools',note:'Light scatters across a larger area, with lower peaks and visible dark zones. The white backing hides the PCB and returns some escaped light. Output strength is a visual hypothesis.'},
    etched:{badge:'Selective engraving + six collector inputs',note:'Fine extraction dots are denser away from the sources. This illustrates the intended broader glow if the collectors feed light into the sheet; it is not a prediction of uniformity or brightness.'},
  };
  function updateLighting() {
    const power=$('#leds').checked?Number($('#light-level').value):0;
    const acrylic=currentDesign!=='original',backing=$('#reflector').checked;
    materials.diffuser.emissiveIntensity=power*1.8;
    glowMaterial.opacity=power*.28;
    sourceLenses.forEach(lens=>lens.visible=!acrylic);
    for(const material of [materials.acrylicClear,materials.acrylicFrosted,materials.acrylicEtched]) {
      // Common display gain for all three fields. This is not calibrated to
      // measured LED output; keep the same gain and six inputs across styles.
      material.emissiveIntensity=power*240*material.userData.fieldPeak*(backing?1:.7);
    }
    for(const result of Object.values(acrylicGroups))result.reflector.visible=backing;
    spots.forEach((spot,i)=>{
      const p=ledParts[i].bounds,x=(p[0]+p[2])/2,y=(p[1]+p[3])/2;
      spot.position.set(x,y,3.825);spot.visible=!acrylic&&power>0;
      pointLights[i].position.set(x,y,4.05);pointLights[i].intensity=power*18;
    });
    for(const legend of legendMeshes)legend.material.emissiveIntensity=0;
    dirty=true;
  }
  function changeDesign(name) {
    currentDesign=name;const acrylic=name!=='original';
    cad.userData.lightingConcept=name;cad.userData.status='Appearance proxy using six original LEDs; physical fit and optics unverified';
    $('#case-design').value=name;
    partMeshes.find(p=>p.name==='upper').visible=currentEdition==='current'&&!acrylic;
    for(const group of Object.values(variantGroups))group.visible=false;
    for(const [id,group] of Object.entries(raisedGroups))group.visible=currentEdition==='raised'&&!acrylic&&id==='original';
    const material={clear:materials.acrylicClear,frosted:materials.acrylicFrosted,etched:materials.acrylicEtched}[name];
    for(const [edition,result] of Object.entries(acrylicGroups)) {
      result.group.visible=acrylic&&currentEdition===edition;
      if(acrylic)result.plate.material=material;
    }
    $('#reflector').disabled=!acrylic;
    $('#concept-badge').textContent=concepts[name].badge;
    $('#concept-note').textContent=concepts[name].note;
    renderer.shadowMap.needsUpdate=true;updateLighting();
  }
  function changeEdition(name) {
    currentEdition=name;$('#case-edition').value=name;cad.userData.caseEdition=name;
    $('#edition-label').textContent=name==='raised'?'Edition 2 · raised key wells':'Edition 1 · floating keys';
    $('#edition-note').textContent=name==='raised'?'Opaque rounded frame conceals the switch housings from outside. The acrylic plate stays at the lower switch seating plane. Its support and retention are still a mechanical concept.':'Original floating-key silhouette. The acrylic plate stays at the existing switch seating plane, inside an opaque printed surround.';
    $('#top-height').textContent=name==='raised'?'9.0 / 22.3 mm':'5.7 / 19.0 mm';
    changeDesign(currentDesign);
  }
  function changeTravel() {
    const travel=Number($('#key-travel').value);
    $('#travel-value').textContent=travel.toFixed(1)+' mm';
    for(const cap of capMeshes)cap.position.z=cap.userData.restZ-travel;
    for(const label of legendMeshes)label.position.z=label.userData.restZ-travel;
    for(const stem of stemMeshes)stem.position.z=8.65-travel;
    renderer.shadowMap.needsUpdate=true;dirty=true;
  }
  function updateRoom() {
    const dim=$('#room').value==='dim';const raking=$('#raking').checked;
    scene.background.set(dim?'#161e23':'#eeefea');
    stage.classList.toggle('dim',dim);
    ambient.intensity=dim?.09:1;
    scene.environmentIntensity=dim?.09:.6;
    light.intensity=dim?.35:2.4;
    light.position.set(...(raking?[-260,75,160]:[-170,320,180]));
    if(raking)light.intensity*=1.35;
    fill.intensity=dim?.12:1.2;
    lowFill.intensity=dim?.07:.45;
    renderer.toneMappingExposure=dim?1.02:1.12;
    renderer.shadowMap.needsUpdate=true;dirty=true;
  }
  $('#cap-profile').addEventListener('change',e=>rebuildCaps(e.target.value));
  $('#case-edition').addEventListener('change',e=>changeEdition(e.target.value));
  $('#key-travel').addEventListener('input',changeTravel);
  $('#seat-depth').addEventListener('input',()=>rebuildCaps(currentProfile,false));
  $('#case-design').addEventListener('change',e=>changeDesign(e.target.value));
  $('#light-level').addEventListener('input',updateLighting);
  $('#room').addEventListener('change',updateRoom);
  $('#reflector').addEventListener('change',updateLighting);
  $('#caps-visible').addEventListener('change',()=>{keys.visible=$('#caps-visible').checked;legends.visible=keys.visible&&$('#legends').checked;renderer.shadowMap.needsUpdate=true;dirty=true;});

  let currentView = 'hero';
  const views = {
    hero: { name: 'Front three-quarter', direction: [0.55, 1.5, 1.3], target: [0, 14, 0], scale: 1.25 },
    front: { name: 'Front · low rounded leading edge', direction: [0, 0.045, 1], target: [0, 17, 0], scale: 1.35 },
    rear: { name: 'Rear three-quarter · USB-C & power', direction: [-0.65, 0.6, -1.55], target: [0, 14, 0], scale: 1.35 },
    side: { name: 'Right profile · current 5.7° slope', direction: [1, 0, 0], target: [0, 17, 0], scale: 1.8 },
    top: { name: 'Top · continuous rounded perimeter', direction: [0, 1, 0.0001], target: [0, 14, 0], scale: 1.22 },
    bottom: { name: 'Underneath · eight recessed fasteners', direction: [0, -1, 0.0001], target: [0, 0, 0], scale: 1.3 },
    edge: { name: 'Front-right · 2.5 mm roll-over', direction: [1.0, 0.65, 1.3], target: [width / 2 - 16, 8, depth / 2 - 16], span: 103 },
    usb: { name: 'Rear-left · socket and insert joint', direction: [-0.4, 0.3, -1.6], target: [-width / 2 + 33, 14, -depth / 2 + 4], span: 100 },
    light: { name: 'Light detail · plate between the keycaps', direction: [.12, 1.6, .45], target: [-18, 14, -7], span: 116 },
  };
  const bbox = new THREE.Box3(new THREE.Vector3(-width / 2, 0, -depth / 2), new THREE.Vector3(width / 2, 38, depth / 2));
  let fittedHeight = 190;
  function fitTo(v) {
    const dir = new THREE.Vector3(...v.direction).normalize();
    const target = new THREE.Vector3(...v.target);
    camera.position.copy(target).addScaledVector(dir, 850);
    camera.up.set(0, 1, 0);
    controls.target.copy(target);
    camera.lookAt(target);
    camera.updateMatrixWorld(true);
    const right = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 0);
    const up = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 1);
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    for (const x of [bbox.min.x, bbox.max.x]) for (const y of [bbox.min.y, bbox.max.y]) for (const z of [bbox.min.z, bbox.max.z]) {
      const q = new THREE.Vector3(x, y, z).sub(target);
      const xx = q.dot(right), yy = q.dot(up);
      minX = Math.min(minX, xx); maxX = Math.max(maxX, xx);
      minY = Math.min(minY, yy); maxY = Math.max(maxY, yy);
    }
    const aspect = stage.clientWidth / stage.clientHeight;
    fittedHeight = v.span ? Math.max(v.span * 0.65, v.span / aspect) : Math.max((maxX - minX) / aspect, maxY - minY) * v.scale;
    // Leave room for the view controls under the keyboard, especially on phones.
    const displayCenter = v.span ? 0 : -fittedHeight * 0.035;
    camera.left = -fittedHeight * aspect / 2;
    camera.right = fittedHeight * aspect / 2;
    camera.top = fittedHeight / 2 + displayCenter;
    camera.bottom = -fittedHeight / 2 + displayCenter;
    camera.zoom = 1;
    camera.updateProjectionMatrix();
    controls.update();
  }
  function stopSpin() { controls.autoRotate = false; $('#spin').checked = false; }
  function setView(name) {
    currentView = name;
    stopSpin();
    controls.enableDamping = false;
    fitTo(views[name]);
    controls.enableDamping = true;
    $('#view-name').textContent = views[name].name;
    document.querySelectorAll('[data-view]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.view === name)));
    render();
  }
  function render() {
    floor.visible = $('#ground').checked && camera.position.y > 2;
    renderer.render(scene, camera);
    dirty = false;
  }
  function resize() {
    renderer.setSize(stage.clientWidth, stage.clientHeight, false);
    const aspect = stage.clientWidth / stage.clientHeight;
    camera.left = -fittedHeight * aspect / 2;
    camera.right = fittedHeight * aspect / 2;
    camera.updateProjectionMatrix();
    render();
  }
  new ResizeObserver(() => { resize(); fitTo(views[currentView]); }).observe(stage);
  document.querySelectorAll('[data-view]').forEach(button => button.addEventListener('click', () => setView(button.dataset.view)));
  controls.addEventListener('start', () => {
    stopSpin();
    $('#view-name').textContent = 'Free orbit · assembled v10';
    document.querySelectorAll('[data-view]').forEach(b => b.setAttribute('aria-pressed', 'false'));
  });
  controls.addEventListener('change', () => { dirty = true; });
  for (const name of ['click', 'input', 'change']) document.addEventListener(name, () => { dirty = true; });
  $('#reset').addEventListener('click', () => setView('hero'));
  window.addEventListener('keydown', event => {
    if (/input|select|textarea/i.test(event.target.tagName)) return;
    if (event.key.toLowerCase() === 'r') setView('hero');
    if (event.key === 'Escape' && document.fullscreenElement) document.exitFullscreen();
  });
  $('#spin').addEventListener('change', e => { controls.autoRotate = e.target.checked; });
  $('#legends').addEventListener('change', e => { legends.visible = e.target.checked&&keys.visible; });
  $('#leds').addEventListener('change', updateLighting);
  $('#raking').addEventListener('change', updateRoom);
  $('#roughness').addEventListener('input', e => {
    materials.shell.roughness = materials.base.roughness = Number(e.target.value);
    $('#finish-name').textContent = Number(e.target.value) < 0.46 ? 'Satin' : 'Matte';
  });
  const themes = {
    graphite: { shell: '#343c40', alpha: '#dddcd4', modifier: '#7b8583', accent: '#859e8b' },
    chalk: { shell: '#dcdad2', alpha: '#e9e6dc', modifier: '#b6b9ae', accent: '#839582' },
    slate: { shell: '#75858b', alpha: '#e2e4de', modifier: '#a4b4b9', accent: '#778f9e' },
  };
  let theme = themes.graphite;
  function recolorKeys() {
    const style = $('#key-style').value;
    const profile = profiles[currentProfile];
    for (const type of ['alpha', 'modifier', 'accent']) {
      const color = style === 'source' ? (currentProfile === 'xvx-wob' ? '#20262a' : '#e6e5df') : style === 'dark' ? '#30383c' : style === 'light' ? theme.alpha : theme[type];
      materials[type].color.set(color);
    }
    for (const legend of legendMeshes) {
      const c = materials[legend.userData.keyType].color;
      const luminance = 0.2126 * c.r + 0.7152 * c.g + 0.0722 * c.b;
      legend.material.color.set(luminance > 0.13 ? '#454c48' : '#f1f0e7');
    }
  }
  function setShell(color) {
    materials.shell.color.set(color);
    materials.base.color.set(color);
    $('#case-color').value = color;
  }
  document.querySelectorAll('[data-finish]').forEach(button => button.addEventListener('click', () => {
    theme = themes[button.dataset.finish];
    setShell(theme.shell);
    recolorKeys();
    document.querySelectorAll('[data-finish]').forEach(b => b.setAttribute('aria-pressed', String(b === button)));
  }));
  $('#case-color').addEventListener('input', e => {
    setShell(e.target.value);
    document.querySelectorAll('[data-finish]').forEach(b => b.setAttribute('aria-pressed', 'false'));
  });
  $('#key-style').addEventListener('change', recolorKeys);
  let toastTimer;
  function toast(message) {
    clearTimeout(toastTimer);
    $('#toast').textContent = message;
    $('#toast').classList.add('visible');
    toastTimer = setTimeout(() => $('#toast').classList.remove('visible'), 2300);
  }
  function saveImage() {
    stopSpin();
    const size = new THREE.Vector2();
    renderer.getSize(size);
    const ratio = renderer.getPixelRatio();
    renderer.setPixelRatio(1);
    renderer.setSize(Math.round(size.x * 2), Math.round(size.y * 2), false);
    render();
    const url = canvas.toDataURL('image/png');
    renderer.setPixelRatio(ratio);
    renderer.setSize(size.x, size.y, false);
    render();
    const a = document.createElement('a');
    a.download = `v10-${currentEdition}-${currentProfile}-${currentDesign}-${currentView}.png`;
    a.href = url;
    a.click();
    toast('Image saved at twice the viewer resolution');
  }
  $('#save').addEventListener('click', saveImage);
  $('#download-model').addEventListener('click', async () => {
    const button=$('#download-model');button.disabled=true;
    try {
      const bytes=await new GLTFExporter().parseAsync(cad,{binary:true,onlyVisible:true});
      const url=URL.createObjectURL(new Blob([bytes],{type:'model/gltf-binary'}));
      const a=document.createElement('a');a.href=url;a.download=`v10-${currentEdition}-${currentProfile}-${currentDesign}.glb`;a.click();
      setTimeout(()=>URL.revokeObjectURL(url),2000);toast('Selected model exported');
    } catch(error) { console.error(error);toast('Export failed. See the browser console for details.'); }
    finally {button.disabled=false;}
  });
  rebuildCaps('xvx-bow');
  changeDesign('etched');
  changeEdition('raised');
  updateRoom();
  resize();
  setView('hero');
  const clock = new THREE.Clock();
  let active = true;
  document.addEventListener('visibilitychange', () => { active = !document.hidden; clock.getDelta(); });
  renderer.setAnimationLoop(() => {
    const dt = Math.min(clock.getDelta(), 0.05);
    if (!active) return;
    const moved = controls.update(dt);
    if (dirty || moved) render();
  });
  $('#loading').hidden = true;
  // Read-only inspection / export hooks used to validate and capture this artifact.
  window.v10 = {
    ready: true, scene, cad, camera, controls, renderer, materials, setView, render,
    keyCount: capMeshes.length, partMeshes, rebuildCaps, profiles, variantGroups, raisedGroups, acrylicGroups, fieldRecords, pointLights, updateLighting, changeEdition,
    selection: () => ({ edition:currentEdition,profile: currentProfile, design: currentDesign, seat: Number($('#seat-depth').value), travel:Number($('#key-travel').value),backing:$('#reflector').checked,capsVisible:keys.visible }),
    exportGLB: async () => {
      const binary = await new GLTFExporter().parseAsync(cad, { binary: true, onlyVisible: true });
      return new Uint8Array(binary);
    },
    summary: () => ({ keys: capMeshes.length, caseTriangles: data.parts.filter(p => ['upper', 'bottom', 'bezel'].includes(p.name)).map(p => ({ name: p.name, triangles: p.triangles })), drawCalls: renderer.info.render.calls, triangles: renderer.info.render.triangles, camera: camera.position.toArray(), target: controls.target.toArray(), zoom: camera.zoom }),
  };
}

function roundedRing(w, d, r, z) {
  const hw = w / 2, hd = d / 2;
  const result = [];
  for (let corner = 0; corner < 4; corner++) {
    const cx = [hw - r, -hw + r, -hw + r, hw - r][corner];
    const cy = [hd - r, hd - r, -hd + r, -hd + r][corner];
    for (let segment = 0; segment <= 8; segment++) {
      const angle = corner * Math.PI / 2 + segment / 8 * Math.PI / 2;
      result.push(cx + r * Math.cos(angle), cy + r * Math.sin(angle), z);
    }
  }
  return result;
}

function makeCap(w, d, height = 5, dish = .65) {
  const rings = [[w - 0.7, d - 0.7, 0.75, 0], [w, d, 1, 0.45], [w, d, 1, 1], [w - 1, d - 0.8, 1.05, 4.1], [w - 1.6, d - 1.5, 1.1, 4.7], [w - 2, d - 1.9, 1.1, 5]];
  for (const r of rings) r[3] *= height / 5;
  const positions = rings.flatMap(r => roundedRing(...r));
  const outerCount = positions.length / rings.length / 3;
  for (const scale of [.78, .53, .26]) {
    const ring = roundedRing((w-2)*scale, (d-1.9)*scale, Math.min(1.1*scale, .5*(d-1.9)*scale), height);
    for (let i=0; i<ring.length; i+=3) ring[i+2] = capSurface(ring[i], ring[i+1], w-2, d-1.9, height, dish);
    positions.push(...ring);
  }
  for (let i=(rings.length-1)*outerCount*3; i<rings.length*outerCount*3; i+=3) positions[i+2] = capSurface(positions[i], positions[i+1], w-2, d-1.9, height, dish);
  const totalRings = rings.length + 3;
  const n = outerCount;
  const indices = [];
  for (let ring = 0; ring < totalRings - 1; ring++) for (let j = 0; j < n; j++) {
    const a = ring * n + j, b = ring * n + (j + 1) % n, c = b + n, e = a + n;
    indices.push(a, b, c, a, c, e);
  }
  const bottom = positions.length / 3;
  positions.push(0, 0, 0, 0, 0, height-dish);
  const topStart = (totalRings - 1) * n;
  for (let j = 0; j < n; j++) {
    indices.push(bottom, (j + 1) % n, j);
    indices.push(bottom + 1, topStart + j, topStart + (j + 1) % n);
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geometry.setIndex(indices);
  const smooth = toCreasedNormals(geometry, Math.PI / 4);
  geometry.dispose();
  return smooth;
}

function makeLegend(label, width, north = false) {
  const canvas = document.createElement('canvas');
  canvas.width = Math.ceil((width - 3.6) / 13.4 * 160);
  canvas.height = 160;
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#ffffff';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  const size = label.length > 3 ? 23 : label.length > 1 ? 29 : 37;
  ctx.font = `500 ${size}px Arial, sans-serif`;
  ctx.fillText(label, canvas.width / 2, north ? canvas.height*.25 : canvas.height/2+2);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.anisotropy = 4;
  return texture;
}

function roundedShape(w, h, r, Type = THREE.Shape) {
  const s = new Type();
  const hw = w / 2, hh = h / 2;
  s.moveTo(-hw + r, -hh);
  s.lineTo(hw - r, -hh);
  s.absarc(hw - r, -hh + r, r, -Math.PI / 2, 0);
  s.lineTo(hw, hh - r);
  s.absarc(hw - r, hh - r, r, 0, Math.PI / 2);
  s.lineTo(-hw + r, hh);
  s.absarc(-hw + r, hh - r, r, Math.PI / 2, Math.PI);
  s.lineTo(-hw, -hh + r);
  s.absarc(-hw + r, -hh + r, r, Math.PI, Math.PI * 1.5);
  s.closePath();
  return s;
}

function addUSB(group, box, materials) {
  const part = data.components.find(p => p.ref === 'USB_SOCKET');
  const [x, y, xx, yy] = part.bounds;
  const w = xx - x, h = part.height;
  const cx = (x + xx) / 2, cz = part.z_top - h / 2;
  const shell = roundedShape(w, h, 1.35);
  shell.holes.push(roundedShape(w - 0.5, h - 0.5, 1.1, THREE.Path));
  const geometry = new THREE.ExtrudeGeometry(shell, { depth: yy - y, bevelEnabled: false, curveSegments: 12 });
  const socket = new THREE.Mesh(geometry, materials.metal);
  socket.rotation.x = Math.PI / 2;
  socket.position.set(cx, yy, cz);
  socket.name = 'USB-C socket shell — illustrative';
  socket.castShadow = true;
  group.add(socket);
  box(group, 'USB-C dark cavity — illustrative', x + 0.26, y - 0.2, part.z_top - h + 0.26, w - 0.52, 0.15, h - 0.52);
  box(group, 'USB-C contact tongue — illustrative', cx - 3.2, y + 0.1, cz - 0.25, 6.4, yy - y - 0.2, 0.5);
}

function capSurface(x, y, width, depth, height, dish) {
  return height - dish * Math.max(0, 1-(2*x/width)**2) * Math.max(0, 1-(2*y/depth)**2);
}

function legendSurface(cap,width,depth,minZ) {
  const source=cap.attributes.position;const positions=[],uv=[];
  const a=new THREE.Vector3(),b=new THREE.Vector3(),c=new THREE.Vector3();
  for(let i=0;i<source.count;i+=3) {
    a.fromBufferAttribute(source,i);b.fromBufferAttribute(source,i+1);c.fromBufferAttribute(source,i+2);
    if(Math.min(a.z,b.z,c.z)<minZ)continue;
    const normal=b.clone().sub(a).cross(c.clone().sub(a)).normalize();if(normal.z<.5)continue;
    for(const p of [a,b,c]){positions.push(p.x,p.y,p.z+.025);uv.push(p.x/width+.5,p.y/depth+.5);}
  }
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.computeVertexNormals();return g;
}
