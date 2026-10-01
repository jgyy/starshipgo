extends AppBase
## Science lab: run experiments (progress advances while a terminal is open), a periodic table, a spectrograph.

var _tabs: TabContainer
var _exp: Tree
var _prog: UIW.Meter
var _res: Label
var _elem_grid: GridContainer
var _elem_info: Label
var _spec: UIW.Canvas
var _elem_sel := 0
var _t := 0.0

const ELEMENTS := [["H", "Hydrogen", 1.008], ["He", "Helium", 4.003], ["Li", "Lithium", 6.94], ["Be", "Beryllium", 9.012], ["B", "Boron", 10.81], ["C", "Carbon", 12.011],
	["N", "Nitrogen", 14.007], ["O", "Oxygen", 15.999], ["F", "Fluorine", 18.998], ["Ne", "Neon", 20.18], ["Na", "Sodium", 22.99], ["Mg", "Magnesium", 24.305],
	["Al", "Aluminium", 26.982], ["Si", "Silicon", 28.085], ["P", "Phosphorus", 30.974], ["S", "Sulfur", 32.06], ["Cl", "Chlorine", 35.45], ["Ar", "Argon", 39.948],
	["K", "Potassium", 39.098], ["Ca", "Calcium", 40.078], ["Ti", "Titanium", 47.867], ["Cr", "Chromium", 51.996], ["Mn", "Manganese", 54.938], ["Fe", "Iron", 55.845],
	["Co", "Cobalt", 58.933], ["Ni", "Nickel", 58.693], ["Cu", "Copper", 63.546], ["Zn", "Zinc", 65.38], ["Ag", "Silver", 107.87], ["Sn", "Tin", 118.71],
	["W", "Tungsten", 183.84], ["Pt", "Platinum", 195.08], ["Au", "Gold", 196.97], ["Hg", "Mercury", 200.59], ["Pb", "Lead", 207.2], ["U", "Uranium", 238.03]]

func title_text() -> String:
	return "SCIENCE LAB"

func build() -> void:
	_tabs = tab_container(self, ["EXPERIMENTS", "PERIODIC TABLE", "SPECTROGRAPH"])
	var p := page(_tabs, 0)
	_exp = table(p, ["Experiment", "Progress", "State"], [330, 90, 110])
	_exp.item_selected.connect(refresh)
	var br := hb(p)
	btn(br, "START / STOP", _toggle)
	btn(br, "RESET", _reset)
	_prog = meter(p, "SELECTED")
	_res = wrap_lbl(p, "", 14, T.TEXT_DIM)
	var ep := page(_tabs, 1)
	_elem_grid = GridContainer.new()
	_elem_grid.columns = 9
	ep.add_child(_elem_grid)
	for i in ELEMENTS.size():
		var b := Button.new()
		b.text = ELEMENTS[i][0]
		b.custom_minimum_size = Vector2(56, 44)
		b.focus_mode = Control.FOCUS_NONE
		b.pressed.connect(_pick_elem.bind(i))
		_elem_grid.add_child(b)
	_elem_info = wrap_lbl(ep, "", 16, T.TEXT)
	_pick_elem(0)
	_spec = canvas(page(_tabs, 2), 240)
	_spec.draw_fn = _draw_spec
	wrap_lbl(page(_tabs, 2), "Emission spectrum of the selected element (periodic table tab).", 13, T.TEXT_DIM)
	if host_tex() == "periodic":
		_tabs.current_tab = 1

func _sel() -> int:
	var m: Variant = table_selected(_exp)
	return -1 if m == null else int(m)

func _toggle() -> void:
	var i := _sel()
	if i >= 0:
		var e: Dictionary = st.experiments[i]
		if float(e["progress"]) >= 100.0:
			return
		e["running"] = not e["running"]
		st.say("Experiment %s: %s" % ["started" if e["running"] else "paused", e["name"]], "science")
		st.changed.emit()

func _reset() -> void:
	var i := _sel()
	if i >= 0:
		st.experiments[i].merge({"progress": 0.0, "running": false, "result": ""}, true)
		st.changed.emit()

func _pick_elem(i: int) -> void:
	_elem_sel = i
	var e: Array = ELEMENTS[i]
	_elem_info.text = "%s (%s)   atomic number %d   mass %.3f u" % [e[1], e[0], i + 1, e[2]]
	if _spec != null:
		_spec.queue_redraw()

func tick(dt: float) -> void:
	_t += dt
	if _tabs.current_tab == 2:
		_spec.queue_redraw()

func refresh() -> void:
	var rows: Array = []
	var metas: Array = []
	for i in st.experiments.size():
		var e: Dictionary = st.experiments[i]
		rows.append([e["name"], "%.0f%%" % e["progress"], ["RUNNING", T.WARN] if e["running"] else (["DONE", T.OK] if float(e["progress"]) >= 100.0 else ["idle", T.TEXT_DIM])])
		metas.append(i)
	table_fill(_exp, rows, metas)
	var i2 := _sel()
	if i2 >= 0:
		var e2: Dictionary = st.experiments[i2]
		_prog.set_value(float(e2["progress"]) / 100.0, "%.0f%%" % e2["progress"])
		_res.text = String(e2["result"])

func _draw_spec(c: UIW.Canvas) -> void:
	var f := c.get_theme_default_font()
	var w := c.size.x - 24.0
	var base := c.size.y - 44.0
	for i in 100:
		var x := 12.0 + w * i / 99.0
		var lam := 380.0 + 400.0 * i / 99.0
		c.draw_line(Vector2(x, base), Vector2(x, base + 16), _wave_col(lam), 3.0)
	for k in 7:
		var lam2 := 390.0 + 380.0 * fmod(rnd(ELEMENTS[_elem_sel][0], k) * 1.7 + k * 0.13, 1.0)
		var x2 := 12.0 + w * (lam2 - 380.0) / 400.0
		var hgt := (40.0 + 140.0 * rnd(ELEMENTS[_elem_sel][0], k + 20)) * (0.8 + 0.2 * sin(_t * 3.0 + k))
		c.draw_line(Vector2(x2, base), Vector2(x2, base - hgt), _wave_col(lam2), 4.0)
		c.draw_string(f, Vector2(x2 - 14, base - hgt - 4), "%.0f nm" % lam2, HORIZONTAL_ALIGNMENT_LEFT, -1, 10, T.TEXT_DIM)
	c.draw_string(f, Vector2(12, 18), "%s emission lines" % ELEMENTS[_elem_sel][1], HORIZONTAL_ALIGNMENT_LEFT, -1, 14, T.ACCENT)

func _wave_col(nm: float) -> Color:
	return Color.from_hsv(clampf((780.0 - nm) / 400.0 * 0.78, 0.0, 0.78), 0.9, 1.0)
