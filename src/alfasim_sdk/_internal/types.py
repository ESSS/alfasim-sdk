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

from alfasim_sdk._internal.validators import non_empty_str
from alfasim_sdk._internal.validators import valid_unit


@attr.s(kw_only=True)
class ALFAsimType:
    name: str = attrib(default="ALFAsim")


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
    A base field for all types available at ALFAsim.

    :ivar caption: Label to be displayed on the right side of the component.

    :ivar tooltip: Shows a tip, a short piece of text.

    :ivar enable_expr: Function to evaluate if the component will be enabled or not.

    :ivar visible_expr: Function to inform if the component will be visible or not.

    .. rubric:: **Caption and Tooltip**:

    Caption is the most basic information that all fields must inform, it will display Label over the right side of
    the component on the ``Model Explorer`` window.

    Tooltips are short pieces of text to reminder/inform the user about some specificity about the property when they
    keep the mouse over the field. Tooltips must be a string and can have HTML tags and Unicode characters  as well.

    :raise TypeError: if the tooltip informed is not a string.

    .. rubric:: Example myplugin.py

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

    The images below shows the output from the example above.

    .. image:: /_static/images/api/base_field_caption.png
        :scale: 60%

    .. image:: /_static/images/api/base_field_tootip_1.png
        :scale: 70%

    .. image:: /_static/images/api/base_field_tootip_2.png
        :scale: 70%

    .. _enable-expression-section:

    .. rubric:: **Enable Expression**:

    Accepts a python function that controls either the component will be enabled, or disabled.
    The python function will receive two arguments, an instance of itself (to check local values) and an instance of
    :class:`~alfasim_sdk._internal.context.Context` to retrieve information about the application.

    This function must return a boolean, informing True (for enabled) or False (for disabled).

    .. epigraph:: **enabled**:
        The component will handle keyboard and mouse events.

    .. epigraph:: **disabled**:
        The component will not handle events and it will be grayed out.

    .. rubric:: Example myplugin.py

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

    The image below shows the ``N_ions`` property disabled, when the property ``bool_value`` is disabled (False)

    .. image:: /_static/images/api/base_field_enable_expr_1.png

    .. image:: /_static/images/api/base_field_enable_expr_2.png


    .. _visible-expression-section:

    .. rubric:: **Visible Expression**:

    Accepts a python function that controls either the component will be visible, or not.
    The python function will receive two arguments, an instance of itself (to check local values) and an instance of
    :func:`~alfasim_sdk._internal.context.Context` to retrieve information about the application.

    This function must return a boolean, informing True (for visible) or False (for invisible).

    .. rubric:: Example myplugin.py

    .. code-block:: python
        :emphasize-lines: 1-2, 11

        def my_check(self, ctx):
            return self.bool_value


        @data_model(icon="", caption="My Plugin")
        class MyModel:
            bool_value = Boolean(value=True, caption="Enabled")
            N_ions = Quantity(
                caption="Number of Ions",
                value=1,
                unit="-",
                visible_expr=my_check,
            )


        @alfasim_sdk.hookimpl
        def alfasim_get_data_model_type():
            return [MyModel]


    The image below shows the ``N_ions`` property visible, when the property ``bool_value`` is enabled (True)

    .. image:: /_static/images/api/base_field_visible_expr_1.png

    .. image:: /_static/images/api/base_field_visible_expr_2.png

    .. Development only

        The :class:`~BaseField` class and all others classes that inheritance from it, must use kw_only=True for all attributes.
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

    The String field have all options available from :class:`BaseField`, plus the following ones

    :ivar value: property to hold the value informed by the user.

    .. rubric:: Example myplugin.py

    .. code-block:: python

        @data_model(icon="", caption="My Plugin")
        class MyModel:
            string_field = String(
                value="Default Value",
                caption="String Field",
            )

    .. image:: /_static/images/api/string_field_example.png

    .. rubric:: **Accessing String Field from Plugin**:

    In order to access this field from inside the plugin implementation, in C/C++  you need to use :cpp:func:`get_plugin_input_data_string_size`
    together with :cpp:func:`get_plugin_input_data_string_size`

    .. rubric:: **Accessing String Field from Context**:

    When accessed from the :class:`~alfasim_sdk._internal.context.Context`, the String field will return the currently text as ``str``.

    .. code-block:: python

        >>> ctx.get_model("MyModel").string_field
        'Default Value'

        >>> type(ctx.get_model("MyModel").string_field)
        <class 'str'>

    """

    value: str = attrib(validator=non_empty_str)


@attr.s(kw_only=True)
class Enum(BaseField):
    """
    The Enum field provides list of options to the user, showing  only the select item but providing a way to display
    a list of all options through a combo-box.

    The Enum field have all options available from :class:`~BaseField`, besides the listed the ones listed above:

    :ivar values: A list of strings with the available options.
    :ivar initial: Indicates which one of the options should be selected per default.
                    If not given, the first item in ``values`` will be used as default.

    .. rubric:: Example myplugin.py

    .. code-block:: python

        @data_model(icon="", caption="My Plugin")
        class MyModel:
            enum_field = Enum(
                values=["Option 1, Option 2"],
                initial="Option 1",
                caption="Enum Field",
            )

    .. image:: /_static/images/api/enum_field_example.png

    .. rubric:: **Accessing Enum Field from Plugin**:

    In order to access this field from inside the plugin implementation, in C/C++,  you need to use :cpp:func:`get_plugin_input_data_enum`

    .. rubric:: **Accessing Enum Field from Context**:

    When accessed from the :class:`~alfasim_sdk._internal.context.Context`, the Enum field will return the currently selected option
    as ``str``.

    .. code-block:: python

        @data_model(icon="", caption="My Plugin")
        class MyModel:
            enum_field = Enum(
                values=["Option 1", "Option 2"],
                initial="Option 1",
                caption="Enum Field",
            )

    .. code-block:: bash

        # From Terminal
        >>> ctx.get_model("MyModel").enum_field
        'Option 1'

        >>> type(ctx.get_model("MyModel").enum_field)
        <class 'str'>

    """

    values: List[str] = attrib()
    initial: Optional[str] = attrib(validator=optional(instance_of(str)), default=None)

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
                    "The initial condition must be within the declared values"
                )


@attr.s(kw_only=True)
class BaseReference(BaseField):
    ref_type: type = attrib()
    container_type: Optional[str] = attrib(
        default=None, validator=optional(non_empty_str)
    )

    def __attrs_post_init__(self):
        if issubclass(self.ref_type, ALFAsimType):
            self.container_type = self.ref_type._CONTAINER_TYPE
        else:
            if self.container_type is None:
                raise TypeError(
                    "The container_type field must be given when ref_type is a class decorated with 'data_model'"
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

    :ALFAsimTypes: models from ALFAsim, for example, Tracers.
    :Custom Data: a model defined within the plugin.

    .. note::
        In order to reference custom data, the model must be inside a container.

    :ivar caption: Property used as a label for the field.

    :ivar ref_type: Property that indicates which type of data the Reference will hold.

    :ivar container_type:
        The name of the class that holds the ref_type, this property must be used when the ``ref_type`` references model from the plugin.

    .. rubric:: Example using ``ALFAsimTypes`` on myplugin.py

    .. code-block:: python

        @data_model(icon="", caption="My Plugin")
        class MyModel:
            tracer_ref = Reference(
                ref_type=TracerType,
                caption="Tracer Type",
            )


    .. image:: /_static/images/api/reference_field_example_1.png

    .. rubric:: Example using ``Custom Data`` on myplugin.py

    .. code-block:: python

        @data_model(caption="My Model")
        class MyModel:
            field_1 = String(value="Value 1", caption="String 1")


        @container_model(caption="My Container", model=MyModel, icon="")
        class MyContainer:
            internal_ref = Reference(
                ref_type=MyModel,
                container_type="MyContainer",
                caption="Internal Reference",
            )


    .. image:: /_static/images/api/reference_field_example_2.png

    .. rubric:: **Accessing Reference Field from Plugin**:

    In order to access this field from inside the plugin implementation, in C/C++,  you need to use :cpp:func:`get_plugin_input_data_reference`

    .. rubric:: **Accessing Reference Field from Context**:

    When accessed from the :class:`~alfasim_sdk._internal.context.Context`, the Reference field will return the currently selected option
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
                caption="Internal Reference",
            )

        # Example with Tracer
        >>> ctx.get_model("MyContainer").tracer_ref
        TracerModel(gas_partition_coefficient=[...])

        >>> ctx.get_model("MyContainer").tracer_ref.gas_partition_coefficient
        Scalar(0.0, 'kg/kg', 'mass fraction')

        # Example with Custom Data
        >>> ctx.get_model("MyContainer").internal_ref
        MyModel(field_1='Value 1', name='My Model 1')

        >>> ctx.get_model("MyContainer").internal_ref.field_1
        'Value 1'

    """


