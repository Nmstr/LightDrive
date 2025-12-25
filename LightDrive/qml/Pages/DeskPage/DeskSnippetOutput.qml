import QtQuick

DeskBaseItem {
    headerText: "Snippet Output"
    inputModel: snippetOutputInputModel

    ListModel {
        id: snippetOutputInputModel

        ListElement {
            type: "bool"
        }
    }
}
