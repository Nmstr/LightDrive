extends Node2D


func _on_button_pressed() -> void:
	if Globals.mode == Globals.available_modes.EDITOR:
		Globals.mode = Globals.available_modes.LIVE
		$ToggleModeButton.text = "Enter Editor Mode"
		get_parent().get_node("Fixture").change_selection_status(false)
		get_parent().get_node("Fixture").collision_indicator.hide()
	else:
		Globals.mode = Globals.available_modes.EDITOR
		$ToggleModeButton.text = "Enter Live Mode"
		get_parent().get_node("Fixture").reset()
		get_parent().get_node("Fixture").collision_indicator.show()
