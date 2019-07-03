import numbers
from typing import Callable
from typing import FrozenSet
from typing import List
from typing import Optional
from typing import Union

import attr
from attr import attrib
from attr._make import Attribute
from attr.validators import instance_of
from attr.validators import is_callable
from attr.validators import optional

from alfasim_sdk._validators import non_empty_str
from alfasim_sdk._validators import valid_unit


@attr.s(kw_only=True)
class ALFAsimType:
    name = attrib(default="ALFAsim")


@attr.s(kw_only=True)
class TracerType(ALFAsimType):
    _CONTAINER_TYPE = "TracerModelContainer"


@attr.s(kw_only=True)
class Tab:
    """
    Base class for tab attributes available at ALFAsim.
    """


@attr.s(kw_only=True)
class Tabs:
    """
    Base class for tabs attributes available at ALFAsim.
    """


@attr.s(kw_only=True)
class Group:
    """
    Base class for Group attribute available at ALFAsim.
    """


@attr.s(kw_only=True)
class BaseField:
    """
    Base class for all widget fields available at ALFAsim.

    The BaseField class and all others classes that inheritance from BaseField must use kw_only=True
    for all attributes.
    This is due to the necessity to make enable_expr and visible_expr an optional value and the
    only way to have properties with default values mixed with required properties is with
    key-word only arguments.
    """

    caption: str = attrib(validator=non_empty_str)
    tooltip: Optional[Callable] = attrib(default="", validator=instance_of(str))
    enable_expr: Optional[Callable] = attrib(
        default=None, validator=optional(is_callable())
    )
    visible_expr: Optional[Callable] = attrib(
        default=None, validator=optional(is_callable())
    )


@attr.s(kw_only=True)
class String(BaseField):
    """
    The String represents an input that the user can provide a string text for the application.

    GUI Representation:
    On the GUI interface, the String represent an text input with a one-line text editor.

    Properties:
    caption - property used as a label for the text input.
    value   - property that holds the value informed from the user, or the default value that
              should be displayed for the user.


    """

    value: str = attrib(validator=non_empty_str)


@attr.s(kw_only=True)
class Enum(BaseField):
    """
    The Enum field provides list of options to the user, showing  only the select item but providing a way to display
    a list of all options through a combo-box.

    :ivar str caption: A string to be displayed on the right side of the component.
    :ivar List[str] values: A list of strings with the available options.
    :ivar str initial: Indicates which one of the options should be selected per default. If not given, the first item in ``values`` will be used as default.

    """

    values: List[str] = attrib()
    initial: str = attrib(validator=optional(instance_of(str)), default=None)

    @values.validator
    def check(  # pylint: disable=arguments-differ
        self, attr: Attribute, values: List[str]
    ) -> None:
        if not isinstance(values, list):
            raise TypeError(
                f"{attr.name} must be a list, got a '{type(values).__name__}'."
            )

        for value in values:
            if not isinstance(value, str):
                raise TypeError(
                    f"{attr.name} must be a list of strings, the item '{value}' is a '{type(value).__name__}'"
                )
            non_empty_str(self, attr, value)

        if self.initial is not None:
            if self.initial not in values:
                raise TypeError(
                    f"The initial condition must be within the declared values"
                )


@attr.s(kw_only=True)
class BaseReference(BaseField):
    ref_type = attrib()
    container_type = attrib(default=None, validator=optional(non_empty_str))

    def __attrs_post_init__(self):
        if issubclass(self.ref_type, ALFAsimType):
            self.container_type = self.ref_type._CONTAINER_TYPE
        else:
            if self.container_type is None:
                raise TypeError(
                    f"The container_type field must be given when ref_type is a class decorated with 'data_model'"
                )

    @ref_type.validator
    def check(self, attr: Attribute, value) -> None:
        if not isinstance(value, type):
            raise TypeError(f"{attr.name} must be a class")

        if not issubclass(value, ALFAsimType):
            if not hasattr(value, "_alfasim_metadata"):
                raise TypeError(
                    f"{attr.name} must be an ALFAsim type or a class decorated with 'data_model'"
                )

            if value._alfasim_metadata["model"] is not None:
                raise TypeError(
                    f"{attr.name} must be an ALFAsim type or a class decorated with 'data_model', got a class decorated with 'container_model'"
                )


