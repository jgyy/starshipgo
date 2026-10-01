extends AppBase
## Medical: patient vitals with a live ECG trace, treatment, crew life signs, medbay beds.

var _tabs: TabContainer
var _crew_t: Tree
var _ecg: UIW.Canvas
var _vit: Label
var _name_l: Label
var _note: Label
var _treat: Button
var _admit: Button
var _signs: Tree
var _beds: Tree
var _summary: Label
var _phase := 0.0

func title_text() -> String:
	return "MEDICAL"

func build() -> void:
	_tabs = tab_container(self, ["PATIENTS", "LIFE SIGNS", "MEDBAY"])
	var row := hb(page(_tabs, 0), 10)
	_crew_t = table(row, ["Name", "Role", "Status"], [170, 140, 80])
	_crew_t.size_flags_stretch_ratio = 1.1
	_crew_t.item_selected.connect(refresh)
	var right := vb(row, 8)
	_name_l = lbl(right, "Select a patient.", 22, T.ACCENT)
	_ecg = canvas(right, 150)
	_ecg.draw_fn = _draw_ecg
	_vit = lbl(right, "", 16, T.TEXT)
	_note = wrap_lbl(right, "", 14, T.TEXT_DIM)
	var br := hb(right)
	_treat = btn(br, "TREAT / CLEAR", _do_treat)
	_admit = btn(br, "ADMIT TO MEDBAY", _do_admit)
	var sp := page(_tabs, 1)
	_summary = lbl(sp, "", 16, T.ACCENT)
	_signs = table(sp, ["Crew", "Heart rate", "Location", "Status"], [190, 90, 200, 90])
	var bp := page(_tabs, 2)
	_beds = table(bp, ["Bed", "Occupant", "Monitor"], [100, 220, 160])
	if host_tex() == "lifesigns":
		_tabs.current_tab = 1

func _sel() -> int:
	var m: Variant = table_selected(_crew_t)
	return -1 if m == null else int(m)

func _do_treat() -> void:
	var i := _sel()
	if i < 0:
		return
	var c: Dictionary = st.crew[i]
	if c["status"] != "ok":
		c["status"] = "ok"
		c["note"] = "Treated and cleared for duty."
		st.say("Treated %s: cleared for duty" % c["name"], "medical")
		st.changed.emit()

func _do_admit() -> void:
	var i := _sel()
	if i < 0:
		return
	var c: Dictionary = st.crew[i]
	c["bed"] = not c.get("bed", false)
	st.say("%s %s medbay" % [c["name"], "admitted to" if c["bed"] else "discharged from"], "medical")
	st.changed.emit()

func _vitals(i: int) -> Dictionary:
	var c: Dictionary = st.crew[i]
	var t := st.elapsed()
	var hr := float(c["hr"]) + (24.0 if c["status"] == "injured" else (10.0 if c["status"] == "sick" else 0.0)) + 3.0 * sin(t * 0.7 + i)
	return {"hr": hr, "sys": 118 + int(rnd(c["name"], 1) * 14), "dia": 76 + int(rnd(c["name"], 2) * 8), "spo2": 98.0 - (2.0 if c["status"] != "ok" else 0.0) + sin(t * 0.3 + i) * 0.4,
		"temp": 36.7 + (1.3 if c["status"] == "sick" else 0.0) + rnd(c["name"], 4) * 0.4}

func tick(dt: float) -> void:
	var i := _sel()
	var hr := 70.0 if i < 0 else float(_vitals(i)["hr"])
	_phase = fposmod(_phase + dt * hr / 60.0, 1.0)
	if _tabs.current_tab == 0:
		_ecg.queue_redraw()

func _draw_ecg(c: UIW.Canvas) -> void:
	var w := c.size.x
	var mid := c.size.y * 0.6
	var pts := PackedVector2Array()
	for x in int(w):
		var ph := fposmod(float(x) / 150.0 - _phase, 1.0)
		var y := 0.0
		if ph > 0.1 and ph < 0.2:
			y = 6.0 * sin((ph - 0.1) / 0.1 * PI)
		elif ph > 0.3 and ph < 0.33:
			y = -8.0
		elif ph >= 0.33 and ph < 0.38:
			y = 48.0 * (1.0 - absf(ph - 0.355) / 0.025)
		elif ph >= 0.38 and ph < 0.42:
			y = -12.0
		elif ph > 0.5 and ph < 0.65:
			y = 10.0 * sin((ph - 0.5) / 0.15 * PI)
		pts.append(Vector2(x, mid - y))
	c.draw_polyline(pts, Color(0.4, 1.0, 0.55), 2.0, true)
	c.draw_line(Vector2(0, mid), Vector2(w, mid), Color(0.15, 0.3, 0.3, 0.5), 1.0)

func refresh() -> void:
	var rows: Array = []
	var metas: Array = []
	var srows: Array = []
	var bad := 0
	for i in st.crew.size():
		var c: Dictionary = st.crew[i]
		var scol := T.OK if c["status"] == "ok" else (T.WARN if c["status"] == "sick" else T.BAD)
		rows.append([c["name"], c["role"], [String(c["status"]).to_upper(), scol]])
		metas.append(i)
		srows.append([c["name"], "%.0f bpm" % _vitals(i)["hr"], _room_name(c["room"]), [String(c["status"]).to_upper(), scol]])
		if c["status"] != "ok":
			bad += 1
	table_fill(_crew_t, rows, metas)
	table_fill(_signs, srows, metas)
	_summary.text = "%d crew aboard, %d in medical care" % [st.crew.size(), bad]
	var brows: Array = []
	var bi := 1
	for c2 in st.crew:
		if c2.get("bed", false):
			brows.append(["Bed %d" % bi, c2["name"], "monitoring"])
			bi += 1
	while bi <= 6:
		brows.append(["Bed %d" % bi, "(free)", "standby"])
		bi += 1
	table_fill(_beds, brows)
	var i2 := _sel()
	if i2 >= 0:
		var c3: Dictionary = st.crew[i2]
		var v := _vitals(i2)
		_name_l.text = String(c3["name"]).to_upper()
		_vit.text = "HR %.0f bpm   BP %d/%d   SpO2 %.0f%%   Temp %.1f C" % [v["hr"], v["sys"], v["dia"], v["spo2"], v["temp"]]
		_note.text = "%s - %s\n%s" % [c3["role"], "in medbay" if c3.get("bed", false) else "ambulatory", c3["note"]]
		_treat.disabled = c3["status"] == "ok"

func _room_name(rid: String) -> String:
	for r in st.ship.get("rooms", []):
		if r["id"] == rid:
			return r["name"]
	return rid

func demo() -> void:
	table_select(_crew_t, 6)
