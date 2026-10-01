class_name AppBase
extends Control
## Base class of every terminal application.  An app is a Control tree built in code:
##   build()        create widgets (called once by start())
##   refresh()      pull values from ShipState into the widgets (4 Hz while the terminal is open, and on open)
##   tick(dt)       per-frame animation hook (scopes, spinning holograms) - keep it cheap
##   title_text()   default window title; the terminal prefixes the host machine's label
## The helper methods below create themed widgets so apps stay short.

const T = preload("res://scripts/ui/ui_theme.gd")

var st: ShipState
var host: Dictionary = {}             # {model, label, category, room, room_name, tex, app, title}
var app_id := ""
var terminal: Node                    # the Terminal overlay (for close / log helpers)

func _init() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	size_flags_horizontal = Control.SIZE_EXPAND_FILL
	size_flags_vertical = Control.SIZE_EXPAND_FILL

func start(state: ShipState, h: Dictionary) -> void:
	st = state
	host = h
	build()
	refresh()

func build() -> void:
	pass

func refresh() -> void:
	pass

func tick(_dt: float) -> void:
	pass

func title_text() -> String:
	return app_id.to_upper()

## Initial tab/mode hint from the host machine's screen texture (e.g. radar -> sensors).
func host_tex() -> String:
	return String(host.get("tex", ""))

# ------------------------------------------------------------------ widget helpers
func _add(parent: Node, c: Control) -> Control:
	if parent != null:
		parent.add_child(c)
	return c

func fill(c: Control, h := true, v := true) -> Control:
	if h:
		c.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	if v:
		c.size_flags_vertical = Control.SIZE_EXPAND_FILL
	return c

func vb(parent: Node = null, sep := -1) -> VBoxContainer:
	var b := VBoxContainer.new()
	if sep >= 0:
		b.add_theme_constant_override("separation", sep)
	fill(b)
	_add(parent, b)
	return b

func hb(parent: Node = null, sep := -1) -> HBoxContainer:
	var b := HBoxContainer.new()
	if sep >= 0:
		b.add_theme_constant_override("separation", sep)
	fill(b, true, false)
	_add(parent, b)
	return b

func grid(parent: Node, cols: int) -> GridContainer:
	var g := GridContainer.new()
	g.columns = cols
	fill(g, true, false)
	_add(parent, g)
	return g

func lbl(parent: Node, text: String, size := 15, col := T.TEXT) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", col)
	_add(parent, l)
	return l

func wrap_lbl(parent: Node, text: String, size := 15, col := T.TEXT) -> Label:
	var l := lbl(parent, text, size, col)
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	return l

func heading(parent: Node, text: String) -> void:
	lbl(parent, text.to_upper(), 16, T.ACCENT)
	var s := HSeparator.new()
	s.add_theme_stylebox_override("separator", T.box(T.RULE, T.RULE, 0, 0, 0))
	_add(parent, s)

## Titled panel; returns the inner VBox to add content to.
func panel(parent: Node, title := "", expand := true) -> VBoxContainer:
	var p := PanelContainer.new()
	if expand:
		fill(p)
	else:
		fill(p, true, false)
	_add(parent, p)
	var v := VBoxContainer.new()
	fill(v)
	p.add_child(v)
	if title != "":
		heading(v, title)
	return v

func btn(parent: Node, text: String, cb: Callable, toggle := false) -> Button:
	var b := Button.new()
	b.text = text
	b.toggle_mode = toggle
	b.focus_mode = Control.FOCUS_NONE
	if cb.is_valid():
		if toggle:
			b.toggled.connect(func(on: bool) -> void:
				if st: st.click()
				cb.call(on))
		else:
			b.pressed.connect(func() -> void:
				if st: st.click()
				cb.call())
	_add(parent, b)
	return b

func check(parent: Node, text: String, on: bool, cb: Callable) -> CheckButton:
	var c := CheckButton.new()
	c.text = text
	c.button_pressed = on
	c.focus_mode = Control.FOCUS_NONE
	c.toggled.connect(func(v: bool) -> void:
		if st: st.click()
		cb.call(v))
	_add(parent, c)
	return c

## Labelled slider row.  The value label is kept in the slider's meta "vl".
func slider(parent: Node, caption: String, lo: float, hi: float, val: float, cb: Callable, step := 1.0, fmt := "%.0f") -> HSlider:
	var row := hb(parent)
	var cl := lbl(row, caption, 14, T.TEXT_DIM)
	cl.custom_minimum_size.x = 130
	var s := HSlider.new()
	s.min_value = lo
	s.max_value = hi
	s.step = step
	s.value = val
	s.focus_mode = Control.FOCUS_NONE
	s.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	s.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	s.custom_minimum_size.y = 20
	row.add_child(s)
	var vl := lbl(row, fmt % val, 14, T.TEXT)
	vl.custom_minimum_size.x = 64
	vl.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	s.set_meta("vl", vl)
	s.set_meta("fmt", fmt)
	s.value_changed.connect(func(v: float) -> void:
		vl.text = fmt % v
		cb.call(v))
	return s

