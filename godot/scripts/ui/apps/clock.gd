extends AppBase
## Chronometer: ship time, stardate, the ship-day wheel, a stopwatch and a countdown timer.

var _big: Label
var _sd: Label
var _day: UIW.Meter
var _sw: Label
var _cd: Label
var _cd_s: HSlider
var _sw_run := false
var _sw_t := 0.0
var _cd_run := false
var _cd_t := 0.0
var _wheel: UIW.Canvas

func title_text() -> String:
	return "CHRONOMETER"

func build() -> void:
	var row := hb(self, 12)
	var left := vb(row, 8)
	_big = lbl(left, "", 64, T.ACCENT)
	_big.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_sd = lbl(left, "", 20, T.TEXT)
	_sd.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_day = meter(left, "SHIP DAY")
	_wheel = canvas(left, 160)
	_wheel.draw_fn = _draw_wheel
	var right := vb(row, 8)
	right.custom_minimum_size.x = 360
	right.size_flags_horizontal = Control.SIZE_FILL
	var s := panel(right, "Stopwatch", false)
	_sw = lbl(s, "00:00.0", 36, T.TEXT)
	var sb := hb(s)
	btn(sb, "START / STOP", func() -> void: _sw_run = not _sw_run)
	btn(sb, "RESET", func() -> void:
		_sw_t = 0.0
		_sw_run = false)
	var c := panel(right, "Countdown", false)
	_cd = lbl(c, "00:00", 36, T.WARN)
	_cd_s = slider(c, "Minutes", 1, 60, 5, _on_cd, 1.0, "%.0f min")
	_cd_t = 300.0
	var cb := hb(c)
	btn(cb, "START / STOP", func() -> void: _cd_run = not _cd_run)
	btn(cb, "SET", func() -> void:
		_cd_t = _cd_s.value * 60.0
		_cd_run = false)

func _on_cd(v: float) -> void:
	if not _cd_run:
		_cd_t = v * 60.0

func tick(dt: float) -> void:
	if _sw_run:
		_sw_t += dt
	if _cd_run:
		_cd_t = maxf(0.0, _cd_t - dt)
		if _cd_t <= 0.0:
			_cd_run = false
			st.say("Timer elapsed", "info")
	_sw.text = "%02d:%04.1f" % [int(_sw_t) / 60, fmod(_sw_t, 60.0)]
	_cd.text = "%02d:%02d" % [int(_cd_t) / 60, int(_cd_t) % 60]
	_wheel.queue_redraw()

func _secs() -> float:
	var p := st.ship_clock().split(":")
	return float(int(p[0]) * 3600 + int(p[1]) * 60 + int(p[2]))

func refresh() -> void:
	_big.text = st.ship_clock()
	_sd.text = "STARDATE %.2f" % st.stardate()
	_day.set_value(_secs() / 86400.0, "%.0f%% of ship day" % (_secs() / 864.0))

func _draw_wheel(c: UIW.Canvas) -> void:
	var ctr := c.size * 0.5
	var r := minf(c.size.x, c.size.y) * 0.42
	c.draw_arc(ctr, r, 0, TAU, 60, T.ACCENT_DIM, 2.0, true)
	for i in 24:
		var a := TAU * i / 24.0
		c.draw_line(ctr + Vector2(sin(a), -cos(a)) * (r - (8 if i % 6 == 0 else 4)), ctr + Vector2(sin(a), -cos(a)) * r, T.ACCENT_DIM, 1.5)
	var s := _secs()
	var ha := TAU * s / 86400.0 * 2.0
	var ma := TAU * fmod(s, 3600.0) / 3600.0
	var sa := TAU * fmod(s, 60.0) / 60.0
	c.draw_line(ctr, ctr + Vector2(sin(ha), -cos(ha)) * r * 0.5, Color.WHITE, 3.0, true)
	c.draw_line(ctr, ctr + Vector2(sin(ma), -cos(ma)) * r * 0.8, T.ACCENT, 2.0, true)
	c.draw_line(ctr, ctr + Vector2(sin(sa), -cos(sa)) * r * 0.9, T.WARN, 1.0, true)
