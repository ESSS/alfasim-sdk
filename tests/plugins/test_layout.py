import pytest

from alfasim_sdk.layout import tab
from alfasim_sdk.layout import tabs
from alfasim_sdk.types import String


def test_group():
    from alfasim_sdk.models import data_model
    from alfasim_sdk.layout import group

    @data_model(caption="Foo")
    class ValidClass:
        string_from_main = String(caption="Caption from Root", value="Root")

        @group(caption="This is a Group")
        class GroupMain:
            string_from_group = String(
                caption="Caption From Group", value="Inside Group"
            )

    import attr

    # Checking the Model has all attributes
    assert [x.name for x in attr.fields(ValidClass)] == [
        "string_from_main",
        "GroupMain",
    ]

    # Checking attributes from the GroupMain
    group_class = attr.fields(ValidClass)[1].default
    assert [x.name for x in attr.fields(group_class)] == ["string_from_group"]

    # A Group inside a tab is valid
    @data_model(caption="Foo")
    class ValidClassTabGroup:
        @tabs()
        class TabsMain:
            @tab(caption="Fist Tab")
            class Tab1:
                string_from_first_tab = String(caption="first", value="1")

                @group(caption="This is a Group")
                class GroupMain:
                    string_from_first_tab_inside_group = String(
                        caption="Caption From Group", value="Inside Group"
                    )

            @tab(caption="Second Tab")
            class Tab2:
                string_from_second_tab = String(caption="second", value="2")

    tabs_main = attr.fields(ValidClassTabGroup)[0].default
    tab_1 = attr.fields(tabs_main)[0].default
    tab_2 = attr.fields(tabs_main)[1].default
    string_from_first_tab = attr.fields(tab_1)[0].default
    string_from_second_tab = attr.fields(tab_2)[0].default

    group_main = attr.fields(tab_1)[1].default
    string_from_group_main = attr.fields(group_main)[0].default

    assert string_from_first_tab.caption == "first"
    assert string_from_second_tab.caption == "second"
    assert string_from_group_main.caption == "Caption From Group"


def test_tabs():
    from alfasim_sdk.types import String
    from alfasim_sdk.layout import tabs, tab
    from alfasim_sdk.models import data_model

    error_msg = "Error on attribute 'a' expecting a class decorated with @tab but received a String type"
    with pytest.raises(TypeError, match=error_msg):

        @data_model(caption="Foo")
        class InvalidClass:  # pylint: disable=unused-variable
            @tabs()
            class Main:
                a = String(caption="1", value="2")

                @tab(caption="Fist Tab")
                class Tab1:
                    pass

                @tab(caption="Second Tab")
                class Tab2:
                    pass

    @data_model(caption="Foo")
    class ValidClass:
        string_from_main = String(caption="main", value="2")

        @tabs()
        class TabsMain:
            @tab(caption="Fist Tab")
            class Tab1:
                string_from_first_tab = String(caption="first", value="2")

            @tab(caption="Second Tab")
            class Tab2:
                string_from_second_tab = String(caption="second", value="2")

    import attr

    # Checking the Model has all attributes
    assert len(attr.fields(ValidClass)) == 2
    assert attr.fields(ValidClass)[0].name == "string_from_main"
    assert attr.fields(ValidClass)[1].name == "TabsMain"

    # Checking attributes from the @tabs
    tabs_main_class = attr.fields(ValidClass)[1].default
    assert len(attr.fields(tabs_main_class)) == 2
    assert attr.fields(tabs_main_class)[0].name == "Tab1"
    assert attr.fields(tabs_main_class)[1].name == "Tab2"

    # Checking the attribute from @tab
    first_tab_class = attr.fields(tabs_main_class)[0].default
    assert len(attr.fields(first_tab_class)) == 1
    assert attr.fields(first_tab_class)[0].name == "string_from_first_tab"
