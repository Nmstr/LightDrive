import tempfile
import tarfile
import shutil
import json
import os

def write_workspace_file(workspace_file_path: str, fixtures: list) -> None:
    """
    Creates a workspace file
    :param workspace_file_path: The path to the workspace file
    :param fixtures: The fixtures available in the workspace
    :return: None
    """
    # Create a tmp dir
    tmp_dir = tempfile.mkdtemp()

    # Create files inside the tmp dir to create the workspace file later
    with tempfile.NamedTemporaryFile(dir=tmp_dir, delete=False) as fixtures_file:
        fixtures_file.write(json.dumps(fixtures, indent=4).encode())
        fixtures_file = fixtures_file.name

    # Archive the files in the tmp dir into the workspace file
    with tarfile.open(workspace_file_path, "w") as archive:
        archive.add(fixtures_file, "fixtures.json")

    # Remove the tmp dir again
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
