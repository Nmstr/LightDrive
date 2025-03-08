extends Node

var host := "127.0.0.1"
var port := 7500
var client := StreamPeerTCP.new()
var reconnect_delay := 1.0  # Time in seconds to wait before attempting to reconnect
var time_since_last_attempt := 0.0


func _ready() -> void:
	connect_to_server()


func _process(delta: float) -> void:
	client.poll()
	if client.get_status() == StreamPeerTCP.STATUS_CONNECTED:
		if client.get_available_bytes() > 0:
			var data = client.get_utf8_string(client.get_available_bytes())
			data = JSON.parse_string(data)
			if data == null:
				return
			get_parent().set_dmx_values(data)
	elif client.get_status() == StreamPeerTCP.STATUS_CONNECTING:
		pass
	else:
		time_since_last_attempt += delta
		if time_since_last_attempt >= reconnect_delay:
			print("Attempting reconnect")
			time_since_last_attempt = 0.0
			connect_to_server()


func connect_to_server() -> void:
	client = StreamPeerTCP.new()  # Create a new instance of StreamPeerTCP
	client.connect_to_host(host, port)
