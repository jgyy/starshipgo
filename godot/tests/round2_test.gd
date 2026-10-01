extends SceneTree
## Regression tests for the round-2 Godot defects (ledger: docs/bugs/round2/godot.json, ids G0xx):
##   godot --headless --path godot -s res://tests/round2_test.gd
## Each check names the defect it keeps fixed.  No renderer needed.

var failures: Array[String] = []
var b: ShipBuilder

func _initialize() -> void:
	_run.call_deferred()

func _check(ok: bool, msg: String) -> void:
	if not ok:
		failures.append(msg)

func _run() -> void:
	b = ShipBuilder.new()
	b.use_probes = false
	root.add_child(b)
	b.load_data()
	b.build()
	_test_prism_normals()
	_test_hud()
	_test_deck_map()
	_test_deck_order()
	_test_map_labels()
	_test_audio_loops()
	_test_bench()
	_test_tour_plan()
	_test_textures()
	_test_shell_clearances()
	_test_capture_rules()
	await _test_window_aspect()
	await _test_player_bob()
	if failures.is_empty():
		print("ROUND2 TEST PASSED")
		quit(0)
	else:
		for f in failures:
			printerr("FAIL: ", f)
		quit(1)

# G001: every side face of a shell prism must point away from the prism (both polygon windings)
func _test_prism_normals() -> void:
	for pts in [
			[Vector2(0, 0), Vector2(1, 0), Vector2(1, 1), Vector2(0, 1)],
			[Vector2(0, 0), Vector2(0, 1), Vector2(1, 1), Vector2(1, 0)]]:
		var sh := ShipBuilder.Shell.new()
		sh.prism(pts, 0.0, 1.0, "s", "t", "b", false, false)
		var v: PackedVector3Array = sh.surf["s"]["v"]
		var n: PackedVector3Array = sh.surf["s"]["n"]
		var inward := 0
		for t in range(0, v.size(), 3):
			var cen := (v[t] + v[t + 1] + v[t + 2]) / 3.0
			if n[t].dot(cen - Vector3(0.5, 0.5, 0.5)) < 0.0:
				inward += 1
			# the winding must agree with the stored normal (front faces are clockwise in Godot)
			var wn := -(v[t + 1] - v[t]).cross(v[t + 2] - v[t]).normalized()
			_check(wn.dot(n[t]) > 0.99, "G001: prism side winding disagrees with its normal")
		_check(inward == 0, "G001: %d of %d prism side triangles face into the prism" % [inward, v.size() / 3])
	# and in the built ship: the room-facing face of the north wall of 'core' (z = -12.85) must face +z
	var node: Node3D = b.room_nodes["core"]
	for c in node.get_children():
		if c is MeshInstance3D and c.name == "Mesh_wall":
			var arr: Array = (c as MeshInstance3D).mesh.surface_get_arrays(0)
			var v2: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
			var n2: PackedVector3Array = arr[Mesh.ARRAY_NORMAL]
			var seen := false
			for t in range(0, v2.size(), 3):
				if absf(v2[t].z + 12.85) < 0.002 and absf(v2[t + 1].z + 12.85) < 0.002 and absf(v2[t + 2].z + 12.85) < 0.002:
					seen = true
					_check(n2[t].z > 0.99, "G001: core north wall inner face normal is %s, want +z" % n2[t])
			_check(seen, "G001: no wall face found at z = -12.85 in core")

# G004: the help text must be inside the window
func _test_hud() -> void:
	var hud: CanvasLayer = load("res://scripts/hud.gd").new()
	root.add_child(hud)
	var vp := root.get_visible_rect().size
	var r := Rect2(hud.help_label.global_position, hud.help_label.size)
	_check(r.position.x >= 0.0 and r.position.y >= 0.0 and r.end.x <= vp.x and r.end.y <= vp.y,
		"G004: help label %s outside the %s viewport" % [r, vp])
	# G020: the banner / prompt / crosshair must not print over the deck map
	hud.show_room("Test room", "DECK 9")
	hud.set_prompt("STAIRS")
	hud.map.visible = true
	_check(not hud.room_label.visible and not hud.deck_label.visible and not hud.prompt_label.visible and not hud.crosshair.visible and not hud.help_label.visible,
		"G005: HUD banner / prompt / crosshair / help are still visible over the open deck map")
	hud.map.visible = false
	_check(hud.room_label.visible and hud.crosshair.visible and hud.help_label.visible, "G005: the HUD must come back when the map closes")
	hud.set_prompt("STAIRS  -  walk up or down the flights")
	hud.show_banner("Exterior", "STARSHIPGO")
	_check(hud.prompt_label.text == "", "G015: a tour banner must clear the previous camera's stair prompt")
	hud.queue_free()

