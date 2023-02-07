import os
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Callable
from typing import List
from unittest.mock import ANY

import pytest
from barril.units import Array
from barril.units import Scalar

from alfasim_sdk import convert_alfacase_to_description
from alfasim_sdk import PluginDescription
from alfasim_sdk._internal.alfacase.case_description import CaseDescription
from alfasim_sdk._internal.alfacase.case_description import PluginFileContent
from alfasim_sdk._internal.alfacase.case_description import PluginInternalReference
from alfasim_sdk._internal.alfacase.case_description import PluginMultipleReference
from alfasim_sdk._internal.alfacase.case_description import PluginTableContainer
from alfasim_sdk._internal.alfacase.case_description import PluginTracerReference
from alfasim_sdk._internal.alfacase.case_description_attributes import (
    InvalidPluginDataError,
)
from alfasim_sdk._internal.alfacase.plugin_alfacase_to_case import (
    dump_file_contents_and_update_plugins,
)
from alfasim_sdk._internal.alfacase.plugin_alfacase_to_case import (
    get_plugin_module_candidates,
)
from alfasim_sdk._internal.alfacase.plugin_alfacase_to_case import (
    load_plugin_data_structure,
)


def test_get_plugin_module_candidates(monkeypatch):
    monkeypatch.setenv("ALFASIM_PLUGINS_DIR", f"foo{os.path.pathsep}bar")
    monkeypatch.setattr(Path, "home", lambda: Path("xxx"))
    candidates = get_plugin_module_candidates("cool_stuff")
    assert candidates == [
        Path("foo/cool_stuff/artifacts/cool_stuff.py"),
        Path("bar/cool_stuff/artifacts/cool_stuff.py"),
        Path("xxx/.alfasim_plugins/cool_stuff/artifacts/cool_stuff.py"),
    ]


def test_load_plugin_data_structure(abx_plugin):
    models = load_plugin_data_structure("abx")
    assert [m.__name__ for m in models] == ["AContainer", "BContainer"]


def test_load_plugin_multiple_containers(datadir, abx_plugin):
    alfacase = datadir / "test.alfacase"
    alfacase.write_text(
        textwrap.dedent(
            """\
            plugins:
            -   name: abx
                is_enabled: False
                gui_models:
                    AContainer:
                        _children_list:
                        -   asd: aaa
                        -   qwe: sss
                    BContainer:
                        _children_list:
                        -   qwe: zzz
                        -   asd: xxx
            """
        )
    )
    case = convert_alfacase_to_description(alfacase)
    assert case.plugins == [
        PluginDescription(
            name="abx",
            is_enabled=False,
            gui_models={
                "AContainer": {
                    "_children_list": [
                        {"asd": "aaa"},
                        {"qwe": "sss"},
                    ],
                },
                "BContainer": {
                    "_children_list": [
                        {"qwe": "zzz"},
                        {"asd": "xxx"},
                    ],
                },
            },
        ),
    ]


def test_load_plugin_with_missing_top_level_models(
    datadir: Path, abx_plugin: None
) -> None:
    """
    Plugins can declare models to represent user input, they will be represented by `data_model`s (like a struct
    to hold data) or `container_model`s (like `data_model` it can hold data but also it can have any number of
    children `data_model`s) in the `gui_models` entry:

    ```yaml
    gui_models:
    -   name: abx
        AContainer:  # top level.
            _children_list:
                - {}  # not top level.
        BContainer:  # top level.
            _children_list:
                - {}  # not top level.
                - {}  # not top level.
    ```

    This tests if an alfacase missing those top level models (`data_model` or `container_model`) can be loaded.
    """
    alfacase = datadir / "test.alfacase"
    alfacase.write_text(
        textwrap.dedent(
            """\
            plugins:
            -   name: abx
                gui_models: {}
            """
        )
    )
    case = convert_alfacase_to_description(alfacase)
    assert case.plugins == [
        PluginDescription(
            name="abx",
            is_enabled=True,
            gui_models={},
        ),
    ]


def test_load_plugin_empty_top_containers(datadir: Path, abx_plugin: None) -> None:
    """
    See `test_load_plugin_missing_top_level_models` first paragraph.

    This tests if empty containers (or ones missing the `_children_list` entry) can be properly loaded.
    """
    alfacase = datadir / "test.alfacase"
    alfacase.write_text(
        textwrap.dedent(
            """\
            plugins:
            -   name: abx
                gui_models:
                    # strictyaml requires adjacent mappings to have the same internal indent.
                    AContainer: {}
                    BContainer: {_children_list: []}
            """
        )
    )
    case = convert_alfacase_to_description(alfacase)
    assert case.plugins == [
        PluginDescription(
            name="abx",
            is_enabled=True,
            gui_models={
                "AContainer": {"_children_list": []},
                "BContainer": {"_children_list": []},
            },
        ),
    ]


