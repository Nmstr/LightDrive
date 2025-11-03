import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Pages.FixturePage 1.0
import Pages.SnippetPage 1.0
import Pages.ConsolePage 1.0
import Pages.ControlDeskPage 1.0
import Pages.IoPage 1.0

ApplicationWindow {
    visible: true
    width: 1024
    height: 768
    title: "LightDrive"

    Rectangle {
        anchors.fill: parent
        color: "#303030"

        Header {
            id: header
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
        }

        StackLayout {
            id: pageStack
            anchors {
                top: header.bottom
                left: parent.left
                right: parent.right
                bottom: parent.bottom
            }

            FixturePage { }
            SnippetPage { }
            ConsolePage { }
            ControlDeskPage { }
            IoPage { }
        }
    }
}
