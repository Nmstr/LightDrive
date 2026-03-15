import QtQuick

Rectangle {
    id: rect
    x: 0
    y: 0
    width: 100
    height: 100

    DragHandler {
        target: parent
        acceptedModifiers: Qt.ControlModifier
        xAxis.enabled: true
        xAxis.minimum: 0
        xAxis.maximum: vConsole.width - rect.width
        yAxis.enabled: true
        yAxis.minimum: 0
        yAxis.maximum: vConsole.height - rect.height
    }

    MouseArea {
        anchors.fill: parent
        onDoubleClicked: (mouse) => {
            if (mouse.modifier === Qt.CtrlModifier) {
                if (typeof openConfig === "function") {
                    openConfig();
                } else {
                    console.log("WARNING: Missing VConsole item configuration page");
                }
            }
        }
    }
}
