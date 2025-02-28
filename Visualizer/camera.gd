extends Node3D

@export var camera_pivot_indicator_visibility := true

@onready var twist_pivot := $TwistPivot
@onready var pitch_pivot := $TwistPivot/PitchPivot
@onready var camera := $TwistPivot/PitchPivot/Camera3D

func _ready() -> void:
	if not camera_pivot_indicator_visibility:
		$TwistPivot/PitchPivot/CameraPivotIndicator.hide()


func _process(_delta: float) -> void:
	# Handle inputs
	if Input.is_action_just_pressed("move_forward"):
		camera.translate(Vector3(0, 0, -1))
	if Input.is_action_just_pressed("move_backward"):
		camera.translate(Vector3(0, 0, 1))
	if Input.is_action_pressed("middle_mouse_click"):
		var mouse_motion = Input.get_last_mouse_velocity()
		if Input.is_action_pressed("r_click"):
			twist_pivot.rotate_y(deg_to_rad(-mouse_motion.x * 0.01))
			pitch_pivot.rotate_x(deg_to_rad(-mouse_motion.y * 0.01))
			pitch_pivot.rotation.x = clamp(pitch_pivot.rotation.x,
					deg_to_rad(-70),
					deg_to_rad(70)
			)
		else:
			twist_pivot.translate(Vector3(-mouse_motion.x * 0.0001, mouse_motion.y * 0.0001, 0))
