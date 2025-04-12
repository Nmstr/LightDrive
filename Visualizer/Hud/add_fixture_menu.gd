extends ItemList

var last_click_time := 0
var is_shown := false

@export var max_ms_double_click := 500 # The max time in ms for a double click to register

@onready var hud_node := get_parent().get_parent()


func _ready() -> void:
	var dir := DirAccess.open("res://Assets")
	if dir == null: printerr("Could not open folder"); return
	dir.list_dir_begin()
	var reader = ZIPReader.new()
	for file: String in dir.get_files():
		if file.ends_with(".ldvf"):
			var err := reader.open(dir.get_current_dir() + "/" + file)
			if err != OK:
				print(err)
				return
			var thumbnail_file := reader.read_file("thumbnail.png")
			reader.close()
			
			var image = Image.new()
			image.load_png_from_buffer(thumbnail_file)
			var icon = ImageTexture.create_from_image(image)
			
			var index := self.add_icon_item(icon)
			self.set_item_metadata(index, dir.get_current_dir() + "/" + file) # Store the path to the fixture as metadata of item


func _on_add_fixture_button_pressed() -> void:
	hud_node.show_menu("AddFixtureMenu")


func _on_close_fixture_menu_pressed() -> void:
	hud_node.hide_menu()


func _on_item_clicked(index: int, _at_position: Vector2, mouse_button_index: int) -> void:
	if mouse_button_index:
		if Time.get_ticks_msec() - last_click_time < max_ms_double_click:
			get_node('/root/Stage').add_fixture(get_item_metadata(index))
			last_click_time = 0 # Reset double click
		else:
			last_click_time = Time.get_ticks_msec()
