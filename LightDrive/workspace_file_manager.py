import tempfile
import tarfile
import shutil
import json
import os

def read_workspace_file(workspace_file_path: str) -> dict:
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
    with open(os.path.join(tmp_dir, 'fixtures.json')) as f:
        fixtures = json.load(f)

    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)

    return fixtures

def write_workspace_file(workspace_file_path: str, fixtures: list) -> None:
    """
    Creates a workspace file
    :param workspace_file_path: The path to the workspace file
    :param fixtures: The fixtures available in the workspace
    :return: None
    """
    tmp_dir = tempfile.mkdtemp()

    # Create files inside the tmp dir to create the workspace file later
    with tempfile.NamedTemporaryFile(dir=tmp_dir, delete=False) as fixtures_file:
        fixtures_file.write(json.dumps(fixtures, indent=4).encode())
        fixtures_file = fixtures_file.name

    # Archive the files in the tmp dir into the workspace file
    with tarfile.open(workspace_file_path, "w") as archive:
        archive.add(fixtures_file, "fixtures.json")

    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
