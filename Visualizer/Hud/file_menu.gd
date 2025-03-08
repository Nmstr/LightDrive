extends VBoxContainer

var dialog_selected_file := ""


func _ready() -> void:
	pass


func _on_file_button_pressed() -> void:
	get_parent().show_menu("FileMenu")


func _on_close_file_menu_button_pressed() -> void:
	get_parent().hide_menu()


func _on_save_file_button_pressed() -> void:
	$SaveFileDialog.show()


func _on_save_file_dialog_file_selected(path: String) -> void:
	_save_file(path)


func _save_file(path: String) -> void:
	# Collect the save data
	var save_data = []
	for fixture in get_tree().get_nodes_in_group("Persist"):
		save_data.append({
			"fixture_path": fixture.path,
			"x_pos": fixture.position.x,
			"y_pos": fixture.position.y,
			"z_pos": fixture.position.z,
			"x_rot": fixture.rotation.x,
			"y_rot": fixture.rotation.y,
			"z_rot": fixture.rotation.z
		})
	
	# Create the save file
	var save_file = FileAccess.open(path, FileAccess.WRITE)
	save_file.store_line(JSON.stringify(save_data))


func _on_load_file_button_pressed() -> void:
	$LoadFileDialog.show()


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
	get_parent().get_parent().fixtures = []
	
	# Load the save file
	var save_file = FileAccess.open(path, FileAccess.READ)
	var json = JSON.new()
	json.parse(save_file.get_as_text())
	for fixture in json.data:
		get_parent().get_parent().add_fixture(fixture.fixture_path,
				fixture.x_pos,
				fixture.y_pos,
				fixture.z_pos,
				fixture.x_rot,
				fixture.y_rot,
				fixture.z_rot
		)
