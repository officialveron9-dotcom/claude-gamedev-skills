# Construction realism: parts, boards, bevels, grain, hardware

Read when modelling a piece by hand or extending a generator. Tags as in [dimensions.md](dimensions.md):
[V] = verified headless in this skill's tests (bpy 5.2.2 and 4.5.14), [N] = practice.

## 1. Model the parts a carpenter would cut

| Piece | Separate parts (closed shells) | Skip for games |
|---|---|---|
| Table | top, 4 legs, 4 aprons (rails), optional stretchers, drawer front | tenons, corner blocks, screws |
| Chair | seat, 4 legs, seat rails, 2 back posts (or one bent back leg), 1–3 back slats/top rail, stretchers | dowels |
| Bar stool | seat (round, 24 segments), 4 splayed legs with level-cut ends, footrest stretchers (staggered heights) | seat cushion → soft skill |
| Bookcase | 2 sides, top, bottom, plinth rail, fixed shelves, back panel | shelf pins (texture or tiny cylinders) |
| Cabinet / wardrobe / kitchen unit | 2 sides, top, bottom, back, plinth or legs, doors (one per ≤0.6 m), handles, worktop (kitchen) | interior shelves and rails while doors stay closed |
| Drawer unit | carcass as above, drawer fronts, handles; drawer boxes (2 sides, back, bottom) only if drawers open | runners |
| Bed frame | 2 side rails, 2 end rails, ledgers, slats, legs (+ centre legs ≥ 1.4 m wide), headboard, footboard | mattress → `blender-soft-furniture` |
| Billiard table | slate/bed, cushions (6, profiled), rails, apron, legs, pocket cups, sights | pocket nets, bolts |

Rules [V]:
- Parts touch (face against face) and never share vertices. Touching faces point in opposite directions and are hidden;
  that is fine. **Two faces of different parts in the same plane, facing the same way and overlapping = z-fighting.**
  Typical traps: a back post flush with the seat side while sinking into it; two crossing stretchers at the same
  height; a back panel inset exactly flush with the side edges. Fix by a 1–8 mm offset (seat overhang, rail setback,
  staggered stretchers, back panel 2 mm inside the outline).
- Interpenetrating parts are acceptable when no faces are coplanar (stretcher ends buried in splayed legs).
- Rotate a tilted backrest about the edge that keeps it embedded (front-bottom edge): the back edge then sinks a few mm
  into the seat. Rotating about the back edge lifts the front and leaves a visible wedge gap.
- Splayed legs: build them as sheared boxes with **horizontal** top and bottom faces (`Parts.hexa`), not rotated boxes —
  a rotated box stands on one edge and its top pokes through the seat.
- Hidden interiors (shelves behind closed doors, drawer boxes) cost triangles and bake/lightmap space. Model them only
  if the doors/drawers open in game, and then make the fronts separate objects with a correct pivot.

## 2. Board and part thicknesses [N]

| Part | Thickness | Bevel (rounded edge) |
|---|---|---|
| Carcass (chipboard/MDF with edge band) | 16/18/19 mm | 1–2 mm (ABS edge band is radiused ~1–2 mm) |
| Solid wood top | 20–40 mm | 2–3 mm (chunky style up to 5 mm) |
| Laminate / chipboard top, desk | 18–25 mm | 1–2 mm |
| Kitchen worktop | 28–40 mm | 2–3 mm front, square at the wall |
| Stone top | 20–30 mm | 2–3 mm eased edge |
| Doors / drawer fronts | 18–22 mm | 1–2 mm |
| Back panel | 3 mm HDF nailed on (8 mm grooved in kitchens) | ≤ 1.2 mm (see the clamp pitfall) |
| Drawer box sides / bottom | 12–16 mm / 6–8 mm | 1 mm |
| Legs | wood 30–70 mm square, steel tube 20–40 mm | 2–3 mm wood, 1–2 mm metal |
| Glass top / shelf | 8–12 mm / 6–8 mm | 1 mm polished |
| Bar handle / knob | 10–14 mm bar, 25–35 mm knob | 1 mm |

