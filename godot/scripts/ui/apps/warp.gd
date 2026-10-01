extends AppBase
## Warp core control: warp factor, eight lattice coils (temperature limit 4800 K), engage and plasma dump.

var _warp: HSlider
var _speed: Label
var _limit: Label
var _coils: Array = []
var _graph: UIW.Graph
var _engage: Button
var _dump: Button
var _status: Label

const COIL_LIMIT := 4800.0

func title_text() -> String:
	return "WARP CORE CONTROL"

func build() -> void:
	var row := hb(self, 10)
	var left := vb(row, 8)
	var p := panel(left, "Warp factor", false)
	_warp = slider(p, "Warp factor", 0.0, float(Lore.ship_info().get("top_warp", 9.2)), st.warp, _on_warp, 0.1, "%.1f")
	_speed = lbl(p, "", 22, T.ACCENT)
	_limit = wrap_lbl(p, "", 14, T.TEXT_DIM)
	var br := hb(p)
	_engage = btn(br, "ENGAGE", func() -> void:
		if st.destination == "":
			_status.text = "No course set - use navigation or the star map."
		elif not st.jump():
			_status.text = "Cannot engage: already there, in transit or reactor offline."
		else:
			_status.text = "Warp engaged.")
	_dump = btn(br, "VENT COIL PLASMA", func() -> void:
		for i in st.coils.size():
			st.coils[i] = float(st.coils[i]) * 0.85
		st.say("Plasma vented from the lattice coils", "warn"))
	_status = wrap_lbl(p, "", 14, T.WARN)
	var g := panel(left, "Coil 4 temperature")
	_graph = graph(g, "COIL 4", "K", 120)
	_graph.guide = COIL_LIMIT
	var cp := panel(row, "Lattice coils")
	cp.custom_minimum_size.x = 380
	for i in 8:
		var m := meter(cp, "COIL %d" % (i + 1), 0.7, 0.85)
		_coils.append(m)

func _on_warp(v: float) -> void:
	st.warp = v
	st.changed.emit()

func refresh() -> void:
	if absf(_warp.value - st.warp) > 0.01:
		set_slider(_warp, st.warp)
	_speed.text = "%.2f ly/day%s" % [st.warp_ly_per_day(), "   [ENGAGED]" if st.warp_engaged else ""]
	var hot := 0.0
	for i in 8:
		var t: float = st.coils[i]
		hot = maxf(hot, t)
		(_coils[i] as UIW.Meter).set_value(t / 6000.0, "%.0f K" % t)
	_limit.text = "Power draw %.0f MW of %.0f MW. %s" % [st.total_load(), st.supply(), "Coils at the limit: reduce warp." if hot > COIL_LIMIT else "Coils within limits."]
	_limit.add_theme_color_override("font_color", T.BAD if hot > COIL_LIMIT else T.TEXT_DIM)
	_engage.disabled = st.in_transit
	_graph.set_series([{"data": st.hist.get("coil", PackedFloat32Array()), "color": T.ACCENT}])
