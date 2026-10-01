"""Recipes for the circulation spaces shared by every deck: spine corridors, the mid-ship stair lobby and
the two stair towers.  Nothing stands on the floor of a corridor - 3 m of clear width is the escape route;
everything is wall / ceiling mounted and placed at regular *stations* like on a real ship."""
from dressing import *   # noqa: F401,F403

DEPT_SIGN = {   # destination room -> department sign model label
    "bridge": "dept_bridge", "ready": "dept_bridge", "conf": "dept_bridge", "comms": "dept_bridge",
    "mess": "dept_mess", "galley": "dept_mess", "medbay": "dept_medical", "sci": "dept_science", "astro": "dept_science",
    "armory": "dept_security", "brig": "dept_security", "secoff": "dept_security",
    "eng": "dept_engineering", "shop": "dept_engineering", "aux": "dept_engineering", "core": "dept_engineering",
    "life": "dept_engineering", "cargo": "dept_cargo", "depot": "dept_cargo", "hangar": "dept_hangar",
    "airlock": "dept_airlock", "lounge": "dept_quarters", "capt": "dept_quarters", "cabinA": "dept_quarters",
    "cabinB": "dept_quarters", "dorm": "dept_quarters", "rec": "dept_quarters", "hydro": "dept_science",
    "starcart": "dept_science", "observ": "dept_science", "theatre": "dept_bridge", "wardroom": "dept_mess",
    "library": "dept_quarters", "arbor": "dept_science", "flag": "dept_quarters", "antimatter": "dept_engineering",
    "provisions": "dept_cargo", "water": "dept_engineering", "waste": "dept_engineering", "fab": "dept_engineering",
    "auxctl": "dept_bridge", "hold": "dept_cargo", "drone": "dept_hangar",
}


def near(R, side, m, at, y=None, spread=3.0, step=0.35):
    """Hang wall item `m` as close as possible to position `at` along the wall (tries alternately either side)."""
    if m is None:
        return None
    k = 0
    while k * step <= spread:
        for sgn in ((0,) if k == 0 else (1, -1)):
            p = R.wall_item(side, m, at + sgn * k * step, y=y)
            if p:
                return p
        k += 1
    return None


