# LightDrive Visualizer Stage Model Files (.ldvm)

These files store 3D models for stages in the Visualizer.

## File Structure

Under the hood, .ldvm files are zip archives. They contain a directory and a few files. They follow this
structure:
```
fixture_name.ldvf
├── config.json
├── model.glb
└── thumbnail.png
```

### config.json

These files include the configuration of the stage model. The `objects` property should contain all objects
that are also in the model.json. Each object can have a `color` property, which sets the color of the object.
They should also have a `surface_overrides` property, which is an array of surface indices and colors. The
colors are in hexadecimal format. They override the color of the surface with the given index.

An example config.json file:
```
{
  "objects": {
    "Body": {
      "color": "#363D4A",
      "surface_overrides": {
        "0": "#FF0000",
        "1": "#FF0000",
        "2": "#FF0000",
        "3": "#FF0000"
      }
    }
  }
}
```

### model.glb

This file contains the 3D model of the stage. It is a GLB file. This model is the actual model that gets
rendered in the Visualizer.

!!! TIP
    The model should not cover (0, 0, 0) so that fixtures fo not appear inside the model, as then they
    might become inaccessible. The built-in stage model files can be viewed as an example and guideline
    for when creating your own.


### thumbnail.png

This file is used to show a preview of the stage model before it is added to the stage. It may be any size,
but it is recommended to be square.

