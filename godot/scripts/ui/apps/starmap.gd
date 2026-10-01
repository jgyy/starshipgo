extends AppBase
## Star cartography: an interactive 3D chart of the Reach.  Drag to rotate, wheel to zoom, click a system.
## Systems come from lore.json: colour = faction, size = luminosity, ring = visited.  PLOT COURSE sets ShipState's
## destination (shown on the HUD and the nav app); JUMP runs a timed transit and moves the ship to the system.

var yaw := -0.55
var pitch := 0.5
var zoom := 1.0
var selected := ""
var hover := ""
var show_all := false
var labels := true
var faction_filter := ""
var search := ""

var _cv: UIW.Canvas
var _proj: Dictionary = {}
var _centre := Vector3.ZERO
var _radius := 20.0
var _press := Vector2.ZERO
var _dragging := false
var _mouse := Vector2.ZERO
var _faction_opt: OptionButton
var _search_box: LineEdit
var _name_l: Label
var _fac_l: Label
var _info_l: Label
var _sum_l: Label
var _lore_l: Label
var _planets: Tree
var _route_l: Label
var _plot_b: Button
var _jump_b: Button
var _prog: UIW.Meter
var _wp: Tree
var _tabs: TabContainer

func title_text() -> String:
	return "STAR CARTOGRAPHY"

func build() -> void:
	var systems := Lore.systems()
	if not systems.is_empty():
		var sum := Vector3.ZERO
		for s in systems:
			sum += Lore.pos_of(s["id"])
		_centre = sum / systems.size()
		for s in systems:
			_radius = maxf(_radius, Lore.pos_of(s["id"]).distance_to(_centre))
	var row := hb(self, 10)
	var left := vb(row, 6)
	left.size_flags_stretch_ratio = 2.2
	var tb := hb(left, 6)
	_search_box = line_edit(tb, "search systems...", func(t: String) -> void:
		var q := t.to_lower()
		for s in Lore.systems():
			if String(s["name"]).to_lower().contains(q):
				select(s["id"])
				break)
	_search_box.text_changed.connect(func(t: String) -> void:
		search = t.strip_edges().to_lower()
		_cv.queue_redraw())
	_faction_opt = OptionButton.new()
	_faction_opt.focus_mode = Control.FOCUS_NONE
	_faction_opt.add_item("ALL FACTIONS")
	for f in Lore.factions():
		_faction_opt.add_item(String(f["name"]).to_upper())
	_faction_opt.item_selected.connect(func(i: int) -> void:
		faction_filter = "" if i == 0 else String(Lore.factions()[i - 1]["id"])
		_cv.queue_redraw())
	tb.add_child(_faction_opt)
	var routes_b := btn(tb, "ALL ROUTES", _set_routes, true)
	routes_b.name = "RoutesToggle"
	var lab_b := btn(tb, "LABELS", _set_labels, true)
	lab_b.name = "LabelsToggle"
	lab_b.set_pressed_no_signal(true)
	btn(tb, "RESET VIEW", func() -> void:
		yaw = -0.55
		pitch = 0.5
		zoom = 1.0)
	_cv = canvas(left, 300)
	_cv.draw_fn = _draw_map
	_cv.click_fn = _on_click
	_cv.motion_fn = _on_motion
	_cv.wheel_fn = func(dir: int) -> void:
		zoom = clampf(zoom * (1.1 if dir > 0 else 0.9), 0.4, 3.5)
		_cv.queue_redraw()
	_cv.mouse_exited.connect(func() -> void:
		hover = ""
		_dragging = false)
	var right := vb(row, 6)
	right.custom_minimum_size.x = 400
	right.size_flags_horizontal = Control.SIZE_FILL
	_tabs = tab_container(right, ["SYSTEM", "WAYPOINTS", "LEGEND"])
	var sp := page(_tabs, 0)
	_name_l = lbl(sp, "", 26, T.ACCENT)
	_fac_l = lbl(sp, "", 15, T.TEXT)
	_info_l = wrap_lbl(sp, "", 14, T.TEXT_DIM)
	_sum_l = wrap_lbl(sp, "", 15, T.TEXT)
	_planets = table(sp, ["Planet", "Type", "g", "Atmosphere", "Hab"], [100, 80, 40, 100, 40])
	_planets.custom_minimum_size.y = 100
	_lore_l = wrap_lbl(sp, "", 13, T.TEXT_DIM)
	_route_l = wrap_lbl(sp, "", 14, T.WARN)
	var br := hb(sp)
	_plot_b = btn(br, "PLOT COURSE", func() -> void: st.set_destination(selected))
	_jump_b = btn(br, "JUMP", _do_jump)
	_plot_b.name = "PlotButton"
	_jump_b.name = "JumpButton"
	_prog = meter(sp, "TRANSIT")
	var wp := page(_tabs, 1)
	_wp = table(wp, ["System", "Objective", "ETA", "Status"], [90, 190, 50, 70])
	var wrows: Array = []
	var wmeta: Array = []
	for w in Lore.data().get("waypoints", []):
		wrows.append([Lore.system_name(w["system"]), w["objective"], "%s d" % str(w.get("eta_days", "?")), w.get("status", "")])
		wmeta.append(w["system"])
	table_fill(_wp, wrows, wmeta)
	_wp.item_selected.connect(func() -> void:
		var m: Variant = table_selected(_wp)
		if m != null:
			select(String(m)))
	var lg := page(_tabs, 2)
	for f in Lore.factions():
		var r := hb(lg)
		var dot := ColorRect.new()
		dot.color = Lore.faction_color(f["id"])
		dot.custom_minimum_size = Vector2(14, 14)
		dot.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		r.add_child(dot)
		wrap_lbl(r, "%s - %s" % [f["name"], f.get("description", "")], 13, T.TEXT)
	for h in [0, 1, 2, 3, 4, 5]:
		var r2 := hb(lg)
		var d2 := ColorRect.new()
		d2.color = Lore.hazard_color(h)
		d2.custom_minimum_size = Vector2(30, 4)
		d2.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		r2.add_child(d2)
		lbl(r2, "lane hazard %d" % h, 13, T.TEXT_DIM)
	wrap_lbl(lg, "Disc size = luminosity.  Ring = visited.  Pulsing ring = your position.  Diamond = destination.", 13, T.TEXT_DIM)
	select(st.destination if st.destination != "" else st.current_system)

