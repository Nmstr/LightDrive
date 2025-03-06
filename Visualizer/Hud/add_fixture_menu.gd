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
		print(dir.get_current_dir() + "/" + file)
		if file.ends_with(".ldv"):
			var err = reader.open(dir.get_current_dir() + "/" + file)
			if err != OK:
				print(err)
				return
			var thumbnail_file = reader.read_file("thumbnail.png")
			reader.close()
			
			var image = Image.new()
			image.load_png_from_buffer(thumbnail_file)
			var icon = ImageTexture.create_from_image(image)
			
			self.add_icon_item(icon)

func _on_add_fixture_button_pressed() -> void:
	appear()


func _on_focus_exited() -> void:
	disappear()


func appear() -> void:
	if is_shown:
		return # Already "appeared"
	is_shown = true
	for i in range(25):
		hud_node.get_node("LeftSideBar").position.x -= 10
		hud_node.get_node("AddFixtureMenu").position.x += 10
		await get_tree().create_timer(0.005).timeout
	hud_node.get_node("AddFixtureMenu").get_node("FixtureMenuList").grab_focus()


func disappear() -> void:
	if not is_shown:
		return # Already "disappeared"
	is_shown = false
	for i in range(25):
		hud_node.get_node("LeftSideBar").position.x += 10
		hud_node.get_node("AddFixtureMenu").position.x -= 10
		await get_tree().create_timer(0.005).timeout


func _on_item_clicked(_index: int, _at_position: Vector2, mouse_button_index: int) -> void:
	if mouse_button_index:
		if Time.get_ticks_msec() - last_click_time < max_ms_double_click:
			hud_node.get_parent().add_fixture()
			last_click_time = 0 # Reset double click
		else:
			last_click_time = Time.get_ticks_msec()
