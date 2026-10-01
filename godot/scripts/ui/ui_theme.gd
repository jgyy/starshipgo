class_name UITheme
extends RefCounted
## Visual language of the ship's consoles: deep ink panels, thin teal rules, amber for attention, coral for danger.
## One Theme resource is built once and assigned to the terminal root; every app inherits it.

const BG := Color(0.03, 0.05, 0.08, 1.0)
const PANEL := Color(0.055, 0.085, 0.12, 0.96)
const PANEL_HI := Color(0.08, 0.13, 0.18, 1.0)
const RULE := Color(0.16, 0.42, 0.5, 1.0)
const ACCENT := Color(0.32, 0.86, 0.9)
const ACCENT_DIM := Color(0.2, 0.5, 0.58)
const TEXT := Color(0.8, 0.92, 0.95)
const TEXT_DIM := Color(0.48, 0.62, 0.68)
const OK := Color(0.4, 0.9, 0.55)
const WARN := Color(1.0, 0.76, 0.28)
const BAD := Color(1.0, 0.36, 0.3)

static var _theme: Theme

static func box(bg: Color, border: Color = RULE, bw := 1, radius := 3, pad := 6) -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.bg_color = bg
	s.border_color = border
	s.set_border_width_all(bw)
	s.set_corner_radius_all(radius)
	s.content_margin_left = pad + 2
	s.content_margin_right = pad + 2
	s.content_margin_top = pad
	s.content_margin_bottom = pad
	return s

