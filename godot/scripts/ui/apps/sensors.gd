extends AppBase
## Long-range sensors: a rotating radar sweep, a contact table generated from the current system, scan/identify.

var _radar: UIW.Canvas
var _tree: Tree
var _range_s: HSlider
var _detail: Label
var _contacts: Array = []
var _sys_seen := ""
var _sweep := 0.0
var _passive := false
var _range_km := 50.0
var _scanned: Dictionary = {}
var _tabs: TabContainer
var _spec: UIW.Canvas

const KINDS := [["Asteroid", 0.5], ["Vessel", 0.2], ["Debris", 0.4], ["Comet", 0.15], ["Beacon", 0.1], ["Anomaly", 0.05]]

func title_text() -> String:
	return "SENSOR ARRAY"

func build() -> void:
	var row := hb(self, 10)
	var left := vb(row, 6)
	left.size_flags_stretch_ratio = 1.5
	_radar = canvas(left, 300)
	_radar.draw_fn = _draw_radar
	_radar.click_fn = func(e: InputEventMouseButton, p: Vector2) -> void:
		if e.button_index != MOUSE_BUTTON_LEFT:
			return
		var best := -1
		var bd := 18.0
		for i in _contacts.size():
			var d := (_blip(_radar, _contacts[i]) - p).length()
			if d < bd:
				bd = d
				best = i
		if best >= 0:
			table_select(_tree, best)
	_range_s = slider(left, "Range (thousand km)", 10, 100, _range_km, func(v: float) -> void: _range_km = v, 10.0)
	var tg := hb(left)
	check(tg, "Passive mode", false, func(on: bool) -> void: _passive = on)
	btn(tg, "FULL SCAN", _full_scan)
	var right := vb(row, 6)
	right.custom_minimum_size.x = 380
	right.size_flags_horizontal = Control.SIZE_FILL
	_tabs = tab_container(right, ["CONTACTS", "SPECTRUM"])
	var cp := page(_tabs, 0)
	_tree = table(cp, ["#", "Type", "Brg", "Range", "ID"], [30, 90, 50, 70, 70])
	_tree.item_selected.connect(refresh)
	_detail = wrap_lbl(cp, "Select a contact.", 14, T.TEXT_DIM)
	var row2 := hb(cp)
	btn(row2, "SCAN CONTACT", _scan_selected)
	var sp := page(_tabs, 1)
	_spec = canvas(sp, 200)
	_spec.draw_fn = _draw_spectrum
	wrap_lbl(sp, "Stellar spectrum of %s. Absorption lines mark hydrogen, helium and metals." % Lore.system_name(st.current_system), 13, T.TEXT_DIM)
	_gen()

func _gen() -> void:
	_sys_seen = st.current_system
	_contacts.clear()
	var sys := Lore.system(st.current_system)
	var n := 7
	for i in n:
		var k := rnd(_sys_seen, i * 3)
		var kind := "Asteroid"
		var acc := 0.0
		for kk in KINDS:
			acc += kk[1]
			if k * 1.4 < acc:
				kind = kk[0]
				break
		_contacts.append({"i": i + 1, "type": kind, "brg": rnd(_sys_seen, i * 3 + 1) * 360.0, "range": 8.0 + rnd(_sys_seen, i * 3 + 2) * 90.0,
			"id": "%s-%03d" % [kind.substr(0, 2).to_upper(), int(rnd(_sys_seen, i + 40) * 900)], "mass": int(rnd(_sys_seen, i + 9) * 9000) + 100})
	if sys.get("kind", "") == "anomaly":
		_contacts.append({"i": n + 1, "type": "Anomaly", "brg": 40.0, "range": 31.0, "id": "RING-001", "mass": 9000000})
	if sys.get("kind", "") in ["colony", "outpost", "home", "border"]:
		_contacts.append({"i": n + 1, "type": "Station", "brg": 300.0, "range": 12.0, "id": "RELAY-%s" % _sys_seen.substr(0, 3).to_upper(), "mass": 400000})

func refresh() -> void:
	if _sys_seen != st.current_system:
		_gen()
	var rows: Array = []
	var metas: Array = []
	for i in _contacts.size():
		var c: Dictionary = _contacts[i]
		var in_range: bool = float(c["range"]) <= _range_km
		rows.append([str(c["i"]), [c["type"], T.TEXT if in_range else T.TEXT_DIM], "%03.0f" % c["brg"], "%.0f kkm" % c["range"], c["id"] if _scanned.has(c["id"]) else "unknown"])
		metas.append(i)
	table_fill(_tree, rows, metas)
	var sel: Variant = table_selected(_tree)
	if sel != null:
		var c2: Dictionary = _contacts[int(sel)]
		if _scanned.has(c2["id"]):
			_detail.text = "%s %s\nBearing %03.0f  Range %.0f thousand km\nMass %s t.  %s" % [c2["type"], c2["id"], c2["brg"], c2["range"], str(c2["mass"]), _note(c2)]
		else:
			_detail.text = "%s (unscanned)\nBearing %03.0f  Range %.0f thousand km\nPress SCAN CONTACT to identify." % [c2["type"], c2["brg"], c2["range"]]

