import QtQuick
import QtQuick.Controls

DeskBaseItem {
    id: faderItem
    width: 55
    height: 210

    headerText: "Fader"
    outputModel: faderOutputModel

    ListModel {
        id: faderOutputModel

        ListElement {
            type: "number"
        }
    }

    content: Item {
        anchors.fill: parent

        Column {
            id: faderColumn
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 10

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
                id: valueText
                anchors.horizontalCenter: parent.horizontalCenter
                text: "000"
            }
        }
    }
}
