extends Panel

var fog_density := 0.1


func _on_environment_button_pressed() -> void:
	get_parent().show_menu("EnvironmentMenu")


func _on_close_environment_menu_button_pressed() -> void:
	get_parent().hide_menu()


func _on_realistic_lighting_button_toggled(toggled_on: bool) -> void:
	var stage := get_node('/root/Stage')
	if toggled_on:
		stage.get_node("WorldEnvironment").environment.volumetric_fog_enabled = true
		stage.get_node("WorldEnvironment").environment.volumetric_fog_density = fog_density
		for fixture in stage.fixtures:
			for light_cone in fixture.light_cones:
				light_cone.hide()
			for real_light_cone in fixture.real_light_cones:
				real_light_cone.show()
	else:
		stage.get_node("WorldEnvironment").environment.volumetric_fog_enabled = false
		for fixture in stage.fixtures:
			for light_cone in fixture.light_cones:
				light_cone.show()
			for real_light_cone in fixture.real_light_cones:
				real_light_cone.hide()


func _on_fog_density_spin_value_changed(value: float) -> void:
	fog_density = value
	get_node('/root/Stage/WorldEnvironment').environment.volumetric_fog_density = fog_density