static func make() -> Theme:
	if _theme != null:
		return _theme
	var t := Theme.new()
	t.default_font_size = 15
	t.set_color("font_color", "Label", TEXT)
	for ctrl in ["Button", "CheckButton", "CheckBox", "OptionButton"]:
		t.set_color("font_color", ctrl, TEXT)
		t.set_color("font_hover_color", ctrl, Color.WHITE)
		t.set_color("font_pressed_color", ctrl, ACCENT)
		t.set_color("font_hover_pressed_color", ctrl, ACCENT)
		t.set_color("font_focus_color", ctrl, Color.WHITE)
		t.set_color("font_disabled_color", ctrl, TEXT_DIM)
	for ctrl in ["Button", "OptionButton"]:
		t.set_stylebox("normal", ctrl, box(PANEL_HI, RULE))
		t.set_stylebox("hover", ctrl, box(Color(0.1, 0.2, 0.26), ACCENT))
		t.set_stylebox("pressed", ctrl, box(Color(0.12, 0.3, 0.34), ACCENT, 2))
		t.set_stylebox("focus", ctrl, box(Color(0, 0, 0, 0), ACCENT_DIM))
		t.set_stylebox("disabled", ctrl, box(PANEL, Color(0.12, 0.2, 0.25)))
	t.set_stylebox("panel", "PanelContainer", box(PANEL, RULE, 1, 4, 8))
	t.set_stylebox("panel", "Panel", box(PANEL, RULE, 1, 4, 8))
	t.set_stylebox("normal", "LineEdit", box(Color(0.02, 0.04, 0.06), RULE))
	t.set_stylebox("focus", "LineEdit", box(Color(0.02, 0.05, 0.08), ACCENT, 2))
	t.set_color("font_color", "LineEdit", TEXT)
	t.set_color("caret_color", "LineEdit", ACCENT)
	t.set_color("font_placeholder_color", "LineEdit", TEXT_DIM)
	t.set_stylebox("normal", "TextEdit", box(Color(0.02, 0.04, 0.06), RULE))
	t.set_stylebox("focus", "TextEdit", box(Color(0.02, 0.05, 0.08), ACCENT, 2))
	t.set_color("font_color", "TextEdit", TEXT)
	t.set_color("font_color", "RichTextLabel", TEXT)
	t.set_color("default_color", "RichTextLabel", TEXT)
	t.set_stylebox("normal", "RichTextLabel", box(Color(0, 0, 0, 0), Color(0, 0, 0, 0), 0, 0, 2))
	# lists and trees
	for ctrl in ["ItemList", "Tree"]:
		t.set_stylebox("panel", ctrl, box(Color(0.02, 0.04, 0.06), RULE, 1, 3, 4))
		t.set_color("font_color", ctrl, TEXT)
		t.set_color("font_selected_color", ctrl, Color.WHITE)
	t.set_stylebox("focus", "ItemList", box(Color(0, 0, 0, 0), ACCENT_DIM))
	t.set_stylebox("focus", "Tree", box(Color(0, 0, 0, 0), ACCENT_DIM))
	t.set_stylebox("selected", "ItemList", box(Color(0.12, 0.34, 0.4), ACCENT, 1, 2, 2))
	t.set_stylebox("selected_focus", "ItemList", box(Color(0.12, 0.34, 0.4), ACCENT, 1, 2, 2))
	t.set_stylebox("selected", "Tree", box(Color(0.12, 0.34, 0.4), ACCENT, 1, 2, 1))
	t.set_stylebox("selected_focus", "Tree", box(Color(0.12, 0.34, 0.4), ACCENT, 1, 2, 1))
	t.set_stylebox("cursor", "Tree", box(Color(0, 0, 0, 0), Color(0, 0, 0, 0)))
	t.set_stylebox("cursor_unfocused", "Tree", box(Color(0, 0, 0, 0), Color(0, 0, 0, 0)))
	t.set_color("title_button_color", "Tree", ACCENT)
	t.set_stylebox("title_button_normal", "Tree", box(PANEL_HI, RULE, 1, 0, 3))
	t.set_stylebox("title_button_pressed", "Tree", box(PANEL_HI, RULE, 1, 0, 3))
	t.set_stylebox("title_button_hover", "Tree", box(PANEL_HI, RULE, 1, 0, 3))
	# tabs
	t.set_stylebox("panel", "TabContainer", box(PANEL, RULE, 1, 3, 8))
	t.set_stylebox("tab_selected", "TabContainer", box(Color(0.12, 0.3, 0.34), ACCENT, 1, 3, 6))
	t.set_stylebox("tab_unselected", "TabContainer", box(PANEL_HI, RULE, 1, 3, 6))
	t.set_stylebox("tab_hovered", "TabContainer", box(Color(0.1, 0.2, 0.26), ACCENT, 1, 3, 6))
	t.set_stylebox("tab_focus", "TabContainer", box(Color(0, 0, 0, 0), ACCENT_DIM, 1, 3, 6))
	t.set_color("font_selected_color", "TabContainer", Color.WHITE)
	t.set_color("font_unselected_color", "TabContainer", TEXT_DIM)
	t.set_color("font_hovered_color", "TabContainer", Color.WHITE)
	# sliders
	var track := box(Color(0.02, 0.05, 0.07), RULE, 1, 2, 0)
	track.content_margin_top = 3
	track.content_margin_bottom = 3
	var fill := box(Color(0.2, 0.6, 0.68), Color(0.2, 0.6, 0.68), 0, 2, 0)
	fill.content_margin_top = 3
	fill.content_margin_bottom = 3
	t.set_stylebox("slider", "HSlider", track)
	t.set_stylebox("grabber_area", "HSlider", fill)
	t.set_stylebox("grabber_area_highlight", "HSlider", fill)
	var grab := GradientTexture2D.new()
	grab.width = 14
	grab.height = 20
	var g := Gradient.new()
	g.set_color(0, ACCENT)
	g.set_color(1, ACCENT)
	grab.gradient = g
	t.set_icon("grabber", "HSlider", grab)
	t.set_icon("grabber_highlight", "HSlider", grab)
	t.set_icon("grabber_disabled", "HSlider", grab)
	t.set_constant("separation", "VBoxContainer", 6)
	t.set_constant("separation", "HBoxContainer", 8)
	t.set_stylebox("background", "ProgressBar", box(Color(0.02, 0.05, 0.07), RULE, 1, 2, 0))
	t.set_stylebox("fill", "ProgressBar", box(Color(0.2, 0.7, 0.75), Color(0.2, 0.7, 0.75), 0, 2, 0))
	_theme = t
	return t
