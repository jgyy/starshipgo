class_name ScreenRegistry
extends RefCounted
## Finds every screen in the ship and tells which one the player is looking at.
##
## Build time (hooks in ShipBuilder._meshes_of / _build_props): for each model the surfaces whose material is named
## "screen_<texture>" are extracted as oriented quads (centre, normal, in-plane axes, half sizes, glTF node name).  For
## every placed prop those become world-space records kept in per-room lists.  Props without a screen but which are
## machines (consoles, reactors, lockers ...) get an oriented-box record that opens a machine data card.
##
## Run time: update() is called at ~10 Hz with the camera transform; it tests only the player's room and its neighbours,
## analytically (ray vs oriented quad / box, no colliders or per-screen nodes), holds the best candidate within RANGE
## metres and a CONE_DEG cone that is front-facing, and applies hysteresis so the prompt does not flicker.

const RANGE := 3.0
const CONE_DEG := 35.0
const QUAD_MARGIN := 0.12

var model_screens: Dictionary = {}     # model id -> Array of local-space screen dicts
var records: Array = []                # every record
var by_room: Dictionary = {}           # room id -> Array of records
var current: Dictionary = {}           # best candidate or {}
var highlight: MeshInstance3D
var props_with_screens := 0
var props_machine := 0
var _cur_score := 1e9

# ------------------------------------------------------------------ extraction (per model, once)
## meshes: Array of {mesh, xf, name} as built by ShipBuilder._meshes_of.  Returns the model's local screen dicts.
func index_model(id: String, meshes: Array) -> Array:
	var out: Array = []
	for mm in meshes:
		var mesh: Mesh = mm["mesh"]
		var xf: Transform3D = mm["xf"]
		for i in mesh.get_surface_count():
			var mat := mesh.surface_get_material(i)
			if mat == null or not mat.resource_name.begins_with("screen_"):
				continue
			out.append_array(_quads_of(mesh, i, xf, mat.resource_name.trim_prefix("screen_"), String(mm.get("name", ""))))
	model_screens[id] = out
	return out

static func _quads_of(mesh: Mesh, surf: int, xf: Transform3D, tex: String, node_name: String) -> Array:
	var arr := mesh.surface_get_arrays(surf)
	var verts: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
	var normals: Variant = arr[Mesh.ARRAY_NORMAL]
	var idx: Variant = arr[Mesh.ARRAY_INDEX]
	var tris: PackedInt32Array
	if idx is PackedInt32Array and (idx as PackedInt32Array).size() > 0:
		tris = idx
	else:
		tris = PackedInt32Array()
		for k in verts.size():
			tris.append(k)
	# connected components of triangles over shared vertex indices (one quad -> one screen)
	var parent := PackedInt32Array()
	for k in verts.size():
		parent.append(k)
	for t in range(0, tris.size() - 2, 3):
		_union(parent, tris[t], tris[t + 1])
		_union(parent, tris[t], tris[t + 2])
	var comps: Dictionary = {}
	for t in range(0, tris.size() - 2, 3):
		var root := _find(parent, tris[t])
		if not comps.has(root):
			comps[root] = []
		(comps[root] as Array).append(t)
	var out: Array = []
	for root in comps.keys():
		var tl: Array = comps[root]
		var t0: int = tl[0]
		var a: Vector3 = xf * verts[tris[t0]]
		var b: Vector3 = xf * verts[tris[t0 + 1]]
		var c: Vector3 = xf * verts[tris[t0 + 2]]
		var n := (b - a).cross(c - a)
		if n.length() < 1e-9:
			continue
		n = n.normalized()
		# Godot front faces are clockwise: prefer the mesh's own normal when it has one
		if normals is PackedVector3Array and (normals as PackedVector3Array).size() > tris[t0]:
			var mn: Vector3 = (xf.basis * (normals as PackedVector3Array)[tris[t0]]).normalized()
			if mn.dot(n) < 0.0:
				n = -n
		else:
			n = -n
		var pts: Array = []
		for t in tl:
			for j in 3:
				pts.append(xf * verts[tris[t + j]])
		# the two shorter edges of the first triangle are the quad's sides (the longest one is the diagonal)
		var edges: Array = [b - a, c - b, a - c]
		edges.sort_custom(func(x: Vector3, y: Vector3) -> bool: return x.length() < y.length())
		var u: Vector3 = edges[1]
		u = (u - n * u.dot(n)).normalized()
		var v := n.cross(u).normalized()
		var umin := 1e9
		var umax := -1e9
		var vmin := 1e9
		var vmax := -1e9
		var mn3 := Vector3(1e9, 1e9, 1e9)
		var mx3 := Vector3(-1e9, -1e9, -1e9)
		for p in pts:
			var pu: float = (p as Vector3).dot(u)
			var pv: float = (p as Vector3).dot(v)
			umin = minf(umin, pu)
			umax = maxf(umax, pu)
			vmin = minf(vmin, pv)
			vmax = maxf(vmax, pv)
			mn3 = mn3.min(p)
			mx3 = mx3.max(p)
		var plane_d: float = a.dot(n)
		var centre := u * ((umin + umax) * 0.5) + v * ((vmin + vmax) * 0.5) + n * plane_d
		var hu := (umax - umin) * 0.5
		var hv := (vmax - vmin) * 0.5
		if hv > hu:                      # keep u along the longer side
			var tmp := u
			u = v
			v = -tmp
			var th := hu
			hu = hv
			hv = th
		out.append({"tex": tex, "node": node_name, "center": centre, "normal": n, "u": u, "v": v, "hu": hu, "hv": hv,
			"aabb": AABB(mn3, mx3 - mn3)})
	return out

