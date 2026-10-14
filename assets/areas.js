/* Roomi Movers area finder.
   Type a ZIP code, a city or a neighborhood. Suggestions are generated from the service-area data (assets/areas-data.js, built from the
   same list as the area pages). Every result, including places we do not list, carries an estimate request that goes to the company inbox.
   Coverage statements only ever come from that data: an unlisted place is never described as served. */
(function () {
  'use strict';
  var D = window.ROOMI_AREAS, F = window.ROOMI_FACTS || {};
  var root = document.querySelector('[data-area-finder]');
  if (!D || !root) return;

  var input = root.querySelector('input'), list = root.querySelector('[data-af-list]'), clearBtn = root.querySelector('[data-af-clear]');
  var out = root.querySelector('[data-af-result]'), status = root.querySelector('[data-af-status]');
  var chips = [].slice.call(document.querySelectorAll('.cities.all li'));
  var ENDPOINT = F.formEndpoint || 'https://formsubmit.co/ajax/roomimovers@gmail.com';
  var PHONE = F.phone || '(813) 436-3216', TEL = 'tel:' + (F.tel || '+18134363216');
  var SIZES = ['Studio / 1 bedroom', '2 bedrooms', '3 bedrooms', '4+ bedrooms', 'Just a few items', 'Labor only (my truck)'];

  /* ---------- data ---------- */
  var BYSLUG = {}, ZIP = {}, CAND = [];
  var ALIAS = { 'town-n-country': ['town and country', 'townncountry', 'tnc'], 'land-o-lakes': ['land of lakes', 'landolakes'], 'egypt-lake-leto': ['egypt lake', 'leto'] };
  function norm(s) {
    return String(s).toLowerCase().replace(/[’']/g, '').replace(/\band\b/g, 'n').replace(/[^a-z0-9]+/g, ' ').replace(/\s+/g, ' ').trim();
  }
  D.a.forEach(function (a) {
    BYSLUG[a.s] = a;
    a.z.forEach(function (z) { (ZIP[z] = ZIP[z] || { areas: [], place: null }).areas.push(a.s); });
    CAND.push({ t: 'area', key: a.s, label: a.n, area: a, names: [norm(a.n)].concat((ALIAS[a.s] || []).map(norm)) });
    (a.k || []).forEach(function (k) { CAND.push({ t: 'hood', key: a.s + ':' + k, label: k, area: a, names: [norm(k)] }); });
  });
  D.p.forEach(function (p) {
    p.z.forEach(function (z) { (ZIP[z] = ZIP[z] || { areas: [], place: null }).place = p; });
    CAND.push({ t: 'place', key: 'p:' + p.n, label: p.n, place: p, names: [norm(p.n)] });
  });
  // a ZIP shared by a neighborhood area and Tampa lists the specific area first
  Object.keys(ZIP).forEach(function (z) { ZIP[z].areas.sort(function (x, y) { return (x === 'tampa') - (y === 'tampa'); }); });
  var ZIPS_SORTED = Object.keys(ZIP).sort();

  function nameList(slugs) {
    var n = slugs.map(function (s) { return BYSLUG[s].n; });
    return n.length < 2 ? n.join('') : n.slice(0, -1).join(', ') + ' and ' + n[n.length - 1];
  }
  function lev(a, b, max) {
    if (Math.abs(a.length - b.length) > max) return max + 1;
    var prev = [], cur, i, j;
    for (j = 0; j <= b.length; j++) prev[j] = j;
    for (i = 1; i <= a.length; i++) {
      cur = [i];
      for (j = 1; j <= b.length; j++) cur[j] = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a.charAt(i - 1) === b.charAt(j - 1) ? 0 : 1));
      prev = cur;
    }
    return prev[b.length];
  }
  function scoreName(q, c) {
    if (c === q) return 100;
    if (c.indexOf(q) === 0) return 90 - (c.length - q.length) * 0.4;
    if (c.split(' ').some(function (w) { return w.indexOf(q) === 0; })) return 76;
    if (q.length >= 3 && c.indexOf(q) > -1) return 60;
    if (c.length >= 4 && (' ' + q + ' ').indexOf(' ' + c + ' ') > -1) return 72;
    if (q.length >= 4) {
      var max = c.length >= 7 ? 2 : 1, d = lev(q, c, max);
      if (d <= max) return 52 - d * 6;
      var words = c.split(' ');
      if (words.length > 1) for (var i = 0; i < words.length; i++) if (words[i].length >= 4 && lev(q, words[i], 1) <= 1) return 44;
    }
    return 0;
  }

  /* ---------- the generator: whatever is typed becomes a ranked list of options ---------- */
  function zipOption(z) {
    var e = ZIP[z];
    if (e && e.areas.length) return { kind: 'zip', zip: z, areas: e.areas, label: z, sub: nameList(e.areas) };
    if (e && e.place) return { kind: 'zipplace', zip: z, place: e.place, label: z, sub: e.place.n + ' · not on our list yet' };
    return null;
  }
  function generate(raw) {
    var text = raw.trim(), items = [], seen = {};
    function push(o) { var k = o.kind + (o.zip || o.key || ''); if (!seen[k]) { seen[k] = 1; items.push(o); } }
    if (!text) return items;
    var five = text.match(/\b(\d{5})(?:-\d{4})?\b/);
    var onlyDigits = /^[\d\s-]+$/.test(text);
    if (five) {
      var z = five[1], o = zipOption(z);
      push(o || { kind: 'zipunknown', zip: z, label: z, sub: 'Not on our list yet · request an estimate anyway' });
    } else if (onlyDigits) {
      var d = text.replace(/\D/g, '');
      if (d.length >= 1 && d.length <= 4) {
        var n = 0;
        ZIPS_SORTED.forEach(function (z2) { if (z2.indexOf(d) === 0 && n < 8) { var oo = zipOption(z2); if (oo) { push(oo); n++; } } });
      }
    } else {
      var q = norm(text).replace(/\b(fl|florida|usa)\b/g, '').replace(/\s+/g, ' ').trim();
      if (q) {
        var scored = [];
        CAND.forEach(function (c) {
          var s = 0;
          c.names.forEach(function (nm) { s = Math.max(s, scoreName(q, nm)); });
          if (s > 0) scored.push({ s: s + (c.t === 'area' ? 2 : c.t === 'hood' ? 1 : 0), c: c });
        });
        scored.sort(function (a, b) { return b.s - a.s; });
        scored.slice(0, 6).forEach(function (r) {
          var c = r.c;
          if (c.t === 'area') push({ kind: 'area', key: c.key, area: c.area, label: c.label, sub: 'We serve this area · ZIP ' + c.area.z.slice(0, 3).join(', ') + (c.area.z.length > 3 ? '…' : '') });
          else if (c.t === 'hood') push({ kind: 'hood', key: c.key, area: c.area, label: c.label, sub: 'Part of ' + c.area.n });
          else push({ kind: 'place', key: c.key, place: c.place, label: c.label, sub: 'Not on our list yet' + (c.place.c.length ? ' · closest: ' + nameList(c.place.c.slice(0, 2)) : '') });
        });
      }
    }
    push({ kind: 'ask', key: 'ask', text: text, label: 'Request an estimate for “' + text + '”', sub: 'Kareem confirms whether we can come' });
    return items;
  }

  /* ---------- suggestion list (combobox) ---------- */
  var items = [], active = -1, current = null;
  function setOpen(open) {
    list.hidden = !open; input.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (!open) { active = -1; input.removeAttribute('aria-activedescendant'); }
  }
  function renderList() {
    list.textContent = '';
    items.forEach(function (it, i) {
      var li = document.createElement('li');
      li.id = 'af-opt-' + i; li.setAttribute('role', 'option'); li.setAttribute('aria-selected', i === active ? 'true' : 'false');
      li.className = 'af-opt' + (it.kind === 'ask' ? ' is-ask' : '');
      var b = document.createElement('b'); b.textContent = it.label;
      var s = document.createElement('span'); s.textContent = it.sub;
      li.appendChild(b); li.appendChild(s);
      li.addEventListener('mousedown', function (e) { e.preventDefault(); choose(it); });
      list.appendChild(li);
    });
    setOpen(items.length > 0);
    if (active > -1) input.setAttribute('aria-activedescendant', 'af-opt-' + active);
  }
  function filterChips() {
    var keep = null;
    if (items.length) {
      keep = {};
      items.forEach(function (it) {
        if (it.area) keep[it.area.s] = 1;
        if (it.areas) it.areas.forEach(function (s) { keep[s] = 1; });
        if (it.place) it.place.c.forEach(function (s) { keep[s] = 1; });
      });
      if (!Object.keys(keep).length) keep = null;
    }
    chips.forEach(function (li) {
      var a = li.querySelector('a'), slug = a ? a.getAttribute('href').split('/')[2] : null;
      li.hidden = !!(keep && !(slug && keep[slug]));
    });
  }
  function announce(n) {
    status.textContent = n ? n + ' option' + (n === 1 ? '' : 's') + ' available. Use the arrow keys and Enter.' : '';
  }
  function onType() {
    var v = input.value;
    clearBtn.hidden = !v;
    out.textContent = ''; current = null;   // a new search starts clean; typed name and phone are kept in the draft
    items = generate(v); active = -1;
    renderList(); filterChips(); announce(items.length);
    if (!v.trim()) return;
    var five = v.match(/\b\d{5}\b/);
    if (five && items.length) choose(items[0], true);   // a full ZIP code answers itself
  }

  /* ---------- result card ---------- */
  function el(tag, cls, text) { var n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; }
  var draft = { name: '', phone: '', size: SIZES[0], date: '' };

  function describe(it) {
    var served = false, head, body, links = [], from = it.label;
    switch (it.kind) {
      case 'area':
        served = true; head = 'Yes, we move in ' + it.area.n + '.'; links.push(it.area); from = it.area.n;
        body = 'Your free estimate shows your hourly rate and the time we expect, before you book.'; break;
      case 'hood':
        served = true; head = it.label + ' is part of ' + it.area.n + '. We move there.'; links.push(it.area); from = it.label + ', ' + it.area.n;
        body = 'Your free estimate shows your hourly rate and the time we expect, before you book.'; break;
      case 'zip':
        served = true; links = it.areas.map(function (s) { return BYSLUG[s]; }); from = it.zip;
        head = it.areas.length === 1 ? 'ZIP ' + it.zip + ' is in ' + BYSLUG[it.areas[0]].n + '. We move there.'
          : 'ZIP ' + it.zip + ' covers parts of ' + nameList(it.areas) + '. We move in all of them.';
        body = 'Your free estimate shows your hourly rate and the time we expect, before you book.'; break;
      case 'zipplace':
        head = 'ZIP ' + it.zip + ' is ' + it.place.n + '. We do not list it yet.'; from = it.zip; links = it.place.c.map(function (s) { return BYSLUG[s]; });
        body = (it.place.c.length ? 'The closest areas we serve are ' + nameList(it.place.c.slice(0, 2)) + '. ' : '') + 'Send your details and Kareem will tell you whether we can come.'; break;
      case 'place':
        head = it.place.n + ' is not on our service list yet.'; from = it.place.n; links = it.place.c.map(function (s) { return BYSLUG[s]; });
        body = (it.place.c.length ? 'The closest areas we serve are ' + nameList(it.place.c.slice(0, 2)) + '. ' : '') + 'Send your details and Kareem will tell you whether we can come.'; break;
      case 'zipunknown':
        var p3 = it.zip.slice(0, 3), region = D.r[p3], fl = +it.zip >= 32000 && +it.zip <= 34999;
        from = it.zip; head = 'We do not have ZIP ' + it.zip + ' on our list yet.';
        body = (region ? 'It is in ' + region + '. ' : (fl ? '' : 'That ZIP code is outside Florida, and we are a local Tampa Bay mover. ')) +
          'Send your details and Kareem will tell you whether we can come.'; break;
      default:
        head = 'Let’s find out if we cover “' + it.text + '”.'; from = it.text;
        body = 'We do not have that one on our list yet. Send your details and Kareem will tell you whether we can come.';
    }
    return { served: served, head: head, body: body, links: links.slice(0, 3), from: from, it: it };
  }

  function field(id, label, node) {
    var w = el('div', 'af-f'), l = el('label', '', label); l.setAttribute('for', id); node.id = id;
    w.appendChild(l); w.appendChild(node); return w;
  }
  function buildForm(d) {
    var form = el('form', 'af-form'); form.setAttribute('novalidate', '');
    form.appendChild(el('h3', '', 'Request your free estimate'));
    var grid = el('div', 'af-grid');
    var name = el('input'); name.type = 'text'; name.name = 'name'; name.autocomplete = 'name'; name.value = draft.name;
    var phone = el('input'); phone.type = 'tel'; phone.name = 'phone'; phone.autocomplete = 'tel'; phone.inputMode = 'tel'; phone.value = draft.phone;
    var from = el('input'); from.type = 'text'; from.name = 'from'; from.value = d.from;
    var size = el('select'); size.name = 'size';
    SIZES.forEach(function (s) { var o = el('option', '', s); o.value = s; size.appendChild(o); });
    size.value = draft.size;
    var date = el('input'); date.type = 'date'; date.name = 'date'; date.value = draft.date;
    grid.appendChild(field('af-name', 'Your name', name)); grid.appendChild(field('af-phone', 'Phone', phone));
    grid.appendChild(field('af-from', 'Moving from (city or ZIP)', from)); grid.appendChild(field('af-size', 'Home size', size));
    grid.appendChild(field('af-date', 'Move date (optional)', date));
    form.appendChild(grid);
    var hp = el('input', 'hp'); hp.type = 'text'; hp.name = '_honey'; hp.tabIndex = -1; hp.setAttribute('autocomplete', 'off'); hp.setAttribute('aria-hidden', 'true');
    form.appendChild(hp);
    var btn = el('button', 'btn btn-primary', 'Request my free estimate'); btn.type = 'submit';
    var msg = el('p', 'form-msg'); msg.setAttribute('role', 'status'); msg.setAttribute('aria-live', 'polite'); msg.hidden = true;
    form.appendChild(btn); form.appendChild(msg);
    var busy = false, sent = false;
    function say(kind, text) { msg.hidden = false; msg.className = 'form-msg ' + kind; msg.textContent = text; }
    [name, phone, size, date].forEach(function (n) {
      n.addEventListener('input', function () { draft.name = name.value; draft.phone = phone.value; draft.size = size.value; draft.date = date.value; });
    });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (busy || sent || hp.value) return;
      name.removeAttribute('aria-invalid'); phone.removeAttribute('aria-invalid');
      if (!name.value.trim()) { name.setAttribute('aria-invalid', 'true'); say('is-error', 'Please add your name so we know who to call.'); name.focus(); return; }
      var digits = phone.value.replace(/\D/g, '');
      if (digits.length < 10 || digits.length > 11) { phone.setAttribute('aria-invalid', 'true'); say('is-error', 'Please enter a 10-digit phone number so we can reach you.'); phone.focus(); return; }
      var data = {
        _subject: 'New estimate request: ' + name.value.trim() + ' (Area finder)', _template: 'table', 'Form': 'Area finder',
        'Name': name.value.trim(), 'Phone': phone.value.trim(),
        'Searched for': input.value.trim() || '(nothing)',
        'Result': d.served ? 'On our list: ' + (d.links.length ? d.links.map(function (a) { return a.n; }).join(', ') : d.from) : 'Not on our list yet: Kareem to confirm',
        'Moving from': from.value.trim() || '(not given)', 'Home size': size.value, 'Move date': date.value || '(not given)',
        'Sent from': location.href
      };
      busy = true; btn.disabled = true; btn.textContent = 'Sending...'; say('is-pending', 'Sending your request...');
      var ctrl = window.AbortController ? new AbortController() : null;
      var timer = setTimeout(function () { if (ctrl) ctrl.abort(); }, 15000);
      fetch(ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(data), signal: ctrl ? ctrl.signal : undefined })
        .then(function (r) {
          return r.json().catch(function () { return {}; }).then(function (j) {
            if (!r.ok || String(j.success) !== 'true') { var err = new Error('refused'); err.server = true; throw err; }
          });
        })
        .then(function () {
          sent = true; btn.textContent = 'Request sent';
          [].forEach.call(form.querySelectorAll('input,select'), function (n) { n.readOnly = true; });
          say('is-ok', 'Thanks, ' + name.value.trim().split(/\s+/)[0] + '. Your request is in. Kareem will call you at ' + phone.value.trim() + '. Most estimates are back the same day.');
        })
        .catch(function (err) {
          btn.disabled = false; btn.textContent = 'Request my free estimate';
          say('is-error', err && err.server
            ? 'Online requests are not going through right now. Call or text ' + PHONE + ' and Kareem will get you an estimate.'
            : 'Your request did not send. Check your connection and try again, or call or text ' + PHONE + '.');
        })
        .then(function () { clearTimeout(timer); busy = false; });
    });
    return form;
  }
  function renderResult(it, quiet) {
    var d = describe(it);
    current = it;
    out.textContent = '';
    var card = el('section', 'af-card' + (d.served ? ' is-served' : ' is-open'));
    card.setAttribute('aria-labelledby', 'af-head');
    var head = el('h3', 'af-head', d.head); head.id = 'af-head';
    card.appendChild(head);
    card.appendChild(el('p', 'af-body', d.body));
    if (d.links.length) {
      var ul = el('p', 'af-links');
      d.links.forEach(function (a) {
        var link = el('a', 'btn btn-ghost', 'Movers in ' + a.n); link.href = '/areas/' + a.s + '/'; ul.appendChild(link);
      });
      card.appendChild(ul);
    }
    card.appendChild(buildForm(d));
    var call = el('p', 'af-call');
    call.appendChild(document.createTextNode('Prefer to talk? Call or text '));
    var a = el('a', 'ph', PHONE); a.href = TEL; call.appendChild(a); call.appendChild(document.createTextNode('.'));
    card.appendChild(call);
    out.appendChild(card);
    if (!quiet) { try { head.setAttribute('tabindex', '-1'); head.focus({ preventScroll: false }); } catch (e) { /* focus is a convenience */ } }
  }
  function choose(it, quiet) {
    if (it.kind !== 'ask' && !quiet) input.value = it.kind === 'zip' || it.kind === 'zipplace' || it.kind === 'zipunknown' ? it.zip : it.label;
    clearBtn.hidden = !input.value;
    setOpen(false);
    renderResult(it, quiet);
  }

  /* ---------- events ---------- */
  input.addEventListener('input', onType);
  input.addEventListener('focus', function () { if (input.value.trim() && !items.length) onType(); else if (items.length) setOpen(true); });
  input.addEventListener('blur', function () { setTimeout(function () { setOpen(false); }, 120); });
  input.addEventListener('keydown', function (e) {
    var k = e.key;
    if (k === 'ArrowDown' || k === 'ArrowUp') {
      if (!items.length) return;
      e.preventDefault();
      if (list.hidden) setOpen(true);
      active = (active + (k === 'ArrowDown' ? 1 : -1) + items.length) % items.length;
      [].forEach.call(list.children, function (li, i) { li.setAttribute('aria-selected', i === active ? 'true' : 'false'); });
      input.setAttribute('aria-activedescendant', 'af-opt-' + active);
      var cur = list.children[active]; if (cur && cur.scrollIntoView) cur.scrollIntoView({ block: 'nearest' });
    } else if (k === 'Enter') {
      e.preventDefault();
      if (!items.length) return;
      choose(items[active > -1 ? active : 0]);
    } else if (k === 'Escape') {
      if (!list.hidden) { e.preventDefault(); setOpen(false); }
      else if (input.value) { input.value = ''; onType(); }
    }
  });
  clearBtn.addEventListener('click', function () { input.value = ''; onType(); input.focus(); });
  root.querySelector('[data-af-go]').addEventListener('click', function () { if (input.value.trim()) { items = generate(input.value); if (items.length) choose(items[0]); } else input.focus(); });
  // ?q= or ?zip= from another page or a search result lands with the answer ready
  try {
    var qs = new URLSearchParams(location.search), pre = qs.get('zip') || qs.get('q');
    if (pre) { input.value = pre.slice(0, 60); onType(); if (items.length && !/\b\d{5}\b/.test(pre)) choose(items[0], true); setOpen(false); }
  } catch (e) { /* the finder works without it */ }
})();
