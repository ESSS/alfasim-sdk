import os
import textwrap
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any
from unittest.mock import ANY

import pytest
from _pytest.monkeypatch import MonkeyPatch
from barril.units import Array, Scalar
from pytest_mock import MockerFixture

from alfasim_sdk import PluginDescription, convert_alfacase_to_description
from alfasim_sdk._internal.alfacase.case_description import (
    CaseDescription,
    InternalReferencePluginTableColumn,
    PluginFileContent,
    PluginInternalReference,
    PluginMultipleReference,
    PluginTableContainer,
    PluginTracerReference,
    TracerReferencePluginTableColumn,
)
from alfasim_sdk._internal.alfacase.case_description_attributes import (
    InvalidPluginDataError,
)
from alfasim_sdk._internal.alfacase.plugin_alfacase_to_case import (
    dump_file_contents_and_update_plugins,
    load_plugin_data_structure,
    obtain_alfasim_plugins_dir,
)


class TestLoadPluginDataStructure:
    def test_without_importable_python(self, abx_plugin: None) -> None:
        alfasim_plugins_dir = obtain_alfasim_plugins_dir()
        models = load_plugin_data_structure("abx", alfasim_plugins_dir)
        assert models is not None
        assert [m.__name__ for m in models] == ["AContainer", "BContainer"]

        with pytest.raises(ModuleNotFoundError):
            import alfasim_sdk_plugins.abx  # noqa

    def test_with_importable_python(self, importable_plugin: None) -> None:
        with pytest.raises(ModuleNotFoundError):
            import alfasim_sdk_plugins.importable  # noqa

        alfasim_plugins_dir = obtain_alfasim_plugins_dir()
        models = load_plugin_data_structure("importable", alfasim_plugins_dir)
        assert models is not None
        assert [m.__name__ for m in models] == ["Foo"]

        import alfasim_sdk_plugins.importable  # noqa
        from alfasim_sdk_plugins.importable import buz  # noqa

        assert buz.BUZ == "fiz buz!"

    def test_keep_namespace_tidy(
        self,
        importable_plugin: None,
        importable_plugin_source: Path,
        datadir: Path,
        monkeypatch: MonkeyPatch,
        mocker: MockerFixture,
    ) -> None:
        import alfasim_sdk_plugins
        from alfasim_sdk._internal.alfacase import plugin_alfacase_to_case

        # Create an invalid "importable" plugin.
        plugin_root = datadir / "test_invalid_plugins"
        plugin_file = plugin_root / "importable-1.0.0/artifacts/importable.py"
        plugin_file.parent.mkdir(parents=True)
        plugin_file.touch()
        invalid_namespace = plugin_file.parent / "alfasim_sdk_plugins"
        (invalid_namespace / "importable").mkdir(parents=True)
        monkeypatch.setenv(
            "ALFASIM_PLUGINS_DIR", str(plugin_root), prepend=os.path.pathsep
        )

        # Prepare to check if the namespace is being updated while trying to load the plugin.
        valid_namespace = (
            importable_plugin_source / "importable-1.0.0/artifacts/alfasim_sdk_plugins"
        )
        good_namespace = str(valid_namespace.absolute())
        bad_namespace = str(invalid_namespace.absolute())
        expected_namespace_state = iter(
            [
                {"with": bad_namespace, "without": good_namespace},
                {"with": good_namespace, "without": bad_namespace},
            ]
        )
        original_import_module = plugin_alfacase_to_case.import_module

        def mock_import_module(*args: Any, **kwargs: Any) -> Any:
            expected = next(expected_namespace_state)
            assert expected["with"] in alfasim_sdk_plugins.__path__, "AAA"
            assert expected["without"] not in alfasim_sdk_plugins.__path__, "BBB"
            return original_import_module(*args, **kwargs)

        mocker.patch.object(
            plugin_alfacase_to_case, "import_module", new=mock_import_module
        )
        alfasim_plugins_dir = obtain_alfasim_plugins_dir()
        load_plugin_data_structure("importable", alfasim_plugins_dir)

        assert bad_namespace not in alfasim_sdk_plugins.__path__
        assert good_namespace in alfasim_sdk_plugins.__path__

        # Check if `mock import module` has exhausted the expected values.
        with pytest.raises(StopIteration):
            next(expected_namespace_state)


def test_load_plugin_multiple_containers(datadir, abx_plugin):
    alfacase = datadir / "test.alfacase"
    alfacase.write_text(
        textwrap.dedent(
            """\
            plugins:
            -   name: abx
                version: 1.0.0
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
            version="1.0.0",
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
                version: 1.0.0
                gui_models: {}
            """
        )
    )
    case = convert_alfacase_to_description(alfacase)
    assert case.plugins == [
        PluginDescription(
            name="abx",
            version="1.0.0",
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
                version: 1.0.0
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
            version="1.0.0",
            is_enabled=True,
            gui_models={
                "AContainer": {"_children_list": []},
                "BContainer": {"_children_list": []},
            },
        ),
    ]