# G006 / G007: stairs hint and scale of the deck map
func _test_deck_map() -> void:
	var decks: Array = b.ship["decks"]
	var top := 0
	var bottom := 0
	for d in decks:
		if float(d["y"]) >= float(decks[top]["y"]):
			top = decks.find(d)
		if float(d["y"]) <= float(decks[bottom]["y"]):
			bottom = decks.find(d)
	_check(DeckMap.stair_hint(decks, int(decks[top]["id"])) == "DN", "G006: top deck must say STAIRS DN, got '%s'" % DeckMap.stair_hint(decks, int(decks[top]["id"])))
	_check(DeckMap.stair_hint(decks, int(decks[bottom]["id"])) == "UP", "G006: bottom deck must say STAIRS UP")
	var five: Array = []
	for i in 5:
		five.append({"id": i + 1, "y": 16.0 - 4.0 * i})
	_check(DeckMap.stair_hint(five, 3) == "UP/DN", "G006: middle deck of five must say UP/DN")
	_check(DeckMap.stair_hint(five, 5) == "UP" and DeckMap.stair_hint(five, 1) == "DN", "G006: end decks of five are labelled wrongly")
	_check(DeckMap.map_scale(Vector2(100, 80), Vector2(0, 0), Vector2(10, 70), 90.0) > 0.0, "G007: deck map scale must stay positive in a tiny window")

# G020 / G021: the stair test and the smoke test must follow the data, not a three-deck literal
func _test_deck_order() -> void:
	var five: Array = []
	for i in 5:
		five.append({"id": i + 1, "y": 16.0 - 4.0 * i})
	_check(ShipBuilder.deck_order_bottom_to_top(five) == [5, 4, 3, 2, 1], "G020/G021: deck order of five decks is %s" % [ShipBuilder.deck_order_bottom_to_top(five)])
	_check(ShipBuilder.deck_order_bottom_to_top(b.ship["decks"]) == [4, 3, 2, 1, 0], "G020/G021: deck order of this ship")
	_check(ShipBuilder.flights_in(b.ship) == b.stats["stairs"], "G020/G021: flights_in disagrees with the built flights")

# G022: the ambient loops must span the whole clip whatever format the importer chose
func _test_audio_loops() -> void:
	for path in ["res://audio/ambient_hum.wav", "res://audio/engine_rumble.wav"]:
		var s := load(path) as AudioStreamWAV
		var frames: int = MainScript.loop_frames(s)
		_check(frames == int(round(s.get_length() * s.mix_rate)) and frames > 100000, "G022: %s loop_end %d frames, clip is %.2f s at %d Hz" % [path, frames, s.get_length(), s.mix_rate])
		if s.format == AudioStreamWAV.FORMAT_16_BITS:
			_check(frames == s.data.size() / 2, "G022: 16-bit mono loop_end must equal the sample count")
		_check(s.format != AudioStreamWAV.FORMAT_QOA, "G022: %s is still QOA-compressed (stale import: delete godot/audio/*.wav.import and run godot --import)" % path)

# G008: room labels that do not fit are ellipsized, not clipped mid-word
func _test_map_labels() -> void:
	var font := ThemeDB.fallback_font
	var fit: Dictionary = DeckMap.fit_label(font, "Starboard Stair Tower", 40.0, 13, 7)
	_check(font.get_string_size(fit["text"], HORIZONTAL_ALIGNMENT_LEFT, -1, fit["size"]).x <= 40.0, "G008: label '%s' still wider than its room" % fit["text"])
	_check(String(fit["text"]).ends_with("…") and fit["size"] == 7, "G008: a too-long label must shrink to the minimum and end with an ellipsis, got %s" % fit)
	var ok: Dictionary = DeckMap.fit_label(font, "Brig", 200.0, 13, 7)
	_check(ok["text"] == "Brig" and ok["size"] == 13, "G008: a short label must be left alone")

