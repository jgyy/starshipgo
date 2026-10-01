# Architectural assets (stairs, guard, sign, hull fascia)

Separate from the model catalogue (nothing here is registered with `@family`).
Code: `blender/starship/arch.py`, textures `blender/starship/textures_arch.py`, CLI `blender/build_arch.py`.

```bash
python blender/build_arch.py --out godot            # textures + godot/arch/*.glb + godot/data/arch.json (~6 s)
python blender/build_arch.py --out godot --only fascia   # rebuild one model (arch.json entry is merged)
python blender/build_arch.py --check                # builds everything into a temp dir, writes nothing to godot/
godot --headless --path godot --import              # import the new GLB / PNG files
```

Frame: glTF/Godot (+Y up, +Z front, -Z back), metres. Geometry is deterministic (same inputs give the same
vertices and triangles; byte order of the GLB index buffer can still jitter, as for the catalogue).
Embedded GLB textures are 256 px JPEG copies; the full-size PBR sets live in `godot/textures/surfaces/`.

## Stair flight `arch_stair_flight`

| item | value |
|---|---|
| origin | centre of the foot edge on the floor; z = 0 is the front face plane of riser 1 |
| climb direction | -Z |
| width | 1.40 m (x -0.70 .. +0.70, stringers included) |
| steps | 11, riser 4.0/22 = 0.181818 m, tread 0.28 m |
| step i (1..11) | top at y = i*riser, spans z from -(i-1)*0.28 to -i*0.28 |
| step 11 | top y = 2.0, z in [-3.08, -2.80]; start of the landing (next flight/landing starts at z = -3.08, y = 2.0) |
| stringers | closed 4 cm steel plates on both sides, down to the floor, 5 cm kerb above the treads, soffit plate below |
| nosing | steel strip (inside the tread span) + emissive amber edge line + cool-white LED strip under the nose |
| handrails | round tube r = 0.02, 0.90 m above the nosing line (y = 0.1818 + 0.6494*(-z) + 0.9), second rail at 0.45 m, posts on steps 1/4/7/10; bottom end turns down into a newel to the floor, top rail runs level to z = -3.08 and returns down to y = 2.0. Rail centre x = +-0.67 (max extent +-0.705) |
| budget | ~4000 tris, ~270 KB |

## Other assets

| id | origin | size | notes |
|---|---|---|---|
| `arch_stair_guard` | centre of the foot, on the floor; panel in the XY plane (faces +Z) | 0.50 w x 1.0 h x ~0.11 d | posts, 2 rails, balusters, kick plate, amber top strip |
| `arch_stair_sign` | wall mount: centre of the back plane, extends +Z | 0.6 x 0.3 x 0.03 | emissive up-arrow + 3 level bars + amber strips |
| `arch_hull_fascia` | world coordinates (ship origin), no extra transform | whole hull | see below |

### `arch_hull_fascia` (world space, -Z = bow)
Built from `godot/data/ship.json["hull"]` when present (tolerant of `{"decks": {"1": {"outline": [[x,z],...]}}}`
style layouts, else `tools/layout/hull.py`); deck floor y from `ship.json["decks"]`, ceiling = floor + 3.4.
Named mesh nodes:

* `fascia_deck1|2|3` - sheer-strake rail (0.12 m proud, ~0.22 m body) at floor level (y -0.33..+0.15 rel. to the floor)
  and at ceiling level (y +0..+0.35 above floor + 3.4), each with a recessed emissive running-light strip
  (Deck 1 cyan, Deck 2 amber, Deck 3 white-blue). Deck 3 is an open chain (no rail across the stern/hangar mouth); its
  ceiling rail climbs from y 3.4 to the hangar height 7.0 between z = 20 and z = 26 (`HANGAR_Z0/Z1` in arch.py).
* `stem_deckN` - pointed bow fairings on the floor and ceiling bands at each nose.
* `transom_deck1|2` - stern plates: apron (floor+0.15..0.78) and band (floor+3.02..3.4) so windows stay free.
* `hangar_frame` - 14 m x 7 m mouth frame at z = 32 (jambs, header, sill, corner gussets, amber edge lights).
* `nacelle_port`, `nacelle_starboard` - engine pods hung below the stern corners (x = +-11.6, y = -0.25, z ~ 23..34).

## Materials (names in the GLBs)
Textured: `arch_tread` (stair_tread), `arch_riser` (stair_riser), `arch_steel` (existing hull_dark), `arch_hull_plate` (hull_plate).
Plain: `arch_nosing`, `arch_rail`, `arch_post`, `arch_dark_panel`; emissive `arch_led`, `arch_run_cyan|amber|white`,
plus kit materials (`em_amber`, `em_cyan`, `hazard_yellow`, `chrome`...).
UVs are box-projected in metres: tread 0.5 m/tile, riser 0.7 m wide x one riser tall per tile, hull_plate 4 m/tile.

## Textures (godot/textures/surfaces/<name>_{albedo,normal,orm}.png, ORM = ao/rough/metal)
`hull_plate` 1024 (4 m tiling, 2 m panels, rivets, welds, stencil grooves, scorching), `stair_tread` 512 (0.5 m tile),
`stair_riser` 512 (0.7 m x 0.18 m, hazard band on the top edge), `hull_window_frame` 512 (spare, unused by the GLBs).
