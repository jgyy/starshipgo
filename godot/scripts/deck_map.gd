class_name DeckMap
extends Control
## Top-down deck plan drawn from ship.json (tapered rooms, doors, windows, stairs) with the player marker.

var ship: Dictionary = {}
var player: Node3D
var deck := 2

const DEPT := {
	"command": Color(0.25, 0.45, 0.9), "engineering": Color(0.95, 0.55, 0.15), "medical": Color(0.35, 0.85, 0.8),
	"science": Color(0.35, 0.8, 0.4), "security": Color(0.9, 0.3, 0.3), "crew": Color(0.7, 0.6, 0.9),
	"cargo": Color(0.75, 0.7, 0.3), "transit": Color(0.5, 0.55, 0.62), "life": Color(0.3, 0.75, 0.6),
}

var _last_key := ""

func _process(_d: float) -> void:
	if not visible:
		_last_key = ""
		return
	if player:
		for d in ship.get("decks", []):
			if absf(player.global_position.y - float(d["y"])) < 2.0:
				deck = int(d["id"])
	# redraw only when the picture can have changed (deck, player position/heading, window size)
	var key := "%d|%s|%s|%s" % [deck, str(size), "" if player == null else "%.1f,%.1f" % [player.global_position.x, player.global_position.z],
		"" if player == null else "%.2f" % player.rotation.y]
	if key != _last_key:
		_last_key = key
		queue_redraw()

func _bounds() -> Array:
	var mn := Vector2(1e9, 1e9)
	var mx := Vector2(-1e9, -1e9)
	for k in ship.get("hull", {}).keys():
		for p in ship["hull"][k]:
			mn = mn.min(Vector2(p[0], p[1]))
			mx = mx.max(Vector2(p[0], p[1]))
	if mn.x > mx.x:
		for r in ship["rooms"]:
			var rc: Array = r["rect"]
			mn = mn.min(Vector2(rc[0], rc[1]))
			mx = mx.max(Vector2(rc[2], rc[3]))
	return [mn, mx]

func _draw() -> void:
	if ship.is_empty():
		return
	var vp := size
	draw_rect(Rect2(Vector2.ZERO, vp), Color(0.02, 0.05, 0.09, 0.92))
	var bb := _bounds()
	var mn: Vector2 = bb[0]
	var mx: Vector2 = bb[1]
	var margin := 90.0
	var sc := map_scale(vp, mn, mx, margin)
	var off := Vector2(margin, margin) + ((vp - Vector2(margin, margin) * 2.0) - (mx - mn) * sc) * 0.5
	var font := ThemeDB.fallback_font
	var tf := func(p) -> Vector2: return (Vector2(p[0], p[1]) - mn) * sc + off
	# hull outline of this deck
	var hull: Array = ship.get("hull", {}).get(str(deck), [])
	if hull.size() > 2:
		var hp := PackedVector2Array()
		for p in hull:
			hp.append(tf.call(p))
		hp.append(hp[0])
		draw_polyline(hp, Color(0.55, 0.75, 1.0, 0.55), 3.0)
	for r in ship["rooms"]:
		if int(r["deck"]) != deck:
			continue
		var pts := PackedVector2Array()
		var c := Vector2.ZERO
		for p in r["poly"]:
			var q: Vector2 = tf.call(p)
			pts.append(q)
			c += q
		c /= float(pts.size())
		var col: Color = DEPT.get(r.get("dept", "transit"), DEPT["transit"])
		draw_colored_polygon(pts, Color(col, 0.28))
		var closed := pts.duplicate()
		closed.append(pts[0])
		draw_polyline(closed, col, 2.0)
		var rc: Array = r["rect"]
		var wpx: float = (rc[2] - rc[0]) * sc
		var hpx: float = (rc[3] - rc[1]) * sc
		if wpx > 34.0 and hpx > 20.0:
			var fit := fit_label(font, r["name"], wpx - 6.0, 13, 7)
			draw_string(font, c + Vector2(-wpx * 0.5 + 3.0, 4.0), fit["text"], HORIZONTAL_ALIGNMENT_CENTER, wpx - 6.0, fit["size"], Color(1, 1, 1, 0.9))
		# windows (cyan) on the hull walls
		var edges := {}
		for e in r["edges"]:
			edges[e["side"]] = e
		for o in r.get("openings", []):
			if o["kind"] != "window":
				continue
			var e: Dictionary = edges.get(o["side"], {})
			if e.is_empty():
				continue
			var a := Vector2(e["a"][0], e["a"][1])
			var b := Vector2(e["b"][0], e["b"][1])
			var u := (b - a).normalized()
			var mid: Vector2
			var s: String = o["side"]
			if s == "N" or s == "S":
				mid = Vector2(o["c"], a.y)
			elif s == "E" or s == "W":
				mid = Vector2(a.x, o["c"])
			else:
				mid = a + u * float(o["c"])
			var h := u * float(o["w"]) * 0.5
			draw_line((mid - h - mn) * sc + off, (mid + h - mn) * sc + off, Color(0.5, 0.85, 1.0), 3.0)
		# stair towers: arrows
		if str(r["id"]).begins_with("tower"):
			draw_string(font, c + Vector2(-16, 18), "STAIRS " + stair_hint(ship.get("decks", []), deck), HORIZONTAL_ALIGNMENT_LEFT, -1, 10, Color(1, 0.92, 0.5))
	for d in ship.get("doors", []):
		var y: float = d["pos"][1]
		for dk in ship["decks"]:
			if int(dk["id"]) == deck and absf(float(dk["y"]) - y) < 0.1:
				var pp: Vector2 = tf.call([d["pos"][0], d["pos"][2]])
				var horiz: bool = absf(float(d.get("yaw", 0.0))) < 1.0
				var hv := Vector2(10, 0) if horiz else Vector2(0, 10)
				draw_line(pp - hv, pp + hv, Color(1, 0.4, 0.3), 3.0)
	draw_string(font, Vector2(40, 48), "DECK %d  -  %s" % [deck, _deck_name()], HORIZONTAL_ALIGNMENT_LEFT, -1, 26, Color(0.7, 0.9, 1.0))
	draw_string(font, Vector2(40, 74), "bow (fore) is up   |   red = doors, cyan = windows   |   M closes the map", HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color(0.6, 0.7, 0.8))
	if player:
		var pp: Vector2 = tf.call([player.global_position.x, player.global_position.z])
		var yaw: float = player.rotation.y
		var fwd := Vector2(-sin(yaw), -cos(yaw))
		var side := Vector2(-fwd.y, fwd.x)
		draw_colored_polygon(PackedVector2Array([pp + fwd * 11, pp - fwd * 7 + side * 6, pp - fwd * 7 - side * 6]), Color(1, 0.9, 0.3))

