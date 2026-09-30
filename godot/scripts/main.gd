extends Node3D
## Entry point: builds environment, ship, player and HUD.
##   godot --path godot                          play
##   godot --path godot -- --tour=/tmp/shots     render the camera tour from ship.json and quit

var builder: ShipBuilder
var player: CharacterBody3D
var hud: CanvasLayer
var _room_id := ""
var _acc := 0.0

func _ready() -> void:
	_make_environment()
	builder = ShipBuilder.new()
	builder.name = "Ship"
	add_child(builder)
	builder.load_data()
	builder.build()
	player = load("res://scripts/player.gd").new()
	player.name = "Player"
	add_child(player)
	var sp: Dictionary = builder.ship["spawn"]
	player.global_position = Vector3(sp["pos"][0], sp["pos"][1], sp["pos"][2])
	player.look_at_yaw_pitch(deg_to_rad(sp.get("yaw", 0.0)), 0.0)
	hud = load("res://scripts/hud.gd").new()
	add_child(hud)
	hud.map.ship = builder.ship
	hud.map.player = player
	player.interact_prompt.connect(hud.set_prompt)
	for l in builder.lifts:
		l.deck_changed.connect(func(_d): hud.flash_fade())
	var tour := _tour_dir()
	if tour != "":
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		_run_tour.call_deferred(tour)

func _tour_dir() -> String:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--tour="):
			return a.substr(7)
	return ""

func _process(delta: float) -> void:
	_acc += delta
	if _acc < 0.25:
		return
	_acc = 0.0
	var p := player.global_position
	for r in builder.ship["rooms"]:
		var rc: Array = r["rect"]
		if p.x >= rc[0] and p.x <= rc[2] and p.z >= rc[1] and p.z <= rc[3]:
			var y0 := 0.0
			for d in builder.ship["decks"]:
				if int(d["id"]) == int(r["deck"]):
					y0 = float(d["y"])
			if p.y >= y0 - 0.5 and p.y <= y0 + float(r.get("height", 3.4)):
				if r["id"] != _room_id:
					_room_id = r["id"]
					var dn := ""
					for d in builder.ship["decks"]:
						if int(d["id"]) == int(r["deck"]):
							dn = "DECK %d - %s" % [int(d["id"]), d["name"]]
					hud.show_room(r["name"], dn)
				return

func _make_environment() -> void:
	var env := Environment.new()
	env.background_mode = Environment.BG_SKY
	var sky := Sky.new()
	var pm := PanoramaSkyMaterial.new()
	pm.panorama = load("res://textures/sky/stars.png")
	sky.sky_material = pm
	env.sky = sky
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.86, 0.88, 0.95)
	env.ambient_light_energy = 0.5
	env.reflected_light_source = Environment.REFLECTION_SOURCE_DISABLED
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.tonemap_exposure = 1.0
	env.ssao_enabled = true
	env.ssao_radius = 1.4
	env.ssao_intensity = 2.2
	env.ssao_power = 1.6
	env.glow_enabled = true
	env.glow_intensity = 0.9
	env.glow_bloom = 0.08
	env.glow_hdr_threshold = 1.1
	env.adjustment_enabled = true
	env.adjustment_saturation = 1.08
	env.adjustment_contrast = 1.05
	var we := WorldEnvironment.new()
	we.environment = env
	add_child(we)
	# distant planet and sun, visible through windows only (render layer 2)
	var planet := MeshInstance3D.new()
	var sm := SphereMesh.new()
	sm.radius = 420.0
	sm.height = 840.0
	sm.radial_segments = 96
	sm.rings = 48
	planet.mesh = sm
	var pmat := StandardMaterial3D.new()
	pmat.albedo_texture = load("res://textures/sky/planet.png")
	pmat.roughness = 1.0
	pmat.rim_enabled = true
	pmat.rim = 0.4
	pmat.rim_tint = 0.8
	planet.material_override = pmat
	planet.layers = 2
	planet.position = Vector3(-330, -190, -1100)
	planet.rotation_degrees = Vector3(20, 40, 0)
	add_child(planet)
	var sun := DirectionalLight3D.new()
	sun.light_cull_mask = 2
	sun.light_energy = 2.4
	sun.light_color = Color(1.0, 0.95, 0.85)
	sun.rotation_degrees = Vector3(-18, -125, 0)
	add_child(sun)

func _run_tour(dir: String) -> void:
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(1.0).timeout
	var only := ""
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--only="):
			only = a.substr(7)
	for cam in builder.ship.get("cameras", []):
		if only != "" and not (cam["name"] in only.split(",")):
			continue
		var pos: Array = cam["pos"]
		player.global_position = Vector3(pos[0], pos[1] - 1.62, pos[2])
		player.velocity = Vector3.ZERO
		player.look_at_yaw_pitch(deg_to_rad(cam.get("yaw", 0.0)), deg_to_rad(cam.get("pitch", 0.0)))
		hud.show_room(cam.get("title", cam["name"]), cam.get("subtitle", ""))
		hud.help_label.visible = false
		for i in 10:
			await get_tree().process_frame
		var img := get_viewport().get_texture().get_image()
		var path := "%s/%s.png" % [dir, cam["name"]]
		img.save_png(path)
		print("shot ", path)
	if only != "":
		get_tree().quit()
		return
	# deck map screenshots
	hud.map.visible = true
	for d in builder.ship["decks"]:
		player.global_position = Vector3(0, float(d["y"]) + 0.1, 0)
		await get_tree().process_frame
		await get_tree().process_frame
		var im := get_viewport().get_texture().get_image()
		im.save_png("%s/map_deck%d.png" % [dir, int(d["id"])])
	get_tree().quit()
