extends SceneTree
## Headless smoke test:  godot --headless --path godot -s res://tests/smoke_test.gd
## Builds the entire ship from data and checks that the 1000 components are all present.

func _init() -> void:
	var failures: Array[String] = []
	var b := ShipBuilder.new()
	root.add_child(b)
	b.load_data()
	if b.catalog.size() != 1000:
		failures.append("catalog has %d models, expected 1000" % b.catalog.size())
	var missing := 0
	for id in b.catalog:
		if not ResourceLoader.exists("res://" + b.catalog[id]["file"]):
			missing += 1
	if missing > 0:
		failures.append("%d GLB files are not imported/loadable" % missing)
	b.build()
	var used: int = b.stats["models_used"].size()
	if used != b.catalog.size():
		failures.append("ship uses %d/%d models" % [used, b.catalog.size()])
	if b.doors.size() < 25:
		failures.append("too few doors: %d" % b.doors.size())
	if b.stats["props"] < 3000:
		failures.append("too few props: %d" % b.stats["props"])
	var mesh_count := 0
	var stack: Array[Node] = [b]
	while stack.size() > 0:
		var n: Node = stack.pop_back()
		if n is MeshInstance3D:
			mesh_count += 1
		stack.append_array(n.get_children())
	print("meshes in ship: ", mesh_count)
	if failures.is_empty():
		print("SMOKE TEST PASSED")
		quit(0)
	else:
		for f in failures:
			printerr("FAIL: ", f)
		quit(1)
