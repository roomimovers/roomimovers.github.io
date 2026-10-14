/* Roomi Movers area and address finder.
   One search box. Type a street address, a ZIP code, a city or a neighborhood.
   - Street addresses: suggestions come from OpenStreetMap data (Photon). Picking one is verified against the U.S. Census Bureau address
     database, which confirms the address and its ZIP and gives its location. The location is compared with our service areas.
   - ZIP codes, names and neighborhoods: answered instantly from the service-area data (assets/areas-data.js).
   Every result carries an estimate request that goes to the company inbox. "We can help" is shown only for a ZIP on our service list;
   anything else is described as "to be confirmed by Kareem", never as served. */
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
  var PHOTON = 'https://photon.komoot.io/api/', CENSUS = 'https://geocoding.geo.census.gov/geocoder/locations/onelineaddress';
  var BBOX = '-83.2,27.3,-81.8,28.7';            // Tampa Bay region: suggestions stay local
  var FAR_MILES = 60;

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
  function miles(a, b) {
    var R = 3958.8, r = Math.PI / 180, dLa = (b[0] - a[0]) * r, dLo = (b[1] - a[1]) * r;
    var h = Math.sin(dLa / 2) * Math.sin(dLa / 2) + Math.cos(a[0] * r) * Math.cos(b[0] * r) * Math.sin(dLo / 2) * Math.sin(dLo / 2);
    return 2 * R * Math.asin(Math.sqrt(h));
  }
  function nearest(lat, lon) {
    var best = null;
    D.a.forEach(function (a) {
      if (!a.c) return;
      var m = miles([lat, lon], a.c);
      if (!best || m < best.m) best = { area: a, m: m };
    });
    return best;
  }
  function pretty(s) {   // "9306 DEER CREEK DR, TAMPA, FL, 33647" -> "9306 Deer Creek Dr, Tampa, FL 33647"
    var parts = String(s).split(',').map(function (x) { return x.trim(); });
    var fixed = parts.map(function (p, i) {
      if (/^[A-Za-z]{2}$/.test(p) && i > 0) return p.toUpperCase();
      return p.toLowerCase().replace(/\b([a-z])([a-z']*)/g, function (m, a, b) {
        if (/^(ne|nw|se|sw)$/i.test(m)) return m.toUpperCase();
        return a.toUpperCase() + b;
      }).replace(/\b(\d+)(St|Nd|Rd|Th)\b/g, function (m, n, suf) { return n + suf.toLowerCase(); });
    });
    var last = fixed.length - 1;
    if (last >= 2 && /^\d{5}/.test(fixed[last]) && /^[A-Z]{2}$/.test(fixed[last - 1])) {
      fixed.splice(last - 1, 2, fixed[last - 1] + ' ' + fixed[last]);
    }
    return fixed.join(', ');
  }
  function looksLikeAddress(t) { return /^\s*\d{1,6}[A-Za-z]?\s+\S*[A-Za-z]/.test(t); }

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
    if (looksLikeAddress(text)) {
      /* address typing: suggestions arrive asynchronously, nothing local to add */
    } else if (five) {
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
    return items;
  }
  function askOption(text) {
    return { kind: 'ask', key: 'ask', text: text, label: 'Request an estimate for “' + text + '”', sub: 'Kareem confirms whether we can come' };
  }

  /* ---------- address suggestions (OpenStreetMap data through Photon) ---------- */
  var addrSeq = 0, addrTimer = null, addrCtrl = null, addrCache = {}, addrState = 'idle', addrItems = [];
  function typedNumber(t) { var m = t.match(/^\s*(\d{1,6}[A-Za-z]?)\b/); return m ? m[1] : ''; }
  function fromFeature(f, typed) {
    var p = f.properties || {}, c = f.geometry && f.geometry.coordinates;
    if (!c || p.state && p.state !== 'Florida') return null;
    var street = p.street || (p.type === 'street' || p.osm_key === 'highway' ? p.name : '');
    if (!street) return null;
    var city = p.city || p.locality || p.district || p.county || '';
    var number = p.housenumber || typed, streetOnly = !p.housenumber;
    if (!number) return null;
    var line1 = number + ' ' + street, zip = p.postcode ? String(p.postcode).slice(0, 5) : '';
    var cityBit = city ? city + ', FL' : 'FL', full = line1 + ', ' + cityBit + (zip ? ' ' + zip : '');
    return { kind: 'addr', key: full.toLowerCase(), label: line1, sub: cityBit + (zip ? ' ' + zip : '') + (streetOnly ? ' · we will check your number' : ''),
             full: full, zip: zip, lat: c[1], lon: c[0], streetOnly: streetOnly };
  }
  function fetchAddresses(q) {
    var mySeq = ++addrSeq;
    if (addrCache[q]) { addrItems = addrCache[q]; addrState = 'done'; refreshList(); return; }
    if (addrCtrl) { try { addrCtrl.abort(); } catch (e) { /* already finished */ } }
    addrCtrl = window.AbortController ? new AbortController() : null;
    addrState = 'loading'; refreshList();
    var url = PHOTON + '?q=' + encodeURIComponent(q) + '&lat=28.0&lon=-82.45&location_bias_scale=0.3&limit=8&lang=en&bbox=' + BBOX;
    var typed = typedNumber(q);
    fetch(url, { signal: addrCtrl ? addrCtrl.signal : undefined }).then(function (r) {
      if (!r.ok) throw new Error('http'); return r.json();
    }).then(function (j) {
      if (mySeq !== addrSeq) return;
      var seen = {}, res = [];
      (j.features || []).forEach(function (f) {
        var o = fromFeature(f, typed);
        if (o && !seen[o.key]) { seen[o.key] = 1; res.push(o); }
      });
      addrCache[q] = res; addrItems = res.slice(0, 6); addrState = 'done'; refreshList();
    }).catch(function (e) {
      if (mySeq !== addrSeq || (e && e.name === 'AbortError')) return;
      addrItems = []; addrState = 'error'; refreshList();
    });
  }

  /* ---------- verification (U.S. Census Bureau geocoder, script-tag mode) ---------- */
  var geoN = 0;
  function census(address, cb) {
    var name = '__roomiGeo' + (++geoN), s = document.createElement('script'), done = false, timer;
    function finish(r) {
      if (done) return; done = true; clearTimeout(timer);
      try { delete window[name]; } catch (e) { window[name] = undefined; }
      if (s.parentNode) s.parentNode.removeChild(s);
      cb(r);
    }
    window[name] = function (r) { finish(r); };
    s.onerror = function () { finish(null); };
    timer = setTimeout(function () { finish(null); }, 9000);
    s.src = CENSUS + '?address=' + encodeURIComponent(address) + '&benchmark=Public_AR_Current&format=jsonp&callback=' + name;
    document.head.appendChild(s);
  }
  function matchesOf(r) { return r && r.result && r.result.addressMatches ? r.result.addressMatches : []; }
  function fromMatch(m) {
    var c = m.coordinates || {}, comp = m.addressComponents || {};
    return { source: 'census', matched: pretty(m.matchedAddress), zip: comp.zip ? String(comp.zip).slice(0, 5) : '', lat: c.y, lon: c.x };
  }

  /* ---------- suggestion list (combobox) ---------- */
  var items = [], active = -1, current = null, token = 0;
  function setOpen(open) {
    list.hidden = !open; input.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (!open) { active = -1; input.removeAttribute('aria-activedescendant'); }
  }
  function rowFor(it, i) {
    var li = document.createElement('li');
    li.id = 'af-opt-' + i; li.setAttribute('role', 'option'); li.setAttribute('aria-selected', i === active ? 'true' : 'false');
    li.className = 'af-opt' + (it.kind === 'ask' ? ' is-ask' : '') + (it.kind === 'addr' ? ' is-addr' : '');
    var b = document.createElement('b'); b.textContent = it.label;
    var s = document.createElement('span'); s.textContent = it.sub;
    li.appendChild(b); li.appendChild(s);
    li.addEventListener('mousedown', function (e) { e.preventDefault(); choose(it); });
    return li;
  }
  function renderList() {
    list.textContent = '';
    items.forEach(function (it, i) { list.appendChild(rowFor(it, i)); });
    if (addrState === 'loading' || addrState === 'error' || (addrState === 'done' && !addrItems.length && looksLikeAddress(input.value))) {
      var note = document.createElement('li');
      note.className = 'af-note'; note.setAttribute('role', 'presentation');
      note.textContent = addrState === 'loading' ? 'Searching addresses…'
        : addrState === 'error' ? 'Address search is unavailable right now. You can still request an estimate below.'
          : 'No matching address yet. Add the street name, or keep typing.';
      list.insertBefore(note, list.firstChild);
    }
    setOpen(list.children.length > 0);
    if (active > -1) input.setAttribute('aria-activedescendant', 'af-opt-' + active);
  }
  function composeItems() {
    var v = input.value, t = v.trim();
    var local = generate(v);
    items = looksLikeAddress(t) ? addrItems.concat(local) : local;
    if (t) items.push(askOption(t));
  }
  function refreshList() {
    composeItems(); active = -1; renderList(); filterChips(); announce(items.length);
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
    var v = input.value, t = v.trim();
    clearBtn.hidden = !v;
    token++; out.textContent = ''; current = null;   // a new search starts clean; typed name and phone stay in the draft
    clearTimeout(addrTimer);
    if (looksLikeAddress(t) && t.length >= 4) {
      addrItems = []; addrState = 'loading';
      addrTimer = setTimeout(function () { fetchAddresses(t); }, 320);
    } else {
      addrSeq++; addrItems = []; addrState = 'idle';
    }
    refreshList();
    if (!t) return;
    var five = t.match(/\b\d{5}\b/);
    if (five && !looksLikeAddress(t) && items.length) choose(items[0], true);   // a full ZIP code answers itself
  }

  /* ---------- result card ---------- */
  function el(tag, cls, text) { var n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; }
  var draft = { name: '', phone: '', size: SIZES[0], date: '', to: '' };
  var ONLIST = 'Your free estimate shows your hourly rate and the time we expect, before you book.';

  function describe(it) {
    var served = false, head, body, links = [], from = it.label, extra = {};
    switch (it.kind) {
      case 'area':
        served = true; head = 'Yes, we move in ' + it.area.n + '.'; links.push(it.area); from = it.area.n; body = ONLIST; break;
      case 'hood':
        served = true; head = it.label + ' is part of ' + it.area.n + '. We move there.'; links.push(it.area); from = it.label + ', ' + it.area.n; body = ONLIST; break;
      case 'zip':
        served = true; links = it.areas.map(function (s) { return BYSLUG[s]; }); from = it.zip;
        head = it.areas.length === 1 ? 'ZIP ' + it.zip + ' is in ' + BYSLUG[it.areas[0]].n + '. We move there.'
          : 'ZIP ' + it.zip + ' covers parts of ' + nameList(it.areas) + '. We move in all of them.';
        body = ONLIST; break;
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
      case 'address':
        return describeAddress(it);
      default:
        head = 'Let’s find out if we cover “' + it.text + '”.'; from = it.text;
        body = 'We do not have that one on our list yet. Send your details and Kareem will tell you whether we can come.';
    }
    return { served: served, head: head, body: body, links: links.slice(0, 3), from: from, it: it, extra: extra };
  }
  function describeAddress(v) {
    var z = v.zip && ZIP[v.zip], areas = z && z.areas.length ? z.areas : null;
    var near = (v.lat != null && v.lon != null) ? nearest(+v.lat, +v.lon) : null;
    var verified = v.source === 'census';
    var line = verified ? 'Verified address: ' + v.matched : 'Address from map data: ' + v.matched + ' (Kareem will confirm the exact address)';
    var extra = { 'Verified address': v.matched, 'Address check': verified ? 'Verified by U.S. Census address data' : 'Found on map data, not verified', 'ZIP': v.zip || '(unknown)' };
    var d = { it: v, from: v.matched, line: line, extra: extra, verified: verified };
    if (areas) {
      d.served = true; d.state = 'ok'; d.links = areas.map(function (s) { return BYSLUG[s]; }).slice(0, 3);
      d.badge = 'We can help';
      d.head = areas.length === 1 ? 'Your address is in ' + BYSLUG[areas[0]].n + '.' : 'Your address is in ZIP ' + v.zip + ', covering ' + nameList(areas) + '.';
      d.body = ONLIST;
      extra['Coverage'] = 'On our list: ' + nameList(areas);
    } else {
      d.served = false; d.state = 'check'; d.badge = 'Let’s confirm';
      var tail = 'Send your details and Kareem will tell you whether we can come.';
      if (near && near.m > FAR_MILES) {
        d.head = 'That address is outside our usual Tampa Bay area.';
        d.body = 'It is about ' + Math.round(near.m) + ' miles from the nearest area we serve (' + near.area.n + '). ' + tail;
        d.links = [];
        extra['Coverage'] = 'Outside area: about ' + Math.round(near.m) + ' mi from ' + near.area.n + ': Kareem to confirm';
      } else if (near) {
        d.head = (v.zip ? 'ZIP ' + v.zip : 'That address') + ' is not on our service list yet.';
        d.body = 'The closest area we serve is ' + near.area.n + ', about ' + Math.max(1, Math.round(near.m)) + ' mile' + (Math.round(near.m) === 1 ? '' : 's') + ' away. ' + tail;
        d.links = [near.area];
        extra['Coverage'] = 'Not on our list yet: about ' + Math.max(1, Math.round(near.m)) + ' mi from ' + near.area.n + ': Kareem to confirm';
      } else {
        d.head = 'We could not place that address on our map.';
        d.body = tail; d.links = [];
        extra['Coverage'] = 'Unknown: Kareem to confirm';
      }
    }
    return d;
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
    var to = el('input'); to.type = 'text'; to.name = 'to'; to.value = draft.to; to.placeholder = 'City, ZIP or address';
    var size = el('select'); size.name = 'size';
    SIZES.forEach(function (s) { var o = el('option', '', s); o.value = s; size.appendChild(o); });
    size.value = draft.size;
    var date = el('input'); date.type = 'date'; date.name = 'date'; date.value = draft.date;
    grid.appendChild(field('af-name', 'Your name', name)); grid.appendChild(field('af-phone', 'Phone', phone));
    grid.appendChild(field('af-from', 'Moving from', from)); grid.appendChild(field('af-to', 'Moving to (optional)', to));
    grid.appendChild(field('af-size', 'Home size', size)); grid.appendChild(field('af-date', 'Move date (optional)', date));
    form.appendChild(grid);
    var hp = el('input', 'hp'); hp.type = 'text'; hp.name = '_honey'; hp.tabIndex = -1; hp.setAttribute('autocomplete', 'off'); hp.setAttribute('aria-hidden', 'true');
    form.appendChild(hp);
    var btn = el('button', 'btn btn-primary', 'Request my free estimate'); btn.type = 'submit';
    var msg = el('p', 'form-msg'); msg.setAttribute('role', 'status'); msg.setAttribute('aria-live', 'polite'); msg.hidden = true;
    form.appendChild(btn); form.appendChild(msg);
    var busy = false, sent = false;
    function say(kind, text) { msg.hidden = false; msg.className = 'form-msg ' + kind; msg.textContent = text; }
    [name, phone, size, date, to].forEach(function (n) {
      n.addEventListener('input', function () { draft.name = name.value; draft.phone = phone.value; draft.size = size.value; draft.date = date.value; draft.to = to.value; });
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
        'Moving from': from.value.trim() || '(not given)', 'Moving to': to.value.trim() || '(not given)',
        'Home size': size.value, 'Move date': date.value || '(not given)'
      };
      var ex = d.extra || {};
      Object.keys(ex).forEach(function (k) { data[k] = ex[k]; });
      data['Sent from'] = location.href;
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
  function renderResult(d, quiet) {
    current = d.it;
    out.textContent = '';
    var cls = 'af-card' + (d.state === 'ok' ? ' is-ok' : d.state === 'check' ? ' is-check' : d.served ? ' is-served' : ' is-open');
    var card = el('section', cls);
    card.setAttribute('aria-labelledby', 'af-head');
    if (d.badge) {
      var badge = el('p', 'af-badge ' + (d.state === 'ok' ? 'is-ok' : 'is-check'));
      var ico = el('span', 'af-badge-ico', d.state === 'ok' ? '✓' : '?'); ico.setAttribute('aria-hidden', 'true');
      badge.appendChild(ico); badge.appendChild(document.createTextNode(d.badge));
      card.appendChild(badge);
    }
    var head = el('h3', 'af-head', d.head); head.id = 'af-head';
    card.appendChild(head);
    if (d.line) card.appendChild(el('p', 'af-line' + (d.verified ? ' is-verified' : ''), d.line));
    card.appendChild(el('p', 'af-body', d.body));
    if (d.links && d.links.length) {
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
  function renderChecking(text) {
    out.textContent = '';
    var card = el('section', 'af-card is-open');
    var p = el('p', 'af-head', text); p.setAttribute('role', 'status');
    card.appendChild(p); out.appendChild(card);
  }

  /* ---------- picking an option ---------- */
  function verifyAddress(it) {
    var my = ++token;
    renderChecking('Checking that address…');
    census(it.full, function (r) {
      if (my !== token) return;
      var ms = matchesOf(r);
      if (ms.length) { renderResult(describe(Object.assign({ kind: 'address' }, fromMatch(ms[0]))), false); return; }
      if (!it.streetOnly) {   // a house number from the map data: use it, but say it is not verified
        renderResult(describe({ kind: 'address', source: 'map', matched: it.full, zip: it.zip, lat: it.lat, lon: it.lon }), false); return;
      }
      renderResult({ served: false, state: 'check', badge: 'Let’s confirm', head: 'We could not verify that house number.',
        body: 'Check the number and street, or send your details and Kareem will confirm the address.', links: [], from: it.full, it: it,
        extra: { 'Address check': 'Not verified', 'Coverage': 'Unknown: Kareem to confirm' } }, false);
    });
  }
  function verifyRaw(text) {   // typed address, no suggestion picked: ask the Census directly
    var my = ++token;
    renderChecking('Checking that address…');
    census(text, function (r) {
      if (my !== token) return;
      var ms = matchesOf(r);
      if (ms.length === 1) { renderResult(describe(Object.assign({ kind: 'address' }, fromMatch(ms[0]))), false); return; }
      if (ms.length > 1) {
        out.textContent = '';
        addrItems = ms.slice(0, 5).map(function (m) {
          var v = fromMatch(m);
          return { kind: 'addr', key: v.matched, label: v.matched.split(',')[0], sub: v.matched.split(',').slice(1).join(',').trim(), full: v.matched, zip: v.zip, lat: v.lat, lon: v.lon, streetOnly: false };
        });
        addrState = 'done'; refreshList(); input.focus();
        return;
      }
      renderResult({ served: false, state: 'check', badge: 'Let’s confirm', head: 'We could not find that address.',
        body: 'Check the spelling, or add the city and ZIP. You can still send your details and Kareem will confirm.', links: [], from: text, it: { kind: 'ask', text: text },
        extra: { 'Address check': 'Not verified', 'Coverage': 'Unknown: Kareem to confirm' } }, false);
    });
  }
  function choose(it, quiet) {
    setOpen(false);
    if (it.kind === 'addr') {
      input.value = it.full; clearBtn.hidden = false;
      addrState = 'idle'; addrItems = [];
      verifyAddress(it);
      return;
    }
    if (it.kind !== 'ask' && !quiet) input.value = it.kind === 'zip' || it.kind === 'zipplace' || it.kind === 'zipunknown' ? it.zip : it.label;
    clearBtn.hidden = !input.value;
    token++;
    renderResult(describe(it), quiet);
  }
  function go() {
    var t = input.value.trim();
    if (!t) { input.focus(); return; }
    if (looksLikeAddress(t) && !addrItems.length) { setOpen(false); verifyRaw(t); return; }
    composeItems();
    if (items.length) choose(items[0]);
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
      [].forEach.call(list.querySelectorAll('[role=option]'), function (li, i) { li.setAttribute('aria-selected', i === active ? 'true' : 'false'); });
      input.setAttribute('aria-activedescendant', 'af-opt-' + active);
      var cur = document.getElementById('af-opt-' + active); if (cur && cur.scrollIntoView) cur.scrollIntoView({ block: 'nearest' });
    } else if (k === 'Enter') {
      e.preventDefault();
      if (active > -1 && items[active]) { choose(items[active]); return; }
      go();
    } else if (k === 'Escape') {
      if (!list.hidden) { e.preventDefault(); setOpen(false); }
      else if (input.value) { input.value = ''; onType(); }
    }
  });
  clearBtn.addEventListener('click', function () { input.value = ''; onType(); input.focus(); });
  root.querySelector('[data-af-go]').addEventListener('click', go);
  // ?q= or ?zip= from another page or a search result lands with the answer ready
  try {
    var qs = new URLSearchParams(location.search), pre = qs.get('zip') || qs.get('q');
    if (pre) { input.value = pre.slice(0, 80); onType(); if (items.length && !looksLikeAddress(pre) && !/\b\d{5}\b/.test(pre)) choose(items[0], true); setOpen(false); }
  } catch (e) { /* the finder works without it */ }
})();
