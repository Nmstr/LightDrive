extends Node

var pan_input := 0.0
var tilt_input := 0.0

@onready var moving_head := $MovingHead


func _ready() -> void:
	pass


func _process(delta: float) -> void:
	moving_head.set_pan(pan_input)
	moving_head.set_tilt(tilt_input)
	pan_input += 1 * delta * 255 / 2
	tilt_input += 1 * delta * 255 / 2
