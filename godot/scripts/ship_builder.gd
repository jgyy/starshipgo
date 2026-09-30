class_name ShipBuilder
extends Node3D
## Builds the whole starship at runtime from res://data/ship.json (rooms, doors, lights,
## props) and res://data/catalog.json (the 1000 Blender GLB components).

const WALL_T := 0.15
const SLAB_T := 0.3

var catalog: Dictionary = {}          # id -> catalog entry
var ship: Dictionary = {}
var doors: Array[Node3D] = []
var lifts: Array[Node3D] = []
var room_nodes: Dictionary = {}       # room id -> Node3D
var stats := {"props": 0, "lights": 0, "doors": 0, "models_used": {}}
var _scenes: Dictionary = {}
var _box_meshes: Dictionary = {}

func load_data() -> void:
	var cat: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/catalog.json"))
	for m in cat["models"]:
		catalog[m["id"]] = m
	ship = JSON.parse_string(FileAccess.get_file_as_string("res://data/ship.json"))

func build() -> void:
	for room in ship["rooms"]:
		_build_room(room)
	for d in ship["doors"]:
		_place_door(d)
	for l in ship.get("lifts", []):
		_place_lift(l)
	print("ship built: %d rooms, %d props, %d lights, %d doors, %d distinct models" % [
		ship["rooms"].size(), stats["props"], stats["lights"], stats["doors"], stats["models_used"].size()])

# ------------------------------------------------------------------ shell
func _deck_y(deck: int) -> float:
	for d in ship["decks"]:
		if int(d["id"]) == deck:
			return float(d["y"])
	return 0.0

class BoxSet:
	var boxes: Dictionary = {}     # material key -> Array[AABB]
	func add(key: String, a: Vector3, b: Vector3) -> void:
		if b.x - a.x < 0.001 or b.y - a.y < 0.001 or b.z - a.z < 0.001:
			return
		if not boxes.has(key):
			boxes[key] = []
		boxes[key].append(AABB(a, b - a))

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
	return ShipMaterials.surface("hull_panel")

func _build_room(room: Dictionary) -> void:
	var rid: String = room["id"]
	var node := Node3D.new()
	node.name = rid
	add_child(node)
	room_nodes[rid] = node
	var r: Array = room["rect"]
	var x0: float = r[0]; var z0: float = r[1]; var x1: float = r[2]; var z1: float = r[3]
	var y0 := _deck_y(int(room["deck"]))
	var h: float = room.get("height", 3.4)
	var set := BoxSet.new()
	# slabs
	set.add("floor", Vector3(x0, y0 - SLAB_T, z0), Vector3(x1, y0, z1))
	var hole = room.get("hole")
	if hole != null:
		pass
	set.add("ceiling", Vector3(x0, y0 + h, z0), Vector3(x1, y0 + h + SLAB_T, z1))
	# walls
	for side in ["N", "S", "E", "W"]:
		var ops: Array = []
		for o in room.get("openings", []):
			if o["side"] == side:
				ops.append(o)
		_wall(set, room, side, ops, x0, z0, x1, z1, y0, h)
	# meshes + collision + occluders
	var body := StaticBody3D.new()
	body.name = "Shell"
	body.collision_layer = 1
	body.collision_mask = 0
	node.add_child(body)
	for key in set.boxes.keys():
		var st := SurfaceTool.new()
		st.begin(Mesh.PRIMITIVE_TRIANGLES)
		for bb in set.boxes[key]:
			var bm := BoxMesh.new()
			bm.size = bb.size
			st.append_from(bm, 0, Transform3D(Basis.IDENTITY, bb.position + bb.size * 0.5))
			if key != "glass":
				var cs := CollisionShape3D.new()
				var sh := BoxShape3D.new()
				sh.size = bb.size
				cs.shape = sh
				cs.position = bb.position + bb.size * 0.5
				body.add_child(cs)
			else:
				var cs2 := CollisionShape3D.new()
				var sh2 := BoxShape3D.new()
				sh2.size = bb.size
				cs2.shape = sh2
				cs2.position = bb.position + bb.size * 0.5
				body.add_child(cs2)
		st.generate_normals()
		st.generate_tangents()
		var mi := MeshInstance3D.new()
		mi.mesh = st.commit()
		mi.material_override = _mat_for(key, room)
		mi.name = "Mesh_" + key
		if key == "glass":
			mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		node.add_child(mi)
	# forcefield planes / decorative extras
	for ff in room.get("forcefields", []):
		var q := MeshInstance3D.new()
		var qm := QuadMesh.new()
		qm.size = Vector2(ff["size"][0], ff["size"][1])
		q.mesh = qm
		q.material_override = ShipMaterials.forcefield()
		q.position = Vector3(ff["pos"][0], ff["pos"][1], ff["pos"][2])
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
	# lights
	for l in room.get("lights", []):
		_add_light(node, l)
	# props
	var pnode := Node3D.new()
	pnode.name = "Props"
	node.add_child(pnode)
	var pbody := StaticBody3D.new()
	pbody.name = "PropBody"
	pbody.collision_layer = 1
	pbody.collision_mask = 0
	node.add_child(pbody)
	for p in room.get("props", []):
		_place_prop(pnode, pbody, p)

