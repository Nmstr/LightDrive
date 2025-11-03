import QtQuick

Rectangle {
    id: iconButton
    width: 40
    height: 40
    color: "#424243"
    required property string iconSource
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

    MouseArea {
        anchors.fill: parent
        onClicked: iconButton.clicked()
    }
}
