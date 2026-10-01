extends SceneTree
## Headless UI test:  godot --headless --path godot -s res://tests/ui_test.gd
## 1. ray-vs-quad / ray-vs-box math, 2. screen discovery (every screen_* prop registered and mapped to an app),
## 3. look-at selection, 4. ShipState world effects (alert lights, door lock, hangar field, destination, jump),
## 5. every application is instantiated, refreshed, ticked and driven with synthetic input (button / slider / tab /
## list / text events), 6. real mouse clicks through the viewport on alert, star map and galley, 7. terminal open/close
## and player lock.  Script errors print "SCRIPT ERROR" - CI greps the log for it in addition to the exit code.

var failures: Array[String] = []
var b: ShipBuilder
var st: ShipState
var term: Terminal
var player: CharacterBody3D

func ok(cond: bool, msg: String) -> void:
	if not cond:
		failures.append(msg)
		printerr("FAIL: ", msg)

func _initialize() -> void:
	_run.call_deferred()

func _finish() -> void:
	if failures.is_empty():
		print("UI TEST PASSED")
		quit(0)
	else:
		for f in failures:
			printerr("FAIL: ", f)
		quit(1)

func _run() -> void:
	root.size = Vector2i(1280, 720)           # headless windows default to 64x64: lay the UI out like a real one
	_test_math()
	b = ShipBuilder.new()
	b.use_probes = false
	root.add_child(b)
	b.load_data()
	b.build()
	_test_registry()
	st = ShipState.new()
	st.name = "ShipState"
	root.add_child(st)
	st.bind_world(b)
	st.jump_seconds = 0.0
	player = load("res://scripts/player.gd").new()
	root.add_child(player)
	term = Terminal.new()
	root.add_child(term)
	term.bind(st)
	await process_frame
	_test_lookat()
	_test_state_effects()
	await _test_terminal_and_player()
	await _test_all_apps()
	await _test_clicks()
	await _test_computer()
	_finish()

# ------------------------------------------------------------------ 1. math
func _test_math() -> void:
	var c := Vector3(0, 1, 0)
	var n := Vector3(0, 0, 1)
	var u := Vector3(1, 0, 0)
	var v := Vector3(0, 1, 0)
	var t := ScreenRegistry.ray_quad(Vector3(0, 1, 2), Vector3(0, 0, -1), c, n, u, v, 0.3, 0.2)
	ok(absf(t - 2.0) < 1e-4, "ray_quad straight hit distance (got %f)" % t)
	ok(ScreenRegistry.ray_quad(Vector3(0.5, 1, 2), Vector3(0, 0, -1), c, n, u, v, 0.3, 0.2) < 0.0, "ray_quad misses outside the half-width")
	ok(ScreenRegistry.ray_quad(Vector3(0.45, 1, 2), Vector3(0, 0, -1), c, n, u, v, 0.3, 0.2, 0.2) > 0.0, "ray_quad margin widens the quad")
	ok(ScreenRegistry.ray_quad(Vector3(0, 1, -2), Vector3(0, 0, 1), c, n, u, v, 0.3, 0.2) < 0.0, "ray_quad rejects the back face")
	ok(ScreenRegistry.ray_quad(Vector3(0, 1, 2), Vector3(0, 1, 0), c, n, u, v, 0.3, 0.2) < 0.0, "ray_quad rejects a parallel ray")
	ok(ScreenRegistry.ray_quad(Vector3(0, 1, -2), Vector3(0, 0, -1), c, n, u, v, 0.3, 0.2) < 0.0, "ray_quad rejects a quad behind the ray")
	var tilt := Vector3(0, 1, 1).normalized()          # quad tilted 45 degrees: normal and v rotate together
	var v2 := Vector3(0, 1, -1).normalized()
	ok(ScreenRegistry.ray_quad(Vector3(0, 1, 3), Vector3(0, 0, -1), c, tilt, u, v2, 0.3, 0.3) > 0.0, "ray_quad hits a tilted quad")
	var box := Transform3D(Basis.from_euler(Vector3(0, PI * 0.25, 0)), Vector3(0, 1, 0))
	ok(ScreenRegistry.ray_box(Vector3(0, 1, 5), Vector3(0, 0, -1), box, Vector3(0.5, 0.5, 0.5)) > 0.0, "ray_box hits a rotated box")
	ok(ScreenRegistry.ray_box(Vector3(2, 1, 5), Vector3(0, 0, -1), box, Vector3(0.5, 0.5, 0.5)) < 0.0, "ray_box misses beside the box")
	ok(ScreenRegistry.ray_box(Vector3(0, 1, 0), Vector3(0, 0, -1), box, Vector3(0.5, 0.5, 0.5)) == 0.0, "ray_box from inside returns 0")

