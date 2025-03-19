from Workspace.Snippets.scene import SceneData
from Workspace.Snippets.sequence import SequenceData
from Workspace.Snippets.cue import CueData
from Workspace.Snippets.rgb_matrix import RgbMatrixData
from Workspace.Snippets.script import ScriptData
from Workspace.Snippets.two_d_efx import TwoDEfxData
from Workspace.Snippets.directory import DirectoryData
from Workspace.Snippets.sound_resource import SoundResourceData
from Workspace.Snippets.show import ShowData
from PySide6.QtWidgets import QFileDialog
from dataclasses import asdict
import tempfile
import tarfile
import shutil
import json
import os

def read_workspace_file(workspace_file_path: str, sr_tmp_dir: str) -> tuple[dict, dict, list, list]:
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

    snippets = []
    if os.path.exists(os.path.join(tmp_dir, 'snippets')):
        for file in os.listdir(os.path.join(tmp_dir, 'snippets')):
            with open(os.path.join(tmp_dir, 'snippets', file)) as f:
                snippets.append(json.load(f))

    if os.path.exists(os.path.join(tmp_dir, 'desk_configuration.json')):
        with open(os.path.join(tmp_dir, 'desk_configuration.json')) as f:
            desk_configuration = json.load(f)
    else:
        desk_configuration = []

    if os.path.exists(os.path.join(tmp_dir, 'sound_resources')):
        shutil.copytree(os.path.join(tmp_dir, 'sound_resources'), sr_tmp_dir, dirs_exist_ok=True)

    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)

    return fixtures, dmx_output_configuration, snippets, desk_configuration

