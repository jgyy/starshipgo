class_name Lore
extends RefCounted
## Cached readers for the data files behind the terminals: lore.json (ship, systems, routes, logs),
## specs.json (machine data cards) and software.json (app catalogue).  Every reader degrades to an empty/default
## structure when a file is missing, so the UI never crashes on partial data.

static var _cache: Dictionary = {}

static func _read(path: String) -> Dictionary:
	if _cache.has(path):
		return _cache[path]
	var out: Dictionary = {}
	if FileAccess.file_exists(path):
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
		if typeof(parsed) == TYPE_DICTIONARY:
			out = parsed
	_cache[path] = out
	return out

static func data() -> Dictionary:
	return _read("res://data/lore.json")

static func specs() -> Dictionary:
	return _read("res://data/specs.json")

static func software() -> Dictionary:
	return _read("res://data/software.json")

static func ship_info() -> Dictionary:
	return data().get("ship", {"name": "ISV Meridian Dawn", "registry": "SG-1000", "class": "Survey cruiser", "cruise_warp": 6.0,
		"top_warp": 9.0, "ly_per_day_at_cruise": 3.0, "motto": "", "description": ""})

static func systems() -> Array:
	return data().get("systems", [])

static func system(id: String) -> Dictionary:
	for s in systems():
		if s["id"] == id:
			return s
	return {}

static func system_name(id: String) -> String:
	var s := system(id)
	return s.get("name", id.capitalize()) if id != "" else "-"

static func factions() -> Array:
	return data().get("factions", [])

static func faction(id: String) -> Dictionary:
	for f in factions():
		if f["id"] == id:
			return f
	return {"id": id, "name": id.capitalize(), "color": "#c6b6ff", "description": "", "stance": "unknown"}

static func faction_color(id: String) -> Color:
	return Color.from_string(faction(id).get("color", "#c6b6ff"), Color.WHITE)

static func pos_of(id: String) -> Vector3:
	var s := system(id)
	if s.is_empty():
		return Vector3.ZERO
	var p: Array = s.get("pos", [0, 0, 0])
	return Vector3(p[0], p[1], p[2])

static func distance(a: String, b: String) -> float:
	return pos_of(a).distance_to(pos_of(b))

static func routes() -> Array:
	return data().get("routes", [])

## Direct route between two systems (either direction) or {}.
static func route(a: String, b: String) -> Dictionary:
	for r in routes():
		if (r["a"] == a and r["b"] == b) or (r["a"] == b and r["b"] == a):
			return r
	return {}

static func neighbours(id: String) -> Array:
	var out: Array = []
	for r in routes():
		if r["a"] == id:
			out.append(r["b"])
		elif r["b"] == id:
			out.append(r["a"])
	return out

## Shortest chain of systems along known routes (Dijkstra on route length); [] when unreachable.
static func plot(a: String, b: String) -> Array:
	if a == b or system(a).is_empty() or system(b).is_empty():
		return []
	var dist := {a: 0.0}
	var prev := {}
	var open: Array = [a]
	while not open.is_empty():
		var best := 0
		for i in open.size():
			if dist[open[i]] < dist[open[best]]:
				best = i
		var cur: String = open.pop_at(best)
		if cur == b:
			break
		for nb in neighbours(cur):
			var r := route(cur, nb)
			var nd: float = dist[cur] + float(r.get("ly", distance(cur, nb)))
			if nd < dist.get(nb, 1e18):
				dist[nb] = nd
				prev[nb] = cur
				if not open.has(nb):
					open.append(nb)
	if not prev.has(b):
		return []
	var path: Array = [b]
	while path[0] != a:
		path.push_front(prev[path[0]])
	return path

static func route_length(path: Array) -> float:
	var total := 0.0
	for i in range(path.size() - 1):
		var r := route(path[i], path[i + 1])
		total += float(r.get("ly", distance(path[i], path[i + 1])))
	return total

static func hazard_color(h: String) -> Color:
	match h:
		"none": return Color(0.35, 0.85, 0.55)
		"low": return Color(0.65, 0.88, 0.4)
		"medium": return Color(1.0, 0.8, 0.3)
		"patrolled": return Color(0.55, 0.65, 1.0)
		"high": return Color(1.0, 0.38, 0.32)
	return Color(0.6, 0.7, 0.8)

static func logs() -> Array:
	return data().get("logs", [])

static func datapads() -> Array:
	return data().get("datapads", [])

static func glossary() -> Array:
	return data().get("glossary", [])

## Machine data card for one model id ({} when specs.json has no entry).
static func spec(model_id: String) -> Dictionary:
	return specs().get("models", {}).get(model_id, {})
