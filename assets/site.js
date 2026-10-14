/* Roomi Movers: small page tools. Everything is optional: pages work without this file. */
(function () {
  'use strict';
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return [].slice.call((r || document).querySelectorAll(s)); }
  /* When real hourly rates are ready, fill these in (for example 'Full-Service Move': 'from $__ per hour') and the finder shows them. */
  var RATES = window.ROOMI_RATES || {};
  function store(k, v) { try { if (v === undefined) return JSON.parse(localStorage.getItem(k) || 'null'); localStorage.setItem(k, JSON.stringify(v)); } catch (e) { return null; } }

  /* ---- package finder: three or four answers become a recommendation and a prefilled estimate request ---- */
  $$('[data-finder]').forEach(function (root) {
    var out = $('.finder-result', root);
    function val(name) { var e = $('input[name="' + name + '"]:checked', root); return e ? e.value : ''; }
    var SIZE = { studio: 'Studio / 1 bedroom', two: '2 bedrooms', three: '3 bedrooms', four: '4+ bedrooms', few: 'Just a few items' };
    function render() {
      var truck = val('truck'), size = val('size'), care = val('care');
      var flags = $$('input[name="flag"]:checked', root).map(function (c) { return c.value; });
      $('[data-needs-truck]', root).hidden = truck !== 'no';
      $('[data-needs-care]', root).hidden = truck !== 'no';
      var ready = truck === 'yes' || (truck === 'no' && size && care);
      if (!ready) { out.hidden = true; return; }
      var pkg, why;
      if (truck === 'yes') {
        pkg = 'Labor Only';
        why = 'You already have the truck, container or storage unit, so you need two movers to load or unload it, with pads, straps and dollies.';
      } else if (care === 'protect' || size === 'four') {
        pkg = 'White-Glove Move';
        why = size === 'four' && care !== 'protect'
          ? 'A larger home is what White-Glove is built for: floor runners and door-frame guards, boxed TVs, art and mirrors, furniture placed room by room, and an extra crew member.'
          : 'You want extra protection, which is what White-Glove adds: floor runners and door-frame guards, boxed TVs, art and mirrors, furniture placed room by room, and an extra crew member.';
      } else {
        pkg = 'Full-Service Move';
        why = 'The box truck is included, your furniture is wrapped and padded, and beds are taken apart and set back up.';
      }
      var tell = ['Your move date and both addresses (city or ZIP is fine)'];
      if (flags.indexOf('stairs') > -1) tell.push('Which floors, and whether there are stairs, at both addresses');
      if (flags.indexOf('heavy') > -1) tell.push('The item, its size and weight, and where it is going (items over 300 lbs may add to the price)');
      if (flags.indexOf('tight') > -1) tell.push('How far the truck will be from the door, or any tight hallways or doorways');
      var notes = 'Package I was looking at: ' + pkg + '.' + (flags.length ? ' Flags: ' + flags.join(', ') + '.' : '');
      var size_q = truck === 'yes' ? 'Labor only (my truck)' : SIZE[size] || '';
      var href = '/contact/?size=' + encodeURIComponent(size_q) + '&notes=' + encodeURIComponent(notes) + '#quote';
      out.innerHTML = '<p class="finder-kicker">A good fit</p><h3>' + pkg + '</h3><p>' + why + '</p>' +
        (RATES[pkg] ? '<p class="finder-sub">' + RATES[pkg] + '</p>' : '') + '<p class="finder-sub">When you ask for your estimate, tell us:</p><ul class="ticks">' + tell.map(function (t) { return '<li>' + t.replace(/&/g, '&amp;').replace(/</g, '&lt;') + '</li>'; }).join('') + '</ul>' +
        '<p style="margin-top:18px"><a class="btn btn-primary" href="' + href + '">Request a free estimate for this</a></p>' +
        '<p class="finder-fine">This is a guide, not a quote. Your free estimate shows your hourly rate and the time we expect.</p>';
      out.hidden = false;
    }
    root.addEventListener('change', render);
    render();
  });

  /* ---- FAQ search ---- */
  $$('[data-faq-search]').forEach(function (input) {
    var items = $$('.faq details'), empty = $('[data-faq-empty]');
    function run() {
      var q = input.value.trim().toLowerCase(), shown = 0;
      items.forEach(function (d) {
        var hit = !q || d.textContent.toLowerCase().indexOf(q) > -1;
        d.hidden = !hit;
        if (hit) shown++;
        if (q && hit) d.open = true;
      });
      if (!q && items[0]) { items.forEach(function (d, i) { d.open = i === 0; }); }
      if (empty) empty.hidden = shown > 0;
    }
    input.addEventListener('input', run);
  });

  /* ---- area finder ---- */
  $$('[data-area-filter]').forEach(function (input) {
    var items = $$('.cities.all li'), msg = $('[data-area-msg]');
    input.addEventListener('input', function () {
      var q = input.value.trim().toLowerCase(), n = 0;
      items.forEach(function (li) { var hit = !q || li.textContent.toLowerCase().indexOf(q) > -1; li.hidden = !hit; if (hit) n++; });
      if (msg) {
        msg.hidden = !(q && n === 0);
      }
    });
  });

  /* ---- checklist: remembers what you ticked on this device ---- */
  $$('[data-checklist]').forEach(function (root) {
    var key = 'roomi-checklist-' + root.getAttribute('data-checklist');
    var boxes = $$('input[type="checkbox"]', root), saved = store(key) || {}, label = $('[data-progress]', root.parentNode) || $('[data-progress]');
    function update() {
      var done = boxes.filter(function (b) { return b.checked; }).length;
      if (label) label.textContent = done + ' of ' + boxes.length + ' done';
      var bar = $('[data-bar]');
      if (bar) bar.style.transform = 'scaleX(' + (boxes.length ? done / boxes.length : 0) + ')';
    }
    boxes.forEach(function (b, i) {
      b.checked = !!saved[i];
      b.addEventListener('change', function () {
        var s = {}; boxes.forEach(function (x, j) { if (x.checked) s[j] = 1; });
        store(key, s); update();
      });
    });
    update();
    var reset = $('[data-reset]'); if (reset) reset.addEventListener('click', function () { boxes.forEach(function (b) { b.checked = false; }); store(key, {}); update(); });
    var print = $('[data-print]'); if (print) print.addEventListener('click', function () { window.print(); });
  });

  /* ---- estimate form prefill from ?size= and ?notes= ---- */
  var form = document.getElementById('quoteForm');
  if (form) {
    try {
      var p = new URLSearchParams(location.search);
      if (p.get('size') && form.elements.size) {
        var want = p.get('size');
        [].forEach.call(form.elements.size.options, function (o) { if (o.text === want || o.value === want) form.elements.size.value = o.value; });
      }
      if (p.get('notes') && form.elements.notes && !form.elements.notes.value) form.elements.notes.value = p.get('notes');
    } catch (e) { /* the form still works without prefill */ }
  }
})();
