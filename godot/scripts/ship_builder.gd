class_name ShipBuilder
extends Node3D
## Builds the whole starship at runtime from res://data/ship.json (rooms, doors, stairs, lights,
## props), res://data/catalog.json (the 1000 Blender GLB components) and res://data/arch.json
## (stair flights and the hull fascia, also made in Blender).
##
## Rooms are convex polygons (drafting rectangle clipped by the tapered hull).  Every wall is an
## edge with mitered corners; hull walls get an outer plating layer (windows cut through it).
## Props are batched into one MultiMesh per (room, model mesh) and only the rooms near the player
## are drawn (see update_culling), which keeps the draw-call count low on a ~1.3k prop ship.

const WALL_T := 0.15
const SLAB_T := 0.3
const CLAD_T := 0.12
const RISER := 4.0 / 22.0
const TREAD := 0.28
const FLIGHT_W := 1.4
const REVEAL := 0.01                  # window frames overlap the opening edges by this much (no coplanar faces)
const CULL_HOPS := 2
const CULL_TICK := 0.2

var catalog: Dictionary = {}          # id -> catalog entry
var arch: Dictionary = {}             # id -> arch entry
var ship: Dictionary = {}
var doors: Array[Node3D] = []
var room_nodes: Dictionary = {}       # room id -> Node3D (shell + content)
var room_content: Dictionary = {}     # room id -> Node3D (props, lights, probe) toggled by the culling
var room_polys: Dictionary = {}       # room id -> PackedVector2Array
var room_adj: Dictionary = {}         # room id -> Array of neighbour room ids (doors, arches, stairs)
var use_probes := true
var use_culling := true
var use_occluders := false            # OccluderInstance3D per room shell; only useful with viewport occlusion culling on
var stats := {"props": 0, "lights": 0, "doors": 0, "stairs": 0, "models_used": {}, "multimeshes": 0, "colliders": 0}
var screen_registry := ScreenRegistry.new()   # interactive screens / machines (see scripts/ui/screen_registry.gd)
var hangar_fields: Array = []         # [{"mesh": MeshInstance3D, "shape": CollisionShape3D}] toggled by the docking app
var _scenes: Dictionary = {}
var _model_meshes: Dictionary = {}    # id -> Array[{mesh, xf}]
var _cull_acc := 0.0
var _visible_rooms: Dictionary = {}
var _current_room := ""

# ------------------------------------------------------------------ geometry accumulator
class Shell:
	var surf: Dictionary = {}          # material key -> {v, n, uv}
	var hulls: Array = []              # Array of PackedVector3Array (convex collision hulls)
	var occ_v := PackedVector3Array()
	var occ_i := PackedInt32Array()

	func _s(key: String) -> Dictionary:
		if not surf.has(key):
			surf[key] = {"v": PackedVector3Array(), "n": PackedVector3Array(), "uv": PackedVector2Array()}
		return surf[key]

	func tri(key: String, a: Vector3, b: Vector3, c: Vector3, n: Vector3, ua: Vector2, ub: Vector2, uc: Vector2) -> void:
		if (b - a).cross(c - a).dot(n) > 0.0:     # Godot: front faces are clockwise
			var t := b; b = c; c = t
			var tu := ub; ub = uc; uc = tu
		var s := _s(key)
		s["v"].append(a); s["v"].append(b); s["v"].append(c)
		s["n"].append(n); s["n"].append(n); s["n"].append(n)
		s["uv"].append(ua); s["uv"].append(ub); s["uv"].append(uc)

	## Convex prism from a plan polygon (x, z) between y0 and y1.
	func prism(pts: Array, y0: float, y1: float, k_side: String, k_top: String = "", k_bot: String = "",
			collide: bool = true, occlude: bool = false) -> void:
		var n := pts.size()
		if n < 3 or y1 - y0 < 0.001:
			return
		var area := 0.0
		for i in n:
			var p: Vector2 = pts[i]
			var q: Vector2 = pts[(i + 1) % n]
			area += p.x * q.y - q.x * p.y
		if absf(area) < 1e-7:
			return
		if k_top == "": k_top = k_side
		if k_bot == "": k_bot = k_side
		for i in range(1, n - 1):
			var a: Vector2 = pts[0]; var b: Vector2 = pts[i]; var c: Vector2 = pts[i + 1]
			tri(k_top, Vector3(a.x, y1, a.y), Vector3(b.x, y1, b.y), Vector3(c.x, y1, c.y), Vector3.UP, a, b, c)
			tri(k_bot, Vector3(a.x, y0, a.y), Vector3(b.x, y0, b.y), Vector3(c.x, y0, c.y), Vector3.DOWN, a, b, c)
		var acc := 0.0
		for i in n:
			var p: Vector2 = pts[i]
			var q: Vector2 = pts[(i + 1) % n]
			var d := q - p
			var ln := d.length()
			if ln < 1e-6:
				continue
			var nrm := Vector3(d.y, 0.0, -d.x).normalized()
			# outward normal: flip if the polygon winds the other way
			if area > 0.0:
				nrm = -nrm
			var v00 := Vector3(p.x, y0, p.y); var v01 := Vector3(p.x, y1, p.y)
			var v10 := Vector3(q.x, y0, q.y); var v11 := Vector3(q.x, y1, q.y)
			tri(k_side, v00, v10, v11, nrm, Vector2(acc, y0), Vector2(acc + ln, y0), Vector2(acc + ln, y1))
			tri(k_side, v00, v11, v01, nrm, Vector2(acc, y0), Vector2(acc + ln, y1), Vector2(acc, y1))
			acc += ln
		if collide:
			var pts3 := PackedVector3Array()
			for p in pts:
				pts3.append(Vector3(p.x, y0, p.y)); pts3.append(Vector3(p.x, y1, p.y))
			hulls.append(pts3)
		if occlude:
			var base := occ_v.size()
			for p in pts:
				occ_v.append(Vector3(p.x, y0, p.y)); occ_v.append(Vector3(p.x, y1, p.y))
			# triangulate the convex prism by fan over its hull vertices (2n points): top, bottom and sides
			for i in range(1, n - 1):
				occ_i.append_array(PackedInt32Array([base + 1, base + 2 * i + 1, base + 2 * i + 3]))
				occ_i.append_array(PackedInt32Array([base, base + 2 * i + 2, base + 2 * i]))
			for i in n:
				var j := (i + 1) % n
				occ_i.append_array(PackedInt32Array([base + 2 * i, base + 2 * i + 1, base + 2 * j + 1]))
				occ_i.append_array(PackedInt32Array([base + 2 * i, base + 2 * j + 1, base + 2 * j]))