func _wall(set: BoxSet, room: Dictionary, side: String, ops: Array, x0: float, z0: float, x1: float, z1: float, y0: float, h: float) -> void:
	# wall runs along an axis; a/b = start/end coordinate along it
	var horizontal := side == "N" or side == "S"   # runs along X
	var a: float; var b: float
	var p0: float; var p1: float                   # across thickness
	if horizontal:
		a = x0; b = x1
		if side == "N":
			p0 = z0; p1 = z0 + WALL_T
		else:
			p0 = z1 - WALL_T; p1 = z1
	else:
		a = z0 + WALL_T; b = z1 - WALL_T
		if side == "W":
			p0 = x0; p1 = x0 + WALL_T
		else:
			p0 = x1 - WALL_T; p1 = x1
	ops.sort_custom(func(u, v): return u["c"] < v["c"])
	var cur := a
	for o in ops:
		var oa: float = o["c"] - o["w"] * 0.5
		var ob: float = o["c"] + o["w"] * 0.5
		_wall_box(set, "wall", horizontal, cur, oa, p0, p1, y0, y0 + h)
		var yb: float = o.get("y0", 0.0)
		var yt: float = o.get("y1", 2.6)
		if yb > 0.01:
			_wall_box(set, "wall", horizontal, oa, ob, p0, p1, y0, y0 + yb)
		if yt < h - 0.01:
			_wall_box(set, "wall", horizontal, oa, ob, p0, p1, y0 + yt, y0 + h)
		if o.get("kind", "door") == "window":
			var gm := (p0 + p1) * 0.5
			_wall_box(set, "glass", horizontal, oa, ob, gm - 0.015, gm + 0.015, y0 + yb, y0 + yt)
			var f := 0.08
			_wall_box(set, "frame", horizontal, oa - f, oa, p0 - 0.02, p1 + 0.02, y0 + yb - f, y0 + yt + f)
			_wall_box(set, "frame", horizontal, ob, ob + f, p0 - 0.02, p1 + 0.02, y0 + yb - f, y0 + yt + f)
			_wall_box(set, "frame", horizontal, oa, ob, p0 - 0.02, p1 + 0.02, y0 + yb - f, y0 + yb)
			_wall_box(set, "frame", horizontal, oa, ob, p0 - 0.02, p1 + 0.02, y0 + yt, y0 + yt + f)
			# mullions every ~3 m for wide windows
			var n := int(floor((ob - oa) / 3.2))
			for k in range(1, n + 1):
				var mx := oa + (ob - oa) * k / float(n + 1)
				_wall_box(set, "frame", horizontal, mx - 0.05, mx + 0.05, p0 - 0.03, p1 + 0.03, y0 + yb, y0 + yt)
		cur = ob
	_wall_box(set, "wall", horizontal, cur, b, p0, p1, y0, y0 + h)