@attr.s(kw_only=True)
class MultipleReference(BaseReference):
    """
    The MultipleReference field works similar to :class:`Reference`, providing a list of options
    to the user, but allowing multiple values, of the same type, to be chosen.

    There are two types of models supported by this field.
    :ALFAsimTypes: models from ALFAsim, for example, Tracers.
    :Custom Data: a model defined within the plugin.

    .. note::
        In order to reference a custom data the model must be inside a container.

    :ivar caption:
        Property used as a label for the field.

    :ivar ref_type:
        Property that indicates which type of data the Reference will hold.

    :ivar container_type:
        The name of the class that holds the ref_type, this property must be used when the ref_type references model from the plugin.

    .. rubric:: Example using ``ALFAsimTypes`` on myplugin.py

    .. code-block:: python

        @data_model(icon="", caption="My Plugin")
        class MyModel:
            tracer_ref = MultipleReference(
                ref_type=TracerType, caption="Tracer Type"
            )


    .. image:: /_static/images/api/multiplereference_field_example_1.png

    .. rubric:: Example using ``Custom Data`` on myplugin.py

    .. code-block:: python

        @data_model(caption="My Model")
        class MyModel:
            field_1 = String(value="Value 1", caption="String 1")


        @container_model(caption="My Container", model=MyModel, icon="")
        class MyContainer:
            internal_ref = MultipleReference(
                ref_type=MyModel,
                container_type="MyContainer",
                caption="Internal Reference",
            )


    .. image:: /_static/images/api/multiplereference_field_example_2.png

    .. rubric:: **Accessing MultipleReference Field from Plugin**:

    In order to access this field from inside the plugin implementation, in C/C++,  you need to use :cpp:func:`get_plugin_input_data_multiplereference_selected_size`

    .. rubric:: **Accessing MultipleReference Field from Context**:

    When accessed from the :class:`~alfasim_sdk._internal.context.Context`, the MultipleReference field will return a list with
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
                caption="Internal Reference",
            )


        # Example
        >>> ctx.get_model("MyContainer").internal_ref
        [MyModel(field_1='Value 1', name='My Model 1'),
        MyModel(field_1='Value 1', name='My Model 4')]

        >>> type(ctx.get_model("MyContainer").internal_ref)
        <class 'list'>

        >>> ctx.get_model("MyContainer").internal_ref[0]
        MyModel(field_1='Value 1', name='My Model 1')

    """


