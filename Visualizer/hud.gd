extends Node2D


func _on_button_pressed() -> void:
	if Globals.mode == Globals.available_modes.EDITOR:
		Globals.mode = Globals.available_modes.LIVE
		$ToggleModeButton.text = "Enter Editor Mode"
		get_parent().get_node("MovingHead").change_selection_status(false)
	else:
		Globals.mode = Globals.available_modes.EDITOR
		$ToggleModeButton.text = "Enter Live Mode"
