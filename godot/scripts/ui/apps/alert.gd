extends AppBase
## Alert status: choose green / yellow / red.  The level tints and pulses every ship light (group "ship_lights").

var _big: Label
var _btns: Dictionary = {}
var _desc: Label
var _log: RichTextLabel
var _auto: CheckButton
var _last := ""

const INFO := {
	"green": ["NORMAL OPERATIONS", "All systems nominal. Ship lighting at full duty. Doors operate normally."],
	"yellow": ["CAUTION", "Elevated readiness. Lighting shifts amber. Crew report to stations; weapons may be armed."],
	"red": ["EMERGENCY", "All hands to battle stations. Emergency lighting pulses red. The armory, brig, security office and computer core seal automatically."],
}

func title_text() -> String:
	return "ALERT STATUS"

func build() -> void:
	var v := vb(self, 8)
	_big = lbl(v, "", 44, T.OK)
	_big.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_desc = wrap_lbl(v, "", 17, T.TEXT)
	_desc.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	var row := hb(v, 14)
	for lv in ["green", "yellow", "red"]:
		var b := btn(row, lv.to_upper() + " ALERT", func() -> void: st.set_alert(lv), true)
		b.custom_minimum_size = Vector2(0, 74)
		b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		b.add_theme_font_size_override("font_size", 22)
		_btns[lv] = b
	var opts := panel(v, "Automation", false)
	_auto = check(opts, "Red alert seals armory, brig, security office and computer core", st.red_auto_lock, func(on: bool) -> void: st.red_auto_lock = on)
	var p := panel(v, "Alert log")
	_log = rich(p)
	_log.scroll_following = true

func refresh() -> void:
	var lv := st.alert
	var col: Color = {"green": T.OK, "yellow": T.WARN, "red": T.BAD}[lv]
	_big.text = "%s  -  %s" % [lv.to_upper(), INFO[lv][0]]
	_big.add_theme_color_override("font_color", col)
	_desc.text = INFO[lv][1]
	for k in _btns.keys():
		(_btns[k] as Button).set_pressed_no_signal(k == lv)
	var out := ""
	for m in st.messages:
		if m["kind"] in ["alert", "security"]:
			out += "[%s] %s\n" % [m["t"], m["text"]]
	if out != _last:
		_last = out
		_log.text = out
