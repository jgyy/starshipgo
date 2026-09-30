# StarshipGo

A first-person exploration game set inside the interior of a starship.
**Blender** (headless, via the `bpy` module) procedurally generates **1000 unique GLB components** and
their textures; **Godot 4** assembles them into a walkable three-deck ship with sliding doors,
turbolifts, ~280 real-time lights, reflections, haze, ambient sound, a deck map and a planet outside the windows.
The game is all about walking around the *inside* of the ship in first person. No people, just the ship.

| | |
|---|---|
| ![Bridge](docs/screenshots/01_bridge.png) | ![Command corridor](docs/screenshots/03_command_corridor.png) |
| ![Mess hall](docs/screenshots/09_mess_hall.png) | ![Main engineering](docs/screenshots/18_main_engineering.png) |
| ![Galley](docs/screenshots/10_galley.png) | ![Hangar](docs/screenshots/24_hangar_bay.png) |

## Quick start

```bash
# 1. (optional) regenerate the assets - needs Python 3.14:  pip install bpy numpy
python blender/build_all.py --out godot          # 1000 GLBs + textures + data/catalog.json (~20 s on 4 cores)
python tools/layout/generate_ship.py             # arrange them: godot/data/ship.json

# 2. play (Godot 4.7+)
godot --path godot --import                      # first run only: import the GLBs
godot --path godot
```

The generated GLBs, textures and `ship.json` are committed, so opening `godot/` in the editor is enough.

**Controls** - `WASD` move, `Shift` sprint, mouse look, `F` flashlight, `M` deck map, `H` help,
`Esc` release the mouse. Step into a turbolift (aft end of every deck) and press `1` / `2` / `3` to change deck.

## Pipeline

```mermaid
flowchart LR
    subgraph Blender["Blender 5 (headless bpy)"]
        K[kit.py<br/>bmesh primitives + PBR materials] --> F[11 component modules<br/>93 categories]
        T[textures.py<br/>numpy -> PNG via bpy] --> S[screens / surfaces / sky]
        F --> G[[1000 x .glb]]
        F --> C[(catalog.json<br/>bounds, mount, tags)]
    end
    subgraph Layout["tools/layout (Python)"]
        C --> L[generate_ship.py<br/>rooms, doors, recipes, lights]
        L --> J[(ship.json)]
    end
    subgraph Godot["Godot 4"]
        G --> B[ShipBuilder.gd]
        S --> B
        J --> B
        B --> W((Playable ship<br/>player, doors, lifts, HUD))
    end
```

* `blender/starship/kit.py` - modelling kit: boxes, cylinders, tori, prisms, screens, materials, exporter.
  Authoring frame = glTF frame (+Y up, +Z front, metres). See [`blender/CONVENTIONS.md`](blender/CONVENTIONS.md).
* `blender/starship/components/*.py` - the 1000 models, registered with `@family(category, labels, mount, tags)`.
* `tools/layout/` - deterministic arrangement of every model into rooms (`shiplib.py` helpers,
  `recipes_deck{1,2,3}.py` per-room furnishing). Every one of the 1000 models is placed at least once.
* `godot/scripts/` - `ship_builder.gd` (walls/floors/windows/lights/props from JSON), `player.gd`,
  `door.gd`, `lift.gd`, `hud.gd`, `deck_map.gd`.

## The component library (1000 GLBs)

```mermaid
pie showData
    title Components by domain
    "Engineering" : 135
    "Structure (doors, panels, pipes)" : 130
    "Cargo & hangar" : 130
    "Crew (beds, galley, gym...)" : 125
    "Bridge & command" : 100
    "Security & safety" : 100
    "Lighting & utility" : 85
    "Life support" : 50
    "Science" : 50
    "Comms & computing" : 50
    "Medical" : 45
```

~707k triangles, 36 MB in total; each model is a single mesh (doors have separate `leaf_l` / `leaf_r`
nodes that the game slides open). Emissive screens use generated UI textures (`godot/textures/screens`).

| | |
|---|---|
| ![Gallery 1](docs/screenshots/gallery_1.png) | ![Gallery 2](docs/screenshots/gallery_2.png) |

## The ship

Three decks, 40 rooms, 25 sliding doors + 8 open portals, six turbolift cars (A/B on every deck), a hangar bay with a force-field door. About 6,700 props (~7,000 meshes) furnish it.

```mermaid
flowchart TB
    subgraph D1["Deck 1 - Command (y = 8 m)"]
        direction LR
        BR[Bridge] --- CC1[Command corridor]
        CC1 --- RR[Ready room] & CF[Conference] & OL[Observation lounge] & CM[Comms centre] & AS[Astrometrics] & OQ[Officers' cabins x2] & CQ[Captain's quarters]
        CC1 --- LB1[Lift lobby]
    end
    subgraph D2["Deck 2 - Habitat (y = 4 m)"]
        direction LR
        CC2[Main corridor] --- AR[Armory] & GA[Galley] & MH[Mess hall] & RG[Recreation & gym] & CQR[Crew quarters]
        CC2 --- BG[Brig] & SO[Security office] & MB[Medical bay] & SL[Science lab] & HY[Hydroponics]
        CC2 --- LB2[Lift lobby]
    end
    subgraph D3["Deck 3 - Engineering (y = 0 m)"]
        direction LR
        CC3[Engineering corridor] --- LS[Life support] & CO[Computer core] & WS[Workshop] & CA[Cargo bay 1]
        CC3 --- AL[Airlock] & ME[Main engineering<br/>reactor] & PD[Power distribution] & CB[Cargo bay 2]
        CC3 --- LB3[Lift lobby] --- HG[Hangar bay]
    end
    LB1 <-->|turbolift| LB2 <-->|turbolift| LB3
```

