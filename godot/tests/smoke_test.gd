extends SceneTree
## Headless smoke test:  godot --headless --path godot -s res://tests/smoke_test.gd
## Builds the whole ship from data and checks its structure (rooms, hull, doors, stairs, batching).

func _init() -> void:
	var failures: Array[String] = []
	var b := ShipBuilder.new()
	root.add_child(b)
	b.load_data()
	if b.catalog.size() < 1000:
		failures.append("catalog has %d models, expected at least 1000" % b.catalog.size())
	var missing := 0
	for id in b.catalog:
		if not ResourceLoader.exists("res://" + b.catalog[id]["file"]):
			missing += 1
	for id in b.arch:
		if not ResourceLoader.exists("res://" + b.arch[id]["file"]):
			missing += 1
	if missing > 0:
		failures.append("%d GLB files are not imported/loadable" % missing)
	if b.arch.size() < 4:
		failures.append("architectural models missing (stair flight, guard, sign, hull fascia): %d" % b.arch.size())
	b.build()
	if b.ship["rooms"].size() < 40:
		failures.append("too few rooms: %d" % b.ship["rooms"].size())
	if b.doors.size() < 25:
		failures.append("too few doors: %d" % b.doors.size())
	for d in b.doors:
		if d.find_child("leaf_l", true, false) == null or d.find_child("leaf_r", true, false) == null:
			failures.append("door model without leaf_l / leaf_r nodes: " + d.name)
	var want_flights: int = 4 * (b.ship["decks"].size() - 1)
	if b.stats["stairs"] != want_flights:
		failures.append("expected %d stair flights (2 towers x runs x 2 flights), got %d" % [want_flights, b.stats["stairs"]])
	if b.stats["props"] < 600:
		failures.append("too few props: %d" % b.stats["props"])
	if b.stats["multimeshes"] >= b.stats["props"]:
		failures.append("props are not batched (%d multimeshes for %d props)" % [b.stats["multimeshes"], b.stats["props"]])
	var hull_decks: int = b.ship.get("hull", {}).size()
	if hull_decks != 5:
		failures.append("hull outlines missing: %d" % hull_decks)
	for r in b.ship["rooms"]:
		if not b.room_nodes.has(r["id"]) or not b.room_content.has(r["id"]):
			failures.append("room %s was not built" % r["id"])
	var mesh_count := 0
	var lifts := 0
	var stack: Array[Node] = [b]
	while stack.size() > 0:
		var n: Node = stack.pop_back()
		if n is MeshInstance3D or n is MultiMeshInstance3D:
			mesh_count += 1
		if n.name.to_lower().begins_with("lift") or "turbolift" in n.name.to_lower():
			lifts += 1
		stack.append_array(n.get_children())
	if lifts > 0:
		failures.append("%d lift nodes still in the ship" % lifts)
	# room graph: every room reachable from the spawn room
	var spawn: Dictionary = b.ship["spawn"]
	var start := b.room_at(Vector3(spawn["pos"][0], spawn["pos"][1] + 0.9, spawn["pos"][2]))
	if start == "":
		failures.append("spawn point is not inside any room")
	else:
		var seen := {start: true}
		var q: Array = [start]
		while q.size() > 0:
			var cur: String = q.pop_back()
			for nb in b.room_adj.get(cur, []):
				if not seen.has(nb):
					seen[nb] = true
					q.append(nb)
		if seen.size() != b.ship["rooms"].size():
			failures.append("room graph: %d of %d rooms reachable from %s" % [seen.size(), b.ship["rooms"].size(), start])
	print("ship: %d rooms, %d props in %d multimeshes, %d colliders, %d mesh nodes" % [
		b.ship["rooms"].size(), b.stats["props"], b.stats["multimeshes"], b.stats["colliders"], mesh_count])
	if failures.is_empty():
		print("SMOKE TEST PASSED")
		quit(0)
	else:
		for f in failures:
			printerr("FAIL: ", f)
		quit(1)