static func _find(p: PackedInt32Array, x: int) -> int:
	while p[x] != x:
		p[x] = p[p[x]]
		x = p[x]
	return x

static func _union(p: PackedInt32Array, a: int, b: int) -> void:
	var ra := _find(p, a)
	var rb := _find(p, b)
	if ra != rb:
		p[ra] = rb

# ------------------------------------------------------------------ placement
## Register the screens (or the machine box) of one placed prop.  `room` is the ship.json room dict.
func add_prop(room: Dictionary, model_id: String, entry: Dictionary, xf: Transform3D) -> void:
	var rid: String = room["id"]
	var dept: String = room.get("dept", "")
	var cat: String = entry.get("category", "")
	var label: String = String(entry.get("label", model_id)).capitalize()
	var screens: Array = model_screens.get(model_id, [])
	if not by_room.has(rid):
		by_room[rid] = []
	var sc := xf.basis.get_scale().x
	if not screens.is_empty():
		props_with_screens += 1
		for s in screens:
			var rec := {
				"kind": "screen", "model": model_id, "label": label, "category": cat, "room": rid, "room_name": room.get("name", rid),
				"tex": s["tex"], "node": s["node"],
				"center": xf * (s["center"] as Vector3),
				"normal": (xf.basis * (s["normal"] as Vector3)).normalized(),
				"u": (xf.basis * (s["u"] as Vector3)).normalized(),
				"v": (xf.basis * (s["v"] as Vector3)).normalized(),
				"hu": float(s["hu"]) * sc, "hv": float(s["hv"]) * sc,
			}
			rec["app"] = AppCatalog.resolve(model_id, cat, String(s["tex"]), rid, dept)
			records.append(rec)
			by_room[rid].append(rec)
		return
	var app_override: bool = AppCatalog.ID_APP.has(model_id) or AppCatalog.CATEGORY_APP.has(cat)
	if cat in AppCatalog.MACHINE_CATS or app_override:
		var lo: Array = entry.get("bounds_min", [-0.3, 0, -0.3])
		var hi: Array = entry.get("bounds_max", [0.3, 1, 0.3])
		var lc := Vector3((lo[0] + hi[0]) * 0.5, (lo[1] + hi[1]) * 0.5, (lo[2] + hi[2]) * 0.5) * sc
		var half := Vector3(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]) * 0.5 * sc
		if half.length() < 0.12:
			return
		var ob := xf.basis.orthonormalized()
		var rec := {
			"kind": "box", "model": model_id, "label": label, "category": cat, "room": rid, "room_name": room.get("name", rid),
			"tex": "", "node": "", "center": xf.origin + ob * lc, "box": Transform3D(ob, xf.origin + ob * lc),
			"half": half + Vector3.ONE * 0.04,
		}
		rec["app"] = AppCatalog.resolve(model_id, cat, "", rid, dept)
		records.append(rec)
		by_room[rid].append(rec)
		props_machine += 1

# ------------------------------------------------------------------ analytic tests
## Ray vs oriented quad.  Returns the ray parameter t >= 0 of a front-facing hit, or -1.
static func ray_quad(o: Vector3, d: Vector3, c: Vector3, n: Vector3, u: Vector3, v: Vector3, hu: float, hv: float, margin := 0.0) -> float:
	var denom := d.dot(n)
	if denom >= -1e-6:
		return -1.0                       # parallel or looking at the back
	var t := (c - o).dot(n) / denom
	if t < 0.0:
		return -1.0
	var p := o + d * t - c
	if absf(p.dot(u)) <= hu + margin and absf(p.dot(v)) <= hv + margin:
		return t
	return -1.0

## Ray vs oriented box (slab test in box space).  Returns entry distance (0 when inside) or -1.
static func ray_box(o: Vector3, d: Vector3, box: Transform3D, half: Vector3) -> float:
	var lo := box.affine_inverse() * o
	var ld := box.basis.inverse() * d
	var tmin := 0.0
	var tmax := 1e9
	for k in 3:
		if absf(ld[k]) < 1e-9:
			if absf(lo[k]) > half[k]:
				return -1.0
		else:
			var t1 := (-half[k] - lo[k]) / ld[k]
			var t2 := (half[k] - lo[k]) / ld[k]
			tmin = maxf(tmin, minf(t1, t2))
			tmax = minf(tmax, maxf(t1, t2))
			if tmin > tmax:
				return -1.0
	return tmin