func _wall_box(set: BoxSet, key: String, horizontal: bool, a: float, b: float, p0: float, p1: float, ya: float, yb: float) -> void:
	if horizontal:
		set.add(key, Vector3(a, ya, p0), Vector3(b, yb, p1))
	else:
		set.add(key, Vector3(p0, ya, a), Vector3(p1, yb, b))

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
	lt.distance_fade_begin = 24.0
	lt.distance_fade_shadow = 14.0
	lt.distance_fade_length = 8.0
	lt.light_specular = 0.6
	lt.position = Vector3(l["pos"][0], l["pos"][1], l["pos"][2])
	parent.add_child(lt)
	stats["lights"] += 1

# ------------------------------------------------------------------ props
func _scene_for(id: String) -> PackedScene:
	if _scenes.has(id):
		return _scenes[id]
	var entry: Dictionary = catalog.get(id, {})
	if entry.is_empty():
		push_warning("unknown model " + id)
		return null
	var ps: PackedScene = load("res://" + entry["file"])
	_scenes[id] = ps
	return ps

func _place_prop(parent: Node3D, body: StaticBody3D, p: Dictionary) -> Node3D:
	var ps := _scene_for(p["m"])
	if ps == null:
		return null
	var inst: Node3D = ps.instantiate()
	var pos: Array = p["pos"]
	inst.position = Vector3(pos[0], pos[1], pos[2])
	inst.rotation_degrees = Vector3(p.get("pitch", 0.0), p.get("yaw", 0.0), p.get("roll", 0.0))
	var sc: float = p.get("scale", 1.0)
	if sc != 1.0:
		inst.scale = Vector3.ONE * sc
	parent.add_child(inst)
	var entry: Dictionary = catalog[p["m"]]
	var size := Vector3(entry["size"][0], entry["size"][1], entry["size"][2])
	var maxd := maxf(size.x, maxf(size.y, size.z))
	var vr := 16.0 if maxd < 0.3 else (28.0 if maxd < 0.8 else (48.0 if maxd < 2.0 else 90.0))
	_set_visibility(inst, vr)
	stats["props"] += 1
	stats["models_used"][p["m"]] = true
	if p.get("solid", entry.get("solid", false)) and size.y > 0.35 and (size.x > 0.25 or size.z > 0.25):
		var lo: Array = entry["bounds_min"]
		var hi: Array = entry["bounds_max"]
		var c := Vector3((lo[0] + hi[0]) * 0.5, (lo[1] + hi[1]) * 0.5, (lo[2] + hi[2]) * 0.5) * sc
		var cs := CollisionShape3D.new()
		var bs := BoxShape3D.new()
		bs.size = size * sc * Vector3(0.95, 1.0, 0.95)
		cs.shape = bs
		cs.transform = Transform3D(inst.basis.orthonormalized(), inst.position + inst.basis.orthonormalized() * c)
		body.add_child(cs)
	return inst

func _set_visibility(n: Node, vr: float) -> void:
	if n is GeometryInstance3D:
		var g := n as GeometryInstance3D
		g.visibility_range_end = vr
		g.visibility_range_end_margin = 3.0
	for c in n.get_children():
		_set_visibility(c, vr)

# ------------------------------------------------------------------ doors / lifts
func _place_door(d: Dictionary) -> void:
	var ps := _scene_for(d["m"])
	if ps == null:
		return
	var inst: Node3D = ps.instantiate()
	inst.set_script(load("res://scripts/door.gd"))
	inst.position = Vector3(d["pos"][0], d["pos"][1], d["pos"][2])
	inst.rotation_degrees.y = d.get("yaw", 0.0)
	add_child(inst)
	inst.call("setup", d.get("locked", false))
	_set_visibility(inst, 60.0)
	doors.append(inst)
	stats["doors"] += 1
	stats["models_used"][d["m"]] = true

func _place_lift(l: Dictionary) -> void:
	var area := Area3D.new()
	area.set_script(load("res://scripts/lift.gd"))
	area.position = Vector3(l["pos"][0], l["pos"][1], l["pos"][2])
	area.name = "Lift_" + str(l.get("name", "lift"))
	add_child(area)
	area.call("setup", Vector3(l["size"][0], l["size"][1], l["size"][2]), ship["decks"])
	lifts.append(area)
