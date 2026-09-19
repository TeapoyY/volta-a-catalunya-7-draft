"""
Volta a Catalunya 7-0 — Fork from Paris-Nice 8-0 source
X-0 Sports Draft #18 — 9/19/2026
Catalan week-stage cycling, 7 stages, blue ocean confirmed (iTunes 8 query × 0 draft).
"""
import re

# === Step 1: Read Paris-Nice source ===
with open('/tmp/paris-nice-build/output.html', 'r', encoding='utf-8') as f:
    html = f.read()

# === Step 2: Read Volta a Catalunya dataset ===
with open('/tmp/volta-catalunya-build/volta_drivers.js', 'r', encoding='utf-8') as f:
    drivers_data = f.read()
with open('/tmp/volta-catalunya-build/volta_schedule.js', 'r', encoding='utf-8') as f:
    schedule_data = f.read()
with open('/tmp/volta-catalunya-build/volta_era.js', 'r', encoding='utf-8') as f:
    era_data = f.read()

# === Step 3: Brand replacements — compound FIRST, then substring ===
# Volta a Catalunya = "Volta a Catalunya" (compound, similar to "Vuelta a España")
# 整体 FIRST (compound "Volta a Catalunya" is the full race name)
html = html.replace('Paris-Nice', 'Volta a Catalunya')
html = html.replace('Paris-Nice', 'Volta a Catalunya')  # belt-and-suspenders
html = html.replace('ParisNice', 'VoltaCatalunya')      # hashtag variant
html = html.replace('paris-nice', 'volta-a-catalunya')  # filename / slug variant
html = html.replace('Paris_Nice', 'Volta_Catalunya')    # JS variable variant

# Substring replacements AFTER compound
html = html.replace('Paris', 'Volta')   # 兜底 (covers any remaining "Paris" without "Nice")

# Number prefix replacements (8-0 → 7-0)
html = html.replace('8-0:', '7-0:')
html = html.replace('8-0 ', '7-0 ')
html = html.replace('8-0<', '7-0<')
html = html.replace('8-stage', '7-stage')
html = html.replace('try to win every stage in an 8-stage', 'try to win every stage in a 7-stage')

# Article grammar: "an 8-stage" → "a 7-stage"
html = html.replace('in an 8-stage', 'in a 7-stage')

# French flag → Catalan flag
html = html.replace('🇫🇷', '🏴󠁥󠁳󠁣󠁴󠁿')  # 🇪🇸 Spain for Catalonia (regional = Spanish flag)

# Country/region references
html = html.replace('French ', 'Catalan ')  # "French flag", "French tricolor" → Catalan
html = html.replace('French', 'Catalan')    # belt-and-suspenders
html = html.replace('French cycling legends', 'Catalan cycling legends')

# Color theme — CdD/Paris-Nice/TdS = #fbbf24 yellow (Maillot Jaune)
# Volta a Catalunya = Red/Orange Catalan stripes (Senyera)
html = html.replace('--accent: #fbbf24;', '--accent: #dc2626;')      # Catalan red (Senyera)
html = html.replace('--accent2: #7f1d1d;', '--accent2: #f59e0b;')   # Catalan yellow stripe
html = html.replace('rgba(251,191,36', 'rgba(220,38,38')            # CSS gradient yellow → red

# === Step 4: Replace DRIVERS, SCHEDULE, ERA_NAMES, ERA_LABELS blocks ===
# Use regex with lambda wrapper (9/16 fix)
drv_pattern = re.compile(r'const DRIVERS = \[([\s\S]*?)\];')
sch_pattern = re.compile(r'const SCHEDULE = \[([\s\S]*?)\];')

# DRIVERS extraction — dataset file is raw array (no const wrapper)
drv_match = drv_pattern.search(drivers_data)
if drv_match:
    new_drivers_block = f"const DRIVERS = [\n{drv_match.group(1).strip()}\n];"
else:
    # No const wrapper — wrap the raw content
    new_drivers_block = f"const DRIVERS = [\n{drivers_data.strip()}\n];"
html = drv_pattern.sub(lambda m: new_drivers_block, html, count=1)
print(f"✓ DRIVERS replaced (84 drivers)")

# SCHEDULE extraction — dataset file is raw array
sch_match = sch_pattern.search(schedule_data)
if sch_match:
    new_schedule_block = f"const SCHEDULE = [\n{sch_match.group(1).strip()}\n];"
else:
    new_schedule_block = f"const SCHEDULE = [\n{schedule_data.strip()}\n];"
html = sch_pattern.sub(lambda m: new_schedule_block, html, count=1)
print(f"✓ SCHEDULE replaced (7 stages)")

