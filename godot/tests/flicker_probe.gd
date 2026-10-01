extends SceneTree
## Shimmer probe: renders the same view N times with the camera yawed by tiny sub-pixel steps and writes the
## frames as PNG (HUD hidden).  tools/quality/flicker_metric.py turns them into a number.
##
## Ship mode (default) - real rooms of the ship:
##   xvfb-run -a -s "-screen 0 1280x720x24" godot --path godot --rendering-driver vulkan --resolution 960x540 \
##       -s res://tests/flicker_probe.gd -- --out=/tmp/fl --cams=01_bridge,08_mess,17_eng,20_cargo --frames=8 --step=0.005
## Texture mode - a bare 4 m x 3 m x 80 m corridor, every surface textured with one kind, so the number measures the
## texture alone (no props, no light probes, no geometry edges other than the corridor corners):
##       ... -s res://tests/flicker_probe.gd -- --mode=tex --out=/tmp/fl_tex --kinds=carpet:4,deck_plate:4,wood_parquet:2
##       (kind:metres-per-tile, comma separated)
## Optional: --taa=1 (temporal AA), --msaa=0|1|2|3 (off, 2x, 4x, 8x).  The game's own settings are kept by default.
##
## Needs a real (or software) renderer; it cannot run with --headless.

func _arg(prefix: String, def: String) -> String:
	for a in OS.get_cmdline_user_args():
		if a.begins_with(prefix):
			return a.substr(prefix.length())
	return def

func _initialize() -> void:
	if _arg("--mode=", "ship") == "tex":
		_run_tex.call_deferred()
	else:
		_run.call_deferred()

func _apply_aa() -> void:
	var taa_arg := _arg("--taa=", "")
	var msaa_arg := _arg("--msaa=", "")
	if taa_arg != "":
		root.use_taa = taa_arg == "1"
	if msaa_arg != "":
		root.msaa_3d = [Viewport.MSAA_DISABLED, Viewport.MSAA_2X, Viewport.MSAA_4X, Viewport.MSAA_8X][clampi(int(msaa_arg), 0, 3)]

func _run() -> void:
	var out := _arg("--out=", "/tmp/flicker")
	var cams := _arg("--cams=", "01_bridge,08_mess,17_eng,20_cargo").split(",")
	var frames := int(_arg("--frames=", "8"))
	var step := float(_arg("--step=", "0.005"))
	DirAccess.make_dir_recursive_absolute(out)
	var main: Node3D = load("res://scenes/Main.tscn").instantiate()
	root.add_child(main)
	for i in 5:
		await process_frame
	_apply_aa()
	var taa: bool = root.use_taa
	var player: CharacterBody3D = main.player
	player.set_physics_process(false)
	main.hud.visible = false
	var builder = main.builder
	for cam in builder.ship.get("cameras", []):
		if not (cam["name"] in cams):
			continue
		var pos: Array = cam["pos"]
		player.global_position = Vector3(pos[0], pos[1] - 1.62, pos[2])
		player.velocity = Vector3.ZERO
		player.camera.fov = cam.get("fov", 78.0)
		builder._current_room = ""
		builder.update_culling(player.global_position + Vector3(0, 0.9, 0))
		for k in frames:
			player.look_at_yaw_pitch(deg_to_rad(cam.get("yaw", 0.0) + step * k), deg_to_rad(cam.get("pitch", 0.0)))
			for i in (14 if k == 0 else (6 if taa else 3)):
				await process_frame
			var img := root.get_texture().get_image()
			img.save_png("%s/%s_%02d.png" % [out, cam["name"], k])
		print("probe ", cam["name"])
	quit()

func _plane(parent: Node3D, size: Vector2, pos: Vector3, rot: Vector3, mat: Material) -> void:
	var pm := PlaneMesh.new()
	pm.size = size
	var mi := MeshInstance3D.new()
	mi.mesh = pm
	mi.position = pos
	mi.rotation_degrees = rot
	mi.material_override = mat
	parent.add_child(mi)

func _run_tex() -> void:
	var out := _arg("--out=", "/tmp/flicker_tex")
	var frames := int(_arg("--frames=", "8"))
	var step := float(_arg("--step=", "0.005"))
	DirAccess.make_dir_recursive_absolute(out)
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.05, 0.06, 0.08)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.86, 0.88, 0.95)
	env.ambient_light_energy = 0.5
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	var we := WorldEnvironment.new()
	we.environment = env
	root.add_child(we)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-55, 25, 0)
	sun.light_energy = 1.1
	root.add_child(sun)
	var spot := OmniLight3D.new()                                  # a point light gives specular glints on the floor
	spot.position = Vector3(0, 2.8, -6)
	spot.omni_range = 40.0
	spot.light_energy = 2.0
	root.add_child(spot)
	var cam := Camera3D.new()
	cam.fov = 78.0
	cam.current = true
	cam.position = Vector3(0, 1.6, 0)
	root.add_child(cam)
	_apply_aa()
	var taa: bool = root.use_taa
	var holder := Node3D.new()
	root.add_child(holder)
	for spec in _arg("--kinds=", "").split(",", false):
		var kv := spec.split(":")
		var kind := kv[0]
		var tile := float(kv[1]) if kv.size() > 1 else 2.0
		for c in holder.get_children():
			c.queue_free()
		var m := ShipMaterials.surface(kind, Color.WHITE, tile)
		_plane(holder, Vector2(4, 80), Vector3(0, 0, -40), Vector3(0, 0, 0), m)                   # floor
		_plane(holder, Vector2(4, 80), Vector3(0, 3, -40), Vector3(180, 0, 0), m)                 # ceiling
		_plane(holder, Vector2(3, 80), Vector3(-2, 1.5, -40), Vector3(0, 0, -90), m)              # left wall
		_plane(holder, Vector2(3, 80), Vector3(2, 1.5, -40), Vector3(0, 0, 90), m)                # right wall
		for k in frames:
			cam.rotation_degrees = Vector3(-3.0, -(step * k), 0)
			for i in (8 if k == 0 else (6 if taa else 3)):
				await process_frame
			root.get_texture().get_image().save_png("%s/%s_%02d.png" % [out, kind, k])
		print("probe ", kind)
	quit()