# G009 / G010: benchmark statistics and report
func _test_bench() -> void:
	var st: Dictionary = BenchRun.summarize(PackedFloat32Array())
	_check(st["median"] == 0.0 and st["worst"] == 0.0, "G009: empty bench summary")
	st = BenchRun.summarize(PackedFloat32Array([3.0, 1.0, 2.0]))
	_check(is_equal_approx(st["median"], 2.0) and is_equal_approx(st["worst"], 3.0) and is_equal_approx(st["mean"], 2.0), "G009: bench summary wrong: %s" % st)
	_check(not BenchRun.write_report("/nonexistent_dir_xyz/out.json", {}), "G010: write_report must return false, not crash, for an unwritable path")

# G011 / G012 / G013: tour option handling
func _test_tour_plan() -> void:
	var cams := [{"name": "01_a"}, {"name": "02_b"}, {"name": "X1"}]
	var all: Dictionary = MainScript.tour_plan("", cams)
	_check(all["cams"].size() == 3 and all["maps"], "G011: no filter must render every camera and the maps")
	var mixed: Dictionary = MainScript.tour_plan("01_a,maps", cams)
	_check(mixed["cams"].size() == 1 and mixed["maps"], "G011: --only=01_a,maps must render the camera AND the maps")
	var only_maps: Dictionary = MainScript.tour_plan("maps", cams)
	_check(only_maps["cams"].is_empty() and only_maps["maps"], "G011: --only=maps renders no cameras")
	var bad: Dictionary = MainScript.tour_plan("01_a,nope", cams)
	_check(bad["unknown"] == ["nope"], "G012: unknown camera names must be reported")
	_check(MainScript.usage_error(PackedStringArray(["--tour="])) != "", "G013: --tour= without a path must be a usage error")
	_check(MainScript.usage_error(PackedStringArray(["--bench=/tmp/x.json", "--tour=/tmp/x"])) == "", "G013: valid options must not be an error")

# G002 / G010: every texture a shell surface or a prop uses must have a mip chain
func _test_textures() -> void:
	var missing: Array[String] = []
	var checked := 0
	for kind in ["wall_trim", "deck_plate", "ceiling", "hull_dark", "hull_panel", "hull_plate", "carpet"]:
		var m: StandardMaterial3D = ShipMaterials.surface(kind)
		for tex in [m.albedo_texture, m.normal_texture, m.roughness_texture]:
			if tex == null:
				continue
			checked += 1
			if not (tex as Texture2D).get_image().has_mipmaps():
				missing.append(String((tex as Texture2D).resource_path))
	_check(checked > 0, "G002: no surface textures found")
	_check(missing.is_empty(), "G002: %d surface textures have no mipmaps (shimmer at distance): %s" % [missing.size(), missing.slice(0, 4)])
	var props_missing := 0
	var props_checked := 0
	var seen := {}
	for id in ["seat_captain_command_chair", "display_deck_plan_board", "noticeboard_duty_roster_display", "safety_evac_route_map"]:
		for mm: Dictionary in b._meshes_of(id):
			var mesh: Mesh = mm["mesh"]
			for si in mesh.get_surface_count():
				var mat := mesh.surface_get_material(si)
				if not (mat is BaseMaterial3D):
					continue
				for slot in TextureFix.SLOTS:                      # the prop screens / decals are EMISSION textures
					var tex: Variant = (mat as BaseMaterial3D).get(slot)
					if tex is Texture2D and not seen.has(tex):
						seen[tex] = true
						props_checked += 1
						if not (tex as Texture2D).get_image().has_mipmaps():
							props_missing += 1
	_check(props_checked >= 4, "G003: expected to find the prop screen textures, found %d" % props_checked)
	_check(props_missing == 0, "G003: %d of %d prop textures have no mipmaps" % [props_missing, props_checked])
	# the load-time repair for stale .import files (G002): forced conversion yields an ImageTexture with a mip chain
	var t: Texture2D = load("res://textures/surfaces/hull_panel_albedo.png")
	var fixed := TextureFix.with_mipmaps(t, false, true)
	_check(fixed is ImageTexture and fixed.get_image().has_mipmaps() and fixed.get_width() == t.get_width(), "G002: TextureFix did not produce a mipmapped copy")
	_check(not TextureFix.lacks_mipmaps(t), "G002: hull_panel_albedo.png is still imported without mipmaps - delete the stale *.png.import files and re-run godot --import")

