extends AppBase
## Ship's log: crew log entries from lore.json (filter by role, open in a reader), the live ship event log, and a
## personal entry box.

var _tabs: TabContainer
var _tree: Tree
var _role: OptionButton
var _reader: RichTextLabel
var _events: RichTextLabel
var _last := ""
var _entry: LineEdit

func title_text() -> String:
	return "SHIP'S LOG"

func build() -> void:
	_tabs = tab_container(self, ["CREW LOGS", "SHIP EVENTS"])
	var row := hb(page(_tabs, 0), 10)
	var left := vb(row, 6)
	left.size_flags_stretch_ratio = 1.0
	_role = OptionButton.new()
	_role.focus_mode = Control.FOCUS_NONE
	_role.add_item("ALL ROLES")
	var roles := {}
	for l in Lore.logs():
		roles[l["role"]] = true
	for r in roles.keys():
		_role.add_item(String(r).to_upper())
	_role.item_selected.connect(func(_i: int) -> void: _fill())
	left.add_child(_role)
	_tree = table(left, ["SD", "Role", "Title"], [70, 120, 160])
	_tree.item_selected.connect(_read)
	_reader = rich(row)
	_reader.size_flags_stretch_ratio = 1.3
	_fill()
	var ev := page(_tabs, 1)
	_events = rich(ev)
	_events.scroll_following = true
	var er := hb(ev)
	_entry = line_edit(er, "add a personal log entry...", _add_entry)
	btn(er, "ADD", func() -> void: _add_entry(_entry.text))

func _fill() -> void:
	var rows: Array = []
	var metas: Array = []
	var want := "" if _role.selected <= 0 else _role.get_item_text(_role.selected)
	var logs := Lore.logs()
	for i in logs.size():
		var l: Dictionary = logs[i]
		if want != "" and String(l["role"]).to_upper() != want:
			continue
		rows.append([l["stardate"], l["role"], l["title"]])
		metas.append(i)
	table_fill(_tree, rows, metas)
	if rows.is_empty():
		_reader.text = "[color=#7a95a0]No crew log entries in lore.json.[/color]"

func _read() -> void:
	var m: Variant = table_selected(_tree)
	if m == null:
		return
	var l: Dictionary = Lore.logs()[int(m)]
	var loc := ""
	for r in st.ship.get("rooms", []):
		if r["id"] == l.get("room", ""):
			loc = "  -  recorded in %s" % r["name"]
	_reader.text = "[b][color=#5cd6e0]%s[/color][/b]\n[color=#7a95a0]%s, stardate %s%s[/color]\n\n%s" % [l["title"], l["role"], l["stardate"], loc, l["text"]]

func _add_entry(t: String) -> void:
	t = t.strip_edges()
	if t == "":
		return
	st.say("Personal log: " + t, "log")
	_entry.clear()

func refresh() -> void:
	var out := ""
	for m in st.messages:
		out += "[color=#7a95a0]%s[/color]  %s\n" % [m["t"], String(m["text"]).replace("[", "[lb]")]
	if out != _last:
		_last = out
		_events.text = out

func demo() -> void:
	table_select(_tree, 3)
