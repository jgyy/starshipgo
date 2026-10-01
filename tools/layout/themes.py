"""Per-room surface themes (pure python, no bpy).

`theme_for(room_id, dept)` returns the texture *kinds* (names of godot/textures/surfaces/<kind>_{albedo,normal,orm}.png)
the Godot ship builder should use for that room's shell:

    wall        wall surfaces
    floor       floor
    ceiling     ceiling
    trim        skirting / accent strips around doors and windows (key "trim" in ship_builder._mat_for)
    accent_tex  frames (door / window frames, key "frame")
    clad        outer hull plating of that room (keys clad / roof / belly) - varies per department
    tint_wall   0..1 how much of the room's pastel `tint` colour is multiplied over the wall texture (0 = none)
    tint_floor  same for the room's `floor_tint`

generate_ship.py writes the dict to ship.json as room["mats"]; the Godot side falls back to the old behaviour for
rooms without it.  Rooms are matched by exact id first, then by prefix (corF1 -> "corF", lobby2 -> "lobby", ...),
then by department (DEPT_THEME), so the two future decks need no entries here.
"""

ROOM_THEME = {
    # ---- command
    "bridge": {"wall": "panel_cmd_blue", "floor": "carpet_geo_blue", "ceiling": "ceiling", "trim": "alu_anodised_blue", "accent_tex": "alu_graphite"},
    "ready": {"wall": "panel_grey", "floor": "carpet_tweed_navy", "ceiling": "ceiling", "trim": "alu_silver", "accent_tex": "alu_graphite"},
    "conf": {"wall": "wood_oak", "floor": "carpet_stripe_navy", "ceiling": "acoustic_panel_grey", "trim": "alu_silver", "accent_tex": "wood_walnut"},
    "comms": {"wall": "panel_cmd_blue", "floor": "rubber_floor_black", "ceiling": "perforated_dark", "trim": "alu_anodised_blue", "accent_tex": "gunmetal_blasted"},
    "core": {"wall": "hex_plate_dark", "floor": "hex_plate_steel", "ceiling": "perforated_dark", "trim": "alu_anodised_blue", "accent_tex": "titanium_brushed"},
    # ---- crew
    "lounge": {"wall": "wood_walnut", "floor": "carpet_tweed_red", "ceiling": "ceiling", "trim": "wood_teak", "accent_tex": "brass_brushed"},
    "cabin": {"wall": "laminate_beige", "floor": "carpet_tweed_grey", "ceiling": "ceiling", "trim": "wood_oak", "accent_tex": "alu_silver"},
    "capt": {"wall": "wood_mahogany", "floor": "carpet_geo_burgundy", "ceiling": "ceiling", "trim": "brass_brushed", "accent_tex": "wood_walnut"},
    "galley": {"wall": "ceramic_subway_white", "floor": "ceramic_tile_sand", "ceiling": "laminate_white", "trim": "steel_brushed", "accent_tex": "steel_brushed"},
    "mess": {"wall": "panel_crew_beige", "floor": "wood_parquet", "ceiling": "ceiling", "trim": "wood_teak", "accent_tex": "alu_silver"},
    "rec": {"wall": "panel_crew_beige", "floor": "rubber_floor_grey", "ceiling": "acoustic_panel_grey", "trim": "alu_anodised_red", "accent_tex": "alu_silver"},
    "dorm": {"wall": "laminate_beige", "floor": "carpet_loop_beige", "ceiling": "ceiling", "trim": "wood_oak", "accent_tex": "alu_silver"},
    # ---- science / medical / life
    "astro": {"wall": "panel_sci_violet", "floor": "carpet_hex_teal", "ceiling": "ceiling", "trim": "alu_anodised_teal", "accent_tex": "titanium_brushed"},
    "sci": {"wall": "laminate_white", "floor": "ceramic_tile_white", "ceiling": "laminate_white", "trim": "alu_anodised_blue", "accent_tex": "alu_silver"},
    "medbay": {"wall": "laminate_clinic_blue", "floor": "ceramic_tile_white", "ceiling": "laminate_white", "trim": "alu_anodised_teal", "accent_tex": "alu_silver"},
    "hydro": {"wall": "panel_life_green", "floor": "ceramic_tile_green", "ceiling": "laminate_white", "trim": "alu_anodised_teal", "accent_tex": "steel_brushed"},
    "life": {"wall": "panel_life_green", "floor": "diamond_plate_steel", "ceiling": "insulation_blanket", "trim": "steel_brushed", "accent_tex": "steel_brushed"},
    # ---- security
    "armory": {"wall": "panel_sec_red", "floor": "diamond_plate_dark", "ceiling": "riveted_plate_grey", "trim": "gunmetal_blasted", "accent_tex": "gunmetal_blasted"},
    "brig": {"wall": "concrete_smooth", "floor": "epoxy_floor_grey", "ceiling": "concrete_rough", "trim": "steel_brushed", "accent_tex": "gunmetal_blasted"},
    "secoff": {"wall": "panel_grey", "floor": "carpet_tweed_grey", "ceiling": "ceiling", "trim": "alu_anodised_red", "accent_tex": "alu_graphite"},
    "airlock": {"wall": "panel_sec_red", "floor": "hazard_floor", "ceiling": "riveted_plate_steel", "trim": "steel_brushed", "accent_tex": "gunmetal_blasted"},
    # ---- engineering
    "eng": {"wall": "panel_eng_orange", "floor": "diamond_plate_steel", "ceiling": "riveted_plate_grey", "trim": "copper_brushed", "accent_tex": "steel_brushed"},
    "shop": {"wall": "panel_grey", "floor": "diamond_plate_dark", "ceiling": "perforated_mesh", "trim": "steel_brushed", "accent_tex": "gunmetal_blasted"},
    "aux": {"wall": "panel_eng_orange", "floor": "grating", "ceiling": "riveted_plate_steel", "trim": "copper_brushed", "accent_tex": "steel_brushed"},
    # ---- cargo
    "cargo": {"wall": "panel_cargo_yellow", "floor": "cargo_deck_lanes", "ceiling": "riveted_plate_big", "trim": "hazard_floor", "accent_tex": "steel_brushed"},
    "depot": {"wall": "concrete_poured", "floor": "cargo_deck_lanes", "ceiling": "riveted_plate_big", "trim": "hazard_floor", "accent_tex": "steel_brushed"},
    "hangar": {"wall": "armour_clean", "floor": "cargo_deck_lanes", "ceiling": "riveted_plate_big", "trim": "hazard_floor", "accent_tex": "armour_dark"},
    # ---- transit (corridors, lobbies, stair towers); matched by prefix
    "corF": {"wall": "panel_white", "floor": "rubber_floor_grey", "ceiling": "ceiling", "trim": "alu_anodised_blue", "accent_tex": "alu_silver"},
    "corA": {"wall": "panel_grey", "floor": "rubber_floor_grey", "ceiling": "ceiling", "trim": "alu_anodised_blue", "accent_tex": "alu_graphite"},
    "lobby": {"wall": "panel_white", "floor": "marble_white", "ceiling": "ceiling", "trim": "alu_silver", "accent_tex": "alu_anodised_gold"},
    "tower": {"wall": "concrete_smooth", "floor": "diamond_plate_alu", "ceiling": "ceiling", "trim": "steel_brushed", "accent_tex": "alu_graphite"},
}

