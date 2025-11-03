import QtQuick

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

        CollapsibleButton {
            iconSource: "qrc:/icons/fixture_page.svg"
            labelText: "Fixtures"
        }
        CollapsibleButton {
            iconSource: "qrc:/icons/snippet_page.svg"
            labelText: "Snippets"
        }
        CollapsibleButton {
            iconSource: "qrc:/icons/console_page.svg"
            labelText: "Console"
        }
        CollapsibleButton {
            iconSource: "qrc:/icons/control_desk_page.svg"
            labelText: "Control Desk"
        }
        CollapsibleButton {
            iconSource: "qrc:/icons/io_page.svg"
            labelText: "I/O"
        }
    }
}
