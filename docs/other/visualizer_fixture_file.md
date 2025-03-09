# LightDrive Visualizer Fixture Files (.ldvf)

LightDrive Visualizer fixture files are used to store fixture definitions for the Visualizer. These
definitions are used to create fixtures in the Visualizer. They contain the model and configuration of the
fixture, as well as a thumbnail.

## File Structure

Under the hood, .ldvf files are zip archives. They contain a directory and a few files. They follow this
structure:
```
fixture_name.ldvf
├── config.json
├── model.glb
└── thumbnail.png
```

### config.json

This file includes the configuration of the fixture. The `min_pan_angle` and `max_pan_angle` properties
control the minimum and maximum pan angle of the fixture. The `min_tilt_angle` and `max_tilt_angle`
properties control the minimum and maximum tilt angle of the fixture. The `light_sources` array contains
all light sources  of the fixture. Each light source is an object with the following properties:
`x_offset`, `y_offset`, `z_offset`, `angle`, `length`, `x_rotation`, `y_rotation` and `z_rotation`.
Each light source will be  added to the fixture in the visualizer. For example a fixture with one light
source will have one  light beam in the visualizer, while a fixture with two light sources will have
two separate light beams.

An example `config.json` file:
```
{
  "min_pan_angle": 0.0,
  "min_tilt_angle": -135.0,
  "max_pan_angle": 540.0,
  "max_tilt_angle": 270.0,
  "light_sources": [
    {
      "x_offset": 0.0,
      "y_offset": 0.5,
      "z_offset": 0.0,
      "angle": 5.0,
      "length": 10.0,
      "x_rotation": 0.0,
      "y_rotation": 0.0,
      "z_rotation": 0.0
    }
  ]
}
```

### model.glb

This file contains the 3D model of the fixture. It is a GLB file, which is a binary form of the glTF 
file format. The model is used to display the fixture in the Visualizer.

!!! TIP
    The model should be centered around the origin (0, 0, 0) for rotation to properly work. The
    built-in fixture files can be viewed as an example and guideline for when creating your own.

### thumbnail.png

This file is used to show a preview of the fixture before it is added to the stage. It may be any size,
but is recommended to be square and at least 256x256 pixels.