# ------------------------------------------------------------------ 2. discovery
func _test_registry() -> void:
	var reg := b.screen_registry
	var expected := 0
	var props_with := 0
	var machine_props := 0
	for r in b.ship["rooms"]:
		for p in r.get("props", []):
			var s: Array = reg.model_screens.get(p["m"], [])
			if not s.is_empty():
				props_with += 1
				expected += s.size()
			elif b.catalog.has(p["m"]) and (b.catalog[p["m"]].get("category", "") in AppCatalog.MACHINE_CATS):
				machine_props += 1
	var screens := 0
	for rec in reg.records:
		if rec["kind"] == "screen":
			screens += 1
	ok(expected > 100, "ship has many screens (%d)" % expected)
	ok(screens == expected, "every placed screen is registered: %d of %d" % [screens, expected])
	ok(reg.props_with_screens == props_with, "props with screens %d vs %d" % [reg.props_with_screens, props_with])
	ok(reg.props_machine >= machine_props * 0.9, "machine data cards registered (%d vs %d)" % [reg.props_machine, machine_props])
	var sm := reg.summary()
	ok(int(sm["unmapped"]) == 0, "no screen maps to an unknown app: %s" % str(sm))
	var known := AppCatalog.known_ids()
	var textures := {}
	for rec in reg.records:
		ok(rec["app"] in known and AppCatalog.has_script(rec["app"]), "record %s has a real app, got '%s'" % [rec["model"], rec["app"]])
		if rec["kind"] == "screen":
			textures[rec["tex"]] = true
			ok(float(rec["hu"]) > 0.002 and float(rec["hv"]) > 0.002, "screen %s has a size" % rec["model"])
			ok(absf((rec["normal"] as Vector3).length() - 1.0) < 1e-3, "screen %s normal is unit" % rec["model"])
	for tex in textures.keys():
		for room_id in ["bridge", "eng", "medbay", ""]:
			var app := AppCatalog.resolve("x", "console", tex, room_id, "")
			ok(app in known and AppCatalog.has_script(app), "texture %s in room '%s' resolves to an app (%s)" % [tex, room_id, app])
	for tex in AppCatalog.TEXTURE_MAP.keys():
		ok(AppCatalog.texture_map()[tex] in known, "texture_map entry %s -> known app" % tex)
	for a in AppCatalog.APPS.keys():
		ok(AppCatalog.has_script(a), "app script exists: " + a)
	print("registry: %d screens on %d props, %d machine cards, textures %s" % [screens, props_with, reg.props_machine, str(textures.keys())])

# ------------------------------------------------------------------ 3. selection by looking
func _test_lookat() -> void:
	var reg := b.screen_registry
	var rec: Dictionary = {}
	for r in reg.records:
		if r["kind"] == "screen" and float(r["hu"]) > 0.15:
			rec = r
			break
	ok(not rec.is_empty(), "found a screen record for the look test")
	if rec.is_empty():
		return
	var c: Vector3 = rec["center"]
	var n: Vector3 = rec["normal"]
	var eye := c + n * 1.4
	var look := Transform3D(Basis.looking_at(c - eye, Vector3.UP), eye)
	var got := reg.update(look, rec["room"], b.room_adj, null)
	ok(not got.is_empty() and got["model"] == rec["model"], "looking at a screen selects its prop")
	var away := Transform3D(Basis.looking_at(-(c - eye), Vector3.UP), eye)
	var none := reg.update(away, rec["room"], b.room_adj, null)
	ok(none.is_empty() or none["model"] != rec["model"] or none["room"] != rec["room"] or none["center"] != rec["center"], "looking away drops the target")
	var far_eye := c + n * 6.0
	var far := Transform3D(Basis.looking_at(c - far_eye, Vector3.UP), far_eye)
	ok(reg.update(far, rec["room"], b.room_adj, null).get("center", Vector3.ZERO) != rec["center"], "target beyond 3 m is ignored")
	var behind_eye := c - n * 1.4
	var behind := Transform3D(Basis.looking_at(c - behind_eye, Vector3.UP), behind_eye)
	ok(reg.update(behind, rec["room"], b.room_adj, null).get("center", Vector3.ZERO) != rec["center"], "back of a screen is not selectable")
	reg.current = {}

