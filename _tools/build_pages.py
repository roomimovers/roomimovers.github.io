"""Builds the service and area pages, assets/site.css, sitemap.xml and robots.txt.

Run from the repo root:  py _tools/build_pages.py
Styles come from the home page's <style> blocks, so the pages always match it.
Folders starting with "_" are not published by GitHub Pages, so this script stays private.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = 'https://roomimovers.com'
UPDATED = '2026-10-12'
PHONE, PHONE_TEL, EMAIL = '(813) 436-3216', '+18134363216', 'makeroom@roomimovers.com'
OFFER = '<b>Launch special:</b> $50 off moves booked by Dec 31, 2026'

PRICING = [
    'Billed by the hour, with a two-hour minimum. The clock starts when we arrive and stops when the last item is placed.',
    'Your free estimate shows the hourly rate and how long we expect the job to take.',
    'Stairs, long carries from the truck and items over 300 lbs (like gun safes) may add to the price. We tell you before you book.',
]
WHITE_GLOVE = ['Floor runners and door-frame guards', 'TVs, art and mirrors boxed', 'Furniture placed room by room', 'Extra crew member for faster moves']

SERVICES = [
    {
        'slug': 'home-moves', 'card': 'Houses and townhomes, with the box truck, wrapping and bed setup included.', 'name': 'Home Moves', 'short': 'Home moves',
        'title': 'Home Movers in Tampa Bay | Roomi Movers',
        'desc': 'House and townhome moves in Tampa, Wesley Chapel, Lutz and Carrollwood. Box truck included, furniture wrapped and padded, beds set back up. Hourly rate, free estimate.',
        'h1': 'Home moves, handled like our own',
        'lede': 'House and townhome moves across Tampa, Wesley Chapel, Lutz and Carrollwood. We bring the box truck, wrap and pad your furniture, and set everything in place at your new home.',
        'included_title': 'Included with a full-service move',
        'included': ['Box truck, moving blankets, stretch wrap, dollies and straps', 'Furniture wrapped and padded', 'Beds taken apart and set back up', 'Loaded tight so nothing shifts on the drive', 'Everything set in place at your new home'],
        'extra_title': 'Want more protection? Choose White-Glove',
        'extra_intro': 'For larger homes and the pieces you care most about:',
        'extra': WHITE_GLOVE,
        'notes': [
            ('Plan ahead', 'One to two weeks ahead is ideal. Weekends and the last few days of the month book first, so reach out early if your date is fixed.'),
            ('Big or unusual items', 'Text a photo of anything large to %s and we will tell you what it takes.' % PHONE),
        ],
    },
    {
        'slug': 'apartment-condo-moves', 'card': 'Studios to 3 bedrooms, walk-ups and elevator buildings, on your move-out timeline.', 'name': 'Apartment & Condo Moves', 'short': 'Apartment & condo moves',
        'title': 'Apartment & Condo Movers in Tampa Bay | Roomi Movers',
        'desc': 'Apartment and condo moves from studios to 3 bedrooms in Tampa, Wesley Chapel, Lutz and Carrollwood. Walk-ups and elevators, move-out deadlines met. Free estimate.',
        'h1': 'Apartment and condo moves, on your schedule',
        'lede': 'Studios to three bedrooms, walk-ups and elevator buildings. We work around your move-out deadline and keep you posted on timing.',
        'included_title': 'What we handle',
        'included': ['Walk-ups and elevator buildings', 'Move-out deadlines met', 'Studios to 3 bedrooms', 'Furniture wrapped and padded', 'Beds taken apart and set back up'],
        'extra_title': 'Help us plan your building',
        'extra_intro': 'Tell us when you request your estimate:',
        'extra': ['Which floor you are on, at both places', 'Whether there is an elevator, and if it needs a reservation', 'Where the truck can park, and how far it is to your door', 'Any gate codes or building move-in rules'],
        'notes': [
            ('Stairs and long carries', 'Stairs and long walks from the truck can add time, so we ask about them up front and include them in your estimate.'),
            ('Two-hour arrival window', 'We give you a two-hour arrival window and keep you posted on timing, so you are not waiting around all day.'),
        ],
    },
    {
        'slug': 'loading-unloading', 'card': 'Two movers for your rental truck, moving container or storage unit.', 'name': 'Loading & Unloading', 'short': 'Loading & unloading',
        'title': 'Moving Labor: Loading & Unloading in Tampa Bay | Roomi Movers',
        'desc': 'Labor-only moving help in Tampa Bay. Two movers load or unload your rental truck, moving container or storage unit, packed tight so nothing shifts. Free estimate.',
        'h1': 'Loading and unloading help, packed tight',
        'lede': 'Already have the truck, container or storage unit? Our labor-only crew does the heavy lifting and packs everything tight so nothing shifts.',
        'included_title': 'Labor only, done right',
        'included': ['Two movers for your rental truck, PODS or other moving container', 'Storage units, loading or unloading', 'Pads, straps and dollies', 'Packed tight so nothing shifts'],
        'extra_title': 'Need the truck too?',
        'extra_intro': 'Choose a full-service move instead and we bring the box truck:',
        'extra': ['Box truck included', 'Furniture wrapped and padded', 'Beds taken apart and set up'],
        'notes': [
            ('What to tell us', 'Where the truck or container will be parked, the size of the home, and any stairs or heavy items.'),
            ('Hourly, two-hour minimum', 'Labor-only moves are billed by the hour like every Roomi move, with a free estimate first.'),
        ],
    },
    {
        'slug': 'heavy-specialty-items', 'card': 'Gun safes, appliances, treadmills and oversized furniture.', 'name': 'Heavy & Specialty Items', 'short': 'Heavy & specialty items',
        'title': 'Gun Safe, Appliance & Heavy Item Movers in Tampa | Roomi Movers',
        'desc': 'Moving gun safes, washers, dryers, fridges, treadmills and oversized furniture in Tampa Bay. Tell us the size and where it is going and we bring the right equipment.',
        'h1': 'Heavy and specialty items, moved safely',
        'lede': 'Gun safes, appliances, treadmills and oversized furniture. Tell us the size and where it is going, and we bring the right equipment for the job.',
        'included_title': 'Items we move',
        'included': ['Gun safes', 'Washers, dryers and fridges', 'Treadmills and exercise equipment', 'Oversized furniture'],
        'extra_title': 'Get an accurate estimate',
        'extra_intro': 'Send us:',
        'extra': ['The item, with its size and weight if you know it', 'Where it is going: garage, upstairs, a tight hallway', 'A photo, texted to %s' % PHONE],
        'notes': [
            ('Items over 300 lbs', 'Items over 300 lbs, like gun safes, may add to the price. We tell you before you book.'),
            ('Part of a bigger move?', 'Heavy items can be part of any home, apartment or labor-only move. Just list them in your estimate request.'),
        ],
    },
]

# Local facts below were checked against Wikipedia on 2026-10-12 (county, ZIP codes, main roads, landmarks).
# Keep them factual: no claims about past jobs, reviews or anything we have not confirmed.
AREAS = [
    {
        'slug': 'tampa', 'name': 'Tampa',
        'title': 'Movers in Tampa, FL | Roomi Movers',
        'desc': 'Family-run movers based in Tampa: condos downtown and in Channelside, homes in Seminole Heights, Hyde Park and New Tampa. Hourly rate, two-hour minimum, free estimate.',
        'h1': 'Tampa movers, based right here',
        'lede': 'Roomi Movers is a family-run moving company based in Tampa. When you call, you talk to the person who shows up at your door.',
        'facts': [('County', 'Hillsborough (Tampa is the county seat)'), ('Main routes', 'I-275 and I-4'),
                  ('Neighborhoods', 'Downtown, Channelside, Hyde Park, Seminole Heights, Westshore and New Tampa')],
        'about': [
            'Tampa homes range from high-rise condos downtown and in Channelside to houses in Seminole Heights, Hyde Park and New Tampa. Each plans a little differently, so your estimate starts with a few questions about the building, the stairs and the parking.',
            'We also move people between Tampa and Wesley Chapel, Lutz and Carrollwood.',
        ],
        'plan': [
            ('Condo and apartment towers', 'Downtown, Channelside and Westshore buildings often have move-in rules. Ask your building manager about elevator reservations, loading areas and move hours, and tell us what they need.'),
            ('Houses with street parking', 'If the truck has to park on the street or away from the door, tell us how far the walk is. Long carries can add time, and we include them in your estimate.'),
        ],
    },
    {
        'slug': 'wesley-chapel', 'name': 'Wesley Chapel',
        'title': 'Movers in Wesley Chapel, FL | Roomi Movers',
        'desc': 'Wesley Chapel movers for homes, townhomes and apartments in ZIP codes 33543, 33544 and 33545. Family-run, hourly rate, free estimate before you book.',
        'h1': 'Wesley Chapel movers you can reach directly',
        'lede': 'Moving in or out of Wesley Chapel? We bring the truck, wrap and pad your furniture, and set beds back up at your new place.',
        'facts': [('County', 'Pasco'), ('ZIP codes', '33543, 33544, 33545'), ('Main routes', 'I-75, SR 56 and Bruce B. Downs Boulevard'),
                  ('Landmarks', 'Shops at Wiregrass, Tampa Premium Outlets and Cypress Creek Town Center')],
        'about': [
            'Wesley Chapel sits in Pasco County, north of Tampa along I-75. Moving between Wesley Chapel and Tampa, Lutz or Carrollwood? We plan the drive and the timing as part of your estimate.',
        ],
        'plan': [
            ('Community and HOA rules', 'If your neighborhood has an HOA or gated entry, check its rules for moving trucks and parking, and have gate codes ready for both addresses.'),
            ('Moving day timing', 'Tell us your closing or lease times. A two-hour arrival window, and updates on timing, help you plan around key handoffs.'),
        ],
    },
    {
        'slug': 'lutz', 'name': 'Lutz',
        'title': 'Movers in Lutz, FL | Roomi Movers',
        'desc': 'Lutz movers for homes, apartments and condos in ZIP codes 33548, 33549, 33558 and 33559, on both the Hillsborough and Pasco sides. Hourly rate, free estimate.',
        'h1': 'Lutz movers, just up the road',
        'lede': 'From north Tampa to Lutz and back, our crew handles homes, apartments, loading help and the heavy pieces.',
        'facts': [('County', 'Hillsborough and Pasco (Lutz spans both)'), ('ZIP codes', '33548, 33549, 33558, 33559'),
                  ('Main routes', 'US 41, I-275, State Road 597 and State Road 54')],
        'about': [
            'Lutz sits just north of Tampa and stretches across the Hillsborough and Pasco county line, with US 41 running through the middle. We move people within Lutz and between Lutz and Tampa, Wesley Chapel and Carrollwood.',
        ],
        'plan': [
            ('Send us the exact address', 'Because Lutz spans two counties and four ZIP codes, the full address helps us plan the route and timing for your estimate.'),
            ('Long driveways and big yards', 'If the truck can\'t get close to the door, tell us how far the walk is. Long carries can add time, and we include them in your estimate.'),
        ],
    },
    {
        'slug': 'carrollwood', 'name': 'Carrollwood',
        'title': 'Movers in Carrollwood, FL | Roomi Movers',
        'desc': 'Carrollwood movers for homes, apartments and condos in ZIP codes 33618 and 33624, near Dale Mabry Highway and Lake Carroll. Hourly rate, free estimate.',
        'h1': 'Carrollwood movers who keep you posted',
        'lede': 'Home, apartment and condo moves in Carrollwood, with a two-hour arrival window and updates on timing.',
        'facts': [('County', 'Hillsborough'), ('ZIP codes', '33618, 33624'), ('Main routes', 'Dale Mabry Highway, Busch Boulevard, Bearss Avenue and Fletcher Avenue'),
                  ('Landmarks', 'Lake Carroll and Carrollwood Village')],
        'about': [
            'Carrollwood is in north Tampa, built out around Lake Carroll starting in 1959. Many of its homes date from those early decades, alongside newer apartments and condos near Dale Mabry Highway.',
            'We move people within Carrollwood and between Carrollwood and Tampa, Wesley Chapel and Lutz.',
        ],
        'plan': [
            ('Older homes, tighter spaces', 'Homes from the 1960s and 70s can have narrower halls and doorways. Measure your largest pieces, or text us photos, and we will plan how they come out.'),
            ('Apartments and condos', 'Ask your building about elevator access and move hours, and tell us which floor you are on at both addresses.'),
        ],
    },
]
AREA_TIPS = [
    'Reserve the elevator or loading area if your building asks for it.',
    'Check community or HOA rules for moving trucks and parking.',
    'Have gate codes and parking directions ready for both addresses.',
    'Measure large furniture against tight doorways and stairwells.',
]

PAGE_CSS = '''
/* inner pages */
.page-hero{background:var(--band);padding-block:44px 56px}
.page-hero .wrap{display:grid;grid-template-columns:1.1fr .9fr;gap:44px;align-items:center}
.crumbs{font-size:14px;color:var(--muted);margin:0 0 14px;padding:0;list-style:none;display:flex;flex-wrap:wrap;gap:6px}
.crumbs li+li::before{content:"/";margin-right:6px;color:var(--line)}
.crumbs a{color:var(--muted)}
.page-hero h1{font-size:clamp(34px,5vw,56px);font-weight:900;letter-spacing:-.03em;margin-top:10px}
.page-hero .lede{color:var(--muted)}
.page-hero .offer{margin-top:22px;display:inline-block;padding:10px 14px;border-radius:12px;background:var(--card);border:2px dashed var(--coral);font-size:15px}
.page-photo{margin:0}
.page-photo img{display:block;width:100%;height:auto;aspect-ratio:16/11;object-fit:cover;object-position:30% 12%;border-radius:18px;box-shadow:14px 14px 0 var(--blue)}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:24px}
.card{padding:28px;border:1px solid var(--line);border-radius:16px;background:var(--card)}
.card h2{font-size:clamp(24px,2.6vw,30px)}
.card p{color:var(--muted);margin-top:10px}
.card h3 a{color:inherit;text-decoration:none}
.card h3 a:hover{color:var(--coral-ink);text-decoration:underline;text-underline-offset:3px}
.ticks{list-style:none;padding:0;display:grid;gap:10px;margin-top:16px}
.ticks li{display:flex;gap:10px;align-items:flex-start}
.ticks li::before{content:"";flex:none;width:18px;height:18px;margin-top:5px;border-radius:50%;background:#F7652F url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M20 6 9 17l-5-5' fill='none' stroke='%231A0E0A' stroke-width='3.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center/12px no-repeat}
.notes{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px;margin-top:24px}
.notes h3{font-size:19px}
.notes p{color:var(--muted);margin-top:8px}
.chips{display:flex;flex-wrap:wrap;gap:10px;list-style:none;padding:0;margin-top:16px}
.chips a{display:block;padding:10px 18px;border:2px solid var(--ink);border-radius:999px;text-decoration:none;color:var(--ink);font-family:var(--display);font-weight:800}
.chips a:hover{border-color:var(--coral)}
.prose{max-width:46em}
.card h2 a{color:inherit;text-decoration:none}
.card h2 a:hover{color:var(--coral-ink);text-decoration:underline;text-underline-offset:3px}
.cols .card h2{font-size:clamp(22px,2.2vw,28px)}
#faq .head,#quote .quote-side>.eyebrow,#quote .quote-side>h2{display:none}
#faq{padding-top:48px}
.area-intro{display:grid;grid-template-columns:1.2fr 1fr;gap:32px 48px;align-items:start}
.facts{display:grid;gap:14px;margin:16px 0 0}
.facts div{display:grid;gap:2px;padding-top:14px;border-top:1px solid var(--line)}
.facts div:first-child{border-top:0;padding-top:0}
.facts dt{font-family:var(--display);font-weight:800;font-size:14px;color:var(--coral-ink)}
.facts dd{margin:0;color:var(--ink)}
.services .card h3{font-size:20px}
.services .card p{font-size:15.5px}
.prose p{color:var(--muted);margin-top:12px}
@media (max-width:860px){.page-hero .wrap,.cols,.notes,.area-intro{grid-template-columns:1fr}.page-photo{max-width:520px}}
'''


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def build_css():
    home = (ROOT / 'index.html').read_text(encoding='utf-8')
    head = home[:home.index('</head>')]
    blocks = re.findall(r'<style>(.*?)</style>', head, re.S)
    css = '\n'.join(blocks).replace('url(images/', 'url(/images/')
    out = '/* Generated by _tools/build_pages.py from the home page styles. Edit index.html, then rebuild. */\n' + css + PAGE_CSS
    (ROOT / 'assets').mkdir(exist_ok=True)
    (ROOT / 'assets' / 'site.css').write_text(out, encoding='utf-8', newline='\n')


def ticks(items):
    return '<ul class="ticks">' + ''.join('<li>%s</li>' % esc(i) for i in items) + '</ul>'


BUSINESS_REF = {'@type': 'MovingCompany', '@id': SITE + '/#business', 'name': 'Roomi Movers', 'url': SITE + '/', 'telephone': '+1-813-436-3216'}


def breadcrumbs_ld(trail):
    return {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': SITE + u} for i, (n, u) in enumerate(trail)]}


def page(path, title, desc, crumbs, h1, lede, body, ld):
    url = SITE + path
    crumb_html = '<ol class="crumbs">' + ''.join(
        ('<li><a href="%s">%s</a></li>' % (u, esc(n))) if u else '<li aria-current="page">%s</li>' % esc(n) for n, u in crumbs) + '</ol>'
    graph = {'@context': 'https://schema.org', '@graph': ld}
    return '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" href="/images/apple-touch-icon.png">
<meta name="theme-color" content="#061A3C">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{site}/images/og-image.jpg">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;800;900&family=Figtree:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="/assets/site.css">
<script type="application/ld+json">
{ld}
</script>
</head>
<body>
<a class="skip" href="#main">Skip to main content</a>
<div class="util">
  <div class="wrap">
    <span>Local movers serving Tampa, Wesley Chapel, Lutz &amp; Carrollwood</span>
    <span><a class="ph" href="tel:{tel}">{phone}</a> · <a href="mailto:{email}">{email}</a></span>
  </div>
</div>

<header class="bar">
  <div class="wrap">
    <a class="brand" href="/" aria-label="Roomi Movers home">
      <img src="/images/logo-mark.png" alt="" width="56" height="40">
      <span class="brand-word"><b>roomi</b><span>MOVERS</span></span>
    </a>
    <nav class="links" id="site-nav" aria-label="Main">
      <a href="/services/">Services</a>
      <a href="/pricing/">Pricing</a>
      <a href="/areas/">Service Areas</a>
      <a href="/about/">About</a>
      <a href="/faq/">FAQ</a>
      <a href="/contact/">Contact</a>
    </nav>
    <div class="bar-ctas">
      <a class="call ph" href="tel:{tel}">{phone}</a>
      <a class="btn btn-primary bar-cta" href="/contact/">Free Estimate</a>
      <button class="menu-btn" type="button" aria-expanded="false" aria-controls="site-nav"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>Menu</button>
    </div>
  </div>
</header>

<main id="main" tabindex="-1">
  <section class="page-hero">
    <div class="wrap">
      <div>
        <nav aria-label="Breadcrumb">{crumbs}</nav>
        <p class="eyebrow">Roomi Movers · Tampa Bay</p>
        <h1>{h1}</h1>
        <p class="lede">{lede}</p>
        <div class="ctas">
          <a class="btn btn-primary" href="/contact/">Get a Free Estimate</a>
          <a class="btn btn-ghost" href="tel:{tel}">Call {phone}</a>
        </div>
        <p class="offer">{offer}</p>
      </div>
      <figure class="page-photo">
        <picture>
          <source type="image/webp" srcset="/images/roomi-team-truck-960.webp 960w, /images/roomi-team-truck-1672.webp 1672w" sizes="(max-width: 860px) 100vw, 520px">
          <img src="/images/roomi-team-truck-960.jpg" srcset="/images/roomi-team-truck-960.jpg 960w, /images/roomi-team-truck-1672.jpg 1672w" sizes="(max-width: 860px) 100vw, 520px" alt="Kareem Aboroomi, owner of Roomi Movers, in front of the Roomi Movers box truck" width="960" height="540">
        </picture>
      </figure>
    </div>
  </section>
{body}
  <section class="closer">
    <div class="wrap" style="padding-top:56px">
      <h2>Ready to move?</h2>
      <p>Get your free estimate, or call or text and talk to us directly. Most estimates are back the same day.</p>
      <div class="ctas">
        <a class="btn btn-primary" href="/contact/">Get a Free Estimate</a>
        <a class="btn btn-ghost" href="tel:{tel}">Call</a>
        <a class="btn btn-ghost" href="sms:{tel}">Text</a>
      </div>
    </div>
  </section>
</main>
{footer}
<nav class="actionbar" aria-label="Quick actions">
  <a href="tel:{tel}">Call</a>
  <a href="sms:{tel}">Text</a>
  <a class="main" href="/contact/">Free Estimate</a>
</nav>
<script>
(function () {{
  var btn = document.querySelector('.menu-btn'), nav = document.getElementById('site-nav');
  if (!btn || !nav) return;
  function set(open) {{ nav.classList.toggle('is-open', open); btn.setAttribute('aria-expanded', open ? 'true' : 'false'); }}
  btn.addEventListener('click', function () {{ set(btn.getAttribute('aria-expanded') !== 'true'); }});
  nav.addEventListener('click', function (e) {{ if (e.target.closest('a')) set(false); }});
  document.addEventListener('keydown', function (e) {{ if (e.key === 'Escape' && nav.classList.contains('is-open')) {{ set(false); btn.focus(); }} }});
  document.addEventListener('click', function (e) {{ if (!e.target.closest('.bar')) set(false); }});
}})();
</script>
</body>
</html>
'''.format(title=esc(title), desc=esc(desc), url=url, site=SITE, ld=json.dumps(graph, indent=1, ensure_ascii=False),
           tel=PHONE_TEL, phone=PHONE, email=EMAIL, crumbs=crumb_html, h1=esc(h1), lede=esc(lede), offer=OFFER,
           body=body, footer=footer())


def footer():
    svc = ''.join('<li><a href="/services/%s/">%s</a></li>' % (s['slug'], esc(s['short'])) for s in SERVICES)
    areas = ''.join('<li><a href="/areas/%s/">%s</a></li>' % (a['slug'], esc(a['name'])) for a in AREAS)
    return '''<footer>
  <div class="wrap">
    <div class="fcols">
      <div>
        <a class="brand" href="/" aria-label="Roomi Movers home"><img class="flogo" src="/images/logo-full.png" alt="Roomi Movers: We make room." width="588" height="600" loading="lazy"></a>
        <p style="margin-top:8px"><a class="ph" href="tel:{tel}">{phone}</a><br><a href="mailto:{email}">{email}</a></p>
      </div>
      <div><h2>Quick links</h2><ul><li><a href="/services/">Services</a></li><li><a href="/pricing/">Pricing</a></li><li><a href="/areas/">Service areas</a></li><li><a href="/about/">About</a></li><li><a href="/faq/">FAQ</a></li><li><a href="/contact/">Free Estimate</a></li></ul></div>
      <div><h2>Services</h2><ul>{svc}</ul></div>
      <div><h2>Service areas</h2><ul>{areas}</ul></div>
    </div>
    <p class="legal">© 2026 Roomi Movers LLC · Tampa, Florida</p>
  </div>
</footer>'''.format(tel=PHONE_TEL, phone=PHONE, email=EMAIL, svc=svc, areas=areas)


def pricing_card():
    return '''      <div class="card">
        <h2>How pricing works</h2>
        {ticks}
      </div>'''.format(ticks=ticks(PRICING))


def chips(items):
    return '<ul class="chips">' + ''.join('<li><a href="%s">%s</a></li>' % (u, esc(n)) for n, u in items) + '</ul>'


def service_page(s):
    others = [(o['short'], '/services/%s/' % o['slug']) for o in SERVICES if o is not s]
    notes = ''.join('<div><h3>%s</h3><p>%s</p></div>' % (esc(h), esc(p)) for h, p in s['notes'])
    body = '''  <section class="band">
    <div class="wrap">
      <div class="cols">
        <div class="card">
          <h2>{inc_t}</h2>
          {inc}
        </div>
        <div class="card">
          <h2>{ext_t}</h2>
          <p>{ext_i}</p>
          {ext}
        </div>
      </div>
      <div class="notes">{notes}</div>
    </div>
  </section>
  <section class="band alt">
    <div class="wrap">
      <div class="cols">
{pricing}
        <div class="card">
          <h2>Where we move</h2>
          <p>Local moves in and between these areas. Outside our area? Call us anyway.</p>
          {areas}
        </div>
      </div>
      <h2 style="margin-top:44px;font-size:clamp(24px,2.6vw,30px)">Other Roomi services</h2>
      {others}
    </div>
  </section>'''.format(inc_t=esc(s['included_title']), inc=ticks(s['included']), ext_t=esc(s['extra_title']), ext_i=esc(s['extra_intro']),
                       ext=ticks(s['extra']), notes=notes, pricing=pricing_card(),
                       areas=chips([(a['name'], '/areas/%s/' % a['slug']) for a in AREAS]), others=chips(others))
    path = '/services/%s/' % s['slug']
    ld = [
        {'@type': 'Service', 'name': s['name'], 'serviceType': s['name'], 'url': SITE + path, 'description': s['desc'], 'provider': BUSINESS_REF,
         'areaServed': [{'@type': 'City', 'name': a['name'] + ', FL'} for a in AREAS]},
        breadcrumbs_ld([('Home', '/'), ('Services', '/services/'), (s['name'], path)]),
    ]
    return path, page(path, s['title'], s['desc'], [('Home', '/'), ('Services', '/services/'), (s['name'], None)], s['h1'], s['lede'], body, ld)


def facts_html(facts):
    return '<dl class="facts">' + ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (esc(k), esc(v)) for k, v in facts) + '</dl>'


def area_page(a):
    others = [(o['name'], '/areas/%s/' % o['slug']) for o in AREAS if o is not a]
    plan = ''.join('<div><h3>%s</h3><p>%s</p></div>' % (esc(h), esc(p)) for h, p in a['plan'])
    svc = ''.join('<div class="card"><h3><a href="/services/{slug}/">{name}</a></h3><p>{lede}</p></div>'.format(
        slug=s['slug'], name=esc(s['name']), lede=esc(s['card'])) for s in SERVICES)
    body = '''  <section class="band">
    <div class="wrap">
      <div class="area-intro">
        <div class="prose">
          <h2>Moving in {name}</h2>
          {about}
        </div>
        <div class="card facts-card">
          <h2>Know before you go</h2>
          {facts}
        </div>
      </div>
      <div class="notes">{plan}</div>
      <h2 style="margin-top:48px;font-size:clamp(24px,2.6vw,30px)">Services in {name}</h2>
      <div class="services" style="margin-top:18px">{svc}</div>
    </div>
  </section>
  <section class="band alt">
    <div class="wrap">
      <div class="cols">
{pricing}
        <div class="card">
          <h2>Before moving day</h2>
          <p>A few things that make any move go faster:</p>
          {tips}
        </div>
      </div>
      <h2 style="margin-top:44px;font-size:clamp(24px,2.6vw,30px)">Other areas we serve</h2>
      {others}
    </div>
  </section>'''.format(name=esc(a['name']), about=''.join('<p>%s</p>' % esc(p) for p in a['about']), svc=svc,
                       pricing=pricing_card(), tips=ticks(AREA_TIPS), others=chips(others), facts=facts_html(a['facts']), plan=plan)
    path = '/areas/%s/' % a['slug']
    biz = dict(BUSINESS_REF, areaServed={'@type': 'Place', 'name': a['name'] + ', FL'}, address={'@type': 'PostalAddress', 'addressLocality': 'Tampa', 'addressRegion': 'FL', 'addressCountry': 'US'})
    ld = [
        {'@type': 'WebPage', 'name': a['title'], 'url': SITE + path, 'description': a['desc'], 'about': biz},
        breadcrumbs_ld([('Home', '/'), ('Service areas', '/areas/'), (a['name'], path)]),
    ]
    return path, page(path, a['title'], a['desc'], [('Home', '/'), ('Service areas', '/areas/'), (a['name'], None)], a['h1'], a['lede'], body, ld)


# ---------- top-level pages for each header tab (built from the home page's own sections) ----------
HOME = (ROOT / 'index.html').read_text(encoding='utf-8')


def home_section(sid):
    m = re.search(r'<section class="[^"]*" id="%s"[^>]*>.*?</section>' % sid, HOME, re.S)
    assert m, sid
    s = m.group(0)
    s = s.replace('src="images/', 'src="/images/').replace('srcset="images/', 'srcset="/images/').replace(', images/', ', /images/')
    s = s.replace('href="#quote"', 'href="/contact/"').replace('href="#services"', 'href="/services/"').replace('href="#areas"', 'href="/areas/"')
    return s


def hub_page(path, title, desc, crumb, h1, lede, body, extra_ld=None):
    ld = [{'@type': 'WebPage', 'name': title, 'url': SITE + path, 'description': desc, 'about': BUSINESS_REF},
          breadcrumbs_ld([('Home', '/'), (crumb, path)])] + (extra_ld or [])
    return path, page(path, title, desc, [('Home', '/'), (crumb, None)], h1, lede, body, ld)


def pricing_strip():
    return ('  <section class="band alt">\n    <div class="wrap">\n      <div class="cols">\n' + pricing_card() +
            '\n        <div class="card"><h2>Ready for your price?</h2><p>Your free estimate shows your hourly rate and how long we expect the move to take.</p>'
            '<p style="margin-top:16px"><a class="btn btn-primary" href="/contact/">Get a Free Estimate</a></p></div>\n      </div>\n    </div>\n  </section>')


def services_hub():
    cards = ''.join(
        '<article class="card"><h2><a href="/services/%s/">%s</a></h2><p>%s</p>%s<p style="margin-top:16px"><a class="btn btn-ghost" href="/services/%s/">See %s</a></p></article>'
        % (s['slug'], esc(s['name']), esc(s['lede']), ticks(s['included'][:4]), s['slug'], esc(s['short'].lower())) for s in SERVICES)
    body = ('  <section class="band">\n    <div class="wrap">\n      <div class="cols">' + cards + '</div>\n'
            '      <p class="after" style="margin-top:28px"><b>Not sure what it will take?</b> Text a photo of your big items to '
            '<a class="ph" href="sms:+18134363216">(813) 436-3216</a> and we will tell you.</p>\n    </div>\n  </section>\n' + pricing_strip())
    return hub_page('/services/', 'Moving Services in Tampa Bay | Roomi Movers',
                    'Home moves, apartment and condo moves, loading and unloading, and heavy or specialty items across Tampa, Wesley Chapel, Lutz and Carrollwood. Hourly rate, free estimate.',
                    'Services', 'Moving services for every kind of move',
                    'Four services, one hourly rate. Pick the one that fits, or tell us about your move and we will recommend it.', body)


def pricing_page():
    body = home_section('pricing') + '\n' + home_section('how')
    return hub_page('/pricing/', 'Pricing: Hourly Rate, Two-Hour Minimum | Roomi Movers',
                    'Roomi Movers bills by the hour with a two-hour minimum. Labor-only, full-service and white-glove packages, with a free estimate before you book.',
                    'Pricing', 'One hourly rate, explained up front',
                    'Every package is billed by the hour with a two-hour minimum. Your free estimate shows the rate and the time we expect, so there are no surprises on moving day.', body)


def areas_hub():
    cards = ''.join(
        '<article class="card"><h2><a href="/areas/%s/">%s</a></h2><p>%s</p>%s<p style="margin-top:16px"><a class="btn btn-ghost" href="/areas/%s/">Movers in %s</a></p></article>'
        % (a['slug'], esc(a['name']), esc(a['lede']), facts_html(a['facts'][:2]), a['slug'], esc(a['name'])) for a in AREAS)
    body = ('  <section class="band">\n    <div class="wrap">\n      <div class="cols">' + cards + '</div>\n'
            '      <p class="after" style="margin-top:28px">Outside these areas? Call us anyway at <a class="ph" href="tel:+18134363216">(813) 436-3216</a>.</p>\n    </div>\n  </section>')
    return hub_page('/areas/', 'Service Areas: Tampa, Wesley Chapel, Lutz & Carrollwood | Roomi Movers',
                    'Roomi Movers is based in Tampa and moves homes and apartments in Tampa, Wesley Chapel, Lutz and Carrollwood, FL. Hourly rate, free estimate.',
                    'Service areas', 'Proudly moving North Tampa',
                    'Based in Tampa and serving the neighborhoods around it. Choose your area for local planning notes and what to know before moving day.', body)


def about_page():
    body = home_section('about') + '\n' + home_section('reviews')
    return hub_page('/about/', 'About Roomi Movers | Family-Run Movers in Tampa',
                    'Roomi Movers is run by Kareem Aboroomi and his family in Tampa. Meet the team behind the truck and learn how we treat your home like our own.',
                    'About', 'A local, family-run moving company',
                    'Roomi Movers is run by Kareem Aboroomi and his family, right here in Tampa. When you call, you talk to the person who shows up at your door.', body)


def faq_page():
    sec = home_section('faq')
    qa = re.findall(r'<summary>(.*?)</summary><p>(.*?)</p>', sec, re.S)
    ld = [{'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': re.sub('<[^>]+>', '', q),
           'acceptedAnswer': {'@type': 'Answer', 'text': re.sub('<[^>]+>', '', a)}} for q, a in qa]}]
    return hub_page('/faq/', 'Moving FAQ: Pricing, Trucks, Booking | Roomi Movers',
                    'Answers to common questions about Roomi Movers: hourly pricing, the truck, heavy items, how far ahead to book and the areas we serve.',
                    'FAQ', 'Your questions, answered',
                    'Hourly pricing, what is included, and how to book. Do not see your question? Call or text us.', sec, ld)


def contact_page():
    path, html = hub_page('/contact/', 'Contact & Free Estimate | Roomi Movers',
                          'Request a free moving estimate from Roomi Movers, or call or text (813) 436-3216. Most estimates are back the same day.',
                          'Contact', 'Get your free estimate',
                          'Tell us about your move and Kareem will get back to you with your hourly rate and an estimate. Most estimates are back the same day.',
                          home_section('quote'))
    m = re.search(r'<script>\n/\* Quote requests\..*?</script>', HOME, re.S)
    assert m
    return path, html.replace('</body>', m.group(0) + '\n</body>')


def main():
    build_css()
    paths = ['/']
    for fn in (services_hub, pricing_page, areas_hub, about_page, faq_page, contact_page):
        path, html = fn()
        out = ROOT / path.strip('/') / 'index.html'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding='utf-8', newline='\n')
        paths.append(path)
    for builder, items in ((service_page, SERVICES), (area_page, AREAS)):
        for item in items:
            path, html = builder(item)
            out = ROOT / path.strip('/') / 'index.html'
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(html, encoding='utf-8', newline='\n')
            paths.append(path)
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(
        '  <url><loc>%s%s</loc><lastmod>%s</lastmod></url>\n' % (SITE, p, UPDATED) for p in paths) + '</urlset>\n'
    (ROOT / 'sitemap.xml').write_text(sitemap, encoding='utf-8', newline='\n')
    (ROOT / 'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n' % SITE, encoding='utf-8', newline='\n')
    print('built', len(paths), 'urls')


if __name__ == '__main__':
    main()
