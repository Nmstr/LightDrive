import QtQuick

DeskBaseItem {
    height: 25

    content: Item {
        Text {
            id: clock
            text: Qt.formatTime(new Date(), "hh:mm:ss")
        }
        Timer {
            interval: 100
            running: true
            repeat: true
            onTriggered: clock.text = Qt.formatTime(new Date(), "hh:mm:ss")
        }
    }
}
