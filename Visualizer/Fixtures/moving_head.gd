extends StaticBody3D

@export var min_pan_angle := 0.0
@export var min_tilt_angle := -135.0
@export var max_pan_angle := 540.0
@export var max_tilt_angle := 270.0

@onready var pan_pivot := $PanPivot
@onready var tilt_pivot := $PanPivot/TiltPivot


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
	tilt_pivot.rotation.z = deg_to_rad(new_tilt_angle + min_tilt_angle)