# outer hull plating per department (ship_builder keys clad / roof / belly)
HULL_BY_DEPT = {
    "command": "armour_clean", "crew": "hull_plate", "science": "armour_clean", "medical": "armour_clean",
    "life": "hull_plate", "security": "armour_dark", "engineering": "armour_weathered", "cargo": "armour_dark",
    "transit": "hull_plate",
}

DEPT_THEME = {
    "command": {"wall": "panel_cmd_blue", "floor": "carpet_tweed_navy", "ceiling": "ceiling", "trim": "alu_anodised_blue", "accent_tex": "alu_graphite"},
    "crew": {"wall": "panel_crew_beige", "floor": "carpet_tweed_grey", "ceiling": "ceiling", "trim": "wood_oak", "accent_tex": "alu_silver"},
    "science": {"wall": "laminate_white", "floor": "ceramic_tile_white", "ceiling": "laminate_white", "trim": "alu_anodised_blue", "accent_tex": "alu_silver"},
    "medical": {"wall": "laminate_clinic_blue", "floor": "ceramic_tile_white", "ceiling": "laminate_white", "trim": "alu_anodised_teal", "accent_tex": "alu_silver"},
    "life": {"wall": "panel_life_green", "floor": "ceramic_tile_green", "ceiling": "laminate_white", "trim": "alu_anodised_teal", "accent_tex": "steel_brushed"},
    "security": {"wall": "panel_sec_red", "floor": "diamond_plate_dark", "ceiling": "riveted_plate_grey", "trim": "gunmetal_blasted", "accent_tex": "gunmetal_blasted"},
    "engineering": {"wall": "panel_eng_orange", "floor": "diamond_plate_steel", "ceiling": "riveted_plate_grey", "trim": "copper_brushed", "accent_tex": "steel_brushed"},
    "cargo": {"wall": "panel_cargo_yellow", "floor": "cargo_deck_lanes", "ceiling": "riveted_plate_big", "trim": "hazard_floor", "accent_tex": "steel_brushed"},
    "transit": {"wall": "panel_white", "floor": "rubber_floor_grey", "ceiling": "ceiling", "trim": "alu_anodised_blue", "accent_tex": "alu_silver"},
}

# kinds that already carry the room's own pastel colour: the wall / floor tints of the room are multiplied over them
_TINTABLE_WALL = {"laminate_white", "laminate_beige", "laminate_grey", "laminate_clinic_blue", "panel_white", "panel_grey",
                  "concrete_smooth", "concrete_poured", "panel_crew_beige"}
_TINTABLE_FLOOR = {"carpet_tweed_grey", "carpet_tweed_navy", "carpet_loop_beige", "rubber_floor_grey", "epoxy_floor_grey"}


def kinds_used():
    """Every texture kind the themes reference (the tests check each one exists on disk)."""
    out = set(HULL_BY_DEPT.values())
    for table in (ROOM_THEME, DEPT_THEME):
        for t in table.values():
            out.update(v for k, v in t.items() if not k.startswith("tint"))
    return sorted(out)


def _lookup(room_id, dept):
    if room_id in ROOM_THEME:
        return ROOM_THEME[room_id]
    # longest prefix wins; trailing digits / letters+digits of numbered ids (corF1, cabinA, towerB2) are ignored
    best = None
    for key in ROOM_THEME:
        if room_id.startswith(key) and (best is None or len(key) > len(best)):
            best = key
    if best:
        return ROOM_THEME[best]
    return DEPT_THEME.get(dept, DEPT_THEME["transit"])


def theme_for(room_id, dept):
    """Texture kinds for one room (a fresh dict)."""
    t = dict(_lookup(room_id, dept))
    t["clad"] = HULL_BY_DEPT.get(dept, "hull_plate")
    t["tint_wall"] = 0.6 if t["wall"] in _TINTABLE_WALL else 0.0
    t["tint_floor"] = 0.6 if t["floor"] in _TINTABLE_FLOOR else 0.0
    return t
