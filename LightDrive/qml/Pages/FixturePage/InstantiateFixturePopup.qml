import QtQuick
import QtQuick.Controls

Popup {
    id: instantiateFixturePopup
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
            text: "Instantiate Fixture"
            font.pixelSize: 16
            color: "white"
        }
    }

    Row {
        anchors {
            top: topper.bottom
            left: parent.left
            right: parent.right
            bottom: footer.bottom
            margins: 10
        }
        spacing: 10

        TreeView {
            id: availableFixtureTree
            width: (parent.width - parent.spacing) / 2
            height: parent.height
            model: fixtureBlueprintModel
            clip: true

            delegate: TreeViewDelegate {
                implicitWidth: availableFixtureTree.width
                text: model.display
                leftPadding: 30 + 20 * availableFixtureTree.depth(model.index)
                onClicked: {
                    availableFixtureTree.toggleExpanded(model.index);
                }
                Component.onCompleted: {
                    availableFixtureTree.expand(model.index);
                }
            }
        }

        Item {
            width: (parent.width - parent.spacing) / 2
            height: parent.height

            Text {
                id: fixtureNameInfo
                text: "Fixture Name:"
                color: "white"
                font.pointSize: 14
            }

            TextField {
                id: fixtureNameInput
                anchors {
                    left: fixtureNameInfo.right
                    leftMargin: 10
                    right: parent.right
                }
                placeholderText: "Fixture Name"
                color: "white"
                background: Rectangle {
                    color: "#636363"
                }
            }

            Text {
                id: universeSelectorInfo
                anchors.top: fixtureNameInfo.bottom
                text: "Universe:"
                color: "white"
                font.pointSize: 14
            }

            ComboBox {
                id: universeCombo
                model: universeModel
                anchors {
                    top: fixtureNameInfo.bottom
                    left: universeSelectorInfo.right
                    leftMargin: 10
                    right: parent.right
                }
            }

            Text {
                id: addressSelectorInfo
                anchors.top: universeSelectorInfo.bottom
                text: "Address:"
                color: "white"
                font.pointSize: 14
            }

            SpinBox {
                id: addressSpin
                anchors {
                    top: universeSelectorInfo.bottom
                    left: addressSelectorInfo.right
                    leftMargin: 10
                    right: parent.right
                }
                from: 1
                to: 512
                editable: true
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
            id: instantiateButton
            background: Rectangle {
                color: instantiateButton.down ? "#434343" : "#636363"
                Rectangle {
                    anchors.bottom: parent.bottom
                    width: parent.width; height: 2
                    color: "#2677ed"
                }
            }
            contentItem: Text {
                text: "Instantiate"
                color: "white"
                font.pointSize: 14
            }
            onClicked: {
                cleanup();
            }
        }
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
            onClicked: {
                cleanup()
            }
        }
    }

    function cleanup () {
        fixtureNameInput.clear();
        universeCombo.currentIndex = 0;
        addressSpin.value = 1;
        instantiateFixturePopup.close();
    }
}