@attr.s(kw_only=True, frozen=True)
class Quantity(BaseField):
    """
    The Quantity field provides a way to the user provide a scalar value into the application.

    The Quantity field have all options available from :class:`~BaseField`, besides the listed the ones listed above:
    :ivar values:  A number value.
    :ivar unit:    Unit for the given scalar.

    All scalar values are created using the `Barril library`_

    Checkout the Barril documentation, `to see all available units <https://barril.readthedocs.io/en/latest/units.html>`_

    .. note::

        If you want to check the input value, is recommended to include a status monitor in your plugin
        to make sure that the provided value is valid.

        For more details about status monitor check :func:`~alfasim_sdk._internal.hook_specs_gui.alfasim_get_status`

    .. rubric:: Example myplugin.py

    .. code-block:: python

        @data_model(icon="", caption="My Plugin")
        class MyModel:
            quantity_field = Quantity(
                value=1, unit="degC", caption="Quantity Field"
            )


    .. image:: /_static/images/api/quantity_field_example.png

    .. rubric:: **Accessing Quantity Field from Plugin**:

    In order to access this field from inside the plugin implementation, in C/C++,  you need to use :cpp:func:`get_plugin_input_data_quantity`

    .. rubric:: **Accessing Quantity Field from Context**:

    When accessed from the :class:`~alfasim_sdk._internal.context.Context`, the Quantity field will return a :class:`barril.units.Scalar` object, with
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
        >>> ctx.get_model("MyModel").quantity_field
        Scalar(1.0, 'degC', 'temperature')

        >>> ctx.get_model("MyModel").quantity_field.value
        1.0

        >>> ctx.get_model("MyModel").quantity_field.unit
        'degC'

        >>> ctx.get_model("MyModel").quantity_field.GetValue('K')
        274.15

    .. _Barril library: https://github.com/ESSS/barril
    .. _Scalar documentation from Barril:  https://barril.readthedocs.io/en/latest/api.html#scalar
    """

    value: numbers.Real = attrib(validator=instance_of(numbers.Real))
    unit: str = attrib(validator=[non_empty_str, valid_unit])


