extends AppBase
## Reactor monitor: output and coolant sliders, temperature / containment dials, supply-vs-load graph, SCRAM.

var _out: HSlider
var _cool: HSlider
var _dials: Dictionary = {}
var _graph: UIW.Graph
var _fuel: UIW.Meter
var _scram: Button
var _state: Label

func title_text() -> String:
	return "REACTOR MONITOR"

func build() -> void:
	var row := hb(self, 10)
	var left := vb(row, 8)
	var dr := hb(left)
	for d in [["temp", "CORE TEMP K", 0.0, 7000.0, 4800.0, 5600.0], ["cont", "CONTAINMENT %", 0.0, 100.0, NAN, NAN], ["out", "OUTPUT %", 0.0, 120.0, 100.0, 110.0], ["cool", "COOLANT %", 0.0, 100.0, NAN, NAN]]:
		var dial := UIW.Dial.new()
		dial.caption = d[1]
		dial.vmin = d[2]
		dial.vmax = d[3]
		dial.warn_above = d[4]
		dial.crit_above = d[5]
		dial.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		dr.add_child(dial)
		_dials[d[0]] = dial
	var p := panel(left, "Controls", false)
	_out = slider(p, "Reactor output", 0, 120, st.reactor["output"], _set_out, 1.0, "%.0f %%")
	_cool = slider(p, "Coolant flow", 0, 100, st.reactor["coolant"], _set_cool, 1.0, "%.0f %%")
	_fuel = meter(p, "FUEL", 0.25, 0.1)
	_fuel.invert = true
	var br := hb(p)
	_scram = btn(br, "SCRAM", func() -> void: st.set_scram(not st.reactor["scram"]))
	_state = lbl(br, "", 16, T.OK)
	var g := panel(row, "Supply and demand")
	g.custom_minimum_size.x = 420
	_graph = graph(g, "LOAD (cyan) vs SUPPLY (amber)", "MW", 200)

func _set_out(v: float) -> void:
	st.reactor["output"] = v
	st.changed.emit()

func _set_cool(v: float) -> void:
	st.reactor["coolant"] = v
	st.changed.emit()

func refresh() -> void:
	var r := st.reactor
	(_dials["temp"] as UIW.Dial).set_value(r["temp"])
	(_dials["cont"] as UIW.Dial).set_value(r["containment"])
	(_dials["out"] as UIW.Dial).set_value(0.0 if r["scram"] else r["output"])
	(_dials["cool"] as UIW.Dial).set_value(r["coolant"])
	if absf(_out.value - float(r["output"])) > 0.5:
		set_slider(_out, r["output"])
	if absf(_cool.value - float(r["coolant"])) > 0.5:
		set_slider(_cool, r["coolant"])
	_fuel.set_value(float(r["fuel"]) / 100.0, "%.1f %%" % r["fuel"])
	_scram.text = "RESTART REACTOR" if r["scram"] else "SCRAM"
	var txt := "SCRAMMED" if r["scram"] else ("OVERLOAD" if st.brownout() else ("HOT" if float(r["temp"]) > 4800.0 else "STABLE"))
	_state.text = txt
	_state.add_theme_color_override("font_color", T.OK if txt == "STABLE" else (T.WARN if txt == "HOT" else T.BAD))
	_graph.set_series([{"data": st.hist.get("demand", PackedFloat32Array()), "color": T.ACCENT}, {"data": st.hist.get("supply", PackedFloat32Array()), "color": T.WARN}])
