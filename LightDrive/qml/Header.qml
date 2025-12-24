import QtQuick
import Elements 1.0

Rectangle {
    id: header
    implicitHeight: 50
    color: "#2980ff"

    Row {
        anchors {
            left: parent.left
            verticalCenter: parent.verticalCenter
            leftMargin: 10
        }
        spacing: 10

        IconButton {
            iconSource: "qrc:/icons/lightdrive.svg"
            onClicked: workspacePopout.open()
        }
        CollapsibleButton {
            iconSource: "qrc:/icons/fixture_page.svg"
            labelText: "Fixtures"
            destinationIndex: 0
        }
        CollapsibleButton {
            iconSource: "qrc:/icons/snippet_page.svg"
            labelText: "Snippets"
            destinationIndex: 1
        }
        CollapsibleButton {
            iconSource: "qrc:/icons/console_page.svg"
            labelText: "Console"
            destinationIndex: 2
        }
        CollapsibleButton {
            iconSource: "qrc:/icons/desk_page.svg"
            labelText: "Desk"
            destinationIndex: 3
        }
        CollapsibleButton {
            iconSource: "qrc:/icons/io_page.svg"
            labelText: "I/O"
            destinationIndex: 4
        }
    }
}