@pytest.fixture(name="prepare_foobar_plugin")
def prepare_foobar_plugin_(monkeypatch, datadir) -> Callable[[list[str]], None]:
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

    def prepare_foobar_plugin_impl(data_model_fields: list[str]) -> None:
        plugin_root = datadir / "test_plugins"
        monkeypatch.setenv("ALFASIM_PLUGINS_DIR", str(plugin_root))
        plugin_file = plugin_root / "foobar-1.0.0/artifacts/foobar.py"
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

            @alfasim_sdk.container_model(model=Bar, icon="", caption="Bar Container")
            class BarContainer:
                pass

            {data_model_source}

            @alfasim_sdk.container_model(model=Foo, icon="", caption="Foo Container")
            class FooContainer:
                pass

            @alfasim_sdk.hookimpl
            def alfasim_get_data_model_type():
                return [FooContainer, BarContainer]
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
                version: 1.0.0
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
            version="1.0.0",
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
                version: 1.0.0
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
                version: 1.0.0
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
            version="1.0.0",
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
                version: 1.0.0
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
                version: 1.0.0
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
            version="1.0.0",
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
                version: 1.0.0
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
                version: 1.0.0
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
            version="1.0.0",
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
                version: 1.0.0
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
                version: 1.0.0
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
            version="1.0.0",
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
                version: 1.0.0
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
                version: 1.0.0
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
            version="1.0.0",
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
                version: 1.0.0
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
                version: 1.0.0
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
            version="1.0.0",
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
                version: 1.0.0
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


class TestLoadTable:
    def test_quantity(
        self, datadir: Path, prepare_foobar_plugin: Callable[[list[str]], None]
    ) -> None:
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
                    version: 1.0.0
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
                version="1.0.0",
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
                    version: 1.0.0
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
                    version: 1.0.0
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
                    version: 1.0.0
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
                    version: 1.0.0
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

    def test_references(
        self, datadir: Path, prepare_foobar_plugin: Callable[[list[str]], None]
    ) -> None:
        # Setup.
        prepare_foobar_plugin(
            [
                """x = alfasim_sdk.Table(
                    rows=[
                        alfasim_sdk.TableColumn(
                            id='aaa',
                            value=alfasim_sdk.Reference(
                                container_type='BarContainer', ref_type=Bar, caption="A Bar"
                            ),
                        ),
                        alfasim_sdk.TableColumn(
                            id='sss',
                             value=alfasim_sdk.Reference(
                                ref_type=alfasim_sdk.TracerType, caption="A Tracer"
                            ),
                        ),
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
                    version: 1.0.0
                    is_enabled: True
                    gui_models:
                        FooContainer:
                            _children_list:
                            -   x:
                                    columns:
                                        aaa:
                                            container_key: BarContainer
                                            plugin_item_ids: [0, 0, 2, 2]
                                        sss:
                                            tracer_ids: [1, 2, 3, 3]
                """
            )
        )
        # Test.
        case = convert_alfacase_to_description(alfacase)
        assert case.plugins == [
            PluginDescription(
                name="foobar",
                version="1.0.0",
                is_enabled=True,
                gui_models={
                    "FooContainer": {
                        "_children_list": [
                            {
                                "x": PluginTableContainer(
                                    columns={
                                        "aaa": InternalReferencePluginTableColumn(
                                            container_key="BarContainer",
                                            plugin_item_ids=[0, 0, 2, 2],
                                        ),
                                        "sss": TracerReferencePluginTableColumn(
                                            tracer_ids=[1, 2, 3, 3]
                                        ),
                                    }
                                )
                            },
                        ],
                    },
                },
            ),
        ]


def test_dump_file_contents_and_update_plugins(datadir, monkeypatch):
    def prop_getter(case: CaseDescription, child_index: int, key: str) -> object:
        gui_models = case.plugins[0].gui_models
        return gui_models["FooContainer"]["_children_list"][child_index][key]

    case_description = CaseDescription(
        plugins=[
            PluginDescription(
                name="foobar",
                version="1.0.0",
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
    plugin_file = plugin_root / "no_input-1.0.0/artifacts/no_input.py"
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
                version: 1.0.0
                is_enabled: True
            """
        )
    )

    case = convert_alfacase_to_description(alfacase)
    assert case.plugins == [
        PluginDescription(
            name="no_input",
            version="1.0.0",
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
                version: 0.0.0
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


def test_load_plugin_without_version(
    datadir: Path, abx_plugin: None, monkeypatch: MonkeyPatch
) -> None:
    """
    Test to ensure the backward compatibility in case of version is not specifeid in the
    .alfacase file.
    """
    plugins_root = datadir / "test_plugins"
    monkeypatch.setenv("ALFASIM_PLUGINS_DIR", str(plugins_root))

    assets = plugins_root / "abx-1.0.0" / "assets"
    assets.mkdir()

    plugin_yaml = assets / "plugin.yaml"
    plugin_yaml.touch()

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
            version=None,
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

    wrong_alfacase = datadir / "wrong.alfacase"
    wrong_alfacase.write_text(
        textwrap.dedent(
            """\
            plugins:
            -   name: abs
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
