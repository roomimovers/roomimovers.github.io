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
UPDATED = '2026-10-13'
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


# ---------- the other 16 areas on the Google Business Profile ----------
# Facts below were checked against each area's Wikipedia page on 2026-10-12. The planning tips are general moving advice, not claims about past jobs.
TIP = {
    'park': ('Parking and the walk to the door', 'Tell us where the truck can park and how far it is to the door. Long carries can add time, and we include them in your estimate.'),
    'gate': ('Gates and community rules', 'If your community has a gate or rules for moving trucks, check them ahead and have access codes ready for both addresses.'),
    'floor': ('Apartments and condos', 'Tell us the floor at both addresses and whether there is an elevator that needs a reservation.'),
    'between': ('Moving between areas', 'A move between cities includes the drive in your estimate, so send us both full addresses.'),
    'heavy': ('Large and heavy items', 'Gun safes, appliances and oversized furniture need the right equipment. Tell us the size and where it is going.'),
    'book': ('Choosing your day', 'Weekends and the last days of the month book first. One to two weeks ahead is ideal.'),
}
# (name, slug, county, zips, routes, landmarks, about sentence, tips)
EXTRA_AREAS = [
    ('Zephyrhills', 'zephyrhills', 'Pasco', '33541, 33542', 'US 301, SR 39 and SR 54',
     'Zephyrhills Downtown Historic District, Zephyrhills Depot Museum and Zephyrhills Municipal Airport',
     'Zephyrhills began as Abbott in 1888 and was renamed in 1910. US 301 is its main north-south road, and its downtown historic district is on the National Register of Historic Places.',
     ['park', 'between']),
    ('Brandon', 'brandon', 'Hillsborough', '33508, 33509, 33510, 33511', 'I-75, SR 60 (Brandon Boulevard) and US 301',
     'Hillsborough County Fairgrounds and Brandon Regional Library',
     'Brandon is an unincorporated community east of Tampa. I-75 passes through its western part with exits at the Selmon Expressway (SR 618) and SR 60, and SR 60 runs through the middle.',
     ['floor', 'park']),
    ('Riverview', 'riverview', 'Hillsborough', '33568, 33569, 33578, 33579', 'I-75 and US 301',
     'Alafia River and Bell Creek Nature Preserve',
     'Riverview is an unincorporated community founded in 1885 on the north shore of the Alafia River. Downtown Tampa is about 12 miles northwest via US 301 and the Selmon Expressway.',
     ['gate', 'between']),
    ('Temple Terrace', 'temple-terrace', 'Hillsborough', '33617, 33637', 'I-75 nearby',
     'Hillsborough River, Temple Terrace Golf and Country Club and Florida College',
     'Temple Terrace is a city in northeastern Hillsborough County next to Tampa, incorporated in 1925. The Hillsborough River flows through its eastern and southern parts.',
     ['floor', 'book']),
    ("Town 'n' Country", 'town-n-country', 'Hillsborough', '33615', 'Memorial Highway, Hillsborough Avenue and Waters Avenue',
     "Bay Crest Park, Rocky Creek and Sweetwater Creek",
     "Town 'n' Country is a community in western Hillsborough County, developed from 1958 to 1978 on a former dairy farm. It sits close to Tampa International Airport.",
     ['park', 'floor']),
    ('Westchase', 'westchase', 'Hillsborough', '33626', 'Neighborhood streets of the Westchase community',
     'Westchase Golf Course, West Park Village and Tampa Bay Downs',
     'Westchase is a planned community established in 1991, with a community association that governs the largest deed-restricted part of the area.',
     ['gate', 'park']),
    ('Citrus Park', 'citrus-park', 'Hillsborough', '33625', 'SR 589 (Veterans Expressway) and Gunn Highway',
     'Westfield Citrus Park and Big Cat Rescue',
     'Citrus Park is in northwestern Hillsborough County, about 15 miles northwest of Tampa, with the Veterans Expressway running north to south through it.',
     ['gate', 'between']),
    ('Valrico', 'valrico', 'Hillsborough', '33594, 33595, 33596', 'SR 60',
     'James McCabe Theater (the former Valrico Civic Center)',
     'Valrico lies on SR 60, about 14 miles east of Tampa. Its name is said to mean "rich valley", and the railway built through the area in 1890 brought new settlers.',
     ['park', 'heavy']),
    ('Seffner', 'seffner', 'Hillsborough', '33583, 33584', 'I-4 and SR 574 (Dr. Martin Luther King Jr. Boulevard)',
     'Lake Weeks and the Seffner-Mango Branch Library',
     'Seffner is about 13 miles east of downtown Tampa, with I-4 along its northern edge. Its post office opened in 1884 and was named for its first postmaster.',
     ['book', 'floor']),
    ('Gibsonton', 'gibsonton', 'Hillsborough', '33534', 'US 41 and I-75',
     "International Independent Showmen's Museum",
     'Gibsonton was founded in 1884 by James Gibson Sr. and became a wintering town for carnival and circus workers.',
     ['heavy', 'park']),
    ('Oldsmar', 'oldsmar', 'Pinellas', '34677', 'Streets around the northern tip of Tampa Bay',
     'Oldsmar Public Library and Tampa Bay Downs',
     'Oldsmar is a city on the northern tip of Tampa Bay, named for automobile pioneer Ransom E. Olds, who began the planned community in 1916.',
     ['between', 'floor']),
    ('Thonotosassa', 'thonotosassa', 'Hillsborough', '33592', 'I-4, I-75 and US 301',
     'Hillsborough River, Lake Thonotosassa and the Thonotosassa Branch Library',
     'Thonotosassa is in northeastern Hillsborough County, with I-4 along its southern edge and I-75 along its western edge. Its name is said to come from Seminole-Creek words for "flint".',
     ['park', 'heavy']),
    ('Egypt Lake-Leto', 'egypt-lake-leto', 'Hillsborough', '33614', 'Streets just north of Tampa International Airport',
     'Egypt Lake, Leto and West Park Estates',
     'Egypt Lake-Leto is about 7 miles northwest of downtown Tampa and takes in the communities of Egypt Lake, Leto and West Park Estates.',
     ['floor', 'park']),
    ("Land O' Lakes", 'land-o-lakes', 'Pasco', '33599, 34637, 34638, 34639', 'US 41, SR 52, SR 54 and the Suncoast Parkway (SR 589)',
     "Conner Preserve, Cypress Creek Preserve and the Land O' Lakes Branch Library",
     "Land O' Lakes was renamed in 1950. US 41 is its main north-south road, and the Suncoast Parkway runs along its western edge.",
     ['gate', 'book']),
    ('Dade City', 'dade-city', 'Pasco', '33523, 33525, 33526', 'US 98, US 301 and SR 52',
     'Pioneer Florida Museum, Hugh Embry Library and AdventHealth Dade City',
     'Dade City is the county seat of Pasco County, named for Major Francis L. Dade. It hosts an annual Kumquat Festival.',
     ['between', 'book']),
    ('San Antonio', 'san-antonio', 'Pasco', '33576', 'Streets in the city of San Antonio',
     'San Antonio City Hall, St. Anthony of Padua Catholic Church and Lake Jovita',
     'San Antonio is a small city in Pasco County, incorporated as a town in 1891, with the motto "Gem of the Highlands". Saint Leo University is nearby.',
     ['park', 'heavy']),
]
for _n, _s, _c, _z, _r, _l, _about, _tips in EXTRA_AREAS:
    AREAS.append({
        'slug': _s, 'name': _n, 'extra': True,
        'title': 'Movers in %s, FL | Roomi Movers' % _n,
        'desc': 'Roomi Movers serves %s in %s County (ZIP %s). Hourly rate, two-hour minimum, free estimate before you book.' % (_n, _c, _z),
        'h1': 'Movers in %s, FL' % _n,
        'lede': 'Moving in or out of %s? Roomi Movers brings the truck, wraps and pads your furniture, and sets beds back up at your new place.' % _n,
        'facts': [('County', _c), ('ZIP codes', _z), ('Main routes', _r), ('Landmarks', _l)],
        'about': [_about, 'We move people within %s and between %s and Tampa, Carrollwood, Wesley Chapel and Lutz.' % (_n, _n)],
        'plan': [TIP[k] for k in _tips],
    })


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
.cols.cols3{grid-template-columns:repeat(3,minmax(0,1fr))}
@media (max-width:860px){.cols.cols3{grid-template-columns:1fr}}
.ph-box{border:2px dashed var(--coral);border-radius:16px;padding:22px;background:#FFF8F2}
.ph-tag{font-family:var(--display);font-weight:800;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--coral-ink)}
.ph-big{font-family:var(--display);font-weight:900;font-size:36px;margin:6px 0}
.ph-big small{font-size:16px;color:var(--muted)}
.ph-stars{color:var(--coral);letter-spacing:3px;margin:6px 0}
.ph-note{color:var(--muted);font-size:14px;margin-top:10px}
.ph-h{font-size:clamp(22px,2.4vw,28px);margin-bottom:18px}
.ph-photos{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
.ph-photo{aspect-ratio:4/3;border:2px dashed var(--coral);border-radius:14px;background:#FFF8F2;display:grid;place-items:center;text-align:center;padding:14px;font-weight:700;color:var(--muted)}
.ph-chips{display:flex;flex-wrap:wrap;gap:10px}
.ph-chip{border:2px dashed var(--coral);border-radius:999px;padding:10px 18px;font-weight:800;background:#FFF8F2}
.ph-table{width:100%;border-collapse:collapse}
.ph-table th,.ph-table td{text-align:left;padding:12px 14px;border-bottom:1px solid var(--line)}
.ph-table th{font-family:var(--display);font-size:14px;letter-spacing:.06em;text-transform:uppercase;color:var(--coral-ink)}
@media (max-width:640px){.ph-photos{grid-template-columns:1fr 1fr}}
.journey.is-short.is-live{height:300vh;height:300svh}
.cols .card .btn+.btn{margin-left:6px}
.card h2 a{color:inherit;text-decoration:none}
.card h2 a:hover{color:var(--coral-ink);text-decoration:underline;text-underline-offset:3px}
.cols .card h2{font-size:clamp(22px,2.2vw,28px)}
.is-faq #faq .head,.is-contact #quote .quote-side>.eyebrow,.is-contact #quote .quote-side>h2{display:none}
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
<script src="/assets/rates.js"></script>
<script src="/assets/site.js" defer></script>
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
      <picture><source type="image/webp" srcset="/images/logo-mark-120.webp"><img src="/images/logo-mark-120.png" alt="" width="41" height="40"></picture>
      <span class="brand-word"><b>roomi</b><span>MOVERS</span></span>
    </a>
    <nav class="links" id="site-nav" aria-label="Main">
      <a href="/services/">Services</a>
      <a href="/pricing/">Pricing</a>
      <a href="/areas/">Service Areas</a>
      <a href="/about/">About</a>
      <a href="/faq/">FAQ</a>
      <a href="/resources/">Guides</a>
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
          <source type="image/webp" srcset="/images/roomi-team-v2-960.webp 960w, /images/roomi-team-v2-1672.webp 1672w" sizes="(max-width: 860px) 100vw, 520px">
          <img src="/images/roomi-team-v2-960.jpg" srcset="/images/roomi-team-v2-960.jpg 960w, /images/roomi-team-v2-1672.jpg 1672w" sizes="(max-width: 860px) 100vw, 520px" alt="Kareem Aboroomi, owner of Roomi Movers, in front of the Roomi Movers box truck" width="960" height="540">
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
    areas = ''.join('<li><a href="/areas/%s/">%s</a></li>' % (a['slug'], esc(a['name'])) for a in AREAS if not a.get('extra')) + '<li><a href="/areas/">All service areas</a></li>'
    return '''<footer>
  <div class="wrap">
    <div class="fcols">
      <div>
        <a class="brand" href="/" aria-label="Roomi Movers home"><picture><source type="image/webp" srcset="/images/logo-full-300.webp"><img class="flogo" src="/images/logo-full-300.png" alt="Roomi Movers: We make room." width="150" height="153" loading="lazy"></picture></a>
        <p style="margin-top:8px"><a class="ph" href="tel:{tel}">{phone}</a><br><a href="mailto:{email}">{email}</a></p>
      </div>
      <div><h2>Quick links</h2><ul><li><a href="/services/">Services</a></li><li><a href="/pricing/">Pricing</a></li><li><a href="/areas/">Service areas</a></li><li><a href="/about/">About</a></li><li><a href="/faq/">FAQ</a></li><li><a href="/resources/">Guides</a></li><li><a href="/contact/">Free Estimate</a></li></ul></div>
      <div><h2>Services</h2><ul>{svc}</ul></div>
      <div><h2>Service areas</h2><ul>{areas}</ul></div>
    </div>
    <p class="legal">© 2026 Roomi Movers LLC · Tampa, Florida · <a href="/privacy/">Privacy policy</a></p>
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
    quote = home_section('quote').replace('name="from">', 'name="from" value="%s, FL">' % esc(a['name']))
    quote = quote.replace('<h2 style="margin-top:12px">Tell us about your move</h2>', '<h2 style="margin-top:12px">Get a free estimate for your %s move</h2>' % esc(a['name']))
    body = body + '\n' + quote
    html = page(path, a['title'], a['desc'], [('Home', '/'), ('Service areas', '/areas/'), (a['name'], None)], a['h1'], a['lede'], body, ld)
    html = html.replace('href="/contact/">Get a Free Estimate</a>', 'href="#quote">Get a Free Estimate</a>', 1)
    m = re.search(r'<script>\n/\* Quote requests\..*?</script>', HOME, re.S)
    return path, html.replace('</body>', m.group(0) + '\n</body>')


# ---------- top-level pages for each header tab (built from the home page's own sections) ----------
# ======================= trust section, review wall and price slots (rendered into index.html from business.json) =======================
def _biz():
    return json.loads((ROOT / '_tools' / 'business.json').read_text(encoding='utf-8'))


SHIELD = ('<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" '
          'stroke-linejoin="round" aria-hidden="true"><path d="M12 2.5l8 3v6c0 5-3.4 9.2-8 10.5-4.6-1.3-8-5.5-8-10.5v-6z"/><path d="M8.5 12.2l2.4 2.4 4.6-5"/></svg>')
FDACS_URL = 'https://www.fdacs.gov/Consumer-Resources'


def license_state():
    lic = _biz().get('license') or {}
    return 'active' if (lic.get('status') == 'active' and lic.get('registration_number')) else 'pending'


def badge_text():
    b = _biz(); lic = b.get('license') or {}
    if license_state() == 'active':
        return 'Licensed &amp; Insured &middot; FDACS #%s' % esc(str(lic['registration_number']))
    return 'Licensed &amp; insured before every move'


def trust_inner():
    b = _biz(); lic = b.get('license') or {}
    if license_state() == 'active':
        head = 'Licensed and insured.'
        chips = '<div class="trust-chips"><span>Florida registered mover &middot; FDACS #%s</span>' % esc(str(lic['registration_number']))
        if lic.get('insurance_summary'):
            chips += '<span>%s</span>' % esc(lic['insurance_summary'])
        chips += '</div>'
        c1 = ('Registered with the State of Florida', 'Roomi Movers is registered with the Florida Department of Agriculture and Consumer Services (FDACS) as a household mover.')
        c2 = ('Insured for your protection', 'We carry the insurance Florida requires of movers, so your belongings are protected from the first box to the last.')
        fine = 'Registration number and coverage shown above. You can confirm any mover at FDACS.'
    else:
        head = 'Licensed and insured. Before your move, not after.'
        chips = ''
        c1 = ('Registered with the State of Florida', 'Florida requires household movers to register with the Florida Department of Agriculture and Consumer Services (FDACS). Roomi Movers registers before moving a single customer.')
        c2 = ('Insured for your protection', 'We put the insurance Florida requires of movers in place before your first move, so your belongings are protected from the first box to the last.')
        fine = 'Our registration number and coverage details are listed here as soon as they are issued, so you can check us yourself.'
    c3 = ('Check us yourself', 'You can confirm any Florida mover with FDACS at <a href="%s">fdacs.gov/Consumer-Resources</a> or by calling 1-800-HELP-FLA (435-7352).' % FDACS_URL)
    cards = ''.join('<div class="tcard"><span class="tnum">%s</span><h3>%s</h3><p>%s</p></div>' % (n, esc(t), body)
                    for n, (t, body) in zip(['1', '2', '3'], [c1, c2, c3]))
    return ('<div class="trust-head"><span class="trust-shield">%s</span><div><p class="eyebrow">Licensed and insured</p><h2 id="trust-title">%s</h2></div></div>'
            '<div class="trust-cards">%s</div>%s<p class="trust-fine">%s</p>') % (SHIELD, head, cards, chips, fine)


def review_card(r, demo=False, hidden=False):
    stars = '&#9733;' * int(r.get('rating', 5))
    src = esc(r.get('source') or 'Google')
    who = '<b>%s</b>%s<span class="rsrc">%s</span>' % (esc(r['name']), (' &middot; ' + esc(r['area'])) if r.get('area') else '', src)
    return ('<li class="rcard"%s><p class="rstars" aria-label="%d out of 5 stars">%s</p><blockquote>&ldquo;%s&rdquo;</blockquote><p class="rwho">%s</p></li>'
            % (' aria-hidden="true"' if hidden else '', int(r.get('rating', 5)), stars, esc(r['text']), who))


def reviews_wall(reviews, g_url=None, g_link=None, demo=False):
    n = len(reviews)
    avg = sum(int(r.get('rating', 5)) for r in reviews) / float(n)
    cards = ''.join(review_card(r) for r in reviews)
    dup = ''.join(review_card(r, hidden=True) for r in reviews)
    dur = max(40, n * 9)
    ctas = ''
    if g_url: ctas += '<a class="btn btn-ghost" href="%s" rel="noopener">Read all our reviews on Google</a>' % esc(g_url)
    if g_link: ctas += '<a class="btn btn-primary" href="%s" rel="noopener">Leave a review</a>' % esc(g_link)
    ctas = ('<div class="ctas" style="justify-content:center">%s</div>' % ctas) if ctas else ''
    tag = '<p class="ph-tag" style="text-align:center;margin-bottom:10px">Sample layout: not real reviews. Never shown on the live site.</p>' if demo else ''
    return ('  <section class="band alt reviews-wall" id="reviews" aria-labelledby="reviews-title">\n    <div class="wrap">\n      %s<div class="head center"><p class="eyebrow">Reviews</p>'
            '<h2 id="reviews-title">What our customers say</h2><p class="score"><span class="stars-glow" aria-hidden="true">&#9733;&#9733;&#9733;&#9733;&#9733;</span>'
            '<span>%.1f out of 5 from %d review%s</span></p></div>\n    </div>\n    <div class="marquee" role="region" aria-label="Customer reviews"><ul class="marquee-track" style="--dur:%ds">%s%s</ul></div>\n'
            '    <div class="wrap" style="margin-top:22px">%s</div>\n  </section>') % (tag, avg, n, '' if n == 1 else 's', dur, cards, dup, ctas)


def reviews_empty(g_link=None):
    star = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" aria-hidden="true">'
            '<path d="M12 2.8l2.8 5.8 6.4.9-4.6 4.5 1.1 6.4L12 17.4l-5.7 3 1.1-6.4L2.8 9.5l6.4-.9z"/></svg>')
    btn = ('<a class="btn btn-primary" href="%s" rel="noopener">Be our first review</a>' % esc(g_link)) if g_link else ''
    return ('  <section class="band alt reviews-band" id="reviews" aria-labelledby="reviews-title">\n    <div class="wrap reviews">\n      <div>\n        <p class="eyebrow">Reviews</p>\n'
            '        <h2 id="reviews-title">Our first reviews are on the way</h2>\n        <p class="reviews-note">We\'re new and family-run, so this space is saved for real reviews from the people we move.</p>\n      </div>\n'
            '      <div>\n        <p class="stars-sm">' + star * 5 + '<span>No reviews yet</span></p>\n        <div class="ctas">' + btn +
            '<a class="btn btn-ghost" href="sms:+18134363216">Text us a review</a><a class="btn btn-ghost" href="mailto:makeroom@roomimovers.com?subject=My%20Roomi%20Movers%20review">Email a review</a></div>\n'
            '      </div>\n    </div>\n  </section>')


def render_slots():
    b = _biz()
    p = ROOT / 'index.html'
    s = p.read_text(encoding='utf-8')
    badge = ('<li><span class="i">' + SHIELD.replace('width="30" height="30"', 'width="22" height="22"') + '</span>' + badge_text() + '</li>')
    trust = ('<section class="band trust-band" id="trust" aria-labelledby="trust-title">\n    <div class="wrap">' + trust_inner() + '</div>\n  </section>\n')
    revs = b.get('reviews') or []
    reviews = reviews_wall(revs, b.get('google_reviews_url'), b.get('google_review_link')) if revs else reviews_empty(b.get('google_review_link'))
    fills = {'badge-lic': badge, 'trust': trust, 'reviews': reviews + '\n'}
    for name, html in fills.items():
        s = re.sub(r'<!--slot:%s-->.*?<!--/slot:%s-->' % (re.escape(name), re.escape(name)),
                   lambda m, n=name, h=html: '<!--slot:%s-->%s<!--/slot:%s-->' % (n, h, n), s, flags=re.S)
    for pkg, rate in (b.get('rates') or {}).items():
        inner = ('<span class="price" style="font-size:30px">%s</span><span class="price-sub">Crew size and total confirmed in your free estimate</span>' % esc(rate)) if rate else \
                '<span class="price" style="font-size:30px">Billed hourly</span><span class="price-sub">Exact rate with your free estimate</span>'
        s = re.sub(r'<!--slot:price:%s-->.*?<!--/slot:price:%s-->' % (re.escape(pkg), re.escape(pkg)),
                   lambda m, n=pkg, h=inner: '<!--slot:price:%s-->%s<!--/slot:price:%s-->' % (n, h, n), s, flags=re.S)
    p.write_text(s, encoding='utf-8', newline='\n')


DEMO_REVIEWS = [
    {'name': 'Sample reviewer', 'area': 'Tampa', 'rating': 5, 'text': 'The crew showed up on time and wrapped everything. Nothing was scratched.', 'source': 'Google'},
    {'name': 'Sample reviewer', 'area': 'Lutz', 'rating': 5, 'text': 'They kept us posted all morning and left the new place spotless.', 'source': 'Google'},
    {'name': 'Sample reviewer', 'area': 'Brandon', 'rating': 5, 'text': 'Clear hourly rate up front and no surprises on the day.', 'source': 'Google'},
    {'name': 'Sample reviewer', 'area': 'Wesley Chapel', 'rating': 5, 'text': 'Careful with our gun safe and the piano. I would hire them again.', 'source': 'Google'},
    {'name': 'Sample reviewer', 'area': 'Carrollwood', 'rating': 5, 'text': 'Friendly, fast, and the owner called me himself.', 'source': 'Google'},
    {'name': 'Sample reviewer', 'area': 'Riverview', 'rating': 5, 'text': 'Best moving experience we have had.', 'source': 'Google'},
]


def sample_wall():
    return reviews_wall(DEMO_REVIEWS, None, None, demo=True)


render_slots()

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


ALL_AREAS = ["Tampa", "Carrollwood", "Wesley Chapel", "Zephyrhills", "Brandon", "Riverview", "Temple Terrace", "Town 'n' Country", "Westchase",
             "Citrus Park", "Valrico", "Seffner", "Gibsonton", "Oldsmar", "Thonotosassa", "Egypt Lake-Leto", "Lutz", "Land O' Lakes", "Dade City", "San Antonio"]


def all_area_chips():
    pages = {a['name']: a['slug'] for a in AREAS}
    return '<ul class="cities all">' + ''.join(
        ('<li><a href="/areas/%s/">%s</a></li>' % (pages[n], esc(n))) if n in pages else '<li><span>%s</span></li>' % esc(n) for n in ALL_AREAS) + '</ul>'


def areas_hub():
    cards = ''.join(
        '<article class="card"><h2><a href="/areas/%s/">%s</a></h2><p>%s</p>%s<p style="margin-top:16px"><a class="btn btn-ghost" href="/areas/%s/">Movers in %s</a></p></article>'
        % (a['slug'], esc(a['name']), esc(a['lede']), facts_html(a['facts'][:2]), a['slug'], esc(a['name'])) for a in AREAS if not a.get('extra'))
    body = ('  <section class="band">\n    <div class="wrap">\n      <div class="cols">' + cards + '</div>\n'
            '      <h2 style="margin-top:44px;font-size:clamp(24px,2.6vw,30px)">All the areas we serve</h2>'
            '<p class="after" style="margin-bottom:14px">Choose your area for local details and to request an estimate there.</p>' + all_area_chips() +
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
    path_, html_ = hub_page('/faq/', 'Moving FAQ: Pricing, Trucks, Booking | Roomi Movers',
                    'Answers to common questions about Roomi Movers: hourly pricing, the truck, heavy items, how far ahead to book and the areas we serve.',
                    'FAQ', 'Your questions, answered',
                    'Hourly pricing, what is included, and how to book. Do not see your question? Call or text us.', sec, ld)
    return path_, html_.replace('<main id="main"', '<main id="main" class="is-faq"', 1)


def contact_page():
    path, html = hub_page('/contact/', 'Contact & Free Estimate | Roomi Movers',
                          'Request a free moving estimate from Roomi Movers, or call or text (813) 436-3216. Most estimates are back the same day.',
                          'Contact', 'Get your free estimate',
                          'Tell us about your move and Kareem will get back to you with your hourly rate and an estimate. Most estimates are back the same day.',
                          home_section('quote'))
    m = re.search(r'<script>\n/\* Quote requests\..*?</script>', HOME, re.S)
    assert m
    return path, html.replace('<main id="main"', '<main id="main" class="is-contact"', 1).replace('</body>', m.group(0) + '\n</body>')


# ======================= richer tab pages, shared journey animation, privacy and 404 =======================
def sec(inner, alt=False, extra=''):
    return '  <section class="band%s"%s>\n    <div class="wrap">\n%s\n    </div>\n  </section>' % (' alt' if alt else '', extra, inner)


def cards(items, cols=2):
    return '<div class="cols%s">' % (' cols3' if cols == 3 else '') + ''.join(
        '<div class="card"><h2>%s</h2>%s</div>' % (esc(h), b) for h, b in items) + '</div>'


def para(s):
    return '<p>%s</p>' % esc(s)


def journey_parts():
    m = re.search(r'<section class="journey".*?</section>', HOME, re.S)
    assert m
    section = m.group(0).replace('<section class="journey"', '<section class="journey is-short"', 1).replace('href="#services"', 'href="#after-journey"')
    section += '\n<div id="after-journey"></div>'
    s = re.search(r'<script src="https://cdnjs[^"]*gsap\.min\.js"></script>\s*<script src="[^"]*ScrollTrigger\.min\.js"></script>\s*<script>\n/\* Scroll journey.*?</script>', HOME, re.S)
    assert s
    return section, s.group(0)


def form_script():
    m = re.search(r'<script>\n/\* Quote requests\..*?</script>', HOME, re.S)
    assert m
    return m.group(0)


def with_journey(html):
    section, scr = journey_parts()
    if 'id="quote"' not in html:
        section = section.replace('href="#quote"', 'href="/contact/"')
    i = html.index('</section>', html.index('<section class="page-hero">')) + len('</section>')
    html = html[:i] + '\n' + section + html[i:]
    return html.replace('</body>', scr + '\n</body>')


def with_journey_late(html):
    section, scr = journey_parts()
    i = html.index('</section>', html.index('id="quote"')) + len('</section>')
    html = html[:i] + '\n' + section + html[i:]
    return html.replace('</body>', scr + '\n</body>')


def with_form(html, cls=''):
    html = html.replace('</body>', form_script() + '\n</body>')
    if cls:
        html = html.replace('<main id="main"', '<main id="main" class="%s"' % cls, 1)
    return html


def _faq_items_v1():
    return [
        ('How much does a move cost?', 'We charge by the hour with a two-hour minimum. Your total depends on home size, stairs, distance and heavy items. Get a free estimate and we will give you your hourly rate, the time we expect it to take, and any extra charges before you book.'),
        ('What does the two-hour minimum mean?', 'Every move is billed for at least two hours. The clock starts when we arrive and stops when the last item is placed.'),
        ('What can add to the price?', 'Stairs, long carries from the truck to the door, and items over 300 lbs, like gun safes, may add to the price. We tell you before you book.'),
        ('How fast will I get my estimate?', 'Most estimates are back the same day. Kareem calls you with your hourly rate and the time we expect the move to take.'),
        ('What are the packages?', 'Labor Only is two movers loading or unloading your own truck, container or storage unit. Full-Service adds the box truck, wrapped and padded furniture, and beds taken apart and set up. White-Glove adds floor runners and door-frame guards, boxed TVs, art and mirrors, furniture placed room by room, and an extra crew member.'),
        ('Do you bring the truck?', 'Yes. The box truck, moving blankets, stretch wrap, dollies and straps are included with a full-service move. Need help with your own rental truck instead? Choose labor only.'),
        ('Do you protect floors and door frames?', 'Floor runners and door-frame guards are part of the White-Glove package. On every full-service move your furniture is wrapped and padded.'),
        ('Will you take my bed apart and set it back up?', 'Yes. Beds are taken apart and set back up on full-service moves.'),
        ('Can you move a gun safe or appliances?', 'Yes. Tell us the size and where it is going (garage, upstairs, etc.) so we bring the right equipment. Items over 300 lbs may add to the price.'),
        ('Do you move apartments and condos?', 'Yes, from studios to three bedrooms, including walk-ups and elevator buildings. Tell us the floor and elevator situation at both addresses when you request your estimate.'),
        ('What are your hours?', 'Our hours are ' + BUSINESS['hours'] + '. Call or text (813) 436-3216, or send an estimate request any time.'),
        ('How big is the arrival window?', 'A two-hour arrival window, and we keep you posted on timing so you are not waiting around all day.'),
        ('How far ahead should I book?', 'One to two weeks is ideal. Weekends and the last few days of the month book first, so reach out early if your date is fixed.'),
        ('Is there a launch offer?', 'Yes: $50 off moves booked by Dec 31, 2026.'),
        ('Which areas do you serve?', 'Tampa, Carrollwood, Wesley Chapel and Lutz, plus Brandon, Riverview, Temple Terrace, Westchase, Zephyrhills and the other areas on our service areas page. If you are close by, call us anyway.'),
    ]


def faq_details(items, open_first=True):
    return ''.join('<details%s><summary>%s</summary><p>%s</p></details>' % (' open' if i == 0 and open_first else '', esc(q), esc(a)) for i, (q, a) in enumerate(items))


def services_hub():
    svc = ''.join(
        '<article class="card"><h2><a href="/services/%s/">%s</a></h2><p>%s</p>%s<p style="margin-top:16px"><a class="btn btn-ghost" href="/services/%s/">See %s</a></p></article>'
        % (s['slug'], esc(s['name']), esc(s['lede']), ticks(s['included'][:4]), s['slug'], esc(s['short'].lower())) for s in SERVICES)
    b = sec('<div class="cols">' + svc + '</div>\n<p class="after" style="margin-top:28px"><b>Not sure what it will take?</b> Text a photo of your big items to <a class="ph" href="sms:+18134363216">(813) 436-3216</a> and we will tell you.</p>')
    b += '\n' + sec('<h2 style="font-size:clamp(26px,3vw,36px)">What comes with a full-service move</h2>' + cards([
        ('On the truck', ticks(['Box truck, moving blankets, stretch wrap, dollies and straps', 'Furniture wrapped and padded', 'Beds taken apart and set back up', 'Loaded tight so nothing shifts on the drive'])),
        ('Three ways to book', '<p>Choose the level of help that fits your move. Every package is billed by the hour with a two-hour minimum.</p>' + ticks(['Labor Only: two movers for your own truck, container or storage unit', 'Full-Service: the truck and crew for apartments and homes', 'White-Glove: extra protection and an extra crew member']) + '<p style="margin-top:16px"><a class="btn btn-ghost" href="/pricing/">Compare packages and pricing</a></p>'),
    ]), alt=True)
    b += '\n' + home_section('how')
    b += '\n' + sec('<h2 style="font-size:clamp(26px,3vw,36px)">Quick answers</h2><div class="faq" style="margin-top:20px">' + faq_details([faq_items()[i] for i in (0, 5, 8)]) + '</div><p class="after" style="margin-top:20px"><a href="/faq/">See all questions</a></p>', alt=True)
    b += '\n' + sec('<h2 style="font-size:clamp(26px,3vw,36px)">Where we move</h2><p class="after">Local moves across Tampa Bay.</p>' + all_area_chips())
    p, html = hub_page('/services/', 'Moving Services in Tampa Bay | Roomi Movers',
                       'Home moves, apartment and condo moves, loading and unloading, and heavy or specialty items across Tampa, Wesley Chapel, Lutz and Carrollwood. Hourly rate, free estimate.',
                       'Services', 'Moving services for every kind of move',
                       'Four services, one hourly rate. Pick the one that fits, or tell us about your move and we will recommend it.', b)
    return p, with_journey(html)


def pricing_page():
    b = home_section('pricing')
    b += '\n' + sec('<h2 style="font-size:clamp(26px,3vw,36px)">How the clock works</h2><ol class="steps" style="margin-top:24px">'
                    '<li><h3>We arrive</h3><p>The clock starts when we arrive. You get a two-hour arrival window and updates on timing.</p></li>'
                    '<li><h3>We wrap, load and move</h3><p>We walk through with you, wrap and pad your furniture and get everything where it needs to go.</p></li>'
                    '<li><h3>The last item is placed</h3><p>The clock stops when the last item is placed. There is a two-hour minimum on every move.</p></li></ol>', alt=True)
    b += '\n' + sec('<h2 style="font-size:clamp(26px,3vw,36px)">What changes your total</h2>' + cards([
        ('Home size and stairs', para('A larger home takes more time, and stairs slow every trip. Tell us the rooms and the floors at both addresses.')),
        ('Distance and long carries', para('The drive and the walk from the truck to your door both count. Tell us how far the truck will be from the door.')),
        ('Heavy items', para('Items over 300 lbs, like gun safes, may add to the price. Send us the size and where it is going.')),
        ('Package', para('Labor Only, Full-Service and White-Glove include different help, so choose the one that fits your move.')),
    ]))
    b += '\n' + sec('<div class="cols"><div class="card"><h2>Get the most accurate estimate</h2>' + ticks(['The number of rooms or your home size', 'Stairs and elevators at both addresses', 'Big or heavy items, with a photo texted to (813) 436-3216', 'Your move date']) +
                    '<p style="margin-top:18px"><a class="btn btn-primary" href="/contact/">Get a Free Estimate</a></p></div>'
                    '<div class="card"><h2>Launch special</h2><p><b>$50 off moves booked by Dec 31, 2026.</b></p></div></div>', alt=True)
    b += '\n' + home_section('how')
    p, html = hub_page('/pricing/', 'Pricing: Hourly Rate, Two-Hour Minimum | Roomi Movers',
                       'Roomi Movers bills by the hour with a two-hour minimum. Labor-only, full-service and white-glove packages, with a free estimate before you book.',
                       'Pricing', 'One hourly rate, explained up front',
                       'Every package is billed by the hour with a two-hour minimum. Your free estimate shows the rate and the time we expect, so there are no surprises on moving day.', b)
    return p, with_journey(html)


def areas_hub():
    core = [a for a in AREAS if not a.get('extra')]
    crd = ''.join(
        '<article class="card"><h2><a href="/areas/%s/">%s</a></h2><p>%s</p>%s<p style="margin-top:16px"><a class="btn btn-ghost" href="/areas/%s/">Movers in %s</a></p></article>'
        % (a['slug'], esc(a['name']), esc(a['lede']), facts_html(a['facts'][:2]), a['slug'], esc(a['name'])) for a in core)
    b = sec('<div class="cols">' + crd + '</div>')
    b += '\n' + sec('<h2 style="font-size:clamp(26px,3vw,36px)">All the areas we serve</h2><p class="after" style="margin-bottom:14px">Choose your area for local details and to request an estimate there.</p>' + all_area_chips() +
                    '<p class="after" style="margin-top:24px">Outside these areas? Call us anyway at <a class="ph" href="tel:+18134363216">(813) 436-3216</a>.</p>', alt=True)
    b += '\n' + sec('<h2 style="font-size:clamp(26px,3vw,36px)">In every area</h2>' + cards([
        ('What you get', ticks(['A free estimate with your hourly rate and expected time', 'A two-hour arrival window, with updates on timing', 'Furniture wrapped and padded on full-service moves', 'The new place left clean'])),
        ('How to start', '<p>Pick your area above and use the form on its page, or call or text <a class="ph" href="tel:+18134363216">(813) 436-3216</a>. Most estimates are back the same day.</p>'),
    ]))
    b += '\n' + home_section('quote').replace('Tell us about your move', 'Get a free estimate for your area')
    p, html = hub_page('/areas/', 'Service Areas: Tampa, Wesley Chapel, Lutz & Carrollwood | Roomi Movers',
                       'Roomi Movers is based in Tampa and moves homes and apartments in Tampa, Wesley Chapel, Lutz, Carrollwood and 16 nearby areas. Hourly rate, free estimate.',
                       'Service areas', 'Proudly moving Tampa Bay',
                       'Based in Tampa and serving the areas around it. Choose your area for local planning notes and what to know before moving day.', b)
    return p, with_journey(with_form(html))


def about_page():
    b = home_section('about')
    b += '\n' + sec('<h2 style="font-size:clamp(26px,3vw,36px)">What you can count on</h2>' + cards([
        ('A clear hourly rate', para('You get your rate and the time we expect before you book, with any extra charges named up front.')),
        ('A two-hour arrival window', para('We keep you posted on timing so you are not waiting around all day.')),
        ('Furniture wrapped and padded', para('We treat your home like our own, with your furniture wrapped and the load packed tight so nothing shifts.')),
        ('The new place left clean', para('Beds set back up, every piece in place, and the new place left clean.')),
    ]), alt=True)
    b += '\n' + home_section('reviews')
    p, html = hub_page('/about/', 'About Roomi Movers | Family-Run Movers in Tampa',
                       'Roomi Movers is run by Kareem Aboroomi and his family in Tampa. Meet the team behind the truck and learn how we treat your home like our own.',
                       'About', 'A local, family-run moving company',
                       'Roomi Movers is run by Kareem Aboroomi and his family, right here in Tampa. When you call, you talk to the person who shows up at your door.', b)
    return p, with_journey(html)


def faq_page():
    items = faq_items()
    ld = [{'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in items]}]
    b = sec('<div class="faq">' + faq_details(items) + '</div>')
    b += '\n' + sec('<div class="cols"><div class="card"><h2>Still have a question?</h2><p>Call or text Kareem and get a straight answer.</p><p style="margin-top:16px">'
                    '<a class="btn btn-primary" href="tel:+18134363216">Call (813) 436-3216</a> <a class="btn btn-ghost" href="sms:+18134363216">Text us</a></p></div>'
                    '<div class="card"><h2>Ready for your price?</h2><p>Your free estimate shows your hourly rate and the time we expect.</p><p style="margin-top:16px"><a class="btn btn-ghost" href="/contact/">Get a Free Estimate</a></p></div></div>', alt=True)
    p, html = hub_page('/faq/', 'Moving FAQ: Pricing, Trucks, Booking | Roomi Movers',
                       'Answers to common questions about Roomi Movers: hourly pricing, the two-hour minimum, the truck, packages, heavy items, booking and the areas we serve.',
                       'FAQ', 'Your questions, answered',
                       'Hourly pricing, what is included, and how to book. Do not see your question? Call or text us.', b, ld)
    return p, with_journey(html)


def contact_page():
    b = home_section('quote')
    b += '\n' + sec('<div class="cols"><div class="card"><h2>Other ways to reach us</h2>' + ticks(['Call (813) 436-3216', 'Text a photo of your big items to (813) 436-3216', 'Email makeroom@roomimovers.com', 'Hours: ' + BUSINESS['hours']]) +
                    '<p style="margin-top:16px"><a class="btn btn-ghost" href="tel:+18134363216">Call now</a> <a class="btn btn-ghost" href="sms:+18134363216">Text us</a></p></div>'
                    '<div class="card"><h2>What happens next</h2><ol class="steps" style="margin-top:12px;grid-template-columns:1fr">'
                    '<li><h3>We review your request</h3><p>Kareem looks at your rooms, stairs and big items.</p></li>'
                    '<li><h3>You get your estimate</h3><p>He calls with your hourly rate and the time we expect. Most estimates are back the same day.</p></li>'
                    '<li><h3>You lock in your date</h3><p>We confirm your rate, crew size and a two-hour arrival window.</p></li></ol></div></div>', alt=True)
    p, html = hub_page('/contact/', 'Contact & Free Estimate | Roomi Movers',
                       'Request a free moving estimate from Roomi Movers, or call or text (813) 436-3216. Most estimates are back the same day.',
                       'Contact', 'Get your free estimate',
                       'Tell us about your move and Kareem will get back to you with your hourly rate and an estimate. Most estimates are back the same day.', b)
    return p, with_journey_late(with_form(html, 'is-contact'))


def privacy_page():
    b = sec('<div class="prose">'
            '<h2>What we collect</h2><p>When you request an estimate we collect the details you type into the form: your name, phone number, move date, home size, the cities or ZIP codes you are moving from and to, and any notes about stairs or heavy items.</p>'
            '<h2 style="margin-top:28px">How we use it</h2><p>We use it to call you with your estimate and to plan your move. We do not sell your information.</p>'
            '<h2 style="margin-top:28px">Who handles it</h2><p>Estimate requests are sent from this website to Roomi Movers through FormSubmit, a form-delivery service that emails each request to us. Calls and texts to (813) 436-3216 are handled by Roomi Movers directly.</p>'
            '<h2 style="margin-top:28px">Your choices</h2><p>To ask us to delete your request, call or text (813) 436-3216 or email makeroom@roomimovers.com.</p>'
            '<p style="margin-top:28px;color:var(--muted)">Last updated October 2026.</p></div>')
    return hub_page('/privacy/', 'Privacy Policy | Roomi Movers',
                    'How Roomi Movers uses the details you share when you request a moving estimate.',
                    'Privacy', 'Privacy policy', 'How we handle the details you share when you request an estimate.', b)


def notfound_page():
    b = sec('<div class="card" style="max-width:640px"><h2>That page does not exist</h2><p>The page you were looking for may have moved. Try one of these instead.</p>'
            '<p style="margin-top:16px"><a class="btn btn-primary" href="/">Go to the home page</a> <a class="btn btn-ghost" href="/services/">See services</a> <a class="btn btn-ghost" href="/contact/">Get a free estimate</a></p></div>')
    p, html = hub_page('/404.html', 'Page not found | Roomi Movers', 'Page not found.', 'Page not found', 'Page not found', 'Let us get you back on the road.', b)
    return p, html.replace('<meta name="viewport"', '<meta name="robots" content="noindex">\n<meta name="viewport"', 1)


# ======================= guides, tools, and page-specific modules =======================
def nophoto(html):
    html = re.sub(r'<figure class="page-photo">.*?</figure>', '', html, flags=re.S)
    return html.replace('<section class="page-hero">', '<section class="page-hero no-photo">', 1)


def glance():
    items = [('20', 'areas served'), ('4', 'moving services'), ('3', 'packages'), ('2-hour', 'arrival window')]
    return '<div class="glance">' + ''.join('<div><b>%s</b><span>%s</span></div>' % (n, l) for n, l in items) + '</div>'


def after_journey(html, block):
    return html.replace('<div id="after-journey"></div>', '<div id="after-journey"></div>\n' + block, 1)


def radio(name, value, label):
    return '<label class="opt"><input type="radio" name="%s" value="%s"> <span>%s</span></label>' % (name, value, esc(label))


def check(name, value, label):
    return '<label class="opt"><input type="checkbox" name="%s" value="%s"> <span>%s</span></label>' % (name, value, esc(label))


def finder_block():
    return sec('''<div class="finder-wrap">
        <div>
          <p class="eyebrow">Package finder</p>
          <h2 style="margin-top:12px;font-size:clamp(26px,3vw,38px)">Which package fits your move?</h2>
          <p class="lede-sm">Answer a few quick questions. We will point you to the right package and tell you what to share for an accurate estimate.</p>
        </div>
        <div class="finder card" data-finder>
          <fieldset><legend>Do you already have a truck, container or storage unit to load or unload?</legend>%s%s</fieldset>
          <fieldset data-needs-truck hidden><legend>How big is the home?</legend>%s%s%s%s%s</fieldset>
          <fieldset data-needs-care hidden><legend>What matters most?</legend>%s%s</fieldset>
          <fieldset><legend>Anything we should plan for? <span class="opt-note">(optional)</span></legend>%s%s%s</fieldset>
          <div class="finder-result" aria-live="polite" hidden></div>
        </div>
      </div>''' % (
        radio('truck', 'yes', 'Yes, I have my own'), radio('truck', 'no', 'No, I need the truck too'),
        radio('size', 'studio', 'Studio or 1 bedroom'), radio('size', 'two', '2 bedrooms'), radio('size', 'three', '3 bedrooms'), radio('size', 'four', '4 or more bedrooms'), radio('size', 'few', 'Just a few items'),
        radio('care', 'care', 'Furniture wrapped and padded, beds set back up'), radio('care', 'protect', 'Extra protection for floors, TVs, art and mirrors'),
        check('flag', 'stairs', 'Stairs or an elevator'), check('flag', 'heavy', 'A heavy item over 300 lbs, like a gun safe'), check('flag', 'tight', 'A long walk from the truck or tight doorways')))


_pricing_v2 = pricing_page


def pricing_page():
    p, html = _pricing_v2()
    return p, after_journey(html, finder_block())


_faq_v2 = faq_page


def faq_page():
    p, html = _faq_v2()
    search = sec('<label class="search">Search the questions<input type="search" data-faq-search placeholder="Try: stairs, truck, minimum, safe" autocomplete="off"></label>'
                 '<p class="after" data-faq-empty hidden>No match. Call or text us at <a class="ph" href="tel:+18134363216">(813) 436-3216</a> and we will answer it.</p>')
    return p, after_journey(html, search)


_areas_v2 = areas_hub


def areas_hub():
    p, html = _areas_v2()
    html = html.replace('<ul class="cities all">',
                        '<label class="search" style="max-width:420px;margin:6px 0 18px">Find your area<input type="search" data-area-filter placeholder="Type your city" autocomplete="off"></label>'
                        '<p class="after" data-area-msg hidden>Not on the list? Call us anyway at <a class="ph" href="tel:+18134363216">(813) 436-3216</a>.</p>'
                        '<ul class="cities all">', 1)
    return p, after_journey(html, sec(glance()))


_services_v2 = services_hub


def services_hub():
    p, html = _services_v2()
    return p, after_journey(html, sec(glance()))


_about_v2 = about_page


def about_page():
    p, html = _about_v2()
    return p, after_journey(nophoto(html), sec(glance()))


# ---------- the guides ----------
def gh(t):
    return '<h2 style="margin-top:32px">%s</h2>' % esc(t)


def gp(t):
    return '<p>%s</p>' % esc(t)


def gl(items):
    return '<ul class="ticks">' + ''.join('<li>%s</li>' % esc(i) for i in items) + '</ul>'


GUIDES = [
    {
        'slug': 'how-hourly-moving-pricing-works', 'short': 'How hourly pricing works', 'tag': 'Pricing',
        'title': 'How Hourly Moving Pricing Works | Roomi Movers',
        'desc': 'What the clock counts, what makes a move take longer, and how to keep your hourly total down, explained by Roomi Movers in Tampa.',
        'h1': 'How hourly moving pricing works',
        'lede': 'An hourly rate is easy to understand once you know what the clock counts. Here is how it works, what changes the total, and how to keep it down.',
        'body': (gh('What the clock counts') +
                 gp('At Roomi Movers the clock starts when we arrive and stops when the last item is placed. Every move has a two-hour minimum.') +
                 gh('Your estimate has three parts') +
                 gl(['Your hourly rate for the package you choose', 'The time we expect the move to take, based on what you tell us', 'Any extra charges, named before you book']) +
                 gp('The more accurate your answers, the closer the estimate. That is why we ask about rooms, stairs and big items.') +
                 gh('What makes a move take longer') +
                 gl(['Stairs, at either address', 'A long walk from the truck to the door', 'Boxes that are not packed or labeled when we arrive', 'Large furniture that has to come apart', 'Heavy items, such as gun safes, appliances and treadmills', 'Blocked pathways, or parking far from the door']) +
                 gh('How to keep your total down') +
                 gl(['Be packed before we arrive, with every box taped and labeled', 'Clear the pathways and keep the truck close to the door', 'Tell us about stairs, elevators and heavy items when you ask for your estimate', 'Decide where larger furniture will go before moving day']) +
                 gh('Extra charges we name up front') +
                 gp('Stairs, long carries from the truck and items over 300 lbs, like gun safes, may add to the price. We tell you before you book, so nothing is a surprise on moving day.') +
                 gh('Packages') +
                 gp('Labor Only is two movers for your own truck, container or storage unit. Full-Service adds the box truck, wrapped and padded furniture, and beds taken apart and set back up. White-Glove adds floor runners and door-frame guards, boxed TVs, art and mirrors, furniture placed room by room, and an extra crew member.')),
        'related': ['moving-day-preparation', 'moving-checklist'],
    },
    {
        'slug': 'moving-day-preparation', 'short': 'Moving day preparation', 'tag': 'Moving day',
        'title': 'How to Prepare for Moving Day | Roomi Movers',
        'desc': 'A simple guide to getting ready for the movers: parking, pathways, elevators, valuables and what to have on hand. From Roomi Movers in Tampa.',
        'h1': 'How to get ready for moving day',
        'lede': 'A little preparation makes moving day faster and calmer. Here is what to do before the truck arrives.',
        'body': (gh('The day before') +
                 gl(['Finish packing and tape every box', 'Label each box with its room and contents', 'Pack an essentials bag with chargers, medications, toiletries and a change of clothes', 'Set aside documents, jewelry and other valuables to carry yourself']) +
                 gh('Make room for the truck') +
                 gp('Save a parking spot close to the door if you can. If you live in an apartment or condo, reserve the elevator or loading area if your building requires it, and ask about move-in hours.') +
                 gh('Clear the way') +
                 gl(['Move cars, bikes and boxes out of driveways and hallways', 'Keep pets and small children in a safe room', 'Open gates and have access codes ready for both addresses']) +
                 gh('Appliances and electronics') +
                 gl(['Empty and defrost the fridge and freezer ahead of time', 'Disconnect and drain washer hoses', 'Take a photo of how cables are connected before you unplug them']) +
                 gh('When we arrive') +
                 gl(['Walk through with us and point out fragile or high-value items', 'Tell us where each room at the new place is', 'Keep your essentials bag with you']) +
                 gh('Before we leave') +
                 gp('Do a last walk through every room, closet and cabinet, and check that everything has been placed where you want it.')),
        'related': ['moving-checklist', 'packing-guide'],
    },
    {
        'slug': 'packing-guide', 'short': 'Packing guide', 'tag': 'Packing',
        'title': 'Packing Guide: How to Pack for a Move | Roomi Movers',
        'desc': 'Simple packing tips from a local Tampa moving company: boxes, heavy items, fragile things, clothing, electronics and labels.',
        'h1': 'A simple guide to packing',
        'lede': 'Good packing keeps your things safe and keeps your move moving. Start early and go room by room.',
        'body': (gh('Gather supplies') +
                 gl(['Sturdy boxes in a few sizes', 'Packing paper or bubble wrap for fragile items', 'Strong tape and a marker', 'Bags or covers for mattresses']) +
                 gh('Pack room by room') +
                 gp('Start with the rooms you use least. Keep every room in its own boxes so unpacking is quick.') +
                 gh('Heavy things in small boxes') +
                 gp('Books and tools go in small boxes. Lighter items, like linens and pillows, go in larger ones. A box you can lift comfortably is easier and safer to carry.') +
                 gh('Wrap the fragile things') +
                 gl(['Wrap dishes one at a time and stand plates on their edges', 'Fill empty space so nothing shifts', 'Mark the box FRAGILE on the top and sides']) +
                 gh('Clothes, art and electronics') +
                 gl(['Leave clothes on hangers in wardrobe boxes or garment bags if you can', 'Keep TVs, art and mirrors upright, wrapped and protected', 'Photograph cable setups before unplugging']) +
                 gh('Label everything') +
                 gp('Write the room and a short list of contents on two sides of each box, and number them so you can tell that every box arrived.') +
                 gh('Do not pack') +
                 gp('Keep flammables, cleaning chemicals and other hazardous materials out of the truck, and carry important papers, medications and valuables with you.') +
                 gh('Want help?') +
                 gp('On a full-service move we wrap and pad your furniture and take beds apart and set them back up. Tell us what is packed and what is not when you request your estimate.')),
        'related': ['moving-day-preparation', 'moving-checklist'],
    },
    {
        'slug': 'moving-heavy-items', 'short': 'Moving heavy items', 'tag': 'Heavy items',
        'title': 'Moving Gun Safes, Appliances & Heavy Items | Roomi Movers',
        'desc': 'How to prepare a gun safe, washer, dryer, fridge or treadmill for a move, and what to tell your movers. From Roomi Movers in Tampa.',
        'h1': 'Moving gun safes, appliances and other heavy items',
        'lede': 'Heavy items need a plan and the right equipment. Here is how to prepare, and what to tell us so we bring what the job needs.',
        'body': (gh('Tell us three things') +
                 gl(['What it is and how large it is, with a photo if you can', 'About how much it weighs', 'Where it is going: garage, upstairs, a tight hallway']) +
                 gp('Items over 300 lbs, like gun safes, may add to the price. We tell you before you book.') +
                 gh('Measure first') +
                 gp('Measure the item, the doorways, the hallways and the stairs at both addresses. A piece that does not fit through a doorway cannot be moved through it.') +
                 gh('Gun safes') +
                 gl(['Empty the safe before the move and carry its contents yourself', 'Make sure the path from the safe to the truck is clear', 'Tell us the weight and where it is going']) +
                 gh('Washers, dryers and refrigerators') +
                 gl(['Disconnect the water, power and drain lines ahead of time', 'Empty and defrost the fridge and freezer the day before', 'Secure or remove loose shelves and drawers']) +
                 gh('Treadmills and exercise equipment') +
                 gl(['Unplug and fold or lower the equipment if it is designed to', 'Remove loose parts and keep screws in a labeled bag']) +
                 gh('Oversized furniture') +
                 gp('Take note of any piece that may need to come apart, and tell us which one. On full-service moves, beds are taken apart and set back up.')),
        'related': ['how-hourly-moving-pricing-works', 'moving-day-preparation'],
    },
]
CHECKLIST = [
    ('6 to 8 weeks before', ['Set your move date and book your movers', 'Decide what to keep, donate or sell', 'Start collecting boxes, tape and packing paper', 'Measure large furniture and the doorways and stairs at your new place']),
    ('4 weeks before', ['Start packing the rooms you use least', 'Request time off for moving day if you need it', 'Reserve the elevator or loading area if your building requires it', 'Tell your landlord or building manager your move-out date']),
    ('2 weeks before', ['Change your address with USPS and update banks, insurance and subscriptions', 'Schedule power, water and internet at your new place for move-in day', 'Arrange care for pets and children for moving day', 'Text photos of large or heavy items to (813) 436-3216 for an accurate estimate']),
    ('1 week before', ['Confirm your arrival window with us', 'Pack everything except daily essentials', 'Empty and defrost the fridge and freezer, and drain washer hoses', 'Label every box with its room and contents', 'Set aside documents, medications and valuables to carry yourself']),
    ('The day before', ['Pack an essentials bag with chargers, medications, toiletries and a change of clothes', 'Photograph cable setups before you unplug electronics', 'Clear pathways and save parking close to the door']),
    ('Moving day', ['Walk through with the crew and point out fragile items', 'Tell the crew where each room is at the new place', 'Do a last walk through every room, closet and cabinet', 'Keep your essentials bag with you']),
    ('After the move', ['Unpack the essentials first', 'Update the address on your driver license and vehicle registration', 'Call us promptly if anything needs attention']),
]


def guide_cards(slugs):
    return ''.join('<a class="gcard" href="/resources/%s/"><span class="gtag">%s</span><b>%s</b><span>%s</span></a>' % (
        g['slug'], esc(g['tag']), esc(g['short']), esc(g['lede'])) for g in GUIDES if g['slug'] in slugs)


def guide_page(g):
    path = '/resources/%s/' % g['slug']
    related = ''.join('<li><a href="/resources/%s/">%s</a></li>' % (s, esc(t)) for s, t in
                      [(x['slug'], x['short']) for x in GUIDES if x['slug'] in g['related']] + ([('moving-checklist', 'Printable moving checklist')] if 'moving-checklist' in g['related'] else []))
    aside = ('<aside class="card guide-aside"><h2>Need a hand?</h2><p>Get your hourly rate and an estimate, free.</p>'
             '<p style="margin-top:14px"><a class="btn btn-primary" href="/contact/">Get a Free Estimate</a></p>'
             '<p style="margin-top:12px">or call <a class="ph" href="tel:+18134363216">(813) 436-3216</a></p>'
             '<h3 style="margin-top:22px">Keep reading</h3><ul class="plain">%s</ul></aside>' % related)
    b = sec('<div class="guide"><article class="prose">%s</article>%s</div>' % (g['body'], aside))
    ld = [{'@type': 'Article', 'headline': g['h1'], 'description': g['desc'], 'url': SITE + path, 'datePublished': '2026-10-13', 'dateModified': '2026-10-13',
           'author': BUSINESS_REF, 'publisher': BUSINESS_REF}]
    p, html = hub_page(path, g['title'], g['desc'], g['short'], g['h1'], g['lede'], b, ld)
    html = html.replace('<li><a href="/resources/">Guides</a></li>', '')
    html = html.replace('<li aria-current="page">%s</li>' % esc(g['short']), '<li><a href="/resources/">Guides</a></li><li aria-current="page">%s</li>' % esc(g['short']), 1)
    return p, nophoto(html)


def checklist_page():
    secs = ''
    for title, items in CHECKLIST:
        secs += '<section class="chk-sec"><h2>%s</h2>%s</section>' % (esc(title), ''.join('<label class="chk"><input type="checkbox"> <span>%s</span></label>' % esc(i) for i in items))
    b = sec('<div class="chk-top"><div><p data-progress class="chk-count">0 of 0 done</p><div class="chk-bar"><i data-bar></i></div></div>'
            '<div class="chk-actions"><button type="button" class="btn btn-ghost" data-print>Print</button><button type="button" class="btn btn-ghost" data-reset>Clear</button></div></div>'
            '<div class="checklist" data-checklist="moving">' + secs + '</div>'
            '<p class="after" style="margin-top:28px">Your ticks are saved on this device only. Ready for your estimate? <a href="/contact/">Request one here</a>.</p>')
    path = '/resources/moving-checklist/'
    ld = [{'@type': 'Article', 'headline': 'Moving checklist', 'description': 'A printable moving checklist from Roomi Movers.', 'url': SITE + path,
           'datePublished': '2026-10-13', 'dateModified': '2026-10-13', 'author': BUSINESS_REF, 'publisher': BUSINESS_REF}]
    p, html = hub_page(path, 'Moving Checklist: What to Do and When | Roomi Movers',
                       'A printable moving checklist from Roomi Movers: what to do 6 to 8 weeks out, the week before, moving day and after, with your progress saved on this device.',
                       'Moving checklist', 'Your moving checklist',
                       'From six weeks out to the day after. Tick things off as you go and print it if you like.', b, ld)
    html = html.replace('<li aria-current="page">Moving checklist</li>', '<li><a href="/resources/">Guides</a></li><li aria-current="page">Moving checklist</li>', 1)
    return p, nophoto(html)


def resources_hub():
    cards = ('<a class="gcard gcard-main" href="/resources/moving-checklist/"><span class="gtag">Checklist</span><b>Printable moving checklist</b>'
             '<span>From six weeks out to the day after, with your progress saved on this device.</span></a>' + guide_cards([g['slug'] for g in GUIDES]))
    b = sec('<div class="gcards">' + cards + '</div>')
    b += '\n' + sec('<div class="cols"><div class="card"><h2>Ready for your estimate?</h2><p>Tell us about your move and Kareem will call with your hourly rate and the time we expect. Most estimates are back the same day.</p>'
                    '<p style="margin-top:16px"><a class="btn btn-primary" href="/contact/">Get a Free Estimate</a></p></div>'
                    '<div class="card"><h2>Have a question that is not here?</h2><p>Call or text us and ask. We will answer it, and it might become a guide.</p>'
                    '<p style="margin-top:16px"><a class="btn btn-ghost" href="tel:+18134363216">Call (813) 436-3216</a> <a class="btn btn-ghost" href="/faq/">Read the FAQ</a></p></div></div>', alt=True)
    p, html = hub_page('/resources/', 'Moving Guides & Checklist | Roomi Movers',
                       'Free moving guides from Roomi Movers in Tampa: a printable checklist, how hourly pricing works, moving day preparation, packing and heavy items.',
                       'Guides', 'Moving guides and tools',
                       'Plain-English help from a local moving company: a printable checklist, how hourly pricing works, and what to do before the truck arrives.', b)
    return p, nophoto(html)


# ---------- final pass: each page gets its own hero identity and related guides ----------
HERO_FIXED = {
    '/services/': ('What we move', True), '/pricing/': ('Pricing', True), '/areas/': ('Where we move', True),
    '/about/': ('About Roomi Movers', True), '/faq/': ('FAQ', True), '/contact/': ('Contact', False),
    '/privacy/': ('Legal', False), '/resources/': ('Moving guides', False), '/resources/moving-checklist/': ('Tool: checklist', False),
}
GUIDES_FOR = {
    '/services/home-moves/': ['moving-checklist', 'packing-guide', 'moving-day-preparation'],
    '/services/apartment-condo-moves/': ['moving-day-preparation', 'moving-checklist', 'how-hourly-moving-pricing-works'],
    '/services/loading-unloading/': ['how-hourly-moving-pricing-works', 'moving-day-preparation', 'packing-guide'],
    '/services/heavy-specialty-items/': ['moving-heavy-items', 'how-hourly-moving-pricing-works', 'moving-day-preparation'],
}


def guide_card(slug):
    if slug == 'moving-checklist':
        return ('<a class="gcard gcard-main" href="/resources/moving-checklist/"><span class="gtag">Checklist</span><b>Printable moving checklist</b>'
                '<span>From six weeks out to the day after, with your progress saved on this device.</span></a>')
    g = [x for x in GUIDES if x['slug'] == slug][0]
    return '<a class="gcard" href="/resources/%s/"><span class="gtag">%s</span><b>%s</b><span>%s</span></a>' % (slug, esc(g['tag']), esc(g['short']), esc(g['lede']))


def finish_pages(paths):
    tags = {'/resources/%s/' % x['slug']: x['tag'] for x in GUIDES}
    for path in paths:
        if path == '/':
            continue
        f = ROOT / path.strip('/') / 'index.html'
        html = f.read_text(encoding='utf-8')
        if path in HERO_FIXED:
            eb, ctas = HERO_FIXED[path]
        elif path in tags:
            eb, ctas = 'Guide: ' + tags[path].lower(), False
        elif path.startswith('/services/'):
            eb, ctas = 'Moving service', True
        elif path.startswith('/areas/'):
            eb, ctas = 'Service area', True
        else:
            eb, ctas = 'Roomi Movers', True
        html = html.replace('<p class="eyebrow">Roomi Movers · Tampa Bay</p>', '<p class="eyebrow">%s</p>' % esc(eb), 1)
        if not ctas:
            html = re.sub(r'\s*<div class="ctas">\s*<a class="btn btn-primary"[^>]*>Get a Free Estimate</a>\s*<a class="btn btn-ghost"[^>]*>[^<]*</a>\s*</div>\s*<p class="offer">.*?</p>',
                          '', html, count=1, flags=re.S)
        slugs = GUIDES_FOR.get(path) or (['moving-checklist', 'how-hourly-moving-pricing-works', 'moving-day-preparation'] if path.startswith('/areas/') and path != '/areas/' else None)
        if slugs and '<section class="closer">' in html:
            block = ('  <section class="band">\n    <div class="wrap">\n      <h2 style="font-size:clamp(24px,2.6vw,30px);margin-bottom:20px">Helpful guides</h2>\n'
                     '      <div class="gcards">' + ''.join(guide_card(s) for s in slugs) + '</div>\n    </div>\n  </section>\n')
            html = html.replace('  <section class="closer">', block + '  <section class="closer">', 1)
        f.write_text(html, encoding='utf-8', newline='\n')


# ======================= business facts that arrive later, and the private placeholder board =======================
import json as _json
BUSINESS = _json.loads((ROOT / '_tools' / 'business.json').read_text(encoding='utf-8'))


def write_rates_js():
    rates = {k: v for k, v in (BUSINESS.get('rates') or {}).items() if v}
    (ROOT / 'assets' / 'rates.js').write_text('window.ROOMI_RATES = ' + _json.dumps(rates, ensure_ascii=False) + ';\n', encoding='utf-8', newline='\n')


def phbox(title, inner, note=''):
    return '<div class="ph-box"><p class="ph-tag">Placeholder</p><h3>%s</h3>%s%s</div>' % (esc(title), inner, ('<p class="ph-note">%s</p>' % esc(note)) if note else '')


def preview_page():
    tiers = ''.join(
        '<div class="ph-box"><p class="ph-tag">Placeholder</p><h3>%s</h3><p class="ph-big">$___ <small>/ hour</small></p><p>%s</p></div>' % (esc(n), esc(d))
        for n, d in [('Labor Only', '2 movers, your truck'), ('Full-Service Move', 'Crew of ___ with the box truck'), ('White-Glove Move', 'Crew of ___ with extra protection')])
    reviews = ''.join(
        '<div class="ph-box"><p class="ph-tag">Placeholder</p><p class="ph-stars">&#9733;&#9733;&#9733;&#9733;&#9733;</p><p>"Real review text goes here."</p><p class="ph-note">First name, area, where it was posted</p></div>'
        for _ in range(3))
    photos = ''.join('<div class="ph-photo"><span>%s</span></div>' % esc(n) for n in
                     ['Crew in front of the truck', 'Couch through a doorway', 'Furniture being wrapped', 'Packed truck interior', 'Floor runners in place', 'A finished, tidy room'])
    social = ''.join('<span class="ph-chip">%s</span>' % esc(n) for n in ['Google profile', 'Facebook', 'Instagram', 'TikTok', 'YouTube', 'Nextdoor', 'Yelp'])
    rows = [('1', 'Hourly rates and crew sizes', 'Pricing cards, package finder, FAQ'),
            ('2', 'Real customer reviews', 'Reviews section, search results'),
            ('3', 'FDACS registration number and insurance summary', 'About trust card, footer, structured data'),
            ('4', 'Photos and short videos', 'Hero, About, area pages, Google profile'),
            ('5', 'Profile links', 'Footer and structured data'),
            ('6', 'Days you work (hours are 7:00 AM to 8:00 PM)', 'Hours in search results'),
            ('7', 'Payment, cancellation and damage policies', 'FAQ and terms')]
    table = '<table class="ph-table"><thead><tr><th>#</th><th>What to send</th><th>Where it goes</th></tr></thead><tbody>' + ''.join(
        '<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % tuple(esc(x) for x in r) for r in rows) + '</tbody></table>'
    b = sec('<p class="after">This private board shows exactly where each missing piece will appear. Customers do not see any of these placeholders on the live pages: they only appear once real information replaces them.</p>')
    b += '\n' + sec('<h2 class="ph-h">1. Hourly rates</h2><div class="cols cols3">' + tiers + '</div>', alt=True)
    b += '\n' + sec('<h2 class="ph-h">2. Real reviews: the scrolling wall (sample layout only)</h2>' + sample_wall() + '<h3 style="margin:28px 0 12px">Where your real reviews will go</h3><div class="cols cols3">' + reviews + '</div>')
    b += '\n' + sec('<h2 class="ph-h">3. License and insurance</h2>' + phbox('Trust card on the About page and footer',
        '<p><b>Florida registered mover</b> &middot; FDACS registration #__________</p><p><b>Insured</b> &middot; General liability $_______ &middot; Cargo or bond $_______ &middot; Workers\' compensation</p>',
        'Only shown once you have the real number and policy details.'), alt=True)
    b += '\n' + sec('<h2 class="ph-h">4. Photos</h2><div class="ph-photos">' + photos + '</div>')
    b += '\n' + sec('<h2 class="ph-h">5. Profile links</h2><div class="ph-chips">' + social + '</div>', alt=True)
    b += '\n' + sec('<h2 class="ph-h">What to send me</h2>' + table)
    p, html = hub_page('/preview-placeholders/', 'Site setup board (private) | Roomi Movers', 'Private board.', 'Setup board',
                       'Site setup board', 'Where each piece of missing information will appear. Private: not linked from the site.', b)
    html = html.replace('<meta name="viewport"', '<meta name="robots" content="noindex,nofollow">\n<meta name="viewport"', 1)
    return p, nophoto(html)


# ---------- trust section on the pages where people decide ----------
def trust_block():
    return '  <section class="band trust-band" aria-labelledby="trust-title">\n    <div class="wrap">' + trust_inner() + '</div>\n  </section>'


def insert_after_section_containing(html, marker, block):
    i = html.index('</section>', html.index(marker)) + len('</section>')
    return html[:i] + '\n' + block + html[i:]


_pricing_v4 = pricing_page


def pricing_page():
    p, html = _pricing_v4()
    return p, insert_after_section_containing(html, 'data-finder', trust_block())


_about_v4 = about_page


def about_page():
    p, html = _about_v4()
    return p, insert_after_section_containing(html, 'class="glance"', trust_block())


_contact_v4 = contact_page


def contact_page():
    p, html = _contact_v4()
    return p, insert_after_section_containing(html, 'id="quote"', trust_block())


def faq_items():
    items = _faq_items_v1()
    r = {k: v for k, v in (_biz().get('rates') or {}).items() if v}
    if r:
        q, a = items[0]
        a += (' Our rates start at %s for Labor Only, %s for a full-service move with the truck, and %s for White-Glove. '
              'Larger crews and heavier jobs are quoted in your estimate.') % (
                  r.get('Labor Only', '').replace('From ', '').lower() if r.get('Labor Only') else '',
                  r.get('Full-Service Move', '').replace('From ', '').lower() if r.get('Full-Service Move') else '',
                  r.get('White-Glove Move', '').replace('From ', '').lower() if r.get('White-Glove Move') else '')
        items[0] = (q, a)
    return items


def main():
    build_css()
    paths = ['/']
    for fn in (services_hub, pricing_page, areas_hub, about_page, faq_page, contact_page, privacy_page, resources_hub, checklist_page) + tuple((lambda g=g: guide_page(g)) for g in GUIDES):
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
    finish_pages(paths)
    write_rates_js()
    _, pv = preview_page()
    (ROOT / 'preview-placeholders').mkdir(exist_ok=True)
    (ROOT / 'preview-placeholders' / 'index.html').write_text(pv, encoding='utf-8', newline='\n')
    _, nf = notfound_page()
    (ROOT / '404.html').write_text(nf, encoding='utf-8', newline='\n')
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(
        '  <url><loc>%s%s</loc><lastmod>%s</lastmod></url>\n' % (SITE, p, UPDATED) for p in paths) + '</urlset>\n'
    (ROOT / 'sitemap.xml').write_text(sitemap, encoding='utf-8', newline='\n')
    (ROOT / 'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n' % SITE, encoding='utf-8', newline='\n')
    print('built', len(paths), 'urls')


if __name__ == '__main__':
    main()
