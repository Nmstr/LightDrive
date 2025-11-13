import QtQuick
import QtQuick.Controls
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
                onClicked: add_universe_dialog.open()
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
        model: universeModel

        delegate: Rectangle {
            width: universeList.width
            height: 25
            color: "#555555"

            Text {
                anchors.centerIn: parent
                text: model.display
                color: "white"
                font.pixelSize: 20
            }
        }
    }

    Dialog {
        id: add_universe_dialog
        x: (parent.width - width) / 2
        y: (parent.height - height) / 2
        width: 300
        height: 100
        title: "Set Universe Name"
        standardButtons: Dialog.Ok | Dialog.Cancel

        onAccepted: {
            universeHandler.add_universe(universe_name_input.text);
            universe_name_input.clear();
        }

        Text {
            TextField {
                id: universe_name_input
                placeholderText: "Universe Name"
                width: 288
            }
        }
    }
}
