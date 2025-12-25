import QtQuick

Rectangle {
    id: baseItem
    x: 0
    y: 0
    width: 100
    height: 100

    required property string headerText
    property Item content

    Rectangle {
        id: itemHeader
        anchors {
            top: parent.top
            left: parent.left
            right: parent.right
        }
        height: 25
        color: "#dddddd"

        Text {
            text: baseItem.headerText
        }

        MouseArea {
            id: headerDrag
            anchors.fill: parent
            drag.target: baseItem
            onPositionChanged: {
                baseItem.x = Math.min(Math.max(baseItem.x, 0), desk.width - baseItem.width);
                baseItem.y = Math.min(Math.max(baseItem.y, 0), desk.height - baseItem.height);
            }
        }
    }

    Item {
        anchors {
            top: itemHeader.bottom
            left: parent.left
            right: parent.right
            bottom: parent.bottom
        }
        visible: content !== null

        Component.onCompleted: {
            if (content) {
                content.parent = this
            }
        }
    }
}
