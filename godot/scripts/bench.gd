class_name BenchRun
extends Node
## Flythrough benchmark:  godot --path godot --rendering-driver vulkan --resolution 960x540 -- --bench=/tmp/out.json
## Visits every interior tour camera, lets the renderer settle, then averages the frame time and draw statistics.

func run(main: Node, player: Node3D, cams: Array, out_path: String) -> void:
	var t_all := PackedFloat32Array()
	var per := []
	var visited := 0
	var dc_sum := 0
	var prim_sum := 0
	var obj_sum := 0
	for cam in cams:
		var pos: Array = cam["pos"]
		player.global_position = Vector3(pos[0], pos[1] - 1.62, pos[2])
		player.velocity = Vector3.ZERO
		player.set_physics_process(false)
		player.look_at_yaw_pitch(deg_to_rad(cam.get("yaw", 0.0)), deg_to_rad(cam.get("pitch", 0.0)))
		if cam.get("exterior", false):
			continue
		main.builder._current_room = ""
		main.builder.update_culling(player.global_position + Vector3(0, 0.9, 0))
		for i in 8:
			await get_tree().process_frame
		var ts := PackedFloat32Array()
		var dc := 0
		var pr := 0
		var ob := 0
		var n := 12
		for i in n:
			var t0 := Time.get_ticks_usec()
			await RenderingServer.frame_post_draw
			ts.append((Time.get_ticks_usec() - t0) / 1000.0)
			dc += RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME)
			pr += RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_PRIMITIVES_IN_FRAME)
			ob += RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_OBJECTS_IN_FRAME)
		var avg := 0.0
		for v in ts:
			avg += v
		avg /= n
		visited += 1
		per.append({"camera": cam["name"], "ms": snappedf(avg, 0.1), "draw_calls": dc / n, "primitives": pr / n, "objects": ob / n})
		t_all.append(avg)
		dc_sum += dc / n
		prim_sum += pr / n
		obj_sum += ob / n
	var st := summarize(t_all)
	var mean: float = st["mean"]
	var res := {
		"cameras": visited, "mean_frame_ms": snappedf(mean, 0.1), "median_frame_ms": snappedf(st["median"], 0.1),
		"worst_frame_ms": snappedf(st["worst"], 0.1), "mean_draw_calls": dc_sum / max(1, visited),
		"mean_primitives": prim_sum / max(1, visited), "mean_objects": obj_sum / max(1, visited),
		"static_mem_mb": snappedf(OS.get_static_memory_usage() / 1048576.0, 0.1),
		"nodes": int(Performance.get_monitor(Performance.OBJECT_NODE_COUNT)),
		"video_mem_mb": snappedf(Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED) / 1048576.0, 0.1),
		"load_ms": int(get_meta("load_ms", 0)),
		"renderer": RenderingServer.get_video_adapter_name(), "per_camera": per}
	if visited == 0:
		printerr("bench: no interior camera was visited (cameras=%d) - nothing to measure" % cams.size())
		get_tree().quit(1)
		return
	if not write_report(out_path, res):
		get_tree().quit(1)
		return
	print("BENCH mean=%.1f ms  median=%.1f  draw_calls=%d  prims=%d  objects=%d  nodes=%d  load=%d ms" % [
		mean, res["median_frame_ms"], res["mean_draw_calls"], res["mean_primitives"], res["mean_objects"], res["nodes"], res["load_ms"]])
	get_tree().quit()

## Writes the report; false (with a message) when the file cannot be created - FileAccess.open() returns null then, and the
## old code called store_string() on it.
static func write_report(out_path: String, res: Dictionary) -> bool:
	var f := FileAccess.open(out_path, FileAccess.WRITE)
	if f == null:
		printerr("bench: cannot write ", out_path, " (error ", FileAccess.get_open_error(), ")")
		return false
	f.store_string(JSON.stringify(res, "  "))
	f.close()
	return true

## mean / median / worst of the per-camera frame times; all zero for an empty list (the old code indexed sorted[-1] of an
## empty array and aborted when every camera was exterior or the camera list was empty).
static func summarize(t_all: PackedFloat32Array) -> Dictionary:
	if t_all.is_empty():
		return {"mean": 0.0, "median": 0.0, "worst": 0.0}
	var mean := 0.0
	for v in t_all:
		mean += v
	mean /= t_all.size()
	var sorted := Array(t_all)
	sorted.sort()
	return {"mean": mean, "median": sorted[sorted.size() / 2], "worst": sorted[-1]}
