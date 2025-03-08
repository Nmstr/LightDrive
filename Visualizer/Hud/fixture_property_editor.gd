extends ScrollContainer

var is_shown := false


func appear() -> void:
	if is_shown:
		return # Already "appeared"
	is_shown = true
	position.x = 1152
	for i in range(25):
		position.x -= 17
		await get_tree().create_timer(0.005).timeout
	position.x = 722


func disappear() -> void:
	if not is_shown:
		return # Already "disappeared"
	is_shown = false
	for i in range(25):
		position.x += 17
		await get_tree().create_timer(0.005).timeout
	position.x = 1200
