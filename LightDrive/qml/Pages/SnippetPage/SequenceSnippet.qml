import QtQuick
import QtQuick.Controls
import Elements

Rectangle {
    id: sequenceSnippetRoot
    color: "transparent"
    property string sequenceUuid

    Rectangle {
        id: topper
        anchors {
            top: parent.top
            left: parent.left
            right: parent.right
        }
        implicitHeight: topperColumn.height
        color: "transparent"

        Column {
            id: topperColumn
            anchors.verticalCenter: parent.verticalCenter
            spacing: 10
            padding: 10

            Row {
                spacing: 10

                Text {
                    text: "Name:"
                    color: "white"
                    font.pixelSize: 20
                }

                TextField {
                    id: sequenceNameInput
                    placeholderText: "Sequence Name"
                    onEditingFinished: snippetHandler.set_snippet_name(sequenceUuid, text)
                }
            }
            Row {
                spacing: 125

                TextIconButton {
                    iconSource: "qrc:/icons/add.svg"
                    labelText: "Add Scene"
                    onClicked: addScenePopup.open();
                }
                TextIconButton {
                    iconSource: "qrc:/icons/remove.svg"
                    labelText: "Remove Scene"
                    onClicked: console.log("remove scene")
                }
            }
        }
    }

    ListView {
        id: sequenceSceneEntryListView
        anchors {
            top: topper.bottom
            left: parent.left
            right: parent.right
            bottom: parent.bottom
        }
        model: undefined

        header: Rectangle {
            width: parent.width
            height: childrenRect.height

            Text {
                text: "Scene Name\tFade In\tDuration\tFade Out"
            }
        }

        delegate: Rectangle {
            width: parent.width
            height: childrenRect.height

            Text {
                text: model.display + "\t" + model.fadeIn + "ms\t" + model.duration + "ms\t" + model.fadeOut + "ms"
            }
        }
    }

    Connections {
        target: snippetHandler

        function onLoadSequence(uuid, name, sequenceModel) {
            sequenceNameInput.text = name;
            sequenceSnippetRoot.sequenceUuid = uuid;
            sequenceSceneEntryListView.model = undefined;  // This is required for the ListView the recognize a change in the model.
                                                           // For some reason this is only _sometimes_ required... weird.
            sequenceSceneEntryListView.model = sequenceModel;
        }
    }

    Popup {
        id: addScenePopup
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
            id: popupTopper
            implicitWidth: parent.width
            height: 30
            color: "#2677ed"
            Text {
                anchors.fill: parent
                anchors.leftMargin: 10
                anchors.topMargin: 5
                text: "Add Scene"
                font.pixelSize: 16
                color: "white"
            }
        }

        TreeView {
            id: snippetTree
            anchors {
                top: popupTopper.bottom
                left: parent.left
                right: parent.right
                bottom: footer.top
            }
            model: snippetModel
            clip: true

            delegate: TreeViewDelegate {
                implicitWidth: snippetTree.width
                text: model.display
                leftPadding: 30 + 20 * snippetTree.depth(model.index)
                onClicked: {
                    snippetTree.toggleExpanded(model.index);
                }
                onDoubleClicked: {
                    snippetHandler.get_sequence_subhandler().add_scene(sequenceSnippetRoot.sequenceUuid, model.uuid);
                    addScenePopup.close();
                }
            }
            Component.onCompleted: {
                snippetTree.expand(model.index);
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
                onClicked: addScenePopup.close();
            }
        }
    }
}