@pytest.fixture(name="prepare_foobar_plugin")
def prepare_foobar_plugin_(monkeypatch, datadir) -> Callable[[List[str]], None]:
    """
    Create a fake plugin and "install"s it.

    The fake plugin is named "foobar". As data model it contains a `data_model` of type Bar (no attributes) and
    a `container_model` of type FooContainer (no attributes but containing item of the type Foo, this items contain
    the attributes listed when calling):

    ```python
    def test_example(datadir, prepare_foobar_plugin):
        prepare_foobar_plugin(
            [
                "a_string_attr = alfasim_sdk.String(value='default string value', caption='a gui caption')",
                "a_bool_attr = alfasim_sdk.Boolean(value=False, caption='to_be or not to_be')",
            ],
        )
    ```
    """

    def prepare_foobar_plugin_impl(data_model_fields: List[str]) -> None:
        plugin_root = datadir / "test_plugins"
        monkeypatch.setenv("ALFASIM_PLUGINS_DIR", str(plugin_root))
        plugin_file = plugin_root / "foobar/artifacts/foobar.py"
        plugin_file.parent.mkdir(parents=True)

        data_model_source = "\n    ".join(
            [
                "@alfasim_sdk.data_model(icon='', caption='Foo!')\nclass Foo:",
                *data_model_fields,
            ]
        )
        plugin_file_source = textwrap.dedent(
            """\
            import alfasim_sdk

            @alfasim_sdk.data_model(icon='', caption='Bar!')
            class Bar:
                pass

            {data_model_source}

            @alfasim_sdk.container_model(model=Foo, icon="", caption="Foo Container")
            class FooContainer:
                pass

            @alfasim_sdk.hookimpl
            def alfasim_get_data_model_type():
                return [FooContainer]
            """
        )
        plugin_file_source = plugin_file_source.format(
            data_model_source=data_model_source
        )
        plugin_file.write_text(plugin_file_source)

    return prepare_foobar_plugin_impl


def test_load_boolean(datadir, prepare_foobar_plugin):
    prepare_foobar_plugin(["x = alfasim_sdk.Boolean(value=False, caption='x')"])
    alfacase = datadir / "test.alfacase"

    alfacase.write_text(
        textwrap.dedent(
            """\
            plugins:
            -   name: foobar
                is_enabled: True
                gui_models:
                    FooContainer:
                        _children_list:
                        -   x: True
                        -   x: False
            """
        )
    )
    case = convert_alfacase_to_description(alfacase)
    assert case.plugins == [
        PluginDescription(
            name="foobar",
            is_enabled=True,
            gui_models={
                "FooContainer": {
                    "_children_list": [
                        {"x": True},
                        {"x": False},
                    ],
                },
            },
        ),
    ]

    alfacase.write_text(
        textwrap.dedent(
            """\
            plugins:
            -   name: foobar
                is_enabled: True
                gui_models:
                    FooContainer:
                        _children_list:
                        -   x: {a: b}
            """
        )
    )
    with pytest.raises(InvalidPluginDataError, match="Can not convert"):
        convert_alfacase_to_description(alfacase)


def test_load_enum(datadir, prepare_foobar_plugin):
    prepare_foobar_plugin(
        ["x = alfasim_sdk.Enum(values=['A', 'B'], initial='A', caption='x')"]
    )
    alfacase = datadir / "test.alfacase"

    alfacase.write_text(
        textwrap.dedent(
            """\
            plugins:
            -   name: foobar
                is_enabled: True
                gui_models:
                    FooContainer:
                        _children_list:
                        -   x: A
                        -   x: B
            """
        )
    )
    case = convert_alfacase_to_description(alfacase)
    assert case.plugins == [
        PluginDescription(
            name="foobar",
            is_enabled=True,
            gui_models={
                "FooContainer": {
                    "_children_list": [
                        {"x": "A"},
                        {"x": "B"},
                    ],
                },
            },
        ),
    ]

    alfacase.write_text(
        textwrap.dedent(
            """\
            plugins:
            -   name: foobar
                is_enabled: True
                gui_models:
                    FooContainer:
                        _children_list:
                        -   x: C
            """
        )
    )
    with pytest.raises(InvalidPluginDataError, match="Can not convert"):
        convert_alfacase_to_description(alfacase)


