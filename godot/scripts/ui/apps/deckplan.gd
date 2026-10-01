extends AppBase
## Deck plan from ship.json: hull outline, rooms by department, doors (red = locked), you-are-here, room search.

var deck := 1
var selected := ""
var _cv: UIW.Canvas
var _search: LineEdit
var _tree: Tree
var _info: Label
var _deck_btns: Array = []
var _xf := {"o": Vector2.ZERO, "s": 1.0}

const DEPT := {
	"command": Color(0.25, 0.45, 0.9), "engineering": Color(0.95, 0.55, 0.15), "medical": Color(0.35, 0.85, 0.8),
	"science": Color(0.35, 0.8, 0.4), "security": Color(0.9, 0.3, 0.3), "crew": Color(0.7, 0.6, 0.9),
	"cargo": Color(0.75, 0.7, 0.3), "transit": Color(0.5, 0.55, 0.62), "life": Color(0.3, 0.75, 0.6),
}

func title_text() -> String:
	return "DECK PLAN"

func _player() -> Node3D:
	return get_tree().get_first_node_in_group("player") as Node3D if is_inside_tree() else null

func build() -> void:
	var row := hb(self, 10)
	var left := vb(row, 6)
	left.size_flags_stretch_ratio = 2.0
	var tb := hb(left)
	for d in st.ship.get("decks", []):
		var id := int(d["id"])
		var b := btn(tb, "DECK %d  %s" % [id, String(d["name"]).replace(" Deck", "")], _set_deck.bind(id), true)
		_deck_btns.append([id, b])
	_cv = canvas(left, 300)
	_cv.draw_fn = _draw_plan
	_cv.click_fn = func(e: InputEventMouseButton, p: Vector2) -> void:
		if e.button_index == MOUSE_BUTTON_LEFT:
			var rid := _room_at(p)
			if rid != "":
				selected = rid
				_update_info()
	var right := vb(row, 6)
	right.custom_minimum_size.x = 340
	right.size_flags_horizontal = Control.SIZE_FILL
	_search = line_edit(right, "find a room...", func(_t: String) -> void: refresh())
	_search.text_changed.connect(func(_t: String) -> void: refresh())
	_tree = table(right, ["Room", "Deck", "Dept"], [200, 40, 90])
	_tree.item_selected.connect(func() -> void:
		var m: Variant = table_selected(_tree)
		if m != null:
			selected = String(m)
			for r in st.ship.get("rooms", []):
				if r["id"] == selected:
					deck = int(r["deck"])
			_update_info())
	_info = wrap_lbl(right, "", 14, T.TEXT)
	var p0 := _player()
	if p0 != null:
		for d in st.ship.get("decks", []):
			if absf(p0.global_position.y - float(d["y"])) < 2.5:
				deck = int(d["id"])
	elif st.player_room != "":
		for r in st.ship.get("rooms", []):
			if r["id"] == st.player_room:
				deck = int(r["deck"])

func _set_deck(on: bool, id: int) -> void:
	deck = id
	_cv.queue_redraw()

func tick(_dt: float) -> void:
	_cv.queue_redraw()

func _update_info() -> void:
	for r in st.ship.get("rooms", []):
		if r["id"] == selected:
			_info.text = "%s [%s]\nDeck %s - %s department\n%.0f m2, ceiling %.1f m\n%s" % [r["name"], r["id"], r["deck"], r.get("dept", ""), r.get("area", 0.0), r.get("height", 3.4), r.get("brief", {}).get("purpose", "") if r.get("brief") is Dictionary else ""]

func refresh() -> void:
	for p in _deck_btns:
		(p[1] as Button).set_pressed_no_signal(p[0] == deck)
	var rows: Array = []
	var metas: Array = []
	var q := _search.text.to_lower()
	for r in st.ship.get("rooms", []):
		if q != "" and not (String(r["name"]).to_lower().contains(q) or String(r["id"]).to_lower().contains(q)):
			continue
		if q == "" and r.get("dept", "") == "transit":
			continue
		rows.append([r["name"], str(r["deck"]), String(r.get("dept", "")).capitalize()])
		metas.append(r["id"])
	table_fill(_tree, rows, metas)

