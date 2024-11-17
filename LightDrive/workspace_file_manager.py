import tempfile
import tarfile
import shutil
import json
import os

def read_workspace_file(workspace_file_path: str) -> tuple[dict, dict]:
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

    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)

    return fixtures, dmx_output_configuration

def write_workspace_file(workspace_file_path: str, fixtures: list, dmx_output_configuration: dict) -> None:
    """
    Creates a workspace file
    :param workspace_file_path: The path to the workspace file
    :param fixtures: The fixtures available in the workspace
    :param dmx_output_configuration: The configuration of output
    :return: None
    """
    tmp_dir = tempfile.mkdtemp()

    # Create files inside the tmp dir to create the workspace file later
    with tempfile.NamedTemporaryFile(dir=tmp_dir, delete=False) as fixtures_file:
        fixtures_file.write(json.dumps(fixtures, indent=4).encode())
    with tempfile.NamedTemporaryFile(dir=tmp_dir, delete=False) as dmx_output_file:
        dmx_output_file.write(json.dumps(dmx_output_configuration, indent=4).encode())

    # Archive the files in the tmp dir into the workspace file
    with tarfile.open(workspace_file_path, "w") as archive:
        archive.add(fixtures_file.name, "fixtures.json")
        archive.add(dmx_output_file.name, "dmx_output_configuration.json")

    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
