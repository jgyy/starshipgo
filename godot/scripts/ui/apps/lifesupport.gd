extends AppBase
## Life support: oxygen, CO2, temperature and pressure setpoints with a slow simulation; scrubbers and fans.

var _dials: Dictionary = {}
var _o2: HSlider
var _temp: HSlider
var _fans: HSlider
var _scr: CheckButton
var _graph: UIW.Graph
var _tree: Tree
var _warn: Label

func title_text() -> String:
	return "LIFE SUPPORT"

func build() -> void:
	var row := hb(self, 10)
	var left := vb(row, 8)
	var dr := hb(left)
	for d in [["o2", "O2 %", 10.0, 30.0, NAN, NAN], ["co2", "CO2 %", 0.0, 3.0, 0.5, 1.5], ["temp", "TEMP C", 5.0, 40.0, 26.0, 32.0], ["pres", "PRESSURE kPa", 60.0, 130.0, NAN, NAN]]:
		var dial := UIW.Dial.new()
		dial.caption = d[1]
		dial.vmin = d[2]
		dial.vmax = d[3]
		dial.warn_above = d[4]
		dial.crit_above = d[5]
		dial.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		dr.add_child(dial)
		_dials[d[0]] = dial
	var p := panel(left, "Setpoints", false)
	_o2 = slider(p, "Oxygen target", 18.0, 24.0, st.life["o2_set"], _set_o2, 0.1, "%.1f %%")
	_temp = slider(p, "Temperature target", 16.0, 28.0, st.life["temp_set"], _set_temp, 0.5, "%.1f C")
	_fans = slider(p, "Circulation fans", 10.0, 100.0, st.life["fans"], _set_fans, 5.0, "%.0f %%")
	_scr = check(p, "CO2 scrubbers", st.life["scrubbers"], _set_scr)
	_warn = wrap_lbl(p, "", 14, T.TEXT_DIM)
	var right := vb(row, 8)
	right.custom_minimum_size.x = 400
	right.size_flags_horizontal = Control.SIZE_FILL
	var g := panel(right, "Oxygen history")
	_graph = graph(g, "O2", "%", 140)
	var t := panel(right, "Decks")
	_tree = table(t, ["Deck", "O2", "Temp", "Pressure"], [150, 70, 70, 90])

func _set_o2(v: float) -> void:
	st.life["o2_set"] = v
	st.changed.emit()

func _set_temp(v: float) -> void:
	st.life["temp_set"] = v
	st.changed.emit()

func _set_fans(v: float) -> void:
	st.life["fans"] = v
	st.changed.emit()

func _set_scr(on: bool) -> void:
	st.life["scrubbers"] = on
	st.say("CO2 scrubbers %s" % ("ONLINE" if on else "OFFLINE"), "life")
	st.changed.emit()

func refresh() -> void:
	var l := st.life
	(_dials["o2"] as UIW.Dial).set_value(l["o2"])
	(_dials["co2"] as UIW.Dial).set_value(l["co2"])
	(_dials["temp"] as UIW.Dial).set_value(l["temp"])
	(_dials["pres"] as UIW.Dial).set_value(l["pressure"])
	var msg := "Atmosphere nominal."
	if float(l["co2"]) > 0.5:
		msg = "CO2 rising - enable the scrubbers."
	elif float(l["o2"]) < 19.0:
		msg = "Oxygen low - raise the target."
	elif brownout_note():
		msg = "Power brownout: life support running at reduced capacity."
	_warn.text = msg
	_graph.set_series([{"data": st.hist.get("o2", PackedFloat32Array()), "color": T.OK}])
	var rows: Array = []
	var i := 0
	for d in st.ship.get("decks", []):
		rows.append([d["name"], "%.1f%%" % (float(l["o2"]) + 0.15 * sin(i + st.elapsed() * 0.1)), "%.1f C" % (float(l["temp"]) + 0.4 * i), "%.1f kPa" % (float(l["pressure"]) - 0.2 * i)])
		i += 1
	table_fill(_tree, rows)

func brownout_note() -> bool:
	return st.brownout()
