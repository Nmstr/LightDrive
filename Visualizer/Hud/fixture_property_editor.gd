extends ScrollContainer

var is_shown := false

@onready var x_pos_spin := $Background/FixturePropertyVBox/PositionHBox/XPosSpin
@onready var y_pos_spin := $Background/FixturePropertyVBox/PositionHBox/YPosSpin
@onready var z_pos_spin := $Background/FixturePropertyVBox/PositionHBox/ZPosSpin
@onready var x_rot_spin := $Background/FixturePropertyVBox/RotationHBox/XRotSpin
@onready var y_rot_spin := $Background/FixturePropertyVBox/RotationHBox/YRotSpin
@onready var z_rot_spin := $Background/FixturePropertyVBox/RotationHBox/ZRotSpin


func show_fixture(fixture: Node3D) -> void:
	x_pos_spin.value = fixture.position.x
	y_pos_spin.value = fixture.position.y
	z_pos_spin.value = fixture.position.z
	x_rot_spin.value = fixture.rotation.x
	y_rot_spin.value = fixture.rotation.y
	z_rot_spin.value = fixture.rotation.z


func appear() -> void:
	if is_shown:
		return # Already "appeared"
	is_shown = true
	position.x = 1152
	for i in range(25):
		position.x -= 17
		await get_tree().create_timer(0.005).timeout
	position.x = 722


func disappear() -> void:
	if not is_shown:
		return # Already "disappeared"
	is_shown = false
	for i in range(25):
		position.x += 17
		await get_tree().create_timer(0.005).timeout
	position.x = 1200
