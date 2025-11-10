import QtQuick
import QtQuick.Controls

Rectangle {
    id: consolePage
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

            Text {
                text: "Universe:"
                color: "white"
                font.pixelSize: 24
            }

            ComboBox {
                anchors.verticalCenter: parent.verticalCenter
                model: universeListModel
            }
        }
    }

    Rectangle {
        anchors {
            top: buttonRow.bottom
            left: parent.left
            right: parent.right
            bottom: parent.bottom
            margins: 10
        }
        color: "transparent"

        ScrollView {
            width: parent.width
            ScrollBar.horizontal.policy: ScrollBar.AlwaysOn

            ListView {
                width: parent.width
                spacing: 10
                model: 512
                orientation: ListView.Horizontal
                delegate: ChannelFader {}
            }
        }
    }
}