def write_workspace_file(workspace_file_path: str, fixtures: list,
                         dmx_output_configuration: dict,
                         snippet_configuration: list,
                         desk_configuration: list,
                         sound_resource_tmp_dir: str) -> None:
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

    # Create temp file for the fixtures
    with tempfile.NamedTemporaryFile(dir=tmp_dir, delete=False) as fixtures_file:
        fixtures_file.write(json.dumps(fixtures, indent=4).encode())

    # Create temp file for the dmx output
    with tempfile.NamedTemporaryFile(dir=tmp_dir, delete=False) as dmx_output_file:
        dmx_output_file.write(json.dumps(dmx_output_configuration, indent=4).encode())

    # Create temp files for the snippets
    snippet_dir = os.path.join(tmp_dir, "snippets")
    os.makedirs(snippet_dir)
    snippet_files = {}
    for snippet in snippet_configuration:
        with tempfile.NamedTemporaryFile(dir=tmp_dir, delete=False) as snippet_file:
            snippet_file.write(json.dumps(snippet, indent=4).encode())
        snippet_files[snippet_file.name] = snippet

    # Create temp file for the desk
    with tempfile.NamedTemporaryFile(dir=tmp_dir, delete=False) as desk_file:
        desk_file.write(json.dumps(desk_configuration, indent=4).encode())

    # Create temp dir for the sound resources and copy them into it
    sound_resource_dir = os.path.join(tmp_dir, "sound_resources")
    os.makedirs(sound_resource_dir)
    shutil.copytree(sound_resource_tmp_dir, sound_resource_dir, dirs_exist_ok=True)

    # Add the files to the archive
    with tarfile.open(workspace_file_path, "w") as archive:
        archive.add(fixtures_file.name, "fixtures.json")
        archive.add(dmx_output_file.name, "dmx_output_configuration.json")
        archive.add(desk_file.name, "desk_configuration.json")
        archive.add(snippet_dir, "snippets")
        for snippet_file, snippet in snippet_files.items():
            file_name = os.path.join("snippets", f"{snippet['name'].lower().replace(' ', '_')}-{snippet['uuid']}.json")
            archive.add(snippet_file, file_name)
        archive.add(sound_resource_dir, "sound_resources")

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
                                 desk_configuration=self.window.control_desk_view.get_desk_configuration(),
                                 sound_resource_tmp_dir=self.window.snippet_manager.sound_resource_manager.sr_tmp_dir)

    def get_snippet_configuration(self) -> list:
        """
        Gets the current snippet configuration
        :return: A list of the current snippet configuration
        """
        snippets = []
        for uuid, snippet in self.window.snippet_manager.available_snippets.items():
            snippets.append(asdict(snippet))
        return snippets

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
        fixtures, dmx_output_configuration, snippets, desk_configuration = read_workspace_file(workspace_file_path, self.window.snippet_manager.sound_resource_manager.sr_tmp_dir)
        # Configure the dmx output
        self.window.dmx_output.write_output_configuration(dmx_output_configuration)

        self.window.console_display_universes()
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
        def _add_snippet(snippet) -> None:
            """
            Adds a snippet to the workspace
            :param snippet: The snippet to add
            :return: None
            """
            # Return snippet if parent is not found and is not root
            parent = self.window.snippet_manager.find_snippet_entry_by_uuid(snippet["directory"])
            if snippet.get("directory") != "root":
                if not parent:
                    return snippet

            # Create the snippet
            match snippet["type"]:
                case "scene":
                    scene_data = SceneData(snippet["uuid"], snippet["name"], fixtures=snippet.get("fixtures", []), fixture_configs=snippet.get("fixture_configs", {}), directory=snippet.get("directory", "root"))
                    self.window.snippet_manager.scene_manager.scene_create(parent=parent, scene_data=scene_data)
                case "sequence":
                    sequence_data = SequenceData(snippet["uuid"], snippet["name"], scenes=snippet.get("scenes", {}), directory=snippet.get("directory", "root"))
                    self.window.snippet_manager.sequence_manager.sequence_create(parent=parent, sequence_data=sequence_data)
                case "cue":
                    cue_data = CueData(snippet["uuid"], snippet["name"], fixtures=snippet.get("fixtures", []), keyframes=snippet.get("keyframes", {}), directory=snippet.get("directory", "root"))
                    self.window.snippet_manager.cue_manager.cue_create(parent=parent, cue_data=cue_data)
                case "two_d_efx":
                    efx_2d_data = TwoDEfxData(snippet["uuid"], snippet["name"], snippet.get("pattern", "Circle"), snippet.get("width", 512), snippet.get("height", 512), snippet.get("x_offset", 0), snippet.get("y_offset", 0), snippet.get("fixture_mappings", {}), snippet.get("duration", 5000), snippet.get("direction", "Forward"), directory=snippet.get("directory", "root"))
                    self.window.snippet_manager.two_d_efx_manager.two_d_efx_create(parent=parent, two_d_efx_data=efx_2d_data)
                case "rgb_matrix":
                    rgb_matrix_data = RgbMatrixData(snippet["uuid"], snippet["name"], directory=snippet.get("directory", "root"))
                    self.window.snippet_manager.rgb_matrix_manager.rgb_matrix_create(parent=parent, rgb_matrix_data=rgb_matrix_data)
                case "script":
                    script_data = ScriptData(snippet["uuid"], snippet["name"], directory=snippet.get("directory", "root"))
                    self.window.snippet_manager.script_manager.script_create(parent=parent, script_data=script_data)
                case "directory":
                    directory_data = DirectoryData(snippet["uuid"], snippet["name"], directory=snippet.get("directory", "root"))
                    self.window.snippet_manager.directory_manager.dir_create(parent=parent, directory_data=directory_data)
                case "sound_resource":
                    sound_resource_data = SoundResourceData(snippet["uuid"], snippet["name"], directory=snippet.get("directory", "root"))
                    self.window.snippet_manager.sound_resource_manager.sound_resource_create(parent=parent, sound_resource_data=sound_resource_data)
                case "show":
                    show_data = ShowData(snippet["uuid"], snippet["name"], directory=snippet.get("directory", "root"), sound_resource_uuid=snippet.get("sound_resource_uuid", None))
                    self.window.snippet_manager.show_manager.show_create(parent=parent, show_data=show_data)

        while snippets:
            for snippet in snippets:
                if _add_snippet(snippet):
                    continue
                snippets.remove(snippet)

        # Load the desk configuration
        self.window.control_desk_view.load_desk_configuration(desk_configuration)