def _stations(a, b, step, off=0.0):
    """Regular stations along [a, b] (frame spacing)."""
    n = max(1, int((b - a) // step))
    pad = ((b - a) - (n - 1) * step) / 2
    return [a + pad + i * step + off for i in range(n)]


def corridor(R, B, label):
    c = B.cat
    z0, z1 = R.z0 + 0.3, R.z1 - 0.3
    R.describe(
        "%s spine corridor: the 3 m wide fore-aft escape route and service way of the deck; every room on this side opens onto it." % R.name.split()[0],
        basis="Clear width 3.0 m (two people plus a stretcher); no floor-standing items; all equipment is wall or ceiling mounted "
              "at a 6 m station spacing; extinguishers every 12 m; emergency lighting every 6 m.",
        adjacency="Doors to every room of its deck half; open arch to the mid-ship stair lobby.")
    R.line("Ceiling lighting", "Linear troffers at about 5 m pitch give 200 lux along the escape route without glare.")
    R.light_grid(cats=("ceilinglight",), spacing=5.0, energy=1.2, color="#f2f6ff", shadow_every=4, x_margin=0.5,
                 pred=lambda m: m["size"][0] < 1.4 and m["size"][2] < 1.4 and m["mount"] == "ceiling" and m["size"][1] < 0.3)
    R.line("Emergency lighting and public address",
           "Battery-backed emergency lights and PA speakers at 6 m stations keep the route lit and announce alerts during a power or pressure emergency.")
    for i, z in enumerate(_stations(z0, z1, 6.0)):
        side = "W" if i % 2 == 0 else "E"
        near(R, side, c.pick("beacon", label="emergency_lighting_unit"), z, y=2.55)
        near(R, "E" if side == "W" else "W", c.pick("beacon", label="intercom_speaker"), z + 3.0, y=2.55)
    R.line("Fire extinguishers", "A fire extinguisher within 12 m of any point of the route is the regulation for an occupied corridor.")
    for i, z in enumerate(_stations(z0 + 1.0, z1 - 1.0, 12.0)):
        near(R, "W" if i % 2 else "E", c.pick("safety", label="fire_extinguisher"), z, y=1.1)
    R.line("Department wayfinding signs",
           "A department sign above each door on the corridor side tells crew what lies behind it, so nobody opens the wrong hatch in an emergency.")
    for lk in R.links:
        tgt = lk["to"]
        if lk["kind"] == "open" or tgt not in DEPT_SIGN or lk["side"] not in ("E", "W"):
            continue
        m = c.pick("sign", label=DEPT_SIGN[tgt])
        if m and m["mount"] == "wall":
            R.wall_item(lk["side"], m, lk["c"], y=3.0, check=False)
    R.line("Overhead cable tray and ventilation trunk",
           "Power and data cable trays plus a ventilation trunk run above the corridor so every room on the deck can be fed without floor penetrations.")
    ix0, iz0, ix1, iz1 = R.inner()
    for cats, xoff in (("cabletray", -0.85), ("duct", 0.85)):
        z = iz0 + 0.3
        while z < iz1 - 0.3:
            m = c.pick(cats, pred=lambda m: m["mount"] == "ceiling" and m["size"][0] >= 1.0 and m["size"][2] < 0.6)
            if m is None:
                break
            ln = m["size"][0]
            if not R.place(m, R.cx + xoff, z + ln / 2, 90.0, y=R.y + R.h, check=True):
                z += 0.5
                continue
            z += ln + 0.05
    R.line("Deck evacuation map", "Crew must be able to find the nearest stair from any corridor; the route map sits next to the stair lobby.")
    at_lobby = R.z0 + 1.6 if R.id.startswith("corA") else R.z1 - 1.6
    near(R, "W", c.pick("safety", label="evac_route_map"), at_lobby, y=1.5)
    if R.id.startswith("corA"):
        R.line("Drinking fountain", "Crew working aft need water without going to the mess; a wall fountain at wheelchair height is fitted on the aft corridor.")
        near(R, "E", c.pick("fountain", label="drinking_fountain"), R.cz, y=0.9, spread=4.0)


def f_corF(R, B): corridor(R, B, "forward")
def f_corA(R, B): corridor(R, B, "aft")


def f_lobby(R, B):
    c = B.cat
    R.describe(
        "Mid-ship cross passage that joins the two stair towers and both halves of the spine corridor; the only place a deck changes.",
        basis="3.6 m deep, 12.8 m long. Only wall-mounted equipment and low benches against the walls; the centre stays clear for two-way traffic on the stairs.",
        adjacency="Fore and aft spine corridors, port and starboard stair towers.")
    deck = R.deck
    R.line("Ceiling lighting", "A row of panel lights bright enough (300 lux) to read the signs and safely see the stair entrance.")
    R.light_grid(cats=("ceilinglight",), spacing=4.0, energy=1.4, color="#f4f8ff", shadow_every=3, x_margin=0.8,
                 pred=lambda m: m["size"][0] < 1.4 and m["size"][2] < 1.4 and m["size"][1] < 0.3)
    R.line("Waiting benches", "Padded benches against the walls give somewhere to wait for the next shift change without blocking the route.")
    for x in (-4.3, 4.3):
        near(R, "S" if x < 0 else "N", c.pick("bench", label="padded_wall_bench"), x, y=None, spread=0.8)
    if deck == 2:
        R.line("Vending machines", "The habitat deck is the crew's living deck; drink and snack machines at the stair lobby save a walk to the mess hall.")
        for x in (-2.3, 2.3):
            m = c.pick("vending", pred=lambda m: m["size"][0] < 1.3)
            if m:
                R.against_wall("N" if x < 0 else "S", m, x, gap=0.03)
    R.line("Deck number signs", "Large deck numbers above each arch stop crew from taking the wrong flight of stairs.")
    sign = c.pick("sign", label="deck_%d" % deck)
    near(R, "N", sign, -3.9, y=2.55)
    near(R, "S", sign, 3.9, y=2.55)
    R.line("Deck plan boards", "A you-are-here plan board at each side of the passage shows the layout of the deck and the two stair locations.")
    near(R, "N", c.pick("display", label="deck_plan_board"), 4.2, y=1.75)
    near(R, "S", c.pick("display", label="deck_plan_board"), -4.2, y=1.75)
    R.line("Fire fighting and first aid", "Extinguisher and first-aid cabinet sit beside the stairs, the most likely meeting point during an emergency.")
    near(R, "N", c.pick("safety", label="fire_extinguisher"), -2.4, y=1.1)
    near(R, "S", c.pick("safety", label="fire_extinguisher"), 2.4, y=1.1)
    near(R, "N", c.pick("safety", label="first_aid_cabinet"), 2.4, y=1.5)
    near(R, "S", c.pick("safety", label="evac_route_map"), -2.4, y=1.5)
    R.line("Notice board and duty roster", "Watch bills and notices are posted where everybody passes every day.")
    near(R, "N", c.pick("noticeboard", label="duty_roster"), 5.4, y=1.75)
    near(R, "S", c.pick("noticeboard", label="digital_message"), -5.4, y=1.75)
    R.line("Overhead services", "Fire-suppression nozzles and air diffusers in the ceiling of the busiest junction of the deck.")
    for x in (-5.0, 5.0):
        R.place(c.pick("duct", label="ceiling_square_diffuser"), x, R.cz, 0.0, y=R.y + R.h)
    R.place(c.pick("safety", label="sprinkler_head"), 0.0, R.cz, 0.0, y=R.y + R.h)


def _tower(R, B, side):
    c = B.cat
    deck = R.deck
    xa, xb = R.x0, R.x1
    strip_mid = (xb - 0.15 - 0.9) if side == "A" else (xa + 0.15 + 0.9)
    sgn = 1 if side == "A" else -1
    R.describe(
        "Dog-leg stair tower linking all three decks on the %s side; two 1.4 m flights and a mid-landing per deck pair." %
        ("port" if side == "A" else "starboard"),
        basis="Rise 181.8 mm, going 280 mm, 11 risers per flight, 4.0 m floor-to-floor; 0.9 m handrails on both sides; second means of escape.",
        adjacency="Opens to the mid-ship stair lobby through a 3.2 m wide arch.")
    R.line("Stair level signage", "Deck number plate and exit arrow at the landing tell people which level they are on and where the exit is.")
    near(R, "N", c.pick("sign", label="deck_%d" % deck), strip_mid, y=2.0, spread=0.6)
    near(R, "S", c.pick("sign", label="exit_arrow"), strip_mid, y=2.4, spread=0.6)
    R.line("Fire extinguisher and emergency lighting", "Stair towers are protected escape routes: a hand extinguisher and battery lights are mandatory at every level.")
    near(R, "S", c.pick("safety", label="fire_extinguisher"), strip_mid + 0.5 * sgn, y=1.1, spread=0.6)
    near(R, "N", c.pick("beacon", label="emergency_lighting_unit"), strip_mid + 0.5 * sgn, y=2.8, spread=0.6)
    R.line("Stair lighting", "Recessed downlights over the deck-level strip and, where the ceiling is solid, over the landing light every tread; the stairs are the main way between decks.")
    for x in (strip_mid, (xa + xb) / 2 - 1.2 * sgn, (xa + xb) / 2 - 3.4 * sgn):
        m = c.pick("ceilinglight", pred=lambda m: m["mount"] == "ceiling" and m["size"][0] < 0.7 and m["size"][2] < 0.7 and m["size"][1] < 0.4)
        if m:
            R.place(m, x, R.cz, 0.0, y=R.y + R.h)
    R.lights.append({"type": "omni", "pos": [round((xa + xb) / 2, 2), round(R.y + R.h - 0.4, 2), round(R.cz, 2)],
                     "energy": 1.6, "color": "#eaf2ff", "range": 9.0, "shadow": False})
    R.lights.append({"type": "omni", "pos": [round((xa + xb) / 2, 2), round(R.y + 1.2, 2), round(R.cz, 2)],
                     "energy": 0.8, "color": "#ffe9c8", "range": 7.0, "shadow": False})


def f_towerA(R, B): _tower(R, B, "A")
def f_towerB(R, B): _tower(R, B, "B")
