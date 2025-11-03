import QtQuick
import QtQuick.Controls
import Elements

Rectangle {
    id: fixturePage
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

    TreeView {
        id: fixtureTree
        anchors {
            top: buttonRow.bottom
            left: parent.left
            right: parent.right
            bottom: parent.bottom
        }
        model: fixturesModel
        clip: true

        delegate: TreeViewDelegate {
            implicitWidth: fixtureTree.width
            text: model.display
            leftPadding: 30 + 20 * fixtureTree.depth(model.index)
            onClicked: {
                fixtureTree.toggleExpanded(model.index);
            }
            Component.onCompleted: {
                fixtureTree.expand(model.index);
            }
        }
    }
}
