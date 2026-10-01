class_name AppCatalog
extends RefCounted
## Which application a screen or machine opens.  The authoritative spec is docs/SOFTWARE_SPEC.md and
## res://data/software.json (apps, texture_map, fallback); the built-in tables below are the defaults used when that
## file is missing or incomplete, and are merged under it.

const APPS := {
	"starmap": "STAR CARTOGRAPHY", "nav": "NAVIGATION", "sensors": "SENSOR ARRAY", "tactical": "TACTICAL",
	"warp": "WARP CORE CONTROL", "reactor": "REACTOR MONITOR", "power": "POWER GRID", "engineering": "ENGINEERING STATUS",
	"lifesupport": "LIFE SUPPORT", "hydroponics": "HYDROPONICS", "medical": "MEDICAL", "science": "SCIENCE LAB",
	"comms": "COMMUNICATIONS", "security": "SECURITY", "cargo": "CARGO MANIFEST", "fabricator": "FABRICATOR",
	"galley": "GALLEY REPLICATOR", "vending": "VENDING", "alert": "ALERT STATUS", "computer": "COMPUTER",
	"deckplan": "DECK PLAN", "logbook": "SHIP'S LOG", "roster": "CREW ROSTER", "clock": "CHRONOMETER",
	"atmosphere": "ATMOSPHERE", "docking": "DOCKING & HANGAR", "diagnostics": "DIAGNOSTICS", "datapad": "DATAPAD",
	"holo": "HOLO PROJECTOR", "datacard": "MACHINE DATA CARD",
}

const TEXTURE_MAP := {
	"radar": "sensors", "waveform": "medical", "graph": "science", "text": "computer", "starmap": "starmap",
	"schematic": "engineering", "bars": "power", "warp": "warp", "vitals": "medical", "power": "power", "nav": "nav",
	"alert": "alert", "tactical": "tactical", "systems": "engineering", "lifesigns": "medical", "comm": "comms",
	"medical": "medical", "periodic": "science", "hazard": "alert", "diagnostic": "diagnostics", "globe": "starmap",
	"off": "computer",
}

## Textures that do not say what the machine is for: the room (or the machine) decides.
const GENERIC := ["text", "graph", "bars", "systems", "schematic", "off", "hazard", "waveform"]

const ROOM_APP := {
	"bridge": "nav", "ready": "computer", "lounge": "logbook", "conf": "starmap", "astro": "sensors", "capt": "logbook",
	"comms": "comms", "armory": "security", "galley": "galley", "mess": "galley", "brig": "security", "secoff": "security",
	"medbay": "medical", "rec": "clock", "dorm": "roster", "sci": "science", "hydro": "hydroponics", "life": "lifesupport",
	"core": "computer", "airlock": "atmosphere", "eng": "engineering", "shop": "fabricator", "cargo": "cargo",
	"aux": "power", "depot": "cargo", "hangar": "docking", "cabinA": "roster", "cabinB": "roster",
}

const DEPT_APP := {
	"command": "computer", "engineering": "engineering", "medical": "medical", "science": "science", "security": "security",
	"crew": "roster", "cargo": "cargo", "life": "lifesupport", "transit": "deckplan",
}

## Model-id / category overrides: the machine itself decides before anything else.
const CATEGORY_APP := {
	"vending": "vending", "clock": "clock", "holo": "holo", "noticeboard": "logbook", "medscanner": "medical",
	"reactor": "reactor", "generator": "power", "capacitor": "power", "scrubber": "lifesupport", "planter": "hydroponics",
	"cryo": "medical", "medbed": "medical", "commsunit": "comms", "antenna": "comms", "cell": "security", "camera": "security",
	"weaponrack": "tactical", "turbine": "reactor", "particle": "warp", "coil": "warp", "microscope": "science", "sciinstrument": "science", "telescope": "sensors",
}

