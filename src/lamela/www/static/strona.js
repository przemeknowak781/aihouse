/* Dom LAMELA — zachowania strony: zakładki, lupa galerii, podświetlanie pomieszczeń, formularz DEMO, kopiowanie adresu. */
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* zakładki (role="tablist"): klik + strzałki */
  $$('[role="tablist"]').forEach(function (tl) {
    var tabs = $$('[role="tab"]', tl);
    function pokaz(t, fokus) {
      tabs.forEach(function (x) {
        var on = x === t;
        x.setAttribute('aria-selected', on ? 'true' : 'false');
        x.tabIndex = on ? 0 : -1;
        var p = document.getElementById(x.getAttribute('aria-controls'));
        if (p) p.hidden = !on;
      });
      if (fokus) t.focus();
    }
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { pokaz(t, false); });
      t.addEventListener('keydown', function (e) {
        var k = e.key, j = i;
        if (k === 'ArrowRight') j = (i + 1) % tabs.length;
        else if (k === 'ArrowLeft') j = (i - 1 + tabs.length) % tabs.length;
        else if (k === 'Home') j = 0;
        else if (k === 'End') j = tabs.length - 1;
        else return;
        e.preventDefault();
        pokaz(tabs[j], true);
      });
    });
  });

  /* zestawienie pomieszczeń ↔ rzut */
  $$('tr[data-pom]').forEach(function (tr) {
    var id = tr.getAttribute('data-pom');
    var panel = tr.closest('.panel');
    function hi(on) {
      tr.classList.toggle('hi', on);
      if (!panel) return;
      $$('[data-pom="' + id + '"]', panel).forEach(function (el) { if (el !== tr) el.classList.toggle('hi', on); });
    }
    tr.addEventListener('mouseenter', function () { hi(true); });
    tr.addEventListener('mouseleave', function () { hi(false); });
    tr.addEventListener('focusin', function () { hi(true); });
    tr.addEventListener('focusout', function () { hi(false); });
  });

  /* lupa galerii (<dialog>, bez pobierania plików) */
  var dlg = $('#lupa'), dImg = $('#lupa-img'), dOpis = $('#lupa-opis');
  var kafle = $$('.gal button[data-duzy]'), idx = 0;
  function otworz(i) {
    idx = (i + kafle.length) % kafle.length;
    var b = kafle[idx];
    dImg.src = b.getAttribute('data-duzy');
    dImg.alt = b.querySelector('img').alt;
    dOpis.textContent = b.getAttribute('data-opis') || '';
    if (!dlg.open) { if (dlg.showModal) dlg.showModal(); else dlg.setAttribute('open', ''); }
  }
  kafle.forEach(function (b, i) { b.addEventListener('click', function () { otworz(i); }); });
  if (dlg) {
    $('#lupa-zamknij').addEventListener('click', function () { dlg.close(); });
    $('#lupa-nast').addEventListener('click', function () { otworz(idx + 1); });
    $('#lupa-poprz').addEventListener('click', function () { otworz(idx - 1); });
    dlg.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') otworz(idx + 1);
      if (e.key === 'ArrowLeft') otworz(idx - 1);
    });
    dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });
  }

  /* kopiowanie adresu (adres pokazany jako tekst; schowek może być niedostępny) */
  $$('[data-kopiuj]').forEach(function (b) {
    b.addEventListener('click', function () {
      var el = document.getElementById(b.getAttribute('data-kopiuj'));
      var txt = el ? el.textContent : '';
      function zaznacz() {
        var r = document.createRange(); r.selectNodeContents(el);
        var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
        b.textContent = 'Zaznaczono — skopiuj';
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(txt).then(function () { b.textContent = 'Skopiowano'; }, zaznacz);
      } else { zaznacz(); }
    });
  });

  /* formularz DEMO: walidacja, preventDefault, podsumowanie na stronie — nic nie jest wysyłane */
  var f = $('#form-zap');
  if (f) {
    var reguly = {
      'z-imie': function (v) { return v.trim().length >= 2 ? '' : 'Podaj imię i nazwisko (co najmniej 2 znaki).'; },
      'z-email': function (v) { return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v.trim()) ? '' : 'Podaj adres e-mail w formacie nazwa@domena.pl.'; },
      'z-tel': function (v) { return !v.trim() || /^[+0-9 ()-]{7,20}$/.test(v.trim()) ? '' : 'Telefon może zawierać cyfry, spacje, +, - i nawiasy (7–20 znaków).'; },
      'z-temat': function (v) { return v ? '' : 'Wybierz temat zapytania.'; },
      'z-tresc': function (v) { return v.trim().length >= 10 ? '' : 'Opisz krótko, czego dotyczy zapytanie (co najmniej 10 znaków).'; },
      'z-zgoda': function (v, el) { return el.checked ? '' : 'Zaznacz, że rozumiesz demonstracyjny charakter formularza.'; }
    };
    function sprawdz(id) {
      var el = document.getElementById(id), msg = reguly[id](el.value, el);
      var b = document.getElementById(id + '-blad');
      el.setAttribute('aria-invalid', msg ? 'true' : 'false');
      if (b) b.textContent = msg;
      return !msg;
    }
    Object.keys(reguly).forEach(function (id) {
      var el = document.getElementById(id);
      el.addEventListener('blur', function () { if (el.value || el.type === 'checkbox') sprawdz(id); });
      el.addEventListener('change', function () { sprawdz(id); });
    });
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var ok = Object.keys(reguly).map(sprawdz).every(Boolean);
      var w = $('#wynik');
      if (!ok) {
        var pierwszy = $('[aria-invalid="true"]', f);
        if (pierwszy) pierwszy.focus();
        w.hidden = true;
        return;
      }
      var dl = $('#wynik-dl'); dl.textContent = '';
      [['Imię i nazwisko', 'z-imie'], ['E-mail', 'z-email'], ['Telefon', 'z-tel'], ['Temat', 'z-temat'], ['Pakiet', 'z-pakiet'],
       ['Lokalizacja działki', 'z-miejsce'], ['Treść', 'z-tresc']].forEach(function (p) {
        var v = document.getElementById(p[1]).value.trim(); if (!v) return;
        var dt = document.createElement('dt'); dt.textContent = p[0];
        var dd = document.createElement('dd'); dd.textContent = v;
        dl.appendChild(dt); dl.appendChild(dd);
      });
      w.hidden = false;
      w.focus();
    });
    f.addEventListener('reset', function () {
      $('#wynik').hidden = true;
      Object.keys(reguly).forEach(function (id) {
        document.getElementById(id).setAttribute('aria-invalid', 'false');
        var b = document.getElementById(id + '-blad'); if (b) b.textContent = '';
      });
    });
  }
})();