func _bounds() -> Rect2:
	var mn := Vector2(1e9, 1e9)
	var mx := Vector2(-1e9, -1e9)
	for k in st.ship.get("hull", {}).keys():
		for p in st.ship["hull"][k]:
			mn = mn.min(Vector2(p[0], p[1]))
			mx = mx.max(Vector2(p[0], p[1]))
	if mn.x > mx.x:
		return Rect2(-15, -35, 30, 50)
	return Rect2(mn, mx - mn)

func _w2s(p: Vector2) -> Vector2:
	return (_xf["o"] as Vector2) + p * float(_xf["s"])

func _s2w(p: Vector2) -> Vector2:
	return (p - (_xf["o"] as Vector2)) / float(_xf["s"])

func _room_at(p: Vector2) -> String:
	var w := _s2w(p)
	for r in st.ship.get("rooms", []):
		if int(r["deck"]) != deck:
			continue
		var pv := PackedVector2Array()
		for q in r["poly"]:
			pv.append(Vector2(q[0], q[1]))
		if Geometry2D.is_point_in_polygon(w, pv):
			return r["id"]
	return ""

func _draw_plan(c: UIW.Canvas) -> void:
	var b := _bounds()
	var s := minf((c.size.x - 30.0) / b.size.x, (c.size.y - 30.0) / b.size.y)
	_xf["s"] = s
	# world x to screen x, world z (forward = -z) to screen y: bow at the top
	_xf["o"] = (c.size - b.size * s) * 0.5 - b.position * s
	var font := c.get_theme_default_font()
	var hull: Array = st.ship.get("hull", {}).get(str(deck), [])
	if not hull.is_empty():
		var pv := PackedVector2Array()
		for p in hull:
			pv.append(_w2s(Vector2(p[0], p[1])))
		pv.append(pv[0])
		c.draw_polyline(pv, T.ACCENT_DIM, 2.5, true)
	var q := _search.text.to_lower() if _search != null else ""
	for r in st.ship.get("rooms", []):
		if int(r["deck"]) != deck:
			continue
		var pts := PackedVector2Array()
		for p in r["poly"]:
			pts.append(_w2s(Vector2(p[0], p[1])))
		var col: Color = DEPT.get(r.get("dept", ""), Color(0.5, 0.5, 0.5))
		var hit: bool = q != "" and (String(r["name"]).to_lower().contains(q) or String(r["id"]).to_lower().contains(q))
		var a := 0.55 if (r["id"] == selected or hit) else 0.22
		c.draw_colored_polygon(pts, Color(col.r, col.g, col.b, a))
		pts.append(pts[0])
		c.draw_polyline(pts, Color(col.r, col.g, col.b, 0.9 if r["id"] == selected else 0.5), 2.0 if r["id"] == selected else 1.0, true)
		if r.get("dept", "") != "transit" and s > 8.0:
			var rc: Array = r["rect"]
			var mid := _w2s(Vector2((rc[0] + rc[2]) * 0.5, (rc[1] + rc[3]) * 0.5))
			c.draw_string(font, mid - Vector2(40, -4), r["name"], HORIZONTAL_ALIGNMENT_CENTER, 80, 10, Color(0.9, 0.97, 1, 0.9))
	# doors
	var ys := 0.0
	for d in st.ship.get("decks", []):
		if int(d["id"]) == deck:
			ys = float(d["y"])
	for i in st.doors.size():
		var dn := st.doors[i] as Node3D
		if dn == null or absf(dn.position.y - ys) > 2.0:
			continue
		var pp := _w2s(Vector2(dn.position.x, dn.position.z))
		c.draw_circle(pp, 3.0, T.BAD if st.door_locked(i) else T.ACCENT)
	var pl := _player()
	if pl != null:
		var pos := pl.global_position
		var inside := absf(pos.y - ys) < 2.5
		if inside:
			var pp2 := _w2s(Vector2(pos.x, pos.z))
			var yaw := pl.rotation.y
			var dir := Vector2(-sin(yaw), -cos(yaw))
			var nrm := Vector2(-dir.y, dir.x)
			c.draw_colored_polygon(PackedVector2Array([pp2 + dir * 9, pp2 - dir * 5 + nrm * 5, pp2 - dir * 5 - nrm * 5]), Color(0.4, 1.0, 0.6))
			c.draw_string(font, pp2 + Vector2(10, -6), "YOU ARE HERE", HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Color(0.4, 1.0, 0.6))
	c.draw_string(font, Vector2(10, c.size.y - 8), "BOW ^   red dots: locked doors", HORIZONTAL_ALIGNMENT_LEFT, -1, 11, T.TEXT_DIM)
