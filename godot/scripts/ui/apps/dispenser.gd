extends AppBase
## Shared food dispenser UI for the galley replicator (free crew meals) and the vending machines (credits).
## The menu is built from catalog.json: models in food-like categories (tableware, food, drink ...) or whose id
## names food or drink.  Specs and prices come from specs.json when it has an entry.

const FOOD_CATS := ["tableware", "food", "drink", "beverage", "meal", "snack", "bakery", "dessert", "produce", "fruit"]
const FOOD_WORDS := ["food", "drink", "meal", "coffee", "tea", "snack", "fruit", "salad", "bread", "pizza", "soup", "juice", "pastry", "cake", "burger", "sandwich", "noodle", "rice", "cheese", "milk", "lunch", "dessert"]
const VEND_WORDS := ["cup", "mug", "bottle", "drink", "coffee", "tea", "snack", "bar", "fruit", "juice", "water", "pitcher", "bread", "salad", "lunch", "pizza"]

var mode := "galley"                   # "galley" (free) or "vending" (credits)
var _items: Array = []                 # [{id, label, category, price}]
var _tree: Tree
var _filter: LineEdit
var _cat: OptionButton
var _detail: Tree
var _title: Label
var _qty: HSlider
var _credits: Label
var _hist: RichTextLabel
var _status: Label
var _equip: Tree

func title_text() -> String:
	return "VENDING" if mode == "vending" else "GALLEY REPLICATOR"

func is_food(id: String, e: Dictionary) -> bool:
	var cat: String = e.get("category", "")
	if cat in ["vending", "galley", "planter", "plant", "chair", "table", "bench"]:
		return false
	if cat in FOOD_CATS:
		return true
	var toks := id.split("_")
	for w in FOOD_WORDS:
		if w in toks:
			return true
	return false

func price_of(id: String) -> float:
	if mode == "galley":
		return 0.0
	var sp := Lore.spec(id)
	for k in ["price", "price_cr", "cost"]:
		if sp.has(k) and (sp[k] is float or sp[k] is int):
			return float(sp[k]) * 0.02 if float(sp[k]) > 100.0 else float(sp[k])
	return snappedf(1.0 + rnd(id, 5) * 4.5, 0.05)

func build() -> void:
	for id in st.catalog.keys():
		var e: Dictionary = st.catalog[id]
		if not is_food(id, e):
			continue
		if mode == "vending":
			var ok := false
			for w in VEND_WORDS:
				if id.contains(w):
					ok = true
			if not ok:
				continue
		_items.append({"id": id, "label": String(e.get("label", id)).capitalize(), "category": e.get("category", ""), "price": price_of(id)})
	if mode == "vending" and _items.is_empty():
		for id in st.catalog.keys():
			if is_food(id, st.catalog[id]):
				_items.append({"id": id, "label": String(st.catalog[id].get("label", id)).capitalize(), "category": st.catalog[id].get("category", ""), "price": price_of(id)})
	_items.sort_custom(func(a: Dictionary, b: Dictionary) -> bool: return a["label"] < b["label"])
	var row := hb(self, 10)
	var left := vb(row, 6)
	left.size_flags_stretch_ratio = 1.3
	var tb := hb(left)
	_filter = line_edit(tb, "search the menu...", func(_t: String) -> void: refresh())
	_filter.text_changed.connect(func(_t: String) -> void: refresh())
	_cat = OptionButton.new()
	_cat.focus_mode = Control.FOCUS_NONE
	_cat.add_item("ALL")
	var cats := {}
	for it in _items:
		cats[it["category"]] = true
	var cl: Array = cats.keys()
	cl.sort()
	for c in cl:
		_cat.add_item(String(c).to_upper())
	_cat.item_selected.connect(func(_i: int) -> void: refresh())
	tb.add_child(_cat)
	_tree = table(left, ["Item", "Category", "Price"], [230, 110, 70])
	_tree.item_selected.connect(_show_item)
	var right := vb(row, 6)
	right.custom_minimum_size.x = 400
	right.size_flags_horizontal = Control.SIZE_FILL
	_title = lbl(right, "Select an item", 20, T.ACCENT)
	_detail = table(right, ["Property", "Value"], [120, 240])
	_detail.custom_minimum_size.y = 150
	_qty = slider(right, "Quantity", 1, 6, 1, func(_v: float) -> void: pass, 1.0, "%.0f")
	var br := hb(right)
	btn(br, "DISPENSE", _dispense)
	_credits = lbl(br, "", 15, T.WARN)
	_status = wrap_lbl(right, "", 14, T.TEXT_DIM)
	_hist = rich(right)
	_hist.scroll_following = true
	_hist.custom_minimum_size.y = 90
	refresh()

func _sel() -> Dictionary:
	var m: Variant = table_selected(_tree)
	if m == null:
		return {}
	for it in _items:
		if it["id"] == m:
			return it
	return {}

func _show_item() -> void:
	var it := _sel()
	if it.is_empty():
		return
	_title.text = String(it["label"]).to_upper()
	var e: Dictionary = st.catalog.get(it["id"], {})
	var rows: Array = [["Model", it["id"]], ["Category", String(it["category"]).capitalize()]]
	if e.has("size"):
		rows.append(["Size", "%.2f x %.2f x %.2f m" % [e["size"][0], e["size"][1], e["size"][2]]])
	rows.append(["Price", "free (crew ration)" if mode == "galley" else "%.2f cr" % it["price"]])
	var sp := Lore.spec(it["id"])
	for k in sp.keys():
		rows.append([String(k).replace("_", " ").capitalize(), ", ".join(sp[k]) if sp[k] is Array else str(sp[k])])
	if sp.is_empty():
		rows.append(["Specs", ["no record in specs.json", T.TEXT_DIM]])
	table_fill(_detail, rows)

func _dispense() -> void:
	var it := _sel()
	if it.is_empty():
		_status.text = "Select an item first."
		return
	var n := int(_qty.value)
	var done := 0
	for i in n:
		if st.dispense(it["id"], it["label"], float(it["price"])):
			done += 1
	if done > 0:
		st.dispensed += done
		_hist.append_text("%d x %s\n" % [done, it["label"]])
		_status.text = "Dispensed %d x %s." % [done, it["label"]]
	else:
		_status.text = "Not enough credits."
	st.changed.emit()

func refresh() -> void:
	var rows: Array = []
	var metas: Array = []
	var q := _filter.text.to_lower()
	var cat := "" if _cat.selected <= 0 else _cat.get_item_text(_cat.selected).to_lower()
	for it in _items:
		if q != "" and not String(it["label"]).to_lower().contains(q):
			continue
		if cat != "" and it["category"] != cat:
			continue
		rows.append([it["label"], String(it["category"]).capitalize(), "free" if mode == "galley" else "%.2f cr" % it["price"]])
		metas.append(it["id"])
	table_fill(_tree, rows, metas)
	_credits.text = "Credits: %.2f" % st.credits if mode == "vending" else "Served: %d" % st.dispensed

func demo() -> void:
	if not _items.is_empty():
		table_select(_tree, _items[mini(3, _items.size() - 1)]["id"])
