# Sources (accessed 2026-10-10)

Legend: **D** = read directly (cloned repo, source file, or executed); **S** = search-result snippet only (the page
itself was blocked from this environment: catas.com, wpapool.com, cuesportsindia.com, ikea.com, docs.blender.org,
polyhaven.com, ambientcg.com and most other sites); **V** = verified by running bpy headless.

## Executed / source code
- V `bpy` 5.2.2 LTS (Python 3.13) and 4.5.14 LTS (Python 3.11) wheels from PyPI: generator tests 276/276; modifier
  defaults (Bevel width 0.1 m, segments 1, Angle 30°, Harden Normals off, Miter Sharp, Clamp on; Weighted Normal
  Face Area/50/0.01; Mirror merge 0.001; Array merge off; Boolean EXACT, solvers FLOAT/EXACT/MANIFOLD; Triangulate
  keep_custom_normals off); Principled 5.2 socket list; Clamp Overlap probe (2.0 → 1.5 mm with a 3 mm part); Mirror
  probe (closed half + merge = 8 non-manifold edges, open half = 0); FBX round trip; `KeyError ... "Clearcoat"`.
- D https://github.com/Sollumz/Sollumz `main` 07d6a49 (2026-10-10): `ydr/ydrexport.py` (`create_model` exports the
  evaluated mesh, bmesh triangulation, `split_vert_buffers` MAX_INDEX 65535), `ydr/vertex_buffer_builder.py` (loop
  normals, Vertex domain averaging), `ydr/properties.py` (`lod_dist_high/med/low/vlow` default 9998),
  `ytyp/properties/ytyp.py` (archetype `lod_dist` 200, `hd_texture_dist` 100), `ybn/gta5/presets/flag_presets.json`.
- D Sollumz/szio `x/szio/gta5/Shaders.xml`: shader names and texture slots (`normal_spec`, `normal_spec_detail`,
  `normal_spec_tnt`, `normal_spec_reflect`, `spec_reflect`, `normal_spec_decal`, `decal`, `glass*`,
  `mirror_default`, `emissive`, `default`, `cloth_normal_spec`).
- D https://github.com/Sollumz/wiki `ab7338c` (2026-09-25): Creating Props (normal_spec, Convert to Drawable, LOD
  panel, Auto LOD tool).
- D Blender source `blender-v5.2-release` d13f752 (`rna_modifier.cc` WeightedNormal properties).
- D This repo: `blender-python-pitfalls` (API changes, FBX settings), `fivem-mlo-doors-windows`
  (`references/procedural-modeling.md` conventions, `sz_*` functions), `fivem-mlo-creation` (collision materials,
  Gen9 128 limit, MLO entity rules), `gta-texture-editing` (SpecSampler intensity/gloss), `billiards-game-dev`
  (`references/constants.md`: WPA table, pockets, nose height 0.635 D), `scenario-blender-hard-surface`.

