import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

Popup {
    property string currentUuid;
    id: configureUniversePopup
    x: (parent.width - width) / 2
    y: (parent.height - height) / 2
    width: parent.width - 150
    height: parent.height - 150
    padding: 0
    dim: true
    background: Rectangle {
        color: "#4f4f4f"
    }

    Rectangle {
        id: topper
        implicitWidth: parent.width
        height: 30
        color: "#2677ed"
        Text {
            anchors.fill: parent
            anchors.leftMargin: 10
            anchors.topMargin: 5
            text: "Configure Universe"
            font.pixelSize: 16
            color: "white"
        }
    }

    Column {
        anchors {
            top: topper.bottom
            left: parent.left
            right: parent.right
            bottom: footer.bottom
            margins: 10
        }
        spacing: 10

        GridLayout {
            columns: 2

            Text {
                text: "Name:"
                color: "white"
            }
            TextField {
                id: universeNameInput
                placeholderText: "Universe Name"
                text: ""
            }
        }
        Row {
            CheckBox {
                anchors.verticalCenter: parent.verticalCenter
                id: tcpBackendCheckbox
            }
            Text {
                anchors.verticalCenter: parent.verticalCenter
                text: "Enable TCP Socket"
                color: "white"
            }
        }
        GridLayout {
            id: tcpBackendGrid
            columns: 2
            enabled: tcpBackendCheckbox.checkState

            Text {
                text: "Target IP:"
                color: "white"
            }
            TextField {
                id: tcpTargetIpInput
                placeholderText: "127.0.0.1"
                text: "127.0.0.1"
            }
            Text {
                text: "Port:"
                color: "white"
            }
            TextField {
                id: tcpPortInput
                placeholderText: "7500"
                text: "7500"
            }
            Text {
                text: "Hz:"
                color: "white"
            }
            SpinBox {
                id: tcpHzSpin
                from: 0
                to: 255
                stepSize: 1
                editable: true
            }
        }
        Row {
            CheckBox {
                anchors.verticalCenter: parent.verticalCenter
                id: artnetBackendCheckbox
            }
            Text {
                anchors.verticalCenter: parent.verticalCenter
                text: "Enable ArtNet"
                color: "white"
            }
        }
        GridLayout {
            id: artnetBackendGrid
            columns: 2
            enabled: artnetBackendCheckbox.checkState

            Text {
                text: "Target IP:"
                color: "white"
            }
            TextField {
                id: artnetTargetIpInput
                placeholderText: "127.0.0.1"
                text: "127.0.0.1"
            }
            Text {
                text: "Universe:"
                color: "white"
            }
            SpinBox {
                id: artnetUniverseSpin
                from: 0
                to: 32767
                stepSize: 1
                editable: true
            }
            Text {
                text: "Max FPS"
                color: "white"
            }
            SpinBox {
                id: artnetMaxFpsSpin
                from: 1
                to: 100
                stepSize: 1
                editable: true
            }
            Text {
                text: "Min Interval:"
                color: "white"
            }
            SpinBox {
                id: artnetMinIntervalSpin
                from: 100
                to: 100_000
                stepSize: 100
                editable: true
            }
        }
    }

    Row {
        id: footer
        anchors {
            right: parent.right
            bottom: parent.bottom
            margins: 10
        }
        spacing: 10

        Button {
            id: confirmButton
            background: Rectangle {
                color: confirmButton.down ? "#434343" : "#636363"
                Rectangle {
                    anchors.bottom: parent.bottom
                    width: parent.width; height: 2
                    color: "#2677ed"
                }
            }
            contentItem: Text {
                text: "Confirm"
                color: "white"
                font.pointSize: 14
            }
            onClicked: {
                universeHandler.configure_universe(currentUuid, universeNameInput.text);
                universeHandler.configure_tcp_backend(currentUuid, tcpBackendCheckbox.checkState, tcpTargetIpInput.text, tcpPortInput.text, tcpHzSpin.value);
                cleanup();
            }
        }
        Button {
            id: cancelButton
            background: Rectangle {
                color: cancelButton.down ? "#434343" : "#636363"
                Rectangle {
                    anchors.bottom: parent.bottom
                    width: parent.width; height: 2
                    color: "#ff3030"
                }
            }
            contentItem: Text {
                text: "Cancel"
                color: "white"
                font.pointSize: 14
            }
            onClicked: {
                cleanup()
            }
        }
    }

    function loadData(universeUuid) {
        currentUuid = universeUuid;

        let universeData = universeHandler.get_universe_configuration(currentUuid);
        universeNameInput.text = universeData[0];

        let tcpBackendData = universeHandler.get_tcp_backend_configuration(currentUuid);
        tcpBackendCheckbox.checkState = tcpBackendData[0];
        tcpTargetIpInput.text = tcpBackendData[1];
        tcpPortInput.text = tcpBackendData[2];
        tcpHzSpin.value = tcpBackendData[3];
    }

    function cleanup() {
        universeNameInput.text = "";

        tcpBackendCheckbox.checkState = false;
        tcpTargetIpInput.text = "127.0.0.1";
        tcpPortInput.text = "7500";
        tcpHzSpin.value = 30

        currentUuid = "";
        configureUniversePopup.close();
    }
}