func _set_routes(on: bool) -> void:
	show_all = on
	_cv.queue_redraw()

func _set_labels(on: bool) -> void:
	labels = on
	_cv.queue_redraw()

func demo() -> void:
	select("kepler_x")
	st.set_destination("kepler_x")
	show_all = true
	(find_child("RoutesToggle", true, false) as Button).set_pressed_no_signal(true)

func tick(_dt: float) -> void:
	_cv.queue_redraw()

func refresh() -> void:
	if selected == "":
		return
	var s := Lore.system(selected)
	var is_here := selected == st.current_system
	var dist := Lore.distance(st.current_system, selected)
	var plot := Lore.plot(st.current_system, selected)
	var lane := Lore.route_length(plot) if plot.size() >= 2 else dist
	var info := "Class %s  |  %d K  |  %.2f L-sun  |  %s" % [s.get("star", {}).get("class", "?"), int(s.get("star", {}).get("temp_k", 0)), float(s.get("star", {}).get("lum_solar", 0)), String(s.get("kind", "")).capitalize()]
	if not is_here:
		info += "\nStraight line %.1f ly  |  by lanes %.1f ly in %d hop(s)  |  ETA %.1f d at warp %.1f" % [dist, lane, maxi(plot.size() - 1, 1), lane / maxf(0.05, st.warp_ly_per_day()), st.warp]
	_info_l.text = info
	var worst := "0"
	for i in range(plot.size() - 1):
		var h := str(int(Lore.route(plot[i], plot[i + 1]).get("hazard", 0)))
		if int(h) > int(worst):
			worst = h
	_route_l.text = "" if is_here else ("Lane: %s  (worst hazard level %s of 5)" % [" > ".join(plot.map(func(x: String) -> String: return Lore.system_name(x))), worst] if plot.size() >= 2 else "No charted lane - dead reckoning only.")
	if st.destination == selected:
		_route_l.text += "   COURSE PLOTTED"
	_plot_b.disabled = is_here or st.in_transit
	_jump_b.disabled = is_here or st.in_transit
	_prog.visible = st.in_transit
	if st.in_transit:
		_prog.set_value(st.transit_progress(), "%s -> %s  %.0f%%" % [Lore.system_name(st.transit_from), Lore.system_name(st.transit_to), st.transit_progress() * 100.0])

