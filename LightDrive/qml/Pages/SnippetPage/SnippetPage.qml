import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Elements

Rectangle {
    id: snippetPage
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
                iconSource: "qrc:/icons/cue.svg"
                onClicked: console.log("Cue")
            }
            IconButton {
                iconSource: "qrc:/icons/scene.svg"
                onClicked: console.log("Scene")
            }
            IconButton {
                iconSource: "qrc:/icons/sequence.svg"
                onClicked: console.log("Sequence")
            }
            IconButton {
                iconSource: "qrc:/icons/efx_2d.svg"
                onClicked: console.log("2D Efx")
            }
            IconButton {
                iconSource: "qrc:/icons/rgb_matrix.svg"
                onClicked: console.log("RGB Matrix")
            }
            IconButton {
                iconSource: "qrc:/icons/script.svg"
                onClicked: console.log("Script")
            }
            IconButton {
                iconSource: "qrc:/icons/directory.svg"
                onClicked: console.log("Directory")
            }
            IconButton {
                iconSource: "qrc:/icons/sound_resource.svg"
                onClicked: console.log("Sound Resource")
            }
            IconButton {
                iconSource: "qrc:/icons/show.svg"
                onClicked: console.log("Show")
            }
        }
    }

    Row {
        anchors {
            top: buttonRow.bottom
            left: parent.left
            right: parent.right
            bottom: parent.bottom
        }
        spacing: 10

        TreeView {
            id: snippetTree
            width: parent.width / 2
            height: parent.height
            model: snippetModel
            clip: true

            delegate: TreeViewDelegate {
                implicitWidth: snippetTree.width
                text: model.display
                leftPadding: 30 + 20 * snippetTree.depth(model.index)
                onClicked: {
                    snippetTree.toggleExpanded(model.index);
                }
                Component.onCompleted: {
                    snippetTree.expand(model.index);
                }
            }
        }

        StackLayout {
            id: snippetStack
            width: parent.width / 2
            height: parent.height

            CueSnippet {}
            SceneSnippet {}
            SequenceSnippet {}
            Efx2DSnippet {}
            RgbMatrixSnippet {}
            ScriptSnippet {}
            DirectorySnippet {}
            SoundResourceSnippet {}
            ShowSnippet {}
        }
    }
}
