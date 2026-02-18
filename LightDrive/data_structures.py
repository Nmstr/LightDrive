from dataclasses import dataclass, field
import uuid

@dataclass
class UniverseGenericBackend:
    enabled: bool = field(default=False, init=False)

@dataclass
class UniverseTcpBackend(UniverseGenericBackend):
    target_ip: str = field(default="127.0.0.1", init=False)
    port: int = field(default=7500, init=False)
    hz: int = field(default=30, init=False)

@dataclass
class UniverseArtNetBackend(UniverseGenericBackend):
    target_ip: str = field(default="127.0.0.1", init=False)
    universe: int = field(default=0, init=False)
    fps: int = field(default=30, init=False)

@dataclass
class Universe:
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()), init=False)
    name: str
    tcp_backend: UniverseTcpBackend = field(default_factory=UniverseTcpBackend, init=False)
    artnet_backend: UniverseArtNetBackend = field(default_factory=UniverseArtNetBackend, init=False)


@dataclass
class Channel:
    type: str
    name: str
    description: str = field(default="")

@dataclass
class Fixture:
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()), init=False)
    name: str
    universe_uuid: str  # UUID of the universe this fixture is a part of
    address: int

    type: str
    manufacturer: str
    channels: list[Channel]
    description: str = field(default="")


@dataclass
class GenericSnippet:
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()), init=False)
    parent_uuid: str = field(default="", init=False)  # Parent snippet in the tree
    name: str

@dataclass
class CueKeyframe:
    x: int = field(default=0)
    y: int = field(default=0)

@dataclass
class CueSnippet(GenericSnippet):
    keyframes: dict[str, list[list[CueKeyframe]]] = field(default_factory=dict, init=False)  # Example below
    """
    {
        fixture_uuid: [         # The uuid of the fixture for the CueKeyframes
            [                   # The master channel
                CueKeyframe,
                CueKeyframe
            ],
            [                   # First DMX channel
                CueKeyframe,
                CueKeyframe,
                CueKeyframe
            ]
        ],
        fixture_uuid: [         # uuid of the 2nd fixture
            [                   # master channel
                CueKeyframe,
                CueKeyframe
            ],
            [                   # First DMX channel
                CueKeyframe,
                CueKeyframe,
                CueKeyframe
            ]
        ]
    }
    """

@dataclass
class SceneChannelEntry:
    active: bool = field(default=False, init=False)  # Deactivated channels get skipped, no matter their value
    value: int = field(default=0, init=False)

@dataclass
class SceneSnippet(GenericSnippet):
    channel_values: dict[str, list[SceneChannelEntry]] = field(default_factory=dict, init=False)  # example below
    """
    {
        fixture_uuid: [             # The uuid of the fixture for the SceneChannels
            SceneChannelEntry,      # First DMX channel
            SceneChannelEntry,      # Second DMX channel
            SceneChannelEntry       # ...
        ],
        fixture_uuid: [             # uuid of the 2nd fixture
            SceneChannelEntry,      # First DMX channel
            SceneChannelEntry       # Second DMX channel
        ]
    }
    """

@dataclass
class SequenceSceneEntry:
    scene_uuid: str
    fade_in: int = field(default=0, init=False)
    duration: int = field(default=1000, init=False)
    fade_out: int = field(default=0, init=False)

@dataclass
class SequenceSnippet(GenericSnippet):
    scenes: list[SequenceSceneEntry] = field(default_factory=list, init=False)

@dataclass
class TwoDEfxPattern:
    preset: str = field(default="circle", init=False)  # Available: "circle", "square", "triangle", "line", "eight"

@dataclass
class TwoDEfxSnippet(GenericSnippet):
    pattern: TwoDEfxPattern = field(default_factory=TwoDEfxPattern, init=False)
    x_offset: int = field(default=0, init=False)
    y_offset: int = field(default=0, init=False)
    x_stretch: float = field(default=0, init=False)
    y_stretch: float = field(default=0, init=False)
    fixture_mappings_x: list[dict[str, int]] = field(default_factory=list, init=False)  # example below
    fixture_mappings_y: list[dict[str, int]] = field(default_factory=list, init=False)  # example below
    """
    [                           # Each element in the list is one mapping to x/y
        {
            fixture_uuid: 1     # uuid of the fixture mapped with the channel that is mapped
        },
        {
            fixture_uuid: 3
        }
    ]
    """
    duration: int = field(default=1000, init=False)
    reverse: bool = field(default=False, init=False)
    ricochet: bool = field(default=False, init=False)

@dataclass
class RgbMatrixSnippet(GenericSnippet):
    pass  # Not yet implemented

@dataclass
class ScriptSnippet(GenericSnippet):
    script_contents: str = field(default="", init=False)

@dataclass
class DirectorySnippet(GenericSnippet):
    pass  # No extra attributes, but separate class required because for type distinction

@dataclass
class SoundResourceSnippet(GenericSnippet):
    sound_path: str = field(default="", init=False)
    volume: int = field(default=0, init=False)

@dataclass
class ShowSnippet(GenericSnippet):
    sound_resource_uuid: str = field(default="", init=False)
    # Not yet implemented


@dataclass
class GenericVConsoleItem:
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()), init=False)
    name: str
    x: int = field(default=0, init=False)
    y: int = field(default=0, init=False)
    width: int = field(default=0, init=False)
    height: int = field(default=0, init=False)

@dataclass
class VConsoleButton(GenericVConsoleItem):
    hotkey: str = field(default="", init=False)
    mode: str = field(default="toggle", init=False)  # Available: "toggle", "flash"
    flash_duration: float = field(default=0, init=False)

@dataclass
class VConsoleFader(GenericVConsoleItem):
    display_style: str = field(default="value", init=False)  # Available: "value", "percentage"
    min: float = field(default=0.0, init=False)
    max: float = field(default=255.0, init=False)
    step_size: float = field(default=1.0, init=False)
    inverted: bool = field(default=False, init=False)

@dataclass
class VConsoleKnob(GenericVConsoleItem):
    display_style: str = field(default="value", init=False)  # Available: "value", "percentage"
    min: float = field(default=0.0, init=False)
    max: float = field(default=255.0, init=False)
    step_size: float = field(default=1.0, init=False)

@dataclass
class VConsoleSoundTrigger(GenericVConsoleItem):
    pass  # Not yet implemented

@dataclass
class VConsoleLabel(GenericVConsoleItem):
    pass  # No extra attributes, but separate class required because for type distinction

@dataclass
class VConsoleClock(GenericVConsoleItem):
    mode: str = field(default="clock", init=False)  # Available: "clock", "timer", "stopwatch"
    timer_duration: float = field(default=0, init=False)


@dataclass
class Workspace:
    universes: list[Universe] = field(default_factory=list, init=False)
    fixtures: list[Fixture] = field(default_factory=list, init=False)
    snippets: list[GenericSnippet] = field(default_factory=list, init=False)
    v_console_items: list[GenericVConsoleItem] = field(default_factory=list, init=False)
