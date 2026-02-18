import QtQuick
import Elements

Rectangle {
    id: vConsolePage
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
                iconSource: "qrc:/icons/v_console_button.svg"
                onClicked: console.log("button")
            }
            IconButton {
                iconSource: "qrc:/icons/v_console_fader.svg"
                onClicked: console.log("fader")
            }
            IconButton {
                iconSource: "qrc:/icons/v_console_knob.svg"
                onClicked: console.log("knob")
            }
            IconButton {
                iconSource: "qrc:/icons/v_console_sound_trigger.svg"
                onClicked: console.log("sound_trigger")
            }
            IconButton {
                iconSource: "qrc:/icons/v_console_label.svg"
                onClicked: console.log("label")
            }
            IconButton {
                iconSource: "qrc:/icons/v_console_clock.svg"
                onClicked: console.log("clock")
            }
        }
    }

    Rectangle {
        id: vConsole
        anchors {
            top: buttonRow.bottom
            left: parent.left
            right: parent.right
            bottom: parent.bottom
            margins: 10
        }
        color: "#555555"

        VConsoleButton {x: 100; y: 100}
        VConsoleFader {x: 250; y: 100}
        VConsoleKnob {x: 300; y: 100}
        VConsoleLabel {x: 100; y: 50}
        VConsoleClock {x: 250; y: 50}
    }
}
