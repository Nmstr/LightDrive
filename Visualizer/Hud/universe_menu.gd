extends Panel

var universe_entry_scene := preload("res://Hud/universe_entry.tscn")


func _on_universes_button_pressed() -> void:
	get_parent().show_menu("UniverseMenu")


func _on_close_universe_menu_pressed() -> void:
	get_parent().hide_menu()


func _on_add_universe_button_pressed() -> void:
	var universe_entry := universe_entry_scene.instantiate()
	$UniverseScroll/UniverseVBox.add_child(universe_entry)
	get_parent().get_parent().universes.append(universe_entry)


func _on_remove_universe_button_pressed() -> void:
	if get_parent().get_parent().universes.size() <= 0:
		return # There are no universes to remove
	var removed_universe = get_parent().get_parent().universes.pop_back()
	removed_universe.queue_free()


func _on_apply_universes_button_pressed() -> void:
	pass
