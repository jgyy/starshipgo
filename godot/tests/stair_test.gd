extends SceneTree
## Walks the player up and down both stair towers with simulated input:
##   godot --headless --path godot -s res://tests/stair_test.gd
## Fails if the player cannot climb from Deck 4 (hold) to Deck 0 (sky) and back, or falls through a hole.

var b: ShipBuilder
var p: CharacterBody3D
var failures: Array[String] = []

func _initialize() -> void:
	_run.call_deferred()

func _run() -> void:
	b = ShipBuilder.new()
	root.add_child(b)
	b.load_data()
	b.use_probes = false
	b.build()
	p = load("res://scripts/player.gd").new()
	root.add_child(p)
	var up_order := ShipBuilder.deck_order_bottom_to_top(b.ship["decks"])
	var down_order := up_order.duplicate()
	down_order.reverse()
	for st in b.ship["stairs"]:
		await _climb(st, up_order)            # from the bottom deck to the top one
		await _climb(st, down_order)
	if failures.is_empty():
		print("STAIR TEST PASSED")
		quit(0)
	else:
		for f in failures:
			printerr("FAIL: ", f)
		quit(1)

func _dir(yaw_deg: float) -> Vector3:
	var y := deg_to_rad(yaw_deg)
	return Vector3(-sin(y), 0.0, -cos(y))

func _walk_to(target: Vector3, limit_s: float = 14.0) -> bool:
	var t := 0.0
	while t < limit_s:
		var d := Vector3(target.x - p.global_position.x, 0.0, target.z - p.global_position.z)
		if d.length() < 0.22:
			p.sim_move = Vector2.ZERO
			return true
		d = d.normalized()
		p.sim_move = Vector2(d.x, d.z)
		await physics_frame
		t += 1.0 / Engine.physics_ticks_per_second
	p.sim_move = Vector2.ZERO
	return false

func _climb(st: Dictionary, order: Array) -> void:
	var strip: Array = st["strip"]
	var sc := Vector3((strip[0] + strip[2]) * 0.5, 0.0, (strip[1] + strip[3]) * 0.5)
	var runs: Array = st["runs"]
	var decks := {}
	for d in b.ship["decks"]:
		decks[int(d["id"])] = float(d["y"])
	var up: bool = int(order[0]) > int(order[1])
	var seq: Array = []
	for i in order.size() - 1:
		var lo := maxi(int(order[i]), int(order[i + 1]))
		for r in runs:
			if int(r["deck_lo"]) == lo:
				seq.append(r)
	p.sim_move = Vector2.ZERO
	p.velocity = Vector3.ZERO
	var start_deck: int = order[0]
	p.global_position = Vector3(sc.x, decks[start_deck] + 0.15, sc.z)
	for i in 30:
		await physics_frame
	for r in seq:
		var fa: Dictionary = r["flights"][0]
		var fb: Dictionary = r["flights"][1]
		var pa := Vector3(fa["pos"][0], fa["pos"][1], fa["pos"][2])
		var pb := Vector3(fb["pos"][0], fb["pos"][1], fb["pos"][2])
		var da := _dir(fa["yaw"])
		var db := _dir(fb["yaw"])
		var wps: Array = []
		if up:
			wps = [pa - da * 0.8, pa + da * 3.4, Vector3(pa.x + da.x * 3.4, 0, pb.z), pb + db * 3.4, Vector3(sc.x, 0, pb.z)]
		else:
			wps = [Vector3(sc.x, 0, pb.z), pb + db * 3.4, Vector3(pa.x + da.x * 3.4, 0, pb.z), pa + da * 3.4, pa - da * 0.8, Vector3(sc.x, 0, pa.z)]
		for w in wps:
			var ok: bool = await _walk_to(w)
			if not ok:
				failures.append("%s: stuck going %s towards %s at %s" % [st["id"], "up" if up else "down", w, p.global_position])
				return
		for i in 20:
			await physics_frame
		var target_deck: int = int(r["deck_hi"]) if up else int(r["deck_lo"])
		var want: float = decks[target_deck]
		if absf(p.global_position.y - want) > 0.2 or not p.is_on_floor():
			failures.append("%s: after run %d->%d the player is at y=%.2f (wanted %.2f, on_floor=%s)" % [
				st["id"], int(r["deck_lo"]), int(r["deck_hi"]), p.global_position.y, want, p.is_on_floor()])
			return
		print("%s: %s to deck %d ok (y=%.2f)" % [st["id"], "up" if up else "down", target_deck, p.global_position.y])
