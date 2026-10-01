extends Node3D
## Entry point: builds environment, ship, player and HUD.
##   godot --path godot                          play
##   godot --path godot -- --tour=/tmp/shots     render the camera tour from ship.json and quit
##   godot --path godot -- --bench=/tmp/b.json   fly through the tour cameras and write frame-time statistics
## Options: --hq (volumetric fog, 4x MSAA, full SSAO), --no-probes, --no-fog, --no-culling, --only=a,b (tour),
##          --occlusion / --no-occlusion (force raycast occlusion culling on / off, see _occlusion)

var builder: ShipBuilder
var player: CharacterBody3D
var hud: CanvasLayer
var _room_id := ""
var _acc := 0.0
var _hq := false
var _sun: DirectionalLight3D

func _arg(prefix: String) -> String:
	for a in OS.get_cmdline_user_args():
		if a.begins_with(prefix):
			return a.substr(prefix.length())
	return ""

func _flag(name: String) -> bool:
	return name in OS.get_cmdline_user_args()

## Raycast occlusion culling (~3.7x fewer draw calls) runs on Embree.  Official Godot builds bundle Embree; distro
## builds that link the system library can segfault inside rtcIntersect16 as soon as one occluder exists (Arch
## godot 4.7.2 + embree 4.4.1), so they default to off.  The project setting stays off for the same reason.
func _occlusion() -> bool:
	if _flag("--occlusion"):
		return true
	if _flag("--no-occlusion"):
		return false
	return Engine.get_version_info().get("build", "") == "official"

func _ready() -> void:
	var t0 := Time.get_ticks_msec()
	_hq = _flag("--hq")
	_make_environment()
	builder = ShipBuilder.new()
	builder.name = "Ship"
	builder.use_probes = not _flag("--no-probes")
	builder.use_culling = not _flag("--no-culling")
	builder.use_occluders = _occlusion()
	get_viewport().use_occlusion_culling = builder.use_occluders
	add_child(builder)
	builder.load_data()
	if builder.ship.get("rooms", []).is_empty():
		printerr("no ship data - run tools/layout/generate_ship.py and godot --import first")
		get_tree().quit(1)
		return
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
	_make_audio()
	_make_ui()
	var load_ms := Time.get_ticks_msec() - t0
	if _flag("--screen-scan"):
		_screen_scan()
		return
	var ui_shot := _arg("--ui-shot=")
	if ui_shot != "":
		_interactive = false
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		_run_ui_shots.call_deferred(ui_shot, _arg("--ui-out="))
		return
	var bench := _arg("--bench=")
	if bench != "":
		_interactive = false
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		var b := Node.new()
		b.set_script(load("res://scripts/bench.gd"))
		b.set_meta("load_ms", load_ms)
		add_child(b)
		b.run.call_deferred(self, player, builder.ship["cameras"], bench)
		return
	var tour := _arg("--tour=")
	if tour != "":
		_interactive = false
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		_run_tour.call_deferred(tour)

# ------------------------------------------------------------------ interactive screens (see docs/UI.md)
var state: ShipState
var terminal: Terminal
var _interactive := true
var _scan_acc := 0.0

func _make_ui() -> void:
	state = ShipState.new()
	state.name = "ShipState"
	add_child(state)
	state.bind_world(builder)
	terminal = Terminal.new()
	terminal.name = "Terminal"
	add_child(terminal)
	terminal.bind(state)
	builder.screen_registry.attach_highlight(builder)
	state.changed.connect(_update_status)
	state.alert_changed.connect(func(_l: String) -> void: _update_status())
	_update_status()

func _update_status() -> void:
	hud.set_status(state.hud_line(), state.alert)

## Ten times a second: which screen is the player looking at (analytic, no colliders).
func _scan_screens() -> void:
	var reg := builder.screen_registry
	if terminal.is_open or _room_id == "":
		hud.set_target({})
		reg.show_highlight({})
		return
	var space := player.get_world_3d().direct_space_state
	var rec := reg.update(player.camera.global_transform, _room_id, builder.room_adj, space)
	hud.set_target(rec, AppCatalog.title_of(rec.get("app", "")) if not rec.is_empty() else "")
	reg.show_highlight(rec)

func _unhandled_input(event: InputEvent) -> void:
	if _interactive and event.is_action_pressed("interact") and not terminal.is_open:
		var rec := builder.screen_registry.current
		if not rec.is_empty():
			terminal.open_host(rec)
			get_viewport().set_input_as_handled()