Segment count: games 1–2 (2 gives the highlight a curve), renders 3+. Keep one width and one segment count per asset
so highlights match across parts (the hard-surface skill's micro-bevel, scaled to furniture).

## 3. Doors and drawers

| Style | Construction | Gap |
|---|---|---|
| Full overlay (EU/IKEA, frameless) | door covers the carcass front; carcass edges hidden | 2–3 mm between fronts, gap/2 at the outer edges (generators default 3 / 1.5 mm) [V] |
| Inset (classic) | door sits inside the carcass opening, flush with the front | 2 mm all round |
| Face frame (US) | 38–50 mm hardwood frame on the carcass front, doors overlay the frame | 1/2 in overlay typical [N] |

- Concealed 35 mm cup hinges are invisible from outside: do not model them. Model hinges only for inset/antique doors
  (2–3 knuckle barrels) and glass doors.
- Handles: base units horizontal near the top edge, wall units near the bottom edge, tall doors vertical at ~1.0 m,
  drawers centred. The generator posts are 8 mm square, bar 12 mm, 25 mm proud.
- Opening fronts: separate object per door (origin on the hinge axis, outer back edge, bottom) or per drawer (origin
  at the front's back face, slides along −Y). `make_cabinet(separate_doors=True)` does the doors [V]: opened 90° every
  door stays in front of the carcass.

## 4. Grain direction per part

| Part | Grain (texture U axis) |
|---|---|
| Tabletop, shelf, worktop, seat | along the longest side |
| Legs, posts, carcass sides, doors | vertical |
| Aprons, rails, stretchers, drawer fronts, plinth | horizontal, along the length |
| Back panel | vertical (or no grain: HDF) |
| Headboard | horizontal unless panelled |

`uv_grain_project` (generator) maps U to each part's longest axis wherever it lies in the face plane, with world-scale
UVs (metres / `meters_per_uv`) [V]. By hand: select the part, box-project (Cube Projection with Cube Size = 1 m
equivalent, or the generator function on a bmesh), then rotate wrong islands 90° in the UV editor (R 90). Because the
projection uses object coordinates, identical boards land on different texture regions, so the grain does not repeat.

## 5. Realism without extra polygons

- Bevel every edge (§2). Sharp 90° edges are the strongest CG tell.
- Shadow gaps: 2–3 mm reveals, a 2–3 mm shelf setback, a 10 mm apron setback, recessed plinths.
- Material contrast per part: carcass laminate, lacquered fronts, metal handles, stone worktop.
- Imperfection lives in textures: roughness variation, edge wear from a curvature/AO mask, dust on up-facing faces,
  slightly varied grain per board (UV offset), never pure black or white base colours. Bake masks with
  `scenario-blender-uv-baking`; author in Substance or Blender.
- Optional geometric wear for close-ups: chipped corners on old furniture with a few cuts before the bevel. Avoid noise
  displacement on game meshes.

## 6. Wrong vs right

| Wrong | Right |
|---|---|
| Scale a default cube (2 m) to "look like" a table | Type sizes in metres from the dimension table; apply scale |
| One extruded mesh for a whole cabinet | One closed shell per board; fronts as separate parts |
| `obj.modifiers.new("Bevel", 'BEVEL')` and leave defaults | Width 0.001–0.003, segments 1–3, Harden Normals, Miter Outer Arc (defaults: 0.1 m, 1 segment, off, Sharp) [V] |
| Doors exactly the carcass width | Doors = width − n·gap, gap 2–3 mm, outer gap/2 |
| Back panel 3 mm in the same object with a 2 mm angle-limited bevel | Weight-limited bevel, thin parts weighted down (`finalize`) [V] |
| Merge by distance on the whole multi-part mesh | Merge per part (island) [V] |
| Drawer box resting inside the bottom panel | Box ≥ 3 mm above the bottom panel, 12.5 mm side clearance [V] |
| Splayed leg = rotated box | Sheared box with level ends [V] |
| Stretchers crossing at one height | Staggered by ≥ 1 bar thickness [V] |
| Back post rotated about its back-bottom edge | Rotate about the front-bottom edge [V] |
