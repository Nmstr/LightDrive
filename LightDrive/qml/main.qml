import QtCore
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import Pages.FixturePage 1.0
import Pages.SnippetPage 1.0
import Pages.EditorPage 1.0
import Pages.VConsolePage 1.0
import Pages.IoPage 1.0
import Elements

ApplicationWindow {
    visible: true
    width: 1024
    height: 768
    title: "LightDrive"

    Rectangle {
        anchors.fill: parent
        color: "#303030"

        Header {
            id: header
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
        }

        StackLayout {
            id: pageStack
            anchors {
                top: header.bottom
                left: parent.left
                right: parent.right
                bottom: parent.bottom
            }

            FixturePage { }
            SnippetPage { }
            EditorPage { }
            VConsolePage { }
            IoPage { }
        }

        Popup {
            id: workspacePopout
            x: 10
            y: 50
            width: 200
            background: Rectangle {
                color: "#2d2d2d"
            }

            Column {
                anchors.fill: parent
                spacing: 10

                TextIconButton {
                    iconSource: "qrc:/icons/new.svg"
                    labelText: "New"
                    onClicked: {
                        workspacePopout.close();
                        workspaceHandler.new();
                    }
                }
                TextIconButton {
                    iconSource: "qrc:/icons/open.svg"
                    labelText: "Open"
                    onClicked: openFileDialog.open()
                }
                TextIconButton {
                    iconSource: "qrc:/icons/save.svg"
                    labelText: "Save"
                    onClicked: {
                        workspaceHandler.save();
                        workspacePopout.close();
                    }
                }
                TextIconButton {
                    iconSource: "qrc:/icons/save_as.svg"
                    labelText: "Save As"
                    onClicked: saveAsFileDialog.open()
                }
            }

            FileDialog {
                id: saveAsFileDialog
                currentFolder: StandardPaths.standardLocations(StandardPaths.HomeLocation)[0]
                fileMode: FileDialog.SaveFile
                defaultSuffix: "ldw"
                nameFilters: ["Workspace Files (*.ldw)", "All Files (*)"]
                onAccepted: workspaceHandler.save_as(selectedFile)
            }
            FileDialog {
                id: openFileDialog
                currentFolder: StandardPaths.standardLocations(StandardPaths.HomeLocation)[0]
                fileMode: FileDialog.OpenFile
                defaultSuffix: "ldw"
                nameFilters: ["Workspace Files (*.ldw)", "All Files (*)"]
                onAccepted: workspaceHandler.open(selectedFile)
            }
        }
    }

    Connections {
        target: workspaceHandler

        function onPromptSaveAs() {
            saveAsFileDialog.open();
        }
    }
}
