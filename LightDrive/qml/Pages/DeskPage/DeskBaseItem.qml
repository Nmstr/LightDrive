import QtQuick

Rectangle {
    id: baseItem
    x: 0
    y: 0
    width: 100
    height: 100

    property Item content

    Item {
        anchors.fill: parent
        visible: content !== null

        Component.onCompleted: {
            if (content) {
                content.parent = this
            }
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        drag.target: parent
        onPositionChanged: {
            baseItem.x = Math.min(Math.max(baseItem.x, 0), desk.width - baseItem.width);
            baseItem.y = Math.min(Math.max(baseItem.y, 0), desk.height - baseItem.height);
        }
    }
}