@attr.s(kw_only=True, frozen=True)
class TableColumn(BaseField):
    """
    The TableColumn component provides columns for a :class:`Table` field.
    Currently only columns with a :class:`Quantity` fields are available.

    Check out the documentation from :class:`Table` to see more details about the usage and how to retrieve values.
    """

    id: str = attrib(validator=non_empty_str)
    value: Quantity = attrib()
    caption: str = attrib(init=False, default="")

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
    """
    The Table component provides a table to the user to be able input values manually or by importing it from a file.

    .. rubric:: Example myplugin.py

    .. code-block:: python

        @data_model(icon="", caption="My Model")
        class MyModel:
            Table(
                rows=[
                    TableColumn(
                        id="temperature",
                        value=Quantity(
                            value=1,
                            unit="K",
                            caption="Temperature Column Caption",
                        ),
                    ),
                    TableColumn(
                        id="pressure",
                        value=Quantity(
                            value=2,
                            unit="bar",
                            caption="Pressure Column Caption",
                        ),
                    ),
                ],
                caption="Table Field",
            )

    The image above illustrates the output from the example above.

    .. image:: /_static/images/api/table_field_example_1.png

    With this component, the user can easily import the content from a file by clicking on the last icon from the toolbar menu.

    .. image:: /_static/images/api/table_field_example_2.png

    The wizard assistance supports multiple types of file, the user just needs to inform which kind of configuration the file has.

    .. image:: /_static/images/api/table_field_example_3.png

    By the end, it's possible for the user select to which unit the values must be converted and which columns.

    .. rubric:: **Accessing Table Field from Plugin**:

    In order to access this field from inside the plugin implementation, in C/C++,  you need to use :cpp:func:`get_plugin_input_data_table_quantity`

    .. rubric:: **Accessing Table Field from Context**:

    When accessed from the :class:`~alfasim_sdk._internal.context.Context`, the Table field will return a model, with information about
    all columns.


    .. code-block:: bash
        :linenos:

        @data_model(icon="", caption="My Model")
        class MyModel:
            Table(
                rows=[
                    TableColumn(
                        id='temperature',
                        value=Quantity(value=1, unit='K', caption='Temperature Column Caption'),
                    ),
                    TableColumn(
                        id='pressure',
                        value=Quantity(value=2, unit='bar', caption='Pressure Column Caption'),
                    ),
                ],
                caption="Table Field"
            )

        # From Terminal
        >>> ctx.get_model("MyModel").table_field
        TableContainer([...])

        >>> len(ctx.get_model("MyModel").table_field)
        6

        >>> len(ctx.get_model("MyModel").table_field)
        TableRow(temperature=Scalar(1.0, 'K', 'temperature'), pressure=Scalar(2.0, 'bar', 'pressure'))

        >>> ctx.get_model("MyModel").table_field[0].pressure
        Scalar(2.0, 'bar', 'pressure')


    """

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
    """
    The Boolean field provides a checkbox to select/deselect a property.

    The Boolean fields have all options available from :class:`~BaseField`, besides the listed the ones listed above:
    :ivar value:  A boolean informing the initial state from the Field

    .. rubric:: Example myplugin.py

    .. code-block:: python

        @data_model(icon="", caption="My Plugin")
        class MyModel:
            boolean_field = Boolean(
                value=False,
                caption="Boolean Field",
            )

    .. image:: /_static/images/api/boolean_field_example_1.png

    .. rubric:: **Accessing Boolean Field from Plugin**:

    In order to access this field from inside the plugin implementation, in C/C++,  you need to use :cpp:func:`get_plugin_input_data_boolean`

    .. rubric:: **Accessing Quantity Field from Context**:

    When accessed from the :class:`~alfasim_sdk._internal.context.Context`, the Boolean field will return a boolean value

    .. code-block:: bash

        @data_model(icon="", caption="My Plugin")
        class MyModel:
            quantity_field = Boolean(
                value=False,
                caption="Boolean Field",
            )

        # From Terminal
        >>> ctx.get_model("MyModel").boolean_field
        False
    """

    value: bool = attrib(validator=instance_of(bool))


