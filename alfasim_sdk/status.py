import attr
from attr import attrib
from attr.validators import deep_iterable
from attr.validators import instance_of
from barril.units import Scalar

from alfasim_sdk._validators import non_empty_str


@attr.s(kw_only=True)
class ErrorMessage:
    """
    The model_name and the message informed is displayed on the status monitor of ALFAsim.
    The execution of a new simulation will not be allowed until the error is solved.
    """

    model_name: str = attrib(validator=non_empty_str)
    message: str = attrib(validator=non_empty_str)


@attr.s(kw_only=True)
class WarningMessage:
    """
    The model_name and the message informed is displayed on the status monitor of ALFAsim.
    The execution of a new simulation will be kept normal.
    """

    model_name: str = attrib(validator=non_empty_str)
    message: str = attrib(validator=non_empty_str)


@attr.s(frozen=True)
class PluginInfo:
    name = attr.attrib(validator=non_empty_str)
    enabled = attr.attrib(validator=instance_of(bool))
    models = attr.attrib(
        validator=deep_iterable(
            member_validator=instance_of(str), iterable_validator=instance_of(list)
        )
    )


@attr.s(frozen=True)
class PipelineSegmentInfo:
    edge_name = attr.attrib(validator=non_empty_str)
    inner_diameter = attr.attrib(validator=instance_of(Scalar))
    start_position = attr.attrib(validator=instance_of(Scalar))
