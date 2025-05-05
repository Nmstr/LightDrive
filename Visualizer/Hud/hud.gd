extends Node2D

var current_menu := ""


func _on_toggle_mode_button_pressed() -> void:
	if Globals.mode == Globals.available_modes.EDITOR:
		Globals.mode = Globals.available_modes.LIVE
		$ToggleModeButton.text = "Enter Editor Mode"
		for fixture in get_node("/root/Stage").fixtures:
			fixture.change_selection_status(false)
			fixture.collision_indicator.hide()
		$LeftSideBar.hide()
		hide_menu()
	else:
		Globals.mode = Globals.available_modes.EDITOR
		$ToggleModeButton.text = "Enter Live Mode"
		for fixture in get_node("/root/Stage").fixtures:
			fixture.reset()
			fixture.collision_indicator.show()
		$LeftSideBar.show()


func show_menu(menu: String) -> void:
	if current_menu:
		return # Already "appeared"
	current_menu = menu
	get_node(menu).position.x = -200
	for i in range(25):
		get_node("LeftSideBar").position.x -= 10
		get_node(menu).position.x += 10
		await get_tree().create_timer(0.005).timeout


func hide_menu() -> void:
	if not current_menu:
		return # Already "disappeared"
	for i in range(25):
		get_node("LeftSideBar").position.x += 10
		get_node(current_menu).position.x -= 10
		await get_tree().create_timer(0.005).timeout
	get_node(current_menu).position.x = -250
	current_menu = ""
