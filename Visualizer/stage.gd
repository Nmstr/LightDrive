extends Node

var fixture_scene := preload("res://Fixtures/fixture.tscn")
var fixtures := Array()
var universes := Array()
var dmx_values := {}
var selected_fixture: Node3D

var xr_interface: XRInterface

func _ready() -> void:
	xr_interface = XRServer.find_interface("OpenXR")
	if xr_interface and xr_interface.is_initialized():
		DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
		get_viewport().use_xr = true
		get_node("XROrigin3D").visible = true
		get_node("CustomCamera").visible = false


func set_dmx_values(universe_entry, new_values: Array) -> void:
	var universe := universes.find(universe_entry) + 1
	if not dmx_values.get(universe):
		dmx_values[universe] = []
		dmx_values[universe].resize(512)
		dmx_values[universe].fill(0)
	dmx_values[universe] = new_values


func add_fixture(fixture_path: String,
				x_pos: float = 0.0,
				y_pos: float = 0.0,
				z_pos: float = 0.0,
				x_rot: float = 0.0,
				y_rot: float = 0.0,
				z_rot: float = 0.0,
				universe: int = 1,
				channel: int = 1) -> void:
	var fixture := fixture_scene.instantiate()
	fixture.load_fixture_data(fixture_path)
	fixture.position.x = x_pos
	fixture.position.y = y_pos
	fixture.position.z = z_pos
	fixture.rotation.x = x_rot
	fixture.rotation.y = y_rot
	fixture.rotation.z = z_rot
	fixture.universe = universe
	fixture.channel = channel
	add_child(fixture)
	fixtures.append(fixture)
