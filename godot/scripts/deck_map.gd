extends Control
## Top-down deck plan drawn from ship.json with the player marker.

var ship: Dictionary = {}
var player: Node3D
var deck := 2

const DEPT := {
	"command": Color(0.25, 0.45, 0.9), "engineering": Color(0.95, 0.55, 0.15), "medical": Color(0.35, 0.85, 0.8),
	"science": Color(0.35, 0.8, 0.4), "security": Color(0.9, 0.3, 0.3), "crew": Color(0.7, 0.6, 0.9),
	"cargo": Color(0.75, 0.7, 0.3), "transit": Color(0.5, 0.55, 0.62), "life": Color(0.3, 0.75, 0.6),
}

func _process(_d: float) -> void:
	if visible:
		if player:
			for d in ship.get("decks", []):
				if absf(player.global_position.y - float(d["y"])) < 2.0:
					deck = int(d["id"])
		queue_redraw()

func _draw() -> void:
	if ship.is_empty():
		return
	var vp := size
	draw_rect(Rect2(Vector2.ZERO, vp), Color(0.02, 0.05, 0.09, 0.9))
	# bounds
	var mn := Vector2(1e9, 1e9)
	var mx := Vector2(-1e9, -1e9)
	for r in ship["rooms"]:
		var rc: Array = r["rect"]
		mn = mn.min(Vector2(rc[0], rc[1]))
		mx = mx.max(Vector2(rc[2], rc[3]))
	var margin := 90.0
	var sc := minf((vp.x - margin * 2.0) / (mx.x - mn.x), (vp.y - margin * 2.0) / (mx.y - mn.y))
	var off := Vector2(margin, margin) + ((vp - Vector2(margin, margin) * 2.0) - (mx - mn) * sc) * 0.5
	var font := ThemeDB.fallback_font
	for r in ship["rooms"]:
		if int(r["deck"]) != deck:
			continue
		var rc: Array = r["rect"]
		var p0 := (Vector2(rc[0], rc[1]) - mn) * sc + off
		var p1 := (Vector2(rc[2], rc[3]) - mn) * sc + off
		var col: Color = DEPT.get(r.get("dept", "transit"), DEPT["transit"])
		draw_rect(Rect2(p0, p1 - p0), Color(col, 0.28))
		draw_rect(Rect2(p0, p1 - p0), col, false, 2.0)
		var label: String = r["name"]
		var fs := 13 if (p1.x - p0.x) > 90 else 10
		if (p1.x - p0.x) > 34 and (p1.y - p0.y) > 20:
			draw_string(font, p0 + Vector2(4, 16), label, HORIZONTAL_ALIGNMENT_LEFT, p1.x - p0.x - 6, fs, Color(1, 1, 1, 0.9))
	draw_string(font, Vector2(40, 48), "DECK %d  -  %s" % [deck, _deck_name()], HORIZONTAL_ALIGNMENT_LEFT, -1, 26, Color(0.7, 0.9, 1.0))
	draw_string(font, Vector2(40, 74), "bow (fore) is up   |   M closes the map", HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color(0.6, 0.7, 0.8))
	if player:
		var pp := (Vector2(player.global_position.x, player.global_position.z) - mn) * sc + off
		var yaw: float = player.rotation.y
		var fwd := Vector2(-sin(yaw), -cos(yaw))
		var side := Vector2(-fwd.y, fwd.x)
		draw_colored_polygon(PackedVector2Array([pp + fwd * 11, pp - fwd * 7 + side * 6, pp - fwd * 7 - side * 6]), Color(1, 0.9, 0.3))

func _deck_name() -> String:
	for d in ship.get("decks", []):
		if int(d["id"]) == deck:
			return String(d["name"])
	return ""
