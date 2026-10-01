"""Screen texture families (pure python, no bpy / numpy).

The component modules ask for a generic screen ("radar", "power", ...).  `resolve()` maps that deterministically
(CRC of model id + texture name) onto one of several themed variants, so the 1000 models show ~60 different
displays instead of 21 without changing any model id, count or catalogue size.  The first entry of each family is
the original texture, so a model whose hash picks index 0 is unchanged.
"""
import zlib

FAMILIES = {
    "radar": ("radar", "radar_sector", "sensor_sweep", "docking"),
    "waveform": ("waveform", "lissajous", "comms_spectrum", "waterfall", "ecg_multi"),
    "graph": ("graph", "graph_lines", "engine_temp", "fuel_status"),
    "text": ("text", "log_list", "terminal", "schedule", "crew_roster"),
    "starmap": ("starmap", "star_chart", "orbits", "asteroids", "planet_survey"),
    "schematic": ("schematic", "reactor_core", "warp_coils", "coolant_flow", "damage_control"),
    "bars": ("bars", "cargo_manifest", "inventory_grid", "fuel_status"),
    "warp": ("warp", "warp_coils", "reactor_core", "shield_status"),
    "vitals": ("vitals", "ecg_multi", "dna", "body_scan"),
    "power": ("power", "power_grid", "life_support", "engine_temp"),
    "nav": ("nav", "nav_course", "deck_map", "docking"),
    "alert": ("alert", "airlock_cycle", "radiation", "floor_indicator"),
    "tactical": ("tactical", "weapons", "shield_status", "security_grid"),
    "systems": ("systems", "atmosphere", "life_support", "power_grid", "hydro_status"),
    "lifesigns": ("lifesigns", "crew_roster", "body_scan", "ecg_multi"),
    "comm": ("comm", "uplink", "comms_spectrum", "waterfall"),
    "medical": ("medical", "body_scan", "dna", "assay", "thermal"),
    "periodic": ("periodic", "assay", "inventory_grid", "cargo_manifest"),
    "hazard": ("hazard", "radiation", "alert", "airlock_cycle"),
    "diagnostic": ("diagnostic", "log_list", "terminal", "thermal", "graph_lines"),
    "globe": ("globe", "planet_survey", "orbits"),
}


def resolve(material, model_id):
    """'screen:radar' + model id -> 'screen:<variant>'; anything else is returned unchanged."""
    if not isinstance(material, str) or not material.startswith("screen:"):
        return material
    tex = material.split(":", 1)[1]
    fam = FAMILIES.get(tex)
    if not fam:
        return material
    return "screen:" + fam[zlib.crc32(f"{model_id}|{tex}".encode()) % len(fam)]


def all_variants():
    return sorted({v for fam in FAMILIES.values() for v in fam})