# ------------------------------------------------------------------ 4. world effects
func _test_state_effects() -> void:
	ok(st.doors.size() == b.doors.size() and st.doors.size() > 20, "ShipState bound %d doors" % st.doors.size())
	var lights := get_nodes_in_group("ship_lights")
	ok(lights.size() > 50, "lights joined group ship_lights (%d)" % lights.size())
	var l0 := lights[0] as Light3D
	var base_c := l0.light_color
	var base_e := l0.light_energy
	st.set_alert("red")
	ok(st.alert == "red" and l0.light_color != base_c, "red alert tints the lights")
	st.set_alert("yellow")
	ok(l0.light_color != base_c and absf(l0.light_energy - base_e * 0.92) < 0.01, "yellow alert tints the lights amber")
	st.set_alert("green")
	ok(l0.light_color.is_equal_approx(base_c) and is_equal_approx(l0.light_energy, base_e), "green alert restores the lights")
	ok(not st.set_alert("purple"), "unknown alert level rejected")
	# red alert auto-locks, leaving red releases them
	var before := st.locked_count()
	st.set_alert("red")
	ok(st.locked_count() > before, "red alert seals sensitive rooms (%d locked)" % st.locked_count())
	st.set_alert("green")
	ok(st.locked_count() == before, "leaving red alert releases the auto-locked doors")
	# door lock reaches door.gd
	var idx := st.find_doors("brig")
	ok(not idx.is_empty(), "find_doors('brig')")
	st.set_door_locked(idx[0], true)
	var d: Node = st.doors[idx[0]]
	ok(d.get("locked") == true, "door node is locked")
	d.call("request", true)
	ok(is_equal_approx(float(d.get("_target")), 0.0), "locked door refuses to open")
	st.set_door_locked(idx[0], false)
	d.call("request", true)
	ok(is_equal_approx(float(d.get("_target")), 1.0), "unlocked door opens again")
	d.call("request", false)
	# hangar
	ok(b.hangar_fields.size() >= 1, "hangar force field registered")
	st.set_hangar_field(false)
	var hf: Dictionary = b.hangar_fields[0]
	ok(not (hf["mesh"] as Node3D).visible and (hf["shape"] as CollisionShape3D).disabled, "hangar field off hides the plane and its collider")
	st.set_hangar_field(true)
	ok((hf["mesh"] as Node3D).visible and not (hf["shape"] as CollisionShape3D).disabled, "hangar field on shows plane and collider")
	# navigation
	var here := st.current_system
	ok(st.set_destination("kepler_x"), "destination accepted")
	ok(st.destination == "kepler_x" and st.route.size() >= 2 and st.eta_days() > 0.0, "route and ETA computed (%s)" % st.eta_text())
	ok(st.hud_line().contains("KEPLER"), "HUD line shows the destination: " + st.hud_line())
	ok(not st.set_destination("nowhere"), "unknown system rejected")
	ok(st.jump(), "jump starts")
	ok(st.current_system == "kepler_x" and st.visited.has("kepler_x") and not st.in_transit, "jump updates the current system (%s -> %s)" % [here, st.current_system])
	ok(st.destination == "", "destination cleared on arrival")
	ok(not st.jump("kepler_x"), "cannot jump to where you are")
	st.set_scram(true)
	ok(not st.jump("sol"), "no jump with the reactor scrammed")
	st.set_scram(false)
	ok(st.supply() > 0.0 and st.total_load() > 0.0, "power numbers exist")
	st.reactor["output"] = 20.0
	ok(st.brownout(), "low reactor output browns out")
	st.reactor["output"] = 85.0
	var n0 := st.messages.size()
	ok(st.dispense("x", "Test", 0.0) and st.messages.size() > n0, "dispense logs a message")
	ok(not st.dispense("x", "Costly", 1e6), "dispense refuses when poor")