# ERA_NAMES + ERA_LABELS (multi-line replace)
era_names_old = '''const ERA_NAMES = {
    1: "33-59",
    2: "60-79",
    3: "80-99",
    4: "00-09",
    5: "10-19",
    6: "20-now"
};'''
era_labels_old = '''const ERA_LABELS = {
    1: "33-59",
    2: "60-79",
    3: "80-99",
    4: "00-09",
    5: "10-19",
    6: "20-now"
};'''

# Volta a Catalunya era spans (founded 1911)
new_era_names = '''const ERA_NAMES = {
    1: "1911-1959",
    2: "1960-1979",
    3: "1980-1999",
    4: "2000-2009",
    5: "2010-2019",
    6: "2020-now"
};'''
new_era_labels = '''const ERA_LABELS = {
    1: "11-59",
    2: "60-79",
    3: "80-99",
    4: "00-09",
    5: "10-19",
    6: "20-now"
};'''

html = html.replace(era_names_old, new_era_names)
html = html.replace(era_labels_old, new_era_labels)
print(f"✓ ERA_NAMES + ERA_LABELS replaced (founded 1911)")

# === Step 5: Belt-and-suspenders cleanup of Paris-Nice leftovers ===
leftovers = [
    ('Paris-Nice', 'Volta a Catalunya'),
    ('Paris-Nice', 'Volta a Catalunya'),
    ('parisnice', 'volta-catalunya'),
    ('ParisNice', 'VoltaCatalunya'),
    ('"Course au Soleil"', '"Volta Ciclista a Catalunya"'),
    ('Course au Soleil', 'Volta Ciclista a Catalunya'),
    ('"Race to the Sun"', '"Tour of Catalonia"'),
    ('Race to the Sun', 'Tour of Catalonia'),
    ('Maillot Jaune yellow', 'Senyera red'),
    ('Maillot Jaune', 'Senyera'),
    ('Tricolore', 'Senyera'),
    ('French tricolor', 'Catalan stripes'),
    ('Paris-Nice CYCLISTS', 'VOLTA A CATALUNYA CYCLISTS'),
    ('PARIS-NICE', 'VOLTA A CATALUNYA'),
    ('Paris-Nice 8-0', 'Volta a Catalunya 7-0'),
    ('Paris-Nice 8', 'Volta a Catalunya 7'),
    ('8-0 Paris-Nice', '7-0 Volta a Catalunya'),
    ('ParisNice8Zero', 'VoltaCatalunya7Zero'),
    ('#ParisNice', '#VoltaCatalunya'),
    ('#PN', '#VC'),  # abbreviation
    ('discover Paris-Nice', 'discover Volta a Catalunya'),
    ('across 6 eras. Race 8 stages of authentic 2026 Paris-Nice',
     'across 6 eras. Race 7 stages of authentic 2026 Volta a Catalunya'),
    # Lineage comment (Paris-Nice was #17)
    ('// (lineage comment for fork #18)',
     '// Volta a Catalunya 7-0 (9/19) <- Paris-Nice 8-0 (9/17) #18'),
    # Pick N legends text
    ('Pick 5 Paris-Nice legends', 'Pick 5 Volta a Catalunya legends'),
    ('countText.textContent = \'Pick 5 Paris-Nice legends\';',
     'countText.textContent = \'Pick 5 Volta a Catalunya legends\';'),
    # Stage type bonuses comment (cycle racing)
    ('// Track-type bonuses (Paris-Nice: 8 stages)',
     '// Track-type bonuses (Volta a Catalunya: 7 stages, 1 ITT + 1 flat + 2 hills + 3 mountain)'),
    # Stats panel STAGES value (was 8 hardcoded in source, 9/16 pitfall)
    ('<div class="v">8</div><div class="l">Stages</div>',
     '<div class="v">7</div><div class="l">Stages</div>'),
    # n !== 6 defense (was 5 in current but check anyway)
    ("disabled = n !== 6;", "disabled = n !== 5;"),
    # Draft count (Paris-Nice = 5, Volta = 5 — same)
    # Belt-and-suspenders for emoji
    ('🇫🇷', '🏴󠁥󠁳󠁣󠁴󠁿'),
    # Share text template literal
    ('My Paris-Nice 8-0 season', 'My Volta a Catalunya 7-0 season'),
    # Color commentary
    ('Maillot Jaune gold', 'Senyera red'),
    ('goldMaillot', 'redSenyera'),
    # 8 stages / 8-0 leaks (post-replacement cleanup)
    ('. 84 legends. 6 eras. 8 stages. 1 goal: 8-0.', '. 84 legends. 6 eras. 7 stages. 1 goal: 7-0.'),
    ('Race 8 stages.', 'Race 7 stages.'),
    (' 8 stages · 1 dream:', ' 7 stages · 1 dream:'),
    ('84 legends across 6 eras · 8 stages (no rest)', '84 legends across 6 eras · 7 stages (no rest)'),
    ('Volta a Catalunya calendar (8 stages,', 'Volta a Catalunya calendar (7 stages,'),
    ('Volta a Catalunya: 8 stages, mountain-heavy', 'Volta a Catalunya: 7 stages, mountain-heavy'),
    ('// Real stages: 8 stages total, 1 rest day, so 20 actu',
     '// Real stages: 7 stages total, no rest days'),
    # Volta has NO rest days, fix losses calculation
    ('const losses = totalStages - 1 - wins;  // rest day is not a loss',
     'const losses = totalStages - wins;  // Volta has no rest days'),
    # Display actual wins-losses (not aspirational perfect)
    ("$('finale-record').textContent = `${totalStages}-0`;  // Display as \"21-0\" perfect = \"won every stage\"",
     "$('finale-record').textContent = `${wins}-${losses}`;  // Show actual result for Volta (no rest days)"),
    ("$('share-record').textContent = `${totalStages}-0`;",
     "$('share-record').textContent = `${wins}-${losses}`;"),
    # 8-0 prefix leaks (Stage number, draft count, etc.)
    ('STAGE <span id="race-counter">1</span> OF 8',
     'STAGE <span id="race-counter">1</span> OF 7'),
    # Tagline (will be replaced later too, but belt-and-suspenders)
    ('Race 8 stages of authentic 2026 Volta a Catalunya',
     'Race 7 stages of authentic 2026 Volta a Catalunya'),
    # Hashtag bugs (Paris-Nice was 8Zero, Volta should be 7Zero)
    ('#VoltaCatalunya8Zero', '#VoltaCatalunya7Zero'),
    ('#VoltaCatalunya8Zero', '#VoltaCatalunya7Zero'),  # belt-and-suspenders
    ('#VoltaCatalunya ', '#VoltaCatalunya '),  # OK
    # Hashtag compound "Volta a Catalunya" → "VoltaCatalunya"
    ('#Volta a Catalunya', '#VoltaCatalunya'),
    # Stage log "All 21 Stages"
    ('All 21 Stages', 'All 7 Stages'),
    ('All 8 Stages', 'All 7 Stages'),
]
for old, new in leftovers:
    if old in html:
        html = html.replace(old, new)
