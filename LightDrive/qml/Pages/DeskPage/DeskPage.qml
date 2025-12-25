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

        property point drawingWireStart: Qt.point(-12345, -12345)  // Impossible point by default
        property point drawingWireEnd: Qt.point(-12345, -12345)

        Canvas {
            id: wireCanvas
            anchors.fill: parent
            onPaint: {
                let ctx = getContext("2d");
                ctx.reset();

                if (desk.drawingWireStart !== desk.drawingWireEnd) {
                    ctx.beginPath();
                    ctx.strokeStyle = "#FF0000"
                    ctx.moveTo(desk.drawingWireStart.x + 15, desk.drawingWireStart.y + 7.5);
                    ctx.lineTo(desk.drawingWireEnd.x, desk.drawingWireEnd.y);
                    ctx.closePath();
                    ctx.stroke();
                }
            }
        }

        MouseArea {
            anchors.fill: parent
            onPressed: (mouse) => {
                let outputConnector = getOutputConnector(mouse.x, mouse.y);
                if (!outputConnector) {
                    return;  // No connector was pressed
                }
                console.log(outputConnector);
                let deskConnectorPos = desk.mapFromGlobal(outputConnector.mapToGlobal(outputConnector.x, outputConnector.y))
                desk.drawingWireStart = Qt.point(deskConnectorPos.x, deskConnectorPos.y);
            }
            onPositionChanged: (mouse) => {
                if (desk.drawingWireStart === Qt.point(-12345, -12345)) {
                    return;  // Wire has no valid start point (not dragged from output)
                }
                desk.drawingWireEnd = Qt.point(mouse.x, mouse.y);
                wireCanvas.requestPaint();
            }
            onReleased: (mouse) => {
                desk.drawingWireStart = Qt.point(-12345, -12345)
                desk.drawingWireEnd = Qt.point(-12345, -12345)
                wireCanvas.requestPaint();
            }

            function getOutputConnector(x, y): QQuickRectangle {
                let globalClickPos = desk.mapToGlobal(x, y);

                // This code is awful. I hate it. But it works.
                for (let i = 0; i < deskContentRepeater.count; i++) {  // Iterate over elements in repeater
                    let deskItem = deskContentRepeater.itemAt(i).children[0];  // children[0] is because each DeskItem is wrapped in an Item
                    let localClickPos = deskItem.mapFromGlobal(globalClickPos);
                    if (deskItem.contains(localClickPos)) {  // current DeskItem is clicked DeskItem (else next in iteration)
                        if (deskItem.childAt(localClickPos.x, localClickPos.y)) {  // There is smth at the clicked pos
                            if (deskItem.childAt(localClickPos.x, localClickPos.y).isOutputRect) {  // The clicked thing is the rect containing the connectors
                                let outputConnectorCol = deskItem.childAt(localClickPos.x, localClickPos.y).children[0];  // Remove the Rectangle wrapping the Column containing the connectors
                                let internalClickPos = outputConnectorCol.mapFromGlobal(globalClickPos);  // Local click pos inside the Column
                                let clickedConnector = outputConnectorCol.childAt(internalClickPos.x, internalClickPos.y);  // Finally, the connector actually clicked
                                return clickedConnector;
                            }
                        }
                    }
                }
            }
        }

        Item {
            id: deskContent
            anchors.fill: parent

            Repeater {
                id: deskContentRepeater
                model: deskContentModel

                Item {
                    visible: false

                    Component.onCompleted: {
                        if (model.itemType === "DeskButton") {
                            let component = Qt.createComponent("DeskButton.qml");
                            component.createObject(this, {
                                x: model.x,
                                y: model.y,
                                width: model.width,
                                height: model.height
                            });
                        } else if (model.itemType === "DeskFader") {
                            let component = Qt.createComponent("DeskFader.qml");
                            component.createObject(this, {
                                x: model.x,
                                y: model.y,
                                width: model.width,
                                height: model.height
                            });
                        } else if (model.itemType === "DeskKnob") {
                            let component = Qt.createComponent("DeskKnob.qml");
                            component.createObject(this, {
                                x: model.x,
                                y: model.y,
                                width: model.width,
                                height: model.height
                            });
                        } else if (model.itemType === "DeskLabel") {
                            let component = Qt.createComponent("DeskLabel.qml");
                            component.createObject(this, {
                                x: model.x,
                                y: model.y,
                                width: model.width,
                                height: model.height
                            });
                        } else if (model.itemType === "DeskClock") {
                            let component = Qt.createComponent("DeskClock.qml");
                            component.createObject(this, {
                                x: model.x,
                                y: model.y,
                                width: model.width,
                                height: model.height
                            });
                        } else if (model.itemType === "DeskSubdesk") {
                            let component = Qt.createComponent("DeskSubdesk.qml");
                            component.createObject(this, {
                                x: model.x,
                                y: model.y,
                                width: model.width,
                                height: model.height
                            });
                        } else if (model.itemType === "DeskSnippetOutput") {
                            let component = Qt.createComponent("DeskSnippetOutput.qml");
                            component.createObject(this, {
                                x: model.x,
                                y: model.y,
                                width: model.width,
                                height: model.height
                            });
                        }
                        this.visible = true;
                    }
                }
            }
        }
    }
}
