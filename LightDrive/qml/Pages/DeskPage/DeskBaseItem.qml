import QtQuick

Rectangle {
    id: rect
    x: 0
    y: 0
    width: 100
    height: 100

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        drag.target: parent
        onPositionChanged: {
            rect.x = Math.min(Math.max(rect.x, 0), desk.width - rect.width);
            rect.y = Math.min(Math.max(rect.y, 0), desk.height - rect.height);
        }
    }
}
