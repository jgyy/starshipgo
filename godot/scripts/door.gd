extends Node3D
## Two-leaf sliding door (leaf_l / leaf_r nodes come from the Blender GLB).
## Opens when the player is within ~1 m of the door plane and blocks movement while closed.
## The collider, trigger and leaf travel are derived from the door model, not hard-coded.

const SPEED := 3.2
const TRIGGER_DEPTH := 2.2          # total depth of the trigger volume across the door plane (1.1 m each side)

var _l: Node3D
var _r: Node3D
var _l0 := Vector3.ZERO
var _r0 := Vector3.ZERO
var _travel := 1.0
var _amount := 0.0
var _target := 0.0
var _shape: CollisionShape3D
var _near := 0
var _snd: AudioStreamPlayer3D

func setup() -> void:
	_l = find_child("leaf_l", true, false) as Node3D
	_r = find_child("leaf_r", true, false) as Node3D
	if _l:
		_l0 = _l.position
	if _r:
		_r0 = _r.position
	# door extents from the leaf meshes (door space)
	var bb := _leaf_bounds()
	var width := clampf(bb.size.x, 1.0, 4.0)
	var height := clampf(bb.size.y, 2.0, 3.6)
	_travel = maxf(width * 0.5, 0.4)
	var body := StaticBody3D.new()
	body.collision_layer = 1
	body.collision_mask = 0
	_shape = CollisionShape3D.new()
	var bs := BoxShape3D.new()
	bs.size = Vector3(width, height, 0.16)
	_shape.shape = bs
	_shape.position = Vector3(0, height * 0.5, 0)
	body.add_child(_shape)
	add_child(body)
	var area := Area3D.new()
	area.collision_layer = 0
	area.collision_mask = 2
	var ash := CollisionShape3D.new()
	var abox := BoxShape3D.new()
	abox.size = Vector3(width + 0.6, height, TRIGGER_DEPTH)
	ash.shape = abox
	ash.position = Vector3(0, height * 0.5, 0)
	area.add_child(ash)
	add_child(area)
	area.body_entered.connect(_on_enter)
	area.body_exited.connect(_on_exit)
	_snd = AudioStreamPlayer3D.new()
	_snd.stream = load("res://audio/door.wav")
	_snd.unit_size = 6.0
	_snd.max_distance = 22.0
	_snd.volume_db = -6.0
	_snd.position = Vector3(0, height * 0.5, 0)
	add_child(_snd)
	set_process(false)

## Union of the leaf meshes' bounding boxes in the door's own space.
func _leaf_bounds() -> AABB:
	var out := AABB()
	var first := true
	for leaf in [_l, _r]:
		if leaf == null:
			continue
		var stack: Array = [[leaf, leaf.transform]]
		while stack.size() > 0:
			var it: Array = stack.pop_back()
			var n: Node3D = it[0]
			var xf: Transform3D = it[1]
			if n is MeshInstance3D and (n as MeshInstance3D).mesh != null:
				var a: AABB = xf * (n as MeshInstance3D).get_aabb()
				out = a if first else out.merge(a)
				first = false
			for c in n.get_children():
				if c is Node3D:
					stack.append([c, xf * (c as Node3D).transform])
	if first:
		out = AABB(Vector3(-1.0, 0.0, -0.1), Vector3(2.0, 2.6, 0.2))
	return out

func _on_enter(_b: Node3D) -> void:
	_near += 1
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

func _process(delta: float) -> void:
	_amount = move_toward(_amount, _target, delta * SPEED)
	if _l:
		_l.position = _l0 + Vector3(-_travel * _amount, 0, 0)
	if _r:
		_r.position = _r0 + Vector3(_travel * _amount, 0, 0)
	_shape.set_deferred("disabled", _amount > 0.35)
	if is_equal_approx(_amount, _target):
		set_process(false)
