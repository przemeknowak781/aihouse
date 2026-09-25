// Renderer wizualizacji modelu Dom LAMELA (three.js, headless Chromium przez Playwright — tools/render3d/render.py).
// API (window.LAMELA):
//   await LAMELA.load(url)     → {groups, bbox_budynek, bbox_all, meta}
//   await LAMELA.render(cfg)   → dataURL PNG (rozdzielczość cfg.width*cfg.ss × cfg.height*cfg.ss)
// Współrzędne w cfg — układ budynku (x→E, y→N, z↑); three.js: X=x, Y=z, Z=−y.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { N8AOPass } from 'n8ao';

const B2T = (p) => new THREE.Vector3(p[0], p[2], -p[1]);
const T2B = (v) => [v.x, -v.z, v.y];

let renderer, scene, root, sun, hemi, skyMesh, skyMat, groundDisc, shadowPlane, pmrem, envRT;
const groups = {};
const basePos = {};
let meta = {};
let terrainMinY = -0.5;
let groundBand = null;

function initRenderer() {
  renderer = new THREE.WebGLRenderer({ antialias: false, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
  renderer.setPixelRatio(1);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.0;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  document.body.appendChild(renderer.domElement);
  pmrem = new THREE.PMREMGenerator(renderer);
  scene = new THREE.Scene();

  sun = new THREE.DirectionalLight(0xfff3e2, 3.2);
  sun.castShadow = true;
  sun.shadow.mapSize.set(4096, 4096);
  sun.shadow.bias = -0.00025;
  sun.shadow.normalBias = 0.025;
  sun.shadow.radius = 2.5;
  scene.add(sun);
  scene.add(sun.target);
  hemi = new THREE.HemisphereLight(0xc4d8ef, 0x6f6a58, 0.45);
  scene.add(hemi);

  skyMat = new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: {
      top: { value: new THREE.Color(0x3f78c0) }, horizon: { value: new THREE.Color(0xdfe9f2) },
      bottom: { value: new THREE.Color(0xb9c2b0) }, sunDir: { value: new THREE.Vector3(0, 1, 0) },
      sunCol: { value: new THREE.Color(1.0, 0.92, 0.78) }, glow: { value: 1.0 },
    },
    vertexShader: `varying vec3 vDir; void main(){ vDir = normalize(position); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.0); }`,
    fragmentShader: `uniform vec3 top; uniform vec3 horizon; uniform vec3 bottom; uniform vec3 sunDir; uniform vec3 sunCol; uniform float glow;
      varying vec3 vDir;
      void main(){ vec3 d = normalize(vDir); float h = d.y;
        vec3 c = mix(horizon, top, pow(clamp(h,0.0,1.0), 0.55));
        c = mix(c, bottom, smoothstep(0.0, -0.08, h));
        c = mix(c, horizon * 1.08, exp(-abs(h) * 28.0) * 0.5);
        float s = max(dot(d, normalize(sunDir)), 0.0);
        c += sunCol * glow * (pow(s, 900.0)*6.0 + pow(s, 24.0)*0.18 + pow(s, 4.0)*0.06);
        gl_FragColor = vec4(c, 1.0); }`,
  });
  skyMesh = new THREE.Mesh(new THREE.SphereGeometry(4000, 48, 24), skyMat);
  skyMesh.frustumCulled = false;
  scene.add(skyMesh);

  groundDisc = new THREE.Mesh(new THREE.CircleGeometry(3800, 64),
    new THREE.MeshStandardMaterial({ color: 0x6f7f49, roughness: 1, metalness: 0 }));
  groundDisc.rotation.x = -Math.PI / 2;
  groundDisc.receiveShadow = true;
  scene.add(groundDisc);

  shadowPlane = new THREE.Mesh(new THREE.PlaneGeometry(400, 400), new THREE.ShadowMaterial({ opacity: 0.16 }));
  shadowPlane.rotation.x = -Math.PI / 2;
  shadowPlane.receiveShadow = true;
  shadowPlane.visible = false;
  scene.add(shadowPlane);
}