func select(id: String) -> void:
	if Lore.system(id).is_empty():
		return
	selected = id
	var s := Lore.system(id)
	_name_l.text = String(s["name"]).to_upper()
	var f := Lore.faction(s.get("faction", ""))
	_fac_l.text = "%s  (%s)%s" % [f["name"], f.get("stance", ""), "   VISITED" if st.visited.has(id) else "   unvisited"]
	_fac_l.add_theme_color_override("font_color", Lore.faction_color(s.get("faction", "")))
	_sum_l.text = s.get("summary", "")
	_lore_l.text = f.get("description", "")
	var rows: Array = []
	for p in s.get("planets", []):
		rows.append([p["name"], p.get("type", ""), "%.2f" % float(p.get("gravity_g", 0)), p.get("atmosphere", ""), ["YES", T.OK] if p.get("habitable", false) else ["no", T.TEXT_DIM]])
	if rows.is_empty():
		rows.append(["(no planets charted)", "", "", "", ""])
	table_fill(_planets, rows)
	refresh()
	_cv.queue_redraw()

func _do_jump() -> void:
	if st.destination != selected:
		st.set_destination(selected)
	st.jump()

# ------------------------------------------------------------------ projection and drawing
func _project(pos: Vector3, ctr: Vector2, sc: float) -> Dictionary:
	var p := pos - _centre
	var cy := cos(yaw)
	var sy := sin(yaw)
	var x1 := p.x * cy + p.z * sy
	var z1 := -p.x * sy + p.z * cy
	var cp := cos(pitch)
	var sp := sin(pitch)
	var y2 := p.y * cp - z1 * sp
	var z2 := p.y * sp + z1 * cp
	var persp := 1.0 / (1.0 + z2 * 0.012)
	return {"p": ctr + Vector2(x1, -y2) * sc * persp, "z": z2, "k": persp}

