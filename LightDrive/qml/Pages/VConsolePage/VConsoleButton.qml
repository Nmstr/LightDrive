import QtQuick
import QtQuick.Controls
import Elements

VConsoleBaseItem {
    Text {
        text: "Button"
    }
    function openConfig() {
        buttonConfigPopup.open()
    }

    ItemConfigurationPopup {
        id: buttonConfigPopup
        title: "Configure Button"

        content: Component {
            Column {
                spacing: 3

                Text {
                    horizontalAlignment: Qt.AlignHCenter
                    width: parent.width
                    text: "General"
                    color: "#ffffff"
                }
                Row {
                    spacing: 3

                    Text {
                        verticalAlignment: Qt.AlignVCenter
                        height: parent.height
                        text: "Label:"
                        color: "#ffffff"
                    }
                    TextField {
                        id: labelInput
                        placeholderText: "Button"
                        color: "#ffffff"
                    }
                }
                Row {
                    spacing: 3

                    Text {
                        verticalAlignment: Qt.AlignVCenter
                        height: parent.height
                        text: "Snippet:"
                        color: "#ffffff"
                    }
                    TextField {
                        id: snippetField
                        readOnly: true
                        color: "#ffffff"
                    }
                    Button {
                        id: linkSnippetButton
                        text: "Link"
                    }
                    Button {
                        id: unlinkSnippetButton
                        text: "Unlink"
                    }
                }
                Text {
                    horizontalAlignment: Qt.AlignHCenter
                    width: parent.width
                    text: "Trigger"
                    color: "#ffffff"
                }
                Row {
                    spacing: 3

                    Text {
                        verticalAlignment: Qt.AlignVCenter
                        height: parent.height
                        text: "Hotkey:"
                        color: "#ffffff"
                    }
                    TextField {
                        id: hotkeyField
                        readOnly: true
                        color: "#ffffff"
                    }
                    Button {
                        id: selectHotkeyButton
                        text: "Select"
                    }
                    Button {
                        id: clearHotkeyButton
                        text: "Clear"
                    }
                }
                Text {
                    horizontalAlignment: Qt.AlignHCenter
                    width: parent.width
                    text: "Mode"
                    color: "#ffffff"
                }
                Row {
                    spacing: 3

                    Column {
                        spacing: 3

                        RadioButton {
                            id: modeToggleRadio
                            text: "Toggle"
                        }
                        RadioButton {
                            id: modeMomentaryRadio
                            text: "Momentary"
                        }
                        RadioButton {
                            id: modeFlashRadio
                            text: "Flash"
                        }
                        Component.onCompleted: {
                            modeToggleRadio.contentItem.color = "#ffffff"
                            modeMomentaryRadio.contentItem.color = "#ffffff"
                            modeFlashRadio.contentItem.color = "#ffffff"
                        }
                    }
                    Row {
                        Text {
                            verticalAlignment: Qt.AlignVCenter
                            height: parent.height
                            text: "Flash Duration:"
                            color: "#ffffff"
                        }
                        DoubleSpinBox {}
                    }
                }
            }
        }

        function applyConfiguration() {
            console.log("Applying configuration for button");
        }
    }
}
