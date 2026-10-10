# Curtains

Contents: build · settings (measured) · length to floor · heading types · GTA (static vs env cloth) · UE.

## 1. Build (`SF.make_curtain`) [T]

1. Flat width = finished width × **fullness** (pinch pleat 2.0–2.5, wave/ripple fold 1.5–2.2, flat panel 1.2–1.5).
2. Shape the pleats first: vertices along X, Y offset = A·sin(k·x) with k = 2π·pleats/width and A solved so the
   arc length equals the flat width (bisection). Pleat width 0.10–0.15 m.
3. Pin the top row(s) (`vertex_group_mass` = "pin", weight 1) — heading tape/rings.
4. Short sim (40 frames): it only relaxes the pleats into hanging folds.
5. Apply → Solidify 2 mm (offset 0) → hem: one extra loop 3–5 cm above the bottom edge, crease or a 2 mm thicker
   band. Shade smooth.

Measured (1.4 × 2.4 m, fullness 2, 12 pleats, 2 cm edges, 17 k verts, 23 s): finished width 1.40, pleat depth
9.8 cm, top unchanged, stretch 5.5 mm with tension 60; default tension 15 stretches 12 mm (3 cm edges) [T].

| Setting | Value |
|---|---|
| Tension/Compression | 40–60 (curtain fabric barely stretches) |
| Bending | 0.5 sheer, 1 cotton, 2–5 velvet/blackout |
| Mass | 0.15 sheer, 0.25 cotton, 0.4 velvet |
| Self Collision | on, 0.004 |
| Quality | 8 |
| Pin | top row (rings: one vertex every pleat only, for scalloped tops) |
| Wind | Force field Wind strength 0.5–2 for a breeze still (render only) |

## 2. Length to the floor

- Drop = rod height − ring/heading allowance − floor clearance − expected stretch (5–12 mm at 2.4 m);
  `make_curtain(drop=None, top_z=..., floor_clearance=0.01)` computes it.
- Clearance: "float" 1 cm above the floor; "kiss" 0–5 mm; "break" 2–5 cm onto the floor; "puddle" 10–20 cm (needs a
  floor collider, friction 40, more frames).
- Sill length: 1 cm above the sill; apron: 10–15 cm below.

## 3. Heading types

| Heading | Geometry |
|---|---|
| Pinch/pencil pleat | Sine pleats + pinned top; for pinch pleats gather 3 small folds per pleat in the top 10 cm (sculpt) |
| Eyelet/grommet | Pin only the eyelet vertices; the fabric between drops into deep S-folds (fullness 1.8–2.2) |
| Wave/ripple fold | Larger amplitude, evenly spaced pins on carrier points |
| Roman blind | Not a cloth job: modeled horizontal folds + bevel |

## 4. GTA V / FiveM

- Static curtains (default): normal drawable or MLO entity, `normal_spec` shader, 0.8–3 k tris per panel after
  decimation; open/closed variants via entity sets (fivem-mlo-creation).
- Swaying curtains: GTA environment cloth lives in **fragments (YFT)**, uses the `cloth_*` shaders (flag `IS_CLOTH`,
  e.g. `cloth_normal_spec`), and Sollumz exports one cloth per fragment with `CLOTH_ENV_MAX_VERTICES = 1000` [S,
  Sollumz `ydr/cloth_env.py`, szio `Shaders.xml`]. Tuning and in-game behaviour: (verify) — not tested here.
- Collision: none or a thin box; peds should not collide with curtains.

## 5. Unreal Engine 5.8

- Static mesh, Nanite-compatible if opaque; sheer curtains are translucent or masked → not Nanite-rendered /
  programmable raster cost (`ue5-performance-optimization`).
- Movement: Chaos Cloth (skeletal mesh) for hero curtains, or WPO sway — WPO forces Nanite programmable raster and
  VSM invalidation; set *World Position Offset Disable Distance* (`ue5-performance-optimization`).
- Two-sided material for single-sided panels; Solidify 2 mm geometry is cheaper to light correctly.
