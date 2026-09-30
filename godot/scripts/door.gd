extends Node3D
## Two-leaf sliding door (leaf_l / leaf_r nodes come from the Blender GLB).
## Opens when the player is near and blocks movement while closed.

const OPEN_DIST := 1.0
const SPEED := 3.2

var locked := false
var _l: Node3D
var _r: Node3D
var _l0 := Vector3.ZERO
var _r0 := Vector3.ZERO
var _amount := 0.0
var _target := 0.0
var _shape: CollisionShape3D
var _near := 0
var _snd: AudioStreamPlayer3D

func setup(is_locked: bool = false) -> void:
	locked = is_locked
	_l = find_child("leaf_l", true, false) as Node3D
	_r = find_child("leaf_r", true, false) as Node3D
	if _l:
		_l0 = _l.position
	if _r:
		_r0 = _r.position
	var body := StaticBody3D.new()
	body.collision_layer = 1
	body.collision_mask = 0
	_shape = CollisionShape3D.new()
	var bs := BoxShape3D.new()
	bs.size = Vector3(2.0, 2.6, 0.16)
	_shape.shape = bs
	_shape.position = Vector3(0, 1.3, 0)
	body.add_child(_shape)
	add_child(body)
	var area := Area3D.new()
	area.collision_layer = 0
	area.collision_mask = 2
	var ash := CollisionShape3D.new()
	var abox := BoxShape3D.new()
	abox.size = Vector3(3.6, 2.6, 3.8)
	ash.shape = abox
	ash.position = Vector3(0, 1.3, 0)
	area.add_child(ash)
	add_child(area)
	area.body_entered.connect(_on_enter)
	area.body_exited.connect(_on_exit)
	_snd = AudioStreamPlayer3D.new()
	_snd.stream = load("res://audio/door.wav")
	_snd.unit_size = 6.0
	_snd.max_distance = 22.0
	_snd.volume_db = -6.0
	_snd.position = Vector3(0, 1.3, 0)
	add_child(_snd)
	set_process(false)

func _on_enter(_b: Node3D) -> void:
	_near += 1
	if not locked:
		request(true)

func _on_exit(_b: Node3D) -> void:
	_near = maxi(0, _near - 1)
	if _near == 0:
		request(false)

func request(open: bool) -> void:
	if (1.0 if open else 0.0) != _target and is_inside_tree():
		_snd.pitch_scale = randf_range(0.95, 1.05)
		_snd.play()
	_target = 1.0 if open else 0.0
	set_process(true)

func is_open() -> bool:
	return _amount > 0.35

func _process(delta: float) -> void:
	_amount = move_toward(_amount, _target, delta * SPEED)
	if _l:
		_l.position = _l0 + Vector3(-OPEN_DIST * _amount, 0, 0)
	if _r:
		_r.position = _r0 + Vector3(OPEN_DIST * _amount, 0, 0)
	_shape.set_deferred("disabled", _amount > 0.35)
	if is_equal_approx(_amount, _target):
		set_process(false)
