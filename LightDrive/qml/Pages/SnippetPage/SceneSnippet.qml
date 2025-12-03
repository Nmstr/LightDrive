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
        Repeater {
            id: sceneFixtureTabRepeater
            model: undefined

            TabButton {
                text: model.display
            }
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
        Repeater {
            id: fixtureTabRepeater
            model: undefined

            Rectangle {
                id: fixtureTab
                property string fixtureUuid: model.uuid
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
                        iconSource: "qrc:/icons/copy.svg"
                        labelText: "Copy"
                        onClicked: console.log("Copy")
                    }
                    TextIconButton {
                        iconSource: "qrc:/icons/paste.svg"
                        labelText: "Paste"
                        onClicked: console.log("Paste")
                    }
                }

                ListView {
                    anchors {
                        top: fixtureTabButtonRow.bottom
                        left: parent.left
                        right: parent.right
                        bottom: parent.bottom
                    }
                    orientation: ListView.Horizontal
                    model: channelsModel
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
                                checkState: model.active
                                onToggled: snippetHandler.get_scene_subhandler().set_active(sceneUuid, fixtureUuid, index, checkState)
                            }
                            SpinBox {
                                anchors.horizontalCenter: parent.horizontalCenter
                                id: channelSpinBox
                                from: 0
                                to: 255
                                value: model.value
                                enabled: channelCheckBox.checkState
                                editable: true
                                onValueModified: {
                                    channelFader.value = value;
                                    snippetHandler.get_scene_subhandler().set_value(sceneUuid, fixtureUuid, index, value)
                                }
                            }
                            Slider {
                                anchors.horizontalCenter: parent.horizontalCenter
                                id: channelFader
                                from: 0
                                to: 255
                                value: model.value
                                enabled: channelCheckBox.checkState
                                orientation: Qt.Vertical
                                onMoved: {
                                    channelSpinBox.value = value;
                                    snippetHandler.get_scene_subhandler().set_value(sceneUuid, fixtureUuid, index, value)
                                }
                            }
                            Text {
                                anchors.horizontalCenter: parent.horizontalCenter
                                id: channelAddress
                                text: index
                                color: "white"
                            }
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

        function onLoadScene(uuid, name, channelModel) {
            sceneSnippetRoot.sceneUuid = uuid;
            sceneNameInput.text = name;
            fixtureTabRepeater.model = channelModel;
            sceneFixtureTabRepeater.model = channelModel;
        }
    }
}