func _screen_scan() -> void:
	var s := builder.screen_registry.summary()
	print("screen scan: %d screens on %d props, %d machine data cards, %d records, %d unmapped" % [
		s["screens"], s["props_with_screens"], s["machines"], s["records"], s["unmapped"]])
	print("by app: ", s["by_app"])
	get_tree().quit(1 if int(s["unmapped"]) > 0 else 0)

## --ui-shot=starmap,nav --ui-out=/tmp/ui : render each app full screen to PNG (docs/screenshots/ui_<app>.png) and quit.
func _run_ui_shots(ids: String, out: String) -> void:
	if out == "":
		out = "user://ui"
	DirAccess.make_dir_recursive_absolute(out)
	await get_tree().create_timer(0.5).timeout
	player.set_physics_process(false)
	for id in ids.split(","):
		var host := {"label": "Console", "room": "bridge", "room_name": "Bridge", "tex": ""}
		for r in builder.screen_registry.records:
			if r["app"] == id:
				host = r.duplicate()
				break
		terminal.open_app(id, host)
		if terminal.app != null and terminal.app.has_method("demo"):
			terminal.app.call("demo")
		for i in 14:
			await get_tree().process_frame
		await get_tree().create_timer(0.4).timeout
		var img := get_viewport().get_texture().get_image()
		if img == null or img.is_empty():
			printerr("no rendered image (is a renderer available?)")
			get_tree().quit(1)
			return
		var path := "%s/ui_%s.png" % [out, id]
		if img.save_png(path) != OK:
			printerr("cannot write ", path)
			get_tree().quit(1)
			return
		print("shot ", path)
		terminal.close()
	get_tree().quit()

var _hum: AudioStreamPlayer
var _rumble: AudioStreamPlayer
var _mix_tween: Tween

func _loop(path: String) -> AudioStreamWAV:
	var s := (load(path) as AudioStreamWAV).duplicate() as AudioStreamWAV
	s.loop_mode = AudioStreamWAV.LOOP_FORWARD
	s.loop_begin = 0
	var bytes_per_frame := 1
	match s.format:
		AudioStreamWAV.FORMAT_16_BITS: bytes_per_frame = 2
		AudioStreamWAV.FORMAT_8_BITS: bytes_per_frame = 1
	if s.stereo:
		bytes_per_frame *= 2
	s.loop_end = s.data.size() / bytes_per_frame
	return s

func _make_audio() -> void:
	_hum = AudioStreamPlayer.new()
	_hum.stream = _loop("res://audio/ambient_hum.wav")
	_hum.volume_db = -17.0
	add_child(_hum)
	_hum.play()
	_rumble = AudioStreamPlayer.new()
	_rumble.stream = _loop("res://audio/engine_rumble.wav")
	_rumble.volume_db = -40.0
	add_child(_rumble)
	_rumble.play()

## Engineering areas are louder and rumble; command areas are quiet.
func _mix_for(dept: String) -> void:
	var hum := -17.0
	var rum := -40.0
	match dept:
		"engineering": hum = -14.0; rum = -14.0
		"cargo": hum = -15.0; rum = -22.0
		"life": hum = -13.0; rum = -26.0
		"command": hum = -21.0
		"crew": hum = -20.0
		"medical", "science": hum = -19.0
	if _mix_tween:
		_mix_tween.kill()                              # a new room cancels the previous crossfade
	_mix_tween = create_tween().set_parallel(true)
	_mix_tween.tween_property(_hum, "volume_db", hum, 1.5)
	_mix_tween.tween_property(_rumble, "volume_db", rum, 1.5)

