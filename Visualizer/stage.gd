extends Node

var fixture_scene := preload("res://Fixtures/fixture.tscn")
var fixtures := Array()
var dmx_values := Array()


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


func add_fixture(fixture_path: String) -> void:
	var fixture := fixture_scene.instantiate()
	fixture.load_fixture_data(fixture_path)
	add_child(fixture)
	fixtures.append(fixture)
