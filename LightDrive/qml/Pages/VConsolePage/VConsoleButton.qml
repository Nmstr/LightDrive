import QtQuick

VConsoleBaseItem {
    Text {
        text: "Button"
    }
    function openConfig() {
        buttonConfigPopup.open()
    }

    ItemConfigurationPopup {
        id: buttonConfigPopup
        title: "Configure Button"

        content: Component {
            Rectangle {
                height: 300
                color: "#ff0000"
            }
        }

        function applyConfiguration() {
            console.log("Applying configuration for button");
        }
    }
}
