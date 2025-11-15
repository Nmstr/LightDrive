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
        property string curUuid
        property int curIndex: -1

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

            MouseArea {
                anchors.fill: parent
                hoverEnabled: true

                onEntered: {
                    if (universeList.curUuid === model.uuid) return;
                    parent.color = "#444444";
                }
                onExited:  {
                    if (universeList.curUuid === model.uuid) return;
                    parent.color = "#555555";
                }
                onClicked: {
                    let lastElement = universeList.itemAtIndex(universeList.curIndex);
                    if (lastElement) lastElement.color = "#555555";
                    parent.color = "#666666";
                    universeList.curUuid = model.uuid;
                    universeList.curIndex = model.index;
                }
            }
        }
    }

    Popup {
        id: add_universe_dialog
        x: (parent.width - width) / 2
        y: (parent.height - height) / 2
        width: 400
        height: 95
        padding: 0
        background: Rectangle {
            color: "#4f4f4f"
        }

        Column {
            width: parent.width
            spacing: 5

            Rectangle {
                id: topper
                implicitWidth: parent.width
                height: 30
                color: "#2677ed"
                Text {
                    anchors.fill: parent
                    anchors.margins: 5
                    text: "Set Universe Name"
                    font.pixelSize: 16
                    color: "white"
                }
            }

            TextField {
                id: universe_name_input
                anchors.right: parent.right
                anchors.rightMargin: 5
                implicitWidth: parent.width - 10
                placeholderText: "Universe Name"
                color: "white"
                background: Rectangle {
                    color: "#636363"
                }
            }

            Row {
                anchors.right: parent.right
                anchors.rightMargin: 5
                spacing: 5

                Button {
                    id: createButton
                    text: "Create"
                    background: Rectangle {
                        color: createButton.down ? "#434343" : "#636363"
                        Rectangle {
                            anchors.bottom: parent.bottom
                            width: parent.width; height: 2
                            color: "#2677ed"
                        }
                    }
                    onClicked: {
                        universeHandler.add_universe(universe_name_input.text);
                        universe_name_input.clear();
                        add_universe_dialog.close();
                    }
                }
                Button {
                    id: cancelButton
                    text: "Cancel"
                    background: Rectangle {
                        color: cancelButton.down ? "#434343" : "#636363"
                        Rectangle {
                            anchors.bottom: parent.bottom
                            width: parent.width; height: 2
                            color: "#ff3030"
                        }
                    }
                    onClicked: {
                        universe_name_input.clear();
                        add_universe_dialog.close();
                    }
                }
            }
        }
    }
}
