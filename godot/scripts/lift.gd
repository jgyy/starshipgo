extends Area3D
## Turbolift car: while the player stands inside, keys 1..N pick the deck.

signal deck_changed(deck: int)

var decks: Array = []
var _player: Node3D

func setup(size: Vector3, deck_list: Array) -> void:
	decks = deck_list
	collision_layer = 0
	collision_mask = 2
	var cs := CollisionShape3D.new()
	var bs := BoxShape3D.new()
	bs.size = size
	cs.shape = bs
	add_child(cs)
	body_entered.connect(func(b: Node3D): _player = b; b.set("lift", self))
	body_exited.connect(func(b: Node3D): if _player == b: _player = null; b.set("lift", null))

func go_to_deck(deck: int, player: Node3D) -> bool:
	for d in decks:
		if int(d["id"]) == deck:
			var target_y: float = float(d["y"]) + 0.08
			if absf(player.global_position.y - target_y) < 1.0:
				return false
			player.global_position.y = target_y
			player.set("velocity", Vector3.ZERO)
			deck_changed.emit(deck)
			return true
	return false
