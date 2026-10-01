extends AppBase
## Diagnostics: run a level 1-3 test of every subsystem; the result follows the real subsystem health.

var _tree: Tree
var _prog: UIW.Meter
var _level: OptionButton
var _run: Button
var _out: Label
var _idx := -1
var _t := 0.0
var _results: Array = []
var _names: Array = []

func title_text() -> String:
	return "DIAGNOSTICS"

func build() -> void:
	for s in st.subsystems:
		_names.append(s["name"])
	var v := vb(self, 8)
	var top := hb(v)
	lbl(top, "Test depth", 14, T.TEXT_DIM)
	_level = OptionButton.new()
	for t in ["LEVEL 1  (quick)", "LEVEL 2  (standard)", "LEVEL 3  (full)"]:
		_level.add_item(t)
	_level.selected = 1
	_level.focus_mode = Control.FOCUS_NONE
	top.add_child(_level)
	_run = btn(top, "RUN DIAGNOSTIC", _start)
	btn(top, "CLEAR", func() -> void:
		_results.clear()
		_prog.set_value(0.0, ""))
	_prog = meter(v, "PROGRESS")
	var p := panel(v, "Results")
	_tree = table(p, ["System", "Result", "Detail"], [200, 100, 360])
	_out = wrap_lbl(v, "", 15, T.TEXT)

func _start() -> void:
	if _idx >= 0:
		return
	_results.clear()
	_idx = 0
	_t = 0.0
	_run.disabled = true
	st.say("Diagnostic level %d started" % (_level.selected + 1), "info")

func tick(dt: float) -> void:
	if _idx < 0:
		return
	_t += dt
	var per := 0.35 + 0.35 * _level.selected
	if _t >= per:
		_t = 0.0
		var s: Dictionary = st.subsystems[_idx]
		var hv := float(s["health"])
		var res := ["PASS", T.OK, "within tolerance"]
		if hv < 55.0:
			res = ["FAIL", T.BAD, "fault %d detected - schedule repair" % (100 + int(rnd(String(s["id"]), 1) * 800))]
		elif hv < 85.0:
			res = ["WARN", T.WARN, "degraded to %.0f%%" % hv]
		_results.append([s["name"], [res[0], res[1]], res[2]])
		_idx += 1
		if _idx >= st.subsystems.size():
			_idx = -1
			_run.disabled = false
			var fails := 0
			for r in _results:
				if r[1][0] != "PASS":
					fails += 1
			_out.text = "Diagnostic complete: %d of %d systems need attention." % [fails, _results.size()]
			st.say(_out.text, "info")
		_fill()

func _fill() -> void:
	table_fill(_tree, _results)

func refresh() -> void:
	var done := _results.size()
	_prog.set_value(float(done) / maxf(1.0, st.subsystems.size()), "%d / %d" % [done, st.subsystems.size()])