@attr.s(kw_only=True)
class FileContent(BaseField):
    """
    The FileContent component provides a platform-native file dialog to the user to be able to select a file.
    The name of the selected file will be available over the GUI.

    .. note::

        If you want to make the file mandatory it is recommended to include a status monitor in your plugin
        to make sure that a file is selected.

        For more details about status monitor check :func:`~alfasim_sdk._internal.hook_specs_gui.alfasim_get_status`

    :ivar caption: Label to be displayed on the right side of the component.

    .. rubric:: Example myplugin.py

    .. code-block:: python

        @data_model(icon="", caption="My Plugin")
        class MyModel:
            file_content_field = FileContent(caption="FileContent Field")

    .. image:: /_static/images/api/file_content_field_example_1.png

    .. rubric:: **Accessing FileContent Field from Plugin**:

    In order to access this field from inside the plugin implementation, in C/C++,  you need to use :cpp:func:`get_plugin_input_data_file_content`
    together with :cpp:func:`get_plugin_input_data_file_content_size`

    .. rubric:: **Accessing Quantity Field from Context**:

    When accessed from the :class:`~alfasim_sdk._internal.context.Context`, the FileContent field will return a FileContent object,
    a Model that represent a file from the filesystem.

    Class FileContent

    :ivar path:          Return a `Path object`_ of the file.
    :ivar content:       The content from the file in binary format.
    :ivar size:          The size of the file in bytes.
    :ivar modified_data: Return a `Datetime object`_, with the last time the file was modified

    >>> ctx.get_model("MyModel").file_content_field.path
    WindowsPath('C:/ol-wax-1.wax')

    >>> ctx.get_model("MyModel").file_content_field.content
    b"!Name of Table  [...] "

    >>> ctx.get_model("MyModel").file_content_field.size
    90379

    >>> ctx.get_model("MyModel").file_content_field.modified_data
    datetime.datetime(2019, 5, 10, 14, 22, 11, 50795)

    .. _Path object: https://docs.python.org/3/library/pathlib.html#pure-paths
    .. _Datetime object: https://docs.python.org/3/library/datetime.html#datetime-objects
    """


@attr.s(kw_only=True, frozen=True)
class AddField:
    """
    Allows the plugin to add new fields to Hydrodynamic model.

    An added field **must** be associated to a phase (Using :class:`AddPhase` or :class:`UpdatePhase`)
    and added to a layer (Using :class:`AddLayer` or :class:`UpdateLayer`)

    :ivar name: Name of the new field.

    .. note::
        This type is supposed to be used in the :py:func:`~alfasim_sdk._internal.hook_specs_gui.alfasim_configure_fields` `hook`.

    """

    name: str = attr.ib()


@attr.s(kw_only=True, frozen=True)
class AddLayer:
    """
    Allows the plugin to add new layers to Hydrodynamic model.

    :ivar name: Name of the new layer.

    :ivar fields: List of fields names contained in the added layer.

    :ivar continuous_field: Name of the continuous field of the added layer (must be in the `fields` list).

    .. note::
        This type is supposed to be used in the :func:`~alfasim_sdk._internal.hook_specs_gui.alfasim_configure_layers` `hook`.
    """

    name: str = attr.ib()
    fields: List[str] = attr.ib()
    continuous_field: str = attr.ib()


@attr.s(kw_only=True, frozen=True)
class UpdateLayer:
    """
    Allows the plugin to update existing layer of the Hydrodynamic model.

    List of possible layers names (see :ref:`api-constants-section` for details):
     - ``GAS_LAYER``
     - ``OIL_LAYER``
     - ``WATER_LAYER`` (If a three phase hydrodynamic model is used)

    :ivar name: Name of the updated layer.

    :ivar additional_fields: List of additional fields names to be appended in the fields list of the layer.

    .. note::
        This type is supposed to be used in the :func:`~alfasim_sdk._internal.hook_specs_gui.alfasim_configure_layers` `hook`.
    """

    name: str = attr.ib()
    additional_fields: List[str] = attr.ib()


@attr.s(kw_only=True, frozen=True)
class AddPhase:
    """
    Allows the plugin to add new phases to Hydrodynamic model.

    :ivar name: Name of the new phase.
    :ivar fields: List of fields names associated to the added phase. It is important to know how to calculate
        the state variables of fields.

    :ivar primary_field: Reference field when a phase property calculation is performed through the fields of the phase.

    :ivar is_solid: A boolean variable to identify if the added phase is solid.

    .. note::
        This type is supposed to be used in the :func:`~alfasim_sdk._internal.hook_specs_gui.alfasim_configure_phases` `hook`.
    """

    name: str = attr.ib()
    fields: List[str] = attr.ib()
    primary_field: str = attr.ib()
    is_solid: bool = attr.ib(default=False)


@attr.s(kw_only=True, frozen=True)
class UpdatePhase:
    """
    Allows the plugin update existing phases of the Hydrodynamic model.

    List of possible phase names (see :ref:`api-constants-section` for details):
     - ``GAS_PHASE``
     - ``OIL_PHASE``
     - ``WATER_PHASE`` (If a three phase hydrodynamic model is used)

    :ivar name: Name of the new phase.
    :ivar additional_fields: List of additional fields names to be appended in the fields list of the phase.

    .. note::
        This type is supposed to be used in the :func:`~alfasim_sdk._internal.hook_specs_gui.alfasim_configure_phases` `hook`.
    """

    name: str = attr.ib()
    additional_fields: List[str] = attr.ib()
