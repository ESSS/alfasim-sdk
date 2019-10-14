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
    Base field for all types available at ALFAsim.

    :parameter str caption: Label to be displayed on the right side of the component.

    :param str tooltip: Shows a tip, a short piece of text.

    :param Callable enable_expr: Function to evaluate if the component will be enabled or not.

    :param Callable visible_expr: Function to inform if the component will be visible or not.

    .. rubric:: **Caption and Tooltip**:

    Captions is the most basic information that all fields must inform, it will display Label over the right side of
    the component on the ``Model Explorer`` window.

    Tooltips are short pieces of text to reminder/inform the user about some specificity about the property when they
    keep the mouse over the field. Tooltips must be a string, and can have HTML tags and unicode character as well.

    :raise TypeError: if the tooltip informed it's not a string.

    Example.:

    .. code-block:: python

        @data_model(icon='', caption='My Plugin')
        class MyModel:
            my_string_1= String(
                value='String 1',
                caption='My String 1',
                tooltip="Some Text <br> <b> More Information</b>",
            )
            my_string_2 = String(
                value='String 2',
                caption='My String 2',
                tooltip="∩ ∪ ∫ ∬ ∮",
            )

        @alfasim_sdk.hookimpl
        def alfasim_get_data_model_type():
            return [MyModel]

    The images bellow shows the output from the example above.

    .. image:: _static/base_field_caption.png
        :scale: 60%

    .. image:: _static/base_field_tootip_1.png
        :scale: 70%

    .. image:: _static/base_field_tootip_2.png
        :scale: 70%

    .. rubric:: **Enable Expression**:

    Accepts a python function that controls either the component will be enabled, or disabled.
    The python function will receive two arguments, a instance of itself (to check local values) and a instance of
    :func:`alfasim_sdk.context.Context` to retrieve information about the application.

    This function must return a boolean, informing True (for enabled) or False (for disabled).

    .. epigraph:: **enabled**:
        The component will handles keyboard and mouse events.

    .. epigraph:: **disabled**:
        The component will not handle events and it will be grayed out.

    Example.:

    .. code-block:: python
        :emphasize-lines: 1-2, 11

        def my_check(self, ctx):
            return self.bool_value

        @data_model(icon="", caption="My Plugin")
        class MyModel:
            bool_value = Boolean(value=True, caption="Enabled")
            N_ions = Quantity(
                caption='Number of Ions',
                value=1,
                unit='-',
                enable_expr=my_check,
            )

        @alfasim_sdk.hookimpl
        def alfasim_get_data_model_type():
            return [MyModel]

    The image bellow shows the ``N_ions`` property disabled, when the property ``bool_value`` is disabled (False)

    .. image:: _static/base_field_enable_expr_1.png

    .. image:: _static/base_field_enable_expr_2.png


    .. rubric:: **Visible Expression**:

    Accepts a python function that controls either the component will be visible, or not.
    The python function will receive two arguments, a instance of itself (to check local values) and a instance of
    :func:`alfasim_sdk.context.Context` to retrieve information about the application.

    This function must return a boolean, informing True (for visible) or False (for invisible).

    Example.:

    .. code-block:: python
        :emphasize-lines: 1-2, 11

        def my_check(self, ctx):
            return self.bool_value

        @data_model(icon="", caption="My Plugin")
        class MyModel:
            bool_value = Boolean(value=True, caption="Enabled")
            N_ions = Quantity(
                caption='Number of Ions',
                value=1,
                unit='-',
                visible_expr=my_check,
            )

        @alfasim_sdk.hookimpl
        def alfasim_get_data_model_type():
            return [MyModel]

    The image bellow shows the ``N_ions`` property visible, when the property ``bool_value`` is enabled (True)

    .. image:: _static/base_field_visible_expr_1.png

    .. image:: _static/base_field_visible_expr_2.png

    .. Development only

        The BaseField class and all others classes that inheritance from BaseField must use kw_only=True for all attributes.
        This is due to the necessity to make enable_expr and visible_expr an optional value and the only way to have
        properties with default values mixed with required properties is with key-word only arguments.
    """

    caption: str = attrib(validator=non_empty_str)
    tooltip: str = attrib(default="", validator=instance_of(str))
    enable_expr: Optional[Callable] = attrib(
        default=None, validator=optional(is_callable())
    )
    visible_expr: Optional[Callable] = attrib(
        default=None, validator=optional(is_callable())
    )


@attr.s(kw_only=True)
class String(BaseField):
    """
    The String field represents an input that allows the user to enter and edit a single line of plain text.

    The String fields have all options available from :func:`~alfasim_sdk.types.BaseField`, plus the following ones

    :parameter str value: property to hold the value informed by the user.

    Example of usage:

    .. code-block:: python

        @data_model(icon="", caption="My Plugin")
        class MyModel:
            string_field = String(
                value="Default Value",
                caption="String Field",
            )

    .. image:: _static/string_field_example.png

    .. rubric:: **Accessing String Field from Plugin**:

    In order to access this field from inside the plugin implementation, in C/C++  you need to use :cpp:func:`get_plugin_input_data_string_size`
    together with :cpp:func:`get_plugin_input_data_string_size`

    .. rubric:: **Accessing String Field from Context**:

    When accessed from the :func:`~alfasim_sdk.context.Context`, the String field will return the currently text as ``str``.

    .. code-block:: python

        >>> ctx.GetModel("MyModel").string_field
        'Default Value'

        >>> type(ctx.GetModel("MyModel").string_field)
        <class 'str'>

    """

    value: str = attrib(validator=non_empty_str)


@attr.s(kw_only=True)
class Enum(BaseField):
    """
    The Enum field provides list of options to the user, showing  only the select item but providing a way to display
    a list of all options through a combo-box.

    The String fields have all options available from :func:`~alfasim_sdk.types.BaseField`, beside the listed the ones listed above:

    :param values: A list of strings with the available options.
    :param initial: Indicates which one of the options should be selected per default.
                    If not given, the first item in ``values`` will be used as default.

    Example of usage:

    .. code-block:: python

        @data_model(icon="", caption="My Plugin")
        class MyModel:
            enum_field = Enum(
                values=["Option 1, Option 2"],
                initial="Option 1",
                caption="Enum Field",
            )

    .. image:: _static/enum_field_example.png

    .. rubric:: **Accessing Enum Field from Plugin**:

    In order to access this field from inside the plugin implementation, in C/C++,  you need to use :cpp:func:`get_plugin_input_data_enum`

    .. rubric:: **Accessing Enum Field from Context**:

    When accessed from the :func:`~alfasim_sdk.context.Context`, the Enum field will return the currently selected option
    as ``str``.

    .. code-block:: bash

        @data_model(icon="", caption="My Plugin")
        class MyModel:
            enum_field = Enum(
                values=["Option 1", "Option 2"],
                initial="Option 1",
                caption="Enum Field",
            )

        # From Terminal
        >>> ctx.GetModel("MyModel").enum_field
        'Option 1'

        >>> type(ctx.GetModel("MyModel").enum_field)
        <class 'str'>

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
    The Reference field provides a list of options to the user and displays the current item selected.

    There are two types of models supported by this field.

    :ALFAsimTypes: models from ALFAsim, example Tracers.
    :Custom Data: a model defined within the plugin.

    .. note::
        In order to reference custom data the model must be inside a container.

    :param str caption:
        Property used as a label for the field.

    :param ref_type:
        Property that indicates which type of data the Reference will hold.

    :param container_type:
        The name of the class that holds the ref_type, this property must be used when the ``ref_type`` references model from the plugin.

    Example using ``ALFAsimTypes``:

    .. code-block:: python

        @data_model(icon="", caption="My Plugin")
        class MyModel:
            tracer_ref = Reference(
                ref_type=TracerType,
                caption="Tracer Type",
            )


    .. image:: _static/reference_field_example_1.png

    Example using ``Custom Data``:

    .. code-block:: python

        @data_model(caption="My Model")
        class MyModel:
            field_1 = String(value="Value 1", caption="String 1")

        @container_model(caption="My Container", model=MyModel, icon="")
        class MyContainer:
            internal_ref = Reference(
                ref_type=MyModel,
                container_type="MyContainer",
                caption="Internal Reference"
            )

    .. image:: _static/reference_field_example_2.png

    .. rubric:: **Accessing Reference Field from Plugin**:

    In order to access this field from inside the plugin implementation, in C/C++,  you need to use :cpp:func:`get_plugin_input_data_reference`

    .. rubric:: **Accessing Reference Field from Context**:

    When accessed from the :func:`~alfasim_sdk.context.Context`, the Reference field will return the currently selected option
    object instance.

    With the instance, you can access all attributes from the object normally. Check the example below.

    .. code-block:: bash

        @data_model(caption="My Model")
        class MyModel:
            field_1 = String(value="Value 1", caption="String 1")

        @container_model(caption="My Container", model=MyModel, icon="")
        class MyContainer:
            tracer_ref = Reference(
                ref_type=TracerType,
                caption="Tracer Type",
            )
            internal_ref = Reference(
                ref_type=MyModel,
                container_type="MyContainer",
                caption="Internal Reference"
            )

        # Example with Tracer
        >>> ctx.GetModel("MyContainer").tracer_ref
        TracerModel(gas_partition_coefficient=[...])

        >>> ctx.GetModel("MyContainer").tracer_ref.gas_partition_coefficient
        Scalar(0.0, 'kg/kg', 'mass fraction')

        # Example with Custom Data
        >>> ctx.GetModel("MyContainer").internal_ref
        MyModel(field_1='Value 1', name='My Model 1')

        >>> ctx.GetModel("MyContainer").internal_ref.field_1
        'Value 1'

    """


@attr.s(kw_only=True)
class MultipleReference(BaseReference):
    """
    The MultipleReference field works similar to :func:`~alfasim_sdk.types.Reference`, providing a list of options
    to the user, but allowing multiple values, of the same type, to be chosen.

    The are two types of models supported by this field.
    :ALFAsimTypes: models from ALFAsim, example Tracers.
    :Custom Data: a model defined withing the plugin.

    .. note::
        In order to reference a custom data the model must be inside a container.

    :ivar str caption:
        Property used as a label for the field.

    :ivar ref_type:
        Property that indicates which type of data the Reference will hold.

    :ivar container_type:
        The name of the class that holds the ref_type, this property must be used when the ref_type references model from the plugin.

    Example using ``ALFAsimType``

    .. code-block:: python

        @data_model(icon="", caption="My Plugin")
        class MyModel:
            tracer_ref = MultipleReference(
                ref_type=TracerType,
                caption="Tracer Type",
            )


    .. image:: _static/multiplereference_field_example_1.png

    Example using ``Custom Data``:

    .. code-block:: python

        @data_model(caption="My Model")
        class MyModel:
            field_1 = String(value="Value 1", caption="String 1")

        @container_model(caption="My Container", model=MyModel, icon="")
        class MyContainer:
            internal_ref = MultipleReference(
                ref_type=MyModel,
                container_type="MyContainer",
                caption="Internal Reference"
            )

    .. image:: _static/multiplereference_field_example_2.png

    .. rubric:: **Accessing MultipleReference Field from Plugin**:

    In order to access this field from inside the plugin implementation, in C/C++,  you need to use :cpp:func:`get_plugin_input_data_multiplereference_selected_size`

    .. rubric:: **Accessing MultipleReference Field from Context**:

    When accessed from the :func:`~alfasim_sdk.context.Context`, the MultipleReference field will return a list with
    the currently selected option objects instances.

    With the instance, you can access all attributes from the object. Check the example below.

    .. code-block:: bash

        @data_model(caption="My Model")
        class MyModel:
            field_1 = String(value="Value 1", caption="String 1")

        @container_model(caption="My Container", model=MyModel, icon="")
        class MyContainer:
            internal_ref = MultipleReference(
                ref_type=MyModel,
                container_type="MyContainer",
                caption="Internal Reference"
            )

        # Example
        >>> ctx.GetModel("MyContainer").internal_ref
        [MyModel(field_1='Value 1', name='My Model 1'),
        MyModel(field_1='Value 1', name='My Model 4')]

        >>> type(ctx.GetModel("MyContainer").internal_ref)
        <class 'list'>

        >>> ctx.GetModel("MyContainer").internal_ref[0]
        MyModel(field_1='Value 1', name='My Model 1')

    """


@attr.s(kw_only=True, frozen=True)
class Quantity(BaseField):
    """
    The Quantity field provides a way to the user provide a scalar value into the application.

    The String fields have all options available from :func:`~alfasim_sdk.types.BaseField`, beside the listed the ones listed above:
    :param values:  A number value.
    :param unit:    Unit for the given scalar.

    All scalar values are created using the `Barril library`_

    Checkout the Barril documentation, to see all available units available units [ Needs to implement on Barril this section]

    Example of usage:

    .. code-block:: python

        @data_model(icon="", caption="My Plugin")
        class MyModel:
            quantity_field = Quantity(
                value=1,
                unit="degC",
                caption="Quantity Field",
            )

    .. image:: _static/quantity_field_example.png

    .. rubric:: **Accessing Quantity Field from Plugin**:

    In order to access this field from inside the plugin implementation, in C/C++,  you need to use :cpp:func:`get_plugin_input_data_quantity`

    .. rubric:: **Accessing Quantity Field from Context**:

    When accessed from the :func:`~alfasim_sdk.context.Context`, the Quantity field will return a ``Scalar`` object, with
    the current value and unit.
    Check out the `Scalar documentation from Barril`_ for more details about the usage.

    .. code-block:: bash

        @data_model(icon="", caption="My Plugin")
        class MyModel:
            quantity_field = Enum(
                values=["Option 1", "Option 2"],
                initial="Option 1",
                caption="Enum Field",
            )

        # From Terminal
        >>> ctx.GetModel("MyModel").quantity_field
        Scalar(1.0, 'degC', 'temperature')

        >>> ctx.GetModel("MyModel").quantity_field.value
        1.0

        >>> ctx.GetModel("MyModel").quantity_field.unit
        'degC'

        >>> ctx.GetModel("MyModel").quantity_field.GetValue('K')
        274.15

    .. _Barril library: https://github.com/ESSS/barril
    .. _Scalar documentation from Barril:  https://barril.readthedocs.io/en/latest/api.html#scalar
    """

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
    rows: FrozenSet[TableColumn] = attrib(converter=tuple)

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
class FileContent(BaseField):
    """
    The FileContent component provides a platform-native file dialog to the user to be able to select a file.
    The name of the selected file will be available over the GUI and be enabled to be manually changed.

    If you want to make the file mandatory is recommended to include a status monitor in your plugin
    to make sure that that a file is selected.

    For more details about status monitor check alfasim_sdk.status.ErrorMessage

    :ivar caption: caption - label to be used on the left side of the component, that informs the selected file.
    """


@attr.s(kw_only=True, frozen=True)
class AddField:
    """
        Adding Fields
    """

    name: str = attr.ib()


@attr.s(kw_only=True, frozen=True)
class AddLayer:
    """
        Adding Layers
    """

    name: str = attr.ib()
    fields: list = attr.ib()
    continuous_field: str = attr.ib()


@attr.s(kw_only=True, frozen=True)
class UpdateLayer:
    """
        Updating Layers
    """

    name: str = attr.ib()
    additional_fields: list = attr.ib()


@attr.s(kw_only=True, frozen=True)
class AddPhase:
    """
        Adding Phases
    """

    name: str = attr.ib()
    fields: list = attr.ib()
    primary_field: str = attr.ib()
    is_solid: bool = attr.ib(default=False)


@attr.s(kw_only=True, frozen=True)
class UpdatePhase:
    """
        Updating Phases
    """

    name: str = attr.ib()
    additional_fields: list = attr.ib()
