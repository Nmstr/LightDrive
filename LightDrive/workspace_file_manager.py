from PySide6.QtWidgets import QFileDialog
import tempfile
import tarfile
import shutil
import json
import os

def read_workspace_file(workspace_file_path: str) -> tuple[dict, dict, dict, list]:
    """
    Reads a workspace file and returns its contents.
    :param workspace_file_path: The path to the workspace file
    :return: The contents of the workspace file
    """
    tmp_dir = tempfile.mkdtemp()

    # Extract the file to a temporary location
    with tarfile.open(workspace_file_path) as tar:
        tar.extractall(path=tmp_dir)

    # Open the contents of the files and write them to variables
    if os.path.exists(os.path.join(tmp_dir, 'fixtures.json')):
        with open(os.path.join(tmp_dir, 'fixtures.json')) as f:
            fixtures = json.load(f)
    else:
        fixtures = {}

    if os.path.exists(os.path.join(tmp_dir, 'dmx_output_configuration.json')):
        with open(os.path.join(tmp_dir, 'dmx_output_configuration.json')) as f:
            dmx_output_configuration = json.load(f)
    else:
        dmx_output_configuration = {}

    if os.path.exists(os.path.join(tmp_dir, 'snippets.json')):
        with open(os.path.join(tmp_dir, 'snippets.json')) as f:
            snippets = json.load(f)
    else:
        snippets = {}

    if os.path.exists(os.path.join(tmp_dir, 'desk_configuration.json')):
        with open(os.path.join(tmp_dir, 'desk_configuration.json')) as f:
            desk_configuration = json.load(f)
    else:
        desk_configuration = []

    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)

    return fixtures, dmx_output_configuration, snippets, desk_configuration

def write_workspace_file(workspace_file_path: str, fixtures: list, dmx_output_configuration: dict, snippet_configuration: dict, desk_configuration: list) -> None:
    """
    Creates a workspace file
    :param workspace_file_path: The path to the workspace file
    :param fixtures: The fixtures available in the workspace
    :param dmx_output_configuration: The configuration of output
    :param snippet_configuration: The configuration of the snippets
    :param desk_configuration: The configuration of the control desk
    :return: None
    """
    tmp_dir = tempfile.mkdtemp()

    # Create files inside the tmp dir to create the workspace file later
    with tempfile.NamedTemporaryFile(dir=tmp_dir, delete=False) as fixtures_file:
        fixtures_file.write(json.dumps(fixtures, indent=4).encode())
    with tempfile.NamedTemporaryFile(dir=tmp_dir, delete=False) as dmx_output_file:
        dmx_output_file.write(json.dumps(dmx_output_configuration, indent=4).encode())
    with tempfile.NamedTemporaryFile(dir=tmp_dir, delete=False) as snippet_file:
        snippet_file.write(json.dumps(snippet_configuration, indent=4).encode())
    with tempfile.NamedTemporaryFile(dir=tmp_dir, delete=False) as desk_file:
        desk_file.write(json.dumps(desk_configuration, indent=4).encode())

    # Archive the files in the tmp dir into the workspace file
    with tarfile.open(workspace_file_path, "w") as archive:
        archive.add(fixtures_file.name, "fixtures.json")
        archive.add(dmx_output_file.name, "dmx_output_configuration.json")
        archive.add(snippet_file.name, "snippets.json")
        archive.add(desk_file.name, "desk_configuration.json")

    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)