def test_load_file_content(monkeypatch, datadir, prepare_foobar_plugin):
    prepare_foobar_plugin(["x = alfasim_sdk.FileContent(caption='x')"])
    readme = datadir / "readme.md"
    readme.write_text("**foo** all the **bars**")
    alfacase = datadir / "test.alfacase"

    alfacase.write_text(
        textwrap.dedent(
            """\
            plugins:
            -   name: foobar
                is_enabled: True
                gui_models:
                    FooContainer:
                        _children_list:
                        -   x: foo-bar.txt
                        -   x: readme.md
            """
        )
    )
    case = convert_alfacase_to_description(alfacase)
    children_list = [
        {
            "x": PluginFileContent(
                path=Path("foo-bar.txt"),
                content=b"",
                size=0,
                modified_date=datetime.now(),
                is_valid=False,
            )
        },
        {
            "x": PluginFileContent(
                path=Path("readme.md"),
                content=readme.read_bytes(),
                size=readme.stat().st_size,
                modified_date=datetime.now(),
                is_valid=True,
            )
        },
    ]
    for child in children_list:
        object.__setattr__(child["x"], "modified_date", ANY)
    assert case.plugins == [
        PluginDescription(
            name="foobar",
            is_enabled=True,
            gui_models={
                "FooContainer": {
                    "_children_list": children_list,
                },
            },
        ),
    ]

    alfacase.write_text(
        textwrap.dedent(
            """\
            plugins:
            -   name: foobar
                is_enabled: True
                gui_models:
                    FooContainer:
                        _children_list:
                        -   x: {a: b}
            """
        )
    )
    with pytest.raises(InvalidPluginDataError, match="Can not convert"):
        convert_alfacase_to_description(alfacase)


def test_load_multiple_reference(datadir, prepare_foobar_plugin):
    prepare_foobar_plugin(
        [
            "x = alfasim_sdk.MultipleReference(ref_type=Bar, container_type='FooContainer', caption='x')"
        ]
    )
    alfacase = datadir / "test.alfacase"

    alfacase.write_text(
        textwrap.dedent(
            """\
            plugins:
            -   name: foobar
                is_enabled: True
                gui_models:
                    FooContainer:
                        _children_list:
                        -   x:
                                container_key: FooContainer
                                item_id_list: [0, 2]
            """
        )
    )
    case = convert_alfacase_to_description(alfacase)
    assert case.plugins == [
        PluginDescription(
            name="foobar",
            is_enabled=True,
            gui_models={
                "FooContainer": {
                    "_children_list": [
                        {
                            "x": PluginMultipleReference(
                                container_key="FooContainer",
                                item_id_list=[0, 2],
                            ),
                        },
                    ],
                },
            },
        ),
    ]

    alfacase.write_text(
        textwrap.dedent(
            """\
            plugins:
            -   name: foobar
                is_enabled: True
                gui_models:
                    FooContainer:
                        _children_list:
                        -   x: A
            """
        )
    )
    with pytest.raises(InvalidPluginDataError, match="Can not convert"):
        convert_alfacase_to_description(alfacase)


def test_load_reference(datadir, prepare_foobar_plugin):
    prepare_foobar_plugin(
        [
            "x = alfasim_sdk.Reference(ref_type=Bar, container_type='FooContainer', caption='x')",
            "y = alfasim_sdk.Reference(ref_type=alfasim_sdk.TracerType, caption='y')",
        ]
    )
    alfacase = datadir / "test.alfacase"

    alfacase.write_text(
        textwrap.dedent(
            """\
            plugins:
            -   name: foobar
                is_enabled: True
                gui_models:
                    FooContainer:
                        _children_list:
                        -   x:
                                plugin_item_id: 3
                            y:
                                tracer_id: 5
            """
        )
    )
    case = convert_alfacase_to_description(alfacase)
    assert case.plugins == [
        PluginDescription(
            name="foobar",
            is_enabled=True,
            gui_models={
                "FooContainer": {
                    "_children_list": [
                        {
                            "x": PluginInternalReference(plugin_item_id=3),
                            "y": PluginTracerReference(tracer_id=5),
                        },
                    ],
                },
            },
        ),
    ]

    alfacase.write_text(
        textwrap.dedent(
            """\
            plugins:
            -   name: foobar
                is_enabled: True
                gui_models:
                    FooContainer:
                        _children_list:
                        -   x: A
                            y: A
            """
        )
    )
    with pytest.raises(InvalidPluginDataError, match="Can not convert"):
        convert_alfacase_to_description(alfacase)


