extends SceneTree
## Z-fighting test:  godot --headless --path godot -s res://tests/zfight_test.gd
## Builds the ship and looks for opaque faces with different materials that lie in the same plane, face the same way
## and overlap: the depth test cannot order them, so the two textures flicker against each other as the camera moves.
## Checks every MeshInstance3D (room shells, landings, doors, stair flights, hull fascia); props are MultiMeshes of
## catalog models that are audited separately by tools/layout/audit.py.  Overlaps buried inside solid geometry (a wall
## foot standing on the floor slab, say) can never be seen, so a point 1 cm in front of each overlap is tested against
## the colliders and only visible overlaps fail the test.
## Props (the MultiMeshes of catalog models) are checked against the SHELL only: a flat prop lying exactly on a floor,
## wall or ceiling (rug, hazard panel, wall plaque ...) shares the shell's plane and flickers against it.

const PLANE_EPS := 0.002             # faces closer than 2 mm are one plane as far as the depth buffer is concerned
const MIN_AREA := 0.0004             # ignore overlaps smaller than 2 x 2 cm
const PROBE := 0.01                  # how far in front of an overlap its visibility probe sits

var _buckets: Dictionary = {}        # quantised plane -> Array of face records
var _prop_pairs := false             # `-- --prop-pairs`: also report different props that share a plane (stacked decals, overlapping floor panels)

func _initialize() -> void:
	_run.call_deferred()                 # global transforms need the root inside the tree

## `-- --model=res://models/door/door_cargo.glb` scans one GLB at the origin (every overlap listed, no ship, no visibility
## filter): the quick way to check a Blender component after editing its generator.
func _scan_model(path: String) -> void:
	var ps := load(path) as PackedScene
	if ps == null:
		printerr("cannot load ", path)
		quit(2)
		return
	var inst: Node3D = ps.instantiate()
	root.add_child(inst)
	var stack: Array[Node] = [inst]
	while stack.size() > 0:
		var n: Node = stack.pop_back()
		stack.append_array(n.get_children())
		if n is MeshInstance3D and (n as MeshInstance3D).mesh != null:
			_add_mesh(n as MeshInstance3D, root)
	var found: Array = []
	for key: Vector4i in _buckets:
		var here: Array = _buckets[key]
		_compare(here, here, true, found)
		var up := Vector4i(key.x, key.y, key.z, key.w + 1)
		if _buckets.has(up):
			_compare(here, _buckets[up], false, found)
	for f: Dictionary in found:
		var at: Vector3 = f["at"]
		print("overlap %-32s %.4f m2 at (%.3f, %.3f, %.3f) facing %s  %s" % [f["pair"], f["area"], at.x, at.y, at.z, f["n"], f["owners"]])
	print("%d coplanar overlaps in %s" % [found.size(), path])
	quit(1 if found.size() > 0 else 0)

func _run() -> void:
	var model := ""
	_prop_pairs = "--prop-pairs" in OS.get_cmdline_user_args()
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--model="):
			model = a.substr(8)
	if model != "":
		_scan_model(model)
		return
	var b := ShipBuilder.new()
	b.use_probes = false
	root.add_child(b)
	b.load_data()
	b.build()
	var faces := 0
	var stack: Array[Node] = [b]
	while stack.size() > 0:
		var n: Node = stack.pop_back()
		stack.append_array(n.get_children())
		if n is MeshInstance3D and (n as MeshInstance3D).mesh != null:
			faces += _add_mesh(n as MeshInstance3D, b)
	faces += _add_props(b)
	var found: Array = []                # {pair, area, at, probe, owners}
	for key: Vector4i in _buckets:
		var here: Array = _buckets[key]
		_compare(here, here, true, found)
		var up := Vector4i(key.x, key.y, key.z, key.w + 1)   # faces straddling a quantisation boundary
		if _buckets.has(up):
			_compare(here, _buckets[up], false, found)
	# visibility: drop overlaps whose front side is inside a collider (door leaves are excluded, they slide away)
	# the outer plating has no collider in the game (nobody can stand outside), but it hides whatever lies behind it
	var plating := StaticBody3D.new()
	plating.collision_layer = 128
	plating.collision_mask = 0
	for hull: PackedVector3Array in b.clad_hulls:
		var cs := CollisionShape3D.new()
		var shp := ConvexPolygonShape3D.new()
		shp.points = hull
		cs.shape = shp
		plating.add_child(cs)
	root.add_child(plating)
	await physics_frame
	await physics_frame
	var space := root.get_world_3d().direct_space_state
	var q := PhysicsPointQueryParameters3D.new()
	q.collision_mask = 1 | 128
	var doors: Array[RID] = []
	for d in b.doors:
		for c in d.get_children():
			if c is StaticBody3D:
				doors.append((c as StaticBody3D).get_rid())
	q.exclude = doors
	var hits: Dictionary = {}            # "matA | matB" -> {count, area, where}
	var buried := 0
	for f: Dictionary in found:
		q.position = f["probe"]
		if not space.intersect_point(q, 1).is_empty():
			buried += 1
			continue
		if not hits.has(f["pair"]):
			var at: Vector3 = f["at"]
			var fn: Vector3 = f["n"]
			hits[f["pair"]] = {"pair": f["pair"], "count": 0, "area": 0.0, "where": "(%.2f, %.2f, %.2f) facing (%.2f, %.2f, %.2f) %s" % [
				at.x, at.y, at.z, fn.x, fn.y, fn.z, f["owners"]]}
		hits[f["pair"]]["count"] += 1
		hits[f["pair"]]["area"] += f["area"]
	print("z-fight scan: %d faces in %d planes, %d coplanar overlaps (%d buried inside solids)" % [faces, _buckets.size(), found.size(), buried])
	if hits.is_empty():
		print("ZFIGHT TEST PASSED")
		quit(0)
		return
	var rows := hits.values()
	rows.sort_custom(func(x, y): return x["area"] > y["area"])
	for r in rows:
		printerr("FAIL: %-60s %4d overlaps, %.3f m2, e.g. at %s" % [r["pair"], r["count"], r["area"], r["where"]])
	quit(1)

