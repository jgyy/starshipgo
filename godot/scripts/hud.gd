extends CanvasLayer
## Crosshair, location banner, stair prompt, help and the deck map overlay.

var room_label: Label
var deck_label: Label
var prompt_label: Label
var help_label: Label
var map: Control
var fade: ColorRect
var _room_tween: Tween

func _ready() -> void:
	add_to_group("hud")
	layer = 10
	var cross := Label.new()
	cross.text = "+"
	cross.add_theme_font_size_override("font_size", 22)
	cross.modulate = Color(1, 1, 1, 0.55)
	cross.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	cross.grow_horizontal = Control.GROW_DIRECTION_BOTH
	cross.grow_vertical = Control.GROW_DIRECTION_BOTH
	add_child(cross)
	room_label = _label(30, Color(0.75, 0.92, 1.0))
	room_label.position = Vector2(32, 26)
	deck_label = _label(15, Color(0.55, 0.7, 0.85))
	deck_label.position = Vector2(34, 66)
	prompt_label = _label(20, Color(1, 0.92, 0.6))
	prompt_label.set_anchors_and_offsets_preset(Control.PRESET_CENTER_BOTTOM)
	prompt_label.position.y -= 120
	prompt_label.grow_horizontal = Control.GROW_DIRECTION_BOTH
	prompt_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	help_label = _label(14, Color(0.8, 0.85, 0.9, 0.85))
	help_label.text = "WASD move   Shift sprint   Mouse look   F flashlight   M deck map   H toggle help   Esc release mouse\nStairs: the two stair towers at mid-ship lead to every deck - just walk up or down the flights"
	help_label.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_LEFT)
	help_label.position = Vector2(32, -74)
	map = load("res://scripts/deck_map.gd").new()
	map.visible = false
	map.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(map)
	fade = ColorRect.new()
	fade.color = Color(0, 0, 0, 0)
	fade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	fade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(fade)

func _label(size: int, col: Color) -> Label:
	var l := Label.new()
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", col)
	l.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.85))
	l.add_theme_constant_override("outline_size", 6)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(l)
	return l

func show_room(room_name: String, deck_name: String) -> void:
	room_label.text = room_name.to_upper()
	deck_label.text = deck_name
	room_label.modulate.a = 1.0
	if _room_tween:
		_room_tween.kill()
	_room_tween = create_tween()
	_room_tween.tween_interval(3.5)
	_room_tween.tween_property(room_label, "modulate:a", 0.35, 1.5)

func set_prompt(t: String) -> void:
	prompt_label.text = t

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("toggle_help"):
		help_label.visible = not help_label.visible
	if event.is_action_pressed("deck_map"):
		map.visible = not map.visible
