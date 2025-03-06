extends Node2D


func _on_toggle_mode_button_pressed() -> void:
	if Globals.mode == Globals.available_modes.EDITOR:
		Globals.mode = Globals.available_modes.LIVE
		$ToggleModeButton.text = "Enter Editor Mode"
		for fixture in get_parent().fixtures:
			fixture.change_selection_status(false)
			fixture.collision_indicator.hide()
		$LeftSideBar/AddFixtureButton.hide()
	else:
		Globals.mode = Globals.available_modes.EDITOR
		$ToggleModeButton.text = "Enter Live Mode"
		for fixture in get_parent().fixtures:
			fixture.reset()
			fixture.collision_indicator.show()
		$LeftSideBar/AddFixtureButton.show()
