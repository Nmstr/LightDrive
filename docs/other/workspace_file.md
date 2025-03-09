# LightDrive Workspace Files (.ldw)

LightDrive workspace files are used to store all workspace data. This includes fixtures, universes,
snippets, the desk and more.

They contain all relevant data in themselves and can thus easily be shared between systems and users.

## File Structure

Workspace files are simply tar archives under the hood. They contain a directory and a few files. They follow
this structure:
```
workspace_name.ldw
├── desk_configuration.json
├── dmx_output_configuration.json
├── fixtures.json
└── snippets
    ├── snippet_name-snippet_uuid.json
    ├── snippet_name-snippet_uuid.json
    └── snippet_name-snippet_uuid.json
```

`desk_configuration.json` contains the configuration of the desk. This includes the buttons, faders, knobs, 
labels and all other desk elements and their configuration.

`dmx_output_configuration.json` contains the universe configuration. This includes the universe names and
their configuration.

`fixtures.json` contains all fixtures in the workspace.

`snippets` is a directory containing all snippets in the workspace. Each snippet is stored in its own file.
The snippets are stored in JSON format. The file name is the snippet name followed by a dash and the snippet
UUID. These files store all data relevant to the snippet.
