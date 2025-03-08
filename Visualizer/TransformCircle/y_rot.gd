extends StaticBody3D

var dragging := false
var last_position := Vector2()
var drag_distance := 0.0


# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	input_event.connect(on_input_event)


func _process(delta: float) -> void:
	var fixture := get_parent().get_parent()
	if abs(drag_distance) > 0.0:
		fixture.rotation.y += drag_distance * delta
		fixture.get_parent().get_node("Hud/FixturePropertyEditor/Background/FixturePropertyVBox/RotationHBox/YRotSpin").value = rad_to_deg(fixture.rotation.y)
		drag_distance = 0.0


func on_input_event(_camera, event, _click_position, _click_normal, _shape_idx) -> void:
	var mouse_click := event as InputEventMouseButton

	if mouse_click and mouse_click.button_index == MOUSE_BUTTON_LEFT and mouse_click.pressed:
		last_position = mouse_click.position
		dragging = true


func _input(event) -> void:
	var mouse_click := event as InputEventMouseButton
	var mouse_motion := event as InputEventMouseMotion

	if mouse_click and mouse_click.button_index == MOUSE_BUTTON_LEFT and not mouse_click.pressed:
		dragging = false
	elif mouse_motion and dragging:
		drag_distance += event.position.distance_to(last_position) * event.position.direction_to(last_position).y
		last_position = event.position
