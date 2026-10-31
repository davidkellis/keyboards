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
  scene.add(new THREE.HemisphereLight('#ffffff', '#697166', 1.0));
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
    switch: new THREE.MeshStandardMaterial({ color: '#272c2d', roughness: 0.75 }),
    chip: new THREE.MeshStandardMaterial({ color: '#202626', roughness: 0.8 }),
    alpha: new THREE.MeshStandardMaterial({ color: '#dddcd4', roughness: 0.5 }),
    modifier: new THREE.MeshStandardMaterial({ color: '#7b8583', roughness: 0.54 }),
    accent: new THREE.MeshStandardMaterial({ color: '#859e8b', roughness: 0.54 }),
    legendLight: new THREE.MeshBasicMaterial({ color: '#454c48', transparent: true, depthWrite: false }),
    legendDark: new THREE.MeshBasicMaterial({ color: '#f1f0e7', transparent: true, depthWrite: false }),
    diffuser: new THREE.MeshStandardMaterial({ color: '#c6cec4', roughness: 0.35, emissive: '#b6dfba', emissiveIntensity: 0 }),
  };
  const cad = new THREE.Group();
  cad.name = 'V10 complete keyboard';
  // A proper rotation maps the existing CAD's Z-up frame to Three.js's Y-up.
  cad.rotation.x = -Math.PI / 2;
  cad.position.set(-width / 2, 0, depth / 2);
  scene.add(cad);
  const partMeshes = [];
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
  const keyGeometry = new Map();
  const bodyGeometry = new RoundedBoxGeometry(13.95, 13.95, 5.5, 2, 0.3);
  for (const key of data.switches) {
    const [x, y] = key.xy;
    const w = key.units * 19.05 - 1.05;
    if (!keyGeometry.has(w)) keyGeometry.set(w, makeCap(w, 17));
    const keyType = key.label === 'Esc' ? 'accent' : key.modifier ? 'modifier' : 'alpha';
    const cap = new THREE.Mesh(keyGeometry.get(w), materials[keyType]);
    cap.name = `${key.ref} ${key.label || 'Space'} — illustrative keycap`;
    cap.position.set(x, y, 1.6 + 8.6 - data.config.keycaps.assumed_socket_insertion_mm);
    cap.castShadow = true;
    cap.receiveShadow = true;
    cap.userData.keyType = keyType;
    keys.add(cap);
    capMeshes.push(cap);
    const body = new THREE.Mesh(bodyGeometry, materials.switch);
    body.name = `${key.ref} switch body — illustrative`;
    body.position.set(x, y, 1.6 + 5.5 / 2);
    body.castShadow = true;
    body.receiveShadow = true;
    board.add(body);
    if (key.units >= 2) {
      const offset = key.units >= 6 ? 50 : 11.9;
      for (const sign of [-1, 1]) {
        const stabilizer = new THREE.Mesh(new RoundedBoxGeometry(4.6, 6.8, 3.4, 1, 0.3), materials.switch);
        stabilizer.position.set(x + sign * offset, y, 1.6 + 1.7);
        stabilizer.name = `${key.ref} stabilizer housing — illustrative`;
        stabilizer.castShadow = true;
        board.add(stabilizer);
      }
      const wire = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, offset * 2, 8), materials.metal);
      wire.rotation.z = Math.PI / 2;
      wire.position.set(x, y - 2.4, 3.1);
      wire.name = `${key.ref} stabilizer wire — illustrative`;
      board.add(wire);
    }
    if (key.label) {
      const glyph = makeLegend(key.label, w);
      const material = new THREE.MeshBasicMaterial({ map: glyph, color: keyType === 'alpha' ? '#454c48' : '#f1f0e7', transparent: true, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -1 });
      const label = new THREE.Mesh(new THREE.PlaneGeometry(w - 3.6, 13.4), material);
      label.name = `${key.label} legend`;
      label.position.set(x, y, cap.position.z + 5.015);
      label.userData.keyType = keyType;
      legends.add(label);
      legendMeshes.push(label);
    }
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
      board.add(lens);
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

  let currentView = 'hero';
  const views = {
    hero: { name: 'Front three-quarter', direction: [0.62, 0.92, 1.55], target: [0, 14, 0], scale: 1.35 },
    front: { name: 'Front · low rounded leading edge', direction: [0, 0.045, 1], target: [0, 17, 0], scale: 1.35 },
    rear: { name: 'Rear three-quarter · USB-C & power', direction: [-0.65, 0.6, -1.55], target: [0, 14, 0], scale: 1.35 },
    side: { name: 'Right profile · current 5.7° slope', direction: [1, 0, 0], target: [0, 17, 0], scale: 1.8 },
    top: { name: 'Top · continuous rounded perimeter', direction: [0, 1, 0.0001], target: [0, 14, 0], scale: 1.22 },
    bottom: { name: 'Underneath · eight recessed fasteners', direction: [0, -1, 0.0001], target: [0, 0, 0], scale: 1.3 },
    edge: { name: 'Front-right · 2.5 mm roll-over', direction: [1.0, 0.65, 1.3], target: [width / 2 - 16, 8, depth / 2 - 16], span: 103 },
    usb: { name: 'Rear-left · socket and insert joint', direction: [-0.4, 0.3, -1.6], target: [-width / 2 + 33, 14, -depth / 2 + 4], span: 100 },
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
  $('#legends').addEventListener('change', e => { legends.visible = e.target.checked; });
  $('#leds').addEventListener('change', e => {
    materials.diffuser.emissiveIntensity = e.target.checked ? 0.9 : 0;
    materials.diffuser.color.set(e.target.checked ? '#e0f2da' : '#c6cec4');
  });
  $('#raking').addEventListener('change', e => {
    const raking = e.target.checked;
    light.position.set(...(raking ? [-260, 75, 160] : [-170, 320, 180]));
    light.intensity = raking ? 3.5 : 2.4;
    fill.intensity = raking ? 0.4 : 1.2;
    scene.environmentIntensity = raking ? 0.25 : 0.6;
    renderer.shadowMap.needsUpdate = true;
  });
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
    for (const type of ['alpha', 'modifier', 'accent']) {
      const color = style === 'dark' ? '#3b4445' : style === 'light' ? theme.alpha : theme[type];
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
    a.download = `v10-${currentView}.png`;
    a.href = url;
    a.click();
    toast('Image saved at twice the viewer resolution');
  }
  $('#save').addEventListener('click', saveImage);
  recolorKeys();
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
    keyCount: capMeshes.length, partMeshes,
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

function makeCap(w, d) {
  const rings = [[w - 0.7, d - 0.7, 0.75, 0], [w, d, 1, 0.45], [w, d, 1, 1], [w - 1, d - 0.8, 1.05, 4.1], [w - 1.6, d - 1.5, 1.1, 4.7], [w - 2, d - 1.9, 1.1, 5]];
  const positions = rings.flatMap(r => roundedRing(...r));
  const n = positions.length / rings.length / 3;
  const indices = [];
  for (let ring = 0; ring < rings.length - 1; ring++) for (let j = 0; j < n; j++) {
    const a = ring * n + j, b = ring * n + (j + 1) % n, c = b + n, e = a + n;
    indices.push(a, b, c, a, c, e);
  }
  const bottom = positions.length / 3;
  positions.push(0, 0, 0, 0, 0, 5);
  const topStart = (rings.length - 1) * n;
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

function makeLegend(label, width) {
  const canvas = document.createElement('canvas');
  canvas.width = Math.ceil((width - 3.6) / 13.4 * 160);
  canvas.height = 160;
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#ffffff';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  const size = label.length > 3 ? 23 : label.length > 1 ? 29 : 37;
  ctx.font = `500 ${size}px Arial, sans-serif`;
  ctx.fillText(label, canvas.width / 2, canvas.height / 2 + 2);
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