func _read_json(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		push_error("missing data file " + path + " (run tools/layout/generate_ship.py and blender/build_all.py)")
		return {}
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("invalid JSON in " + path)
		return {}
	return parsed

func load_data() -> void:
	var cat := _read_json("res://data/catalog.json")
	for m in cat.get("models", []):
		catalog[m["id"]] = m
	for m in _read_json("res://data/arch.json").get("models", []):
		arch[m["id"]] = m
	ship = _read_json("res://data/ship.json")
	if ship.is_empty() or int(ship.get("version", 0)) != 2:
		push_error("ship.json is missing or not version 2 - regenerate it with tools/layout/generate_ship.py")
		ship = {"rooms": [], "doors": [], "decks": [], "stairs": []}

func build() -> void:
	for room in ship["rooms"]:
		_build_room(room)
	_build_adjacency()
	for d in ship["doors"]:
		_place_door(d)
	_build_hull_extras()
	for s in ship.get("stairs", []):
		_build_stairs(s)
	print("ship built: %d rooms, %d props (%d multimeshes), %d lights, %d doors, %d stairs, %d distinct models" % [
		ship["rooms"].size(), stats["props"], stats["multimeshes"], stats["lights"], stats["doors"], stats["stairs"],
		stats["models_used"].size()])

func _deck_y(deck: int) -> float:
	for d in ship["decks"]:
		if int(d["id"]) == deck:
			return float(d["y"])
	return 0.0

func _mat_for(key: String, room: Dictionary) -> Material:
	var tint := Color.from_string(room.get("tint", "#ffffff"), Color.WHITE)
	match key:
		"wall": return ShipMaterials.surface("wall_trim", tint, 4.0)
		"floor": return ShipMaterials.surface(room.get("floor", "deck_plate"), Color.from_string(room.get("floor_tint", "#ffffff"), Color.WHITE), 4.0)
		"ceiling": return ShipMaterials.surface("ceiling", Color.WHITE, 4.0)
		"hull": return ShipMaterials.surface("hull_dark", Color.WHITE, 4.0)
		"glass": return ShipMaterials.glass()
		"frame": return ShipMaterials.surface("hull_panel", Color(0.55, 0.58, 0.65), 4.0)
		"trim": return ShipMaterials.surface("hull_panel", Color.from_string(room.get("accent", "#3a6ea5"), Color.WHITE), 4.0)
		"glow": return ShipMaterials.emissive(Color.from_string(room.get("accent", "#3a6ea5"), Color.WHITE).lightened(0.25), 1.8)
		"clad", "roof", "belly": return ShipMaterials.surface("hull_plate", Color.WHITE, 4.0)
		"landing": return ShipMaterials.surface("deck_plate", Color(0.78, 0.82, 0.88), 4.0)
	return ShipMaterials.surface("hull_panel")

# ------------------------------------------------------------------ room shell
func _v2(a: Array) -> Vector2:
	return Vector2(a[0], a[1])

## Edge records (start a, end b, unit u, inward normal n, length) of a room in polygon order.
func _edges_of(room: Dictionary) -> Array:
	var poly: Array = room["poly"]
	var c := Vector2.ZERO
	for p in poly:
		c += _v2(p)
	c /= float(poly.size())
	var out: Array = []
	for e in room["edges"]:
		var a := _v2(e["a"]); var b := _v2(e["b"])
		var d := b - a
		var ln := d.length()
		var u := d / ln
		var n := Vector2(-u.y, u.x)
		if n.dot(c - (a + b) * 0.5) < 0.0:
			n = -n
		out.append({"side": e["side"], "a": a, "b": b, "u": u, "n": n, "len": ln, "hull": e.get("hull", false)})
	return out

## Polygon offset by distance d along the inward edge normals (negative d grows the polygon); mitered corners.
func _offset(edges: Array, d: float) -> Array:
	var n := edges.size()
	var out: Array = []
	for j in n:
		var e0: Dictionary = edges[(j - 1 + n) % n]
		var e1: Dictionary = edges[j]
		var p1: Vector2 = e0["a"] + e0["n"] * d
		var p2: Vector2 = e1["a"] + e1["n"] * d
		var cr: float = (e0["u"] as Vector2).cross(e1["u"])
		if absf(cr) < 1e-5:
			out.append(e1["a"] + e1["n"] * d)
		else:
			var t: float = (p2 - p1).cross(e1["u"]) / cr
			out.append(p1 + (e0["u"] as Vector2) * t)
	return out

func _open_s(e: Dictionary, c: float) -> float:
	var side: String = e["side"]
	if side == "N" or side == "S":
		return absf(c - (e["a"] as Vector2).x)
	if side == "E" or side == "W":
		return absf(c - (e["a"] as Vector2).y)
	return c

## Plan quad of the wall between distances s0..s1 along the edge; the ends that coincide with the edge ends are mitred.
func _wall_quad(e: Dictionary, inner: Array, idx: int, s0: float, s1: float, thickness: float) -> Array:
	var a: Vector2 = e["a"]; var u: Vector2 = e["u"]; var n: Vector2 = e["n"]
	var ln: float = e["len"]
	var o0 := a + u * s0
	var o1 := a + u * s1
	var i0: Vector2 = inner[idx] if s0 <= 1e-5 else o0 + n * thickness
	var i1: Vector2 = inner[(idx + 1) % inner.size()] if s1 >= ln - 1e-5 else o1 + n * thickness
	return [o0, o1, i1, i0]

func _build_room(room: Dictionary) -> void:
	var rid: String = room["id"]
	var node := Node3D.new()
	node.name = rid
	add_child(node)
	room_nodes[rid] = node
	var edges := _edges_of(room)
	var inner := _offset(edges, WALL_T)
	var pv := PackedVector2Array()
	for p in room["poly"]:
		pv.append(_v2(p))
	room_polys[rid] = pv
	var y0 := _deck_y(int(room["deck"]))
	var h: float = room.get("height", 3.4)
	var sh := Shell.new()
	var poly: Array = []
	for p in room["poly"]:
		poly.append(_v2(p))
	# slabs: floor (deck plate on top, hull plating below), ceiling (tiles below, plating on top)
	_slab(sh, poly, room.get("floor_holes", []), y0 - SLAB_T, y0, "floor", "belly", "floor")
	_slab(sh, poly, room.get("ceiling_holes", []), y0 + h, y0 + h + SLAB_T, "ceiling", "ceiling", "roof")
	for i in edges.size():
		_wall(sh, room, edges[i], inner, i, y0, h)
	# hull plating layer outside hull walls
	_cladding(sh, room, edges, y0, h)
	# meshes + collision + occluder
	var body := StaticBody3D.new()
	body.name = "Shell"
	body.collision_layer = 1
	body.collision_mask = 0
	node.add_child(body)
	for hull in sh.hulls:
		var cs := CollisionShape3D.new()
		var shp := ConvexPolygonShape3D.new()
		shp.points = hull
		cs.shape = shp
		body.add_child(cs)
		stats["colliders"] += 1
	for key in sh.surf.keys():
		var s: Dictionary = sh.surf[key]
		var arrays := []
		arrays.resize(Mesh.ARRAY_MAX)
		arrays[Mesh.ARRAY_VERTEX] = s["v"]
		arrays[Mesh.ARRAY_NORMAL] = s["n"]
		arrays[Mesh.ARRAY_TEX_UV] = s["uv"]
		var mesh := ArrayMesh.new()
		mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
		var mi := MeshInstance3D.new()
		mi.mesh = mesh
		mi.material_override = _mat_for(key, room)
		mi.name = "Mesh_" + key
		if key == "glass" or key == "glow":
			mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		if key == "clad" or key == "roof" or key == "belly":
			mi.layers = 3                      # interior + exterior layer: the sun (layer 2 only) lights the outer hull
		node.add_child(mi)
	if use_occluders and sh.occ_v.size() > 0:
		var occ := ArrayOccluder3D.new()
		occ.set_arrays(sh.occ_v, sh.occ_i)
		var oi := OccluderInstance3D.new()
		oi.occluder = occ
		oi.name = "Occluder"
		node.add_child(oi)
	# everything below is "content": toggled by the room culling
	var content := Node3D.new()
	content.name = "Content"
	node.add_child(content)
	room_content[rid] = content
	# forcefield planes
	for ff in room.get("forcefields", []):
		var q := MeshInstance3D.new()
		var qm := QuadMesh.new()
		qm.size = Vector2(ff["size"][0], ff["size"][1])
		q.mesh = qm
		q.material_override = ShipMaterials.forcefield()
		q.position = Vector3(ff["pos"][0], y0 + ff["pos"][1], ff["pos"][2])
		q.rotation_degrees.y = ff.get("yaw", 0.0)
		q.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		node.add_child(q)
		var fb := CollisionShape3D.new()
		var fs := BoxShape3D.new()
		fs.size = Vector3(ff["size"][0], ff["size"][1], 0.2)
		fb.shape = fs
		fb.position = q.position
		fb.rotation_degrees.y = ff.get("yaw", 0.0)
		body.add_child(fb)
		hangar_fields.append({"mesh": q, "shape": fb})
	# a one-shot reflection probe gives metals and glass the room around them
	var rc: Array = room["rect"]
	var area: float = room.get("area", 0.0)
	if use_probes and area > 30.0 and room.get("dept", "") != "transit":
		var probe := ReflectionProbe.new()
		probe.size = Vector3(rc[2] - rc[0], h + 0.4, rc[3] - rc[1])
		probe.position = Vector3((rc[0] + rc[2]) * 0.5, y0 + h * 0.5, (rc[1] + rc[3]) * 0.5)
		probe.interior = true
		probe.box_projection = true
		probe.intensity = 0.8
		probe.update_mode = ReflectionProbe.UPDATE_ONCE
		probe.max_distance = 0.0
		probe.cull_mask = 1
		probe.ambient_mode = ReflectionProbe.AMBIENT_DISABLED
		content.add_child(probe)
	# shadow-casting lights are expensive: keep the brightest few per room (big rooms get more)
	var max_shadows := 3 if area > 150.0 else 2
	var shadows := 0
	for l in room.get("lights", []):
		var ld: Dictionary = l.duplicate()
		if ld.get("shadow", false):
			if shadows >= max_shadows:
				ld["shadow"] = false
			else:
				shadows += 1
		_add_light(content, ld)
	_build_props(room, content, node)

## Slab = convex polygon minus rectangular holes (holes only exist in rectangular rooms).
func _slab(sh: Shell, poly: Array, holes: Array, y0: float, y1: float, k_side: String, k_bot: String, k_top: String) -> void:
	if holes.is_empty():
		sh.prism(poly, y0, y1, k_side, k_top, k_bot, true, true)
		return
	var xs: Array = []
	var zs: Array = []
	var minp := Vector2(1e9, 1e9); var maxp := Vector2(-1e9, -1e9)
	for p in poly:
		minp = minp.min(p); maxp = maxp.max(p)
	xs.append(minp.x); xs.append(maxp.x); zs.append(minp.y); zs.append(maxp.y)
	for hl in holes:
		xs.append(clampf(hl[0], minp.x, maxp.x)); xs.append(clampf(hl[2], minp.x, maxp.x))
		zs.append(clampf(hl[1], minp.y, maxp.y)); zs.append(clampf(hl[3], minp.y, maxp.y))
	xs.sort(); zs.sort()
	for i in xs.size() - 1:
		for j in zs.size() - 1:
			var cx: float = (xs[i] + xs[i + 1]) * 0.5
			var cz: float = (zs[j] + zs[j + 1]) * 0.5
			if xs[i + 1] - xs[i] < 0.01 or zs[j + 1] - zs[j] < 0.01:
				continue
			var in_hole := false
			for hl in holes:
				if cx > hl[0] and cx < hl[2] and cz > hl[1] and cz < hl[3]:
					in_hole = true
					break
			if in_hole:
				continue
			var cell := [Vector2(xs[i], zs[j]), Vector2(xs[i + 1], zs[j]), Vector2(xs[i + 1], zs[j + 1]), Vector2(xs[i], zs[j + 1])]
			sh.prism(cell, y0, y1, k_side, k_top, k_bot, true, true)

func _wall(sh: Shell, room: Dictionary, e: Dictionary, inner: Array, idx: int, y0: float, h: float) -> void:
	var side: String = e["side"]
	var ops: Array = []
	for o in room.get("openings", []):
		if o["side"] == side:
			ops.append({"s": _open_s(e, o["c"]), "w": o["w"], "y0": o.get("y0", 0.0), "y1": o.get("y1", 2.6), "kind": o.get("kind", "door")})
	ops.sort_custom(func(p, q): return p["s"] < q["s"])
	var cur := 0.0
	for o in ops:
		var oa: float = o["s"] - o["w"] * 0.5
		var ob: float = o["s"] + o["w"] * 0.5
		_wall_run(sh, e, inner, idx, cur, oa, y0, y0 + h)
		var yb: float = o["y0"]
		var yt: float = o["y1"]
		if yb > 0.01:
			_wall_run(sh, e, inner, idx, oa, ob, y0, y0 + yb)
		if yt < h - 0.01:
			_wall_run(sh, e, inner, idx, oa, ob, y0 + _soffit(o), y0 + h)
		if o["kind"] == "window":
			_window(sh, e, oa, ob, y0 + yb, y0 + yt)
		cur = ob
	_wall_run(sh, e, inner, idx, cur, e["len"], y0, y0 + h)
	# baseboard / accent stripe / glow on solid runs
	var prev := 0.0
	for o in ops:
		_trim(sh, e, prev, o["s"] - o["w"] * 0.5, y0, h)
		prev = o["s"] + o["w"] * 0.5
	_trim(sh, e, prev, e["len"], y0, h)

## Height of the wall / cladding above an opening.  Open hull mouths are framed by the Blender hull fascia, whose
## header underside and jambs sit exactly on the opening edges: the shell keeps REVEAL clear of them (here and in
## _cladding) so the fascia is the only surface there instead of z-fighting with it.
func _soffit(o: Dictionary) -> float:
	return o["y1"] + (REVEAL if o["kind"] == "open" else 0.0)

func _wall_run(sh: Shell, e: Dictionary, inner: Array, idx: int, s0: float, s1: float, ya: float, yb: float) -> void:
	if s1 - s0 < 0.005 or yb - ya < 0.005:
		return
	sh.prism(_wall_quad(e, inner, idx, s0, s1, WALL_T), ya, yb, "wall", "wall", "wall", true, true)

func _strip(e: Dictionary, s0: float, s1: float, d0: float, d1: float) -> Array:
	var a: Vector2 = e["a"]; var u: Vector2 = e["u"]; var n: Vector2 = e["n"]
	return [a + u * s0 + n * d0, a + u * s1 + n * d0, a + u * s1 + n * d1, a + u * s0 + n * d1]

func _window(sh: Shell, e: Dictionary, oa: float, ob: float, ya: float, yb: float) -> void:
	sh.prism(_strip(e, oa, ob, WALL_T * 0.5 - 0.015, WALL_T * 0.5 + 0.015), ya, yb, "glass", "glass", "glass", true, false)
	# The frame reaches REVEAL into the opening and stands proud of the trim strips (WALL_T + 0.02): a frame face
	# flush with the wall / cladding reveal or the trim front would share its plane and z-fight (flicker).
	var f := 0.08
	var r := REVEAL
	var d0 := -0.02
	var d1 := WALL_T + 0.03
	sh.prism(_strip(e, oa - f, oa + r, d0, d1), ya - f, yb + f, "frame", "frame", "frame", false)
	sh.prism(_strip(e, ob - r, ob + f, d0, d1), ya - f, yb + f, "frame", "frame", "frame", false)
	sh.prism(_strip(e, oa - f, ob + f, d0, d1), ya - f, ya + r, "frame", "frame", "frame", false)
	sh.prism(_strip(e, oa - f, ob + f, d0, d1), yb - r, yb + f, "frame", "frame", "frame", false)
	var n := int(floor((ob - oa) / 3.2))
	for k in range(1, n + 1):
		var mx := oa + (ob - oa) * k / float(n + 1)
		sh.prism(_strip(e, mx - 0.05, mx + 0.05, d0 - 0.01, d1 + 0.01), ya, yb, "frame", "frame", "frame", false)

func _trim(sh: Shell, e: Dictionary, s0: float, s1: float, y0: float, h: float) -> void:
	if s1 - s0 < 0.5:
		return
	var a := s0 + (0.12 if s0 <= 1e-5 else 0.0)
	var b := s1 - (0.12 if s1 >= (e["len"] as float) - 1e-5 else 0.0)
	if b - a < 0.3:
		return
	var d0 := WALL_T
	var d1 := WALL_T + 0.02
	# the baseboard sinks 5 mm into the floor slab so its underside is never flush with anything over a floor hole
	sh.prism(_strip(e, a, b, d0, d1), y0 - 0.005, y0 + 0.14, "hull", "hull", "hull", false)
	sh.prism(_strip(e, a, b, d0, d1), y0 + 1.02, y0 + 1.08, "trim", "trim", "trim", false)
	sh.prism(_strip(e, a, b, d0, d1), y0 + h - 0.17, y0 + h - 0.13, "glow", "glow", "glow", false)

## Outer plating over the hull walls of a room (windows and hull openings cut through it).
func _cladding(sh: Shell, room: Dictionary, edges: Array, y0: float, h: float) -> void:
	var hull: Array = ship.get("hull", {}).get(str(int(room["deck"])), [])
	if hull.is_empty():
		return
	# miter points of the deck outline, pushed outward by CLAD_T
	var oe: Array = _outline_edges(hull)
	var outer := _offset(oe, -CLAD_T)
	var ya := y0 - SLAB_T
	var yb := y0 + h + SLAB_T
	for e in edges:
		if not e["hull"]:
			continue
		var a: Vector2 = e["a"]; var u: Vector2 = e["u"]; var n: Vector2 = e["n"]
		var ln: float = e["len"]
		var out_n := -n
		var ops: Array = []
		for o in room.get("openings", []):
			if o["side"] == e["side"] and o.get("kind", "door") in ["window", "open"]:
				ops.append({"s": _open_s(e, o["c"]), "w": o["w"], "y0": o.get("y0", 0.0), "y1": o.get("y1", 2.6), "kind": o.get("kind", "door")})
		ops.sort_custom(func(p, q): return p["s"] < q["s"])
		var cur := 0.0
		var pieces: Array = []
		for o in ops:
			var widen: float = REVEAL if o["kind"] == "open" else 0.0     # the fascia jambs line the hull mouth
			var oa: float = o["s"] - o["w"] * 0.5 - widen
			var ob: float = o["s"] + o["w"] * 0.5 + widen
			pieces.append([cur, oa, ya, yb])
			if o["y0"] > 0.01:
				pieces.append([oa, ob, ya, y0 + o["y0"]])
			if o["y1"] < h - 0.01:
				pieces.append([oa, ob, y0 + _soffit(o), yb])
			cur = ob
		pieces.append([cur, ln, ya, yb])
		for p in pieces:
			var s0: float = p[0]; var s1: float = p[1]
			if s1 - s0 < 0.005 or p[3] - p[2] < 0.005:
				continue
			var q0 := a + u * s0
			var q1 := a + u * s1
			var o0 := q0 + out_n * CLAD_T
			var o1 := q1 + out_n * CLAD_T
			if s0 <= 1e-5:
				o0 = _outline_miter(hull, outer, q0, o0)
			if s1 >= ln - 1e-5:
				o1 = _outline_miter(hull, outer, q1, o1)
			sh.prism([q0, q1, o1, o0], p[2], p[3], "clad", "clad", "clad", false)

func _outline_edges(hull: Array) -> Array:
	var pts: Array = []
	var c := Vector2.ZERO
	for p in hull:
		pts.append(_v2(p))
		c += _v2(p)
	c /= float(pts.size())
	var out: Array = []
	for i in pts.size():
		var a: Vector2 = pts[i]
		var b: Vector2 = pts[(i + 1) % pts.size()]
		var d := b - a
		var u := d / d.length()
		var n := Vector2(-u.y, u.x)
		if n.dot(c - (a + b) * 0.5) < 0.0:
			n = -n
		out.append({"a": a, "b": b, "u": u, "n": n, "len": d.length()})
	return out

func _outline_miter(hull: Array, outer: Array, p: Vector2, fallback: Vector2) -> Vector2:
	for i in hull.size():
		if _v2(hull[i]).distance_to(p) < 0.01:
			return outer[i]
	return fallback

# ------------------------------------------------------------------ lights
func _add_light(parent: Node3D, l: Dictionary) -> void:
	var lt: Light3D
	var col := Color.from_string(l.get("color", "#fff2dd"), Color.WHITE)
	if l.get("type", "spot") == "spot":
		var s := SpotLight3D.new()
		s.spot_range = l.get("range", 9.0)
		s.spot_angle = l.get("angle", 70.0)
		s.spot_attenuation = 0.8
		s.rotation_degrees.x = -90
		lt = s
	else:
		var o := OmniLight3D.new()
		o.omni_range = l.get("range", 6.0)
		o.omni_attenuation = 1.2
		lt = o
	lt.light_color = col
	lt.light_energy = l.get("energy", 1.5)
	lt.shadow_enabled = l.get("shadow", false)
	lt.shadow_bias = 0.05
	lt.shadow_blur = 1.5
	lt.distance_fade_enabled = true
	lt.distance_fade_begin = 20.0
	lt.distance_fade_shadow = 10.0
	lt.distance_fade_length = 8.0
	lt.light_specular = 0.6
	lt.position = Vector3(l["pos"][0], l["pos"][1], l["pos"][2])
	lt.add_to_group("ship_lights")      # alert level tint / pulse (ShipState.apply_alert_lights)
	parent.add_child(lt)
	stats["lights"] += 1

# ------------------------------------------------------------------ props
func _scene_for(id: String) -> PackedScene:
	if _scenes.has(id):
		return _scenes[id]
	var entry: Dictionary = catalog.get(id, arch.get(id, {}))
	if entry.is_empty():
		push_warning("unknown model " + id)
		return null
	var ps := load("res://" + entry["file"]) as PackedScene
	if ps == null:
		push_error("cannot load model " + id + " (" + str(entry["file"]) + ") - run godot --import")
		return null                                   # not cached: a later call may succeed after an import
	_scenes[id] = ps
	return ps

## Meshes of a model with their transforms relative to the model root (extracted once per model).
func _meshes_of(id: String) -> Array:
	if _model_meshes.has(id):
		return _model_meshes[id]
	var out: Array = []
	var ps := _scene_for(id)
	if ps != null:
		var inst: Node3D = ps.instantiate()
		var stack: Array = [[inst, Transform3D.IDENTITY]]
		while stack.size() > 0:
			var it: Array = stack.pop_back()
			var n: Node3D = it[0]
			var xf: Transform3D = it[1]
			if n != inst:
				xf = xf * n.transform
			if n is MeshInstance3D and (n as MeshInstance3D).mesh != null:
				out.append({"mesh": (n as MeshInstance3D).mesh, "xf": xf, "name": String(n.name)})
			for c in n.get_children():
				if c is Node3D:
					stack.append([c, xf])
		inst.free()
	_model_meshes[id] = out
	screen_registry.index_model(id, out)
	return out

func _build_props(room: Dictionary, content: Node3D, room_node: Node3D) -> void:
	var pbody := StaticBody3D.new()
	pbody.name = "PropBody"
	pbody.collision_layer = 1
	pbody.collision_mask = 0
	room_node.add_child(pbody)
	var groups: Dictionary = {}          # model id -> Array[Transform3D]
	for p in room.get("props", []):
		var id: String = p["m"]
		var entry: Dictionary = catalog.get(id, {})
		if entry.is_empty():
			push_warning("unknown model " + id)
			continue
		var pos: Array = p["pos"]
		var basis := Basis.from_euler(Vector3(deg_to_rad(p.get("pitch", 0.0)), deg_to_rad(p.get("yaw", 0.0)), deg_to_rad(p.get("roll", 0.0))))
		var sc: float = p.get("scale", 1.0)
		basis = basis.scaled(Vector3.ONE * sc)
		var xf := Transform3D(basis, Vector3(pos[0], pos[1], pos[2]))
		if not groups.has(id):
			groups[id] = []
		groups[id].append(xf)
		_meshes_of(id)                   # indexes the model's screen surfaces before the prop is registered
		screen_registry.add_prop(room, id, entry, xf)
		stats["props"] += 1
		stats["models_used"][id] = true
		var size := Vector3(entry["size"][0], entry["size"][1], entry["size"][2])
		if p.get("solid", entry.get("solid", false)) and size.y > 0.35 and (size.x > 0.25 or size.z > 0.25):
			var lo: Array = entry["bounds_min"]
			var hi: Array = entry["bounds_max"]
			var c := Vector3((lo[0] + hi[0]) * 0.5, (lo[1] + hi[1]) * 0.5, (lo[2] + hi[2]) * 0.5) * sc
			var cs := CollisionShape3D.new()
			var bs := BoxShape3D.new()
			bs.size = size * sc * Vector3(0.95, 1.0, 0.95)
			cs.shape = bs
			var ob := basis.orthonormalized()
			cs.transform = Transform3D(ob, xf.origin + ob * c)
			pbody.add_child(cs)
			stats["colliders"] += 1
	for id in groups.keys():
		var entry: Dictionary = catalog[id]
		var xfs: Array = groups[id]
		var maxd := maxf(entry["size"][0], maxf(entry["size"][1], entry["size"][2]))
		for mm in _meshes_of(id):
			var multi := MultiMesh.new()
			multi.transform_format = MultiMesh.TRANSFORM_3D
			multi.mesh = mm["mesh"]
			multi.instance_count = xfs.size()
			for i in xfs.size():
				multi.set_instance_transform(i, (xfs[i] as Transform3D) * (mm["xf"] as Transform3D))
			var mmi := MultiMeshInstance3D.new()
			mmi.multimesh = multi
			# small things do not cast shadows: a large share of the shadow-map cost for no visible gain
			mmi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON if maxd >= 0.6 else GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			mmi.name = id
			content.add_child(mmi)
			stats["multimeshes"] += 1

# ------------------------------------------------------------------ doors
func _place_door(d: Dictionary) -> void:
	var ps := _scene_for(d["m"])
	if ps == null:
		return
	var inst: Node3D = ps.instantiate()
	inst.set_script(load("res://scripts/door.gd"))
	inst.position = Vector3(d["pos"][0], d["pos"][1], d["pos"][2])
	inst.rotation_degrees.y = d.get("yaw", 0.0)
	inst.set_meta("a", d.get("a", ""))      # rooms either side (security app / lock command)
	inst.set_meta("b", d.get("b", ""))
	add_child(inst)
	inst.call("setup")
	_set_visibility(inst, 60.0)
	doors.append(inst)
	stats["doors"] += 1
	stats["models_used"][d["m"]] = true

func _set_visibility(n: Node, vr: float) -> void:
	if n is GeometryInstance3D:
		var g := n as GeometryInstance3D
		g.visibility_range_end = vr
		g.visibility_range_end_margin = 4.0
		g.visibility_range_fade_mode = GeometryInstance3D.VISIBILITY_RANGE_FADE_SELF
	for c in n.get_children():
		_set_visibility(c, vr)

# ------------------------------------------------------------------ hull extras
func _build_hull_extras() -> void:
	if arch.has("arch_hull_fascia"):
		var ps := _scene_for("arch_hull_fascia")
		if ps != null:
			var inst: Node3D = ps.instantiate()
			inst.name = "HullFascia"
			add_child(inst)

# ------------------------------------------------------------------ stairs
func _build_stairs(s: Dictionary) -> void:
	var flight_ps := _scene_for("arch_stair_flight")
	for run in s["runs"]:
		for f in run["flights"]:
			var root := Node3D.new()
			root.name = "Flight_%s_%d_%d" % [s["id"], int(run["deck_lo"]), int(run["deck_hi"])]
			root.position = Vector3(f["pos"][0], f["pos"][1], f["pos"][2])
			root.rotation_degrees.y = f["yaw"]
			add_child(root)
			if flight_ps != null:
				root.add_child(flight_ps.instantiate())
			root.add_child(_flight_body())
			stats["stairs"] += 1
		var lr: Array = run["landing"]["rect"]
		var ly: float = run["landing"]["y"]
		var sh := Shell.new()
		sh.prism([Vector2(lr[0], lr[1]), Vector2(lr[2], lr[1]), Vector2(lr[2], lr[3]), Vector2(lr[0], lr[3])], ly - 0.18, ly, "landing", "landing", "landing", true, false)
		var body := StaticBody3D.new()
		body.collision_layer = 1
		body.collision_mask = 0
		add_child(body)
		for hull in sh.hulls:
			var cs := CollisionShape3D.new()
			var shp := ConvexPolygonShape3D.new()
			shp.points = hull
			cs.shape = shp
			body.add_child(cs)
		for key in sh.surf.keys():
			var srf: Dictionary = sh.surf[key]
			var arrays := []
			arrays.resize(Mesh.ARRAY_MAX)
			arrays[Mesh.ARRAY_VERTEX] = srf["v"]
			arrays[Mesh.ARRAY_NORMAL] = srf["n"]
			arrays[Mesh.ARRAY_TEX_UV] = srf["uv"]
			var mesh := ArrayMesh.new()
			mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
			var mi := MeshInstance3D.new()
			mi.mesh = mesh
			mi.material_override = _mat_for(key, {})
			add_child(mi)

## Walkable surface of one flight (local frame: foot at the origin, climbing -Z).  The plane sits half a
## riser below the nosing line so feet never float more than ~9 cm over a tread; the last 20 cm ramp up
## to landing level so there is no lip.
func _flight_body() -> StaticBody3D:
	var body := StaticBody3D.new()
	body.name = "FlightBody"
	body.collision_layer = 1
	body.collision_mask = 0
	var hw := FLIGHT_W * 0.5 + 0.05
	var t := 0.22
	var s_foot := -0.5 * TREAD
	var s_top := 10.0 * TREAD
	var y_top := 11.0 * RISER - RISER * 0.5
	var y_land := 11.0 * RISER
	var segs := [
		[s_foot, 0.0, s_top, y_top],
		[s_top, y_top, s_top + 0.2, y_land],
		[s_top + 0.2, y_land, 11.0 * TREAD + 0.05, y_land],
	]
	for sg in segs:
		var pts := PackedVector3Array()
		for x in [-hw, hw]:
			pts.append(Vector3(x, sg[1], -sg[0])); pts.append(Vector3(x, sg[3], -sg[2]))
			pts.append(Vector3(x, sg[1] - t, -sg[0])); pts.append(Vector3(x, sg[3] - t, -sg[2]))
		var cs := CollisionShape3D.new()
		var shp := ConvexPolygonShape3D.new()
		shp.points = pts
		cs.shape = shp
		body.add_child(cs)
	return body

# ------------------------------------------------------------------ room graph + culling
func _build_adjacency() -> void:
	for r in ship["rooms"]:
		room_adj[r["id"]] = []
	for r in ship["rooms"]:
		for lk in r.get("links", []):
			if room_adj.has(lk["to"]):
				room_adj[r["id"]].append(lk["to"])
	# stair towers connect vertically (towerA3 <-> towerA2 <-> towerA1)
	for r in ship["rooms"]:
		var rid: String = r["id"]
		if rid.begins_with("tower"):
			var base := rid.substr(0, rid.length() - 1)
			var deck := int(r["deck"])
			for d2 in [deck - 1, deck + 1]:
				var other := "%s%d" % [base, d2]
				if room_adj.has(other):
					room_adj[rid].append(other)

func room_at(p: Vector3) -> String:
	var pt := Vector2(p.x, p.z)
	var best := ""
	var best_dy := 1e9
	for r in ship["rooms"]:
		var rid: String = r["id"]
		var y0 := _deck_y(int(r["deck"]))
		var dy := p.y - y0
		if dy < -0.6 or dy > float(r.get("height", 3.4)) + 0.4:
			continue
		var rc: Array = r["rect"]
		if pt.x < rc[0] - 0.2 or pt.x > rc[2] + 0.2 or pt.y < rc[1] - 0.2 or pt.y > rc[3] + 0.2:
			continue
		if Geometry2D.is_point_in_polygon(pt, room_polys[rid]):
			if absf(dy - 0.9) < best_dy:
				best = rid
				best_dy = absf(dy - 0.9)
	return best

## Show only the room the player is in and its neighbours (CULL_HOPS doors away); walls, floors and hull stay visible.
func update_culling(player_pos: Vector3) -> void:
	if not use_culling:
		return
	var here := room_at(player_pos)
	if here == "" or here == _current_room:
		return
	_current_room = here
	var show: Dictionary = {here: true}
	var frontier: Array = [here]
	for hop in CULL_HOPS:
		var nxt: Array = []
		for rid in frontier:
			for nb in room_adj.get(rid, []):
				if not show.has(nb):
					show[nb] = true
					nxt.append(nb)
		frontier = nxt
	for rid in room_content.keys():
		var vis: bool = show.has(rid)
		if vis != _visible_rooms.get(rid, true):
			(room_content[rid] as Node3D).visible = vis
			_visible_rooms[rid] = vis

func show_all_rooms() -> void:
	for rid in room_content.keys():
		(room_content[rid] as Node3D).visible = true
		_visible_rooms[rid] = true
	_current_room = ""
