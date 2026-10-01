extends AppBase
## Holo projector: a rotating wireframe of the hull built from the deck outlines in ship.json.  Drag to rotate,
## wheel to zoom; toggle decks and room outlines; the green dot is you.

var yaw := 0.6
var pitch := 0.45
var zoom := 1.0
var spin := true
var show_rooms := false
var _decks_on: Dictionary = {}
var _cv: UIW.Canvas
var _centre := Vector3.ZERO
var _radius := 20.0

func title_text() -> String:
	return "HOLO PROJECTOR"

func build() -> void:
	var row := hb(self, 10)
	_cv = canvas(row, 300)
	_cv.size_flags_stretch_ratio = 3.0
	_cv.draw_fn = _draw_holo
	_cv.motion_fn = func(e: InputEventMouseMotion) -> void:
		if e.button_mask & MOUSE_BUTTON_MASK_LEFT:
			yaw += e.relative.x * 0.01
			pitch = clampf(pitch + e.relative.y * 0.01, -1.4, 1.4)
	_cv.wheel_fn = func(dir: int) -> void:
		zoom = clampf(zoom * (1.1 if dir > 0 else 0.9), 0.4, 3.0)
	var right := panel(row, "Projection")
	right.custom_minimum_size.x = 260
	check(right, "Auto-rotate", true, func(on: bool) -> void: spin = on)
	check(right, "Room outlines", false, func(on: bool) -> void: show_rooms = on)
	for d in st.ship.get("decks", []):
		_decks_on[int(d["id"])] = true
		check(right, "Deck %d - %s" % [int(d["id"]), d["name"]], true, _toggle_deck.bind(int(d["id"])))
	wrap_lbl(right, "Hull: %s, %s\nDrag to rotate, wheel to zoom." % [Lore.ship_info().get("name", ""), Lore.ship_info().get("class", "")], 13, T.TEXT_DIM)
	var mn := Vector3(1e9, 1e9, 1e9)
	var mx := Vector3(-1e9, -1e9, -1e9)
	for k in st.ship.get("hull", {}).keys():
		var y := _deck_y(int(k))
		for p in st.ship["hull"][k]:
			mn = mn.min(Vector3(p[0], y, p[1]))
			mx = mx.max(Vector3(p[0], y + 3.4, p[1]))
	if mn.x < mx.x:
		_centre = (mn + mx) * 0.5
		_radius = maxf((mx - mn).length() * 0.5, 5.0)

func _toggle_deck(on: bool, id: int) -> void:
	_decks_on[id] = on

func _deck_y(id: int) -> float:
	for d in st.ship.get("decks", []):
		if int(d["id"]) == id:
			return float(d["y"])
	return 0.0

func tick(dt: float) -> void:
	if spin:
		yaw += dt * 0.4
	_cv.queue_redraw()

func _proj(p: Vector3, ctr: Vector2, sc: float) -> Vector2:
	var q := p - _centre
	var x1 := q.x * cos(yaw) + q.z * sin(yaw)
	var z1 := -q.x * sin(yaw) + q.z * cos(yaw)
	var y2 := q.y * cos(pitch) - z1 * sin(pitch)
	var z2 := q.y * sin(pitch) + z1 * cos(pitch)
	var k := 1.0 / (1.0 + z2 * 0.008)
	return ctr + Vector2(x1, -y2) * sc * k

func _draw_holo(c: UIW.Canvas) -> void:
	var ctr := c.size * 0.5
	var sc := minf(c.size.x, c.size.y) * 0.45 / _radius * zoom
	var glow := Color(0.3, 0.85, 1.0)
	for id in _decks_on.keys():
		if not _decks_on[id]:
			continue
		var hull: Array = st.ship.get("hull", {}).get(str(id), [])
		if hull.is_empty():
			continue
		var y0 := _deck_y(id)
		for yy in [y0, y0 + 3.4]:
			var pts := PackedVector2Array()
			for p in hull:
				pts.append(_proj(Vector3(p[0], yy, p[1]), ctr, sc))
			pts.append(pts[0])
			c.draw_polyline(pts, Color(glow.r, glow.g, glow.b, 0.85 if yy == y0 else 0.4), 1.6, true)
		for i in range(0, hull.size(), 2):
			c.draw_line(_proj(Vector3(hull[i][0], y0, hull[i][1]), ctr, sc), _proj(Vector3(hull[i][0], y0 + 3.4, hull[i][1]), ctr, sc), Color(glow.r, glow.g, glow.b, 0.25), 1.0)
		if show_rooms:
			for r in st.ship.get("rooms", []):
				if int(r["deck"]) != id:
					continue
				var rp := PackedVector2Array()
				for p in r["poly"]:
					rp.append(_proj(Vector3(p[0], y0 + 0.05, p[1]), ctr, sc))
				rp.append(rp[0])
				c.draw_polyline(rp, Color(1.0, 0.75, 0.3, 0.45), 1.0, true)
	var pl := get_tree().get_first_node_in_group("player") as Node3D if is_inside_tree() else null
	if pl != null:
		var pp := _proj(pl.global_position + Vector3(0, 1.0, 0), ctr, sc)
		c.draw_circle(pp, 5.0, Color(0.4, 1.0, 0.6))
		c.draw_arc(pp, 9.0 + 2.0 * sin(Time.get_ticks_msec() / 200.0), 0, TAU, 20, Color(0.4, 1.0, 0.6, 0.7), 2.0, true)
	var f := c.get_theme_default_font()
	c.draw_string(f, Vector2(10, 18), String(Lore.ship_info().get("name", "")).to_upper(), HORIZONTAL_ALIGNMENT_LEFT, -1, 15, T.ACCENT)
	c.draw_string(f, Vector2(10, 36), String(Lore.ship_info().get("registry", "")), HORIZONTAL_ALIGNMENT_LEFT, -1, 12, T.TEXT_DIM)
