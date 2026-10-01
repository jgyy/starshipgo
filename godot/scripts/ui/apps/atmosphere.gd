extends AppBase
## Atmosphere monitor: every room's O2, temperature and pressure; seal a room or vent it.  The hangar follows the
## hangar force field (field off = vacuum).

var _tree: Tree
var _filter: LineEdit
var _detail: Label
var _seal: Button
var _graph: UIW.Graph
var _hist: PackedFloat32Array = PackedFloat32Array()
var _acc := 0.0

func title_text() -> String:
	return "ATMOSPHERE"

func build() -> void:
	var row := hb(self, 10)
	var left := vb(row, 6)
	left.size_flags_stretch_ratio = 1.6
	_filter = line_edit(left, "filter rooms...", func(_t: String) -> void: refresh())
	_filter.text_changed.connect(func(_t: String) -> void: refresh())
	_tree = table(left, ["Room", "Deck", "O2", "Temp", "kPa", "State"], [190, 40, 60, 60, 60, 80])
	_tree.item_selected.connect(refresh)
	var right := panel(row, "Selected room")
	right.custom_minimum_size.x = 340
	_detail = wrap_lbl(right, "Select a room.", 15, T.TEXT)
	_seal = btn(right, "SEAL / UNSEAL ROOM", _toggle_seal)
	_graph = graph(right, "O2 HISTORY", "%", 140)

func _room_vals(r: Dictionary) -> Array:
	var rid: String = r["id"]
	var vac: bool = rid == "hangar" and not st.hangar_field_on
	var o2: float = float(st.life["o2"]) + (rnd(rid, 1) - 0.5) * 0.4
	var temp: float = float(st.life["temp"]) + (rnd(rid, 2) - 0.5) * 2.0 + (4.0 if r.get("dept", "") == "engineering" else 0.0)
	var pr: float = float(st.life["pressure"]) + (rnd(rid, 3) - 0.5)
	if vac:
		o2 = 0.0
		pr = 0.0
		temp = 3.0
	return [o2, temp, pr, vac]

func _toggle_seal() -> void:
	var m: Variant = table_selected(_tree)
	if m == null:
		return
	var rid := String(m)
	st.sealed[rid] = not st.sealed.get(rid, false)
	st.say("Room %s %s" % [rid, "SEALED" if st.sealed[rid] else "unsealed"], "life")
	st.changed.emit()

func tick(dt: float) -> void:
	_acc += dt
	if _acc >= 0.5:
		_acc = 0.0
		var m: Variant = table_selected(_tree)
		if m != null:
			for r in st.ship.get("rooms", []):
				if r["id"] == m:
					_hist.append(_room_vals(r)[0])
					if _hist.size() > 80:
						_hist = _hist.slice(1)

func refresh() -> void:
	var rows: Array = []
	var metas: Array = []
	var q := _filter.text.to_lower()
	for r in st.ship.get("rooms", []):
		if q != "" and not String(r["name"]).to_lower().contains(q):
			continue
		var v := _room_vals(r)
		var state: Array = ["VACUUM", T.BAD] if v[3] else (["SEALED", T.WARN] if st.sealed.get(r["id"], false) else ["OK", T.OK])
		rows.append(["%s" % r["name"], str(int(r["deck"])), "%.1f%%" % v[0], "%.1f C" % v[1], "%.0f" % v[2], state])
		metas.append(r["id"])
	table_fill(_tree, rows, metas)
	var m: Variant = table_selected(_tree)
	if m != null:
		for r in st.ship.get("rooms", []):
			if r["id"] == m:
				var v2 := _room_vals(r)
				_detail.text = "%s\nDeck %d, %.0f m2 (%s)\nO2 %.1f %%   Temp %.1f C   Pressure %.1f kPa\n%s" % [r["name"], int(r["deck"]), r.get("area", 0.0), r.get("dept", ""), v2[0], v2[1], v2[2], "Bay is open to space - switch the hangar force field on." if v2[3] else ("Room is sealed from the ventilation loop." if st.sealed.get(m, false) else "Ventilation normal.")]
		_graph.set_series([{"data": _hist, "color": T.OK}])
