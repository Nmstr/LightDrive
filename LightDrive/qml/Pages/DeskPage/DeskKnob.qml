import QtQuick
import QtQuick.Controls

DeskBaseItem {
    width: knobCircle.width + 15
    height: valueText.height + knobCircle.height + 25

    headerText: "Knob"

    content: Item {
        anchors.fill: parent

        Rectangle {
            id: knobCircle
            width: 50
            height: 50
            color: "#303030"
            radius: 180

            transform: Rotation {
                id: knobRotation
                origin.x: knobCircle.width / 2;
                origin.y: knobCircle.height / 2;
                angle: 0
            }

            Rectangle {
                x: (parent.width - width) / 2
                y: parent.height - height
                width: 10
                height: 10
                color: "#20ee00"
                radius: 180
            }
        }

        MouseArea {
            anchors.fill: knobCircle
            preventStealing: true
            onPositionChanged: {
                let rad = Math.atan2(mouse.x - knobCircle.width / 2, mouse.y - knobCircle.height / 2);
                let deg = rad * (180 / Math.PI);
                knobRotation.angle = -deg;

                let value = deg;
                if (value < 0) {
                    value = -value;
                } else {
                    value = 180 - value + 180;
                }
                valueText.text = Math.round(value);
            }
        }

        Text {
            id: valueText
            anchors.top: knobCircle.bottom
            anchors.horizontalCenter: parent.horizontalCenter
            text: "000"
        }
    }
}
