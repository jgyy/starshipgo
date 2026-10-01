extends AppBase
## Security: lock and unlock the real doors of the ship, lockdown, camera feeds, brig cells.

var _tabs: TabContainer
var _doors: Tree
var _filter: LineEdit
var _count: Label
var _cams: Tree
var _feed: UIW.Canvas
var _cells: Tree
var _t := 0.0

func title_text() -> String:
	return "SECURITY"

func build() -> void:
	_tabs = tab_container(self, ["DOORS", "CAMERAS", "BRIG"])
	var p := page(_tabs, 0)
	var top := hb(p)
	_filter = line_edit(top, "filter doors by room...", func(_t2: String) -> void: refresh())
	_filter.text_changed.connect(func(_t2: String) -> void: refresh())
	_count = lbl(top, "", 15, T.ACCENT)
	_doors = table(p, ["#", "Door", "State"], [40, 480, 90])
	var br := hb(p)
	btn(br, "LOCK SELECTED", func() -> void: _lock_sel(true))
	btn(br, "UNLOCK SELECTED", func() -> void: _lock_sel(false))
	btn(br, "LOCKDOWN (all doors, red alert)", _lockdown)
	btn(br, "RELEASE LOCKDOWN", _release)
	var cp := page(_tabs, 1)
	var cr := hb(cp, 10)
	_cams = table(cr, ["Camera", "Room"], [90, 220])
	var cams: Array = []
	var cm: Array = []
	for r in st.ship.get("rooms", []):
		if r.get("dept", "") != "transit" or r["id"].begins_with("cor"):
			cams.append(["CAM %02d" % (cams.size() + 1), r["name"]])
			cm.append(r["id"])
	table_fill(_cams, cams, cm)
	_feed = canvas(cr, 240)
	_feed.draw_fn = _draw_feed
	var bp := page(_tabs, 2)
	_cells = table(bp, ["Cell", "Occupant", "Field"], [100, 240, 100])
	table_fill(_cells, [["Cell 1", "(empty)", ["ON", T.OK]], ["Cell 2", "(empty)", ["ON", T.OK]], ["Cell 3", "(empty)", ["ON", T.OK]], ["Cell 4", "(empty)", ["ON", T.OK]]])

func _lock_sel(v: bool) -> void:
	var m: Variant = table_selected(_doors)
	if m != null:
		st.set_door_locked(int(m), v)

func _lockdown() -> void:
	st.lock_all(true)
	st.set_alert("red")

func _release() -> void:
	st.lock_all(false)
	st.set_alert("green")

func tick(dt: float) -> void:
	_t += dt
	if _tabs.current_tab == 1:
		_feed.queue_redraw()

func _draw_feed(c: UIW.Canvas) -> void:
	var m: Variant = table_selected(_cams)
	for i in 90:
		var h := hash("%d%d" % [i, int(_t * 14.0)])
		c.draw_line(Vector2(0, float(h & 0xff) / 255.0 * c.size.y), Vector2(c.size.x, float(h & 0xff) / 255.0 * c.size.y), Color(0.3, 0.7, 0.5, 0.06), 1.0)
	var f := c.get_theme_default_font()
	if m == null:
		c.draw_string(f, Vector2(14, 24), "SELECT A CAMERA", HORIZONTAL_ALIGNMENT_LEFT, -1, 16, T.TEXT_DIM)
		return
	var rname := String(m)
	for r in st.ship.get("rooms", []):
		if r["id"] == m:
			rname = r["name"]
			var rc: Array = r["rect"]
			var sc := minf((c.size.x - 40) / (rc[2] - rc[0]), (c.size.y - 60) / (rc[3] - rc[1]))
			c.draw_rect(Rect2(20, 40, (rc[2] - rc[0]) * sc, (rc[3] - rc[1]) * sc), Color(0.2, 0.6, 0.5, 0.35), false, 2.0)
			for k in st.crew:
				if k["room"] == m:
					c.draw_circle(Vector2(20 + (rc[2] - rc[0]) * sc * (0.2 + 0.6 * rnd(k["name"], 1)), 40 + (rc[3] - rc[1]) * sc * (0.2 + 0.6 * rnd(k["name"], 2))), 5.0, Color(1.0, 0.8, 0.3))
	c.draw_string(f, Vector2(14, 22), "REC  %s   %s" % [rname.to_upper(), st.ship_clock()], HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color(1.0, 0.4, 0.35) if int(_t * 2.0) % 2 == 0 else T.TEXT)

func refresh() -> void:
	var rows: Array = []
	var metas: Array = []
	var q := _filter.text.to_lower()
	for i in st.doors.size():
		var lab := st.door_label(i)
		if q != "" and not lab.to_lower().contains(q):
			continue
		rows.append([str(i), lab, ["LOCKED", T.BAD] if st.door_locked(i) else ["open", T.OK]])
		metas.append(i)
	table_fill(_doors, rows, metas)
	_count.text = "%d / %d locked" % [st.locked_count(), st.doors.size()]
