class_name ShipState
extends Node
## Shared live state of the ship behind every terminal.  Nothing here runs per frame unless it must:
##  - sim(dt) is driven by the terminal while a terminal is open (drifting readouts, slow physics of the sliders)
##  - the red-alert light pulse needs _process (20 Hz) only while the alert level is red
##  - jumps use a SceneTreeTimer, the stardate and clock are derived from the wall clock on demand
## Real world effects: alert tints the "ship_lights" group, door locks reach door.gd, the hangar field toggles the
## forcefield plane + its collider, the destination feeds the HUD.

signal alert_changed(level: String)
signal door_lock_changed(index: int, locked: bool)
signal destination_changed(system_id: String)
signal jump_started(system_id: String)
signal jumped(system_id: String)
signal hangar_changed(on: bool)
signal log_added(entry: Dictionary)
signal changed

static var instance: ShipState

const LEVELS := ["green", "yellow", "red"]
const REACTOR_MAX_MW := 4000.0
const HIST_LEN := 90

# ---- world links (set by bind_world)
var ship: Dictionary = {}
var catalog: Dictionary = {}
var doors: Array = []                       # door nodes (door.gd); index = door id used by the security app
var hangar_nodes: Array = []                # [{"mesh": MeshInstance3D, "shape": CollisionShape3D}]
var player_room := ""

# ---- navigation
var alert := "green"
var current_system := ""
var destination := ""
var route: Array = []
var visited: Dictionary = {}
var in_transit := false
var transit_from := ""
var transit_to := ""
var transit_start_ms := 0
var jump_seconds := 6.0
var warp := 6.0
var warp_engaged := false
var heading := Vector3(0.2, 0.3, 0.93)

# ---- engineering
var reactor := {"output": 85.0, "temp": 3600.0, "containment": 99.2, "coolant": 88.0, "fuel": 81.0, "scram": false}
var buses: Array = []                       # [{name, demand, alloc, on, group}]
var subsystems: Array = []                  # [{id, name, health, repair}]
var coils: Array = []                       # 8 lattice coil temperatures (K)
var shields := {"fore": true, "aft": true, "port": true, "starboard": true, "strength": 92.0}
var weapons := {"phasers": false, "torpedoes": false, "target": ""}

# ---- life
var life := {"o2": 20.9, "co2": 0.05, "temp": 21.5, "pressure": 101.3, "o2_set": 20.9, "temp_set": 21.5, "scrubbers": true, "fans": 60.0}
var hydro := {"light_h": 16.0, "nutrient": 70.0, "water": 80.0, "co2_boost": false, "beds": []}
var cargo: Array = []
var fab_queue: Array = []
var credits := 120.0
var crew: Array = []                        # [{name, role, dept, room, hr, status, note}]
var sealed: Dictionary = {}                 # room id -> true (atmosphere app)
var stock := {"alloy": 500.0, "polymer": 300.0, "circuits": 120.0}
var experiments: Array = []                 # [{name, progress, running, result}]
var comm_log: Array = []                    # [{who, text, mine}]
var red_auto_lock := true                   # red alert locks the armory, brig, security office and computer core
var _auto_locked: Array = []
var shuttles: Array = []                    # [{name, state}]
var bay_doors_open := false
var dispensed := 0
var messages: Array = []
var hist: Dictionary = {}                   # key -> PackedFloat32Array

var _t0_ms := 0
var _sim_t := 0.0
var _hist_acc := 0.0
var _pulse_acc := 0.0
var _alert_t := 0.0
var _rng := RandomNumberGenerator.new()
var _click: AudioStreamPlayer

