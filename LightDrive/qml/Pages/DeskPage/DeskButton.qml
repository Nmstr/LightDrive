import QtQuick

DeskBaseItem {
    headerText: "Button"
    outputModel: buttonOutputModel

    ListModel {
        id: buttonOutputModel

        ListElement {
            type: "bool"
        }
    }
}
