# Interactive screens and terminals

Every screen in the ship is a working console. Walk up to a monitor, look at it (the crosshair turns into a ring and the
screen gets a thin cyan frame), read the prompt `[E] Use NAVIGATION (Helm Console)` and press **E**. A full-screen terminal
opens with a real application: a star chart you can rotate, a reactor you can SCRAM, doors you can lock, a replicator that
dispenses food, a computer with a command line. The world keeps running behind it.

![Looking at a screen](screenshots/ui_prompt.png)

## Controls

| Key / mouse | Effect |
| --- | --- |
| `E` | Open the screen or machine under the crosshair (within 3 m, in front of it). While a terminal is open `E` closes it (except when you are typing into a text field). |
| `Esc` or the **CLOSE** button | Close the terminal; mouse capture and player control return. |
| mouse | Click buttons, drag sliders, pick table rows, drag/scroll in the star map and holo projector. |
| `WASD`, mouse look, `F`, `M`, `H` | Suspended while a terminal is open (no ghost input). |

Machines without a screen (reactors, lockers, scanners, ...) give a **machine data card**: catalogue facts plus whatever
`godot/data/specs.json` knows (manufacturer, mass, power, price, MTBF, interfaces); a missing file or entry degrades to the
catalogue data only.

The HUD (top right) shows `ALERT GREEN   DEST: KEPLER GATE   ETA 8.0 d` and follows the ship state.

## Architecture

```mermaid
flowchart LR
  subgraph build["build time (ShipBuilder hooks)"]
    GLB["GLB models<br/>materials screen_*"] --> MO["_meshes_of(): index_model()"]
    MO --> SR[ScreenRegistry]
    BP["_build_props(): add_prop()"] --> SR
    AC[AppCatalog<br/>texture / room / model to app] --> SR
    BP --> LG["lights join group<br/>ship_lights"]
    BP --> FF["hangar force field<br/>registered"]
    BP --> DR["doors carry rooms a/b"]
  end
  subgraph run["run time"]
    CAM[player camera] -->|"10 Hz analytic ray vs quad / box<br/>3 m, 35 degree cone, front facing"| SR
    SR -->|current target| HUD[HUD prompt + ring + frame]
    HUD -->|E| T[Terminal overlay]
    T --> APP["AppBase subclass<br/>scripts/ui/apps/id.gd"]
    APP <--> ST[ShipState]
    ST -->|alert| LG
    ST -->|lock| DR
    ST -->|field on/off| FF
    ST -->|destination, ETA| HUD
    LORE[("lore.json<br/>specs.json<br/>software.json")] --> APP
  end
```

Key points:

* **Discovery** (`godot/scripts/ui/screen_registry.gd`). `ShipBuilder._meshes_of` hands each model's meshes to
  `ScreenRegistry.index_model`, which finds every surface whose material is named `screen_<texture>`, splits it into
  connected quads and stores, per quad, the model-space centre, normal, in-plane axes `u`/`v`, half sizes, AABB and the
  glTF node name. `_build_props` then calls `add_prop` for each placed prop and the quads become world-space records in a
  per-room list. Props with no screen but that are machines (see `AppCatalog.MACHINE_CATS`) get an oriented-box record. No
  node and no collider is created per screen.
* **Selection** (`ScreenRegistry.update`). Ten times a second: only the player's room and its neighbours are tested;
  candidates are front-facing, within 3.0 m and inside a 35 degree cone; a ray hit on the (slightly widened) quad wins over
  a near miss; the best candidate is held with hysteresis. Screens in neighbouring rooms behind a wall are rejected with one
  physics ray. `ray_quad` and `ray_box` are static, unit-tested functions.
* **State** (`godot/scripts/ship_state.gd`). One `ShipState` node holds everything the consoles read and write: alert level,
  doors, reactor and 15 power consumers, subsystems and repairs, warp, destination and the route, life support, hydroponics,
  cargo, fabricator queue, experiments, crew, messages. It runs no per-frame code except the red-alert pulse (20 Hz, red only);
  `sim(dt)` is driven by the terminal while one is open, a jump is a `SceneTreeTimer`, the stardate and clock derive from the
  wall clock.
* **Terminal** (`godot/scripts/ui/terminal.gd`). A `CanvasLayer` overlay with a console frame, scanlines, a status line and the
  hosted app. Opening releases the mouse and calls `player.set_ui_locked(true)`; closing restores them. The app is refreshed at
  4 Hz and on every `ShipState.changed`.
