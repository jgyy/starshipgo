extends AppBase
## Fabricator: queue parts made from stock (alloy, polymer, circuits).  Progress runs while a terminal is open;
## finished parts land in the cargo manifest.

var _rec: Tree
var _queue: Tree
var _stock: Label
var _status: Label

const RECIPES := [
	{"id": "coil", "name": "Lattice coil spare", "alloy": 120.0, "polymer": 20.0, "circuits": 30.0, "secs": 40.0, "mass": 640.0},
	{"id": "medkit", "name": "Field medical kit", "alloy": 2.0, "polymer": 18.0, "circuits": 6.0, "secs": 12.0, "mass": 3.0},
	{"id": "patch", "name": "Hull patch panel", "alloy": 40.0, "polymer": 4.0, "circuits": 0.0, "secs": 18.0, "mass": 60.0},
	{"id": "board", "name": "Control board", "alloy": 1.0, "polymer": 3.0, "circuits": 12.0, "secs": 8.0, "mass": 0.4},
	{"id": "tool", "name": "Multi-tool", "alloy": 4.0, "polymer": 3.0, "circuits": 2.0, "secs": 6.0, "mass": 0.6},
	{"id": "filter", "name": "Scrubber cartridge", "alloy": 6.0, "polymer": 22.0, "circuits": 3.0, "secs": 14.0, "mass": 4.0},
]

func title_text() -> String:
	return "FABRICATOR"

func build() -> void:
	var row := hb(self, 10)
	var left := panel(row, "Recipes")
	_rec = table(left, ["Part", "Alloy", "Polymer", "Circuits", "Time"], [200, 60, 70, 70, 60])
	var rows: Array = []
	var metas: Array = []
	for i in RECIPES.size():
		var r: Dictionary = RECIPES[i]
		rows.append([r["name"], "%.0f" % r["alloy"], "%.0f" % r["polymer"], "%.0f" % r["circuits"], "%.0f s" % r["secs"]])
		metas.append(i)
	table_fill(_rec, rows, metas)
	var br := hb(left)
	btn(br, "FABRICATE", func() -> void: _make(1))
	btn(br, "x5", func() -> void: _make(5))
	_status = wrap_lbl(left, "", 14, T.TEXT_DIM)
	var right := vb(row, 8)
	right.custom_minimum_size.x = 360
	right.size_flags_horizontal = Control.SIZE_FILL
	var sp := panel(right, "Stock", false)
	_stock = lbl(sp, "", 15, T.TEXT)
	var qp := panel(right, "Queue")
	_queue = table(qp, ["Job", "Progress"], [200, 100])
	btn(qp, "CLEAR QUEUE (refund)", _clear)

func _make(n: int) -> void:
	var m: Variant = table_selected(_rec)
	if m == null:
		_status.text = "Select a recipe first."
		return
	var r: Dictionary = RECIPES[int(m)]
	for k in n:
		for mat in ["alloy", "polymer", "circuits"]:
			if float(st.stock[mat]) < float(r[mat]):
				_status.text = "Not enough %s." % mat
				return
		for mat in ["alloy", "polymer", "circuits"]:
			st.stock[mat] = float(st.stock[mat]) - float(r[mat])
		st.fab_queue.append({"id": r["id"], "name": r["name"], "secs": r["secs"], "progress": 0.0, "mass": r["mass"], "cost": [r["alloy"], r["polymer"], r["circuits"]]})
	_status.text = "Queued %d x %s." % [n, r["name"]]
	st.say("Fabricator queued %d x %s" % [n, r["name"]], "engineering")
	st.changed.emit()

func _clear() -> void:
	for j in st.fab_queue:
		st.stock["alloy"] = float(st.stock["alloy"]) + float(j["cost"][0])
		st.stock["polymer"] = float(st.stock["polymer"]) + float(j["cost"][1])
		st.stock["circuits"] = float(st.stock["circuits"]) + float(j["cost"][2])
	st.fab_queue.clear()
	st.changed.emit()

func refresh() -> void:
	_stock.text = "Alloy %.0f kg    Polymer %.0f kg    Circuits %.0f units" % [st.stock["alloy"], st.stock["polymer"], st.stock["circuits"]]
	var rows: Array = []
	for j in st.fab_queue:
		rows.append([j["name"], "%.0f%%" % j["progress"]])
	table_fill(_queue, rows)