## Dimensions (S unless marked)
- https://knowledge.bsigroup.com/products/office-furniture-work-tables-and-desks-dimensions, https://www.dinmedia.de/en/standard/din-en-527-1/136439467 : EN 527-1:2011 scope (seated/sit-stand/standing desks, 5th–95th percentile); numbers not shown.
- https://www.bureaustoel.nl/wp-content/uploads/2022/01/NEN-EN-1335-1-april-2020.pdf, https://www.centrufficio.it/wp-content/uploads/2020/04/Play_certificazione-EN1335-1-2020-tipo-B.pdf : EN 1335-1:2020 seat height ranges per type (Ax/A/B/C), seat depth, backrest ≥ 360 mm.
- https://catas.com/uploads/media/unien1116-eng.pdf (snippet), https://www.mybuilder.com/questions/v/4137/ , https://origin-exchange.autodesk.com/kitchen-unit-measurements : EN 1116 plinth ≥ 80 mm, wall unit ≥ 450 mm above the worktop; 900–910 mm worktops, 720 mm carcass, 150 mm plinth, 600 mm worktop depth.
- https://www.thewcsupply.com/blogs/learn/how-deep-are-kitchen-cabinets , https://houlte.com/blogs/news/how-tall-are-standard-kitchen-cabinets-dimensions-guide : US 34.5 in base, 36 in counter, 24 in depth, toe kick 3.5–4.5 × 3 in, wall cabinets 12 in deep, 18 in above the counter.
- https://www.architectgpt.io/blog/bar-stool-guide-counter-height-bar-height-proportion , https://plankandbeam.com/blogs/home-inspiration-information/what-height-bar-stool-do-i-need , https://barstoolcomforts.com/category/counter-and-bar-height-bar-stools : counter 34–36 in, bar 40–42 in, stools 24–27 / 28–32 in, 10–12 in knee gap.
- https://arcedior.com/blog/chair-clearance-behind-dining-tables , https://www.wakefit.co/blog/dining-table-size-guide-4-6-8-seater-dimensions/ : 60 cm per diner, 0.75–0.90 pull-out, 0.90–1.20 walkway.
- https://www.ikea.com/cz/en/p/pax-wardrobe-frame-dark-grey-50509128/ and other IKEA PAX pages: 50 × 58 × 201 cm frame, 236 cm frames, ceiling ≥ 237 / 240 cm.
- https://www.ikea.cn/cn/en/p/billy-bookcase-black-brown-20351582 , https://mgmt.ikea.gr/en/products/billy-oxberg-bookcase-with-doors-80x30x202-cm/69281776/ : BILLY 80 × 28 × 202 cm, 30 kg/shelf, particleboard; 30 cm deep variant.
- https://www.bricknbolt.com/blogs-and-articles/home-improvement/wardrobe-design-dimensions-storage-tips , https://www.homelane.com/blog/?p=82257 : hanging zones 1.6–1.8 m long, ~1.0 m double, inner depth ≥ 500 mm.
- https://www.woodworker.de/forum/threads/spaltbreite-zwischen-k%C3%BCchenfronten.134871/ , https://www.woodworker.de/forum/threads/schubladen-fugen.79637/ : 3 mm fronts on chipboard, 2 mm solid wood, 4 mm per some drawer data sheets.
- https://www.baunetzwissen.de/fenster-und-tueren/fachwissen/konstruktion-funktion/wandoeffnungen-und-tuergroessen-nach-din-18101-155227 , https://www.hausjournal.net/hoehe-tuerklinke , https://www.woodworker.de/forum/threads/din-h%C3%B6he-dr%C3%BCckergarnitur.16416/ : handle 1050 mm common in DE; DIN 18101 covers leaf sizes (handle height not confirmed in it).
- https://t3.com/features/mattress-size-guide , https://puffy.com/blogs/best-sleep/standard-mattress-sizes-international-mattress-dimension-chart , https://www.tomsguide.com/reference/mattress-sizes-and-bed-dimensions-us-and-uk : EU 90/140/160/180 × 200, UK double 135 × 190 (= US full), UK king/super king variants, Cal king ±4 in vs king.
- https://flowyline.com/blogs/for-diy-ers/how-tall-should-a-nightstand-be , https://carlaaston.com/designed/how-tall-should-your-nightstand-be : nightstand level with the mattress top (±2–4 in).
- https://www.homestyler.com/article/perfect-dining-room-lighting , https://www.crateandbarrel.ca/lighting/how-to-hang-lighting-guide/1 : pendant 30–36 in above the table, +3 in per extra foot of ceiling.
- https://forums.azbilliards.com/threads/diamond-pro.127876 (WPA spec quoted), https://www.poolroom.com/tournament-table-equipment-specifications/ , https://drdavepoolinfo.com/FAQ/table/cushion-nose-height/ , https://pooltableportfolio.com/blogs/magazine/how-big-is-a-pool-table-a-comprehensive-guide-to-pool-table-dimensions-and-table-options : WPA 100 × 50 / 92 × 46 in, bed 29¼–31 in, nose 63.5 % (62.5–64.5 %), cushion 1⅞–2 in, rail 4–7½ in, 18 sights 12½ / 11½ in, sight 3 11/16 in from the nose, pocket mouths; 7 ft range.
- https://wpbsa.com/wp-content/uploads/Rulebook-Website-Updated-May-2022.pdf (snippet), https://club-snooker.web.cern.ch/club-snooker/rules.html : snooker 3569 × 1778 mm ±13, height 864 mm ±13 (older 851–876).

## Modelling, materials, engines (S)
- https://docs.blender.org/manual/en/latest/modeling/modifiers/generate/bevel.html : Clamp Overlap, Loop Slide, Miter Outer Sharp/Patch/Arc, Harden Normals (needs custom normals, created automatically).
- https://docs.polyhaven.com/en/faq : Poly Haven CC0, commercial use, no attribution required.
- https://app.cinevva.com/guides/free-textures-hdris-materials : ambientCG public domain, FreePBR personal-use only.
- https://polycount.com/discussion/comment/2476678 , https://learn.foundry.com/modo/12.0/content/help/pages/uving/texel_density.html : 512 px/m baseline discussion, texel-density arithmetic.
- https://forums.unrealengine.com/t/why-does-nanite-not-work/2738542 , https://uhiyama-lab.com/en/notes/ue/nanite-high-poly-mesh-optimization/ : Nanite falls back for translucent materials; masked support varies by version.

## Add-ons and skills
- D (cloned): s-leger/archipack, Furche/LayoutLab, karelvrabeckv/cupboard-generator, luneszleg/Blender-MCP-Modelling-Skills, adauzat90/Woodworking_AI, arjun988/blender-skills, KevinXu02/aha-3d, hugozap/cozy-room-3d, dasfink/sketchup-mcp, muhammadusamahoyrr/fyp, FIRaci/A-ch-n.
- S https://www.renderjuice.com/blender/extensions/archimesh , https://docs.blender.org/manual/ja/4.1/addons/add_mesh/archimesh.html : Archimesh features, bundled until 4.1, extension 1.2.5 GPL-2.0-or-later.
- S https://wiki.osarch.org/index.php/Archipack , https://blender-archipack.gumroad.com/ : Archipack 2.x paid, free 1.2.85 for 3.0 only, GPLv3.
- S GitHub search metadata: pyrokitty64/mesh-stuff description (CC0 claim).