* **Which app?** (`godot/scripts/ui/app_catalog.gd`). Model id and category overrides first (a `console_helm` is navigation,
  a `vending_*` is a vending machine, a `clock_*` is a chronometer), then the screen texture (`screen_radar` is sensors,
  `screen_starmap` is the star map, ...); generic textures (text, graph, bars, systems, schematic) take their meaning from the
  room (`galley`: galley replicator, `eng`: engineering, `medbay`: medical, ...) or the department. The built-in tables are
  merged under `godot/data/software.json` (`texture_map`, `fallback`, `apps`) when that spec file is present. The terminal
  title shows the machine and the app, e.g. `HELM CONSOLE  -  NAVIGATION`.

## Effects in the world

| Console | Visible effect |
| --- | --- |
| Alert | Tints and scales every light in group `ship_lights`: yellow = amber, red = pulsing red emergency lighting. Red alert also seals the armory, brig, security office and computer core (switchable). |
| Security / computer `lock` | `door.gd` stays shut, plays a low denial sound and flashes a red light when approached; unlocked doors work again. |
| Docking | The hangar force-field plane disappears and its collider turns off, so you can walk out of the bay. |
| Star map, navigation, `dest` | Sets the destination: shown on the HUD with ETA and in every nav app. JUMP animates a transit and moves the ship (current system, visited rings, log). |
| Power, reactor, life support | Sliders change readouts in the other apps (brownout in the power grid, reactor temperature, oxygen, pressure drop when the hangar field is off). |
| Galley / vending | Dispensing logs a message, plays a click and (vending) spends credits. |

## Application catalogue

All 29 applications plus the machine data card are real `Control` trees built in code (`godot/scripts/ui/apps/<id>.gd`),
sharing the console look of `ui_theme.gd` and the widgets in `widgets.gd` (graphs, meters, dials, free canvas).

| App id | What it does | Screenshot |
| --- | --- | --- |
| `starmap` | **The showpiece.** 3D chart of every system in lore.json: drag to rotate, wheel to zoom, hover tooltip, click to select. Colour = faction, disc size = luminosity, ring = visited, pulsing ring = you, diamond = destination. Side panel: summary, star data, planets table (type, gravity, atmosphere, habitable), faction lore, distance by straight line and by lane, ETA, worst hazard. PLOT COURSE, JUMP, ALL ROUTES (hazard coloured), LABELS, faction filter, search box, mission waypoints tab, legend. | ![](screenshots/ui_starmap.png) |
| `nav` | Position, heading compass, destination and ETA, warp slider, ENGAGE, a top-down chart where a click plots a course, waypoint list. | ![](screenshots/ui_nav.png) |
| `sensors` | Rotating radar sweep with generated contacts per system, range slider, active/passive, scan contact, stellar spectrum. | ![](screenshots/ui_sensors.png) |
| `tactical` | Four shield quadrants, phaser/torpedo arming (raises alert), target list, FIRE. | ![](screenshots/ui_tactical.png) |
| `warp` | Warp factor, eight lattice coil temperatures with the 4800 K limit, engage, plasma vent, history graph. | ![](screenshots/ui_warp.png) |
| `reactor` | Output and coolant sliders, temperature / containment / output / coolant dials, SCRAM and restart, load vs supply graph, fuel. | ![](screenshots/ui_reactor.png) |
| `power` | 15 consumers on buses A/B/C: breakers, allocation sliders, shed non-essential, overload and brownout, history. | ![](screenshots/ui_power.png) |
| `engineering` | Subsystem health with repair queue and stress test, ship schematic, event log. | ![](screenshots/ui_engineering.png) |
| `diagnostics` | Level 1-3 test run across all subsystems with progress and pass/warn/fail results. | ![](screenshots/ui_diagnostics.png) |
| `lifesupport` | O2 / CO2 / temperature / pressure dials, setpoints, fans, scrubbers, history, deck table. | ![](screenshots/ui_lifesupport.png) |
| `atmosphere` | Every room's atmosphere, seal a room, hangar goes to vacuum when the field is off. | ![](screenshots/ui_atmosphere.png) |
| `hydroponics` | Six grow beds, light / nutrient / water / CO2 conditions, growth simulation, harvest into cargo. | ![](screenshots/ui_hydroponics.png) |
| `medical` | Patients with live ECG and vitals, treatment, life signs of all crew, medbay beds. | ![](screenshots/ui_medical.png) |
| `science` | Experiments that run while a terminal is open, periodic table, emission spectrograph. | ![](screenshots/ui_science.png) |
| `comms` | Stations from the factions, carrier tuning, hailing and chat with replies by stance. | ![](screenshots/ui_comms.png) |
| `security` | Lock/unlock the real doors, lockdown, camera feeds, brig cells. | ![](screenshots/ui_security.png) |
| `cargo` | Manifest with search and category filter, hold capacity, jettison, resupply. | ![](screenshots/ui_cargo.png) |
| `fabricator` | Recipes, stock, queue with progress; finished parts land in cargo. | ![](screenshots/ui_fabricator.png) |
| `galley` | Food replicator: the food catalogue from catalog.json with specs. | ![](screenshots/ui_galley.png) |
| `vending` | Drinks and snacks for credits. | ![](screenshots/ui_vending.png) |
| `alert` | Green / yellow / red alert, descriptions, automation, alert log. | ![](screenshots/ui_alert.png) |
| `computer` | Command line: `help status map locate specs lore log list alert lock unlock lockall unlockall dest jump warp hangar scram restart time clear`. | ![](screenshots/ui_computer.png) |
| `deckplan` | Hull outline and rooms by department from ship.json, locked doors, you-are-here, room search. | ![](screenshots/ui_deckplan.png) |
| `logbook` | Crew logs from lore.json with a reader, live ship events, personal entries. | ![](screenshots/ui_logbook.png) |
| `roster` | Crew list with department filter and search, profile, intercom call. | ![](screenshots/ui_roster.png) |
| `clock` | Ship time, stardate, ship-day wheel, stopwatch, countdown. | ![](screenshots/ui_clock.png) |
| `docking` | Hangar force field (world effect), bay doors, clamps, shuttle launch/recall. | ![](screenshots/ui_docking.png) |
| `datapad` | Documents, glossary and timeline from lore.json. | ![](screenshots/ui_datapad.png) |
| `holo` | Rotating wireframe of the hull from the ship.json outlines, deck toggles, you-are-here. | ![](screenshots/ui_holo.png) |
| `datacard` | Machine data card for machines without a screen. | ![](screenshots/ui_datacard.png) |

