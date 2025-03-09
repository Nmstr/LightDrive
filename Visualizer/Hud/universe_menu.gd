extends Panel

var universe_entry_scene := preload("res://Hud/universe_entry.tscn")


func _on_universes_button_pressed() -> void:
	get_parent().show_menu("UniverseMenu")


func _on_close_universe_menu_pressed() -> void:
	get_parent().hide_menu()


func _on_add_universe_button_pressed() -> void:
	# Check if port 7500 is free and if so use it
	var used_7500 := false
	for universe in get_parent().get_parent().universes:
		if universe.get_port() == 7500:
			used_7500 = true
			break
	if not used_7500:
		create_universe(7500)
	else:
		create_universe(0)
	
func create_universe(port: int) -> void:
	var universe_entry := universe_entry_scene.instantiate()
	$UniverseScroll/UniverseVBox.add_child(universe_entry)
	get_parent().get_parent().universes.append(universe_entry)
	universe_entry.set_port(port)


func _on_remove_universe_button_pressed() -> void:
	if get_parent().get_parent().universes.size() <= 0:
		return # There are no universes to remove
	var removed_universe = get_parent().get_parent().universes.pop_back()
	removed_universe.queue_free()


func _on_apply_universes_button_pressed() -> void:
	for universe in get_parent().get_parent().universes:
		universe.restart_listening()
