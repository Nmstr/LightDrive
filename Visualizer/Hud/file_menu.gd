extends Panel

var dialog_selected_file := ""


func _on_file_button_pressed() -> void:
	get_parent().show_menu("FileMenu")

func _on_close_file_menu_button_pressed() -> void:
	get_parent().hide_menu()


func _on_save_file_button_pressed() -> void:
	$FileMenuOptions/SaveFileDialog.show()


func _on_save_file_dialog_file_selected(path: String) -> void:
	_save_file(path)


func _save_file(path: String) -> void:
	# Collect the fixture data
	var fixture_data := []
	for fixture in get_tree().get_nodes_in_group("Persist"):
		fixture_data.append({
			"fixture_path": fixture.path,
			"x_pos": fixture.position.x,
			"y_pos": fixture.position.y,
			"z_pos": fixture.position.z,
			"x_rot": fixture.rotation.x,
			"y_rot": fixture.rotation.y,
			"z_rot": fixture.rotation.z,
			"universe": fixture.universe,
			"channel": fixture.channel
		})
	# Collect the universe data
	var universe_data := []
	for universe in get_node('/root/Stage').universes:
		universe_data.append(universe.get_port())
	
	# Collect stage data
	var stage_data = {
		"stage_path": get_node('/root/Stage/StageModel').path
	}
	
	# Create the save file
	var save_data := {
		"fixture_data": fixture_data,
		"universe_data": universe_data,
		"stage_data": stage_data
	}
	var save_file := FileAccess.open(path, FileAccess.WRITE)
	save_file.store_line(JSON.stringify(save_data))


func _on_load_file_button_pressed() -> void:
	$FileMenuOptions/LoadFileDialog.show()


func _on_load_file_dialog_file_selected(path: String) -> void:
	_load_file(path)


func _load_file(path: String) -> void:
	# Verify the path exists
	if not FileAccess.file_exists(path):
		return
	
	# Remove all nodes that get saved/loaded (e.g. fixtures)
	var save_nodes = get_tree().get_nodes_in_group("Persist")
	for i in save_nodes:
		i.queue_free()
	get_node('/root/Stage').fixtures = []
	for universe in get_node('/root/Stage').universes:
		universe.queue_free()
	get_node('/root/Stage').universes = []
	
	# Load the save file
	var save_file := FileAccess.open(path, FileAccess.READ)
	var json := JSON.new()
	json.parse(save_file.get_as_text())
	# Load the fixtures
	for fixture in json.data["fixture_data"]:
		get_node('/root/Stage').add_fixture(fixture.fixture_path,
				fixture.x_pos,
				fixture.y_pos,
				fixture.z_pos,
				fixture.x_rot,
				fixture.y_rot,
				fixture.z_rot,
				fixture.universe,
				fixture.channel
		)
	
	# Load the universes
	for universe in json.data["universe_data"]:
		get_parent().get_node("UniverseMenu").create_universe(universe)
	
	# Load the stage model
	get_node('/root/Stage/StageModel').unload_stage_model()
	get_node('/root/Stage/StageModel').load_stage_model(json.data["stage_data"].get("stage_path"))