# G023 / G031: clearances that keep the shell free of coplanar faces
func _test_shell_clearances() -> void:
	_check(ShipBuilder.CLAD_T < 0.115 or ShipBuilder.CLAD_T > 0.125, "G023: outer plating thickness must not equal the fascia belt depth (0.12)")
	_check(ShipBuilder.BELT_LIFT > 0.005, "G023: exterior belts must stand off the hull skin")
	_check(absf(ShipBuilder.WALL_T + ShipBuilder.GLOW_T - 0.162) > 0.002, "G031: ceiling glow strips must not sit in the plane of wall pipes")
	_check(absf(ShipBuilder.TRIM_T - 0.02) > 0.004, "G031: trim strips must not stand exactly 2 cm off the wall (props have 2 cm back plates)")

# G016: the game must fill windows of any shape (stretch aspect "keep" letterboxed a 1000x1000 window to 1000x562)
func _test_window_aspect() -> void:
	var before := root.size
	for sz in [Vector2i(1000, 1000), Vector2i(2560, 1080), Vector2i(640, 360)]:
		root.size = sz
		await process_frame
		await process_frame
		var vr := root.get_visible_rect().size
		_check(absf(vr.x / vr.y - float(sz.x) / float(sz.y)) < 0.01, "G016: a %s window gets a %s viewport (letterboxed)" % [sz, vr])
	root.size = before
	await process_frame

# G018: only the left button re-captures the pointer
func _test_capture_rules() -> void:
	var PlayerScript: GDScript = load("res://scripts/player.gd")
	var wheel := InputEventMouseButton.new()
	wheel.button_index = MOUSE_BUTTON_WHEEL_UP
	wheel.pressed = true
	var right := InputEventMouseButton.new()
	right.button_index = MOUSE_BUTTON_RIGHT
	right.pressed = true
	var left := InputEventMouseButton.new()
	left.button_index = MOUSE_BUTTON_LEFT
	left.pressed = true
	_check(not PlayerScript.wants_capture(wheel, Input.MOUSE_MODE_VISIBLE, false), "G018: the wheel must not re-capture the mouse")
	_check(not PlayerScript.wants_capture(right, Input.MOUSE_MODE_VISIBLE, false), "G018: a right click must not re-capture the mouse")
	_check(PlayerScript.wants_capture(left, Input.MOUSE_MODE_VISIBLE, false), "G018: a left click must re-capture the mouse")
	_check(not PlayerScript.wants_capture(left, Input.MOUSE_MODE_VISIBLE, true), "G018: no capture while the deck map is open")
	_check(not PlayerScript.wants_capture(left, Input.MOUSE_MODE_CAPTURED, false), "G018: already captured")

# G017: the head bob must not jump when walking starts / stops
func _test_player_bob() -> void:
	var floor_body := StaticBody3D.new()
	var cs := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(60, 1, 60)
	cs.shape = box
	cs.position = Vector3(0, -0.5 - 500.0, 0)         # far below the ship: this test has its own floor
	floor_body.add_child(cs)
	floor_body.collision_layer = 1
	root.add_child(floor_body)
	var p: CharacterBody3D = load("res://scripts/player.gd").new()
	root.add_child(p)
	p.global_position = Vector3(0, -500.0, 0)
	for i in 20:
		await physics_frame
	var worst := 0.0
	for cycle in 6:
		p.sim_move = Vector2(0, -1)                    # walk forward for a random-ish time, then stop for a while
		for i in 17 + cycle * 7:
			await physics_frame
		p.sim_move = Vector2.ZERO
		for i in 45:
			await physics_frame
		p.sim_move = Vector2(0, -1)
		var y_prev: float = p.head.position.y
		for i in 6:
			await physics_frame
			worst = maxf(worst, absf(p.head.position.y - y_prev))
			y_prev = p.head.position.y
		p.sim_move = Vector2.ZERO
		for i in 30:
			await physics_frame
	_check(worst < 0.006, "G017: the camera height jumped %.1f mm in one physics frame when walking started" % (worst * 1000.0))
	p.queue_free()
	floor_body.queue_free()
