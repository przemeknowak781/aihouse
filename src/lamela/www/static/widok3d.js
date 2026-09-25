/* Dom LAMELA — interaktywny model 3D (three.js r147 UMD + GLTFLoader/OrbitControls non-module).
   Plik glb ładowany fetch() z assets/ dopiero po kliknięciu (oszczędność transferu). Układ modelu: x→E, y→N, z↑;
   three.js: X = x, Y = z, Z = −y (jak tools/render3d/render.js). */
(function () {
  'use strict';
  var box = document.getElementById('v3d'), btn = document.getElementById('v3d-start');
  if (!box || !btn) return;
  var cfg = JSON.parse(document.getElementById('dane-3d').textContent);
  var stan = document.getElementById('v3d-stan');
  var ster = Array.prototype.slice.call(document.querySelectorAll('#v3d-ster button'));
  var ruch = !(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  var T, renderer, scene, cam, ctl, grupy = {}, baza = {}, rozsun = 0, cel = 0, anim = null, lot = null;
  function B2T(p) { return new T.Vector3(p[0], p[2], -p[1]); }
  function tokenTla() {
    var c = getComputedStyle(box).getPropertyValue('--d-tlo').trim();
    return c || '#F4F4F0';
  }
  function msg(t) { if (stan) stan.textContent = t; }

  function start() {
    if (!window.THREE || !THREE.GLTFLoader || !THREE.OrbitControls) {
      msg('Nie udało się wczytać biblioteki three.js z CDN — widok 3D jest niedostępny.');
      return;
    }
    T = window.THREE;
    try {
      renderer = new T.WebGLRenderer({ antialias: true, alpha: false });
    } catch (e) { msg('Ta przeglądarka nie obsługuje WebGL — widok 3D jest niedostępny.'); return; }
    btn.disabled = true;
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.outputEncoding = T.sRGBEncoding;
    renderer.toneMapping = T.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.0;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = T.PCFSoftShadowMap;
    scene = new T.Scene();
    scene.background = new T.Color(tokenTla());
    if (T.RoomEnvironment) {
      var pm = new T.PMREMGenerator(renderer);
      scene.environment = pm.fromScene(new T.RoomEnvironment(), 0.04).texture;
    }
    scene.add(new T.HemisphereLight(0xdfe8f0, 0x6f6a58, 0.55));
    var sun = new T.DirectionalLight(0xfff1dc, 2.4);
    var s = cfg.slonce;
    sun.position.copy(B2T([cfg.srodek[0] + 60 * s[0], cfg.srodek[1] + 60 * s[1], 60 * s[2]]));
    sun.target.position.copy(B2T(cfg.srodek));
    sun.castShadow = true;
    sun.shadow.mapSize.set(2048, 2048);
    var R = cfg.promien * 1.6;
    Object.assign(sun.shadow.camera, { left: -R, right: R, top: R, bottom: -R, near: 1, far: 250 });
    sun.shadow.bias = -0.0004;
    scene.add(sun, sun.target);
    cam = new T.PerspectiveCamera(40, 1, 0.3, 4000);
    ctl = new T.OrbitControls(cam, renderer.domElement);
    ctl.enableDamping = ruch;
    ctl.target.copy(B2T(cfg.srodek));
    ctl.maxPolarAngle = Math.PI * 0.495;
    ctl.minDistance = 4; ctl.maxDistance = cfg.promien * 8;
    ctl.addEventListener('change', rysuj);
    box.appendChild(renderer.domElement);
    renderer.domElement.setAttribute('aria-label', 'Model 3D domu — przeciągnij, aby obrócić; kółko lub dwa palce, aby przybliżyć');
    renderer.domElement.tabIndex = 0;
    new ResizeObserver(rozmiar).observe(box);
    rozmiar();
    widok('ogrod', true);
    wczytaj();
  }

  function wczytaj() {
    msg('Wczytywanie modelu…');
    fetch(cfg.plik).then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      var n = +r.headers.get('Content-Length') || 0;
      if (!r.body || !n) return r.arrayBuffer();
      var rd = r.body.getReader(), got = 0, parts = [];
      function pump() {
        return rd.read().then(function (x) {
          if (x.done) {
            var u = new Uint8Array(got), o = 0;
            parts.forEach(function (p) { u.set(p, o); o += p.length; });
            return u.buffer;
          }
          parts.push(x.value); got += x.value.length;
          msg('Wczytywanie modelu… ' + Math.round(100 * got / n) + ' %');
          return pump();
        });
      }
      return pump();
    }).then(function (buf) {
      new T.GLTFLoader().parse(buf, '', gotowy, function () { msg('Plik modelu jest uszkodzony.'); });
    }).catch(function (e) { msg('Nie udało się pobrać modelu (' + e.message + ').'); });
  }