def test_load_quantity(datadir, prepare_foobar_plugin):
    prepare_foobar_plugin(
        ["x = alfasim_sdk.Quantity(value=7.9, unit='m', caption='x')"]
    )
    alfacase = datadir / "test.alfacase"

    alfacase.write_text(
        textwrap.dedent(
            """\
            plugins:
            -   name: foobar
                is_enabled: True
                gui_models:
                    FooContainer:
                        _children_list:
                        -   x:
                                value: 1.3
                                unit: s
                        -   x:
                                value: 3.5
                                unit: m
            """
        )
    )
    case = convert_alfacase_to_description(alfacase)
    assert case.plugins == [
        PluginDescription(
            name="foobar",
            is_enabled=True,
            gui_models={
                "FooContainer": {
                    "_children_list": [
                        {"x": Scalar(1.3, "s")},
                        {"x": Scalar(3.5, "m")},
                    ],
                },
            },
        ),
    ]

    alfacase.write_text(
        textwrap.dedent(
            """\
            plugins:
            -   name: foobar
                is_enabled: True
                gui_models:
                    FooContainer:
                        _children_list:
                        -   x: A
            """
        )
    )
    with pytest.raises(InvalidPluginDataError, match="Can not convert"):
        convert_alfacase_to_description(alfacase)


def test_load_string(datadir, prepare_foobar_plugin):
    prepare_foobar_plugin(["x = alfasim_sdk.String(value='Red', caption='x')"])
    alfacase = datadir / "test.alfacase"

    alfacase.write_text(
        textwrap.dedent(
            """\
            plugins:
            -   name: foobar
                is_enabled: True
                gui_models:
                    FooContainer:
                        _children_list:
                        -   x: Blue
                        -   x: Green
            """
        )
    )
    case = convert_alfacase_to_description(alfacase)
    assert case.plugins == [
        PluginDescription(
            name="foobar",
            is_enabled=True,
            gui_models={
                "FooContainer": {
                    "_children_list": [
                        {"x": "Blue"},
                        {"x": "Green"},
                    ],
                },
            },
        ),
    ]

    alfacase.write_text(
        textwrap.dedent(
            """\
            plugins:
            -   name: foobar
                is_enabled: True
                gui_models:
                    FooContainer:
                        _children_list:
                        -   x: {a: b}
            """
        )
    )
    with pytest.raises(InvalidPluginDataError, match="Can not convert"):
        convert_alfacase_to_description(alfacase)


def test_load_table(datadir, prepare_foobar_plugin):
    prepare_foobar_plugin(
        [
            """x = alfasim_sdk.Table(
                rows=[
                    alfasim_sdk.TableColumn(id='aaa', value=alfasim_sdk.Quantity(value=1, unit='m', caption='a')),
                    alfasim_sdk.TableColumn(id='sss', value=alfasim_sdk.Quantity(value=1, unit='m', caption='s')),
                ],
                caption='x',
            )"""
        ]
    )
    alfacase = datadir / "test.alfacase"

    alfacase.write_text(
        textwrap.dedent(
            """\
            plugins:
            -   name: foobar
                is_enabled: True
                gui_models:
                    FooContainer:
                        _children_list:
                        -   x:
                                columns:
                                    aaa:
                                        values: [1.2, 2.3, 3.4]
                                        unit: s
                                    sss:
                                        values: [9.8, 8.7, 7.6]
                                        unit: m
            """
        )
    )
    case = convert_alfacase_to_description(alfacase)
    assert case.plugins == [
        PluginDescription(
            name="foobar",
            is_enabled=True,
            gui_models={
                "FooContainer": {
                    "_children_list": [
                        {
                            "x": PluginTableContainer(
                                columns={
                                    "aaa": Array([1.2, 2.3, 3.4], "s"),
                                    "sss": Array([9.8, 8.7, 7.6], "m"),
                                }
                            )
                        },
                    ],
                },
            },
        ),
    ]

    alfacase.write_text(
        textwrap.dedent(
            """\
            plugins:
            -   name: foobar
                is_enabled: True
                gui_models:
                    FooContainer:
                        _children_list:
                        -   x:
                                columns:
                                    aaa:
                                        values: [1.2, 2.3, 3.4]
                                        unit: s
            """
        )
    )
    with pytest.raises(InvalidPluginDataError, match="Can not convert"):
        convert_alfacase_to_description(alfacase)

    alfacase.write_text(
        textwrap.dedent(
            """\
            plugins:
            -   name: foobar
                is_enabled: True
                gui_models:
                    FooContainer:
                        _children_list:
                        -   x:
                                columns:
                                    aaa:
                                        values: [1.2, 2.3, 3.4]
                                        unit: s
                                    sss:
                                        values: [9.8, 8.7, 7.6]
            """
        )
    )
    with pytest.raises(InvalidPluginDataError, match="Can not convert"):
        convert_alfacase_to_description(alfacase)

    alfacase.write_text(
        textwrap.dedent(
            """\
            plugins:
            -   name: foobar
                is_enabled: True
                gui_models:
                    FooContainer:
                        _children_list:
                        -   x:
                                aaa:
                                    values: [1.2, 2.3, 3.4]
                                    unit: s
            """
        )
    )
    with pytest.raises(InvalidPluginDataError, match="Can not convert"):
        convert_alfacase_to_description(alfacase)

    alfacase.write_text(
        textwrap.dedent(
            """\
            plugins:
            -   name: foobar
                is_enabled: True
                gui_models:
                    FooContainer:
                        _children_list:
                        -   x: A
            """
        )
    )
    with pytest.raises(InvalidPluginDataError, match="Can not convert"):
        convert_alfacase_to_description(alfacase)