## Evaluate one record for a camera: returns {} when not a candidate, else {"score", "dist", "hit"}.
func evaluate(r: Dictionary, o: Vector3, d: Vector3) -> Dictionary:
	var c: Vector3 = r["center"]
	var to := c - o
	var dist := to.length()
	if dist < 0.05:
		return {}
	var cone := cos(deg_to_rad(CONE_DEG))
	if r["kind"] == "screen":
		var n: Vector3 = r["normal"]
		if (o - c).dot(n) < 0.02:
			return {}
		if dist > RANGE:
			return {}
		var cosang := d.dot(to / dist)
		var hit := ray_quad(o, d, c, n, r["u"], r["v"], r["hu"], r["hv"], QUAD_MARGIN)
		if hit < 0.0 and cosang < cone:
			return {}
		var ang := acos(clampf(cosang, -1.0, 1.0))
		return {"score": ang + (0.0 if hit >= 0.0 else 0.35) + dist * 0.04, "dist": dist, "hit": hit >= 0.0}
	var t := ray_box(o, d, r["box"], r["half"])
	var half: Vector3 = r["half"]
	if t >= 0.0 and t <= RANGE:
		return {"score": 0.45 + t * 0.04, "dist": t, "hit": true}
	if dist - half.length() > RANGE:
		return {}
	var ca := d.dot(to / dist)
	if ca < cos(deg_to_rad(CONE_DEG * 0.5)):
		return {}
	return {"score": acos(clampf(ca, -1.0, 1.0)) + 0.9 + dist * 0.04, "dist": dist, "hit": false}

## Re-evaluate the candidate.  `space` (optional) rejects screens behind walls (neighbour rooms only).
func update(cam: Transform3D, room: String, adj: Dictionary, space: PhysicsDirectSpaceState3D = null) -> Dictionary:
	var o := cam.origin
	var d := -cam.basis.z
	var rooms: Array = [room]
	for nb in adj.get(room, []):
		rooms.append(nb)
	var cands: Array = []
	for rid in rooms:
		for r in by_room.get(rid, []):
			var e := evaluate(r, o, d)
			if e.is_empty():
				continue
			if r["room"] != room and space != null and _occluded(space, o, r["center"], e["dist"]):
				continue
			cands.append([float(e["score"]), r])
	if cands.is_empty():
		current = {}
		_cur_score = 1e9
		return current
	cands.sort_custom(func(a: Array, b: Array) -> bool: return a[0] < b[0])
	var best: Array = cands[0]
	if not current.is_empty():
		for c in cands:               # hysteresis: stay on the held target unless another is clearly better
			if c[1] == current and c[0] <= best[0] + 0.18:
				best = c
				break
	current = best[1]
	_cur_score = best[0]
	return current

func _occluded(space: PhysicsDirectSpaceState3D, o: Vector3, target: Vector3, dist: float) -> bool:
	var q := PhysicsRayQueryParameters3D.create(o, target, 1)
	var hit := space.intersect_ray(q)
	return not hit.is_empty() and o.distance_to(hit["position"]) < dist - 0.35

# ------------------------------------------------------------------ highlight quad
func attach_highlight(parent: Node3D) -> void:
	highlight = MeshInstance3D.new()
	var q := QuadMesh.new()
	q.size = Vector2(1, 1)
	highlight.mesh = q
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	var img := Image.create(64, 64, false, Image.FORMAT_RGBA8)
	for y in 64:
		for x in 64:
			var edge := mini(mini(x, 63 - x), mini(y, 63 - y))
			img.set_pixel(x, y, Color(0.3, 0.92, 1.0, 0.95 if edge < 3 else (0.5 if edge < 5 else 0.07)))
	m.albedo_texture = ImageTexture.create_from_image(img)
	m.albedo_color = Color(0.55, 0.75, 0.8, 0.8)
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	highlight.material_override = m
	highlight.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	highlight.visible = false
	parent.add_child(highlight)

func show_highlight(rec: Dictionary) -> void:
	if highlight == null:
		return
	if rec.is_empty() or rec["kind"] != "screen":
		highlight.visible = false
		return
	var u: Vector3 = rec["u"]
	var v: Vector3 = rec["v"]
	var n: Vector3 = rec["normal"]
	var bas := Basis(u * (float(rec["hu"]) * 2.0 + 0.05), v * (float(rec["hv"]) * 2.0 + 0.05), n)
	highlight.global_transform = Transform3D(bas, (rec["center"] as Vector3) + n * 0.012)
	highlight.visible = true

# ------------------------------------------------------------------ reporting
func summary() -> Dictionary:
	var by_app: Dictionary = {}
	var unmapped := 0
	var screens := 0
	var known := AppCatalog.known_ids()
	for r in records:
		by_app[r["app"]] = int(by_app.get(r["app"], 0)) + 1
		if r["kind"] == "screen":
			screens += 1
		if not (r["app"] in known) or not AppCatalog.has_script(r["app"]):
			unmapped += 1
	return {"records": records.size(), "screens": screens, "props_with_screens": props_with_screens, "machines": props_machine,
		"unmapped": unmapped, "by_app": by_app}
