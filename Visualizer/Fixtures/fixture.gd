extends StaticBody3D

var selected := false
var pan_pivot
var tilt_pivot
var min_pan_angle
var min_tilt_angle
var max_pan_angle
var max_tilt_angle
var path
var universe
var channel

@onready var collision_indicator := $CollisionIndicator
@onready var transform_circle := $TransformCircle


func _ready():
	# Setup collision
	transform_circle.hide()
	input_event.connect(on_input_event)


func load_fixture_data(fixture_path: String) -> void:
	path = fixture_path
	var reader := ZIPReader.new()
	var err := reader.open(path)
	if err != OK:
		print(err)
		return
	var model_file := reader.read_file("model.glb")
	var json_file := reader.read_file("config.json")
	reader.close()
	
	# Load model
	var gltf := GLTFDocument.new()
	var gltf_state := GLTFState.new()
	
	gltf.append_from_buffer(model_file, "base_path?", gltf_state)
	var node := gltf.generate_scene(gltf_state)
	add_child(node)
	
	# Configure pivots
	pan_pivot = node.get_children()[0].get_node("PanPivot")
	tilt_pivot = node.get_children()[0].get_node("TiltPivot")
	call_deferred("_reparent_tilt_pivot")
	
	# Load json
	var json := JSON.new()
	var error := json.parse(json_file.get_string_from_utf8())
	if error == OK:
		var json_data = json.data
		for light_source in json_data.get("light_sources"):
			min_pan_angle = light_source.get("min_pan_angle")
			min_tilt_angle = light_source.get("min_tilt_angle")
			max_pan_angle = light_source.get("max_pan_angle")
			max_tilt_angle = light_source.get("max_tilt_angle")
			var light_cone := MeshInstance3D.new()
			light_cone.position.x = light_source.get("x_offset")
			light_cone.position.y = light_source.get("length") / 2 + light_source.get("y_offset")
			light_cone.position.z = light_source.get("z_offset")
			var light_cone_shape := CylinderMesh.new()
			light_cone_shape.height = light_source.get("length")
			light_cone_shape.bottom_radius = 0.0
			light_cone_shape.top_radius = light_source.get("length") * tan(deg_to_rad(light_source.get("angle")))
			light_cone.set_mesh(light_cone_shape)
			var light_cone_material := StandardMaterial3D.new()
			light_cone_material.transparency = 1
			light_cone_material.blend_mode = 1
			light_cone_material.shading_mode = 0
			light_cone.set_surface_override_material(0, light_cone_material)
			var light_rotation_pivot := Node3D.new()
			light_rotation_pivot.rotation.x = deg_to_rad(light_source.get("x_rotation"))
			light_rotation_pivot.rotation.y = deg_to_rad(light_source.get("y_rotation"))
			light_rotation_pivot.rotation.z = deg_to_rad(light_source.get("z_rotation"))
			light_rotation_pivot.add_child(light_cone)
			tilt_pivot.add_child(light_rotation_pivot)


# The following is here because I can't reparent tilt_pivot under pan_pivot
# before the physics frame in which both where created has finished.
# This is because tilt_pivot needs to first be properly added to the scene tree,
# which I do by waiting for the function that creates it to finish running,
# and then call this one.
func _reparent_tilt_pivot() -> void:
	tilt_pivot.reparent(pan_pivot)


func on_input_event(_camera, event, _click_position, _click_normal, _shape_idx):
	var mouse_click := event as InputEventMouseButton
	if mouse_click and mouse_click.button_index == 1 and mouse_click.pressed:
		if Globals.mode == Globals.available_modes.EDITOR:
			if selected:
				change_selection_status(false)
			else:
				change_selection_status(true)


func change_selection_status(stauts: bool) -> void:
	if stauts:
		if get_parent().selected_fixture:
			get_parent().selected_fixture.change_selection_status(false)
		get_parent().selected_fixture = self
		get_parent().get_node("Hud").hide_menu()
		get_parent().get_node("Hud").get_node("FixturePropertyEditor").appear()
		get_parent().get_node("Hud").get_node("FixturePropertyEditor").show_fixture(self)
		transform_circle.show()
		selected = true
	else:
		get_parent().get_node("Hud").get_node("FixturePropertyEditor").disappear()
		transform_circle.hide()
		selected = false


func _physics_process(delta: float) -> void:
	if Globals.mode == Globals.available_modes.LIVE:
		var dmx_values = get_parent().dmx_values.get(int(universe))
		if not dmx_values:
			reset()
			return
		set_pan(dmx_values[0 + channel - 1])
		set_tilt(dmx_values[1 + channel - 1])

# This expects a value between 0 and 255
# The value will then be mapped against max_pan_angle
# In the end it will be offset by min_pan_angle
func set_pan(pan_value: int) -> void:
	if pan_value < 0:
		return  # Value below minimum
	elif pan_value > 255:
		return  # Value above maximum
	var new_pan_angle = pan_value / 255.0 * max_pan_angle
	pan_pivot.rotation.y = deg_to_rad(new_pan_angle + min_pan_angle)


# This expects a value between 0 and 255
# The value will then be mapped against max_tilt_angle
# In the end it will be offset by min_tilt_angle
func set_tilt(tilt_value: int) -> void:
	if tilt_value < 0:
		return  # Value below minimum
	elif tilt_value > 255:
		return  # Value above maximum
	var new_tilt_angle = tilt_value / 255.0 * max_tilt_angle
	tilt_pivot.rotation.x = deg_to_rad(new_tilt_angle + min_tilt_angle)


func reset() -> void:
	collision_indicator.show()
	pan_pivot.rotation.y = 0
	tilt_pivot.rotation.x = 0
