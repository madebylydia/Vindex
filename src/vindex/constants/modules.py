import dataclasses
import enum
import typing
from datetime import datetime, timezone


class Developers(enum.Enum):
    EAGLE_DYNAMICS = "Eagle Dynamics SA"


@dataclasses.dataclass(kw_only=True)
class Tags:
    """Tags define metadata about a specific module.
    Each modules indicate what it is and what's its capabilities.
    Metadatas.
    """

    cockpit_lang: str
    full_fidelity: bool = dataclasses.field(default=False)
    is_fc3: bool = dataclasses.field(default=False)


@dataclasses.dataclass
class Module:  # pylint: disable=too-many-instance-attributes
    """A class to define a specific module of DCS.
    Contains multiple data about each modules.
    """

    name: str
    """The name of the module."""

    kind: typing.Literal["aircraft", "helicopter", "map", "extension", "campaign", "other"]
    """The kind of module."""

    tags: Tags
    """A class containing metadata about the module."""

    origin: typing.Literal["official", "community"]
    """The origin of the module, either if it's an official module published on the DCS store
    or a module made by the community. If so, the link will be available in the `link` attribute.
    """

    status: typing.Literal["released", "early_access", "in_development", "unknown"]
    """The current status of the module."""

    description: str
    """A description of the aircraft."""

    release_date: datetime | None
    """The release date of the module."""

    developers: Developers
    """The name of the module's developers."""

    link: str | None
    """A link to the advertisement of the module."""

    steam_link: str | None
    """Link to the module on the Steam store."""

    dcs_store: str | None
    """Link to the module on the official DCS store."""


class Modules(enum.Enum):
    """The entire list of modules of DCS."""

    F18 = Module(
        name="F/A-18C Hornet",
        kind="aircraft",
        tags=Tags(cockpit_lang="en", full_fidelity=True),
        origin="official",
        release_date=datetime(2018, 6, 1, 17, 2, tzinfo=timezone.utc),
        status="early_access",
        description="""The F/A-18C is twin engine, supersonic fighter that is flown by a single
pilot in a "glass cockpit". It combines extreme maneuverability, a deadly arsenal of weapons, and
the ability to operate from an aircraft carrier. Operated by several nations, this multi-role
fighter has been instrumental in conflicts from 1986 to today.

The F/A-18C is equipped with a large suite of sensors that includes a radar, targeting pod, and a
helmet mounted sight. In addition to its internal 20mm cannon, the F/A-18C can be armed with a
large assortment of unguided bombs and rockets, laser and GPS-guided bombs, air-to-surface
missiles of all sorts, and both radar and infrared-guided air-to-air missiles. This results in
amazing gameplay potential with this single aircraft.

The F/A-18C is also known for its extreme, slow-speed maneuverability in a dogfight. We have gone
to great lengths to model the flight aerodynamics and fly-by-wire flight control system of the
F/A-18C to allow you to experience the real feeling of power and extreme capabilities this
aircraft has to offer. Although incredibly deadly, the F/A-18C is also a very easy aircraft to
fly.

Being an aircraft carrier capable aircraft, our F/A-18C also comes with a free aircraft carrier.
Catapult from the "boat", strike a large assortment of targets that only DCS can offer, then
"call the ball" and land on the carrier. DCS: F/A-18C in DCS provides the most rich and authentic
digital combat aviation you will ever experience!""",
        developers=Developers.EAGLE_DYNAMICS,
        link="https://www.digitalcombatsimulator.com/en/products/planes/hornet/",
        steam_link="https://store.steampowered.com/app/411950/DCS_FA18C/",
        dcs_store="https://www.digitalcombatsimulator.com/en/shop/modules/hornet/",
    )