# ------------------------------------------------------------------ 7. terminal + player
func _test_terminal_and_player() -> void:
	ok(not term.is_open, "terminal starts closed")
	ok(term.open_app("computer", {"label": "Test console"}), "terminal opens an app")
	await process_frame
	ok(term.is_open and player.ui_locked, "opening the terminal locks the player")
	ok(term.title_label.text.contains("TEST CONSOLE") and term.title_label.text.contains("COMPUTER"), "title shows host label and app: " + term.title_label.text)
	var ev := InputEventAction.new()
	ev.action = "ui_cancel"
	ev.pressed = true
	Input.parse_input_event(ev)
	await process_frame
	await process_frame
	if term.is_open:
		term.close()
		failures.append("ui_cancel did not close the terminal")
	ok(not term.is_open and not player.ui_locked, "closing the terminal releases the player")
	term.open_app("alert", {"label": "Alert board"})
	await process_frame
	await process_frame
	var e2 := InputEventAction.new()
	e2.action = "interact"
	e2.pressed = true
	Input.parse_input_event(e2)
	await process_frame
	await process_frame
	ok(not term.is_open, "E closes the terminal")
	if term.is_open:
		term.close()

# ------------------------------------------------------------------ 5. every app
func _walk(n: Node, out: Array) -> void:
	out.append(n)
	for c in n.get_children():
		_walk(c, out)

func _drive(app: AppBase) -> int:
	var nodes: Array = []
	_walk(app, nodes)
	var acted := 0
	for n in nodes:
		if n is TabContainer:
			var tc := n as TabContainer
			for i in tc.get_tab_count():
				tc.current_tab = i
				app.refresh()
				app.tick(0.05)
				acted += 1
	for n in nodes:
		if n is HSlider:
			var s := n as HSlider
			s.value = s.min_value + (s.max_value - s.min_value) * 0.4
			acted += 1
	for n in nodes:
		if n is Tree:
			var t := n as Tree
			var r := t.get_root()
			if r != null and r.get_child_count() > 0:
				var it := r.get_child(0)
				it.select(0)
				t.item_selected.emit()
				acted += 1
	for n in nodes:
		if n is LineEdit:
			(n as LineEdit).text = "te"
			(n as LineEdit).text_changed.emit("te")
			(n as LineEdit).text_submitted.emit("te")
			(n as LineEdit).text = ""
			(n as LineEdit).text_changed.emit("")
			acted += 1
		elif n is OptionButton:
			var ob := n as OptionButton
			if ob.item_count > 1:
				ob.select(1)
				ob.item_selected.emit(1)
				ob.select(0)
				ob.item_selected.emit(0)
				acted += 1
	for n in nodes:
		if n is CheckButton or (n is Button and (n as Button).toggle_mode):
			var bt := n as Button
			bt.button_pressed = not bt.button_pressed
			acted += 1
		elif n is Button and not (n is OptionButton) and n.name != "CloseButton":
			(n as Button).pressed.emit()
			acted += 1
	return acted

func _test_all_apps() -> void:
	var reg := b.screen_registry
	for id in AppCatalog.APPS.keys():
		st.jump_seconds = 0.0
		var host := {"label": "Test Console", "room": "bridge", "room_name": "Bridge", "tex": "", "model": "console_helm", "category": "console"}
		for r in reg.records:
			if r["app"] == id:
				host = r.duplicate()
				break
		ok(term.open_app(id, host), "app opens: " + id)
		var app := term.app
		ok(app != null and app.app_id == id and app.get_child_count() > 0, "app %s built widgets" % id)
		if app == null:
			continue
		for i in 5:
			st.sim(0.2)
			app.tick(0.1)
			app.refresh()
		await process_frame
		var acted := _drive(app)
		for i in 3:
			st.sim(0.2)
			app.tick(0.1)
			app.refresh()
		await process_frame
		ok(acted >= 1 or id in ["clock", "holo"], "app %s accepted synthetic input (%d actions)" % [id, acted])
		print("  app %-12s ok (%d controls driven, host '%s')" % [id, acted, host.get("label", "")])
		term.close()
		# keep the world sane for the next app
		st.set_alert("green")
		st.lock_all(false)
		st.set_hangar_field(true)
		st.set_scram(false)
		st.reactor["output"] = 85.0
		for bus in st.buses:
			bus["on"] = true
		st.destination = ""
		st.current_system = "luyten"
		st.in_transit = false
		await process_frame

