extends AppBase
## Engineering status: subsystem health with a repair queue, a ship schematic, and the engineering log.

var _tree: Tree
var _tabs: TabContainer
var _schem: UIW.Canvas
var _log: RichTextLabel
var _last_log := ""
var _summary: Label

func title_text() -> String:
	return "ENGINEERING STATUS"

func build() -> void:
	_tabs = tab_container(self, ["SUBSYSTEMS", "SCHEMATIC", "LOG"])
	var p := page(_tabs, 0)
	_summary = lbl(p, "", 16, T.ACCENT)
	_tree = table(p, ["Subsystem", "Health", "State"], [220, 90, 120])
	var br := hb(p)
	btn(br, "REPAIR SELECTED", _repair_sel)
	btn(br, "REPAIR ALL DAMAGED", _repair_all)
	btn(br, "RUN STRESS TEST", _stress)
	_schem = canvas(page(_tabs, 1), 300)
	_schem.draw_fn = _draw_schem
	_log = rich(page(_tabs, 2))
	_log.scroll_following = true
	if host_tex() == "schematic":
		_tabs.current_tab = 1

func _sel() -> int:
	var m: Variant = table_selected(_tree)
	return -1 if m == null else int(m)

func _repair_sel() -> void:
	var i := _sel()
	if i >= 0:
		st.subsystems[i]["repair"] = true
		st.say("Repair crew assigned to %s" % st.subsystems[i]["name"], "engineering")
		st.changed.emit()

func _repair_all() -> void:
	for s in st.subsystems:
		if float(s["health"]) < 98.0:
			s["repair"] = true
	st.say("Damage control: repairing all damaged systems", "engineering")
	st.changed.emit()

func _stress() -> void:
	var s: Dictionary = st.subsystems[randi() % st.subsystems.size()]
	s["health"] = maxf(35.0, float(s["health"]) - 22.0)
	st.say("Stress test strained %s" % s["name"], "warn")
	st.changed.emit()

func tick(_dt: float) -> void:
	if _tabs.current_tab == 1:
		_schem.queue_redraw()

func refresh() -> void:
	var rows: Array = []
	var metas: Array = []
	var worst := 100.0
	for i in st.subsystems.size():
		var s: Dictionary = st.subsystems[i]
		worst = minf(worst, float(s["health"]))
		rows.append([s["name"], pct_cell(float(s["health"])), ["REPAIRING", T.WARN] if s["repair"] else (["NOMINAL", T.OK] if float(s["health"]) > 85.0 else ["DEGRADED", T.WARN])])
		metas.append(i)
	table_fill(_tree, rows, metas)
	_summary.text = "Ship integrity: %.0f%% (weakest: %.0f%%)    Power %.0f/%.0f MW" % [_avg(), worst, st.total_load(), st.supply()]
	var out := ""
	for m in st.messages.slice(maxi(0, st.messages.size() - 40)):
		out += "[%s] %s\n" % [m["t"], m["text"]]
	if out != _last_log:
		_last_log = out
		_log.text = out

func _avg() -> float:
	var t := 0.0
	for s in st.subsystems:
		t += float(s["health"])
	return t / maxf(1.0, st.subsystems.size())

func _draw_schem(c: UIW.Canvas) -> void:
	var f := c.get_theme_default_font()
	var w := c.size.x - 60.0
	var h := c.size.y - 60.0
	var x0 := 30.0
	var y0 := 30.0
	var hull := PackedVector2Array([Vector2(x0, y0 + h * 0.5), Vector2(x0 + w * 0.15, y0), Vector2(x0 + w, y0 + h * 0.2), Vector2(x0 + w, y0 + h * 0.8), Vector2(x0 + w * 0.15, y0 + h)])
	c.draw_colored_polygon(hull, Color(0.05, 0.12, 0.15))
	c.draw_polyline(hull + PackedVector2Array([hull[0]]), T.ACCENT_DIM, 2.0, true)
	var slots := [[0.18, 0.5], [0.4, 0.3], [0.4, 0.7], [0.58, 0.5], [0.72, 0.3], [0.72, 0.7], [0.86, 0.35], [0.86, 0.65], [0.3, 0.5], [0.5, 0.15]]
	for i in st.subsystems.size():
		var s: Dictionary = st.subsystems[i]
		var p := Vector2(x0 + w * slots[i][0], y0 + h * slots[i][1])
		var hv := float(s["health"])
		var col := T.OK if hv > 85.0 else (T.WARN if hv > 55.0 else T.BAD)
		c.draw_circle(p, 12.0, Color(col.r, col.g, col.b, 0.25))
		c.draw_arc(p, 12.0, -PI * 0.5, -PI * 0.5 + TAU * hv / 100.0, 24, col, 3.0, true)
		c.draw_string(f, p + Vector2(-40, 28), s["name"], HORIZONTAL_ALIGNMENT_CENTER, 80, 10, T.TEXT)