func _material_of(mi: MeshInstance3D, surface: int) -> Material:
	if mi.material_override:
		return mi.material_override
	if mi.get_surface_override_material(surface):
		return mi.get_surface_override_material(surface)
	return mi.mesh.surface_get_material(surface)

func _is_opaque(m: Material) -> bool:
	if m is BaseMaterial3D:
		return (m as BaseMaterial3D).transparency == BaseMaterial3D.TRANSPARENCY_DISABLED
	return not (m is ShaderMaterial)     # the forcefield shader is additive and never writes depth

func _add_mesh(mi: MeshInstance3D, ship: Node) -> int:
	var xf := mi.global_transform
	var owner_name := str(ship.get_path_to(mi))
	var src: Node = mi
	while src != ship and src.scene_file_path == "":
		src = src.get_parent()
	if src != ship:                      # name the GLB the face comes from, not the auto-generated node name
		owner_name = "%s:%s" % [src.scene_file_path.get_file().get_basename(), mi.name]
	var added := 0
	for si in mi.mesh.get_surface_count():
		if mi.mesh is ArrayMesh and (mi.mesh as ArrayMesh).surface_get_primitive_type(si) != Mesh.PRIMITIVE_TRIANGLES:
			continue                     # primitive meshes (QuadMesh ...) are always triangles
		var mat := _material_of(mi, si)
		if mat == null or not _is_opaque(mat):
			continue
		var mat_name := mat.resource_name if mat.resource_name != "" else "%s:%d" % [mi.name, si]
		var arrays := mi.mesh.surface_get_arrays(si)
		var v: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
		var idx: PackedInt32Array = arrays[Mesh.ARRAY_INDEX] if arrays[Mesh.ARRAY_INDEX] != null else PackedInt32Array()
		var count := idx.size() if idx.size() > 0 else v.size()
		for t in range(0, count - 2, 3):
			var a := xf * v[idx[t] if idx.size() > 0 else t]
			var bb := xf * v[idx[t + 1] if idx.size() > 0 else t + 1]
			var c := xf * v[idx[t + 2] if idx.size() > 0 else t + 2]
			var cr := (bb - a).cross(c - a)
			if cr.length() < 1e-6:
				continue
			var nrm := -cr.normalized()      # front faces wind clockwise in Godot
			var d := nrm.dot(a)
			var key := Vector4i(roundi(nrm.x * 100.0), roundi(nrm.y * 100.0), roundi(nrm.z * 100.0), floori(d / PLANE_EPS))
			var tri := _flatten(nrm, [a, bb, c])
			if not _buckets.has(key):
				_buckets[key] = []
			_buckets[key].append({"tri": tri, "box": _rect(tri), "d": d, "mat": mat, "name": mat_name,
				"owner": owner_name, "n": nrm, "prop": false})
			added += 1
	return added

