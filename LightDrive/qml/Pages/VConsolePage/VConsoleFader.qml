import QtQuick
import QtQuick.Controls

VConsoleBaseItem {
    width: faderColumn.implicitWidth
    height: faderColumn.implicitHeight

    Column {
        id: faderColumn
        anchors.fill: parent
        spacing: 10

        Text {
            id: valueText
            anchors.horizontalCenter: parent.horizontalCenter
            text: "000"
        }
        Slider {
            id: slider
            anchors.horizontalCenter: parent.horizontalCenter
            orientation: Qt.Vertical
            from: 0
            to: 255
            stepSize: 1
            onMoved: valueText.text = value
        }
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: "Fader"
        }
    }
}