# ------------------------------------------------------------------ 6. real mouse clicks
func _find_button(app: Node, text: String) -> Button:
	var nodes: Array = []
	_walk(app, nodes)
	for n in nodes:
		if n is Button and (n as Button).text == text and (n as Button).is_visible_in_tree():
			return n
	return null

func _click(c: Control) -> void:
	var p := c.get_global_rect().get_center()
	for pressed in [true, false]:
		var e := InputEventMouseButton.new()
		e.button_index = MOUSE_BUTTON_LEFT
		e.position = p
		e.global_position = p
		e.pressed = pressed
		e.button_mask = MOUSE_BUTTON_MASK_LEFT if pressed else 0
		root.push_input(e, true)

func _test_clicks() -> void:
	# alert: click RED, then GREEN
	term.open_app("alert", {"label": "Alert board"})
	await process_frame
	await process_frame
	await process_frame
	var red := _find_button(term.app, "RED ALERT")
	ok(red != null, "alert app has a RED ALERT button")
	if red != null:
		_click(red)
		await process_frame
		ok(st.alert == "red", "mouse click on RED ALERT sets red alert (alert=%s)" % st.alert)
		var green := _find_button(term.app, "GREEN ALERT")
		_click(green)
		await process_frame
		ok(st.alert == "green", "mouse click on GREEN ALERT restores green")
	term.close()
	# security: select a door row, click LOCK SELECTED
	term.open_app("security", {"label": "Security"})
	await process_frame
	await process_frame
	var tree: Tree = null
	var nodes: Array = []
	_walk(term.app, nodes)
	for n in nodes:
		if n is Tree and (n as Tree).get_column_title(1) == "DOOR":
			tree = n
	ok(tree != null, "security app has a door table")
	if tree != null:
		tree.get_root().get_child(2).select(0)
		tree.item_selected.emit()
		var lock := _find_button(term.app, "LOCK SELECTED")
		_click(lock)
		await process_frame
		ok(st.door_locked(2), "mouse click on LOCK SELECTED locks door 2")
		_click(_find_button(term.app, "UNLOCK SELECTED"))
		await process_frame
		ok(not st.door_locked(2), "mouse click on UNLOCK SELECTED unlocks door 2")
	term.close()
	# docking: hangar toggle
	term.open_app("docking", {"label": "Hangar"})
	await process_frame
	await process_frame
	var ff := _find_button(term.app, "FORCE FIELD: ONLINE")
	ok(ff != null, "docking has the force field button")
	if ff != null:
		_click(ff)
		await process_frame
		ok(not st.hangar_field_on, "mouse click on the force field button turns it off")
		_click(_find_button(term.app, "FORCE FIELD: OFFLINE"))
		await process_frame
		ok(st.hangar_field_on, "and on again")
	term.close()
	# starmap: click a system, PLOT COURSE, JUMP
	st.current_system = "luyten"
	st.destination = ""
	term.open_app("starmap", {"label": "Star table"})
	await process_frame
	await process_frame
	await process_frame
	var sm: AppBase = term.app
	var cv: Control = null
	nodes.clear()
	_walk(sm, nodes)
	for n in nodes:
		if n is UIW.Canvas:
			cv = n
			break
	sm.tick(0.01)
	await process_frame
	var proj: Dictionary = sm.get("_proj")
	ok(proj.has("kepler_x"), "star map projected Kepler Gate")
	if proj.has("kepler_x") and cv != null:
		var local: Vector2 = proj["kepler_x"]["p"]
		var gp := cv.get_global_rect().position + local
		for pressed in [true, false]:
			var e := InputEventMouseButton.new()
			e.button_index = MOUSE_BUTTON_LEFT
			e.position = gp
			e.global_position = gp
			e.pressed = pressed
			root.push_input(e, true)
		await process_frame
		ok(sm.get("selected") == "kepler_x", "clicking a star selects it (selected=%s)" % str(sm.get("selected")))
		_click(_find_button(sm, "PLOT COURSE"))
		await process_frame
		ok(st.destination == "kepler_x", "PLOT COURSE sets the destination")
		_click(_find_button(sm, "JUMP"))
		await process_frame
		ok(st.current_system == "kepler_x", "JUMP moves the ship (now at %s)" % st.current_system)
		# drag rotates, wheel zooms
		var y0: float = sm.get("yaw")
		var mm := InputEventMouseMotion.new()
		mm.position = gp
		mm.relative = Vector2(40, 0)
		mm.button_mask = MOUSE_BUTTON_MASK_LEFT
		root.push_input(mm, true)
		await process_frame
		ok(not is_equal_approx(float(sm.get("yaw")), y0), "mouse drag rotates the star map")
		var z0: float = sm.get("zoom")
		var wh := InputEventMouseButton.new()
		wh.button_index = MOUSE_BUTTON_WHEEL_UP
		wh.pressed = true
		wh.position = gp
		wh.global_position = gp
		root.push_input(wh, true)
		await process_frame
		ok(float(sm.get("zoom")) > z0, "wheel zooms the star map")
	term.close()
	# galley: pick the first item and dispense
	term.open_app("galley", {"label": "Replicator"})
	await process_frame
	await process_frame
	var gt: Tree = null
	nodes.clear()
	_walk(term.app, nodes)
	for n in nodes:
		if n is Tree and (n as Tree).get_column_title(0) == "ITEM":
			gt = n
	ok(gt != null and gt.get_root() != null and gt.get_root().get_child_count() > 0, "galley menu has items")
	if gt != null and gt.get_root() != null and gt.get_root().get_child_count() > 0:
		gt.get_root().get_child(0).select(0)
		gt.item_selected.emit()
		var n0 := st.dispensed
		_click(_find_button(term.app, "DISPENSE"))
		await process_frame
		ok(st.dispensed == n0 + 1, "DISPENSE dispenses (served %d)" % st.dispensed)
	term.close()
	st.set_alert("green")

