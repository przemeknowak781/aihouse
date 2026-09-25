// Renderer ujęć marketingowych strony www — NAKŁADKA na tools/render3d/render.js (bez kopiowania i bez zmian w nim).
// Dodaje wyłącznie otoczenie i wygląd terenu; budynek renderuje się bez zmian (te same materiały co w pipeline):
//  * trawa: stonowany kolor bez powtarzalnej tekstury (szum w układzie świata, skala kilku metrów),
//  * dalszy plan: pas zieleni (korony drzew) na pierścieniu 85–170 m wokół budynku zamiast pustego horyzontu,
//  * szkło: nieco mocniejsze odbicia nieba (subtelne).
// Scena render.js jest przechwytywana przez Object3D.prototype.add (moduł three jest współdzielony przez importmap).
import * as THREE from 'three';
import '/r3d/render.js';

let scena = null;
const _add = THREE.Object3D.prototype.add;
THREE.Object3D.prototype.add = function (...o) {
  if (this.isScene && !scena) scena = this;
  return _add.apply(this, o);
};

function rng(seed) {
  let s = seed >>> 0;
  return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
}

function trawa(m) {
  m.map = null;
  m.color.set(0x6e7c52);
  m.roughness = 1.0;
  m.onBeforeCompile = (sh) => {
    sh.vertexShader = sh.vertexShader
      .replace('void main() {', 'varying vec3 vWp;\nvoid main() {')
      .replace('#include <begin_vertex>', '#include <begin_vertex>\nvWp = (modelMatrix * vec4(transformed, 1.0)).xyz;');
    sh.fragmentShader = sh.fragmentShader
      .replace('void main() {', `varying vec3 vWp;
float hh(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float vn(vec2 p){ vec2 i = floor(p), f = fract(p); vec2 u = f * f * (3.0 - 2.0 * f);
  return mix(mix(hh(i), hh(i + vec2(1, 0)), u.x), mix(hh(i + vec2(0, 1)), hh(i + vec2(1, 1)), u.x), u.y); }
void main() {`)
      .replace('#include <color_fragment>', `#include <color_fragment>
float n = 0.55 * vn(vWp.xz / 9.0) + 0.3 * vn(vWp.xz / 2.7 + 17.0) + 0.15 * vn(vWp.xz / 0.6 + 41.0);
diffuseColor.rgb *= 0.86 + 0.26 * n;`);
  };
  m.needsUpdate = true;
}

function pasZieleni(c, zGrunt) {
  // drzewa tła: po 3 bryły korony na drzewo, pierścień 80–175 m, ciemniejsza zieleń (mgła rozjaśnia dalszy plan)
  const r = rng(20260925);
  const nd = 210, nb = 3;
  const geo = new THREE.IcosahedronGeometry(1, 2);
  const mat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 1, metalness: 0 });
  const im = new THREE.InstancedMesh(geo, mat, nd * nb);
  const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), col = new THREE.Color();
  let k = 0;
  for (let i = 0; i < nd; i++) {
    const a = r() * Math.PI * 2, R = 80 + r() * 95;
    const h = 8 + r() * 9, rx = 3.2 + r() * 3.6;
    const x = c.x + Math.cos(a) * R, z = c.z + Math.sin(a) * R;
    const hue = 0.22 + r() * 0.07, sat = 0.22 + r() * 0.14, lum = 0.14 + r() * 0.09;
    for (let j = 0; j < nb; j++) {
      const ox = (r() - 0.5) * rx * 1.1, oz = (r() - 0.5) * rx * 1.1, s = 0.62 + r() * 0.38;
      m4.compose(new THREE.Vector3(x + ox, zGrunt + h * (0.55 + 0.25 * r()), z + oz), q,
                 new THREE.Vector3(rx * s, h * 0.42 * s, rx * s));
      im.setMatrixAt(k, m4);
      col.setHSL(hue, sat, lum * (0.9 + 0.2 * r()));
      im.setColorAt(k, col);
      k++;
    }
  }
  im.castShadow = false;
  im.receiveShadow = false;
  im.name = 'pas_zieleni_www';
  return im;
}

const LAMELA = window.LAMELA;
const _load = LAMELA.load;
LAMELA.load = async (url) => {
  const info = await _load(url);
  const b = info.bbox_budynek;
  const c = new THREE.Vector3((b[0] + b[3]) / 2, 0, -(b[1] + b[4]) / 2);
  const zg = (info.meta && info.meta.dzialka && info.meta.dzialka.teren_z_budynek) || 0;
  scena.traverse((o) => {
    if (!o.isMesh) return;
    const mats = Array.isArray(o.material) ? o.material : [o.material];
    for (const m of mats) {
      const kod = (o.userData && o.userData.material) || m.name || '';
      if (kod === 'TEREN_TRAWA' || kod === 'TEREN_POZA') trawa(m);
      if (kod === 'SZKLO') { m.envMapIntensity = 2.6; m.metalness = 0.45; m.roughness = 0.03; }
    }
    if (o.geometry && o.geometry.type === 'CircleGeometry') { o.material.color.set(0x66744b); trawa(o.material); }
  });
  scena.add(pasZieleni(c, zg - 0.3));
  return info;
};
window.LAMELA_WWW = true;
