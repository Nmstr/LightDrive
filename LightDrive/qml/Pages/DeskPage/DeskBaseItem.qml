import QtQuick

Rectangle {
    id: baseItem
    x: 0
    y: 0
    width: 100
    height: 100

    required property string deskItemUuid
    required property string headerText
    property ListModel inputModel
    property ListModel outputModel
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

    Rectangle {
        id: itemInputs
        anchors.top: itemHeader.bottom
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        width: inputItemColumn.implicitWidth

        property bool isInputRect: true

        Column {
            id: inputItemColumn
            spacing: 5

            Repeater {
                model: baseItem.inputModel

                Rectangle {
                    width: 15
                    height: 15
                    radius: 180
                    color: baseItem.getConnectorColor(model.type)
                }
            }
        }
    }

    Rectangle {
        id: itemOutputs
        anchors.top: itemHeader.bottom
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        width: outputItemColumn.implicitWidth

        property bool isOutputRect: true

        Column {
            id: outputItemColumn
            spacing: 5

            Repeater {
                id: outputItemRepeater
                model: baseItem.outputModel

                Rectangle {
                    width: 15
                    height: 15
                    radius: 180
                    color: baseItem.getConnectorColor(model.type)
                }
            }
        }
    }

    function getConnectorColor(type) {
        if (type === "bool") {
            return "#3bd100";
        } else if (type === "number") {
            return "#009dff"
        }
    }

    Item {
        anchors {
            top: itemHeader.bottom
            left: itemInputs.right
            right: itemOutputs.left
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