function tuneMaterials() {
  const maxAniso = renderer.capabilities.getMaxAnisotropy();
  root.traverse((o) => {
    if (!o.isMesh) return;
    const ud = o.userData || {};
    const pud = (o.parent && o.parent.userData) || {};
    const info = Object.keys(ud).length ? ud : pud;
    o.castShadow = info.castShadow !== false;
    o.receiveShadow = true;
    const mats = Array.isArray(o.material) ? o.material : [o.material];
    for (const m of mats) {
      if (m.map) { m.map.anisotropy = maxAniso; m.map.needsUpdate = true; }
      m.envMapIntensity = 0.9;
      const code = info.material || m.name || '';
      if (m.transparent || m.opacity < 0.999) {
        m.depthWrite = false;
        m.side = THREE.DoubleSide;
        o.renderOrder = 10;
      }
      if (code === 'SZKLO') {
        m.color.set(0x5d7682); m.roughness = 0.02; m.metalness = 0.35; m.envMapIntensity = 2.2; m.opacity = 0.5;
      } else if (code === 'SZKLO_BAL') {
        m.color.set(0x9fb8bf); m.roughness = 0.03; m.metalness = 0.2; m.envMapIntensity = 1.8; m.opacity = 0.22;
      }
      if (info.kind === 'terrain') { o.castShadow = false; }
    }
  });
}

function setSky(mode, sunDirT, elev) {
  // kolory nieba zależne od wysokości Słońca
  const low = Math.max(0, Math.min(1, (elev - 2) / 25));
  const top = new THREE.Color().setHSL(0.603, 0.78, 0.20 + 0.08 * low);
  const hor = new THREE.Color().lerpColors(new THREE.Color(0xf0cfa8), new THREE.Color(0xb4cde6), low);
  skyMat.uniforms.top.value.copy(top);
  skyMat.uniforms.horizon.value.copy(hor);
  skyMat.uniforms.bottom.value.copy(new THREE.Color(0xa9b39c));
  skyMat.uniforms.sunDir.value.copy(sunDirT);
  skyMat.uniforms.sunCol.value.copy(new THREE.Color().lerpColors(new THREE.Color(1.0, 0.62, 0.35), new THREE.Color(1.0, 0.93, 0.8), low));
  if (mode === 'studio') {
    // wartości HDR dobrane tak, by po ACES dać jasną szarość / biel
    skyMat.uniforms.top.value.setRGB(1.45, 1.47, 1.52); skyMat.uniforms.horizon.value.setRGB(1.9, 1.9, 1.9);
    skyMat.uniforms.bottom.value.setRGB(1.9, 1.9, 1.9); skyMat.uniforms.glow.value = 0.0;
  } else if (mode === 'white') {
    skyMat.uniforms.top.value.setRGB(40, 40, 40); skyMat.uniforms.horizon.value.setRGB(40, 40, 40);
    skyMat.uniforms.bottom.value.setRGB(40, 40, 40); skyMat.uniforms.glow.value = 0.0;
  } else {
    skyMat.uniforms.glow.value = 1.0;
  }
  // środowisko (odbicia, światło rozproszone) z nieba
  const envScene = new THREE.Scene();
  const s2 = new THREE.Mesh(new THREE.SphereGeometry(100, 32, 16), skyMat.clone());
  s2.material.uniforms = THREE.UniformsUtils.clone(skyMat.uniforms);
  s2.material.uniforms.glow.value = 0.25;
  if (mode !== 'sky') {
    s2.material.uniforms.top.value.setRGB(0.75, 0.78, 0.84); s2.material.uniforms.horizon.value.setRGB(0.9, 0.9, 0.9);
    s2.material.uniforms.bottom.value.setRGB(0.55, 0.55, 0.53);
  }
  envScene.add(s2);
  if (envRT) envRT.dispose();
  envRT = pmrem.fromScene(envScene, 0.02);
  scene.environment = envRT.texture;
  scene.environmentIntensity = mode === 'sky' ? 0.75 : 0.95;
  return { hor };
}

function boxOf(obj) {
  const b = new THREE.Box3();
  obj.updateMatrixWorld(true);
  obj.traverse((o) => { if (o.isMesh && o.visible !== false) b.expandByObject(o); });
  return b;
}

function b3ToBud(b) {
  if (b.isEmpty()) return null;
  const a = T2B(b.min), c = T2B(b.max);
  return [Math.min(a[0], c[0]), Math.min(a[1], c[1]), Math.min(a[2], c[2]), Math.max(a[0], c[0]), Math.max(a[1], c[1]), Math.max(a[2], c[2])];
}

