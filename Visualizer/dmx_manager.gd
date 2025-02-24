extends Node

var dmx_values := Array()

@onready var moving_head := $MovingHead


func _ready() -> void:
	dmx_values.resize(512)
	dmx_values.fill(0)


func _process(_delta: float) -> void:
	moving_head.set_pan(dmx_values[0])
	moving_head.set_tilt(dmx_values[1])
	#pan_input += 1 * delta * 255 / 2
	#tilt_input += 1 * delta * 255 / 2


func set_dmx_values(new_values: Array) -> void:
	dmx_values = new_values
