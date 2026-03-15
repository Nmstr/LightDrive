import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Popup {
    id: configPopup
    parent: Overlay.overlay
    x: Math.round((parent.width - width) / 2)
    y: Math.round((parent.height - height) / 2)
    padding: 3
    dim: true

    required property string title
    required property Component content

    background: Rectangle {
        color: "#4f4f4f"
        border.color: "#2d2d2d"
        border.width: 3
    }

    ColumnLayout {
        spacing: 0

        Rectangle {
            id: topper
            implicitWidth: parent.width
            height: 30
            color: "#2677ed"
            Text {
                anchors.fill: parent
                anchors.leftMargin: 10
                anchors.topMargin: 5
                text: configPopup.title
                font.pixelSize: 16
                color: "white"
            }
        }

        Loader {
            id: contentLoaer
            Layout.fillWidth: true
            sourceComponent: configPopup.content
        }

        RowLayout {
            id: footer
            Layout.alignment: Qt.AlignRight
            spacing: 10

            Button {
                id: applyAndCloseButton
                background: Rectangle {
                    color: applyAndCloseButton.down ? "#434343" : "#636363"
                    Rectangle {
                        anchors.bottom: parent.bottom
                        width: parent.width; height: 2
                        color: "#2677ed"
                    }
                }
                contentItem: Text {
                    text: "Apply and Close"
                    color: "white"
                    font.pointSize: 14
                }
                onClicked: {
                    configPopup.applyConfiguration();
                    configPopup.close();
                }
            }
            Button {
                id: applyButton
                background: Rectangle {
                    color: applyButton.down ? "#434343" : "#636363"
                    Rectangle {
                        anchors.bottom: parent.bottom
                        width: parent.width; height: 2
                        color: "#2677ed"
                    }
                }
                contentItem: Text {
                    text: "Apply"
                    color: "white"
                    font.pointSize: 14
                }
                onClicked: {
                    configPopup.applyConfiguration();
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
                onClicked: configPopup.close();
            }
        }
    }

    function applyConfiguration() {
        console.log("WARNING: applyConfiguration needs to be overridden");
    }
}