@attr.s(kw_only=True)
class Reference(BaseReference):
    """
    The Reference field stores a reference to another model available at the application.
    The are two types of models supported by this field.
        - ALFAsimTypes: models from ALFAsim, example Tracers.
        - Custom Data: a model defined withing the plugin.
            Note.: In order to reference a custom data the model must be inside a container.

    GUI representation:
        The reference field provides a list of options to the user and displays the current item selected.

    :ivar str caption:
        Property used as a label for the field.

    :ivar Union[alfasim_sdk.types.ALFAsimType, type] ref_type:
        Property that indicates which type of data the Reference will hold.

    :ivar Optional[str] container_type:
        The name of the class that holds the ref_type, this property must be used when the ref_type references model from the plugin.
    """


@attr.s(kw_only=True)
class MultipleReference(BaseReference):
    """
    The MultipleReference field stores a reference to another model in a container, providing a way to store
    multiples references of the same type.

    The are two types of models supported by this field.
        - ALFAsimTypes: models from ALFAsim, example Tracers.
        - Custom Data: a model defined withing the plugin.
            Note.: In order to reference a custom data the model must be inside a container.

    GUI representation:
        The MultipleReference field provides a list of selectable options to the user which can select one or mode items.

    :ivar str caption:
        Property used as a label for the field.

    :ivar Union[alfasim_sdk.types.ALFAsimType, type] ref_type:
        Property that indicates which type of data the Reference will hold.

    :ivar Optional[str] container_type:
        The name of the class that holds the ref_type, this property must be used when the ref_type references model from the plugin.
    """


@attr.s(kw_only=True, frozen=True)
class Quantity(BaseField):
    value: numbers.Real = attrib(validator=instance_of(numbers.Real))
    unit: str = attrib(validator=[non_empty_str, valid_unit])


@attr.s(kw_only=True, frozen=True)
class TableColumn(BaseField):
    id: str = attrib(validator=non_empty_str)
    value: Quantity = attrib()
    caption = attrib(init=False, default="")

    def __attrs_post_init__(self) -> None:
        object.__setattr__(self, "caption", self.value.caption)

    @value.validator
    def check(  # pylint: disable=arguments-differ
        self, attr: Attribute, values: Quantity
    ) -> None:
        if not isinstance(values, Quantity):
            raise TypeError(f"{attr.name} must be a Quantity, got a {type(values)}.")


@attr.s(kw_only=True, frozen=True)
class Table(BaseField):
    rows: FrozenSet[TableColumn] = attrib(converter=frozenset)

    @rows.validator
    def check(  # pylint: disable=arguments-differ
        self, attr: Attribute, values: Union[List[str], str]
    ):
        if not values:
            raise TypeError(f"{attr.name} must be a list with TableColumn.")

        if not all(isinstance(value, TableColumn) for value in values):
            raise TypeError(f"{attr.name} must be a list of TableColumn.")


@attr.s(kw_only=True)
class Boolean(BaseField):
    value: bool = attrib(validator=instance_of(bool))


@attr.s(kw_only=True)
class FilePath(BaseField):
    """
    The FilePath component provides a platform-native file dialog to the user to be able to select a file.
    The name of the selected file will be available over the GUI and be enabled to be manually changed.

    If you want to make the file mandatory is recommended to include a status monitor in your plugin
    to make sure that that a file is selected.

    For more details about status monitor check alfasim_sdk.status.ErrorMessage
    Properties:
        :ivar caption: caption - label to be used on the left side of the component, that informs the selected file.
    """
