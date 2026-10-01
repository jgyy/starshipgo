extends AppBase
## Hydroponics: six grow beds; light hours, nutrients, water and CO2 enrichment drive growth.  Harvest into cargo.

var _beds: Array = []
var _light: HSlider
var _nut: HSlider
var _water: HSlider
var _co2: CheckButton
var _info: Label

func title_text() -> String:
	return "HYDROPONICS"

func build() -> void:
	var row := hb(self, 10)
	var left := panel(row, "Grow beds")
	left.size_flags_stretch_ratio = 1.4
	for i in st.hydro["beds"].size():
		var r := hb(left)
		var on := check(r, "", st.hydro["beds"][i]["on"], _toggle_bed.bind(i))
		var m := meter(r, "", 0.0, 0.0)
		m.custom_minimum_size.y = 30
		m.caption = ""
		var hv := btn(r, "HARVEST", _harvest.bind(i))
		_beds.append({"on": on, "meter": m, "harvest": hv})
	var right := vb(row, 8)
	right.custom_minimum_size.x = 400
	right.size_flags_horizontal = Control.SIZE_FILL
	var p := panel(right, "Conditions", false)
	_light = slider(p, "Light hours / day", 6.0, 22.0, st.hydro["light_h"], _set_light, 1.0, "%.0f h")
	_nut = slider(p, "Nutrient mix", 20.0, 120.0, st.hydro["nutrient"], _set_nut, 5.0, "%.0f %%")
	_water = slider(p, "Water flow", 10.0, 120.0, st.hydro["water"], _set_water, 5.0, "%.0f %%")
	_co2 = check(p, "CO2 enrichment (+30% growth)", st.hydro["co2_boost"], _set_co2)
	var s := panel(right, "Status")
	_info = wrap_lbl(s, "", 15, T.TEXT)

func _toggle_bed(on: bool, i: int) -> void:
	st.hydro["beds"][i]["on"] = on
	st.changed.emit()

func _harvest(i: int) -> void:
	var b: Dictionary = st.hydro["beds"][i]
	if float(b["growth"]) < 90.0:
		return
	var qty := 6 + int(rnd(String(b["crop"]), 2) * 10)
	st.cargo_add("crop_" + String(b["crop"]).to_lower(), "%s (fresh)" % b["crop"], qty, 0.4, "food")
	st.say("Harvested %d kg of %s" % [qty, b["crop"]], "life")
	b["growth"] = 5.0
	st.changed.emit()

func _set_light(v: float) -> void:
	st.hydro["light_h"] = v
	st.changed.emit()

func _set_nut(v: float) -> void:
	st.hydro["nutrient"] = v
	st.changed.emit()

func _set_water(v: float) -> void:
	st.hydro["water"] = v
	st.changed.emit()

func _set_co2(on: bool) -> void:
	st.hydro["co2_boost"] = on
	st.changed.emit()

func refresh() -> void:
	var ready := 0
	for i in _beds.size():
		var b: Dictionary = st.hydro["beds"][i]
		var g := float(b["growth"])
		var m: UIW.Meter = _beds[i]["meter"]
		m.set_value(g / 100.0, "%s - %.0f%%%s" % [b["crop"], g, "  READY" if g >= 90.0 else ""])
		m.tint = T.OK if g >= 90.0 else T.ACCENT
		(_beds[i]["harvest"] as Button).disabled = g < 90.0
		if g >= 90.0:
			ready += 1
	var rate := (float(st.hydro["light_h"]) / 16.0) * (float(st.hydro["nutrient"]) / 70.0) * minf(1.0, float(st.hydro["water"]) / 60.0) * (1.3 if st.hydro["co2_boost"] else 1.0)
	_info.text = "Growth rate: %.0f%% of nominal\nBeds ready to harvest: %d\nWater use: %.0f L/day\nPower: %.0f MW" % [rate * 100.0, ready, float(st.hydro["water"]) * 1.4, 110.0 * float(st.hydro["light_h"]) / 16.0]