# ------------------------------------------------------------------ computer command line
func _test_computer() -> void:
	term.open_app("computer", {"label": "Computer"})
	await process_frame
	var cmp = term.app
	for c in ["help", "status", "map", "time", "locate bridge", "locate Okoro", "specs reactor", "specs reactor_fusion_core_reactor", "lore", "lore kepler", "lore warp",
			"log", "log list", "log 1", "list systems", "list rooms", "list doors", "list apps", "list models", "list models console", "alert", "warp 7.5"]:
		var r: String = cmp.exec(c)
		ok(r != "" and not r.begins_with("Unknown command"), "computer '%s' prints something: %s" % [c, r.substr(0, 40)])
	ok(cmp.exec("bogus").begins_with("Unknown command"), "computer rejects unknown commands")
	cmp.exec("alert red")
	ok(st.alert == "red", "computer: alert red")
	cmp.exec("alert green")
	ok(st.alert == "green", "computer: alert green")
	cmp.exec("lock brig")
	var bi := st.find_doors("brig")
	ok(st.door_locked(bi[0]), "computer: lock brig")
	cmp.exec("unlock brig")
	ok(not st.door_locked(bi[0]), "computer: unlock brig")
	cmp.exec("lockall")
	ok(st.locked_count() == st.doors.size(), "computer: lockall")
	cmp.exec("unlockall")
	ok(st.locked_count() == 0, "computer: unlockall")
	cmp.exec("hangar off")
	ok(not st.hangar_field_on, "computer: hangar off")
	cmp.exec("hangar on")
	ok(st.hangar_field_on, "computer: hangar on")
	st.current_system = "luyten"
	st.in_transit = false
	cmp.exec("dest helios")
	ok(st.destination == "helios_reach", "computer: dest helios -> %s" % st.destination)
	cmp.exec("jump")
	ok(st.current_system == "helios_reach", "computer: jump arrives (%s)" % st.current_system)
	ok(cmp.exec("specs reactor_fusion_core_reactor").contains("reactor"), "computer: specs card")
	# typing through the real LineEdit
	var nodes: Array = []
	_walk(cmp, nodes)
	for n in nodes:
		if n is LineEdit:
			(n as LineEdit).text = "alert yellow"
			(n as LineEdit).text_submitted.emit("alert yellow")
	ok(st.alert == "yellow", "typing a command in the line edit runs it")
	st.set_alert("green")
	term.close()
