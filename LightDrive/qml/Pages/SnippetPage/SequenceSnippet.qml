import QtQuick
import QtQuick.Controls
import Elements

Rectangle {
    id: sequenceSnippetRoot
    color: "transparent"
    property string sequenceUuid

    Rectangle {
        id: topper
        anchors {
            top: parent.top
            left: parent.left
            right: parent.right
        }
        implicitHeight: topperColumn.height
        color: "transparent"

        Column {
            id: topperColumn
            anchors.verticalCenter: parent.verticalCenter
            spacing: 10
            padding: 10

            Row {
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
            Row {
                spacing: 125

                TextIconButton {
                    iconSource: "qrc:/icons/add.svg"
                    labelText: "Add Scene"
                    onClicked: console.log("add scene")
                }
                TextIconButton {
                    iconSource: "qrc:/icons/remove.svg"
                    labelText: "Remove Scene"
                    onClicked: console.log("remove scene")
                }
            }
        }
    }

    ListView {
        anchors {
            top: topper.bottom
            left: parent.left
            right: parent.right
            bottom: parent.bottom
        }
        model: 5
        delegate: Rectangle {
            width: parent.width
            height: childrenRect.height

            Text {
                text: "Scene " + index
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
