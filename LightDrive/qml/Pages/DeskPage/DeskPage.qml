import QtQuick
import Elements

Rectangle {
    id: deskPage
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

        Item {
            id: deskContent
            anchors.fill: parent

            Repeater {
                model: deskContentModel

                Item {
                    visible: false

                    Component.onCompleted: {
                        if (model.itemType === "DeskButton") {
                            let component = Qt.createComponent("DeskButton.qml");
                            component.createObject(deskContent, {
                                x: model.x,
                                y: model.y,
                                width: model.width,
                                height: model.height
                            });
                        } else if (model.itemType === "DeskFader") {
                            let component = Qt.createComponent("DeskFader.qml");
                            component.createObject(deskContent, {
                                x: model.x,
                                y: model.y,
                                width: model.width,
                                height: model.height
                            });
                        } else if (model.itemType === "DeskKnob") {
                            let component = Qt.createComponent("DeskKnob.qml");
                            component.createObject(deskContent, {
                                x: model.x,
                                y: model.y,
                                width: model.width,
                                height: model.height
                            });
                        } else if (model.itemType === "DeskLabel") {
                            let component = Qt.createComponent("DeskLabel.qml");
                            component.createObject(deskContent, {
                                x: model.x,
                                y: model.y,
                                width: model.width,
                                height: model.height
                            });
                        } else if (model.itemType === "DeskClock") {
                            let component = Qt.createComponent("DeskClock.qml");
                            component.createObject(deskContent, {
                                x: model.x,
                                y: model.y,
                                width: model.width,
                                height: model.height
                            });
                        } else if (model.itemType === "DeskSubdesk") {
                            let component = Qt.createComponent("DeskSubdesk.qml");
                            component.createObject(deskContent, {
                                x: model.x,
                                y: model.y,
                                width: model.width,
                                height: model.height
                            });
                        } else if (model.itemType === "DeskSnippetOutput") {
                            let component = Qt.createComponent("DeskSnippetOutput.qml");
                            component.createObject(deskContent, {
                                x: model.x,
                                y: model.y,
                                width: model.width,
                                height: model.height
                            });
                        }
                    }
                }
            }
        }
    }
}
