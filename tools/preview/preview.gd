extends SceneTree
## Contact-sheet renderer for GLB files (no import step needed).
##   godot --path tools/preview --resolution 1600x900 -s res://preview.gd -- out.png a.glb b.glb ...
## Every model is uniformly scaled into a cell, turned 3/4 to the camera and labelled.

func _init() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() < 2:
		printerr("usage: godot --path tools/preview -s res://preview.gd -- out.png a.glb [b.glb ...]")
		quit(2)
		return
	var out_path: String = args[0]
	var files: Array = args.slice(1)
	var n := files.size()
	var cols := int(ceil(sqrt(n * 1.6)))
	var rows := int(ceil(float(n) / cols))
	var cell := 2.0
	var world := Node3D.new()
	root.add_child(world)
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.13, 0.15, 0.19)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.75, 0.8, 0.9)
	env.ambient_light_energy = 0.6
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.glow_enabled = true
	var we := WorldEnvironment.new()
	we.environment = env
	world.add_child(we)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-45, 35, 0)
	sun.light_energy = 1.3
	world.add_child(sun)
	var fill := DirectionalLight3D.new()
	fill.rotation_degrees = Vector3(-20, -140, 0)
	fill.light_energy = 0.5
	world.add_child(fill)
	for i in n:
		var doc := GLTFDocument.new()
		var st := GLTFState.new()
		var err := doc.append_from_file(files[i], st)
		if err != OK:
			printerr("failed to load ", files[i])
			continue
		var node := doc.generate_scene(st)
		var holder := Node3D.new()
		world.add_child(holder)
		holder.add_child(node)
		var aabb := _aabb(node, Transform3D.IDENTITY)
		var m := maxf(aabb.size.x, maxf(aabb.size.y, aabb.size.z))
		var s := 1.5 / maxf(m, 0.01)
		node.scale = Vector3.ONE * s
		node.position = -(aabb.position + aabb.size * 0.5) * s
		node.rotation_degrees.y = 0.0
		holder.rotation_degrees.y = -35.0
		var cx := (i % cols) * cell
		var cy := -(i / cols) * cell
		holder.position = Vector3(cx, cy, 0)
		var lbl := Label3D.new()
		lbl.text = files[i].get_file().get_basename()
		lbl.font_size = 22
		lbl.pixel_size = 0.0045
		lbl.position = Vector3(cx, cy - 0.98, 0.3)
		lbl.billboard = BaseMaterial3D.BILLBOARD_DISABLED
		world.add_child(lbl)
	var cam := Camera3D.new()
	cam.projection = Camera3D.PROJECTION_ORTHOGONAL
	var w := cols * cell
	var h := rows * cell
	var vp := root.size
	cam.size = maxf(h, w * vp.y / vp.x) + 0.1
	var target := Vector3((cols - 1) * cell * 0.5, -(rows - 1) * cell * 0.5, 0)
	cam.rotation_degrees = Vector3(-22, 0, 0)
	cam.position = target + cam.basis.z * 30.0
	world.add_child(cam)
	cam.make_current()
	await create_timer(0.5).timeout
	for i in 6:
		await process_frame
	var img := root.get_texture().get_image()
	img.save_png(out_path)
	print("saved ", out_path, " (", n, " models)")
	quit()

func _aabb(node: Node, xf: Transform3D) -> AABB:
	var res := AABB()
	var first := true
	var stack: Array = [[node, xf]]
	while stack.size() > 0:
		var it: Array = stack.pop_back()
		var nd: Node = it[0]
		var t: Transform3D = it[1]
		if nd is Node3D:
			t = t * (nd as Node3D).transform
		if nd is MeshInstance3D and (nd as MeshInstance3D).mesh:
			var b: AABB = t * (nd as MeshInstance3D).mesh.get_aabb()
			if first:
				res = b
				first = false
			else:
				res = res.merge(b)
		for c in nd.get_children():
			stack.append([c, t])
	return res