func _init() -> void:
	instance = self
	_rng.seed = 1337
	_t0_ms = Time.get_ticks_msec()
	var info := Lore.ship_info()
	warp = float(info.get("cruise_warp", 6.0))
	var cur: Dictionary = Lore.data().get("current", {})
	current_system = cur.get("system", "")
	if current_system == "" and not Lore.systems().is_empty():
		current_system = Lore.systems()[0]["id"]
	var h: Array = cur.get("heading", [0.2, 0.3, 0.93])
	heading = Vector3(h[0], h[1], h[2]).normalized()
	for s in Lore.systems():
		if s.get("visited", false):
			visited[s["id"]] = true
	visited[current_system] = true
	var bus_defs := [
		["Helm / Navigation", 120.0, "A"], ["Sensors", 260.0, "A"], ["Communications", 90.0, "A"], ["Computer core", 180.0, "A"],
		["Shields", 420.0, "B"], ["Weapons", 300.0, "B"], ["Warp lattice", 700.0, "B"], ["Impulse / thrusters", 150.0, "B"],
		["Life support", 240.0, "C"], ["Hydroponics", 110.0, "C"], ["Galley & crew", 85.0, "C"], ["Medical", 95.0, "C"],
		["Science labs", 130.0, "C"], ["Lighting", 70.0, "C"], ["Fabricator & cargo", 160.0, "B"]]
	for b in bus_defs:
		buses.append({"name": b[0], "demand": b[1], "alloc": 100.0, "on": true, "group": b[2]})
	for n in ["Warp lattice", "Reactor containment", "Shield grid", "Sensor array", "Life support", "Hull plating", "Impulse drive", "Computer core", "Comms array", "Hangar systems"]:
		subsystems.append({"id": n.to_lower().replace(" ", "_"), "name": n, "health": float(_rng.randi_range(88, 100)), "repair": false})
	for i in 8:
		coils.append(2600.0 + 40.0 * i)
	for i in 6:
		(hydro["beds"] as Array).append({"name": "Bed %d" % (i + 1), "crop": ["Wheat", "Fern", "Tomato", "Basil", "Potato", "Strawberry"][i], "growth": 15.0 + 13.0 * i, "on": true})
	cargo = [
		{"id": "spares", "name": "Reactor spares", "qty": 12, "mass": 80.0, "cat": "engineering"},
		{"id": "meds", "name": "Medical supplies", "qty": 40, "mass": 12.0, "cat": "medical"},
		{"id": "rations", "name": "Ration packs", "qty": 900, "mass": 1.1, "cat": "food"},
		{"id": "probes", "name": "Survey probes", "qty": 24, "mass": 45.0, "cat": "science"},
		{"id": "alloy", "name": "Hull alloy plate", "qty": 60, "mass": 120.0, "cat": "engineering"},
		{"id": "coils", "name": "Spare lattice coils", "qty": 2, "mass": 640.0, "cat": "engineering"},
		{"id": "mail", "name": "Mail pouches", "qty": 31, "mass": 2.0, "cat": "general"}]
	say("Ship systems nominal. Departure from %s." % Lore.system_name(current_system), "info")
	for k in ["demand", "supply", "o2", "temp", "coil"]:
		var arr := PackedFloat32Array()
		hist[k] = arr
	set_process(false)
	_make_crew()
	for e in [["Gas chromatography of hydroponic exhaust", 140.0], ["Stellar spectrum survey", 90.0], ["Debris-disc dust analysis", 200.0],
			["Hull micro-fracture scan", 60.0], ["Subspace noise floor survey", 120.0], ["Fern allergen assay", 75.0]]:
		experiments.append({"name": e[0], "secs": e[1], "progress": 0.0, "running": false, "result": ""})
	for n in ["Kestrel", "Wren", "Osprey"]:
		shuttles.append({"name": "Shuttle " + n, "state": "docked"})
	for i in 90:                      # warm start: graphs have history and the readouts have settled
		sim(0.5)
	_make_click()

