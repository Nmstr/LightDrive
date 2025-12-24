import QtQuick

DeskBaseItem {
    Text {
        text: "Subdesk"
    }

    Rectangle {
        y: 20
        width: 15
        height: 15
        radius: 180
        color: "#009dff"
    }
    Rectangle {
        y: 40
        width: 15
        height: 15
        radius: 180
        color: "#009dff"
    }
    Rectangle {
        y: 60
        width: 15
        height: 15
        radius: 180
        color: "#009dff"
    }

    Rectangle {
        x: parent.width - width
        y: 40
        width: 15
        height: 15
        radius: 180
        color: "#ff7600"
    }
    Rectangle {
        x: parent.width - width
        y: 20
        width: 15
        height: 15
        radius: 180
        color: "#ff7600"
    }
}
