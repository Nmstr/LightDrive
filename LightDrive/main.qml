import QtQuick
import QtQuick.Controls

ApplicationWindow {
    visible: true
    width: 1024
    height: 768
    title: "LightDrive"

    Rectangle {
        anchors.fill: parent
        color: "#303030"

        Header {
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
        }
    }
}
