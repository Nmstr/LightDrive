import QtQuick

Rectangle {
    width: contentRow.implicitWidth + 20
    height: 40
    color: "#424243"
    required property string iconSource
    required property string labelText

    Row {
        id: contentRow
        anchors.centerIn: parent
        spacing: 5

        Image {
            source: iconSource
            sourceSize: Qt.size(32, 32)
            Image {
                source: parent.source
                width: 0
                height: 0
            }
        }
        Text {
            id: label
            text: labelText
            color: "white"
            width: 0
            font.pixelSize: 24
            font.bold: true
            clip: true

            Behavior on width {
                NumberAnimation {
                    duration: 200
                    easing.type: Easing.InOutQuad
                }
            }
        }
    }

    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        onEntered: {
            label.width = label.implicitWidth
        }
        onExited: {
            label.width = 0
        }
    }
}