func _make_crew() -> void:
	var people := [
		["Capt. Ilse Varga", "Captain", "command", "capt"], ["Cdr. Teo Marsh", "First Officer", "command", "bridge"],
		["Lt. Naia Okoro", "Helm", "command", "bridge"], ["Lt. Dev Rao", "Communications", "command", "comms"],
		["Lt. Cdr. Sun Ye-jin", "Science Officer", "science", "astro"], ["Dr. Amara Bell", "Chief Medical Officer", "medical", "medbay"],
		["Nurse Pavel Ionescu", "Medical Technician", "medical", "medbay"], ["Maj. Reza Tahir", "Security Chief", "security", "secoff"],
		["Ens. Lin Wei", "Security Officer", "security", "brig"], ["Cdr. Hana Brandt", "Chief Engineer", "engineering", "eng"],
		["Tech. Joao Pires", "Warp Engineer", "engineering", "eng"], ["Tech. Mira Kovacs", "Fabrication Tech", "engineering", "shop"],
		["Ens. Olu Adeyemi", "Power Systems", "engineering", "aux"], ["Dr. Felix Hartmann", "Botanist", "life", "hydro"],
		["Tech. Yara Nasser", "Life Support Tech", "life", "life"], ["Chef Bram de Vries", "Chef", "crew", "galley"],
		["Spc. Tomas Lindqvist", "Quartermaster", "cargo", "cargo"], ["Spc. Keiko Mori", "Hangar Chief", "cargo", "hangar"],
		["Dr. Priya Nair", "Astrophysicist", "science", "sci"], ["Ens. Gus Oyelaran", "Computer Tech", "command", "core"],
		["Spc. Ana Silva", "Cargo Handler", "cargo", "depot"], ["Ens. Mateo Cruz", "Helm Relief", "command", "conf"],
		["Tech. Ruth Abara", "Recreation Officer", "crew", "rec"], ["Spc. Ivo Petrov", "Off-duty", "crew", "dorm"]]
	for i in people.size():
		var p: Array = people[i]
		var status := "ok"
		if i == 6:
			status = "sick"
		elif i == 11:
			status = "injured"
		crew.append({"name": p[0], "role": p[1], "dept": p[2], "room": p[3], "hr": 58 + (i * 7) % 28, "status": status,
			"note": "Mild spore allergy, observation." if status == "sick" else ("Burn on left hand, dressed." if status == "injured" else "Fit for duty.")})

func crew_by_name(n: String) -> Dictionary:
	for c in crew:
		if String(c["name"]).to_lower().contains(n.to_lower()):
			return c
	return {}

func _make_click() -> void:
	var w := AudioStreamWAV.new()
	w.format = AudioStreamWAV.FORMAT_8_BITS
	w.mix_rate = 22050
	var data := PackedByteArray()
	for i in 360:
		var env := 1.0 - float(i) / 360.0
		var v := sin(float(i) * 0.42) * env * 0.6 + (_rng.randf() - 0.5) * 0.15 * env
		data.append(int(clampf(v, -1.0, 1.0) * 100.0) & 0xff)
	w.data = data
	_click = AudioStreamPlayer.new()
	_click.stream = w
	_click.volume_db = -12.0
	add_child(_click)

func click() -> void:
	if _click != null and is_inside_tree():
		_click.pitch_scale = _rng.randf_range(0.9, 1.15)
		_click.play()

func bind_world(builder: Node) -> void:
	ship = builder.ship
	catalog = builder.catalog
	doors = builder.doors
	hangar_nodes = builder.hangar_fields
	set_hangar_field(hangar_field_on, false)

var hangar_field_on := true

# ------------------------------------------------------------------ time
func stardate() -> float:
	return 47650.0 + float(Time.get_ticks_msec() - _t0_ms) / 1000.0 * 0.01

func ship_clock() -> String:
	var s := int(14 * 3600 + 20 * 60 + (Time.get_ticks_msec() - _t0_ms) / 1000.0 * 12.0) % 86400
	return "%02d:%02d:%02d" % [s / 3600, (s / 60) % 60, s % 60]

func elapsed() -> float:
	return float(Time.get_ticks_msec() - _t0_ms) / 1000.0

