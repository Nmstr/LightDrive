extends Node

var fixture_scene := preload("res://Fixtures/fixture.tscn")
var fixtures := Array()
var universes := Array()
var dmx_values := Array()
var selected_fixture: Node3D


func _ready() -> void:
	dmx_values.resize(512)
	dmx_values.fill(0)


func _process(_delta: float) -> void:
	# Move the moving head
	if Globals.mode == Globals.available_modes.LIVE:
		for fixture in fixtures:
			fixture.set_pan(dmx_values[0])
			fixture.set_tilt(dmx_values[1])


func set_dmx_values(new_values: Array) -> void:
	dmx_values = new_values


func add_fixture(fixture_path: String,
				x_pos: float = 0.0,
				y_pos: float = 0.0,
				z_pos: float = 0.0,
				x_rot: float = 0.0,
				y_rot: float = 0.0,
				z_rot: float = 0.0) -> void:
	var fixture := fixture_scene.instantiate()
	fixture.load_fixture_data(fixture_path)
	fixture.position.x = x_pos
	fixture.position.y = y_pos
	fixture.position.z = z_pos
	fixture.rotation.x = x_rot
	fixture.rotation.y = y_rot
	fixture.rotation.z = z_rot
	add_child(fixture)
	fixtures.append(fixture)
