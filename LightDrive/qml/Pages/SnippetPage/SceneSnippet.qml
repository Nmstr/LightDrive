import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Elements

Rectangle {
    id: sceneSnippetRoot
    color: "transparent"
    property string sceneUuid

    Rectangle {
        id: configTopper
        anchors {
            top: parent.top
            left: parent.left
            right: parent.right
        }
        height: 50
        color: "transparent"

        Row {
            anchors.verticalCenter: parent.verticalCenter
            spacing: 10

            Text {
                text: "Name:"
                color: "white"
                font.pixelSize: 20
            }

            TextField {
                id: sceneNameInput
                placeholderText: "Scene Name"
            }
        }
    }

    TabBar {
        id: sceneConfigTabBar
        anchors.top: configTopper.bottom
        width: parent.width

        TabButton {
            text: "Scene Configuration"
        }
        TabButton {
            text: "Fixture 1"
        }
    }

    StackLayout {
        anchors.top: sceneConfigTabBar.bottom
        anchors.bottom: parent.bottom
        width: parent.width
        currentIndex: sceneConfigTabBar.currentIndex

        Rectangle {
            id: sceneConfigTab
            color: "#444444"
            Row {
                anchors {
                    top: parent.top
                    left: parent.left
                    right: parent.right
                }
                height: 40
                spacing: 150

                TextIconButton {
                    iconSource: "qrc:/icons/add.svg"
                    labelText: "Add Fixture"
                    onClicked: addFixturePopup.open();
                }
                TextIconButton {
                    iconSource: "qrc:/icons/remove.svg"
                    labelText: "Remove Fixture"
                    onClicked: console.log("Remove Fixture")
                }
            }
        }
        Rectangle {
            id: fixtureTab
            color: "#444444"
            Row {
                id: fixtureTabButtonRow
                anchors {
                    top: parent.top
                    left: parent.left
                    right: parent.right
                }
                height: 40
                spacing: 100

                TextIconButton {
                    iconSource: "qrc:/icons/add.svg"
                    labelText: "Copy"
                    onClicked: console.log("Copy")
                }
                TextIconButton {
                    iconSource: "qrc:/icons/remove.svg"
                    labelText: "Paste"
                    onClicked: console.log("Paste")
                }
            }

            ListModel {
                id: sceneContentModel
                ListElement {address: 1}
                ListElement {address: 2}
                ListElement {address: 3}
            }
            ListView {
                anchors {
                    top: fixtureTabButtonRow.bottom
                    left: parent.left
                    right: parent.right
                    bottom: parent.bottom
                }
                orientation: ListView.Horizontal
                model: sceneContentModel
                clip: true
                spacing: 10

                delegate: Rectangle {
                    implicitWidth: channelColumn.width
                    implicitHeight: channelColumn.height
                    color: "transparent"

                    Column {
                        id: channelColumn
                        CheckBox {
                            anchors.horizontalCenter: parent.horizontalCenter
                            id: channelCheckBox
                        }
                        SpinBox {
                            anchors.horizontalCenter: parent.horizontalCenter
                            id: channelSpinBox
                            from: 0
                            to: 255
                            editable: true
                            onValueModified: channelFader.value = value;
                        }
                        Slider {
                            anchors.horizontalCenter: parent.horizontalCenter
                            id: channelFader
                            from: 0
                            to: 255
                            orientation: Qt.Vertical
                            onMoved: channelSpinBox.value = value;
                        }
                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter
                            id: channelAddress
                            text: model.address
                            color: "white"
                        }
                    }
                }
            }
        }
    }

    Popup {
        id: addFixturePopup
        x: (parent.width - width) / 2
        y: (parent.height - height) / 2
        width: parent.width - 150
        height: parent.height - 150
        padding: 0
        dim: true
        background: Rectangle {
            color: "#4f4f4f"
        }

        Rectangle {
            id: topper
            implicitWidth: parent.width
            height: 30
            color: "#2677ed"
            Text {
                anchors.fill: parent
                anchors.leftMargin: 10
                anchors.topMargin: 5
                text: "Add Fixture"
                font.pixelSize: 16
                color: "white"
            }
        }

        TreeView {
            id: fixtureTree
            anchors {
                top: topper.bottom
                left: parent.left
                right: parent.right
                bottom: footer.top
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
                onDoubleClicked: {
                    if (fixtureTree.depth(model.index) === 1) {
                        snippetHandler.get_scene_subhandler().add_fixture(sceneSnippetRoot.sceneUuid, model.uuid);
                        addFixturePopup.close();
                    }
                }
                Component.onCompleted: {
                    fixtureTree.expand(model.index);
                }
            }
        }

        Row {
            id: footer
            anchors {
                right: parent.right
                bottom: parent.bottom
                margins: 10
            }
            spacing: 10

            Button {
                id: cancelButton
                background: Rectangle {
                    color: cancelButton.down ? "#434343" : "#636363"
                    Rectangle {
                        anchors.bottom: parent.bottom
                        width: parent.width; height: 2
                        color: "#ff3030"
                    }
                }
                contentItem: Text {
                    text: "Cancel"
                    color: "white"
                    font.pointSize: 14
                }
                onClicked: addFixturePopup.close();
            }
        }
    }

    Connections {
        target: snippetHandler

        function onLoadScene(uuid, name) {
            sceneSnippetRoot.sceneUuid = uuid
            sceneNameInput.text = name
        }
    }
}