func say(text: String, kind := "info") -> void:
	var e := {"t": "%.2f" % stardate(), "text": text, "kind": kind}
	messages.append(e)
	if messages.size() > 300:
		messages.pop_front()
	log_added.emit(e)

# ------------------------------------------------------------------ alert level
func set_alert(level: String) -> bool:
	level = level.to_lower()
	if not level in LEVELS:
		return false
	if level == alert:
		return true
	alert = level
	_alert_t = 0.0
	apply_alert_lights()
	set_process(alert == "red" and is_inside_tree())
	say("ALERT LEVEL %s" % level.to_upper(), "alert")
	_auto_lock_doors(alert == "red" and red_auto_lock)
	alert_changed.emit(alert)
	changed.emit()
	return true

## Red alert seals the sensitive rooms; leaving red releases exactly the doors it locked.
func _auto_lock_doors(on: bool) -> void:
	if on:
		for i in doors.size():
			var a: String = doors[i].get_meta("a", "")
			var b: String = doors[i].get_meta("b", "")
			if (a in ["armory", "brig", "secoff", "core"] or b in ["armory", "brig", "secoff", "core"]) and not door_locked(i):
				set_door_locked(i, true)
				_auto_locked.append(i)
	else:
		for i in _auto_locked:
			set_door_locked(i, false)
		_auto_locked.clear()

func _process(delta: float) -> void:
	_pulse_acc += delta
	_alert_t += delta
	if _pulse_acc >= 0.05:
		_pulse_acc = 0.0
		apply_alert_lights()

## Tint / scale every light in group "ship_lights" from the alert level.  Base values are recorded lazily as metadata.
func apply_alert_lights() -> void:
	if not is_inside_tree():
		return
	var amber := Color(1.0, 0.66, 0.18)
	var red := Color(1.0, 0.1, 0.06)
	var pulse := 0.5 + 0.5 * sin(_alert_t * 4.2)
	for n in get_tree().get_nodes_in_group("ship_lights"):
		var l := n as Light3D
		if l == null:
			continue
		if not l.has_meta("e0"):
			l.set_meta("e0", l.light_energy)
			l.set_meta("c0", l.light_color)
		var e0: float = l.get_meta("e0")
		var c0: Color = l.get_meta("c0")
		match alert:
			"green":
				l.light_energy = e0
				l.light_color = c0
			"yellow":
				l.light_energy = e0 * 0.92
				l.light_color = c0.lerp(amber, 0.5)
			"red":
				l.light_energy = e0 * (0.3 + 0.9 * pulse)
				l.light_color = c0.lerp(red, 0.8)

# ------------------------------------------------------------------ doors
func door_label(i: int) -> String:
	if i < 0 or i >= doors.size():
		return "?"
	var d: Node = doors[i]
	return "%s <-> %s" % [_room_name(d.get_meta("a", "?")), _room_name(d.get_meta("b", "?"))]

func _room_name(rid: String) -> String:
	for r in ship.get("rooms", []):
		if r["id"] == rid:
			return r["name"]
	return rid

func door_locked(i: int) -> bool:
	return i >= 0 and i < doors.size() and bool(doors[i].get("locked"))

func set_door_locked(i: int, v: bool) -> bool:
	if i < 0 or i >= doors.size():
		return false
	if door_locked(i) == v:
		return true
	doors[i].call("set_locked", v)
	say("Door %s %s" % [door_label(i), "LOCKED" if v else "unlocked"], "security")
	door_lock_changed.emit(i, v)
	changed.emit()
	return true

func locked_count() -> int:
	var n := 0
	for i in doors.size():
		if door_locked(i):
			n += 1
	return n

