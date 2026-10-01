extends AppBase
## Cargo manifest: stock, mass against capacity, search / category filter, jettison and transfer actions.

const CAPACITY_KG := 60000.0

var _tree: Tree
var _filter: LineEdit
var _cat: OptionButton
var _cap: UIW.Meter
var _qty: HSlider
var _info: Label

func title_text() -> String:
	return "CARGO MANIFEST"

func build() -> void:
	var v := vb(self, 8)
	var top := hb(v)
	_filter = line_edit(top, "search cargo...", func(_t: String) -> void: refresh())
	_filter.text_changed.connect(func(_t: String) -> void: refresh())
	_cat = OptionButton.new()
	_cat.focus_mode = Control.FOCUS_NONE
	_cat.add_item("ALL CATEGORIES")
	for c in ["engineering", "medical", "food", "science", "general", "fabricated"]:
		_cat.add_item(c.to_upper())
	_cat.item_selected.connect(func(_i: int) -> void: refresh())
	top.add_child(_cat)
	_cap = meter(v, "HOLD", 0.8, 0.95)
	_tree = table(v, ["Item", "Category", "Qty", "Unit mass", "Total"], [260, 110, 70, 90, 100])
	_tree.item_selected.connect(refresh)
	var br := hb(v)
	_qty = slider(br, "Quantity", 1, 50, 1, func(_x: float) -> void: pass, 1.0, "%.0f")
	btn(br, "JETTISON", _jettison)
	btn(br, "TO HANGAR", _transfer)
	btn(br, "RESUPPLY +10", _resupply)
	_info = lbl(v, "", 14, T.TEXT_DIM)

func _sel() -> String:
	var m: Variant = table_selected(_tree)
	return "" if m == null else String(m)

func _jettison() -> void:
	var c := st.cargo_item(_sel())
	if c.is_empty():
		return
	var n := mini(int(c["qty"]), int(_qty.value))
	c["qty"] = int(c["qty"]) - n
	if int(c["qty"]) <= 0:
		st.cargo.erase(c)
	st.say("Jettisoned %d x %s" % [n, c["name"]], "cargo")
	st.changed.emit()

func _transfer() -> void:
	var c := st.cargo_item(_sel())
	if c.is_empty():
		return
	st.say("Moved %d x %s to the hangar loading bay" % [mini(int(c["qty"]), int(_qty.value)), c["name"]], "cargo")
	_info.text = "Cargo loader dispatched."

func _resupply() -> void:
	var c := st.cargo_item(_sel())
	if c.is_empty():
		return
	c["qty"] = int(c["qty"]) + 10
	st.say("Resupplied 10 x %s" % c["name"], "cargo")
	st.changed.emit()

func refresh() -> void:
	var rows: Array = []
	var metas: Array = []
	var q := _filter.text.to_lower()
	var cat := "" if _cat.selected <= 0 else _cat.get_item_text(_cat.selected).to_lower()
	for c in st.cargo:
		if q != "" and not String(c["name"]).to_lower().contains(q):
			continue
		if cat != "" and c["cat"] != cat:
			continue
		rows.append([c["name"], String(c["cat"]).capitalize(), str(c["qty"]), "%.1f kg" % c["mass"], "%.0f kg" % (float(c["qty"]) * float(c["mass"]))])
		metas.append(c["id"])
	table_fill(_tree, rows, metas)
	_cap.set_value(st.cargo_mass() / CAPACITY_KG, "%.0f / %.0f kg" % [st.cargo_mass(), CAPACITY_KG])
