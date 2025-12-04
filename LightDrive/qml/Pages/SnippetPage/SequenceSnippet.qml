import QtQuick
import QtQuick.Controls

Rectangle {
    id: sequenceSnippetRoot
    color: "transparent"
    property string sequenceUuid

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
                id: sequenceNameInput
                placeholderText: "Sequence Name"
            }
        }
    }

    Connections {
        target: snippetHandler

        function onLoadSequence(uuid, name, sequenceModel) {
            sequenceNameInput.text = name
            sequenceSnippetRoot.sequenceUuid = uuid
        }
    }
}