## Door indices whose room ids/names contain the query (or index number, or "a-b" room pair).
func find_doors(q: String) -> Array:
	q = q.strip_edges().to_lower()
	var out: Array = []
	if q == "":
		return out
	if q.is_valid_int() and int(q) >= 0 and int(q) < doors.size():
		return [int(q)]
	for i in doors.size():
		var a: String = doors[i].get_meta("a", "")
		var b: String = doors[i].get_meta("b", "")
		var pair := (a + "-" + b).to_lower()
		var names := (_room_name(a) + " " + _room_name(b)).to_lower()
		if q == pair or q == (b + "-" + a).to_lower() or q == a.to_lower() or q == b.to_lower() or names.contains(q):
			out.append(i)
	return out

func lock_all(v: bool) -> void:
	for i in doors.size():
		set_door_locked(i, v)

# ------------------------------------------------------------------ hangar
var hangar_field: bool:
	get: return hangar_field_on

func set_hangar_field(on: bool, announce := true) -> void:
	hangar_field_on = on
	for h in hangar_nodes:
		if is_instance_valid(h["mesh"]):
			(h["mesh"] as Node3D).visible = on
		if is_instance_valid(h["shape"]):
			(h["shape"] as CollisionShape3D).disabled = not on
	if announce:
		say("Hangar force field %s" % ("ONLINE" if on else "OFFLINE - bay open to vacuum"), "docking")
		hangar_changed.emit(on)
		changed.emit()

# ------------------------------------------------------------------ navigation
func warp_ly_per_day() -> float:
	var info := Lore.ship_info()
	var base: float = float(info.get("ly_per_day_at_cruise", 3.0))
	var cw: float = maxf(0.1, float(info.get("cruise_warp", 6.0)))
	return base * pow(maxf(warp, 0.1) / cw, 3.0)

func set_destination(id: String) -> bool:
	if id != "" and Lore.system(id).is_empty():
		return false
	destination = id
	route = Lore.plot(current_system, id) if id != "" else []
	if id != "":
		say("Course plotted to %s: %.1f ly, ETA %s" % [Lore.system_name(id), route_ly(), eta_text()], "nav")
	else:
		say("Course cleared", "nav")
	destination_changed.emit(destination)
	changed.emit()
	return true

func route_ly() -> float:
	if destination == "":
		return 0.0
	if route.size() >= 2:
		return Lore.route_length(route)
	return Lore.distance(current_system, destination)

func eta_days() -> float:
	if destination == "":
		return 0.0
	return route_ly() / maxf(0.05, warp_ly_per_day())

func eta_text() -> String:
	if destination == "":
		return "-"
	var d := eta_days()
	return "%.1f d" % d if d >= 1.0 else "%.0f h" % (d * 24.0)

func hud_line() -> String:
	var s := "ALERT %s" % alert.to_upper()
	if in_transit:
		s += "   TRANSIT -> %s" % Lore.system_name(transit_to).to_upper()
	elif destination != "":
		s += "   DEST: %s   ETA %s" % [Lore.system_name(destination).to_upper(), eta_text()]
	else:
		s += "   AT %s" % Lore.system_name(current_system).to_upper()
	return s

func transit_progress() -> float:
	if not in_transit:
		return 0.0
	return clampf(float(Time.get_ticks_msec() - transit_start_ms) / 1000.0 / maxf(jump_seconds, 0.01), 0.0, 1.0)

## Start a jump to `id` (default: the current destination).  Completes after jump_seconds (a timer, no per-frame work).
func jump(id := "") -> bool:
	if id == "":
		id = destination
	if id == "" or id == current_system or in_transit or Lore.system(id).is_empty():
		return false
	if reactor["scram"]:
		say("Jump refused: reactor SCRAM", "warn")
		return false
	transit_from = current_system
	transit_to = id
	in_transit = true
	warp_engaged = true
	transit_start_ms = Time.get_ticks_msec()
	say("Warp %.1f engaged: %s -> %s" % [warp, Lore.system_name(current_system), Lore.system_name(id)], "nav")
	jump_started.emit(id)
	changed.emit()
	if jump_seconds <= 0.0 or not is_inside_tree():
		_finish_jump()
	else:
		get_tree().create_timer(jump_seconds).timeout.connect(_finish_jump)
	return true

