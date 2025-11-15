import QtQuick

Rectangle {
    id: textIconButton
    width: 40
    height: 40
    color: "#424243"
    required property string iconSource
    required property string labelText
    signal clicked

    Image {
        id: icon
        anchors.centerIn: parent
        source: iconSource
        sourceSize: Qt.size(32, 32)
        Image {
            source: parent.source
            width: 0
            height: 0
        }
    }

    Text {
        anchors {
            verticalCenter: parent.verticalCenter
            left: icon.right
            leftMargin: 10
        }
        text: labelText
        color: "white"
        font.pixelSize: 20
    }

    MouseArea {
        anchors.fill: parent
        onClicked: textIconButton.clicked()
    }
}
