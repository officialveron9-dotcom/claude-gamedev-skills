# Furniture dimensions and proportion rules (metric)

Read when sizing any piece. All values in metres unless marked cm/mm. Tags: **[S]** search-result snippet of a
standard/manufacturer/guide (see [sources.md](sources.md)), **[D]** read directly (repo/source), **[N]** common
practice, not confirmed by a source: say "(verify)" when you pass an [N] value to the user. Standards (EN 527-1,
EN 1335-1, EN 1116, DIN 18101) are paywalled; only their snippets were seen.

## 1. Seating

| Item | Seat height (top of seat) | Other | Tag |
|---|---|---|---|
| Dining chair | 0.43–0.47 (0.45 default) | seat 0.40–0.50 wide, 0.40–0.45 deep; seat-to-tabletop 0.27–0.32; back top 0.80–0.95; back tilt 5–10° from vertical | [N] |
| Office chair EN 1335-1:2020 | Type A 0.400–0.520, Type B 0.420–0.510, Type C 0.430–0.480, Type Ax 0.400–0.540 (adjustment range) | seat depth A 0.425–0.450 (adjustable chairs); backrest height and width ≥ 0.360 | [S] |
| Armchair / lounge | 0.38–0.45 | arm 0.60–0.68 from floor; frames only here, cushions → `blender-soft-furniture` | [N] |
| Sofa frame | 0.40–0.45 seat (compressed cushion) | seat depth 0.55–0.65; frame → this skill, cushions → soft skill | [N] |
| Bench | 0.43–0.47 | | [N] |
| Counter stool (for 0.90–0.92 counter) | 0.61–0.69 (24–27 in); 0.65 default | knee gap seat → underside of top 0.25–0.30 (10–12 in) | [S] |
| Bar stool (for 1.02–1.10 bar) | 0.71–0.81 (28–32 in); 0.75 default | footrest ≈ seat − 0.45 (0.30 for a 0.75 seat) | [S] / footrest [N] |
| Stool seat diameter | 0.30–0.40 | | [N] |

## 2. Tables and desks

| Item | Height (top surface) | Plan size | Tag |
|---|---|---|---|
| Dining table | 0.73–0.76 (EU 0.75; US 29–30 in = 0.74–0.76) | 0.60 width per diner (min 0.55), ~0.40 depth per diner; two-sided table 0.80–1.00 deep; 4 seats 1.20–1.40 × 0.80, 6 seats 1.60–1.80 × 0.90 | width per diner [S], rest [N] |
| Desk EN 527-1:2011 | fixed desks usually 0.72–0.75 (verify against EN 527-1 Table 1); sit-stand ranges ~0.65–1.25 | 1.20–1.80 × 0.70–0.80 | standard scope [S], numbers [N] |
| Coffee table | 0.40–0.46 | 0.40–0.45 from the sofa edge | [N] |
| Side / end table | 0.50–0.65 (near sofa arm height) | 0.40–0.60 | [N] |
| Counter-height table | 0.90–0.92 (36 in) | | [S] |
| Bar table / bar top | 1.02–1.10 (40–42 in) | top depth 0.30–0.60 | height [S], depth [N] |
| Knee clearance | floor → apron/drawer bottom ≥ 0.60–0.63 | apron 0.07–0.12 high | [N] (cross-check: Woodworking_AI notes, no licence) |

Top thickness: solid wood 0.025–0.040, chipboard/MDF 0.018–0.025 (+ edge band), glass 0.008–0.012, stone 0.02–0.03.
Overhang of the top beyond the legs: 0.03–0.08 (0.05 default). [N]

## 3. Clearances (plan view)

| Situation | Clear distance | Tag |
|---|---|---|
| Table edge → wall, chair pulled out only | 0.75–0.90 | [S] (sources disagree; 0.90 safe) |
| Table edge → wall, people walk behind seated diners | 0.90–1.20 | [S] |
| Main walkway | 0.90–1.10 | [N] |
| Sofa → coffee table | 0.40–0.45 | [N] |
| In front of wardrobe / drawers (door swing, kneeling) | ≥ 0.90 | [N] |
| Beside a bed | 0.60–0.70 | [N] |
| Kitchen aisle between counters | 1.00–1.20 | [N] |
| Pool table: every edge → wall | ≥ cue length 1.47 (57–58 in) + stroke, so ~1.5 | [N] |

## 4. Storage: shelves, wardrobes, dressers, nightstands, TV units