func _draw_map(c: UIW.Canvas) -> void:
	var font := c.get_theme_default_font()
	var ctr := c.size * 0.5
	var sc := minf(c.size.x, c.size.y) * 0.52 / _radius * zoom
	# star dust backdrop (stable)
	for i in 70:
		var h := hash("dust%d" % i)
		c.draw_circle(Vector2(float(h & 0xfff) / 4096.0 * c.size.x, float((h >> 12) & 0xfff) / 4096.0 * c.size.y), 0.8, Color(0.5, 0.7, 0.8, 0.25))
	# reference plane rings (y = 0 plane through the chart centre)
	for rr in [10.0, 20.0, 30.0]:
		var ring := PackedVector2Array()
		for i in 65:
			var a := TAU * i / 64.0
			var q := _project(_centre + Vector3(cos(a) * rr, 0.0, sin(a) * rr), ctr, sc)
			ring.append(q["p"])
		c.draw_polyline(ring, Color(0.14, 0.35, 0.42, 0.55), 1.0, true)
	_proj.clear()
	var order: Array = []
	for s in Lore.systems():
		var pr := _project(Lore.pos_of(s["id"]), ctr, sc)
		_proj[s["id"]] = pr
		order.append(s["id"])
	# stems down to the reference plane
	for id in order:
		var pos := Lore.pos_of(id)
		var base := _project(Vector3(pos.x, _centre.y, pos.z), ctr, sc)
		c.draw_line(_proj[id]["p"], base["p"], Color(0.2, 0.5, 0.58, 0.3), 1.0)
		c.draw_circle(base["p"], 2.0, Color(0.2, 0.5, 0.58, 0.5))
	# routes
	var plotted: Array = st.route
	for r in Lore.routes():
		if not _proj.has(r["a"]) or not _proj.has(r["b"]):
			continue
		var touches: bool = r["a"] == st.current_system or r["b"] == st.current_system or r["a"] == selected or r["b"] == selected
		var col: Color = Lore.hazard_color(r.get("hazard", 0))
		col.a = 0.85 if (show_all or touches) else 0.16
		c.draw_line(_proj[r["a"]]["p"], _proj[r["b"]]["p"], col, 1.6 if (show_all or touches) else 1.0, true)
		if show_all:
			var mid: Vector2 = ((_proj[r["a"]]["p"] as Vector2) + (_proj[r["b"]]["p"] as Vector2)) * 0.5
			c.draw_string(font, mid + Vector2(3, -3), "%.0f ly" % float(r.get("ly", 0)), HORIZONTAL_ALIGNMENT_LEFT, -1, 10, Color(col.r, col.g, col.b, 0.9))
	for i in range(plotted.size() - 1):
		if _proj.has(plotted[i]) and _proj.has(plotted[i + 1]):
			c.draw_line(_proj[plotted[i]]["p"], _proj[plotted[i + 1]]["p"], Color(1, 1, 1, 0.95), 3.0, true)
	# systems, far to near
	order.sort_custom(func(a: String, b: String) -> bool: return _proj[a]["z"] > _proj[b]["z"])
	var t := Time.get_ticks_msec() / 1000.0
	for id in order:
		var s := Lore.system(id)
		var pr: Dictionary = _proj[id]
		var p: Vector2 = pr["p"]
		var col := Lore.faction_color(s.get("faction", ""))
		var dim: bool = (faction_filter != "" and s.get("faction", "") != faction_filter) or (search != "" and not String(s["name"]).to_lower().contains(search))
		if dim:
			col.a = 0.2
		var lum := float(s.get("star", {}).get("lum_solar", 1.0))
		var rad: float = clampf(4.5 + 2.4 * log(1.0 + lum) / log(10.0), 4.0, 12.0) * pr["k"]
		c.draw_circle(p, rad + 3.0, Color(col.r, col.g, col.b, 0.12 if not dim else 0.04))
		c.draw_circle(p, rad, col)
		c.draw_circle(p, rad * 0.45, Color(1, 1, 1, 0.8 if not dim else 0.2))
		if st.visited.has(id):
			c.draw_arc(p, rad + 4.0, 0.0, TAU, 28, Color(1, 1, 1, 0.55 if not dim else 0.15), 1.5, true)
		if id == st.current_system and not st.in_transit:
			var pulse := 0.5 + 0.5 * sin(t * 3.0)
			c.draw_arc(p, rad + 9.0 + pulse * 4.0, 0.0, TAU, 32, Color(0.4, 1.0, 0.6, 0.9 - pulse * 0.5), 2.0, true)
		if id == st.destination:
			var d: float = rad + 9.0
			c.draw_polyline(PackedVector2Array([p + Vector2(0, -d), p + Vector2(d, 0), p + Vector2(0, d), p + Vector2(-d, 0), p + Vector2(0, -d)]), T.WARN, 2.0, true)
		if id == selected:
			var b: float = rad + 12.0
			for sx in [-1, 1]:
				for sy in [-1, 1]:
					var corner := p + Vector2(b * sx, b * sy)
					c.draw_line(corner, corner - Vector2(6 * sx, 0), T.ACCENT, 2.0)
					c.draw_line(corner, corner - Vector2(0, 6 * sy), T.ACCENT, 2.0)
		if search != "" and not dim:
			c.draw_arc(p, rad + 8.0, 0.0, TAU, 28, T.ACCENT, 2.0, true)
		var show_label: bool = labels or id == hover or id == selected or id == st.current_system or id == st.destination
		if show_label:
			var txt: String = s["name"]
			if id == st.current_system:
				txt += "  [YOU ARE HERE]"
			c.draw_string(font, p + Vector2(rad + 7.0, 4.0), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color(0.85, 0.95, 1.0, 0.95 if not dim else 0.3))
	# ship in transit
	if st.in_transit and _proj.has(st.transit_from) and _proj.has(st.transit_to):
		var a: Vector2 = _proj[st.transit_from]["p"]
		var b2: Vector2 = _proj[st.transit_to]["p"]
		var f := st.transit_progress()
		var pos2 := a.lerp(b2, f)
		c.draw_line(a, pos2, Color(0.4, 1.0, 0.6, 0.9), 3.0, true)
		var dir := (b2 - a).normalized()
		var nrm := Vector2(-dir.y, dir.x)
		c.draw_colored_polygon(PackedVector2Array([pos2 + dir * 10, pos2 - dir * 6 + nrm * 6, pos2 - dir * 6 - nrm * 6]), Color(0.5, 1.0, 0.7))
	# tooltip
	if hover != "" and _proj.has(hover):
		var s2 := Lore.system(hover)
		var lines: Array = [String(s2["name"]).to_upper(), "%s  |  %s" % [Lore.faction(s2.get("faction", ""))["name"], s2.get("star", {}).get("class", "?")],
			"%.1f ly from the ship" % Lore.distance(st.current_system, hover)]
		var tw := 180.0
		var tp := Vector2(minf(_mouse.x + 16.0, c.size.x - tw - 6.0), minf(_mouse.y + 12.0, c.size.y - 58.0))
		c.draw_rect(Rect2(tp, Vector2(tw, 52)), Color(0.02, 0.06, 0.09, 0.95), true)
		c.draw_rect(Rect2(tp, Vector2(tw, 52)), T.ACCENT_DIM, false, 1.0)
		for i in lines.size():
			c.draw_string(font, tp + Vector2(8, 16 + i * 15), lines[i], HORIZONTAL_ALIGNMENT_LEFT, tw - 12, 12, T.ACCENT if i == 0 else T.TEXT)
	c.draw_string(font, Vector2(10, c.size.y - 10), "drag: rotate   wheel: zoom   click: select      yaw %d  pitch %d  zoom %.1fx" % [int(rad_to_deg(yaw)) % 360, int(rad_to_deg(pitch)), zoom], HORIZONTAL_ALIGNMENT_LEFT, -1, 11, T.TEXT_DIM)

func _nearest(p: Vector2) -> String:
	var best := ""
	var bd := 18.0
	for id in _proj.keys():
		var d: float = ((_proj[id]["p"] as Vector2) - p).length()
		if d < bd:
			bd = d
			best = id
	return best

func _on_click(e: InputEventMouseButton, pos: Vector2) -> void:
	if e.button_index == MOUSE_BUTTON_LEFT:
		var id := _nearest(pos)
		if id != "":
			select(id)

func _on_motion(e: InputEventMouseMotion) -> void:
	_mouse = e.position
	if e.button_mask & MOUSE_BUTTON_MASK_LEFT:
		yaw += e.relative.x * 0.008
		pitch = clampf(pitch + e.relative.y * 0.006, -1.45, 1.45)
	else:
		hover = _nearest(e.position)
	_cv.queue_redraw()
