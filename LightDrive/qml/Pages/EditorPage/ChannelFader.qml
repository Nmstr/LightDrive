import QtQuick
import QtQuick.Controls
import Elements

Column {
    spacing: 10

    Slider {
        id: fader
        anchors.horizontalCenter: parent.horizontalCenter
        from: 0
        to: 255
        orientation: Qt.Vertical

        onMoved: {
            box.value = value;
        }
    }

    SpinBox {
        id: box
        anchors.horizontalCenter: parent.horizontalCenter
        width: 50
        from: 0
        to: 255
        editable: true

        onValueModified: {
            fader.value = value;
        }
    }

    IconButton {
        id: resetButton
        anchors.horizontalCenter: parent.horizontalCenter
        iconSource: "qrc:/icons/channel_reset.svg"
        onClicked: {
            fader.value = 0;
            box.value = 0;
        }
    }
}
