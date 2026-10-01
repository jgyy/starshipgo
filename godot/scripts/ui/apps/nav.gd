extends AppBase
## Helm and navigation: position, heading, course, warp factor and the mission waypoints.

var _pos_l: Label
var _head_l: Label
var _dest_l: Label
var _eta_l: Label
var _route_l: Label
var _warp: HSlider
var _go: Button
var _clear: Button
var _prog: UIW.Meter
var _chart: UIW.Canvas
var _compass: UIW.Canvas
var _wp: Tree
var _set_wp: Button
var _scale := 1.0

func title_text() -> String:
	return "NAVIGATION"

func build() -> void:
	var row := hb(self, 10)
	var left := vb(row, 8)
	left.custom_minimum_size.x = 330
	left.size_flags_horizontal = Control.SIZE_FILL
	var p1 := panel(left, "Position and heading")
	_pos_l = lbl(p1, "", 20, T.ACCENT)
	_head_l = lbl(p1, "", 14, T.TEXT_DIM)
	_compass = canvas(p1, 140)
	_compass.draw_fn = _draw_compass
	var p2 := panel(left, "Helm", false)
	_dest_l = lbl(p2, "", 18, T.WARN)
	_eta_l = wrap_lbl(p2, "", 14, T.TEXT)
	_route_l = wrap_lbl(p2, "", 13, T.TEXT_DIM)
	_warp = slider(p2, "Warp factor", 0.0, float(Lore.ship_info().get("top_warp", 9.2)), st.warp, _on_warp, 0.1, "%.1f")
	var br := hb(p2)
	_go = btn(br, "ENGAGE WARP", func() -> void: st.jump())
	_clear = btn(br, "CLEAR COURSE", func() -> void: st.set_destination(""))
	_prog = meter(p2, "TRANSIT")
	var mid := panel(row, "Navigational chart (top-down, click a system to plot a course)")
	mid.size_flags_stretch_ratio = 1.6
	_chart = canvas(mid, 260)
	_chart.draw_fn = _draw_chart
	_chart.click_fn = func(e: InputEventMouseButton, p: Vector2) -> void:
		if e.button_index == MOUSE_BUTTON_LEFT:
			var id := _nearest(p)
			if id != "":
				st.set_destination(id)
	_chart.wheel_fn = func(dir: int) -> void:
		_scale = clampf(_scale * (1.1 if dir > 0 else 0.9), 0.5, 3.0)
	var right := panel(row, "Mission waypoints")
	right.custom_minimum_size.x = 300
	_wp = table(right, ["System", "Objective", "ETA"], [80, 150, 50])
	var rows: Array = []
	var metas: Array = []
	for w in Lore.data().get("waypoints", []):
		rows.append([Lore.system_name(w["system"]), w["objective"], "%s d" % str(w.get("eta_days", "?"))])
		metas.append(w["system"])
	table_fill(_wp, rows, metas)
	_set_wp = btn(right, "SET DESTINATION", func() -> void:
		var m: Variant = table_selected(_wp)
		if m != null:
			st.set_destination(String(m)))

func _on_warp(v: float) -> void:
	st.warp = v
	st.changed.emit()

func tick(_dt: float) -> void:
	_chart.queue_redraw()
	_compass.queue_redraw()

func refresh() -> void:
	var cur := Lore.system(st.current_system)
	_pos_l.text = "%s%s" % [String(cur.get("name", "?")).to_upper(), "  (IN TRANSIT)" if st.in_transit else ""]
	var h := st.heading
	_head_l.text = "Heading %03.0f mark %+.0f   |   Faction: %s" % [fposmod(rad_to_deg(atan2(h.x, h.z)), 360.0), rad_to_deg(asin(clampf(h.y, -1, 1))), Lore.faction(cur.get("faction", ""))["name"]]
	if st.destination == "":
		_dest_l.text = "NO COURSE SET"
		_eta_l.text = "Pick a system on the chart, the waypoint list, or use the star map."
		_route_l.text = ""
	else:
		_dest_l.text = "DEST: %s" % Lore.system_name(st.destination).to_upper()
		_eta_l.text = "%.1f ly   ETA %s at warp %.1f (%.2f ly/day)" % [st.route_ly(), st.eta_text(), st.warp, st.warp_ly_per_day()]
		var names: Array = []
		for x in st.route:
			names.append(Lore.system_name(x))
		_route_l.text = "Lane: " + (" > ".join(names) if names.size() >= 2 else "direct (uncharted)")
	if absf(_warp.value - st.warp) > 0.01:
		set_slider(_warp, st.warp)
	_go.disabled = st.destination == "" or st.in_transit or st.destination == st.current_system
	_clear.disabled = st.destination == "" or st.in_transit
	_prog.visible = st.in_transit
	if st.in_transit:
		_prog.set_value(st.transit_progress(), "%.0f%%" % (st.transit_progress() * 100.0))