func _finish_jump() -> void:
	if not in_transit:
		return
	in_transit = false
	warp_engaged = false
	var from := current_system
	current_system = transit_to
	visited[current_system] = true
	var d := Lore.pos_of(current_system) - Lore.pos_of(from)
	if d.length() > 0.01:
		heading = d.normalized()
	if destination == current_system:
		destination = ""
		route = []
		destination_changed.emit("")
	elif destination != "":
		route = Lore.plot(current_system, destination)
	say("Arrived at %s (%s)" % [Lore.system_name(current_system), Lore.system(current_system).get("summary", "")], "nav")
	jumped.emit(current_system)
	changed.emit()

# ------------------------------------------------------------------ power
func bus_load(b: Dictionary) -> float:
	return float(b["demand"]) * float(b["alloc"]) / 100.0 if b["on"] else 0.0

func total_load() -> float:
	var t := 0.0
	for b in buses:
		t += bus_load(b)
	if warp_engaged:
		t += pow(warp, 2.0) * 6.0
	return t

func supply() -> float:
	return 0.0 if reactor["scram"] else float(reactor["output"]) / 100.0 * REACTOR_MAX_MW

func brownout() -> bool:
	return total_load() > supply() + 0.5

func set_scram(on: bool) -> void:
	reactor["scram"] = on
	say("REACTOR SCRAM" if on else "Reactor restarted", "warn" if on else "info")
	if on and alert == "green":
		set_alert("yellow")
	changed.emit()

func subsystem_by_id(id: String) -> Dictionary:
	for s in subsystems:
		if s["id"] == id:
			return s
	return {}

# ------------------------------------------------------------------ cargo / dispensers
func cargo_item(id: String) -> Dictionary:
	for c in cargo:
		if c["id"] == id:
			return c
	return {}

func cargo_add(id: String, name: String, qty: int, mass: float, cat := "general") -> void:
	var c := cargo_item(id)
	if c.is_empty():
		cargo.append({"id": id, "name": name, "qty": qty, "mass": mass, "cat": cat})
	else:
		c["qty"] = int(c["qty"]) + qty
	changed.emit()

func cargo_mass() -> float:
	var t := 0.0
	for c in cargo:
		t += float(c["qty"]) * float(c["mass"])
	return t

func dispense(item_id: String, label: String, price: float) -> bool:
	if price > credits + 0.001:
		say("Insufficient credits for %s" % label, "warn")
		return false
	credits -= price
	click()
	say("Dispensed: %s%s" % [label, "" if price <= 0.0 else " (%.2f cr)" % price], "info")
	return true

# ------------------------------------------------------------------ simulation (terminal open)
func hist_push(key: String, v: float) -> void:
	var a: PackedFloat32Array = hist.get(key, PackedFloat32Array())
	a.append(v)
	if a.size() > HIST_LEN:
		a = a.slice(a.size() - HIST_LEN)
	hist[key] = a

func _approach(cur: float, target: float, rate: float, dt: float) -> float:
	return cur + (target - cur) * clampf(rate * dt, 0.0, 1.0)

