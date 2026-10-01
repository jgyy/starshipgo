extends SceneTree
## Shimmer probe: renders the same view N times with the camera yawed by tiny sub-pixel steps and writes the
## frames as PNG (HUD hidden).  tools/quality/flicker_metric.py turns them into a number.
##
##   xvfb-run -a -s "-screen 0 1280x720x24" godot --path godot --rendering-driver vulkan --resolution 960x540 \
##       -s res://tests/flicker_probe.gd -- --out=/tmp/fl --cams=01_bridge,08_mess,17_eng,20_cargo --frames=8 --step=0.02
##
## Needs a real (or software) renderer; it cannot run with --headless.

func _arg(prefix: String, def: String) -> String:
	for a in OS.get_cmdline_user_args():
		if a.begins_with(prefix):
			return a.substr(prefix.length())
	return def

func _initialize() -> void:
	_run.call_deferred()

func _run() -> void:
	var out := _arg("--out=", "/tmp/flicker")
	var cams := _arg("--cams=", "01_bridge,08_mess,17_eng,20_cargo").split(",")
	var frames := int(_arg("--frames=", "8"))
	var step := float(_arg("--step=", "0.02"))
	DirAccess.make_dir_recursive_absolute(out)
	var main: Node3D = load("res://scenes/Main.tscn").instantiate()
	root.add_child(main)
	for i in 5:
		await process_frame
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
			for i in (14 if k == 0 else 3):
				await process_frame
			var img := root.get_texture().get_image()
			img.save_png("%s/%s_%02d.png" % [out, cam["name"], k])
		print("probe ", cam["name"])
	quit()