const ID_APP := {
	"galley_food_replicator": "galley", "console_helm": "nav", "console_navigation": "nav", "console_flight_control": "nav",
	"console_science": "science", "console_sensor": "sensors", "console_tactical": "tactical", "console_weapons": "tactical",
	"console_shield_control": "tactical", "console_engineering_status": "engineering", "console_damage_control": "engineering",
	"console_environmental": "lifesupport", "console_communications": "comms", "console_ops": "computer",
	"console_transporter_control": "docking", "display_deck_plan_board": "deckplan", "display_alert_board": "alert",
	"display_power_board": "power", "display_main_viewscreen": "starmap", "display_comms_log_board": "logbook",
	"controlpanel_alert_level": "alert", "controlpanel_airlock_control": "docking", "controlpanel_environment_control": "atmosphere",
	"controlpanel_breaker_bank": "power", "controlpanel_fuse_box": "power", "controlpanel_power_isolator": "power",
	"controlpanel_biometric_scanner": "security", "controlpanel_card_reader": "security", "controlpanel_keypad_lock": "security",
	"forcefield_hangar_field_arch": "docking", "holo_star_map_globe": "starmap", "holo_ship_schematic_projector": "holo",
	"holo_tactical_plinth": "tactical", "holo_briefing_table": "starmap", "noticeboard_duty_roster_display": "roster",
	"terminal_datapad": "datapad", "terminal_datapad_stack": "datapad", "terminal_portable_reader": "datapad",
	"terminal_info_kiosk": "deckplan", "terminal_ticket_kiosk": "deckplan",
	"display_schematics_wall": "holo", "display_vitals_monitor": "medical", "display_tactical_wall_screen": "tactical",
	"analyzer_3d_fabricator": "fabricator", "console_curved_command_desk": "nav", "console_captain_podium": "starmap",
}

## Categories that get a machine data card when they carry no screen.
const MACHINE_CATS := ["console", "controlpanel", "terminal", "reactor", "generator", "medscanner", "analyzer", "locker", "medcabinet",
	"scrubber", "turbine", "capacitor", "cryo", "commsunit", "router", "sciinstrument", "instrument", "microscope", "telescope",
	"holo", "vending", "galley", "weaponrack", "medbed", "cell", "particle", "camera", "display", "clock", "noticeboard",
	"forcefield", "surgical", "tank", "antenna", "beacon", "valve", "junction", "coil", "cleaningbot", "watertank", "gym", "planter"]

static func known_ids() -> Array:
	var ids: Array = APPS.keys()
	var sw := Lore.software()
	var apps: Variant = sw.get("apps", null)
	if apps is Array:
		for a in apps:
			var aid: String = a.get("id", "") if a is Dictionary else String(a)
			if aid != "" and not ids.has(aid):
				ids.append(aid)
	elif apps is Dictionary:
		for aid in apps.keys():
			if not ids.has(aid):
				ids.append(aid)
	return ids

static func has_script(app_id: String) -> bool:
	return ResourceLoader.exists("res://scripts/ui/apps/%s.gd" % app_id)

static func texture_map() -> Dictionary:
	var m: Dictionary = TEXTURE_MAP.duplicate()
	var sw_map: Variant = Lore.software().get("texture_map", null)
	if sw_map is Dictionary:
		for k in (sw_map as Dictionary).keys():
			m[String(k).trim_prefix("screen_")] = sw_map[k]
	return m

static func fallback_app() -> String:
	return String(Lore.software().get("fallback", "computer"))

static func title_of(app_id: String) -> String:
	var apps: Variant = Lore.software().get("apps", null)
	if apps is Array:
		for a in apps:
			if a is Dictionary and a.get("id", "") == app_id and a.get("title", "") != "":
				return String(a["title"]).to_upper()
	elif apps is Dictionary and (apps as Dictionary).has(app_id):
		var a: Variant = apps[app_id]
		if a is Dictionary and a.get("title", "") != "":
			return String(a["title"]).to_upper()
	return String(APPS.get(app_id, app_id.to_upper()))

## Decide the app for a host machine.  `tex` is the screen texture name without the "screen_" prefix ("" when none).
static func resolve(model_id: String, category: String, tex: String, room_id: String, dept: String) -> String:
	var app := ""
	if ID_APP.has(model_id):
		app = ID_APP[model_id]
	elif model_id.contains("warp") or model_id.contains("lattice"):
		app = "warp"
	elif model_id.contains("diagnostic"):
		app = "diagnostics"
	elif CATEGORY_APP.has(category) and not (tex != "" and category in ["generator", "capacitor"]):
		app = CATEGORY_APP[category]
	if app == "" and tex != "":
		var tm := texture_map()
		var mapped: String = tm.get(tex, "")
		if mapped != "" and not (tex in GENERIC):
			app = mapped
		elif ROOM_APP.has(room_id):
			app = ROOM_APP[room_id]
		elif DEPT_APP.has(dept):
			app = DEPT_APP[dept]
		elif mapped != "":
			app = mapped
	if app == "":
		return "datacard" if tex == "" else fallback_app()
	if not has_script(app) and app != "datacard":
		return fallback_app() if has_script(fallback_app()) else "computer"
	return app

static func make(app_id: String) -> AppBase:
	var path := "res://scripts/ui/apps/%s.gd" % app_id
	if not ResourceLoader.exists(path):
		path = "res://scripts/ui/apps/computer.gd"
		app_id = "computer"
	var a: AppBase = (load(path) as GDScript).new()
	a.app_id = app_id
	return a