def test_dump_file_contents_and_update_plugins(datadir, monkeypatch):
    def prop_getter(case: CaseDescription, child_index: int, key: str) -> object:
        gui_models = case.plugins[0].gui_models
        return gui_models["FooContainer"]["_children_list"][child_index][key]

    case_description = CaseDescription(
        plugins=[
            PluginDescription(
                name="foobar",
                is_enabled=True,
                gui_models={
                    "FooContainer": {
                        "_children_list": [
                            {
                                "x": PluginFileContent(
                                    path=Path("asd/qwe.txt"),
                                    content=b"Let it be",
                                    modified_date=datetime.now(),
                                    size=len(b"Let it be"),
                                    is_valid=True,
                                ),
                                "y": 17,
                            },
                            {
                                "x": PluginFileContent(
                                    path=Path("asd/qwe.txt"),
                                    content=b"Black bird",
                                    modified_date=datetime.now(),
                                    size=len(b"Black bird"),
                                    is_valid=True,
                                ),
                                "y": 27,
                            },
                        ],
                    },
                },
            ),
        ]
    )
    expected_dumped_files = [datadir / "qwe.txt", datadir / "qwe (2).txt"]
    fake_alfacase_file = datadir / "fake.alfacase"

    assert all(not f.exists() for f in expected_dumped_files)
    updated_case_description = dump_file_contents_and_update_plugins(
        case_description, fake_alfacase_file
    )
    assert all(f.is_file() for f in expected_dumped_files)

    monkeypatch.chdir(fake_alfacase_file.parent)
    for index, text in ((0, "Let it be"), (1, "Black bird")):
        original_x = prop_getter(case_description, index, "x")
        assert isinstance(original_x, PluginFileContent)
        updated_x = prop_getter(updated_case_description, index, "x")
        assert isinstance(updated_x, str)
        assert Path(updated_x).read_text() == text

        original_y = prop_getter(case_description, index, "y")
        updated_y = prop_getter(updated_case_description, index, "y")
        assert original_y is updated_y


def test_load_plugin_without_inputs(datadir, monkeypatch):
    plugin_root = datadir / "test_plugins"
    monkeypatch.setenv("ALFASIM_PLUGINS_DIR", str(plugin_root))
    plugin_file = plugin_root / "no_input/artifacts/no_input.py"
    plugin_file.parent.mkdir(parents=True)
    plugin_file_source = textwrap.dedent(
        """\
        import alfasim_sdk

        @alfasim_sdk.data_model(caption='No Input')
        class RequiredModel:
            pass

        @alfasim_sdk.hookimpl
        def alfasim_get_data_model_type():
            return [RequiredModel]
        """
    )
    plugin_file.write_text(plugin_file_source)

    alfacase = datadir / "test.alfacase"
    alfacase.write_text(
        textwrap.dedent(
            """\
            plugins:
            -   name: no_input
                is_enabled: True
            """
        )
    )

    case = convert_alfacase_to_description(alfacase)
    assert case.plugins == [
        PluginDescription(
            name="no_input",
            is_enabled=True,
            gui_models={},
        ),
    ]


def test_load_not_installed_plugin(datadir):
    alfacase = datadir / "test.alfacase"
    alfacase.write_text(
        textwrap.dedent(
            """\
            plugins:
            -   name: not_installed
                is_enabled: True
                gui_models:
                    AContainer:
                        _children_list:
                        -   a: Asd
            """
        )
    )

    case = convert_alfacase_to_description(alfacase)
    assert case.plugins == []
