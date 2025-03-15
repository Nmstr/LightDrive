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
properties control the minimum and maximum tilt angle of the fixture.

The `light_sources` array contains all light sources  of the fixture. Each light source is an object
with the following properties: `x_offset`, `y_offset`, `z_offset`, `angle`, `length`, `x_rotation`,
`y_rotation`, `z_rotation` and `mode`. Each light source will be added to the fixture in the
visualizer separately.

The `channels` object contains all channels of the fixture. The key is the channel number and the value
is an object specifying the type of the channel and some type specific options. The type can be one of
the following:

- pan

Pans the fixture by rotating the PanPivot. The pan angle is controlled by the value of the channel.

- tilt

Tilts the fixture by rotating the TiltPivot. The tilt angle is controlled by the value of the channel.

- rgb

Controls the RGB color of one or multiple light sources. It has a `color` property which specifies the
color to change. Possible colors are `red`, `green` and `blue`. It then sets the intensity of the
color to the value of the channel. The `light_sources` array specifies which light sources to control
with this channel. The array contains the indices of the light sources in the `light_sources` array of
the fixture. These light_sources must have their mode set to `rgb`, otherwise they will be ignored.

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
      "z_rotation": 0.0,
      "mode": "rgb"
    }
  ],
  "channels": {
    "1": {"type": "pan"},
    "2": {"type": "tilt"},
    "3": {"type": "rgb", "color": "red", "light_sources": [0]},
    "4": {"type": "rgb", "color": "green", "light_sources": [0]},
    "5": {"type": "rgb", "color": "blue", "light_sources": [0]}
  }
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