func _process(delta: float) -> void:
	if _interactive and terminal != null:
		_scan_acc += delta
		if _scan_acc >= 0.1:
			_scan_acc = 0.0
			_scan_screens()
	_acc += delta
	if _acc < ShipBuilder.CULL_TICK:
		return
	_acc = 0.0
	var p := player.global_position + Vector3(0, 0.9, 0)
	var here := builder.room_at(p)
	if state != null and here != "":
		state.player_room = here
	builder.update_culling(p)
	if here != "" and here != _room_id:
		_room_id = here
		for r in builder.ship["rooms"]:
			if r["id"] == here:
				var dn := ""
				for d in builder.ship["decks"]:
					if int(d["id"]) == int(r["deck"]):
						dn = "DECK %d - %s" % [int(d["id"]), d["name"]]
				hud.show_room(r["name"], dn)
				_mix_for(r.get("dept", ""))
				hud.set_prompt("STAIRS  -  walk up or down the flights to change deck" if here.begins_with("tower") else "")
				break

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
	# Performance: a cheap depth haze replaces the volumetric fog unless --hq is given.
	if _hq and not _flag("--no-fog"):
		env.volumetric_fog_enabled = true
		env.volumetric_fog_density = 0.006
		env.volumetric_fog_albedo = Color(0.85, 0.9, 1.0)
		env.volumetric_fog_length = 36.0
		env.volumetric_fog_ambient_inject = 0.4
	elif not _flag("--no-fog"):
		env.fog_enabled = true
		env.fog_light_color = Color(0.62, 0.68, 0.8)
		env.fog_density = 0.004
		env.fog_sky_affect = 0.0
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
	var vp := get_viewport()
	if _hq:
		vp.msaa_3d = Viewport.MSAA_4X
		vp.screen_space_aa = Viewport.SCREEN_SPACE_AA_DISABLED
	else:
		vp.msaa_3d = Viewport.MSAA_DISABLED
		vp.screen_space_aa = Viewport.SCREEN_SPACE_AA_FXAA
	# distant planet and sun, visible through windows only (render layer 2)
	var planet := MeshInstance3D.new()
	var sm := SphereMesh.new()
	sm.radius = 420.0
	sm.height = 840.0
	sm.radial_segments = 64
	sm.rings = 32
	planet.mesh = sm
	var pmat := StandardMaterial3D.new()
	pmat.albedo_texture = load("res://textures/sky/planet.png")
	pmat.roughness = 1.0
	pmat.rim_enabled = true
	pmat.rim = 0.4
	pmat.rim_tint = 0.8
	planet.material_override = pmat
	planet.layers = 2
	planet.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	planet.position = Vector3(-330, -190, -1100)
	planet.rotation_degrees = Vector3(20, 40, 0)
	add_child(planet)
	var sun := DirectionalLight3D.new()
	_sun = sun
	sun.light_cull_mask = 2
	sun.light_energy = 1.5
	sun.light_color = Color(1.0, 0.95, 0.85)
	sun.rotation_degrees = Vector3(-18, -125, 0)
	add_child(sun)

func _run_tour(dir: String) -> void:
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(1.0).timeout
	var only := _arg("--only=")
	player.set_physics_process(false)
	for cam in builder.ship.get("cameras", []):
		if only != "" and not (cam["name"] in only.split(",")):
			continue          # --only=maps skips every camera and renders just the deck maps
		var pos: Array = cam["pos"]
		player.global_position = Vector3(pos[0], pos[1] - 1.62, pos[2])
		player.velocity = Vector3.ZERO
		player.look_at_yaw_pitch(deg_to_rad(cam.get("yaw", 0.0)), deg_to_rad(cam.get("pitch", 0.0)))
		player.camera.fov = cam.get("fov", 78.0)
		_sun.shadow_enabled = cam.get("exterior", false)       # the sun only needs shadows when the hull is in view
		if cam.get("exterior", false):
			builder.show_all_rooms()
			hud.show_room(cam.get("title", cam["name"]), cam.get("subtitle", ""))
		else:
			builder._current_room = ""
			builder.update_culling(player.global_position + Vector3(0, 0.9, 0))
			hud.show_room(cam.get("title", cam["name"]), cam.get("subtitle", ""))
		hud.help_label.visible = false
		for i in 10:
			await get_tree().process_frame
		var img := get_viewport().get_texture().get_image()
		if img == null or img.is_empty():
			printerr("no rendered image (is a renderer available?) - aborting the tour")
			get_tree().quit(1)
			return
		var path := "%s/%s.png" % [dir, cam["name"]]
		if img.save_png(path) != OK:
			printerr("cannot write ", path)
			get_tree().quit(1)
			return
		print("shot ", path)
	if only != "" and only != "maps":
		get_tree().quit()
		return
	# deck map screenshots
	hud.map.visible = true
	for d in builder.ship["decks"]:
		player.global_position = Vector3(0, float(d["y"]) + 0.1, 1.8)
		await get_tree().process_frame
		await get_tree().process_frame
		var im := get_viewport().get_texture().get_image()
		im.save_png("%s/map_deck%d.png" % [dir, int(d["id"])])
	get_tree().quit()
