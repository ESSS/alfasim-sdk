import pytest


def test_tabs():
    from alfasim_sdk.types import String
    from alfasim_sdk.layout import tabs, tab
    from alfasim_sdk.models import data_model

    error_msg = "Error on attribute 'a' expecting a class decorated with @tab but received a String type"
    with pytest.raises(TypeError, match=error_msg):
        @data_model(caption='Foo')
        class A:
            @tabs()
            class Main:
                a = String(caption='1', value='2')


                @tab(caption='Fist Tab')
                class Tab1:
                    pass


                @tab(caption='Second Tab')
                class Tab2:
                    pass


    @data_model(caption='Foo')
    class B:
        string_from_main = String(caption='main', value='2')


        @tabs()
        class TabsMain:
            @tab(caption='Fist Tab')
            class Tab1:
                string_from_first_tab = String(caption='first', value='2')


            @tab(caption='Second Tab')
            class Tab2:
                string_from_second_tab = String(caption='second', value='2')


    import attr
    # Checking the Model has all attributes
    assert len(attr.fields(B)) == 2
    assert attr.fields(B)[0].name == 'string_from_main'
    assert attr.fields(B)[1].name == 'TabsMain'

    # Checking attributes from the @tabs
    tabs_main_class = attr.fields(B)[1].default
    assert len(attr.fields(tabs_main_class)) == 2
    assert attr.fields(tabs_main_class)[0].name == "Tab1"
    assert attr.fields(tabs_main_class)[1].name == "Tab2"

    # Checking the attribute from @tab
    first_tab_class = attr.fields(tabs_main_class)[0].default
    assert len(attr.fields(first_tab_class)) == 1
    assert attr.fields(first_tab_class)[0].name == 'string_from_first_tab'
