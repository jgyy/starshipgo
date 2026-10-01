class_name Terminal
extends CanvasLayer
## Full-screen console overlay hosting one AppBase at a time.  While open: the mouse is released, the player is
## locked (player.set_ui_locked), the world keeps running, ShipState.sim() is driven from here and the app is refreshed
## at 4 Hz (or the frame after any ShipState change).  Esc, E or the CLOSE button closes it.

signal opened(app_id: String)
signal closed

var st: ShipState
var is_open := false
var app: AppBase
var host: Dictionary = {}
var title_label: Label
var status_label: Label
var _root: Control
var _frame: PanelContainer
var _body: Control
var _scan: Control
var _acc := 0.0
var _dirty := false
var _opened_frame := -1
var _tween: Tween

func _ready() -> void:
	layer = 20
	add_to_group("terminal")
	process_mode = Node.PROCESS_MODE_ALWAYS
	_root = Control.new()
	_root.theme = UITheme.make()
	_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_root.mouse_filter = Control.MOUSE_FILTER_STOP
	add_child(_root)
	var back := ColorRect.new()
	back.color = Color(0.01, 0.02, 0.035, 0.94)
	back.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	back.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_root.add_child(back)
	var margin := MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for side in ["left", "right", "top", "bottom"]:
		margin.add_theme_constant_override("margin_" + side, 22)
	_root.add_child(margin)
	_frame = PanelContainer.new()
	_frame.add_theme_stylebox_override("panel", UITheme.box(Color(0.03, 0.055, 0.08, 0.98), UITheme.ACCENT_DIM, 2, 8, 10))
	margin.add_child(_frame)
	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 8)
	_frame.add_child(col)
	var head := HBoxContainer.new()
	col.add_child(head)
	title_label = Label.new()
	title_label.add_theme_font_size_override("font_size", 22)
	title_label.add_theme_color_override("font_color", UITheme.ACCENT)
	head.add_child(title_label)
	var sp := Control.new()
	sp.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	head.add_child(sp)
	status_label = Label.new()
	status_label.add_theme_font_size_override("font_size", 14)
	status_label.add_theme_color_override("font_color", UITheme.TEXT_DIM)
	head.add_child(status_label)
	var close_btn := Button.new()
	close_btn.name = "CloseButton"
	close_btn.text = "  CLOSE  [Esc]  "
	close_btn.focus_mode = Control.FOCUS_NONE
	close_btn.pressed.connect(close)
	head.add_child(close_btn)
	var rule := ColorRect.new()
	rule.color = UITheme.RULE
	rule.custom_minimum_size.y = 2
	col.add_child(rule)
	_body = MarginContainer.new()
	_body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_body.clip_contents = true
	col.add_child(_body)
	_scan = Control.new()
	_scan.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_scan.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_scan.draw.connect(_draw_scan)
	_scan.resized.connect(_scan.queue_redraw)
	_root.add_child(_scan)
	_root.visible = false
	set_process(false)

func _draw_scan() -> void:
	var s := _scan.size
	var y := 0.0
	while y < s.y:
		_scan.draw_line(Vector2(0, y), Vector2(s.x, y), Color(0, 0, 0, 0.16), 1.0)
		y += 3.0
	# vignette corners and console bracket marks
	var c := UITheme.ACCENT
	for corner in [Vector2(14, 14), Vector2(s.x - 14, 14), Vector2(14, s.y - 14), Vector2(s.x - 14, s.y - 14)]:
		var sx := 1.0 if corner.x < s.x * 0.5 else -1.0
		var sy := 1.0 if corner.y < s.y * 0.5 else -1.0
		_scan.draw_line(corner, corner + Vector2(26 * sx, 0), c, 2.0)
		_scan.draw_line(corner, corner + Vector2(0, 26 * sy), c, 2.0)

func bind(state: ShipState) -> void:
	st = state
	st.changed.connect(func() -> void: _dirty = true)

## Open the application bound to a registry record (see ScreenRegistry) or any dictionary with an "app" key.
func open_host(rec: Dictionary) -> bool:
	return open_app(String(rec.get("app", "computer")), rec)

func open_app(app_id: String, h: Dictionary = {}) -> bool:
	if st == null:
		return false
	if is_open:
		close()
	host = h.duplicate()
	host["app"] = app_id
	if not host.has("label"):
		host["label"] = ""
	app = AppCatalog.make(app_id)
	app.terminal = self
	_body.add_child(app)
	app.start(st, host)
	var t := AppCatalog.title_of(app.app_id)
	var lab := String(host.get("label", "")).to_upper()
	title_label.text = ("%s  -  %s" % [lab, t]) if lab != "" and app.app_id != "datacard" else t
	if app.app_id == "datacard" and lab != "":
		title_label.text = "%s  -  DATA CARD" % lab
	is_open = true
	_root.visible = true
	_root.modulate.a = 0.0
	if _tween:
		_tween.kill()
	_tween = create_tween()
	_tween.tween_property(_root, "modulate:a", 1.0, 0.18)
	_opened_frame = Engine.get_process_frames()
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	get_tree().call_group("player", "set_ui_locked", true)
	st.click()
	_refresh_header()
	set_process(true)
	opened.emit(app.app_id)
	return true

func close() -> void:
	if not is_open:
		return
	is_open = false
	set_process(false)
	_root.visible = false
	if app != null:
		app.queue_free()
		app = null
	var fo := _root.get_viewport().gui_get_focus_owner()
	if fo != null:
		fo.release_focus()
	get_tree().call_group("player", "set_ui_locked", false)
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	if st:
		st.click()
	closed.emit()

func _input(event: InputEvent) -> void:
	if not is_open:
		return
	if event.is_action_pressed("ui_cancel"):
		close()
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed("interact") and not event.is_echo() and Engine.get_process_frames() != _opened_frame:
		var fo := get_viewport().gui_get_focus_owner()
		if fo is LineEdit or fo is TextEdit:
			return                                 # typing the letter e into a text field
		close()
		get_viewport().set_input_as_handled()

func _process(delta: float) -> void:
	if not is_open:
		return
	st.sim(delta)
	if app != null:
		app.tick(delta)
	_acc += delta
	var slow := _acc >= 0.25
	if slow:
		_acc = 0.0
		_refresh_header()
	if (slow or _dirty) and app != null:
		_dirty = false
		app.refresh()

func _refresh_header() -> void:
	var col := UITheme.TEXT_DIM
	var edge := UITheme.ACCENT_DIM
	match st.alert:
		"yellow": col = UITheme.WARN; edge = UITheme.WARN
		"red": col = UITheme.BAD; edge = UITheme.BAD
	status_label.text = "SD %.2f   %s   %s   " % [st.stardate(), st.ship_clock(), st.hud_line()]
	status_label.add_theme_color_override("font_color", col)
	_frame.add_theme_stylebox_override("panel", UITheme.box(Color(0.03, 0.055, 0.08, 0.98), edge, 2, 8, 10))