## Room label that fits `width`: the font shrinks from max_fs to min_fs and, if the text is still too wide, is cut with an
## ellipsis (the old code stopped shrinking at 7 px and let draw_string clip "Starboard Stair Tower" to "Starboard Stair To").
static func fit_label(font: Font, text: String, width: float, max_fs: int, min_fs: int) -> Dictionary:
	var fs := max_fs
	while fs > min_fs and font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > width:
		fs -= 1
	if font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x <= width:
		return {"text": text, "size": fs}
	for n in range(text.length() - 1, 0, -1):
		var cand := text.substr(0, n).strip_edges() + "…"
		if font.get_string_size(cand, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x <= width:
			return {"text": cand, "size": fs}
	return {"text": "…", "size": fs}

## Pixels per metre of the plan.  A window narrower than 2 x margin made the old expression negative: the plan was drawn
## mirrored and the rooms' text sizes went wrong; the scale now never drops below a sliver.
static func map_scale(vp: Vector2, mn: Vector2, mx: Vector2, margin: float) -> float:
	var w := maxf(mx.x - mn.x, 0.001)
	var h := maxf(mx.y - mn.y, 0.001)
	return maxf(minf((vp.x - margin * 2.0) / w, (vp.y - margin * 2.0) / h), 0.01)

## Which way the stairs lead from `deck`: "UP" when a deck lies higher (larger y), "DN" when one lies lower.  Deck 1 is the
## TOP deck, so the old `deck > 1` / `deck < 3` test (3 decks hard-coded) labelled the top deck "UP" and the bottom deck
## "DN" the wrong way round and could not work with any other number of decks.
static func stair_hint(decks: Array, deck: int) -> String:
	var y := 0.0
	var found := false
	for d in decks:
		if int(d["id"]) == deck:
			y = float(d["y"])
			found = true
	if not found:
		return ""
	var up := false
	var dn := false
	for d in decks:
		var dy := float(d["y"]) - y
		if dy > 0.5:
			up = true
		elif dy < -0.5:
			dn = true
	return "UP/DN" if up and dn else ("UP" if up else ("DN" if dn else ""))

 

func _deck_name() -> String:
	for d in ship.get("decks", []):
		if int(d["id"]) == deck:
			return String(d["name"])
	return ""
