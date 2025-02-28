extends Node2D


func _on_button_pressed() -> void:
	if Globals.mode == Globals.available_modes.EDITOR:
		Globals.mode = Globals.available_modes.LIVE
		$ToggleModeButton.text = "Enter Editor Mode"
	else:
		Globals.mode = Globals.available_modes.EDITOR
		$ToggleModeButton.text = "Enter Live Mode"
