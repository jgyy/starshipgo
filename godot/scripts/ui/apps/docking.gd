extends AppBase
## Docking and hangar: the hangar force field plane (visible + collidable in the world), bay doors, clamps, shuttles.

var _field: Button
var _doors: Button
var _state: Label
var _tree: Tree
var _clamps: Array = []
var _bay: UIW.Canvas

func title_text() -> String:
	return "DOCKING & HANGAR"

func build() -> void:
	var row := hb(self, 10)
	var left := vb(row, 8)
	var p := panel(left, "Hangar bay", false)
	_state = wrap_lbl(p, "", 18, T.ACCENT)
	_field = btn(p, "FORCE FIELD", func(on: bool) -> void: st.set_hangar_field(on), true)
	_field.custom_minimum_size.y = 56
	_doors = btn(p, "BAY DOORS", _set_doors, true)
	_doors.custom_minimum_size.y = 40
	var cp := panel(left, "Docking clamps", false)
	for i in 4:
		var c := check(cp, "Clamp %d engaged" % (i + 1), true, _clamp.bind(i))
		_clamps.append(c)
	var right := vb(row, 8)
	right.custom_minimum_size.x = 420
	right.size_flags_horizontal = Control.SIZE_FILL
	var sp := panel(right, "Shuttles")
	_tree = table(sp, ["Craft", "State"], [220, 120])
	var br := hb(sp)
	btn(br, "LAUNCH", func() -> void: _launch(true))
	btn(br, "RECALL", func() -> void: _launch(false))
	_bay = canvas(right, 120)
	_bay.draw_fn = _draw_bay

func _set_doors(on: bool) -> void:
	st.bay_doors_open = on
	st.say("Hangar bay doors %s" % ("OPEN" if on else "closed"), "docking")
	st.changed.emit()

func _clamp(on: bool, i: int) -> void:
	st.say("Docking clamp %d %s" % [i + 1, "engaged" if on else "RELEASED"], "docking")

func _launch(out: bool) -> void:
	var m: Variant = table_selected(_tree)
	if m == null:
		return
	var s: Dictionary = st.shuttles[int(m)]
	if out:
		if not st.bay_doors_open:
			st.say("Launch refused: bay doors closed", "warn")
			return
		if s["state"] != "docked":
			return
		s["state"] = "launched"
	else:
		if s["state"] != "launched":
			return
		s["state"] = "docked"
	st.say("%s %s" % [s["name"], s["state"]], "docking")
	st.changed.emit()

func tick(_dt: float) -> void:
	_bay.queue_redraw()

func refresh() -> void:
	_field.set_pressed_no_signal(st.hangar_field_on)
	_field.text = "FORCE FIELD: %s" % ("ONLINE" if st.hangar_field_on else "OFFLINE")
	_doors.set_pressed_no_signal(st.bay_doors_open)
	_doors.text = "BAY DOORS: %s" % ("OPEN" if st.bay_doors_open else "CLOSED")
	var vac := st.bay_doors_open and not st.hangar_field_on
	_state.text = "VACUUM IN BAY - DO NOT ENTER" if vac else ("Atmosphere contained by the force field." if st.bay_doors_open else "Bay sealed.")
	_state.add_theme_color_override("font_color", T.BAD if vac else T.ACCENT)
	var rows: Array = []
	for i in st.shuttles.size():
		var s: Dictionary = st.shuttles[i]
		rows.append([s["name"], ["DOCKED", T.OK] if s["state"] == "docked" else ["LAUNCHED", T.WARN]])
	table_fill(_tree, rows)

func _draw_bay(c: UIW.Canvas) -> void:
	var w := c.size.x
	var h := c.size.y
	c.draw_rect(Rect2(10, 20, w - 20, h - 40), Color(0.05, 0.1, 0.13), true)
	c.draw_rect(Rect2(10, 20, w - 20, h - 40), T.ACCENT_DIM, false, 2.0)
	var fcol := Color(0.3, 0.8, 1.0, 0.45 + 0.15 * sin(Time.get_ticks_msec() / 250.0)) if st.hangar_field_on else Color(1, 0.3, 0.3, 0.2)
	c.draw_line(Vector2(w - 12, 22), Vector2(w - 12, h - 22), fcol, 5.0)
	for i in st.shuttles.size():
		if st.shuttles[i]["state"] == "docked":
			c.draw_rect(Rect2(30 + i * 70, h * 0.45, 50, 26), T.ACCENT_DIM, true)
	c.draw_string(c.get_theme_default_font(), Vector2(12, 15), "BAY (PLAN)", HORIZONTAL_ALIGNMENT_LEFT, -1, 11, T.TEXT_DIM)
