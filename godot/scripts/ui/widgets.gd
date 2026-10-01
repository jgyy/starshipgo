class_name UIW
extends RefCounted
## Small custom-drawn widgets shared by the apps (graphs, meters, dials and a free canvas).

## A control that draws through a callback: `draw_fn.call(self)`.  Apps keep their own state and call queue_redraw().
class Canvas extends Control:
	var draw_fn: Callable
	var click_fn: Callable            # (event: InputEventMouseButton, local pos) -> void
	var motion_fn: Callable           # (InputEventMouseMotion) -> void
	var wheel_fn: Callable            # (dir: int) -> void

	func _init() -> void:
		clip_contents = true
		mouse_filter = Control.MOUSE_FILTER_PASS

	func _draw() -> void:
		draw_rect(Rect2(Vector2.ZERO, size), Color(0.015, 0.03, 0.045), true)
		draw_rect(Rect2(Vector2.ZERO, size), UITheme.RULE, false, 1.0)
		if draw_fn.is_valid():
			draw_fn.call(self)

	func _gui_input(e: InputEvent) -> void:
		if e is InputEventMouseButton and e.pressed:
			if e.button_index == MOUSE_BUTTON_WHEEL_UP and wheel_fn.is_valid():
				wheel_fn.call(1)
			elif e.button_index == MOUSE_BUTTON_WHEEL_DOWN and wheel_fn.is_valid():
				wheel_fn.call(-1)
			elif click_fn.is_valid():
				click_fn.call(e, e.position)
		elif e is InputEventMouseMotion and motion_fn.is_valid():
			motion_fn.call(e)

## Multi-series line graph with a grid.  series = [{data: PackedFloat32Array, color: Color, name: String}]
class Graph extends Control:
	var series: Array = []
	var ymin := NAN
	var ymax := NAN
	var title := ""
	var unit := ""
	var guide: float = NAN              # horizontal threshold line
	var guide_color := UITheme.WARN

	func _init() -> void:
		custom_minimum_size = Vector2(160, 90)
		clip_contents = true

	func set_series(s: Array) -> void:
		series = s
		queue_redraw()

	func _draw() -> void:
		var r := Rect2(Vector2.ZERO, size)
		draw_rect(r, Color(0.015, 0.03, 0.045), true)
		draw_rect(r, UITheme.RULE, false, 1.0)
		var lo := ymin
		var hi := ymax
		if is_nan(lo) or is_nan(hi):
			var mn := 1e18
			var mx := -1e18
			for s in series:
				for v in (s["data"] as PackedFloat32Array):
					mn = minf(mn, v)
					mx = maxf(mx, v)
			if mn > mx:
				mn = 0.0
				mx = 1.0
			var pad := maxf((mx - mn) * 0.15, 0.001 + absf(mx) * 0.01)
			lo = mn - pad if is_nan(ymin) else ymin
			hi = mx + pad if is_nan(ymax) else ymax
		var font := get_theme_default_font()
		var m := Rect2(38, 18, size.x - 46, size.y - 28)
		for i in 5:
			var y := m.position.y + m.size.y * i / 4.0
			draw_line(Vector2(m.position.x, y), Vector2(m.end.x, y), Color(0.12, 0.28, 0.33, 0.6), 1.0)
			var val := hi - (hi - lo) * i / 4.0
			draw_string(font, Vector2(3, y + 4), _fmt(val), HORIZONTAL_ALIGNMENT_LEFT, 36, 10, UITheme.TEXT_DIM)
		if not is_nan(guide) and guide > lo and guide < hi:
			var gy := m.position.y + m.size.y * (1.0 - (guide - lo) / (hi - lo))
			draw_line(Vector2(m.position.x, gy), Vector2(m.end.x, gy), guide_color, 1.0)
		for s in series:
			var d: PackedFloat32Array = s["data"]
			if d.size() < 2:
				continue
			var pts := PackedVector2Array()
			for i in d.size():
				pts.append(Vector2(m.position.x + m.size.x * i / float(maxi(1, d.size() - 1)),
					m.position.y + m.size.y * (1.0 - (d[i] - lo) / (hi - lo))))
			draw_polyline(pts, s.get("color", UITheme.ACCENT), 1.8, true)
		draw_string(font, Vector2(8, 13), title + ("  [" + unit + "]" if unit != "" else ""), HORIZONTAL_ALIGNMENT_LEFT, size.x - 12, 12, UITheme.ACCENT)

	static func _fmt(v: float) -> String:
		if absf(v) >= 1000.0:
			return "%.0f" % v
		if absf(v) >= 100.0:
			return "%.0f" % v
		return "%.1f" % v

