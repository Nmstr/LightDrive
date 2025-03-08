extends VBoxContainer

func _ready() -> void:
	$UniverseLabel.text = "Universe " + str(get_parent().get_parent().get_parent().get_parent().get_parent().universes.size() + 1)

func set_port(port) -> void:
	$PortHBox/PortSpin.value = port

func get_port() -> int:
	return $PortHBox/PortSpin.value