| Item | Numbers | Tag |
|---|---|---|
| Bookcase | depth 0.25–0.30 (IKEA BILLY 0.80 × 0.28 × 2.02, 30 kg/shelf, particleboard; some variants 0.30 deep) | [S] |
| Shelf clear height | paperbacks 0.20, hardcovers 0.30, binders 0.32 | [N] |
| Shelf span | 18–19 mm chipboard: keep ≤ 0.80 between supports (sags beyond; plywood a bit more); use 25 mm, a front lip or a middle support for longer spans | [N] (verify with a sag calculator) |
| Wardrobe | depth 0.58–0.60 carcass (IKEA PAX frame 0.58; doors add ~0.02); heights 2.01 and 2.36 (PAX); upright assembly needs ceiling ≥ 2.37 (PAX), sliding doors ≥ 2.40 | [S] |
| Hanging | long garments 1.60–1.80 clear below the rail; double hanging ~1.00 per rail; inner depth ≥ 0.50 for hangers (sliding doors eat 0.075–0.10) | [S] |
| Dresser / chest | height 0.75–1.00, depth 0.45–0.50, width 0.80–1.60; fronts 0.10–0.30 high, graduated (smallest on top) | [N] |
| Nightstand | top level with the mattress top, or within ±0.05 (sources allow up to 0.10 higher); typically 0.45–0.65 high, 0.40–0.50 wide, 0.35–0.45 deep | [S] |
| TV unit | 0.40–0.60 high, 0.40–0.50 deep; screen centre near seated eye height ~1.0–1.1 | [N] |
| Sideboard | 0.75–0.90 high, 0.40–0.50 deep | [N] |

## 5. Kitchen (EU vs US)

| Item | EU | US | Tag |
|---|---|---|---|
| Worktop surface | 0.85–0.95, usually 0.90–0.91 | 36 in (0.914) | [S] |
| Worktop thickness / depth | 0.028–0.040 / 0.60 | 1.5 in (0.038) / 25–25.5 in | EU [S], US [N] |
| Base carcass | 0.72 high (+ plinth), 0.56–0.58 deep + door | box 34.5 in (0.876) incl. toe kick, 24 in (0.61) deep | [S] |
| Plinth / toe kick | 0.10–0.15 high (EN 1116 minimum 0.08 per CATAS summary), set back 0.05–0.06 | 3.5–4.5 in high, 3 in (0.076) deep | [S] |
| Wall units | bottom ≥ 0.45 above the worktop (EN 1116 via CATAS), usually 0.50–0.60 → bottom at ~1.45–1.50; depth 0.30–0.35 | 18 in (0.457) above the counter, 12 in (0.305) deep, 30/36/42 in tall | clearance [S], rest [N] |
| Tall units | 2.00–2.40 high, base depth | 84–96 in | [N] |
| Module widths | 0.30/0.40/0.45/0.50/0.60/0.80/0.90/1.00/1.20 | 9–48 in in 3 in steps | [N] |
| Handle hole spacing | 32 mm system: 96, 128, 160, 192, 256, 320 mm centres | 3, 3.75, 5 in | [N] |

## 6. Bars and counters

| Item | Numbers | Tag |
|---|---|---|
| Counter seating | top 0.90–0.92 + stool seat 0.65 | [S] |
| Bar seating | top 1.05–1.10 (US 40–42 in) + stool seat 0.75 (0.71–0.81) | [S] |
| Seat → underside of top | 0.25–0.30 (10–12 in); some guides 0.23–0.33 | [S] |
| Stool spacing | 0.60 centre to centre (0.55–0.65) | [N] |
| Knee overhang of the top | 0.25–0.30 | [N] |
| Bar foot rail | 0.18–0.25 above floor, 0.15–0.20 out from the bar front | [N] |

## 7. Beds (frame inner size = mattress + 0.01–0.02 per side)

| Mattress | Size (w × l) | Tag |
|---|---|---|
| EU single / double / king / large | 0.90 × 2.00, 1.40 × 2.00, 1.60 × 2.00, 1.80 × 2.00 (also 1.00, 1.20, 2.00 widths) | [S] |
| UK single / double / king / super king | 0.90 × 1.90, 1.35 × 1.90, 1.50 × 2.00 (sources: 1.52 × 1.98), 1.80 × 2.00 (1.83 × 1.98) | [S] |
| US twin / twin XL / full / queen / king / Cal king | 38 × 75, 38 × 80, 54 × 75, 60 × 80, 76 × 80, 72 × 84 in (0.965 × 1.905 … 1.829 × 2.134) | full = UK double [S]; king vs Cal king ±4 in [S]; rest [N] |
| Mattress thickness | 0.18–0.30 (soft skill) | [N] |
| Mattress top above floor | 0.45–0.60 (0.50–0.55 default) | [N] |
| Slat gaps | ≤ 0.05–0.07; slats 0.06–0.07 wide | [N] |
| Headboard top | 0.90–1.20 above floor | [N] |

Nightstand height follows the mattress top (§4).

## 8. Doors, handles, light switches

