import QtQuick
import Elements

Rectangle {
    id: controlDeskPage
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
                iconSource: "qrc:/icons/desk_button.svg"
                onClicked: console.log("button")
            }
            IconButton {
                iconSource: "qrc:/icons/desk_fader.svg"
                onClicked: console.log("fader")
            }
            IconButton {
                iconSource: "qrc:/icons/desk_knob.svg"
                onClicked: console.log("knob")
            }
            IconButton {
                iconSource: "qrc:/icons/desk_sound_trigger.svg"
                onClicked: console.log("sound_trigger")
            }
            IconButton {
                iconSource: "qrc:/icons/desk_label.svg"
                onClicked: console.log("label")
            }
            IconButton {
                iconSource: "qrc:/icons/desk_clock.svg"
                onClicked: console.log("clock")
            }
            IconButton {
                iconSource: "qrc:/icons/desk_subdesk.svg"
                onClicked: console.log("subdesk")
            }
        }
    }

    Rectangle {
        id: desk
        anchors {
            top: buttonRow.bottom
            left: parent.left
            right: parent.right
            bottom: parent.bottom
            margins: 10
        }
        color: "#555555"

        DeskButton {x: 100; y: 100}
        DeskFader {x: 250; y: 100}
        DeskKnob {x: 300; y: 100}
        DeskLabel {x: 100; y: 50}
        DeskClock {x: 250; y: 50}
        DeskSubdesk {x: 100; y: 250}
    }
}