func _note(c: Dictionary) -> String:
	match c["type"]:
		"Vessel": return "Transponder silent. Hull signature civilian."
		"Station": return "Friendly relay. Hailing frequency open."
		"Anomaly": return "Manufactured structure, non-natural. Shields advised."
		"Beacon": return "Automated survey buoy."
		"Comet": return "Water ice and CO2 ice."
	return "Natural body, no hazard."

func _scan_selected() -> void:
	var sel: Variant = table_selected(_tree)
	if sel == null:
		return
	var c: Dictionary = _contacts[int(sel)]
	_scanned[c["id"]] = true
	st.say("Sensors: scanned %s %s at %.0f kkm" % [c["type"], c["id"], c["range"]], "science")
	refresh()

func _full_scan() -> void:
	for c in _contacts:
		if float(c["range"]) <= _range_km:
			_scanned[c["id"]] = true
	st.say("Sensors: full scan, %d contacts identified" % _scanned.size(), "science")
	refresh()

func tick(dt: float) -> void:
	_sweep = fposmod(_sweep + dt * (0.6 if _passive else 1.7), TAU)
	_radar.queue_redraw()
	if _tabs.current_tab == 1:
		_spec.queue_redraw()

func _blip(c: Control, k: Dictionary) -> Vector2:
	var r := minf(c.size.x, c.size.y) * 0.46
	var a := deg_to_rad(float(k["brg"]))
	var d := minf(float(k["range"]) / _range_km, 1.2) * r
	return c.size * 0.5 + Vector2(sin(a), -cos(a)) * d

func _draw_radar(c: UIW.Canvas) -> void:
	var ctr := c.size * 0.5
	var r := minf(c.size.x, c.size.y) * 0.46
	for i in range(1, 5):
		c.draw_arc(ctr, r * i / 4.0, 0, TAU, 48, Color(0.15, 0.4, 0.3, 0.7), 1.0, true)
	for i in 8:
		var a := TAU * i / 8.0
		c.draw_line(ctr, ctr + Vector2(sin(a), -cos(a)) * r, Color(0.15, 0.4, 0.3, 0.5), 1.0)
	for k in 28:
		var a2 := _sweep - k * 0.03
		c.draw_line(ctr, ctr + Vector2(sin(a2), -cos(a2)) * r, Color(0.2, 1.0, 0.5, 0.35 * (1.0 - k / 28.0)), 2.0)
	var sel: Variant = table_selected(_tree)
	for i in _contacts.size():
		var k2: Dictionary = _contacts[i]
		if float(k2["range"]) > _range_km:
			continue
		var a3 := fposmod(deg_to_rad(float(k2["brg"])), TAU)
		var age := fposmod(_sweep - a3, TAU)
		var br := clampf(1.0 - age / (TAU * 0.9), 0.25, 1.0)
		var p := _blip(c, k2)
		var col := Color(0.4, 1.0, 0.6, br)
		if k2["type"] in ["Vessel", "Anomaly"]:
			col = Color(1.0, 0.7, 0.3, br)
		c.draw_circle(p, 4.0, col)
		if sel != null and int(sel) == i:
			c.draw_arc(p, 10.0, 0, TAU, 20, T.ACCENT, 2.0, true)
	c.draw_circle(ctr, 4.0, Color.WHITE)
	c.draw_string(c.get_theme_default_font(), Vector2(8, 16), "RANGE %.0f kkm   %s" % [_range_km, "PASSIVE" if _passive else "ACTIVE"], HORIZONTAL_ALIGNMENT_LEFT, -1, 12, T.ACCENT)

func _draw_spectrum(c: UIW.Canvas) -> void:
	var s := Lore.system(st.current_system)
	var temp := float(s.get("star", {}).get("temp_k", 5800.0))
	var pts := PackedVector2Array()
	var w := c.size.x - 20.0
	var h := c.size.y - 30.0
	var lines: Array = []
	for i in 7:
		lines.append(rnd(st.current_system, 100 + i))
	for i in 120:
		var x := float(i) / 119.0
		var lam := 0.3 + x * 0.6
		var planck := 1.0 / (pow(lam, 5.0) * (exp(1.44 / (lam * temp / 1000.0 * 0.1 + 0.001)) - 1.0) + 0.001)
		var y := clampf(0.2 + 0.7 * sin(PI * clampf((x * 1.0 - (6500.0 - temp) / 40000.0), 0.0, 1.0)), 0.1, 0.95)
		for l in lines:
			y -= 0.35 * exp(-pow((x - l) * 60.0, 2.0))
		pts.append(Vector2(10.0 + x * w, 10.0 + h * (1.0 - clampf(y, 0.02, 1.0))))
		if i % 6 == 0:
			c.draw_line(Vector2(10.0 + x * w, c.size.y - 20), Vector2(10.0 + x * w, c.size.y - 14), T.TEXT_DIM, 1.0)
	c.draw_polyline(pts, T.ACCENT, 2.0, true)
	c.draw_string(c.get_theme_default_font(), Vector2(10, c.size.y - 4), "%s  %d K" % [Lore.system_name(st.current_system), int(temp)], HORIZONTAL_ALIGNMENT_LEFT, -1, 12, T.TEXT_DIM)