| Item | Numbers | Tag |
|---|---|---|
| Room door handle | 1.05 above finished floor in Germany (DIN 18101 not confirmed as the source; barrier-free 0.85 per DIN 18040 guides); US 34–48 in | DE [S], US [N] |
| Room door leaf / opening | see `fivem-mlo-doors-windows` (0.90 × 2.10 clear default) | [D] |
| Cabinet handle position | base units: horizontal bar 0.05–0.07 below the door top edge; wall units: near the bottom edge; tall doors: centre ~0.95–1.10 above floor | [N] |
| Bar handle | 96–320 mm centres, 25–35 mm proud, 10–14 mm bar | [N] |
| Knob | 25–35 mm diameter, 20–30 mm proud | [N] |

## 9. Lamps

| Item | Numbers | Tag |
|---|---|---|
| Pendant over a dining table | bottom 0.75–0.90 (30–36 in) above the tabletop at 2.4 m ceilings; +0.075 per extra 0.30 of ceiling; width 1/2–2/3 of the table width | [S] |
| Floor lamp | 1.50–1.80 total | [N] |
| Table lamp | 0.50–0.75 total; shade bottom near seated eye level | [N] |
| Wall sconce | 1.50–1.70 to centre | [N] |

## 10. Billiard tables

| Item | Value | Tag |
|---|---|---|
| WPA 9 ft playing surface (between cushion noses) | 100 × 50 in = 2.540 × 1.270 (±1/8 in) | [S] |
| 8 ft pro / 8 ft home / 7 ft bar box | 92 × 46 in (2.337 × 1.168) / 88 × 44 in (2.235 × 1.118) / 74–78 × 37–39 in (1.88–1.98 × 0.94–0.99) | 8 ft pro [S], others [S] guide, not WPA |
| Bed (playing surface) height | 29¼–31 in = 0.743–0.787 from the floor (0.762 default) | [S] (WPA notes the spec need not apply to home tables) |
| Cushion nose height | 63.5 % (62.5–64.5 %) of the ball diameter: 36.3 mm for 57.15 mm balls | [S]; matches `billiards-game-dev` [D] |
| Cushion width (feather strip → nose) | 1⅞–2 in (0.048–0.051) | [S] |
| Rail width incl. cushion | 4–7½ in (0.10–0.19) | [S] |
| Sights | 18 (or 17 + name plate); 12½ in apart on a 9 ft (= length/8), 11½ in on 8 ft pro; centre 3 11/16 in (0.094) from the cushion nose | [S] |
| Pocket mouths (nose to nose) | corner 4.5–4.625 in (0.114–0.117), side 5–5.125 in (0.127–0.130); jaw angles and shelves → `billiards-game-dev` | [S] / [D] |
| Snooker | 3.569 × 1.778 (±0.013) between cushion faces; floor → top of cushion rail 0.864 ±0.013 (WPBSA 2022; older rules 0.851–0.876) | [S] |
| Carom match table | 2.84 × 1.42 | [D] via `billiards-game-dev` |
| Room for a 9 ft table | table outline + ~1.5 per side → ~4.3 × 5.6 | [N] |

## 11. Proportion rules that make furniture read as real

| Rule | Value | Tag |
|---|---|---|
| Solid-wood table leg section | ≈ height/12–height/15 (0.05–0.07 for a 0.75 table); chair legs 0.03–0.04; steel tube 0.02–0.04 | [N] (Woodworking_AI: ~1/12) |
| Top thickness vs span | ≥ 1/50 of the unsupported span for wood; chunky "farmhouse" 0.04–0.06 | [N] |
| Apron (table rail) | 0.07–0.12 high, 0.018–0.025 thick, set back 0.01–0.02 from the leg face | [N] |
| Overhang | top 0.03–0.08 past the legs; chair seat 0.005–0.02 past the frame | [N] |
| Reveal (gap) between fronts | 2–3 mm (3 mm most common on chipboard; 2 mm on solid wood; some drawer systems specify 4 mm); outer edge gap/2 | [S] (woodworker forum) |
| Plinth | 0.06–0.15 high, set back 0.02–0.06 | [N] / EN 1116 min 0.08 [S] |
| Door width | split a door wider than ~0.55–0.60 into a pair | [N] |
| Drawer stack | graduated, each front ~10–15 % taller than the one above | [N] |
| Board thicknesses | carcass 16/18/19 mm, back 3 mm HDF (8 mm grooved in kitchens), door 18–22 mm, drawer sides 12–16 mm, drawer bottom 6–8 mm, glass shelf 6–8 mm | [N] |

"Toy-like" = every part too thick (e.g. 50 mm carcass boards), legs too fat, no bevels, no gaps, everything one
material, or a uniformly scaled primitive. Check every board against this table and stand a 1.75 m box next to it.
