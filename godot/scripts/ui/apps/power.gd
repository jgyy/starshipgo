extends AppBase
## Power grid: 15 consumers on three buses.  Per-consumer breaker and allocation; overload browns the ship out.

var _tree: Tree
var _alloc: HSlider
var _breaker: CheckButton
var _sel_l: Label
var _graph: UIW.Graph
var _groups: Dictionary = {}
var _total: UIW.Meter
var _syncing := false

func title_text() -> String:
	return "POWER GRID"

func build() -> void:
	var row := hb(self, 10)
	var left := vb(row, 8)
	left.size_flags_stretch_ratio = 1.5
	var p := panel(left, "Consumers")
	_tree = table(p, ["Consumer", "Bus", "Demand", "Alloc", "Load", "State"], [170, 40, 70, 60, 70, 70])
	_tree.item_selected.connect(_on_select)
	var c := panel(left, "Selected consumer", false)
	_sel_l = lbl(c, "Select a consumer in the table.", 15, T.ACCENT)
	_alloc = slider(c, "Allocation", 10, 100, 100, _on_alloc, 5.0, "%.0f %%")
	_breaker = check(c, "Breaker closed", true, _on_breaker)
	var sh := hb(c)
	btn(sh, "SHED NON-ESSENTIAL", _shed)
	btn(sh, "RESTORE ALL", _restore)
	var right := vb(row, 8)
	right.custom_minimum_size.x = 400
	right.size_flags_horizontal = Control.SIZE_FILL
	var s := panel(right, "Buses", false)
	_total = meter(s, "TOTAL LOAD", 0.85, 1.0)
	for g in ["A", "B", "C"]:
		var m := meter(s, "BUS %s" % g, 0.85, 1.0)
		_groups[g] = m
	var gp := panel(right, "History")
	_graph = graph(gp, "DEMAND vs SUPPLY", "MW", 150)

func _idx() -> int:
	var m: Variant = table_selected(_tree)
	return -1 if m == null else int(m)

func _on_select() -> void:
	_sync_controls()

func _sync_controls() -> void:
	var i := _idx()
	if i < 0:
		return
	_syncing = true
	var b: Dictionary = st.buses[i]
	_sel_l.text = "%s  (bus %s, %.0f MW)" % [b["name"], b["group"], b["demand"]]
	set_slider(_alloc, b["alloc"])
	_breaker.set_pressed_no_signal(b["on"])
	_syncing = false

func _on_alloc(v: float) -> void:
	var i := _idx()
	if i >= 0 and not _syncing:
		st.buses[i]["alloc"] = v
		st.changed.emit()

func _on_breaker(on: bool) -> void:
	var i := _idx()
	if i >= 0 and not _syncing:
		st.buses[i]["on"] = on
		st.say("Breaker %s: %s" % ["closed" if on else "OPEN", st.buses[i]["name"]], "power")
		st.changed.emit()

func _shed() -> void:
	for b in st.buses:
		if b["name"] in ["Hydroponics", "Galley & crew", "Science labs", "Fabricator & cargo", "Lighting", "Medical"]:
			b["on"] = false
	st.say("Non-essential consumers shed", "power")
	st.changed.emit()

func _restore() -> void:
	for b in st.buses:
		b["on"] = true
		b["alloc"] = 100.0
	st.say("All consumers restored", "power")
	st.changed.emit()

func refresh() -> void:
	var rows: Array = []
	var metas: Array = []
	for i in st.buses.size():
		var b: Dictionary = st.buses[i]
		rows.append([b["name"], b["group"], "%.0f MW" % b["demand"], "%.0f%%" % b["alloc"], "%.0f MW" % st.bus_load(b), ["ON", T.OK] if b["on"] else ["OFF", T.BAD]])
		metas.append(i)
	table_fill(_tree, rows, metas)
	var sup := maxf(st.supply(), 1.0)
	_total.set_value(st.total_load() / sup, "%.0f / %.0f MW%s" % [st.total_load(), st.supply(), "  OVERLOAD" if st.brownout() else ""])
	for g in _groups.keys():
		var t := 0.0
		for b2 in st.buses:
			if b2["group"] == g:
				t += st.bus_load(b2)
		(_groups[g] as UIW.Meter).set_value(t / (sup / 3.0), "%.0f MW" % t)
	_graph.set_series([{"data": st.hist.get("demand", PackedFloat32Array()), "color": T.ACCENT}, {"data": st.hist.get("supply", PackedFloat32Array()), "color": T.WARN}])