## Move a slider without firing its callback (used by refresh()).
func set_slider(s: HSlider, v: float) -> void:
	s.set_value_no_signal(v)
	(s.get_meta("vl") as Label).text = String(s.get_meta("fmt")) % v

func meter(parent: Node, caption: String, warn := -1.0, crit := -1.0) -> UIW.Meter:
	var m := UIW.Meter.new()
	m.caption = caption
	m.warn = warn
	m.crit = crit
	fill(m, true, false)
	_add(parent, m)
	return m

func graph(parent: Node, title: String, unit := "", h := 110) -> UIW.Graph:
	var g := UIW.Graph.new()
	g.title = title
	g.unit = unit
	g.custom_minimum_size.y = h
	fill(g)
	_add(parent, g)
	return g

func canvas(parent: Node, h := 200) -> UIW.Canvas:
	var c := UIW.Canvas.new()
	c.custom_minimum_size.y = h
	fill(c)
	_add(parent, c)
	return c

func rich(parent: Node, bbcode := "") -> RichTextLabel:
	var r := RichTextLabel.new()
	r.bbcode_enabled = true
	r.scroll_active = true
	r.selection_enabled = false
	r.focus_mode = Control.FOCUS_NONE
	fill(r)
	r.text = bbcode
	_add(parent, r)
	return r

func line_edit(parent: Node, placeholder: String, on_submit: Callable) -> LineEdit:
	var e := LineEdit.new()
	e.placeholder_text = placeholder
	e.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	if on_submit.is_valid():
		e.text_submitted.connect(on_submit)
	_add(parent, e)
	return e

func tab_container(parent: Node, names: Array) -> TabContainer:
	var tc := TabContainer.new()
	fill(tc)
	tc.focus_mode = Control.FOCUS_NONE
	_add(parent, tc)
	for n in names:
		var page := VBoxContainer.new()
		page.name = n
		fill(page)
		tc.add_child(page)
	return tc

func page(tc: TabContainer, i: int) -> VBoxContainer:
	return tc.get_child(i) as VBoxContainer

## Table backed by a Tree.  Rows are Arrays of cells; a cell is a String or [String, Color].
func table(parent: Node, cols: Array, widths: Array = []) -> Tree:
	var t := Tree.new()
	t.columns = cols.size()
	t.column_titles_visible = true
	t.hide_root = true
	t.select_mode = Tree.SELECT_ROW
	t.focus_mode = Control.FOCUS_NONE
	fill(t)
	for i in cols.size():
		t.set_column_title(i, String(cols[i]).to_upper())
		t.set_column_expand(i, true)
		if i < widths.size():
			t.set_column_custom_minimum_width(i, int(widths[i]))
			t.set_column_expand_ratio(i, int(widths[i]))
	_add(parent, t)
	return t

func table_fill(t: Tree, rows: Array, metas: Array = []) -> void:
	var root := t.get_root()
	if root == null:
		root = t.create_item()
	var items := root.get_children()
	if items.size() != rows.size():
		var sel_meta: Variant = table_selected(t)
		for it in items:
			it.free()
		items = []
		for i in rows.size():
			items.append(t.create_item(root))
		_table_set(t, items, rows, metas)
		if sel_meta != null:
			for it in items:
				if it.get_metadata(0) == sel_meta:
					it.select(0)
					break
		return
	_table_set(t, items, rows, metas)

func _table_set(t: Tree, items: Array, rows: Array, metas: Array) -> void:
	for i in rows.size():
		var it: TreeItem = items[i]
		var row: Array = rows[i]
		for c in row.size():
			var cell: Variant = row[c]
			if cell is Array:
				it.set_text(c, String(cell[0]))
				it.set_custom_color(c, cell[1])
			else:
				it.set_text(c, String(cell))
		if i < metas.size():
			it.set_metadata(0, metas[i])
		else:
			it.set_metadata(0, i)

func table_selected(t: Tree) -> Variant:
	var s := t.get_selected()
	return null if s == null else s.get_metadata(0)

## Select the row carrying this metadata (emits item_selected).
func table_select(t: Tree, meta: Variant) -> void:
	var root := t.get_root()
	if root == null:
		return
	for it in root.get_children():
		if it.get_metadata(0) == meta:
			it.select(0)
			t.item_selected.emit()
			return

func status_dot(ok: bool) -> Array:
	return ["ONLINE", T.OK] if ok else ["OFFLINE", T.BAD]

func pct_cell(v: float, lo_bad := 40.0, lo_warn := 70.0) -> Array:
	var col := T.OK
	if v < lo_bad:
		col = T.BAD
	elif v < lo_warn:
		col = T.WARN
	return ["%.0f%%" % v, col]

## Deterministic pseudo-random float in [0,1) from a string key (stable per machine / room).
func rnd(key: String, salt := 0) -> float:
	var h := hash(key + str(salt))
	return float(h & 0xffff) / 65536.0

func timer_ms() -> int:
	return Time.get_ticks_msec()