async function load(url) {
  if (!renderer) initRenderer();
  const gltf = await new GLTFLoader().loadAsync(url);
  if (root) scene.remove(root);
  root = gltf.scene;
  scene.add(root);
  meta = (gltf.scene.userData && (gltf.scene.userData.metadata || gltf.scene.userData)) || {};
  if (meta.lamela) meta = meta.lamela;
  root.traverse((o) => {
    const nm = (o.userData && o.userData.id) || o.name;
    if (o.userData && o.userData.rola === 'grupa') { groups[nm] = o; basePos[nm] = o.position.clone(); }
  });
  tuneMaterials();
  const bud = new THREE.Box3();
  for (const [k, g] of Object.entries(groups)) {
    if (/^P\d+$/.test(k) || k === 'dach') bud.union(boxOf(g));
  }
  if (groups.teren) { const tb = boxOf(groups.teren); if (!tb.isEmpty()) terrainMinY = tb.min.y; }
  return { groups: Object.keys(groups), bbox_budynek: b3ToBud(bud), bbox_all: b3ToBud(boxOf(root)), meta };
}

function sunDirection(az, el, azY) {
  const a = THREE.MathUtils.degToRad(az - (azY || 0)), e = THREE.MathUtils.degToRad(el);
  return B2T([Math.sin(a) * Math.cos(e), Math.cos(a) * Math.cos(e), Math.sin(e)]).normalize();
}

