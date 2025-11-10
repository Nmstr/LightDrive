import QtQuick
import Elements

Rectangle {
    id: ioPage
    color: "transparent"

    Rectangle {
        id: buttonRow
        width: parent.width
        height: 50
        color: "#555555"

        Row {
            anchors {
                left: parent.left
                verticalCenter: parent.verticalCenter
                leftMargin: 10
            }
            spacing: 10

            IconButton {
                iconSource: "qrc:/icons/add.svg"
                onClicked: console.log("Add")
            }
            IconButton {
                iconSource: "qrc:/icons/remove.svg"
                onClicked: console.log("Remove")
            }
        }
    }

    ListView {
        id: universeList
        anchors {
            top: buttonRow.bottom
            left: parent.left
            right: parent.right
            bottom: parent.bottom
            margins: 10
        }
        model: universeListModel

        delegate: Rectangle {
            width: parent.width
            height: 25
            color: "#555555"

            Text {
                anchors.centerIn: parent
                text: modelData
                color: "white"
                font.pixelSize: 20
            }
        }
    }
}