print(f"✓ Belt-and-suspenders cleanup: {len(leftovers)} patterns applied")

# === Step 6: Update meta description + title ===
old_meta = '''<title>🇫🇷 8-0: Paris-Nice Draft — Can You Win the Maillot Jaune?</title>
<meta name="description" content="Draft legendary Paris-Nice cyclists across 6 eras and try to win every stage in an 8-stage Paris-Nice. 84 legends. 6 eras. 8 stages. 1 goal: 8-0.">'''
new_meta = '''<title>🏴 7-0: Volta a Catalunya Draft — Can You Win the Senyera?</title>
<meta name="description" content="Draft legendary Volta a Catalunya cyclists across 6 eras and try to win every stage in a 7-stage Catalan week race. 84 legends. 6 eras. 7 stages. 1 goal: 7-0.">'''
html = html.replace(old_meta, new_meta)
print(f"✓ Meta description + title updated")

# === Step 7: Update tagline ===
html = html.replace(
    '<div class="tagline">Draft legends. Race 8 stages of authentic 2026 Paris-Nice calendar. Win all. Wear the <em>Maillot Jaune</em>.</div>',
    '<div class="tagline">Draft legends. Race 7 stages of authentic 2026 Volta a Catalunya calendar. Win all. Wear the <em>Senyera</em>.</div>'
)

# === Step 8: Final verification grep ===
print(f"\n=== Final verification ===")
checks = [
    ('Paris-Nice', 0),
    ('Paris', 0),  # May have legitimate "Paris" elsewhere — verify
    ('Maillot Jaune', 0),
    ('8-0', 0),     # Should only show in lineage comments
    ('84 legends', 1),  # Should appear once in tagline or stats
    ('7 stages', 1),
    ('Volta a Catalunya', None),  # Should be many
    ('Senyera', None),
    ('1911-1959', 1),
    ('const DRIVERS', 1),
    ('const SCHEDULE', 1),
    ('const ERA_NAMES', 1),
    ('const ERA_LABELS', 1),
]
for pattern, expected in checks:
    count = html.count(pattern)
    status = '✅' if expected is None or count == expected else ('⚠️' if expected == 0 else '❌')
    if expected == 0 and count > 0:
        print(f"  {status} '{pattern}' = {count} (expected 0) — LEAK")
    elif expected is not None and count != expected:
        print(f"  {status} '{pattern}' = {count} (expected {expected})")
    else:
        print(f"  ✓ '{pattern}' = {count}")

# === Step 9: Write output ===
with open('/tmp/volta-catalunya-build/output.html', 'w', encoding='utf-8') as f:
    f.write(html)
print(f"\n✓ Written /tmp/volta-catalunya-build/output.html ({len(html)} bytes)")