func sim(dt: float) -> void:
	_sim_t += dt
	var r := reactor
	var out_pct: float = 0.0 if r["scram"] else float(r["output"])
	var target_temp := 800.0 + out_pct * 38.0 - float(r["coolant"]) * 6.0
	r["temp"] = _approach(float(r["temp"]), target_temp + sin(_sim_t * 0.7) * 25.0, 0.4, dt)
	var over := maxf(0.0, float(r["temp"]) - 4800.0)
	r["containment"] = clampf(_approach(float(r["containment"]), 99.5 - over * 0.02, 0.2, dt), 0.0, 100.0)
	r["fuel"] = maxf(0.0, float(r["fuel"]) - dt * 0.0008 * out_pct)
	if brownout() and _rng.randf() < dt * 0.15:
		say("Power bus overload - non-essential systems browning out", "warn")
	for i in coils.size():
		var base := 2000.0 + (warp * 330.0 if warp_engaged else 140.0 * warp)
		coils[i] = _approach(float(coils[i]), base + 55.0 * i + sin(_sim_t * 0.9 + i) * 30.0, 0.5, dt)
	# life support
	var l := life
	var scr: bool = l["scrubbers"]
	l["co2"] = clampf(float(l["co2"]) + dt * (-0.004 if scr else 0.01) * (float(l["fans"]) / 60.0), 0.03, 3.0)
	l["o2"] = clampf(_approach(float(l["o2"]), float(l["o2_set"]) - float(l["co2"]) * 0.5, 0.15, dt), 12.0, 30.0)
	l["temp"] = _approach(float(l["temp"]), float(l["temp_set"]) + sin(_sim_t * 0.3) * 0.25, 0.1, dt)
	l["pressure"] = _approach(float(l["pressure"]), 101.3 + (float(l["o2_set"]) - 20.9) * 1.1 + (0.0 if hangar_field_on else -18.0), 0.15, dt)
	for bed in hydro["beds"]:
		if bed["on"]:
			var rate := (float(hydro["light_h"]) / 16.0) * (float(hydro["nutrient"]) / 70.0) * minf(1.0, float(hydro["water"]) / 60.0)
			if hydro["co2_boost"]:
				rate *= 1.3
			bed["growth"] = fposmod(float(bed["growth"]) + dt * 0.35 * rate, 100.0)
	# repairs and fabrication
	for s in subsystems:
		if s["repair"]:
			s["health"] = minf(100.0, float(s["health"]) + dt * 2.5)
			if float(s["health"]) >= 100.0:
				s["repair"] = false
				say("Repairs complete: %s" % s["name"], "info")
		elif _rng.randf() < dt * 0.002 and float(s["health"]) > 60.0:
			s["health"] = float(s["health"]) - _rng.randf_range(1.0, 5.0)
	for e in experiments:
		if e["running"]:
			e["progress"] = float(e["progress"]) + dt * 100.0 / float(e["secs"]) * 6.0
			if float(e["progress"]) >= 100.0:
				e["progress"] = 100.0
				e["running"] = false
				e["result"] = "Complete: %s - %s" % [["no anomalies", "trace contaminants", "unexpected periodicity", "within tolerance"][int(_rng.randi() % 4)], Lore.system_name(current_system)]
				say("Experiment finished: %s" % e["name"], "science")
	for j in fab_queue.duplicate():
		j["progress"] = float(j["progress"]) + dt * 100.0 / float(j["secs"])
		if j["progress"] >= 100.0:
			fab_queue.erase(j)
			cargo_add("fab_" + String(j["id"]), String(j["name"]), 1, float(j.get("mass", 1.0)), "fabricated")
			say("Fabricator finished: %s" % j["name"], "info")
	_hist_acc += dt
	if _hist_acc >= 0.5:
		_hist_acc = 0.0
		hist_push("demand", total_load())
		hist_push("supply", supply())
		hist_push("o2", float(l["o2"]))
		hist_push("temp", float(r["temp"]))
		hist_push("coil", float(coils[3]))

## Plain-text status block used by the computer terminal and the tests.
func status_text() -> String:
	return "%s\nSTARDATE %.2f   SHIP TIME %s\nALERT %s   LOCKED DOORS %d/%d   HANGAR FIELD %s\nPOSITION %s   DEST %s   ETA %s\nREACTOR %.0f%%  LOAD %.0f / %.0f MW%s" % [
		Lore.ship_info().get("name", "Ship"), stardate(), ship_clock(), alert.to_upper(), locked_count(), doors.size(),
		"ON" if hangar_field_on else "OFF", Lore.system_name(current_system), Lore.system_name(destination), eta_text(),
		reactor["output"], total_load(), supply(), "  [BROWNOUT]" if brownout() else ""]
