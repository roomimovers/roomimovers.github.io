/* Roomi Movers chat assistant.
   - Answers common questions from confirmed business facts (assets/facts.js, generated from _tools/business.json).
   - Takes an estimate request one question at a time and posts it to FormSubmit, which emails Roomi Movers.
     "Sent" is only shown after the form service confirms it accepted the request.
   - Optional AI mode: when facts.aiEndpoint is set, questions the fact sheet cannot answer go to the secure relay in _tools/ai-relay.
   Everything the widget says about licensing, prices and policies comes from the same data as the rest of the site. */
(function () {
  'use strict';
  var F = window.ROOMI_FACTS;
  if (!F || F.chatEnabled === false || document.getElementById('rc-root')) return;

  var KEY = 'roomi-chat-v1';
  var PHONE = F.phone, TEL = 'tel:' + F.tel, AI = F.aiEndpoint || '';
  var reduce = !!(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches);
  var mobileMQ = window.matchMedia ? matchMedia('(max-width:560px)') : { matches: false };
  var ORDER = ['name', 'phone', 'date', 'size', 'from', 'to', 'notes'];
  var LABEL = { name: 'Name', phone: 'Phone', date: 'Move date', size: 'Home size', from: 'Moving from', to: 'Moving to', notes: 'Notes' };
  var BASE = ['Get a free estimate', 'How much does it cost?', 'Areas you serve', 'Are you licensed?'];
  var CANCEL = /^(cancel|cancel request|stop|never ?mind|nevermind|start over|quit|exit|no thanks|forget it)\b/i;

  /* ---------- state ---------- */
  var S = { msgs: [], step: 'idle', lead: {}, open: false, ai: 0, asked: [], editing: null, sending: false };
  try {
    var saved = JSON.parse(sessionStorage.getItem(KEY) || 'null');
    if (saved && Array.isArray(saved.msgs)) {
      S.msgs = saved.msgs; S.step = saved.step === 'sending' ? 'confirm' : (saved.step || 'idle'); S.lead = saved.lead || {};
      S.open = !!saved.open; S.ai = saved.ai || 0; S.asked = saved.asked || []; S.editing = saved.editing || null;
    }
  } catch (e) { /* private mode: the chat still works, it just does not survive a page change */ }
  function save() {
    try { sessionStorage.setItem(KEY, JSON.stringify({ msgs: S.msgs.slice(-60), step: S.step, lead: S.lead, open: S.open, ai: S.ai, asked: S.asked, editing: S.editing })); } catch (e) {}
    if (!panel.hidden) syncInput();
  }

  /* ---------- small helpers ---------- */
  function el(tag, cls, text) { var n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; }
  function norm(s) { return ' ' + String(s).toLowerCase().replace(/[’']/g, '').replace(/[^a-z0-9$ ]+/g, ' ').replace(/\s+/g, ' ').trim() + ' '; }
  function words(s) { return norm(s).trim().split(' ').filter(Boolean); }
  function first(name) { return String(name || '').trim().split(/\s+/)[0] || 'there'; }
  function digits10(s) { var d = String(s).replace(/\D/g, ''); if (d.length === 11 && d.charAt(0) === '1') d = d.slice(1); return d.length === 10 ? d : ''; }
  function fmtPhone(d) { return '(' + d.slice(0, 3) + ') ' + d.slice(3, 6) + '-' + d.slice(6); }
  function faqA(sub) {
    for (var i = 0; i < F.faq.length; i++) if (F.faq[i][0].toLowerCase().indexOf(sub) > -1) return F.faq[i][1];
    return '';
  }
  var SVG = {
    chat: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 11.5a8.4 8.4 0 0 1-9 8.4 9 9 0 0 1-3.4-.7L3 21l1.9-5.1A8.4 8.4 0 0 1 3 11.5 8.5 8.5 0 0 1 12 3a8.5 8.5 0 0 1 9 8.5z"/></svg>',
    phone: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg>',
    close: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>',
    send: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
  };

  /* ---------- styles ---------- */
  var css = [
    '.rc-root,.rc-root *{box-sizing:border-box}',
    '.rc-root{--rc-bot:#F7EEE2;--rc-you:#12306B;--rc-chip:#fff;--rc-edge:#12306B}',
    '@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) .rc-root{--rc-bot:#12305F;--rc-you:#1B3F85;--rc-chip:#0A1F45;--rc-edge:#9DB4EA}}',
    ':root[data-theme="dark"] .rc-root{--rc-bot:#12305F;--rc-you:#1B3F85;--rc-chip:#0A1F45;--rc-edge:#9DB4EA}',
    '.rc-sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}',
    '.rc-launch{position:fixed;right:16px;bottom:16px;z-index:40;display:inline-flex;align-items:center;gap:10px;min-height:56px;padding:0 22px 0 16px;border:0;border-radius:999px;background:#F7652F;color:#1A0E0A;font:800 17px/1 var(--display,"Archivo","Helvetica Neue",Arial,sans-serif);cursor:pointer;box-shadow:0 14px 30px -10px rgba(6,26,60,.6),0 2px 6px rgba(6,26,60,.25)}',
    '.rc-launch:hover{filter:brightness(1.06)}',
    '.rc-launch[hidden],.rc-panel[hidden]{display:none!important}',
    '.rc-t-short{display:none}',
    '@media (max-height:540px) and (orientation:landscape){.rc-launch{bottom:calc(10px + env(safe-area-inset-bottom,0px));min-height:44px;padding:0 14px 0 12px;font-size:16px}}',
    '@media (max-width:860px){.rc-launch{right:12px;bottom:calc(82px + env(safe-area-inset-bottom,0px));min-height:52px;padding:0 18px 0 14px}.rc-t-long{display:none}.rc-t-short{display:inline}}',
    '.rc-panel{position:fixed;right:20px;bottom:20px;z-index:60;width:min(396px,calc(100vw - 24px));height:min(640px,calc(100vh - 40px));height:min(640px,calc(100dvh - 40px));display:flex;flex-direction:column;background:var(--bg,#fff);color:var(--ink,#0B1C3D);border:1px solid var(--line,#E4D6C2);border-radius:20px;box-shadow:0 30px 70px -20px rgba(6,26,60,.6);overflow:hidden;font-family:var(--body,"Figtree","Segoe UI",system-ui,sans-serif);font-size:17px;line-height:1.5}',
    '@media (max-width:560px){.rc-panel{left:0;right:0;bottom:auto;top:var(--rc-top,0px);width:auto;height:var(--rc-h,100vh);height:var(--rc-h,100dvh);border-radius:0;border:0}html.rc-lock,html.rc-lock body{overflow:hidden}}',
    '@media (max-height:520px) and (min-width:561px){.rc-panel{top:8px;bottom:8px;height:auto}}',
    '.rc-head{flex:none;display:flex;align-items:center;gap:12px;padding:12px 12px 12px 16px;padding-top:max(12px,env(safe-area-inset-top,0px));background:#061A3C;color:#fff}',
    '.rc-head img{width:42px;height:42px;border-radius:12px;background:#fff;object-fit:contain;padding:4px;flex:none}',
    '.rc-ht{flex:1;min-width:0}',
    '.rc-title{font:900 19px/1.1 var(--display,"Archivo","Helvetica Neue",Arial,sans-serif)}',
    '.rc-sub{margin:3px 0 0;font-size:15px;line-height:1.25;color:#CBD3E3}',
    '.rc-ico{flex:none;width:46px;height:46px;display:inline-flex;align-items:center;justify-content:center;border:0;border-radius:13px;background:rgba(255,255,255,.14);color:#fff;cursor:pointer;text-decoration:none}',
    '.rc-ico:hover{background:rgba(255,255,255,.24)}',
    '.rc-log{flex:1;min-height:0;overflow-y:auto;overscroll-behavior:contain;-webkit-overflow-scrolling:touch;padding:16px 14px 8px;display:flex;flex-direction:column;gap:12px;background:var(--bg,#fff)}',
    '.rc-m{position:relative;max-width:90%;padding:12px 15px;border-radius:18px;overflow-wrap:anywhere}',
    '.rc-m.bot{align-self:flex-start;background:var(--rc-bot);color:var(--ink,#0B1C3D);border-bottom-left-radius:6px}',
    '.rc-m.you{align-self:flex-end;background:var(--rc-you);color:#fff;border-bottom-right-radius:6px}',
    '.rc-m p{margin:0}.rc-m p+p{margin-top:8px}',
    '.rc-m a{color:inherit;font-weight:700;text-underline-offset:3px}',
    '.rc-card{display:grid;grid-template-columns:auto 1fr;gap:6px 12px;margin:10px 0 0;font-size:16px}',
    '.rc-card dt{font-weight:800;color:var(--muted,#3B4663)}',
    '.rc-card dd{margin:0;font-weight:600;overflow-wrap:anywhere}',
    '.rc-m .rc-note{margin-top:10px;font-size:16px;color:var(--muted,#3B4663)}',
    '.rc-chips{display:flex;flex-wrap:wrap;gap:8px;padding:2px 0 4px}',
    '.rc-chip{min-height:46px;padding:8px 16px;border-radius:999px;border:2px solid var(--rc-edge);background:var(--rc-chip);color:var(--ink,#0B1C3D);font:700 16px/1.2 var(--body,"Figtree","Segoe UI",system-ui,sans-serif);cursor:pointer}',
    '.rc-chip:hover{background:var(--rc-bot)}',
    '.rc-chip.main{background:#F7652F;border-color:#F7652F;color:#1A0E0A}',
    '.rc-chip.main:hover{filter:brightness(1.06);background:#F7652F}',
    '.rc-typing{display:inline-flex;gap:5px;align-items:center;min-height:26px}',
    '.rc-typing i{width:8px;height:8px;border-radius:50%;background:currentColor;opacity:.5;animation:rc-b 1s infinite ease-in-out}',
    '.rc-typing i:nth-child(2){animation-delay:.15s}.rc-typing i:nth-child(3){animation-delay:.3s}',
    '@keyframes rc-b{0%,80%,100%{transform:translateY(0);opacity:.35}40%{transform:translateY(-4px);opacity:.95}}',
    '.rc-form{flex:none;display:flex;gap:8px;padding:10px 12px calc(10px + env(safe-area-inset-bottom,0px));border-top:1px solid var(--line,#E4D6C2);background:var(--bg,#fff)}',
    '.rc-in{flex:1;min-width:0;min-height:52px;padding:0 15px;border:2px solid #7C869C;border-radius:14px;font:500 17px var(--body,"Figtree","Segoe UI",system-ui,sans-serif);background:var(--field,#fff);color:var(--ink,#0B1C3D)}',
    '.rc-in:focus{border-color:var(--blue,#12306B);box-shadow:0 0 0 4px rgba(18,48,107,.2);outline:0}',
    '.rc-in:disabled{opacity:.6}',
    '.rc-send{flex:none;width:52px;height:52px;display:inline-flex;align-items:center;justify-content:center;border:0;border-radius:14px;background:#F7652F;color:#1A0E0A;cursor:pointer}',
    '.rc-send:disabled{opacity:.55;cursor:default}',
    '.rc-root :focus-visible{outline:3px solid #F7652F;outline-offset:2px}',
    '.rc-launch:focus-visible,.rc-send:focus-visible,.rc-chip.main:focus-visible{outline:3px solid #fff;outline-offset:0;box-shadow:0 0 0 6px #061A3C}',
    '@media (prefers-reduced-motion: reduce){.rc-typing i{animation:none}}',
    '@media print{.rc-root{display:none!important}}'
  ].join('\n');
  var style = el('style'); style.textContent = css; document.head.appendChild(style);

  /* ---------- DOM ---------- */
  var root = el('div', 'rc-root'); root.id = 'rc-root';
  var launch = el('button', 'rc-launch'); launch.type = 'button'; launch.id = 'rc-launch';
  launch.setAttribute('aria-haspopup', 'dialog'); launch.setAttribute('aria-expanded', 'false'); launch.setAttribute('aria-controls', 'rc-panel');
  launch.setAttribute('aria-label', 'Chat with the Roomi Movers assistant');
  launch.innerHTML = SVG.chat + '<span class="rc-t-long">Chat with us</span><span class="rc-t-short">Chat</span>';

  var panel = el('section', 'rc-panel'); panel.id = 'rc-panel'; panel.hidden = true;
  panel.setAttribute('role', 'dialog'); panel.setAttribute('aria-modal', 'false'); panel.setAttribute('aria-labelledby', 'rc-title');
  var head = el('div', 'rc-head');
  var logo = el('img'); logo.src = '/images/logo-mark-120.png'; logo.width = 42; logo.height = 42; logo.alt = ''; logo.decoding = 'async';
  var ht = el('div', 'rc-ht');
  var title = el('div', 'rc-title', 'Roomi Movers'); title.id = 'rc-title';
  ht.appendChild(title); ht.appendChild(el('p', 'rc-sub', 'Automated assistant. Replies right away.'));
  var callA = el('a', 'rc-ico'); callA.href = TEL; callA.setAttribute('aria-label', 'Call Roomi Movers at ' + PHONE); callA.innerHTML = SVG.phone;
  var closeB = el('button', 'rc-ico'); closeB.type = 'button'; closeB.setAttribute('aria-label', 'Close chat'); closeB.innerHTML = SVG.close;
  head.appendChild(logo); head.appendChild(ht); head.appendChild(callA); head.appendChild(closeB);

  var log = el('div', 'rc-log'); log.id = 'rc-log'; log.setAttribute('role', 'log'); log.setAttribute('aria-live', 'polite'); log.setAttribute('aria-label', 'Conversation with the Roomi Movers assistant'); log.tabIndex = 0;
  var form = el('form', 'rc-form'); form.setAttribute('novalidate', ''); form.setAttribute('autocomplete', 'off');
  var lab = el('label', 'rc-sr', 'Your message'); lab.setAttribute('for', 'rc-in');
  var input = el('input', 'rc-in'); input.id = 'rc-in'; input.type = 'text'; input.maxLength = 500; input.setAttribute('enterkeyhint', 'send'); input.setAttribute('autocapitalize', 'sentences');
  var sendB = el('button', 'rc-send'); sendB.type = 'submit'; sendB.setAttribute('aria-label', 'Send message'); sendB.innerHTML = SVG.send;
  form.appendChild(lab); form.appendChild(input); form.appendChild(sendB);
  panel.appendChild(head); panel.appendChild(log); panel.appendChild(form);
  root.appendChild(launch); root.appendChild(panel); document.body.appendChild(root);

  /* ---------- rendering ---------- */
  var chipsEl = null, typingEl = null;
  function rich(parent, text, untrusted) {
    var re = /\[([^\]]{1,80})\]\(([^)\s]{1,200})\)|\(813\) 436-3216/g, last = 0, m;
    while ((m = re.exec(text))) {
      if (m.index > last) parent.appendChild(document.createTextNode(text.slice(last, m.index)));
      if (m[1]) {
        var href = m[2];
        var ok = /^\/[A-Za-z0-9\-_\/#?=.&]*$/.test(href) || /^(tel|sms):\+?\d+$/.test(href) || (!untrusted && /^https:\/\/www\.fdacs\.gov\//.test(href));
        if (ok) {
          var a = el('a', '', m[1]); a.href = href;
          if (/^https?:/.test(href)) { a.target = '_blank'; a.rel = 'noopener noreferrer'; }
          parent.appendChild(a);
        } else parent.appendChild(document.createTextNode(m[1]));
      } else { var p = el('a', '', PHONE); p.href = TEL; parent.appendChild(p); }
      last = re.lastIndex;
    }
    if (last < text.length) parent.appendChild(document.createTextNode(text.slice(last)));
  }
  function clearChips() { if (chipsEl && chipsEl.parentNode) chipsEl.parentNode.removeChild(chipsEl); chipsEl = null; }
  function toBottom() { setTimeout(function () { log.scrollTop = log.scrollHeight; }, 0); }
  function renderChips(list, mainFirst) {
    clearChips();
    if (!list || !list.length) return;
    chipsEl = el('div', 'rc-chips');
    list.forEach(function (label, i) {
      var b = el('button', 'rc-chip' + (mainFirst && i === 0 ? ' main' : ''), label); b.type = 'button';
      b.addEventListener('click', function () { chip(label); });
      chipsEl.appendChild(b);
    });
    log.appendChild(chipsEl);
  }
  function renderMsg(m, withChips) {
    var d = el('div', 'rc-m ' + (m.r === 'you' ? 'you' : 'bot'));
    d.appendChild(el('span', 'rc-sr', m.r === 'you' ? 'You: ' : 'Assistant: '));
    String(m.t || '').split('\n').forEach(function (line) {
      if (!line) return;
      var p = el('p'); rich(p, line, !!m.ai); d.appendChild(p);
    });
    if (m.card) {
      var dl = el('dl', 'rc-card');
      m.card.forEach(function (kv) { dl.appendChild(el('dt', '', kv[0])); dl.appendChild(el('dd', '', kv[1])); });
      d.appendChild(dl);
    }
    if (m.note) d.appendChild(el('p', 'rc-note', m.note));
    log.appendChild(d);
    if (withChips && m.r === 'bot' && m.chips && m.chips.length) renderChips(m.chips, m.main);
    toBottom();
  }
  function add(role, m) {
    var rec = { r: role, t: m.t, card: m.card, note: m.note, chips: m.chips, main: m.main, ai: m.ai, offer: m.offer };
    S.msgs.push(rec); clearChips(); if (!panel.hidden) renderMsg(rec, true); save();
  }
  function showTyping() {
    if (typingEl) return;
    clearChips();
    typingEl = el('div', 'rc-m bot'); typingEl.setAttribute('aria-hidden', 'true');
    var t = el('span', 'rc-typing'); t.innerHTML = '<i></i><i></i><i></i>'; typingEl.appendChild(t);
    log.appendChild(typingEl); log.setAttribute('aria-busy', 'true'); toBottom();
  }
  function hideTyping() { if (typingEl && typingEl.parentNode) typingEl.parentNode.removeChild(typingEl); typingEl = null; log.removeAttribute('aria-busy'); }

  /* ---------- sequencing: bot messages appear one after another ---------- */
  var chain = Promise.resolve();
  function later(fn) { chain = chain.then(fn).catch(function (e) { hideTyping(); if (window.console) console.error('roomi-chat', e); }); return chain; }
  function wait(ms) { return new Promise(function (r) { setTimeout(r, reduce ? 0 : ms); }); }
  function botSay(m) {
    later(function () {
      showTyping();
      return wait(Math.min(900, 380 + String(m.t || '').length * 4)).then(function () { hideTyping(); add('bot', m); });
    });
  }

  /* ---------- answers from confirmed facts ---------- */
  function A(t, chips, extra) { var o = { t: t, chips: chips || ['Get a free estimate'] }; if (extra) for (var k in extra) o[k] = extra[k]; return o; }
  var EST_OFFER = { offer: true, main: true };
  function ratesLine() {
    var r = F.rates || {}, out = [];
    if (r['Labor Only']) out.push('Labor Only ' + r['Labor Only'].replace(/^From /, 'from '));
    if (r['Full-Service Move']) out.push('Full-Service ' + r['Full-Service Move'].replace(/^From /, 'from ') + ' with the truck');
    if (r['White-Glove Move']) out.push('White-Glove ' + r['White-Glove Move'].replace(/^From /, 'from '));
    return out.join(', ');
  }
  function licenseAnswer() {
    var L = F.license || {};
    if (L.status === 'active' && L.number) {
      return A('Yes. Roomi Movers is registered with the State of Florida as a household mover, FDACS registration #' + L.number + '.' + (L.insurance ? ' ' + L.insurance : '') +
        '\nYou can verify any Florida mover at [fdacs.gov](https://www.fdacs.gov/Consumer-Resources) or by calling 1-800-HELP-FLA (435-7352).', ['Get a free estimate', 'How much does it cost?'], EST_OFFER);
    }
    if (L.insured) {
      return A('Roomi Movers is insured. Florida also requires household movers to register with the Florida Department of Agriculture and Consumer Services (FDACS), and we register before moving a single customer. Our registration number goes on this site the moment it is issued. For coverage details, ask Kareem when he calls with your estimate.' +
        '\nYou can verify any Florida mover yourself at [fdacs.gov](https://www.fdacs.gov/Consumer-Resources) or by calling 1-800-HELP-FLA (435-7352).', ['Get a free estimate', 'How much does it cost?']);
    }
    return A('Florida requires household movers to register with the Florida Department of Agriculture and Consumer Services (FDACS), and to carry insurance. We register and put that insurance in place before moving a single customer. Our registration number and coverage details go on this site the moment they are issued.' +
      '\nYou can verify any Florida mover yourself at [fdacs.gov](https://www.fdacs.gov/Consumer-Resources) or by calling 1-800-HELP-FLA (435-7352).', ['Get a free estimate', 'How much does it cost?']);
  }
  var AREA_ALIAS = { 'town-n-country': /\btown (n|and) country\b|\btownncountry\b|\btnc\b/, 'egypt-lake-leto': /\begypt lake\b/, 'land-o-lakes': /\bland (o|of) lakes\b/ };
  function areaMatch(n) {
    for (var i = 0; i < F.areas.length; i++) {
      var a = F.areas[i], re = AREA_ALIAS[a.s] || new RegExp('\\b' + norm(a.n).trim() + '\\b');
      if (re.test(n)) return a;
    }
    return null;
  }
  function unknownLine() {
    return 'I do not have that in front of me, and I would rather not guess. Kareem can tell you directly: call or text ' + PHONE + ', or I can take your details and he will call you.';
  }
  function fallback() { return A(unknownLine(), ['Have Kareem call me', 'How much does it cost?', 'Areas you serve'], EST_OFFER); }

  function answer(raw) {
    var n = norm(raw), nw = n.trim().split(' ').length;
    function has(re) { return re.test(n); }
    var t;

    if (has(/\b(are you|r u|is this|am i (talking|chatting|speaking))\b.{0,14}\b(bot|robot|ai|human|real|person|machine|automated|computer)\b/))
      return A('I am an automated assistant for Roomi Movers, not a person. I can answer common questions and take your estimate request, and Kareem follows up himself. To reach a person now, call or text ' + PHONE + '.', ['Have Kareem call me', 'How much does it cost?']);

    if (has(/\b(how (fast|long|soon|quickly)|when (will|do|would))\b.{0,40}\b(estimate|quote|call|hear|back|respond|reply)\b/) && (t = faqA('how fast will i get my estimate')))
      return A(t, ['Get a free estimate'], EST_OFFER);

    if (has(/\b(estimate|quote|quotes|book|booking|schedule|reserve|get started|sign me up|call me|call back|callback|contact me|reach me|have kareem|someone (to )?(call|contact)|set up a move|hire you)\b/) &&
        !has(/\b(how much|price|cost|rate|rates|hourly|per hour)\b/))
      return { start: true };

    if (has(/\b(talk to|speak to|speak with|talk with|real person|live person|live agent|human|representative|operator|manager|owner|the owner|phone number|your number)\b/))
      return A('You can reach Kareem and the team by call or text at ' + PHONE + '. Our hours are ' + F.hours + '. If you would rather not wait on the phone, I can take your details and he will call you.', ['Have Kareem call me', 'Get a free estimate']);

    if (has(/\b(two|2) hour\b|\bminimum\b|\bclock\b|\bbilled\b|\bbilling\b/) && (t = faqA('two-hour minimum')))
      return A(t, ['Get a free estimate', 'How much does it cost?']);

    if (has(/\b(add to|adds to|extra charges?|extras|affect|surcharge|additional (fee|charge|cost)|hidden|upcharge)\b/) && (t = faqA('can add to the price')))
      return A(t, ['Get a free estimate', 'How much does it cost?']);

    if (has(/\b(price|prices|pricing|cost|costs|how much|rate|rates|hourly|per hour|an hour|charge|charges|fee|fees|afford|cheap|expensive|ballpark|budget)\b/)) {
      var rl = ratesLine();
      return A((rl ? 'Moves are billed by the hour with a two-hour minimum. Starting rates: ' + rl + '.' : 'Moves are billed by the hour with a two-hour minimum.') +
        '\nStairs, long carries and items over 300 lbs may add to the price. Your exact rate and the time we expect come with your free estimate, before you book.' +
        '\n[How hourly pricing works](/resources/how-hourly-moving-pricing-works/)', ['Get a free estimate', 'What can add to the price?'], EST_OFFER);
    }

    if (has(/\b(license|licence|licensed|licensing|insured|insurance|registered|registration|fdacs|bonded|certified|legit|legitimate)\b/)) return licenseAnswer();

    if (has(/\b(damage|damaged|broke|break|breaks|breakage|claim|claims|liable|liability|lost|stolen|scratch)\b/))
      return A('We wrap and pad furniture on every full-service move, and ' + ((F.license || {}).insured || (F.license || {}).status === 'active' ? 'Roomi Movers is insured' : 'we put the insurance Florida requires of movers in place before moving a customer') + '. I do not have our written claims terms in front of me, so please ask Kareem when he calls with your estimate, or call or text ' + PHONE + '.', ['Have Kareem call me', 'Are you licensed?']);

    if (has(/\b(review|reviews|rating|ratings|testimonial|testimonials|reference|references|yelp)\b/)) {
      if (F.reviewCount > 0) return A('Our customer reviews are on the home page: [See reviews](/#reviews)', ['Get a free estimate']);
      return A('We are new and family-run, so we do not have customer reviews yet, and we will not make any up. Real reviews go on the site as we move our first customers. You are welcome to ask Kareem anything before you decide.', ['Have Kareem call me', 'Are you licensed?']);
    }

    if (has(/\b(deposit|payment|pay|paying|credit card|debit|cash|venmo|zelle|cancel|cancellation|cancelling|refund|reschedule|tip|tipping|contract|binding|invoice|receipt)\b/))
      return A('I do not have our payment, deposit or cancellation terms in front of me, and I will not guess at them. Kareem confirms the details with you when he calls with your estimate, or you can call or text ' + PHONE + '.', ['Have Kareem call me', 'How much does it cost?']);

    if (has(/\b(discount|discounts|coupon|promo|promotion|special|specials|offer|deal|deals|launch|50 off|military|senior|veteran)\b/) && (t = faqA('launch offer')))
      return A(t + ' I do not know of other discounts, so ask Kareem if you think you qualify for something else.', ['Get a free estimate'], EST_OFFER);

    var area = areaMatch(n);
    if (area)
      return A('Yes, we move in ' + area.n + '.\n[Moving in ' + area.n + '](/areas/' + area.s + '/) has the local details, and you can request your free estimate right here.', ['Get a free estimate', 'Areas you serve'], EST_OFFER);
    if (has(/\b(long distance|out of state|interstate|cross country|across the country|orlando|miami|jacksonville|st pete|saint pete|st petersburg|clearwater|sarasota|lakeland|bradenton|ocala|gainesville|largo)\b/))
      return A('I do not have long-distance or those cities confirmed. Kareem can tell you whether we can help: call or text ' + PHONE + ' or leave your details.\n[Our service areas](/areas/)', ['Have Kareem call me', 'Areas you serve']);
    if (has(/\b(area|areas|serve|service area|service areas|where do you|do you (go|come|move|travel|service|cover)|travel|cover|county|hillsborough|pasco|pinellas|tampa bay|near me|zip)\b/) && (t = faqA('which areas')))
      return A(t + '\n[See all service areas](/areas/)', ['Get a free estimate'], EST_OFFER);

    if (has(/\b(hours|open|close|closing|opening|what time|business hours|office hours|available|availability|weekend|weekends|saturday|sunday|holiday|late)\b/)) {
      if (has(/\b(ahead|advance|how soon|earliest|last minute|same day|tomorrow|this week|next week|weekend|weekends|saturday|sunday|availability|available)\b/) && (t = faqA('how far ahead')))
        return A(t + ' I cannot see Kareem’s calendar from here, so the quickest way to hold a date is to request your estimate. Our hours are ' + F.hours + '.', ['Get a free estimate'], EST_OFFER);
      if ((t = faqA('what are your hours'))) return A(t, ['Get a free estimate']);
    }
    if (has(/\b(how far ahead|in advance|how soon|earliest|last minute|same day|tomorrow|this week|next week|book ahead)\b/) && (t = faqA('how far ahead')))
      return A(t + ' I cannot see Kareem’s calendar from here, so the quickest way to hold a date is to request your estimate.', ['Get a free estimate'], EST_OFFER);

    if (has(/\b(arrival|window|arrive|show up|late|on time|how long will)\b/) && (t = faqA('arrival window'))) return A(t, ['Get a free estimate']);

    if (has(/\b(package|packages|labor only|full service|full-service|white glove|whiteglove|what is included|whats included|included|what do you offer|what do you do|services|service)\b/) && (t = faqA('what are the packages')))
      return A(t + '\n[See packages and pricing](/pricing/)', ['How much does it cost?', 'Get a free estimate']);

    if (has(/\b(piano|pool table|hot tub|spa|jacuzzi|boat|vehicle|car|motorcycle)\b/))
      return A('Tell us exactly what it is, its size and where it is going in your estimate request, and Kareem will confirm whether we can take it. I would rather not promise something before he sees the details.', ['Get a free estimate', 'Have Kareem call me'], EST_OFFER);

    if (has(/\b(gun safe|safe|appliance|appliances|washer|dryer|fridge|refrigerator|treadmill|heavy|300 lbs|exercise)\b/) && (t = faqA('gun safe')))
      return A(t + '\n[Moving heavy items](/resources/moving-heavy-items/)', ['Get a free estimate'], EST_OFFER);

    if (has(/\b(stairs|stair|walk up|walkup|flight|flights|second floor|third floor|2nd floor|3rd floor)\b/) && (t = faqA('can add to the price')))
      return A(t + ' ' + (faqA('apartments and condos') || ''), ['Get a free estimate'], EST_OFFER);
    if (has(/\b(apartment|apartments|condo|condos|studio|elevator|townhome|townhouse|dorm)\b/) && (t = faqA('apartments and condos')))
      return A(t, ['Get a free estimate'], EST_OFFER);

    if (has(/\b(truck|trucks|equipment|blanket|blankets|dolly|dollies|strap|straps|stretch wrap|rental truck|u haul|uhaul|pods|container)\b/) && (t = faqA('bring the truck')))
      return A(t, ['Get a free estimate', 'See the packages']);
    if (has(/\b(floor|floors|door frame|door frames|doorframe|protect|protection|runners)\b/) && (t = faqA('protect floors')))
      return A(t, ['Get a free estimate']);
    if (has(/\b(bed|beds|take apart|disassemble|assemble|dismantle|furniture)\b/) && (t = faqA('bed apart')))
      return A(t, ['Get a free estimate']);

    if (has(/\b(pack|packing|packed|boxes|box|supplies|tape|bubble)\b/))
      return A('Our box truck brings blankets, stretch wrap, dollies and straps, and furniture is wrapped and padded on full-service moves. I do not have packing-service details, so mention it in your estimate request and Kareem will confirm.\n[Packing guide](/resources/packing-guide/)\n[Moving checklist](/resources/moving-checklist/)', ['Get a free estimate', 'Have Kareem call me']);

    if (has(/\b(email|e mail|address|where are you located|located|location|office|text you|contact)\b/))
      return A('Call or text ' + PHONE + ', or email makeroom@roomimovers.com. We are based in Tampa and come to you.\n[Contact page](/contact/)', ['Get a free estimate']);

    if (has(/\b(who are you|who owns|about you|about the company|kareem|family|how long (have|has)|years|experience|your company|your story)\b/))
      return A('Roomi Movers is run by Kareem Aboroomi and his family, right here in Tampa. When you call, you talk to the person who shows up at your door.\n[About us](/about/)', ['Get a free estimate', 'Are you licensed?']);

    if (nw <= 6 && has(/^ (hi|hello|hey|hiya|howdy|good (morning|afternoon|evening)|yo|sup) /))
      return A('Hello. How can I help with your move? You can ask a question or tap one below.', BASE);
    if (nw <= 6 && has(/^ (thanks|thank you|thx|ty|great|awesome|perfect|cool|ok|okay|got it|sounds good|appreciate it)\b/))
      return A('You are welcome. Anything else I can help with?', BASE);
    if (nw <= 6 && has(/\b(bye|goodbye|that is all|thats all|nothing else|no thanks|nope|all set)\b/))
      return A('Thanks for stopping by. If you think of anything else, I am here, or call or text ' + PHONE + '.', ['Get a free estimate']);
    return null;
  }

  /* best-effort lookup against the FAQ when no direct intent matched */
  var STOP = {};
  'the and for are you your with can what does how will have has not this that from they them its our out who why but any all get got let may more some than then there their about into over also just very was were been being too off per'.split(' ').forEach(function (w) { STOP[w] = 1; });
  function toks(s) { return words(s).filter(function (w) { return w.length > 2 && !STOP[w]; }); }
  function faqMatch(raw) {
    var u = toks(raw), best = null, top = 0;
    if (!u.length) return null;
    F.faq.forEach(function (p) {
      var q = toks(p[0]), a = toks(p[1]), s = 0, qh = 0;
      u.forEach(function (w) { if (q.indexOf(w) > -1) { s += 2; qh++; } else if (a.indexOf(w) > -1) s += 1; });
      if (qh > 0 && s > top) { top = s; best = p; }
    });
    return top >= 3 ? best : null;
  }

  /* ---------- estimate request flow ---------- */
  function askMsg(step, backLead) {
    var l = S.lead, pre = backLead ? 'Back to your estimate request. ' : '', cancelChip = 'Cancel request';
    var prev = S.editing && l[step] ? ' Right now it says: ' + l[step] + '.' : '';
    switch (step) {
      case 'name': return { t: pre + 'Happy to. It takes about a minute, and Kareem calls you with your rate. What is your name?', chips: [cancelChip] };
      case 'phone': return { t: pre + 'Thanks, ' + first(l.name) + '. What is the best phone number to reach you?' + prev, chips: [cancelChip] };
      case 'date': return { t: pre + 'When are you hoping to move? A date or a rough time frame is fine.' + prev, chips: ['This week', 'Within 2 weeks', 'Later this month', 'Next month', 'Not sure yet', cancelChip] };
      case 'size': return { t: pre + 'What size is the home you are moving out of?' + prev, chips: ['Studio / 1 bedroom', '2 bedrooms', '3 bedrooms', '4+ bedrooms', 'Just a few items', 'Labor only (my truck)', cancelChip] };
      case 'from': return { t: pre + 'Where are you moving from? City or ZIP is fine.' + prev, chips: [cancelChip] };
      case 'to': return { t: pre + 'And where are you moving to? City or ZIP, or tell me if you are not sure yet.' + prev, chips: ['Not sure yet', cancelChip] };
      case 'notes': return { t: pre + 'Anything we should know? Stairs, an elevator, heavy items like a gun safe, tight parking.' + prev, chips: ['Nothing special', cancelChip] };
    }
    return confirmMsg();
  }
  function confirmMsg() {
    var l = S.lead;
    return {
      t: 'Here is what I have. Please check it.',
      card: ORDER.map(function (k) { return [LABEL[k], l[k] || '(not given)']; }),
      note: 'When you send this, Roomi Movers may call or text you at that number about your estimate.',
      chips: ['Send my request', 'Change something', 'Cancel request'], main: true
    };
  }
  function startFlow() {
    S.step = 'name'; S.lead = {}; S.editing = null; save();
    botSay(askMsg('name'));
  }
  function next() {
    if (S.editing) { S.editing = null; S.step = 'confirm'; save(); return botSay(confirmMsg()); }
    var i = ORDER.indexOf(S.step);
    if (i < ORDER.length - 1) { S.step = ORDER[i + 1]; save(); return botSay(askMsg(S.step)); }
    S.step = 'confirm'; save(); botSay(confirmMsg());
  }
  function cancelFlow() {
    S.step = 'idle'; S.lead = {}; S.editing = null; save();
    botSay(A('No problem, I have cleared that. Ask me anything, or start again whenever you like.', BASE));
  }
  function looksLikeName(t) {
    return t.length <= 60 && !/\d/.test(t) && t.split(/\s+/).length <= 5 && !/[?]/.test(t) &&
      !/\b(estimate|quote|price|cost|how|what|when|where|why|move|moving|help|licensed|insured|areas?|hours?)\b/i.test(t);
  }
  function validate(step, raw) {
    var t = raw.replace(/\s+/g, ' ').trim();
    if (step === 'name') {
      t = t.replace(/^(my name is|my name’s|my name's|name is|i am|i’m|i'm|im|this is|it is|its|it’s|call me)\s+/i, '').replace(/[.,!]+$/, '');
      if (t.length < 2 || !/[a-z]/i.test(t)) return { err: 'I did not catch a name there. What should we call you?' };
      return { val: t.slice(0, 60) };
    }
    if (step === 'phone') {
      var d = digits10(t);
      if (!d) return { err: 'That number looks incomplete. Please give the full 10-digit number with area code, like (813) 555-0123.' };
      return { val: fmtPhone(d) };
    }
    if (step === 'notes') return { val: /^(nothing special|no|none|nope|nothing|n\/a)$/i.test(t) ? '(none)' : t.slice(0, 500) };
    if (t.length < 2) return { err: 'Could you add a little more? A short answer is fine.' };
    return { val: t.slice(0, 120) };
  }
  function isQuestion(t) {
    var w = t.trim().split(/\s+/);
    return /\?\s*$/.test(t) || (w.length >= 3 && /^(how|what|when|where|why|do|does|can|could|are|is|will|would|should|who|which)\b/i.test(t));
  }
  function pickMenu() {
    S.step = 'pick'; save();
    botSay({ t: 'What would you like to change?', chips: ORDER.map(function (k) { return LABEL[k]; }).concat(['Back']) });
  }
  function flowInput(text) {
    var step = S.step;
    if (step === 'sending') return;
    if (CANCEL.test(text.trim())) return cancelFlow();
    var n = norm(text);
    if (step === 'confirm') {
      if (/^ (try|send|yes|yep|yeah|sure|ok|okay|submit|looks good|correct|thats right|that is right|go ahead|all good)\b/.test(n)) return send();
      if (/\b(change|edit|wrong|fix|update|no|nope|incorrect|mistake)\b/.test(n)) return pickMenu();
      return botSay({ t: 'Tap "Send my request" when the details look right, or "Change something" to fix one.', chips: ['Send my request', 'Change something', 'Cancel request'], main: true });
    }
    if (step === 'pick') {
      if (/\bback\b/.test(n)) { S.step = 'confirm'; save(); return botSay(confirmMsg()); }
      for (var i = 0; i < ORDER.length; i++) {
        if (n.indexOf(' ' + norm(LABEL[ORDER[i]]).trim()) > -1 || n.trim() === ORDER[i]) { S.editing = ORDER[i]; S.step = ORDER[i]; save(); return botSay(askMsg(ORDER[i])); }
      }
      return botSay({ t: 'Which one would you like to change?', chips: ORDER.map(function (k) { return LABEL[k]; }).concat(['Back']) });
    }
    var q = isQuestion(text), notName = step === 'name' && !looksLikeName(text), ans = null;
    if (q || notName) ans = answer(text);
    if (ans && ans.start) return botSay(askMsg(step, true));
    var interrupt = !!ans || notName || (q && step !== 'date' && step !== 'size' && step !== 'notes');
    if (interrupt) {
      if (ans) { botSay(ans); botSay(askMsg(step, true)); }
      else if (AI) askAI(true);
      else { botSay(A(unknownLine(), ['Cancel request'])); botSay(askMsg(step, true)); }
      return;
    }
    var v = validate(step, text);
    if (v.err) { var m = askMsg(step); return botSay({ t: v.err, chips: m.chips }); }
    S.lead[step] = v.val; save();
    next();
  }
  function post(data) {
    var ctrl = window.AbortController ? new AbortController() : null;
    var timer = setTimeout(function () { if (ctrl) ctrl.abort(); }, 15000);
    return fetch(F.formEndpoint, {
      method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(data), signal: ctrl ? ctrl.signal : undefined
    }).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (j) {
        if (!r.ok || String(j.success) !== 'true') { var err = new Error(j.message || 'HTTP ' + r.status); err.server = true; throw err; }
      });
    }).then(function (v) { clearTimeout(timer); return v; }, function (e) { clearTimeout(timer); throw e; });
  }
  function setBusy(b) { input.disabled = b; sendB.disabled = b; }
  function send() {
    if (S.sending) return;
    S.sending = true; S.step = 'sending'; save(); setBusy(true);
    var l = S.lead;
    var data = {
      _subject: 'New estimate request: ' + l.name + ' (Chat assistant)', _template: 'table', 'Form': 'Chat assistant',
      'Name': l.name, 'Phone': l.phone, 'Move date': l.date, 'Home size': l.size, 'Moving from': l.from, 'Moving to': l.to,
      'Stairs, elevator, heavy items': l.notes || '(none)',
      'Questions asked in chat': S.asked.join(' | ') || '(none)',
      'Sent from': location.href
    };
    later(function () {
      showTyping();
      return post(data).then(function () {
        hideTyping(); S.sending = false; setBusy(false);
        var who = first(l.name), ph = l.phone;
        S.step = 'idle'; S.lead = {}; S.asked = []; S.editing = null;
        add('bot', {
          t: 'Thank you, ' + who + '. Your estimate request is in.\nKareem will call you at ' + ph + ' with your hourly rate and the time we expect the move to take. Most estimates are back the same day.\nIn a hurry? Call or text ' + PHONE + '.',
          chips: ['Close chat', 'Are you licensed?', 'How much does it cost?']
        });
      }, function (err) {
        hideTyping(); S.sending = false; setBusy(false); S.step = 'confirm';
        add('bot', {
          t: err && err.server
            ? 'Online requests are not going through right now. Please call or text ' + PHONE + ' and Kareem will get you an estimate.'
            : 'That did not send. Please check your connection and try again, or call or text ' + PHONE + '.',
          chips: ['Try sending again', 'Cancel request']
        });
        input.focus();
      });
    });
  }

  /* ---------- optional AI replies through the secure relay ---------- */
  function history() {
    var out = [];
    S.msgs.slice(-14).forEach(function (m) {
      var role = m.r === 'you' ? 'user' : 'assistant', text = String(m.t || '').slice(0, 700);
      if (m.card) text += ' ' + m.card.map(function (kv) { return kv[0] + ': ' + kv[1]; }).join('; ');
      if (!text) return;
      if (out.length && out[out.length - 1].role === role) out[out.length - 1].content += '\n' + text;
      else out.push({ role: role, content: text });
    });
    while (out.length && out[0].role !== 'user') out.shift();
    return out;
  }
  function askAI(resume) {
    if (S.ai >= 25) { botSay(A('We have covered a lot here. For anything more, please call or text ' + PHONE + ' and Kareem will help.', ['Have Kareem call me'])); return; }
    S.ai++; save();
    later(function () {
      showTyping();
      var ctrl = window.AbortController ? new AbortController() : null;
      var timer = setTimeout(function () { if (ctrl) ctrl.abort(); }, 25000);
      var lastUser = '';
      for (var i = S.msgs.length - 1; i >= 0; i--) if (S.msgs[i].r === 'you') { lastUser = S.msgs[i].t; break; }
      return fetch(AI, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: history(), page: location.pathname }), signal: ctrl ? ctrl.signal : undefined
      }).then(function (r) {
        return r.json().then(function (j) { if (!r.ok || typeof j.reply !== 'string') throw new Error('bad reply'); return j.reply; });
      }).then(function (reply) {
        clearTimeout(timer); hideTyping();
        var wantsEstimate = /\[\[ESTIMATE\]\]/.test(reply);
        var text = reply.replace(/\[\[ESTIMATE\]\]/g, '').replace(/\s+\n/g, '\n').trim().slice(0, 700);
        if (!text) throw new Error('empty');
        add('bot', { t: text, ai: true, chips: wantsEstimate ? [] : ['Get a free estimate', 'Have Kareem call me'] });
        if (wantsEstimate) startFlow();
        else if (resume && S.step !== 'idle') botSay(askMsg(S.step, true));
      }).catch(function () {
        clearTimeout(timer); hideTyping();
        var fm = faqMatch(lastUser);
        add('bot', fm ? A(fm[1], ['Get a free estimate']) : fallback());
        if (resume && S.step !== 'idle') botSay(askMsg(S.step, true));
      });
    });
  }

  /* ---------- routing ---------- */
  function route(text) {
    if (S.step !== 'idle') return flowInput(text);
    var ans = answer(text);
    if (ans && ans.start) return startFlow();
    if (ans) return botSay(ans);
    if (AI) return askAI(false);
    var fm = faqMatch(text);
    if (fm) return botSay(A(fm[1], ['Get a free estimate'], EST_OFFER));
    botSay(fallback());
  }
  var CHIP_ONLY = BASE.concat(['Have Kareem call me', 'What can add to the price?', 'See the packages']);
  function userSend(text) {
    text = String(text || '').replace(/\s+/g, ' ').trim().slice(0, 500);
    if (!text) return;
    var lastBot = null;
    for (var i = S.msgs.length - 1; i >= 0; i--) if (S.msgs[i].r === 'bot') { lastBot = S.msgs[i]; break; }
    add('you', { t: text });
    if ((S.step === 'idle' || isQuestion(text)) && words(text).length >= 3 && S.asked.length < 5 && CHIP_ONLY.indexOf(text) < 0 && !CANCEL.test(text)) S.asked.push(text.slice(0, 160));
    if (S.step === 'idle' && lastBot && lastBot.offer && /^ (yes|yeah|yep|yup|sure|ok|okay|please|yes please|sounds good|lets do it|do it|go ahead) $/.test(norm(text))) return startFlow();
    route(text);
  }
  function chip(label) {
    if (label === 'Close chat') { closePanel(); return; }
    if (label === 'See the packages') label = 'What are the packages?';
    userSend(label);
  }

  /* ---------- open / close ---------- */
  var lastFocus = null;
  function syncInput() {
    var s = S.step, ph = 'Type your question';
    input.setAttribute('autocomplete', 'off'); input.setAttribute('inputmode', 'text');
    if (s === 'name') { ph = 'Your name'; input.setAttribute('autocomplete', 'name'); }
    else if (s === 'phone') { ph = 'Your phone number'; input.setAttribute('autocomplete', 'tel'); input.setAttribute('inputmode', 'tel'); }
    else if (s === 'date') ph = 'Move date or time frame';
    else if (s === 'size') ph = 'Home size';
    else if (s === 'from') ph = 'City or ZIP you are moving from';
    else if (s === 'to') ph = 'City or ZIP you are moving to';
    else if (s === 'notes') ph = 'Stairs, elevator, heavy items';
    else if (s === 'confirm' || s === 'pick') ph = 'Or type here';
    input.placeholder = ph;
  }
  function fit() {
    if (!mobileMQ.matches) { panel.style.removeProperty('--rc-h'); panel.style.removeProperty('--rc-top'); return; }
    var vv = window.visualViewport;
    if (vv) { panel.style.setProperty('--rc-h', vv.height + 'px'); panel.style.setProperty('--rc-top', vv.offsetTop + 'px'); }
  }
  function openPanel(quiet) {
    if (!panel.hidden) return;
    lastFocus = document.activeElement;
    panel.hidden = false; launch.hidden = true; launch.setAttribute('aria-expanded', 'true');
    panel.setAttribute('aria-modal', mobileMQ.matches ? 'true' : 'false');
    if (mobileMQ.matches) document.documentElement.classList.add('rc-lock');
    S.open = true;
    log.textContent = '';
    if (!S.msgs.length) {
      add('bot', { t: 'Hi, I am the Roomi Movers automated assistant. I can answer common questions and take your estimate request for Kareem. For anything urgent, call or text ' + PHONE + '.', chips: BASE });
    } else {
      S.msgs.forEach(function (m, i) { renderMsg(m, i === S.msgs.length - 1); });
    }
    syncInput(); fit(); toBottom(); save();
    if (!quiet) setTimeout(function () { try { input.focus({ preventScroll: true }); } catch (e) { input.focus(); } }, 30);
  }
  function closePanel() {
    if (panel.hidden) return;
    panel.hidden = true; launch.hidden = false; launch.setAttribute('aria-expanded', 'false');
    document.documentElement.classList.remove('rc-lock');
    S.open = false; save();
    var t = lastFocus && document.contains(lastFocus) && lastFocus !== document.body ? lastFocus : launch;
    try { t.focus(); } catch (e) { launch.focus(); }
  }

  launch.addEventListener('click', function () { openPanel(false); });
  closeB.addEventListener('click', closePanel);
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (input.disabled) return;
    var v = input.value; input.value = '';
    userSend(v);
  });
  document.addEventListener('keydown', function (e) {
    if (panel.hidden) return;
    if (e.key === 'Escape') { e.preventDefault(); closePanel(); return; }
    if (e.key === 'Tab' && mobileMQ.matches) {
      var f = [].filter.call(panel.querySelectorAll('a[href],button,input,[tabindex="0"]'), function (n) { return !n.disabled && n.offsetParent !== null; });
      if (!f.length) return;
      var a = f[0], z = f[f.length - 1];
      if (e.shiftKey && document.activeElement === a) { e.preventDefault(); z.focus(); }
      else if (!e.shiftKey && document.activeElement === z) { e.preventDefault(); a.focus(); }
    }
  });
  if (window.visualViewport) { visualViewport.addEventListener('resize', fit); visualViewport.addEventListener('scroll', fit); }
  if (mobileMQ.addEventListener) mobileMQ.addEventListener('change', function () { fit(); if (!panel.hidden) document.documentElement.classList.toggle('rc-lock', mobileMQ.matches); });
  // any "Chat with us" link on the site can open the assistant
  document.addEventListener('click', function (e) {
    var t = e.target && e.target.closest ? e.target.closest('[data-open-chat],a[href="#chat"]') : null;
    if (t) { e.preventDefault(); openPanel(false); }
  });
  window.RoomiChat = { open: function () { openPanel(false); }, close: closePanel };

  // restore the conversation after a page change (desktop only: on a phone the sheet would cover the page the visitor just opened)
  if (S.open && !mobileMQ.matches) openPanel(true);
  else if (location.hash === '#chat') openPanel(false);
  else S.open = false;
})();
