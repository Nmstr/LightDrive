import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Elements

Rectangle {
    color: "transparent"

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
                    onClicked: console.log("Add Fixture")
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

    Connections {
        target: snippetHandler

        function onLoadScene(name) {
            sceneNameInput.text = name
        }
    }
}