func _draw_compass(c: UIW.Canvas) -> void:
	var ctr := c.size * 0.5
	var r := minf(c.size.x, c.size.y) * 0.42
	c.draw_arc(ctr, r, 0, TAU, 48, T.ACCENT_DIM, 2.0, true)
	var f := c.get_theme_default_font()
	for i in 12:
		var a := TAU * i / 12.0
		c.draw_line(ctr + Vector2(sin(a), -cos(a)) * (r - 6), ctr + Vector2(sin(a), -cos(a)) * r, T.ACCENT_DIM, 1.5)
	for k in [["N", 0.0], ["E", 90.0], ["S", 180.0], ["W", 270.0]]:
		var a2 := deg_to_rad(k[1])
		c.draw_string(f, ctr + Vector2(sin(a2), -cos(a2)) * (r + 12) - Vector2(4, -4), k[0], HORIZONTAL_ALIGNMENT_LEFT, -1, 12, T.TEXT_DIM)
	var h := st.heading
	var ang := atan2(h.x, h.z)
	var tip := ctr + Vector2(sin(ang), -cos(ang)) * (r - 8)
	c.draw_line(ctr, tip, Color(0.4, 1.0, 0.6), 3.0, true)
	c.draw_circle(tip, 5.0, Color(0.4, 1.0, 0.6))
	if st.destination != "" and st.destination != st.current_system:
		var d := Lore.pos_of(st.destination) - Lore.pos_of(st.current_system)
		var a3 := atan2(d.x, d.z)
		c.draw_line(ctr, ctr + Vector2(sin(a3), -cos(a3)) * (r - 4), T.WARN, 2.0, true)

func _to_screen(c: Control, id: String) -> Vector2:
	var p := Lore.pos_of(id) - Lore.pos_of(st.current_system)
	return c.size * 0.5 + Vector2(p.x, p.z) * (minf(c.size.x, c.size.y) / 60.0) * _scale

func _nearest(p: Vector2) -> String:
	var best := ""
	var bd := 16.0
	for s in Lore.systems():
		var d := (_to_screen(_chart, s["id"]) - p).length()
		if d < bd:
			bd = d
			best = s["id"]
	return best

func _draw_chart(c: UIW.Canvas) -> void:
	var f := c.get_theme_default_font()
	var ctr := c.size * 0.5
	for rr in [10.0, 20.0, 30.0]:
		c.draw_arc(ctr, rr * (minf(c.size.x, c.size.y) / 60.0) * _scale, 0, TAU, 48, Color(0.14, 0.35, 0.42, 0.5), 1.0, true)
	for r in Lore.routes():
		var col: Color = Lore.hazard_color(r.get("hazard", ""))
		col.a = 0.35
		c.draw_line(_to_screen(c, r["a"]), _to_screen(c, r["b"]), col, 1.0, true)
	for i in range(st.route.size() - 1):
		c.draw_line(_to_screen(c, st.route[i]), _to_screen(c, st.route[i + 1]), Color.WHITE, 3.0, true)
	for s in Lore.systems():
		var p := _to_screen(c, s["id"])
		var col2 := Lore.faction_color(s.get("faction", ""))
		c.draw_circle(p, 5.0, col2)
		if s["id"] == st.destination:
			c.draw_arc(p, 10.0, 0, TAU, 20, T.WARN, 2.0, true)
		c.draw_string(f, p + Vector2(8, 4), s["name"], HORIZONTAL_ALIGNMENT_LEFT, -1, 12, T.TEXT)
	var t := Time.get_ticks_msec() / 1000.0
	c.draw_arc(ctr, 9.0 + 3.0 * sin(t * 3.0), 0, TAU, 20, Color(0.4, 1.0, 0.6), 2.0, true)
	if st.in_transit:
		var a := _to_screen(c, st.transit_from)
		var b := _to_screen(c, st.transit_to)
		c.draw_circle(a.lerp(b, st.transit_progress()), 6.0, Color(0.5, 1.0, 0.7))
