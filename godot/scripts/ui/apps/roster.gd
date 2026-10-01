extends AppBase
## Crew roster: filter by department, search, profile with location; call the crew member (intercom message).

var _tree: Tree
var _dept: OptionButton
var _search: LineEdit
var _prof: Label
var _note: Label

func title_text() -> String:
	return "CREW ROSTER"

func build() -> void:
	var row := hb(self, 10)
	var left := vb(row, 6)
	left.size_flags_stretch_ratio = 1.5
	var tb := hb(left)
	_search = line_edit(tb, "search name or role...", func(_t: String) -> void: refresh())
	_search.text_changed.connect(func(_t: String) -> void: refresh())
	_dept = OptionButton.new()
	_dept.focus_mode = Control.FOCUS_NONE
	_dept.add_item("ALL DEPARTMENTS")
	for d in ["command", "engineering", "medical", "science", "security", "crew", "cargo", "life"]:
		_dept.add_item(d.to_upper())
	_dept.item_selected.connect(func(_i: int) -> void: refresh())
	tb.add_child(_dept)
	_tree = table(left, ["Name", "Role", "Dept", "Location"], [170, 150, 90, 160])
	_tree.item_selected.connect(refresh)
	var right := panel(row, "Profile")
	right.custom_minimum_size.x = 340
	_prof = wrap_lbl(right, "Select a crew member.", 16, T.TEXT)
	_note = wrap_lbl(right, "", 14, T.TEXT_DIM)
	btn(right, "CALL ON INTERCOM", _call)

func _call() -> void:
	var m: Variant = table_selected(_tree)
	if m == null:
		return
	var c: Dictionary = st.crew[int(m)]
	st.say("Intercom: called %s (%s)" % [c["name"], c["role"]], "comms")
	_note.text = "%s acknowledges: \"On my way.\"" % c["name"]

func refresh() -> void:
	var rows: Array = []
	var metas: Array = []
	var q := _search.text.to_lower()
	var d := "" if _dept.selected <= 0 else _dept.get_item_text(_dept.selected).to_lower()
	for i in st.crew.size():
		var c: Dictionary = st.crew[i]
		if d != "" and c["dept"] != d:
			continue
		if q != "" and not (String(c["name"]).to_lower().contains(q) or String(c["role"]).to_lower().contains(q)):
			continue
		rows.append([c["name"], c["role"], String(c["dept"]).capitalize(), _room(c["room"])])
		metas.append(i)
	table_fill(_tree, rows, metas)
	var m: Variant = table_selected(_tree)
	if m != null:
		var c2: Dictionary = st.crew[int(m)]
		_prof.text = "%s\n%s - %s department\nLocation: %s\nStatus: %s" % [c2["name"], c2["role"], String(c2["dept"]).capitalize(), _room(c2["room"]), String(c2["status"]).to_upper()]

func _room(rid: String) -> String:
	for r in st.ship.get("rooms", []):
		if r["id"] == rid:
			return "%s (deck %s)" % [r["name"], r["deck"]]
	return rid
