import QtQuick

DeskBaseItem {
    height: 25

    headerText: Qt.formatTime(new Date(), "hh:mm:ss")

    Timer {
        interval: 100
        running: true
        repeat: true
        onTriggered: headerText = Qt.formatTime(new Date(), "hh:mm:ss")
    }
}