Different host machines present variants: the title carries the machine label, `screen_lifesigns` opens the medical app on
its life-signs tab, `screen_schematic` opens engineering on the schematic, `screen_periodic` opens the periodic table.

## Data files

* `godot/data/lore.json` - ship, factions, systems (3D position in light-years, star class, faction, kind, visited, planets),
  routes (hazard), waypoints, current position, timeline, logs, datapads, glossary. Every reader (`scripts/ui/lore.gd`)
  degrades to empty data if a key is missing.
* `godot/data/specs.json` - `{"models": {id: {...}}}` machine data cards; shown generically, whatever keys it has.
* `godot/data/software.json` - the software spec's `texture_map` / `fallback` / app titles, merged over the built-ins.

## Command line

```
godot --path godot -- --screen-scan                       # print how many screens/props are interactive, exit 1 if unmapped
godot --path godot -- --ui-shot=starmap,nav --ui-out=DIR  # render apps full screen to DIR/ui_<app>.png and quit
godot --path godot -- --aim-shot=out.png --aim-room=bridge # look at a screen, save the frame with the HUD prompt
```

Screenshots in `docs/screenshots/ui_*.png` are made with:

```
xvfb-run -a -s "-screen 0 1600x900x24" godot --path godot --rendering-driver vulkan --resolution 1280x720 -- \
    --no-probes --ui-shot=starmap,nav,reactor,power,engineering,lifesupport,medical,security,galley,computer,deckplan,alert \
    --ui-out=docs/screenshots
```

An app may define `demo()`; `--ui-shot` calls it after opening so the picture shows something selected.

## Tests

`godot/tests/ui_test.gd` (CI: godot job) builds the whole ship and checks: ray-vs-quad and ray-vs-box math; every placed
`screen_*` prop is registered and maps to an existing app (none unmapped); look-at selection (in front, away, too far, back
face); alert tints the lights and red alert seals doors; a locked door refuses to open; the hangar field toggles plane and
collider; destination, ETA and jump update the ship state; every application is instantiated, ticked, refreshed and driven
with synthetic input (every tab, slider, button, table row, text field); real mouse events through the viewport on the alert
buttons, security lock, docking toggle, star map (click, drag, wheel, PLOT COURSE, JUMP) and galley (DISPENSE); terminal
open/close with `Esc` and `E` and the player lock; every computer command. CI also fails if the log contains
`SCRIPT ERROR`.

## Adding an application

1. Create `godot/scripts/ui/apps/<id>.gd` with `extends AppBase`. Override `build()` (create widgets with the helpers
   `vb hb panel btn check slider meter graph canvas table rich tab_container line_edit`), `refresh()` (pull from `st`, the
   `ShipState`), optionally `tick(dt)` for animation, `demo()` for screenshots. `host` holds the machine
   (`label`, `model`, `room`, `tex`).
2. Add the id and its title to `AppCatalog.APPS` and map textures / rooms / models to it (or list it in
   `software.json`).
3. Mutate the world only through `ShipState` (add a method and a signal there if it needs a visible effect).
4. Run `godot --headless --path godot -s res://tests/ui_test.gd`; the test instantiates every id in `AppCatalog.APPS`.
