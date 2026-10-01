extends CharacterBody3D
## First-person controller: WASD + mouse look, sprint, flashlight.  Walks up and down the stair ramps.

const WALK_SPEED := 3.4
const SPRINT_SPEED := 6.0
const ACCEL := 14.0
const GRAVITY := 18.0

@export var mouse_sens := 0.0022       # radians per pixel
var head: Node3D
var camera: Camera3D
var flash: SpotLight3D
var sim_move: Variant = null          # Vector2 override used by the automated stair test (x = strafe, y = back)
var _bob := 0.0
var _pitch := 0.0
var _steps: Array[AudioStream] = []
var _step_player: AudioStreamPlayer
var _last_half := 0

func _ready() -> void:
	add_to_group("player")
	collision_layer = 2
	collision_mask = 1
	var cs := CollisionShape3D.new()
	var cap := CapsuleShape3D.new()
	cap.radius = 0.32
	cap.height = 1.75
	cs.shape = cap
	cs.position.y = 0.875
	add_child(cs)
	head = Node3D.new()
	head.position.y = 1.62
	add_child(head)
	camera = Camera3D.new()
	camera.fov = 78.0
	camera.near = 0.05
	camera.far = 2500.0
	head.add_child(camera)
	flash = SpotLight3D.new()
	flash.spot_range = 22.0
	flash.spot_angle = 30.0
	flash.spot_attenuation = 0.6
	flash.light_energy = 3.0
	flash.shadow_enabled = true
	flash.visible = false
	camera.add_child(flash)
	# stairs are collision ramps of ~33 degrees: keep walking speed constant on slopes and stay glued to them going down
	floor_max_angle = deg_to_rad(50.0)
	floor_snap_length = 0.55
	floor_constant_speed = true
	floor_stop_on_slope = true
	for i in range(1, 4):
		_steps.append(load("res://audio/footstep_%d.wav" % i))
	_step_player = AudioStreamPlayer.new()
	_step_player.volume_db = -9.0
	add_child(_step_player)
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT:
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE            # never keep the pointer hostage when the window loses focus

func _map_open() -> bool:
	var hud := get_tree().get_first_node_in_group("hud")
	return hud != null and hud.get("map") != null and (hud.get("map") as Control).visible

## A terminal overlay is open: no look, no movement, no flashlight; the pointer belongs to the UI.
var ui_locked := false

func set_ui_locked(v: bool) -> void:
	ui_locked = v
	if v:
		velocity.x = 0.0
		velocity.z = 0.0

func _unhandled_input(event: InputEvent) -> void:
	if ui_locked:
		return
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		rotate_y(-event.relative.x * mouse_sens)
		_pitch = clampf(_pitch - event.relative.y * mouse_sens, -1.5, 1.5)
		head.rotation.x = _pitch
	elif event is InputEventMouseButton and event.pressed and Input.mouse_mode != Input.MOUSE_MODE_CAPTURED and not _map_open():
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	elif event.is_action_pressed("ui_cancel"):
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	if event.is_action_pressed("flashlight"):
		flash.visible = not flash.visible

func look_at_yaw_pitch(yaw: float, pitch: float) -> void:
	rotation.y = yaw
	_pitch = pitch
	head.rotation.x = pitch

func _physics_process(delta: float) -> void:
	var inp: Vector2 = sim_move if sim_move != null else Input.get_vector("move_left", "move_right", "move_forward", "move_back")
	if ui_locked:
		inp = Vector2.ZERO
	var dir := (transform.basis * Vector3(inp.x, 0, inp.y)).normalized()
	var speed := SPRINT_SPEED if Input.is_action_pressed("sprint") and not ui_locked else WALK_SPEED
	var target := dir * speed
	velocity.x = move_toward(velocity.x, target.x, ACCEL * delta)
	velocity.z = move_toward(velocity.z, target.z, ACCEL * delta)
	if is_on_floor():
		velocity.y = -2.0           # presses into the ramp so floor snapping keeps contact on the way down
	else:
		velocity.y -= GRAVITY * delta
	move_and_slide()
	var moving := Vector2(velocity.x, velocity.z).length()
	if moving > 0.5 and is_on_floor():
		_bob += delta * moving * 1.9
		head.position.y = 1.62 + sin(_bob) * 0.028
		head.position.x = cos(_bob * 0.5) * 0.015
		var half := int(floorf(_bob / PI))
		if half != _last_half:
			_last_half = half
			_step_player.stream = _steps[randi() % _steps.size()]
			_step_player.pitch_scale = randf_range(0.9, 1.1)
			_step_player.play()
	else:
		head.position.y = lerpf(head.position.y, 1.62, delta * 8.0)
		head.position.x = lerpf(head.position.x, 0.0, delta * 8.0)
