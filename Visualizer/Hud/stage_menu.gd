extends Panel

var last_click_time := 0
var is_shown := false

@export var max_ms_double_click := 500 # The max time in ms for a double click to register


func _ready() -> void:
	var dir := DirAccess.open("res://Assets")
	if dir == null: printerr("Could not open folder"); return
	dir.list_dir_begin()
	var reader = ZIPReader.new()
	for file: String in dir.get_files():
		if file.ends_with(".ldvm"):
			var err := reader.open(dir.get_current_dir() + "/" + file)
			if err != OK:
				print(err)
				return
			var thumbnail_file := reader.read_file("thumbnail.png")
			reader.close()
			
			var image = Image.new()
			image.load_png_from_buffer(thumbnail_file)
			var icon = ImageTexture.create_from_image(image)
			
			var index = $StageMenuList.add_icon_item(icon)
			$StageMenuList.set_item_metadata(index, dir.get_current_dir() + "/" + file)


func _on_stage_button_pressed() -> void:
	get_parent().show_menu("StageMenu")


func _on_close_stage_menu_button_pressed() -> void:
	get_parent().hide_menu()


func _on_stage_menu_list_item_clicked(index: int, _at_position: Vector2, mouse_button_index: int) -> void:
	if mouse_button_index:
		if Time.get_ticks_msec() - last_click_time < max_ms_double_click:
			get_node('/root/Stage/StageModel').unload_stage_model() # Remove current model
			get_node('/root/Stage/StageModel').load_stage_model($StageMenuList.get_item_metadata(index))  #Load new model
			last_click_time = 0 # Reset double click
		else:
			last_click_time = Time.get_ticks_msec()