class WorkspaceFileManager:
    def __init__(self, window, app, reboot_exit_code: int, current_workspace_file: str) -> None:
        """
        Creates the workspace file manager
        :param window: The main window of the application
        :param app: The app
        :param reboot_exit_code: The exit code for a reboot to start
        :param current_workspace_file: The current workspace file (provided when rebooting)
        """
        self.window = window
        self.app = app
        self.reboot_exit_code = reboot_exit_code
        self.current_workspace_file = current_workspace_file

    def new_workspace(self) -> None:
        """
        Creates a new workspace file by restarting the application empty
        :return: None
        """
        self.current_workspace_file = None
        self.app.exit(self.reboot_exit_code)

    def save_workspace_as(self) -> None:
        """
        Opens a file dialog to save the current workspace file
        :return: None
        """
        dlg = QFileDialog(self.window, directory=os.path.expanduser("~"))
        dlg.setNameFilter("Workspace (*.ldw)")
        dlg.setDefaultSuffix(".ldw")
        dlg.setAcceptMode(QFileDialog.AcceptSave)
        if dlg.exec():
            filename = dlg.selectedFiles()[0]
            self.current_workspace_file = filename
            self.save_workspace()

    def save_workspace(self) -> None:
        """
        Saves the current workspace by either saving it to current_workspace_file or prompting the use using save_workspace_as
        :return: None
        """
        if not self.current_workspace_file:
            self.save_workspace_as()
        else:
            snippet_configuration = self.get_snippet_configuration()
            write_workspace_file(workspace_file_path=self.current_workspace_file,
                                 fixtures=self.window.available_fixtures,
                                 dmx_output_configuration=self.window.dmx_output.get_configuration(),
                                 snippet_configuration=snippet_configuration,
                                 desk_configuration=self.window.control_desk_view.get_desk_configuration())

    def get_snippet_configuration(self) -> dict:
        """
        Gets the current snippet configuration
        :return: The current snippet configuration (dictionary)
        """
        snippet_selector = self.window.ui.snippet_selector_tree
        snippet_configuration = {}

        def add_directory_content(item):
            if item.extra_data["type"] == "directory":
                item.extra_data["content"] = []
                for j in range(item.childCount()):
                    child = item.child(j)
                    item.extra_data["content"].append(child.extra_data)
                    add_directory_content(child)

        for i in range(snippet_selector.topLevelItemCount()):
            item = snippet_selector.topLevelItem(i)
            snippet_configuration[str(i)] = item.extra_data
            add_directory_content(item)
        return snippet_configuration

    def show_open_workspace_dialog(self) -> None:
        """
        Shows the dialog to open a workspace file. It sets the workspace as the current_workspace_file and then restart the application, causing it to load the workspace using open_workspace
        :return: None
        """
        dlg = QFileDialog(self.window, directory=os.path.expanduser("~"))
        dlg.setNameFilter("Workspace (*.ldw)")
        dlg.setDefaultSuffix(".ldw")
        dlg.setFileMode(QFileDialog.ExistingFile)
        if dlg.exec():
            self.current_workspace_file = dlg.selectedFiles()[0]
            self.app.exit(self.reboot_exit_code)  # Restart application (opens workspace while opening)

    def open_workspace(self, workspace_file_path: str) -> None:
        """
        Loads the current workspace file (this runs on reboot)
        :param workspace_file_path: The path to the workspace file
        :return: None
        """
        fixtures, dmx_output_configuration, snippets, desk_configuration = read_workspace_file(workspace_file_path)
        # Configure the dmx output
        self.window.dmx_output.write_output_configuration(dmx_output_configuration)

        self.window.fixture_display_items()
        # Add the fixtures
        for fixture in fixtures:
            # Read the fixture data
            fixture_dir = os.getenv('XDG_CONFIG_HOME', default=os.path.expanduser('~/.config')) + '/LightDrive/fixtures/'
            with open(os.path.join(fixture_dir, fixture["id"] + ".json")) as f:
                fixture_data = json.load(f)
            # Add the fixture
            self.window.add_fixture(amount = 1,
                             fixture_data = fixture_data,
                             universe_uuid = fixture["universe"],
                             address = fixture["address"],
                             provided_uuid = fixture["fixture_uuid"])

        # Add the snippets
        def add_snippets_to_parent(snippets, parent):
            for snippet in snippets:
                match snippet["type"]:
                    case "cue":
                        self.window.snippet_manager.create_cue(extra_data=snippet, parent=parent)
                    case "scene":
                        self.window.snippet_manager.create_scene(extra_data=snippet, parent=parent)
                    case "efx_2d":
                        self.window.snippet_manager.create_efx_2d(extra_data=snippet, parent=parent)
                    case "rbg_matrix":
                        self.window.snippet_manager.create_rgb_matrix(extra_data=snippet, parent=parent)
                    case "script":
                        self.window.snippet_manager.create_script(extra_data=snippet, parent=parent)
                    case "directory":
                        new_parent = self.window.snippet_manager.create_dir(extra_data=snippet, parent=parent)
                        if "content" in snippet:
                            add_snippets_to_parent(snippet["content"], new_parent)

        for i, snippet in snippets.items():
            match snippet["type"]:
                case "cue":
                    self.window.snippet_manager.create_cue(extra_data=snippet)
                case "scene":
                    self.window.snippet_manager.create_scene(extra_data=snippet)
                case "efx_2d":
                    self.window.snippet_manager.create_efx_2d(extra_data=snippet)
                case "rbg_matrix":
                    self.window.snippet_manager.create_rgb_matrix(extra_data=snippet)
                case "script":
                    self.window.snippet_manager.create_script(extra_data=snippet)
                case "directory":
                    parent = self.window.snippet_manager.create_dir(extra_data=snippet)
                    if "content" in snippet:
                        add_snippets_to_parent(snippet["content"], parent)

        # Load the desk configuration
        self.window.control_desk_view.load_desk_configuration(desk_configuration)