## Every placed prop instance as faces (meshes are transformed once per instance, arrays cached per mesh).  The
## transforms come from the builder: the headless renderer does not keep MultiMesh instance data.
func _add_props(b: ShipBuilder) -> int:
	var added := 0
	var cache: Dictionary = {}               # model id -> Array[{v, idx, mat, xf}]
	for pi: Dictionary in b.prop_instances:
		var id: String = pi["m"]
		if not cache.has(id):
			var surfs: Array = []
			for mm: Dictionary in b._meshes_of(id):
				var mesh: Mesh = mm["mesh"]
				for si in mesh.get_surface_count():
					var mat: Material = mesh.surface_get_material(si)
					if mat == null or not _is_opaque(mat):
						continue
					var arrays := mesh.surface_get_arrays(si)
					var idx: PackedInt32Array = arrays[Mesh.ARRAY_INDEX] if arrays[Mesh.ARRAY_INDEX] != null else PackedInt32Array()
					surfs.append({"v": arrays[Mesh.ARRAY_VERTEX], "idx": idx, "mat": mat, "xf": mm["xf"]})
			cache[id] = surfs
		var inst_xf: Transform3D = pi["xf"]
		for s: Dictionary in cache[id]:
			var xf: Transform3D = inst_xf * (s["xf"] as Transform3D)
			var v: PackedVector3Array = s["v"]
			var idx: PackedInt32Array = s["idx"]
			var count := idx.size() if idx.size() > 0 else v.size()
			var mat: Material = s["mat"]
			var mat_name := mat.resource_name if mat.resource_name != "" else "prop"
			for t in range(0, count - 2, 3):
				var a := xf * v[idx[t] if idx.size() > 0 else t]
				var bb := xf * v[idx[t + 1] if idx.size() > 0 else t + 1]
				var c := xf * v[idx[t + 2] if idx.size() > 0 else t + 2]
				var cr := (bb - a).cross(c - a)
				if cr.length() < 1e-6:
					continue
				var nrm := -cr.normalized()
				var d := nrm.dot(a)
				var key := Vector4i(roundi(nrm.x * 100.0), roundi(nrm.y * 100.0), roundi(nrm.z * 100.0), floori(d / PLANE_EPS))
				# only faces that can share a plane with the shell are worth keeping
				if not _prop_pairs and not (_buckets.has(key) or _buckets.has(Vector4i(key.x, key.y, key.z, key.w - 1)) or _buckets.has(Vector4i(key.x, key.y, key.z, key.w + 1))):
					continue
				var tri := _flatten(nrm, [a, bb, c])
				if not _buckets.has(key):
					_buckets[key] = []
				_buckets[key].append({"tri": tri, "box": _rect(tri), "d": d, "mat": mat, "name": mat_name,
					"owner": "%s/%s@(%.1f,%.1f,%.1f)" % [pi["room"], id, inst_xf.origin.x, inst_xf.origin.y, inst_xf.origin.z],
					"n": nrm, "prop": true})
				added += 1
	return added

## Drop the dominant axis of the normal: the triangle's shape in its own plane (up to a scale that does not matter here).
func _flatten(n: Vector3, pts: Array) -> PackedVector2Array:
	var out := PackedVector2Array()
	var ax := n.abs()
	for p: Vector3 in pts:
		if ax.y >= ax.x and ax.y >= ax.z:
			out.append(Vector2(p.x, p.z))
		elif ax.x >= ax.z:
			out.append(Vector2(p.z, p.y))
		else:
			out.append(Vector2(p.x, p.y))
	return out

## Inverse of _flatten: the point of the plane n.p = d above a 2D point.
func _lift(n: Vector3, d: float, p: Vector2) -> Vector3:
	var ax := n.abs()
	if ax.y >= ax.x and ax.y >= ax.z:
		return Vector3(p.x, (d - n.x * p.x - n.z * p.y) / n.y, p.y)
	if ax.x >= ax.z:
		return Vector3((d - n.y * p.y - n.z * p.x) / n.x, p.y, p.x)
	return Vector3(p.x, p.y, (d - n.x * p.x - n.y * p.y) / n.z)

func _rect(t: PackedVector2Array) -> Rect2:
	var r := Rect2(t[0], Vector2.ZERO)
	r = r.expand(t[1])
	return r.expand(t[2])

func _area(poly: PackedVector2Array) -> float:
	var s := 0.0
	for i in poly.size():
		var p := poly[i]
		var q := poly[(i + 1) % poly.size()]
		s += p.x * q.y - q.x * p.y
	return absf(s) * 0.5

func _compare(xs: Array, ys: Array, same: bool, found: Array) -> void:
	for i in xs.size():
		var fa: Dictionary = xs[i]
		for j in range(i + 1 if same else 0, ys.size()):
			var fb: Dictionary = ys[j]
			if fa["mat"] == fb["mat"] or absf(fa["d"] - fb["d"]) > PLANE_EPS:
				continue
			if fa["prop"] and fb["prop"] and (not _prop_pairs or fa["owner"] == fb["owner"]):
				continue                 # prop against prop: model-internal layering is audited with the catalog
			var ra: Rect2 = fa["box"]
			if ra.intersection(fb["box"]).get_area() < MIN_AREA:
				continue
			var area := 0.0
			var biggest := PackedVector2Array()
			var big_area := 0.0
			for poly in Geometry2D.intersect_polygons(fa["tri"], fb["tri"]):
				var pa := _area(poly)
				area += pa
				if pa > big_area:
					big_area = pa
					biggest = poly
			if area < MIN_AREA:
				continue
			var cen := Vector2.ZERO
			for p in biggest:
				cen += p
			cen /= float(biggest.size())
			var n: Vector3 = fa["n"]
			var at := _lift(n, fa["d"], cen)
			var names := [fa["name"], fb["name"]]
			names.sort()
			found.append({"pair": "%s | %s" % names, "area": area, "at": at, "n": n, "probe": at + n * PROBE,
				"owners": "%s / %s" % [fa["owner"], fb["owner"]]})
