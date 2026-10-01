extends AppBase
## Tactical: four shield quadrants, weapons arming, target selection.  Arming weapons raises the alert to yellow.

var _ship: UIW.Canvas
var _q: Dictionary = {}
var _ph: Button
var _tp: Button
var _fire: Button
var _strength: UIW.Meter
var _target_t: Tree
var _status: Label
var _flash := 0.0
var _targets := [["Gate Ring debris", 41.0], ["Unknown carrier 14.2 GHz", 88.0], ["Vael patrol picket", 62.0], ["Training drone", 12.0]]

func title_text() -> String:
	return "TACTICAL"

func build() -> void:
	var row := hb(self, 10)
	var left := panel(row, "Shield grid")
	left.size_flags_stretch_ratio = 1.4
	_ship = canvas(left, 260)
	_ship.draw_fn = _draw_ship
	_strength = meter(left, "SHIELD STRENGTH", 0.0, 0.0)
	_strength.invert = true
	_strength.warn = 0.5
	_strength.crit = 0.25
	var g := grid(left, 4)
	for k in ["fore", "aft", "port", "starboard"]:
		var b := btn(g, k.to_upper(), _set_shield.bind(k), true)
		b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		_q[k] = b
	var right := vb(row, 8)
	right.custom_minimum_size.x = 400
	right.size_flags_horizontal = Control.SIZE_FILL
	var w := panel(right, "Weapons", false)
	_ph = btn(w, "ARM PHASER BANKS", _arm_ph, true)
	_tp = btn(w, "ARM TORPEDO TUBES", _arm_tp, true)
	var tg := panel(right, "Targets")
	_target_t = table(tg, ["Contact", "Range"], [220, 80])
	var rows: Array = []
	for t in _targets:
		rows.append([t[0], "%.0f kkm" % t[1]])
	table_fill(_target_t, rows)
	_target_t.item_selected.connect(func() -> void:
		var m: Variant = table_selected(_target_t)
		if m != null:
			st.weapons["target"] = _targets[int(m)][0]
			st.changed.emit())
	_fire = btn(tg, "FIRE", _do_fire)
	_status = wrap_lbl(tg, "", 14, T.TEXT_DIM)

func _set_shield(on: bool, k: String) -> void:
	st.shields[k] = on
	st.say("Shields %s %s" % [k, "up" if on else "down"], "tactical")
	st.changed.emit()

func _arm_ph(on: bool) -> void:
	st.weapons["phasers"] = on
	_raise()
	st.say("Phaser banks %s" % ("ARMED" if on else "safe"), "tactical")
	st.changed.emit()

func _arm_tp(on: bool) -> void:
	st.weapons["torpedoes"] = on
	_raise()
	st.say("Torpedo tubes %s" % ("ARMED" if on else "safe"), "tactical")
	st.changed.emit()

func _raise() -> void:
	if (st.weapons["phasers"] or st.weapons["torpedoes"]) and st.alert == "green":
		st.set_alert("yellow")

func _do_fire() -> void:
	var tgt: String = st.weapons["target"]
	if tgt == "" or not (st.weapons["phasers"] or st.weapons["torpedoes"]):
		_status.text = "Weapons safe or no target selected."
		return
	_flash = 0.4
	st.shields["strength"] = maxf(0.0, float(st.shields["strength"]) - 3.0)
	_status.text = "Fired at %s." % tgt
	st.say("Weapons fired at %s" % tgt, "tactical")

func tick(dt: float) -> void:
	_flash = maxf(0.0, _flash - dt)
	_ship.queue_redraw()

func refresh() -> void:
	for k in _q.keys():
		(_q[k] as Button).set_pressed_no_signal(st.shields[k])
	_ph.set_pressed_no_signal(st.weapons["phasers"])
	_tp.set_pressed_no_signal(st.weapons["torpedoes"])
	_strength.set_value(float(st.shields["strength"]) / 100.0, "%.0f%%" % st.shields["strength"])
	_fire.disabled = not (st.weapons["phasers"] or st.weapons["torpedoes"]) or st.weapons["target"] == ""

func _draw_ship(c: UIW.Canvas) -> void:
	var ctr := c.size * 0.5
	var s := minf(c.size.x, c.size.y) * 0.3
	var hull := PackedVector2Array([ctr + Vector2(0, -s), ctr + Vector2(s * 0.45, -s * 0.2), ctr + Vector2(s * 0.5, s * 0.8), ctr + Vector2(-s * 0.5, s * 0.8), ctr + Vector2(-s * 0.45, -s * 0.2)])
	c.draw_colored_polygon(hull, Color(0.1, 0.25, 0.3))
	c.draw_polyline(hull + PackedVector2Array([hull[0]]), T.ACCENT, 2.0, true)
	var arcs := {"fore": -PI * 0.5, "starboard": 0.0, "aft": PI * 0.5, "port": PI}
	for k in arcs.keys():
		var a: float = arcs[k]
		var on: bool = st.shields[k]
		var col := Color(0.3, 0.8, 1.0, 0.85) if on else Color(0.5, 0.2, 0.2, 0.5)
		if on and _flash > 0.0:
			col = Color(1, 1, 1, 0.9)
		c.draw_arc(ctr, s * 1.35, a - 0.7, a + 0.7, 20, col, 6.0 if on else 2.0, true)
	if st.weapons["target"] != "":
		c.draw_string(c.get_theme_default_font(), Vector2(10, 20), "TARGET: " + String(st.weapons["target"]), HORIZONTAL_ALIGNMENT_LEFT, -1, 13, T.WARN)
