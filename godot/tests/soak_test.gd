extends SceneTree
## Memory soak test: runs the real game scene and teleports the player through every tour camera for several laps
## (room changes, culling, audio crossfades, HUD tweens, deck map, flashlight), sampling the engine monitors per lap.
##   godot --path godot -s res://tests/soak_test.gd              (rendered: also watches video memory)
##   godot --headless --path godot -s res://tests/soak_test.gd   (objects / nodes / resources / static memory only)
## Fails if anything keeps growing once the first laps have warmed the caches up (first tweens, door sounds ...).

const LAPS := 6
const WARMUP_LAPS := 2
const MIN_FRAMES_PER_CAMERA := 4
const MIN_MS_PER_CAMERA := 260       # > ShipBuilder.CULL_TICK (200 ms) of REAL time: headless frames take ~2 ms, so counting
                                     # 20 frames (as this test did) was only ~40 ms and most stops never ran the room / culling update

const MONITORS := {
	"objects": Performance.OBJECT_COUNT,
	"resources": Performance.OBJECT_RESOURCE_COUNT,
	"nodes": Performance.OBJECT_NODE_COUNT,
	"orphans": Performance.OBJECT_ORPHAN_NODE_COUNT,
	"static_mb": Performance.MEMORY_STATIC,
	"video_mb": Performance.RENDER_VIDEO_MEM_USED,
}
# allowed growth between the end of the warm-up and the last lap: objects covers tweens that are mid-flight
# when the sample is taken; the memory figures cover allocator noise, not a trend
const SLACK := {"objects": 4, "resources": 0, "nodes": 0, "orphans": 0, "static_mb": 4.0, "video_mb": 8.0}

func _initialize() -> void:
	_run.call_deferred()

func _sample() -> Dictionary:
	var out := {}
	for k in MONITORS:
		var v: float = Performance.get_monitor(MONITORS[k])
		out[k] = v / 1048576.0 if k.ends_with("_mb") else v
	return out

func _run() -> void:
	var main: Node = load("res://scenes/Main.tscn").instantiate()
	root.add_child(main)
	await process_frame
	var player: CharacterBody3D = main.get("player")
	var hud: CanvasLayer = main.get("hud")
	if player == null:
		printerr("FAIL: main scene did not build (no ship data?)")
		quit(1)
		return
	var cams: Array = main.get("builder").ship.get("cameras", [])
	var samples: Array[Dictionary] = []
	var interior_stops := 0
	var room_hits := 0                  # stops where main._process had really moved the player into the camera's room
	for lap in LAPS:
		for cam in cams:
			var pos: Array = cam["pos"]
			player.global_position = Vector3(pos[0], pos[1] - 1.62, pos[2])
			player.velocity = Vector3.ZERO
			player.look_at_yaw_pitch(deg_to_rad(cam.get("yaw", 0.0)), 0.0)
			player.flash.visible = not player.flash.visible
			hud.map.visible = not hud.map.visible
			var t0 := Time.get_ticks_msec()
			var f := 0
			while f < MIN_FRAMES_PER_CAMERA or Time.get_ticks_msec() - t0 < MIN_MS_PER_CAMERA:
				await process_frame
				f += 1
			var rid: String = main.get("_room_id")
			if not cam.get("exterior", false):
				interior_stops += 1
				if rid == str(cam.get("room", "")):
					room_hits += 1
		var s := _sample()
		samples.append(s)
		print("lap %d  %s" % [lap + 1, s])
	var failures: Array[String] = []
	if room_hits < interior_stops * 0.9:
		failures.append("only %d of %d interior stops ran the room / culling update: the soak does not exercise it" % [room_hits, interior_stops])
	var first: Dictionary = samples[WARMUP_LAPS - 1]
	var last: Dictionary = samples[-1]
	for k in MONITORS:
		var grew: float = last[k] - first[k]
		if grew > SLACK[k]:
			failures.append("%s grew by %s between lap %d and lap %d (%s -> %s)" % [k, grew, WARMUP_LAPS, LAPS, first[k], last[k]])
	# tear the scene down before quitting so the engine's leak report at exit covers the game, not the test
	main.free()
	for i in 3:
		await process_frame
	if failures.is_empty():
		print("SOAK TEST PASSED")
		quit(0)
	else:
		for f in failures:
			printerr("FAIL: ", f)
		quit(1)
