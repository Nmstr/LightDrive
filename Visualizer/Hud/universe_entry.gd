extends HBoxContainer

var host := "127.0.0.1"
var running_port := 7500
var client := StreamPeerTCP.new()
var reconnect_delay := 1.0  # Time in seconds to wait before attempting to reconnect
var time_since_last_attempt := 0.0


func _ready() -> void:
	$InfoSide/UniverseLabel.text = "Universe " + str(get_node("/root/Stage").universes.size() + 1)

func set_port(port) -> void:
	$InfoSide/PortHBox/PortSpin.value = port


func get_port() -> int:
	return $InfoSide/PortHBox/PortSpin.value


func restart_listening() -> void:
	if $InfoSide/PortHBox/PortSpin.value == 0:
		if client:
			client.disconnect_from_host()
	else:
		connect_to_server()


func _process(delta: float) -> void:
	client.poll()
	if client.get_status() == StreamPeerTCP.STATUS_CONNECTED:
		if client.get_available_bytes() > 0:
			var data = client.get_utf8_string(client.get_available_bytes())
			data = JSON.parse_string(data)
			if data == null:
				return
			get_node("/root/Stage").set_dmx_values(self, data)
	elif client.get_status() == StreamPeerTCP.STATUS_CONNECTING:
		pass
	else:
		time_since_last_attempt += delta
		if time_since_last_attempt >= reconnect_delay:
			time_since_last_attempt = 0.0
			connect_to_server()


func connect_to_server() -> void:
	running_port = $InfoSide/PortHBox/PortSpin.value
	if running_port == 0:
		return
	client = StreamPeerTCP.new()  # Create a new instance of StreamPeerTCP
	var err = client.connect_to_host(host, running_port)


func _on_update_status_timer_timeout() -> void:
	var status = client.get_status()
	if status == StreamPeerTCP.STATUS_CONNECTED:
		if running_port == $InfoSide/PortHBox/PortSpin.value:
			$UniverseStatus.color = Color.GREEN
		else:
			$UniverseStatus.color = Color.BLUE
	elif status == StreamPeerTCP.STATUS_CONNECTING:
		$UniverseStatus.color = Color.ORANGE
	elif status == StreamPeerTCP.STATUS_CONNECTED:
		$UniverseStatus.color = Color.GREEN
	elif status == StreamPeerTCP.STATUS_ERROR:
		$UniverseStatus.color = Color.RED
	else:
		$UniverseStatus.color = Color.WHITE
