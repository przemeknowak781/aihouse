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
  var T, renderer, scene, cam, ctl, grupy = {}, baza = {}, rozsun = 0, cel = 0, anim = null, lot = null, spoczynek = 0;
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
    ctl.addEventListener('change', function () { spoczynek = 0; rysuj(); });
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

  function gotowy(gltf) {
    var root = gltf.scene;
    root.traverse(function (o) {
      var ud = o.userData || {};
      if (ud.rola === 'grupa') { var k = ud.id || o.name; grupy[k] = o; baza[k] = o.position.y; }
      if (!o.isMesh) return;
      o.castShadow = true; o.receiveShadow = true;
      var mats = Array.isArray(o.material) ? o.material : [o.material];
      mats.forEach(function (m) {
        var kod = (ud.material || m.name || '');
        if (m.transparent || m.opacity < 0.999) { m.depthWrite = false; m.side = T.DoubleSide; o.renderOrder = 10; }
        if (kod === 'SZKLO') { m.color.set(0x5d7682); m.roughness = 0.05; m.metalness = 0.3; m.opacity = 0.5; m.transparent = true; }
        if (m.map) m.map.anisotropy = renderer.capabilities.getMaxAnisotropy();
      });
      if (ud.kind === 'terrain' || (o.parent && o.parent.userData && o.parent.userData.kind === 'terrain')) o.castShadow = false;
    });
    scene.add(root);
    ster.forEach(function (b) { b.disabled = false; });
    msg('Przeciągnij, aby obrócić · kółko lub dwa palce — przybliżenie · prawy przycisk — przesunięcie');
    rysuj();
  }

  function rozmiar() {
    var w = box.clientWidth, h = box.clientHeight;
    if (!w || !h) return;
    renderer.setSize(w, h, false);
    cam.aspect = w / h; cam.updateProjectionMatrix();
    rysuj();
  }
  function rysuj() { if (renderer) renderer.render(scene, cam); }

  function petla() {
    var dalej = false;
    if (Math.abs(cel - rozsun) > 0.002) {
      rozsun += (cel - rozsun) * (ruch ? 0.14 : 1);
      if (Math.abs(cel - rozsun) <= 0.002) rozsun = cel;
      cfg.kolejnosc.forEach(function (k, i) { if (grupy[k]) grupy[k].position.y = baza[k] + rozsun * i * cfg.krok; });
      dalej = true;
    }
    if (lot) {
      lot.t = Math.min(1, lot.t + (ruch ? 0.045 : 1));
      var e = lot.t < 0.5 ? 2 * lot.t * lot.t : 1 - Math.pow(-2 * lot.t + 2, 2) / 2;
      cam.position.lerpVectors(lot.p0, lot.p1, e);
      ctl.target.lerpVectors(lot.c0, lot.c1, e);
      if (lot.t >= 1) lot = null; else dalej = true;
    }
    ctl.update();
    rysuj();
    if (dalej) spoczynek = 0;
    anim = (dalej || (ctl.enableDamping && spoczynek++ < 90)) ? requestAnimationFrame(petla) : null;
  }
  function budz() { spoczynek = 0; if (!anim) anim = requestAnimationFrame(petla); }
  ['pointerdown', 'wheel', 'touchstart'].forEach(function (ev) {
    box.addEventListener(ev, budz, { passive: true });
  });

  function widok(nazwa, odRazu) {
    var v = cfg.widoki[nazwa];
    if (!v || !cam) return;
    var p1 = B2T(v.poz), c1 = B2T(v.cel);
    if (odRazu || !ruch) { cam.position.copy(p1); ctl.target.copy(c1); ctl.update(); rysuj(); return; }
    lot = { t: 0, p0: cam.position.clone(), p1: p1, c0: ctl.target.clone(), c1: c1 };
    budz();
  }

  btn.addEventListener('click', function () {
    var pl = document.getElementById('v3d-plakat');
    if (pl) pl.hidden = true;
    start();
  });
  ster.forEach(function (b) {
    b.addEventListener('click', function () {
      var w = b.getAttribute('data-widok'), t = b.getAttribute('data-przelacz');
      if (w) { widok(w, false); return; }
      if (t === 'rozsun') {
        cel = cel ? 0 : 1; b.setAttribute('aria-pressed', cel ? 'true' : 'false'); budz();
      } else if (t === 'otoczenie') {
        var on = b.getAttribute('aria-pressed') !== 'true';
        b.setAttribute('aria-pressed', on ? 'true' : 'false');
        cfg.otoczenie.forEach(function (k) { if (grupy[k]) grupy[k].visible = on; });
        rysuj();
      }
    });
  });
  /* zmiana motywu (system lub data-theme) → tło sceny z tokenu */
  function motyw() { if (scene) { scene.background = new T.Color(tokenTla()); rysuj(); } }
  if (window.matchMedia) {
    var mq = window.matchMedia('(prefers-color-scheme: dark)');
    if (mq.addEventListener) mq.addEventListener('change', motyw);
  }
  new MutationObserver(motyw).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
})();