async function render(cfg) {
  const W = Math.round(cfg.width * (cfg.ss || 2)), H = Math.round(cfg.height * (cfg.ss || 2));
  renderer.setSize(W, H, false);
  renderer.toneMappingExposure = cfg.exposure || 1.0;
  // krycie szkła (np. elewacje ortogonalne — bez prześwitu na tło)
  root.traverse((o) => {
    if (!o.isMesh) return;
    const m = o.material; const code = (o.userData && o.userData.material) || m.name;
    if (code === 'SZKLO') { if (m.userData.op0 === undefined) m.userData.op0 = m.opacity; m.opacity = cfg.glassOpacity || m.userData.op0; }
  });
  // widoczność i rozsunięcie grup
  for (const [k, g] of Object.entries(groups)) {
    g.visible = cfg.groups && k in cfg.groups ? !!cfg.groups[k] : true;
    g.position.copy(basePos[k]);
    if (cfg.explode && k in cfg.explode) g.position.y += cfg.explode[k];
  }
  // kamera
  const c = cfg.camera;
  let cam;
  const aspect = W / H;
  if (c.type === 'ortho') {
    const hh = c.halfHeight;
    cam = new THREE.OrthographicCamera(-hh * aspect, hh * aspect, hh, -hh, 0.1, 5000);
  } else {
    cam = new THREE.PerspectiveCamera(c.fov || 35, aspect, 0.1, 9000);
  }
  if (c.type !== 'ortho' && c.shift) {
    // obiektyw przesuwny (pion bez zbieżności): widok = górna część wirtualnej klatki wyższej o 2·shift
    const s = c.shift;
    const fullH = H * (1 + 2 * s);
    cam.fov = THREE.MathUtils.radToDeg(2 * Math.atan(Math.tan(THREE.MathUtils.degToRad(c.fov || 35) / 2) * (1 + 2 * s)));
    cam.aspect = W / fullH;
    cam.setViewOffset(W, fullH, 0, 0, W, H);
  }
  cam.position.copy(B2T(c.pos));
  cam.up.copy(c.up ? B2T(c.up) : new THREE.Vector3(0, 1, 0));
  cam.lookAt(B2T(c.target));
  cam.updateProjectionMatrix();
  skyMesh.position.copy(cam.position);
  // słońce
  const sd = sunDirection(cfg.sun.az, cfg.sun.el, meta.azymut_osi_y);
  const low = Math.max(0, Math.min(1, (cfg.sun.el - 2) / 25));
  sun.color.copy(new THREE.Color().lerpColors(new THREE.Color(1.0, 0.72, 0.48), new THREE.Color(1.0, 0.955, 0.9), low));
  sun.intensity = (cfg.sun.intensity || 3.2) * (0.55 + 0.45 * low);
  const sb = cfg.shadowBox;
  const smin = B2T([sb[0], sb[1], sb[2]]), smax = B2T([sb[3], sb[4], sb[5]]);
  const sbox = new THREE.Box3().setFromPoints([smin, smax]);
  const ctr = sbox.getCenter(new THREE.Vector3());
  const R = sbox.getSize(new THREE.Vector3()).length() / 2;
  sun.target.position.copy(ctr);
  sun.position.copy(ctr.clone().add(sd.clone().multiplyScalar(R + 150)));
  const sc = sun.shadow.camera;
  sc.left = -R; sc.right = R; sc.top = R; sc.bottom = -R; sc.near = 1; sc.far = 2 * R + 300;
  sc.updateProjectionMatrix();
  sun.shadow.mapSize.set(cfg.shadowMap || 4096, cfg.shadowMap || 4096);
  if (sun.shadow.map) { sun.shadow.map.dispose(); sun.shadow.map = null; }
  // tło, mgła, grunt
  const mode = cfg.bg || 'sky';
  const { hor } = setSky(mode, sd, cfg.sun.el);
  skyMesh.visible = true;
  hemi.intensity = mode === 'sky' ? 0.45 : 0.75;
  groundDisc.visible = mode === 'sky' && cfg.groundDisc !== false;
  groundDisc.position.y = terrainMinY - 0.25;
  shadowPlane.visible = mode !== 'sky';
  if (shadowPlane.visible) {
    const vb = new THREE.Box3();
    for (const [k, g] of Object.entries(groups)) if (g.visible && k !== 'budynek') vb.union(boxOf(g));
    shadowPlane.position.set(ctr.x, (vb.isEmpty() ? 0 : vb.min.y) - 0.01, ctr.z);
  }
  scene.fog = cfg.fog ? new THREE.Fog(hor.clone(), cfg.fogNear || 120, cfg.fogFar || 900) : null;
  // pas terenu (elewacje ortogonalne): pionowa płyta przed budynkiem do rzędnej terenu
  if (groundBand) { scene.remove(groundBand); groundBand = null; }
  if (cfg.groundBand) {
    const gb = cfg.groundBand;
    groundBand = new THREE.Mesh(new THREE.BoxGeometry(400, gb.depth || 3.0, 0.05),
      new THREE.MeshBasicMaterial({ color: new THREE.Color(gb.color || '#8a8f7a') }));
    groundBand.position.copy(B2T([gb.x || 0, gb.y, gb.z - (gb.depth || 3.0) / 2]));
    const line = new THREE.Mesh(new THREE.BoxGeometry(400, 0.05, 0.06), new THREE.MeshBasicMaterial({ color: new THREE.Color(gb.line || '#4a4e44') }));
    line.position.set(0, (gb.depth || 3.0) / 2 - 0.025, 0.01);
    groundBand.add(line);
    scene.add(groundBand);
  }
  // kompozycja: N8AO (SSAO) → OutputPass (ACES + sRGB)
  const composer = new EffectComposer(renderer, new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType }));
  composer.setPixelRatio(1);
  composer.setSize(W, H);
  if (cfg.ao !== false) {
    const n8 = new N8AOPass(scene, cam, W, H);
    n8.configuration.aoRadius = cfg.aoRadius || 1.4;
    n8.configuration.distanceFalloff = cfg.aoFalloff || 0.8;
    n8.configuration.intensity = cfg.aoIntensity || 2.2;
    n8.configuration.aoSamples = 16;
    n8.configuration.denoiseSamples = 8;
    n8.configuration.denoiseRadius = 10;
    n8.configuration.halfRes = false;
    n8.configuration.gammaCorrection = false;
    n8.configuration.transparencyAware = true;
    composer.addPass(n8);
  } else {
    composer.addPass(new RenderPass(scene, cam));
  }
  composer.addPass(new OutputPass());
  composer.render();
  composer.render();
  const url = renderer.domElement.toDataURL('image/png');
  composer.dispose();
  // etykiety (np. kondygnacje w aksonometrii): rzut punktów kotwiczących na obraz [px w rozdzielczości cfg.width]
  const labels = [];
  for (const lb of cfg.labels || []) {
    const g = groups[lb.group];
    if (!g || !g.visible) continue;
    const b = boxOf(g);
    if (b.isEmpty()) continue;
    const bb = b3ToBud(b);
    const pt = [bb[0] + (lb.dx || 0), (bb[1] + bb[4]) / 2 + (lb.dy || 0), (bb[2] + bb[5]) / 2 + (lb.dz || 0)];
    const v = B2T(pt).project(cam);
    labels.push({ text: lb.text, group: lb.group, x: (v.x + 1) / 2 * cfg.width, y: (1 - v.y) / 2 * cfg.height });
  }
  return { url, labels };
}

// rzędna terenu (układ budynku) w punktach [x, y] — promień w dół na siatki grupy 'teren'
function groundZ(points) {
  const rc = new THREE.Raycaster();
  const tgt = groups.teren ? [groups.teren] : [root];
  return points.map((p) => {
    rc.set(B2T([p[0], p[1], 500]), new THREE.Vector3(0, -1, 0));
    const hit = rc.intersectObjects(tgt, true)[0];
    return hit ? T2B(hit.point)[2] : null;
  });
}

window.LAMELA = { load, render, groundZ, ready: true };
window.__lamelaReady = true;