| Deck 1 | Deck 2 | Deck 3 |
|---|---|---|
| ![Deck 1 map](docs/screenshots/map_deck1.png) | ![Deck 2 map](docs/screenshots/map_deck2.png) | ![Deck 3 map](docs/screenshots/map_deck3.png) |

### A tour

| | |
|---|---|
| ![Window](docs/screenshots/02_bridge_window.png) | ![Lounge](docs/screenshots/04_observation_lounge.png) |
| ![Corridor](docs/screenshots/08_main_corridor.png) | ![Medical](docs/screenshots/11_medical_bay.png) |
| ![Hydroponics](docs/screenshots/13_hydroponics.png) | ![Computer core](docs/screenshots/20_computer_core.png) |
| ![Astrometrics](docs/screenshots/06_astrometrics.png) | ![Cargo bay](docs/screenshots/22_cargo_bay.png) |
| ![Airlock](docs/screenshots/23_airlock.png) | ![Reactor](docs/screenshots/19_engineering_reactor.png) |

## Interior experience

* **Every room is furnished for its job.** Hand-written recipes (`recipes_deck*.py`) place the signature equipment
  (bridge stations facing the viewport, reactor with guard rails, mess tables with benches, hydroponic beds ...),
  then a *garnish* pass tops each room up to a target density from its department's own equipment
  (medical gear in the medbay, coils and capacitors in engineering, ...). Small items stand on tables and desks.
* **Clear walkways.** Corridors and lobbies are kept free, doorways have clearance zones and windows are never
  blocked; `tests/test_walkable.py` flood-fills each deck with the player's capsule to prove every room is reachable.
* **Atmosphere.** Baseboards, department-coloured stripes and glowing cove lines on every wall, one-shot
  reflection probes per room (metal and glass reflect the room), subtle volumetric haze in the light beams.
* **Sound** (procedurally generated by `tools/audio/generate_audio.py`): ship hum that changes by department, engine
  rumble in engineering, footsteps, door swish and a turbolift chime.
* **Spares Depot.** Anything not otherwise needed is racked in tidy sorted rows in the Spares Depot on Deck 3.

## Realism notes

* Real-world metric scale (doors 2.0 x 2.6 m, 3.4 m ceilings, 4 m deck pitch); wall thickness, floor and ceiling slabs.
* PBR materials: Blender-generated albedo / normal / ORM maps (tread plate, grating, carpet, panelled
  bulkheads, perforated ceiling tiles) applied with world-space triplanar mapping, so walls tile seamlessly.
* Ceiling downlights are shadow-casting spot lights placed with the fixture models; console glow, reactor and
  hydroponics lights are coloured omni lights; SSAO, glow and filmic tone mapping.
* Windows (bridge, lounge, astrometrics, hydroponics, captain's quarters) look out on a star panorama and a
  planet lit by a sun that lights only the outside (render layer 2), so nothing bleeds into the interior.
* Props sit on wall / floor / ceiling with footprint collision avoidance and door clearance; small items stand
  on tables and desks using each model's measured top surface (`top_y`); solid props have box colliders.
* Visibility ranges by object size keep the ~7,000 meshes cheap to draw.

## CI

```mermaid
flowchart LR
    PR[push / PR] --> P[python<br/>compile, unit tests,<br/>layout reproducible]
    PR --> BL[blender<br/>bpy: regenerate 1000 GLBs,<br/>catalog matches]
    PR --> GD[godot<br/>import, smoke test,<br/>tour screenshots]
    GD --> A[(screenshots artifact)]
    BL --> A2[(regenerated GLBs artifact)]
```

Local checks: `python -m unittest discover -s tests -v` (catalog, layout and walkability) and
`godot --headless --path godot -s res://tests/smoke_test.gd`.

Tour screenshots (also used for this README): `godot --path godot -- --tour=/tmp/shots [--only=01_bridge,...] [--no-probes] [--no-fog]`.
Contact sheets of any GLBs: `GODOT=godot tools/preview/run.sh sheet.png godot/models/console/*.glb`.

## Versions

Blender 5.2 (`bpy` module on PyPI) and Godot 4.7 were used to build and verify this project.
CI installs the latest `bpy` from PyPI and the Godot version in `.github/workflows/ci.yml` (`GODOT_VERSION`,
overridable from *Run workflow*).

## License

See [LICENSE](LICENSE).