## Horizontal bar with caption and value text; colour changes at warn/crit thresholds (fractions of full).
class Meter extends Control:
	var value := 0.0                      # 0..1
	var caption := ""
	var text := ""
	var warn := -1.0                      # fraction above which the bar turns amber (-1 = never)
	var crit := -1.0
	var invert := false                   # low is bad (e.g. health): warn/crit are lower bounds
	var tint := UITheme.ACCENT

	func _init() -> void:
		custom_minimum_size = Vector2(120, 22)

	func set_value(v: float, t := "") -> void:
		value = clampf(v, 0.0, 1.0)
		if t != "":
			text = t
		queue_redraw()

	func _draw() -> void:
		var font := get_theme_default_font()
		var cap_w := 0.0
		if caption != "":
			cap_w = minf(size.x * 0.4, 150.0)
			draw_string(font, Vector2(0, size.y * 0.5 + 5), caption, HORIZONTAL_ALIGNMENT_LEFT, cap_w, 13, UITheme.TEXT_DIM)
		var r := Rect2(cap_w, 3, size.x - cap_w, size.y - 6)
		draw_rect(r, Color(0.02, 0.05, 0.07), true)
		var col := tint
		if invert:
			if crit >= 0.0 and value < crit:
				col = UITheme.BAD
			elif warn >= 0.0 and value < warn:
				col = UITheme.WARN
		else:
			if crit >= 0.0 and value > crit:
				col = UITheme.BAD
			elif warn >= 0.0 and value > warn:
				col = UITheme.WARN
		draw_rect(Rect2(r.position, Vector2(r.size.x * value, r.size.y)), col.darkened(0.25), true)
		draw_rect(Rect2(r.position, Vector2(r.size.x * value, 2)), col, true)
		draw_rect(r, UITheme.RULE, false, 1.0)
		if text != "":
			draw_string(font, Vector2(r.position.x + 6, size.y * 0.5 + 5), text, HORIZONTAL_ALIGNMENT_LEFT, r.size.x - 8, 12, Color.WHITE)

## Circular gauge with a needle and a numeric readout.
class Dial extends Control:
	var value := 0.0
	var vmin := 0.0
	var vmax := 100.0
	var caption := ""
	var unit := ""
	var warn_above := NAN
	var crit_above := NAN

	func _init() -> void:
		custom_minimum_size = Vector2(130, 120)

	func set_value(v: float) -> void:
		value = v
		queue_redraw()

	func _draw() -> void:
		var c := Vector2(size.x * 0.5, size.y * 0.58)
		var rad := minf(size.x * 0.5, size.y * 0.55) - 6.0
		var a0 := deg_to_rad(150.0)
		var span := deg_to_rad(240.0)
		draw_arc(c, rad, a0, a0 + span, 40, Color(0.1, 0.22, 0.27), 6.0, true)
		var f := clampf((value - vmin) / maxf(vmax - vmin, 0.0001), 0.0, 1.0)
		var col := UITheme.ACCENT
		if not is_nan(crit_above) and value > crit_above:
			col = UITheme.BAD
		elif not is_nan(warn_above) and value > warn_above:
			col = UITheme.WARN
		if f > 0.0:
			draw_arc(c, rad, a0, a0 + span * f, 40, col, 6.0, true)
		var ang := a0 + span * f
		draw_line(c, c + Vector2(cos(ang), sin(ang)) * (rad - 10.0), Color.WHITE, 2.0, true)
		draw_circle(c, 4.0, col)
		var font := get_theme_default_font()
		draw_string(font, Vector2(0, c.y + rad * 0.55), "%.0f%s" % [value, unit], HORIZONTAL_ALIGNMENT_CENTER, size.x, 15, Color.WHITE)
		draw_string(font, Vector2(0, 12), caption, HORIZONTAL_ALIGNMENT_CENTER, size.x, 12, UITheme.TEXT_DIM)
