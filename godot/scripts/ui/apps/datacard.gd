extends AppBase
## Machine data card for props without a screen: catalogue facts plus whatever specs.json knows.

var _tree: Tree
var _spin := 0.0
var _canvas: UIW.Canvas
var _status: Label

func title_text() -> String:
	return "MACHINE DATA CARD"

func build() -> void:
	var id: String = host.get("model", "")
	var e: Dictionary = st.catalog.get(id, {})
	var row := hb(self, 12)
	var left := panel(row, "Specification")
	_tree = table(left, ["Property", "Value"], [140, 260])
	var rows: Array = []
	rows.append(["Model", id])
	rows.append(["Name", String(host.get("label", e.get("label", id)))])
	rows.append(["Category", String(e.get("category", host.get("category", "?"))).capitalize()])
	rows.append(["Installed in", String(host.get("room_name", host.get("room", "?")))])
	if e.has("size"):
		rows.append(["Dimensions", "%.2f x %.2f x %.2f m" % [e["size"][0], e["size"][1], e["size"][2]]])
		rows.append(["Mounting", String(e.get("mount", "floor"))])
		rows.append(["Mesh detail", "%d triangles" % int(e.get("tris", 0))])
		rows.append(["Tags", ", ".join(e.get("tags", []))])
	var sp := Lore.spec(id)
	if sp.is_empty():
		rows.append(["Manufacturer record", ["none on file (specs.json)", T.WARN]])
	else:
		for k in sp.keys():
			var v: Variant = sp[k]
			rows.append([String(k).replace("_", " ").capitalize(), ", ".join(v) if v is Array else str(v)])
	table_fill(_tree, rows)
	var right := vb(row, 8)
	var pv := panel(right, "Unit schematic")
	_canvas = canvas(pv, 220)
	_canvas.draw_fn = _draw_box
	var act := panel(right, "Service", false)
	_status = wrap_lbl(act, "Unit responds on the ship network. Press PING to run a self-test.", 14, T.TEXT_DIM)
	var ar := hb(act)
	btn(ar, "PING UNIT", _ping)
	btn(ar, "REPORT FAULT", func() -> void:
		st.say("Fault reported on %s (%s)" % [host.get("label", id), host.get("room_name", "")], "warn")
		_status.text = "Fault ticket opened with Engineering.")

func _ping() -> void:
	var id: String = host.get("model", "")
	var ok := rnd(id, 7) > 0.08
	_status.text = ("%s: self-test PASSED, latency %d ms." % [host.get("label", id), 2 + int(rnd(id, 3) * 20)]) if ok else "%s: self-test reports a degraded sensor; service advised." % host.get("label", id)
	_status.add_theme_color_override("font_color", T.OK if ok else T.WARN)
	st.say("Ping %s: %s" % [host.get("label", id), "ok" if ok else "degraded"], "info")

func tick(dt: float) -> void:
	_spin += dt * 0.7
	_canvas.queue_redraw()

func _draw_box(c: UIW.Canvas) -> void:
	var e: Dictionary = st.catalog.get(host.get("model", ""), {})
	var sz := Vector3(0.6, 0.8, 0.6)
	if e.has("size"):
		sz = Vector3(e["size"][0], e["size"][1], e["size"][2])
	var m := maxf(sz.x, maxf(sz.y, sz.z))
	var s := minf(c.size.x, c.size.y) * 0.28 / m
	var ctr := c.size * 0.5
	var pts: Array = []
	for i in 8:
		var p := Vector3(sz.x * (1 if i & 1 else -1), sz.y * (1 if i & 2 else -1), sz.z * (1 if i & 4 else -1)) * 0.5
		var cs := cos(_spin)
		var sn := sin(_spin)
		var q := Vector3(p.x * cs - p.z * sn, p.y, p.x * sn + p.z * cs)
		var cp := cos(0.45)
		var sp2 := sin(0.45)
		var r := Vector3(q.x, q.y * cp - q.z * sp2, q.y * sp2 + q.z * cp)
		pts.append(ctr + Vector2(r.x, -r.y) * s * 1.6)
	for a in 8:
		for b in [1, 2, 4]:
			if not (a & b):
				c.draw_line(pts[a], pts[a | b], T.ACCENT, 1.6, true)
	c.draw_string(c.get_theme_default_font(), Vector2(10, c.size.y - 10), "%.2f x %.2f x %.2f m" % [sz.x, sz.y, sz.z], HORIZONTAL_ALIGNMENT_LEFT, -1, 13, T.TEXT_DIM)
