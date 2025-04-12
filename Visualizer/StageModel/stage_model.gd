extends Node3D

var path := ""


func _ready() -> void:
	load_stage_model("res://Assets/empty_stage.ldvm")


func load_stage_model(stage_path: String) -> void:
	path = stage_path
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
	var full_model_node = node
	if node.get_children()[0] is not MeshInstance3D:
		full_model_node = node.get_children()[0]
		
	# Make the stage collidable for VR support
	for mesh_instance in full_model_node.get_children():
		#mesh_instance.create_convex_collision()
		mesh_instance.create_trimesh_collision()
	
	# Load json
	var json := JSON.new()
	var error := json.parse(json_file.get_string_from_utf8())
	if error == OK:
		var json_data = json.data
		# Color the objects
		for object in json_data.get("objects"):
			var object_data = json_data.get("objects")[object]
			var gobject := full_model_node.get_node(object)
			var material := StandardMaterial3D.new()
			material.albedo_color = Color.html(object_data.get("color"))
			for i in gobject.mesh.get_surface_count():
				gobject.mesh.surface_set_material(i, material)
			if object_data.get("surface_overrides"):
				for override in object_data.get("surface_overrides"):
					var override_material := StandardMaterial3D.new()
					override_material.albedo_color = Color.html(object_data.get("surface_overrides")[override])
					gobject.mesh.surface_set_material(int(override), override_material)
		# Move the camera to new position
		var raw_cam_pos = json_data.get("initial_camera_position")
		var cam_pos := Vector3(raw_cam_pos[0], raw_cam_pos[1], raw_cam_pos[2])
		get_node("/root/Stage/CustomCamera").global_position = cam_pos
		get_node("/root/Stage/XROrigin3D").position = cam_pos

func unload_stage_model():
	if get_children():
		get_children()[0].queue_free()
