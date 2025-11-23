import QtQuick
import QtQuick.Controls

Rectangle {
    color: "transparent"

    Rectangle {
        anchors {
            top: parent.top
            left: parent.left
            right: parent.right
        }
        height: 50
        color: "transparent"

        Row {
            anchors.verticalCenter: parent.verticalCenter
            spacing: 10

            Text {
                text: "Name:"
                color: "white"
                font.pixelSize: 20
            }

            TextField {
                id: sceneNameInput
                placeholderText: "Scene Name"
            }
        }
    }

    Connections {
        target: snippetHandler

        function onLoadScene(name) {
            sceneNameInput.text = name
        }
    }
}
